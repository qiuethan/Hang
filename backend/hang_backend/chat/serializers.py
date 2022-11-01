from datetime import datetime

from knox.auth import TokenAuthentication
from rest_framework import serializers, validators
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.relations import PrimaryKeyRelatedField

from accounts.serializers import UserSerializer
from .models import Message, MessageChannel, DirectMessage, GroupChat


class MessageChannelSerializer(serializers.ModelSerializer):
    """Serializes a MessageChannel to JSON."""

    class Meta:
        model = MessageChannel
        fields = ["id", "channel_type", "created_at", "message_last_sent"]
        read_only_fields = ["channel_type", "created_at", "message_last_sent"]


class DirectMessageSerializer(MessageChannelSerializer):
    """Serializer for DM."""

    users = UserSerializer(many=True)

    class Meta(MessageChannelSerializer.Meta):
        model = DirectMessage
        fields = MessageChannelSerializer.Meta.fields + ["users", "created_at"]
        read_only_fields = ["id", "channel_type", "created_at"]

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


class GroupChatSerializer(MessageChannelSerializer):
    """Serializer for GC."""
    owner = UserSerializer(required=False)
    users = UserSerializer(many=True)
    channel_type = serializers.CharField(required=False)

    class Meta(MessageChannelSerializer.Meta):
        model = GroupChat
        fields = MessageChannelSerializer.Meta.fields + ["name", "owner", "users", "created_at"]
        read_only_fields = ["id", "channel_type" "created_at"]

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


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for a message."""
    user = UserSerializer(required=False)
    message_channel = PrimaryKeyRelatedField(queryset=MessageChannel.objects.all())

    class Meta:
        model = Message
        fields = ("id", "user", "created_at", "updated_at", "content", "message_channel")
        read_only_fields = ("id", "user", "created_at", "updated_at", "message_channel")

    def create(self, validated_data):
        # Verifies that the MessageChannel exists.
        if not validated_data["message_channel"].users.filter(username=self.context["user"].username).exists():
            raise serializers.ValidationError("Message channel does not exist.")

        # Creates and saves the message.
        message = Message(user=self.context["user"], content=validated_data["content"],
                          message_channel=validated_data["message_channel"])
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
    user = UserSerializer()
    message_channel = MessageChannelSerializer()
    message_id = serializers.IntegerField(default=None)

    def validate(self, data):
        if not data["message_channel"].users.filter(username=data["user"].username).exists():
            raise serializers.ValidationError("Permission denied.")
        return data

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError
