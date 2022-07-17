from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Message, MessageChannel


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email')

    def validate(self, data):
        return User.objects.get(username=data['username'])


class MessageChannelSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=10)


class MessageSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user = UserSerializer()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    content = serializers.CharField(max_length=2000)
    message_channel = MessageChannelSerializer()

    def create(self, validated_data):
        return Message.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.id = validated_data.get('id', instance.id)
        instance.user = validated_data.get('user', instance.user)
        instance.created_at = validated_data.get('created_at', instance.created)
        instance.updated_at = validated_data.get('updated_at', instance.updated_at)
        instance.content = validated_data.get('content', instance.content)
        instance.message_channel = validated_data.get('message_channel', instance.message_channel)
        instance.save()
        return instance


class CreateDMSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, data):
        if not User.objects.filter(email=data).exists():
            raise serializers.ValidationError("The email is not associated with an account.")
        return data

    def validate(self, data):
        return User.objects.get(email=data['email'])


class SendMessageSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    message_channel = serializers.CharField()
    content = serializers.CharField()

    class Meta:
        model = Message
        fields = ('user', 'message_channel', 'content')

    def validate_message_channel(self, data):
        if not MessageChannel.objects.filter(id=data).exists():
            raise serializers.ValidationError("The message channel does not exist.")
        return data

    def validate_content(self, data):
        if len(data) > 2000:
            raise serializers.ValidationError("Messages cannot be over 2000 characters long.")
        return data

    def validate(self, data):
        if not MessageChannel.objects.filter(id=data['message_channel']).get().users.filter(
                username=data['user'].username).exists():
            raise serializers.ValidationError("Permission denied.")
        return data

    def create(self, data):
        message = Message(user=data['user'], content=data['content'],
                          message_channel=MessageChannel.objects.get(id=data['message_channel']))
        message.save()
        return message
