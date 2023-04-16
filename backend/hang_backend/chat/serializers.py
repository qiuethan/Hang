from datetime import datetime

from django.contrib.auth.models import User
from knox.auth import TokenAuthentication
from rest_framework import serializers, validators
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.relations import PrimaryKeyRelatedField

from hang_event.models import HangEvent
from .models import UserMessage, MessageChannel, DirectMessage, GroupChat, Reaction, GroupChatNameChangedMessage, \
    GroupChatUserAddedMessage, GroupChatUserRemovedMessage, MessageChannelUsers, HangEventUserAddedMessage, \
    HangEventUpdatedMessage, HangEventUserRemovedMessage


class MessageChannelSerializer(serializers.ModelSerializer):
    """Serializes a MessageChannel to JSON."""

    class Meta:
        model = MessageChannel
        fields = ["id", "channel_type", "created_at", "message_last_sent"]
        read_only_fields = ["channel_type", "created_at", "message_last_sent"]


class DirectMessageSerializer(MessageChannelSerializer):
    """Serializer for DM."""
    users = PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    has_read = serializers.SerializerMethodField(read_only=True)

    class Meta(MessageChannelSerializer.Meta):
        model = DirectMessage
        fields = MessageChannelSerializer.Meta.fields + ["users", "created_at", "has_read"]
        read_only_fields = ["id", "channel_type", "created_at", "has_read"]

    def create(self, validated_data):
        current_user = self.context["request"].user
        users = list(set(validated_data["users"]))

        # Verifies data.
        if current_user not in users:
            raise validators.ValidationError("The creation of a DM must include the current user.")
        if len(users) != 2:
            raise validators.ValidationError("A DM must have exactly 2 people.")

        to_user = users[0] if users[1] == current_user else users[1]
        if current_user.message_channels.filter(channel_type="DM").filter(users=to_user).exists():
            raise validators.ValidationError("DM already exists.")

        # Creates MessageChannel from data.
        return MessageChannel.objects.create_direct_message(current_user, to_user)

    def update(self, instance, validated_data):
        raise NotImplementedError

    def get_has_read(self, obj):
        current_user = self.context["request"].user
        return MessageChannelUsers.objects.get(user_id=current_user.id, message_channel_id=obj.id).has_read


class GroupChatSerializer(MessageChannelSerializer):
    """Serializer for GC."""
    owner = PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    users = PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    channel_type = serializers.CharField(required=False)
    has_read = serializers.SerializerMethodField(read_only=True)

    class Meta(MessageChannelSerializer.Meta):
        model = GroupChat
        fields = MessageChannelSerializer.Meta.fields + ["name", "owner", "users", "created_at", "has_read"]
        read_only_fields = ["id", "channel_type" "created_at", "has_read"]

    def create(self, validated_data):
        current_user = self.context["request"].user
        users = list(set(validated_data["users"]))

        # Validates data.
        if current_user not in users:
            raise validators.ValidationError("The creation of a DM must include the current user.")

        # Creates GC and saves it.
        return MessageChannel.objects.create_group_chat(name=validated_data["name"], owner=current_user, users=users)

    def update(self, instance, validated_data):
        current_user = self.context["request"].user

        # Verifies if the user is in GC.
        if not instance.users.filter(id=current_user.id).exists():
            raise serializers.ValidationError("Permission Denied.")

        if "users" in validated_data:
            # User can only add more users / leave a GC; owner can remove user.
            users = validated_data["users"]
            curr_users = set(instance.users.all())
            new_users = set(users.copy())

            curr_users.remove(current_user)
            if current_user in users:
                new_users.remove(current_user)

            if len(curr_users.intersection(new_users)) != len(curr_users) and \
                    instance.owner.id != current_user.id:
                raise serializers.ValidationError("Permission Denied.")

        if "owner" in validated_data:
            # Only owner can transfer ownership.
            owner = validated_data["owner"]
            if instance.owner != owner and current_user != instance.owner:
                raise serializers.ValidationError("Permission Denied.")
            if not instance.users.filter(id=owner.id).exists():
                raise serializers.ValidationError("Owner is not in the GC.")

        # Send system messages.
        new_name = validated_data.get("name", instance.name)
        if instance.name != new_name:
            GroupChatNameChangedMessage.objects.create(message_channel=instance, new_name=new_name)
        new_users = validated_data.get("users", instance.users.all())
        for user in new_users:
            if user not in instance.users.all():
                GroupChatUserAddedMessage.objects.create(message_channel=instance, adder=current_user, user_added=user)
        for user in instance.users.all():
            if user not in new_users:
                GroupChatUserRemovedMessage.objects.create(message_channel=instance, remover=current_user,
                                                           user_removed=user)

        # Update fields.
        instance.name = validated_data.get("name", instance.name)
        instance.owner = validated_data.get("owner", instance.owner)
        instance.users.set(validated_data.get("users", instance.users.all()))

        # Transfer ownership if the owner leaves.
        if not instance.users.filter(id=instance.owner.id).exists():
            if instance.users.exists():
                instance.owner = instance.users.first()
            else:
                instance.owner = None

        instance.save()
        return instance

    def get_has_read(self, obj):
        current_user = self.context["request"].user
        qs = MessageChannelUsers.objects.filter(user_id=current_user.id, message_channel_id=obj.id)
        return qs.get().has_read if qs.count() else True


class ReadMessageChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageChannelUsers
        fields = ('user', 'message_channel', 'has_read',)
        read_only_fields = ('user', 'message_channel',)

    def update(self, instance, validated_data):
        instance.has_read = True
        instance.save()
        return instance


class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = ("user", "emoji")
        read_only_fields = ("user", "emoji")


class MessageSerializer(serializers.Serializer):
    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError

    def validate(self, data):
        raise NotImplementedError

    @classmethod
    def get_serializer(cls, _type):
        if _type == "user_message":
            return UserMessageSerializer
        if _type == "group_chat_name_changed_message":
            return GroupChatNameChangedMessageSerializer
        if _type == "group_chat_user_added_message":
            return GroupChatUserAddedMessageSerializer
        if _type == "group_chat_user_removed_message":
            return GroupChatUserRemovedMessageSerializer
        if _type == "hang_event_updated_message":
            return HangEventUpdatedMessageSerializer
        if _type == "hang_event_user_added_message":
            return HangEventUserAddedMessageSerializer
        if _type == "hang_event_user_removed_message":
            return HangEventUserRemovedMessageSerializer

    def to_representation(self, instance):
        serializer = self.get_serializer(instance.type)
        return serializer(serializer.Meta.model.objects.get(pk=instance.pk)).data


class UserMessageSerializer(serializers.ModelSerializer):
    """Serializer for a message."""
    user = PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    message_channel = PrimaryKeyRelatedField(queryset=MessageChannel.objects.all())
    reply = PrimaryKeyRelatedField(queryset=UserMessage.objects.all(), allow_null=True)
    reactions = ReactionSerializer(many=True, required=False)

    class Meta:
        model = UserMessage
        fields = ("type", "id", "user", "created_at", "updated_at", "content", "message_channel", "reply", "reactions")
        read_only_fields = ("type", "id", "user", "created_at", "updated_at", "message_channel", "reply", "reactions")

    def create(self, validated_data):
        # Verifies that the MessageChannel exists.
        if not validated_data["message_channel"].users.filter(username=self.context["user"].username).exists():
            raise serializers.ValidationError("Message channel does not exist.")

        # Verifies that the Message that is being replied exists in the current message channel or is null.
        if validated_data["reply"] is not None and \
                validated_data["reply"].message_channel != validated_data["message_channel"]:
            raise serializers.ValidationError("Replied message does not exist.")

        # Creates and saves the message.
        message = UserMessage(user=self.context["user"], content=validated_data["content"],
                              message_channel=validated_data["message_channel"], reply=validated_data["reply"])
        message.save()

        validated_data["message_channel"].message_last_sent = datetime.now()
        validated_data["message_channel"].save()

        return message

    def update(self, instance, validated_data):
        """Updates and existing message."""
        if instance.user.username != self.context["user"].username:
            raise serializers.ValidationError("Message does not exist.")
        instance.content = validated_data.get("content", instance.content)
        instance.save()
        return instance


