from datetime import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from knox.auth import TokenAuthentication
from rest_framework import serializers, validators
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.relations import PrimaryKeyRelatedField

from .models import UserMessage, MessageChannel, DirectMessageChannel, GroupMessageChannel, Reaction, SystemMessage


class MessageChannelSerializer(serializers.ModelSerializer):
    """Serializes a MessageChannel to JSON."""

    class Meta:
        model = MessageChannel
        fields = ["id", "channel_type", "created_at", "message_last_sent"]
        read_only_fields = ["channel_type", "created_at", "message_last_sent"]


class DirectMessageChannelSerializer(MessageChannelSerializer):
    """Serializer for DM."""
    users = PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    has_read = serializers.SerializerMethodField(read_only=True)

    class Meta(MessageChannelSerializer.Meta):
        model = DirectMessageChannel
        fields = MessageChannelSerializer.Meta.fields + ["users", "created_at", "has_read"]
        read_only_fields = ["id", "channel_type", "created_at", "has_read"]

    def get_has_read(self, obj):
        return obj.has_read_message_channel(self.context["request"].user)

    def create(self, validated_data):
        users = validated_data["users"]
        return MessageChannel.objects.create_direct_message(users[0], users[1])

    def validate(self, data):
        current_user = self.context["request"].user
        users = data["users"]

        # Verifies data.
        if current_user not in users:
            raise serializers.ValidationError("The creation of a DM must include the current user.")
        if len(users) != 2:
            raise serializers.ValidationError("A DM must have exactly 2 people.")

        to_user = users[0] if users[1] == current_user else users[1]
        if current_user.message_channels.filter(channel_type="DM").filter(users=to_user).exists():
            raise serializers.ValidationError("DM already exists.")

        return data


class GroupMessageChannelSerializer(MessageChannelSerializer):
    """Serializer for Group Chat."""
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    channel_type = serializers.CharField(required=False)
    has_read = serializers.SerializerMethodField(read_only=True)

    class Meta(MessageChannelSerializer.Meta):
        model = GroupMessageChannel
        fields = MessageChannelSerializer.Meta.fields + ["name", "owner", "users", "created_at", "has_read"]
        read_only_fields = ["id", "channel_type", "created_at", "has_read"]

    def get_has_read(self, obj):
        return obj.has_read_message_channel(self.context["request"].user)

    def create(self, validated_data):
        current_user = self.context["request"].user
        users = validated_data["users"]

        if current_user not in users:
            raise validators.ValidationError("The creation of a group chats must include the current user.")

        return MessageChannel.objects.create_group_chat(name=validated_data["name"], owner=current_user, users=users)

    def validate_users(self, new_users):
        if self.instance:
            current_user = self.context["request"].user
            users = set(self.instance.users.all())
            new_users_copy = set(new_users.copy())

            users.remove(current_user)
            new_users_copy.discard(current_user)

            if len(users.intersection(new_users_copy)) != len(users) and self.instance.owner.id != current_user.id:
                raise serializers.ValidationError("Permission Denied.")

        return new_users

    def validate_owner(self, new_owner):
        current_user = self.context["request"].user
        instance = self.instance

        if instance.owner != new_owner and current_user != instance.owner:
            raise serializers.ValidationError("Permission Denied.")
        if ("users" in self.initial_data and new_owner.id not in self.initial_data["users"]) or \
                ("users" not in self.initial_data and not instance.users.filter(id=new_owner.id).exists()):
            raise serializers.ValidationError("Owner is not in the group chats.")
        return new_owner

    def update(self, instance, validated_data):
        current_user = self.context["request"].user

        if "users" in validated_data:
            instance.update_users(current_user, validated_data["users"])

        if "owner" in validated_data:
            instance.update_owner(current_user, validated_data["owner"])

        if "name" in validated_data:
            instance.update_name(current_user, validated_data["name"])

        return instance


class ReadMessageChannelSerializer(serializers.ModelSerializer):
    has_read = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MessageChannel
        fields = ["id", "channel_type", "users", "created_at", "message_last_sent", "has_read"]
        read_only_fields = ["id", "channel_type", "users", "created_at", "message_last_sent", "has_read"]

    def update(self, instance, validated_data):
        instance.read_message_channel(self.context["request"].user)
        return instance

    def get_has_read(self, obj):
        return obj.has_read_message_channel(self.context["request"].user)


class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = ("user", "emoji")
        read_only_fields = ("user", "emoji")


class MessageSerializer(serializers.Serializer):

    @classmethod
    def get_serializer(cls, _type):
        if _type == "user_message":
            return UserMessageSerializer
        if _type == "system_message":
            return SystemMessageSerializer

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
        read_only_fields = ("type", "id", "user", "created_at", "updated_at", "reactions")

    def validate_user(self, instance):
        if instance.user.username != self.context["user"].username:
            raise serializers.ValidationError("Message does not exist.")

    def validate_message_channel(self, value):
        try:
            value.users.get(username=self.context["user"].username)
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Message channel does not exist.")
        return value

    def validate_reply(self, value):
        message_channel = self.initial_data.get("message_channel")
        if value is not None and value.message_channel_id != message_channel:
            raise serializers.ValidationError("Replied message does not exist.")
        return value

    def create(self, validated_data):
        message = UserMessage.objects.create(user=self.context["user"], **validated_data)
        validated_data["message_channel"].message_last_sent = datetime.now()
        validated_data["message_channel"].save()
        return message

    def update(self, instance, validated_data):
        self.validate_user(instance)
        instance.content = validated_data.get("content", instance.content)
        instance.save()
        return instance


class SystemMessageSerializer(serializers.ModelSerializer):
    message_channel = PrimaryKeyRelatedField(queryset=MessageChannel.objects.all())
    reactions = ReactionSerializer(many=True, required=False)

    class Meta:
        model = SystemMessage
        fields = ("type", "id", "created_at", "updated_at", "content", "message_channel", "reactions")
        read_only_fields = ("type", "id", "created_at", "updated_at", "message_channel", "reactions")


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
