"""
ICS4U
Paul Chen
This module defines the serializer for the Notification model.
"""

from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Notification model.
    """

    class Meta:
        model = Notification
        fields = ('id', 'title', 'description', 'timestamp', 'user', 'read')
        read_only_fields = ('id', 'title', 'description', 'timestamp', 'user', 'read')

    def update(self, instance, validated_data):
        """
        Marks a notification as read when updating.

        Arguments:
          instance (Notification): The Notification instance being updated.
          validated_data (dict): The validated data used for updating, unused here as all fields are read-only.

        Returns:
          Notification: The updated Notification instance.
        """
        instance.set_as_read()
        return instance
