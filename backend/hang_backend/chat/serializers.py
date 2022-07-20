from django.contrib.auth.models import User
from knox.auth import TokenAuthentication
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from .models import Message, MessageChannel


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(default=None)
    username = serializers.CharField(default=None)
    email = serializers.EmailField(default=None)

    class Meta:
        model = User
        fields = ('id', 'username', 'email')

    def validate_id(self, data):
        if data is not None and not User.objects.filter(id=data).exists():
            raise serializers.ValidationError("The user does not exist.")
        return data

    def validate_username(self, data):
        if data is not None and not User.objects.filter(username=data).exists():
            raise serializers.ValidationError("The user does not exist.")
        return data

    def validate_email(self, data):
        if data is not None and not User.objects.filter(email=data).exists():
            raise serializers.ValidationError("The user does not exist.")
        return data

    def validate(self, data):
        if data['id'] is not None:
            return User.objects.get(id=data['id'])
        if data['username'] is not None:
            return User.objects.get(username=data['username'])
        if data['email'] is not None:
            return User.objects.get(email=data['email'])
        raise serializers.ValidationError("One of id, username, and email must be present.")


class MessageChannelSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=10)

    class Meta:
        model = MessageChannel
        fields = ("id", "name", "channel_type")
        read_only_fields = ["name", "channel_type"]

    def validate_id(self, data):
        if not MessageChannel.objects.filter(id=data).exists():
            raise serializers.ValidationError("The message channel does not exist.")
        return data

    def validate(self, data):
        return MessageChannel.objects.get(id=data['id'])


class MessageChannelFullSerializer(serializers.ModelSerializer):
    users = serializers.ListSerializer(child=UserSerializer())

    class Meta:
        model = MessageChannel
        fields = ("id", "name", "users", "channel_type")
        read_only_fields = ["id", "name", "users", "channel_type"]


class MessageSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user = UserSerializer()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    content = serializers.CharField(max_length=2000)
    message_channel = MessageChannelSerializer()


class CreateDMSerializer(serializers.Serializer):
    user = UserSerializer()

    def validate(self, data):
        return User.objects.get(id=data['user'].id)


class CreateGCSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=75)
    users = serializers.ListSerializer(child=UserSerializer())


class AuthenticateWebsocketSerializer(serializers.Serializer):
    user = UserSerializer()
    token = serializers.CharField(max_length=100)

    def validate_token(self, data):
        try:
            auth = TokenAuthentication().authenticate_credentials(
                data.encode('utf-8'))
            return auth[0]
        except AuthenticationFailed:
            raise serializers.ValidationError("Invalid Token.")

    def validate(self, data):
        if data["token"].username != data["user"].username:
            raise serializers.ValidationError("Token does not match user.")
        return data["token"]


class SendMessageSerializer(serializers.Serializer):
    user = UserSerializer()
    message_channel = MessageChannelSerializer()
    content = serializers.CharField(max_length=2000)

    def validate_content(self, data):
        if len(data) > 2000:
            raise serializers.ValidationError("Messages cannot be over 2000 characters long.")
        return data

    def validate(self, data):
        if not data['message_channel'].users.filter(username=data['user'].username).exists():
            raise serializers.ValidationError("Permission denied.")
        return data

    def create(self, data):
        message = Message(user=data['user'], content=data['content'],
                          message_channel=data['message_channel'])
        message.save()
        return message


class LoadMessageSerializer(serializers.Serializer):
    user = UserSerializer()
    message_channel = MessageChannelSerializer()
    message_id = serializers.IntegerField(default=None)

    def validate(self, data):
        if not data['message_channel'].users.filter(username=data['user'].username).exists():
            raise serializers.ValidationError("Permission denied.")
        return data


class EditMessageSerializer(serializers.Serializer):
    user = UserSerializer()
    message_id = serializers.IntegerField()
    content = serializers.CharField(max_length=2000)

    def validate_message_id(self, data):
        if not Message.objects.filter(id=data).exists():
            raise serializers.ValidationError("The message does not exist.")
        return data

    def validate_content(self, data):
        if len(data) > 2000:
            raise serializers.ValidationError("Messages cannot be over 2000 characters long.")
        return data

    def validate(self, data):
        if not Message.objects.filter(id=data["message_id"]).get().user.username == data["user"].username:
            raise serializers.ValidationError("Permission denied.")
        return data


class DeleteMessageSerializer(serializers.Serializer):
    user = UserSerializer()
    message_id = serializers.IntegerField()

    def validate_message_id(self, data):
        if not Message.objects.filter(id=data).exists():
            raise serializers.ValidationError("The message does not exist.")
        return data

    def validate(self, data):
        if not Message.objects.filter(id=data["message_id"]).get().user.username == data["user"].username:
            raise serializers.ValidationError("Permission denied.")
        return data
