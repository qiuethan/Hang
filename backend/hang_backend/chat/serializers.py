import random
import string
from datetime import datetime

from knox.auth import TokenAuthentication
from rest_framework import serializers, validators
from rest_framework.exceptions import AuthenticationFailed

from accounts.serializers import UserSerializer, UserReaderSerializer
from common.util import validators as util_validators
from .models import Message, MessageChannel, DirectMessage, GroupChat


class MessageChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageChannel
        fields = ["id", "channel_type", "created_at", "message_last_sent"]
        read_only_fields = ["channel_type", "created_at", "message_last_sent"]


class MessageChannelReaderSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=10)
    validators = [
        util_validators.ObjectExistsValidator(queryset=MessageChannel.objects.all(), fields=["id"]),
    ]

    def validate(self, data):
        return MessageChannel.objects.get(id=data["id"])


def generate_random_string():
    return "".join([random.choice(string.ascii_letters) for _ in range(10)])


def generate_message_channel_id():
    message_channel_id = generate_random_string()
    while MessageChannel.objects.filter(id=message_channel_id).exists():
        message_channel_id = generate_random_string()
    return message_channel_id


class DirectMessageSerializer(MessageChannelSerializer):
    users = UserReaderSerializer(many=True)

    class Meta(MessageChannelSerializer.Meta):
        model = DirectMessage
        fields = MessageChannelSerializer.Meta.fields + ["users", "created_at"]
        read_only_fields = ["id", "channel_type", "created_at"]

    def create(self, validated_data):
        current_user = self.context["request"].user
        users = list(set(validated_data["users"]))

        if current_user not in users:
            raise validators.ValidationError("The creation of a DM must include the current user.")
        if len(users) != 2:
            raise validators.ValidationError("A DM must have exactly 2 people.")

        to_user = users[0] if users[1] == current_user else users[1]
        if current_user.message_channels.filter(channel_type="DM").filter(users=to_user).exists():
            raise validators.ValidationError("DM already exists.")

        message_channel_id = generate_message_channel_id()

        direct_message = DirectMessage(id=message_channel_id, channel_type="DM")
        direct_message.save()

        direct_message.users.add(current_user)
        direct_message.users.add(to_user)

        return direct_message


class GroupChatSerializer(MessageChannelSerializer):
    owner = UserReaderSerializer(required=False)
    users = UserReaderSerializer(many=True)
    channel_type = serializers.CharField(required=False)

    class Meta(MessageChannelSerializer.Meta):
        model = GroupChat
        fields = MessageChannelSerializer.Meta.fields + ["name", "owner", "users", "created_at"]
        read_only_fields = ["id", "channel_type" "created_at"]

    def create(self, validated_data):
        current_user = self.context["request"].user
        users = list(set(validated_data["users"]))

        if current_user not in users:
            raise validators.ValidationError("The creation of a DM must include the current user.")

        message_channel_id = generate_message_channel_id()

        group_chat = GroupChat(id=message_channel_id, name=validated_data["name"], owner=current_user,
                               channel_type="GC")
        group_chat.save()

        group_chat.users.add(current_user)
        group_chat.users.add(*users)

        return group_chat

    def update(self, instance, validated_data):
        current_user = self.context["request"].user

        if not instance.users.filter(id=current_user.id).exists():
            raise serializers.ValidationError("Permission Denied.")

        if "users" in validated_data:
            users = validated_data["users"]
            curr_users = set(instance.users.all())
            curr_users.remove(current_user)
            new_users = users.copy()
            if current_user in users:
                new_users.remove(current_user)
            if len(curr_users.intersection(new_users)) != len(curr_users) and \
                    instance.owner.id != current_user.id:
                raise serializers.ValidationError("Permission Denied.")
            if len(users) == 0:
                raise serializers.ValidationError("There must be at least one user in the GC.")

        if "owner" in validated_data:
            owner = validated_data["owner"]
            if instance.owner != owner and current_user != instance.owner:
                raise serializers.ValidationError("Permission Denied.")
            if not instance.users.filter(id=owner.id).exists():
                raise serializers.ValidationError("Owner is not in the GC.")

        instance.name = validated_data.get("name", instance.name)
        instance.owner = validated_data.get("owner", instance.owner)
        instance.users.set(validated_data.get("users", instance.users.all()))

        if not instance.users.filter(id=instance.owner.id).exists():
            instance.owner = instance.users.first()

        instance.save()
        return instance


class MessageSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    message_channel = MessageChannelReaderSerializer()

    class Meta:
        model = Message
        fields = ("id", "user", "created_at", "updated_at", "content", "message_channel")
        read_only_fields = ("id", "user", "created_at", "updated_at", "message_channel")

    def create(self, validated_data):
        if not validated_data["message_channel"].users.filter(username=self.context["user"].username).exists():
            raise serializers.ValidationError("Message channel does not exist.")

        message = Message(user=self.context["user"], content=validated_data["content"],
                          message_channel=validated_data["message_channel"])
        message.save()

        validated_data["message_channel"].message_last_sent = datetime.now()
        validated_data["message_channel"].save()

        return message

    def update(self, instance, validated_data):
        if instance.user.username != self.context["user"].username:
            raise serializers.ValidationError("Message does not exist.")
        instance.content = validated_data.get("content", instance.content)
        instance.save()
        return instance


class AuthenticateWebsocketSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=100)

    def validate_token(self, data):
        try:
            auth = TokenAuthentication().authenticate_credentials(
                data.encode("utf-8"))
            return auth[0]
        except AuthenticationFailed:
            raise serializers.ValidationError("Invalid Token.")

    def validate(self, data):
        if data["token"].username != self.context["user"].username:
            raise serializers.ValidationError("Token does not match user.")
        return data["token"]


class LoadMessageSerializer(serializers.Serializer):
    user = UserSerializer()
    message_channel = MessageChannelSerializer()
    message_id = serializers.IntegerField(default=None)

    def validate(self, data):
        if not data["message_channel"].users.filter(username=data["user"].username).exists():
            raise serializers.ValidationError("Permission denied.")
        return data