class GroupChatNameChangedMessageSerializer(serializers.ModelSerializer):
    message_channel = PrimaryKeyRelatedField(queryset=MessageChannel.objects.all())

    class Meta:
        model = GroupChatNameChangedMessage
        fields = ("type", "id", "created_at", "updated_at", "message_channel", "new_name", "content")
        read_only_fields = ("type", "id", "created_at", "updated_at", "message_channel", "new_name", "content")


class GroupChatUserAddedMessageSerializer(serializers.ModelSerializer):
    message_channel = PrimaryKeyRelatedField(queryset=MessageChannel.objects.all())
    adder = PrimaryKeyRelatedField(queryset=User.objects.all())
    user_added = PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = GroupChatUserAddedMessage
        fields = ("type", "id", "created_at", "updated_at", "message_channel", "adder", "user_added", "content")
        read_only_fields = (
            "type", "id", "created_at", "updated_at", "message_channel", "adder", "user_added", "content")


class GroupChatUserRemovedMessageSerializer(serializers.ModelSerializer):
    message_channel = PrimaryKeyRelatedField(queryset=MessageChannel.objects.all())
    remover = PrimaryKeyRelatedField(queryset=User.objects.all())
    user_removed = PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = GroupChatUserRemovedMessage
        fields = ("type", "id", "created_at", "updated_at", "message_channel", "remover", "user_removed", "content")
        read_only_fields = (
            "type", "id", "created_at", "updated_at", "message_channel", "remover", "user_removed", "content")


class HangEventUpdatedMessageSerializer(serializers.ModelSerializer):
    hang_event = serializers.PrimaryKeyRelatedField(queryset=HangEvent.objects.all())

    class Meta:
        model = HangEventUpdatedMessage
        fields = (
            "type", "id", "created_at", "updated_at", "hang_event", "updated_field", "old_value", "new_value",
            "content")
        read_only_fields = (
            "type", "id", "created_at", "updated_at", "hang_event", "updated_field", "old_value", "new_value",
            "content")


class HangEventUserAddedMessageSerializer(serializers.ModelSerializer):
    hang_event = serializers.PrimaryKeyRelatedField(queryset=HangEvent.objects.all())
    user_added = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = HangEventUserAddedMessage
        fields = ("type", "id", "created_at", "updated_at", "hang_event", "user_added", "content")
        read_only_fields = ("type", "id", "created_at", "updated_at", "hang_event", "user_added", "content")


class HangEventUserRemovedMessageSerializer(serializers.ModelSerializer):
    hang_event = serializers.PrimaryKeyRelatedField(queryset=HangEvent.objects.all())
    user_removed = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = HangEventUserRemovedMessage
        fields = ("type", "id", "created_at", "updated_at", "hang_event", "user_removed", "content")
        read_only_fields = ("type", "id", "created_at", "updated_at", "hang_event", "user_removed", "content")


class AuthenticateWebsocketSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=100)

    def validate_token(self, data):
        # Checks if the AuthToken is valid.
        try:
            auth = TokenAuthentication().authenticate_credentials(data.encode("utf-8"))
            return auth[0]
        except AuthenticationFailed:
            raise serializers.ValidationError("Invalid Token.")

    def validate(self, data):
        # Verifies that the token is for the current user.
        if data["token"].username != self.context["user"].username:
            raise serializers.ValidationError("Token does not match user.")
        return data["token"]

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class LoadMessageSerializer(serializers.Serializer):
    """Serializer for LoadMessage ChatAction."""
    user = PrimaryKeyRelatedField(queryset=User.objects.all())
    message_channel = PrimaryKeyRelatedField(queryset=MessageChannel.objects.all())
    message_id = serializers.IntegerField(default=None)

    def validate(self, data):
        if not data["message_channel"].users.filter(username=data["user"].username).exists():
            raise serializers.ValidationError("Permission denied.")
        return data

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError
