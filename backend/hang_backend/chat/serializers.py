from rest_framework import serializers

from .models import Message


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField(max_length=200)


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
