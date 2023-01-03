from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'title', 'description', 'timestamp', 'user', 'read')
        read_only_fields = ('id', 'title', 'description', 'timestamp', 'user')

    def update(self, instance, validated_data):
        instance.read = True
        instance.save()
        return instance
