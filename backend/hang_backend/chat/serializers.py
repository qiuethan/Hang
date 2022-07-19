from django.contrib.auth.models import User
from rest_framework import serializers

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


class MessageChannelSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=10)

    class Meta:
        model = MessageChannel
        fields = ('id')

    def validate_id(self, data):
        if not MessageChannel.objects.filter(id=data).exists():
            raise serializers.ValidationError("The message channel does not exist.")
        return data

    def validate(self, data):
        return MessageChannel.objects.get(id=data['id'])


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


class SendMessageSerializer(serializers.Serializer):
    user = UserSerializer()
    message_channel = MessageChannelSerializer()
    content = serializers.CharField()

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
    content = serializers.CharField()

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
