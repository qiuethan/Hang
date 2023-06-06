"""
ICS4U
Paul Chen
This module contains serializers for the Task and HangEvent models.
"""

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField

from hang_events.models import HangEvent, Task


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for the Task model."""
    event = serializers.PrimaryKeyRelatedField(queryset=HangEvent.objects.all())

    class Meta:
        model = Task
        fields = ('id', 'event', 'name', 'completed')
        read_only_fields = ("id", "event")

    def validate_event(self, value):
        """
        Validate the event attribute.

        Arguments:
          value (HangEvent): The HangEvent instance to validate.

        Returns:
          HangEvent: The validated HangEvent instance.
        """
        if value.archived:
            raise serializers.ValidationError("Cannot create a Task for an archived HangEvent.")
        if self.context["request"].user not in value.attendees.all():
            raise serializers.ValidationError("HangEvent does not exist.")
        return value

    def update(self, instance, validated_data):
        """
        Update a Task instance.

        Arguments:
          instance (Task): The Task instance to update.
          validated_data (dict): The validated data.

        Returns:
          Task: The updated Task instance.
        """
        if "event" in validated_data:
            raise serializers.ValidationError("Cannot change HangEvent of Task.")
        return super().update(instance, validated_data)


class HangEventSerializer(serializers.ModelSerializer):
    """Serializer for the HangEvent model."""
    tasks = TaskSerializer(many=True, read_only=True)
    attendees = PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, many=True)
    message_channel_has_read = SerializerMethodField(read_only=True)

    class Meta:
        model = HangEvent
        fields = (
            'id', 'name', 'owner', 'picture', 'description', 'scheduled_time_start', 'scheduled_time_end', 'longitude',
            'latitude', 'address', 'budget', 'attendees', 'tasks', 'created_at', 'updated_at', 'message_channel',
            'message_channel_has_read',)
        read_only_fields = ('message_channel', "message_channel_has_read")

    def get_message_channel_has_read(self, obj):
        """
        Check if the message channel has been read by the current user.

        Arguments:
          obj (HangEvent): The HangEvent instance.

        Returns:
          bool: True if the message channel has been read, False otherwise.
        """
        return obj.message_channel.has_read_message_channel(self.context["request"].user)

    def validate_longitude(self, value):
        """
        Validate the longitude attribute.

        Arguments:
          value (float): The longitude value to validate.

        Returns:
          float: The validated longitude value.
        """
        if value is not None and not (-180 <= value <= 180):
            raise serializers.ValidationError("Invalid longitude value.")
        return value

    def validate_latitude(self, value):
        """
        Validate the latitude attribute.

        Arguments:
          value (float): The latitude value to validate.

        Returns:
          float: The validated latitude value.
        """
        if value is not None and not (-90 <= value <= 90):
            raise serializers.ValidationError("Invalid latitude value.")
        return value

    def create(self, validated_data):
        """
        Create a HangEvent instance.

        Arguments:
          validated_data (dict): The validated data.

        Returns:
          HangEvent: The created HangEvent instance.
        """
        current_user = self.context["request"].user
        validated_data["owner"] = current_user
        if"attendees" in validated_data:
            del validated_data["attendees"]

        hang_event = HangEvent.objects.create(**validated_data)
        hang_event.attendees.set([current_user])

        return hang_event

    def update(self, instance, validated_data):
        """
        Update a HangEvent instance.

        Arguments:
          instance (HangEvent): The HangEvent instance to update.
          validated_data (dict): The validated data.

        Returns:
          HangEvent: The updated HangEvent instance.
        """
        current_user = self.context["request"].user
        self.verify_permission(instance, current_user, validated_data)

        instance = self.update_fields(instance, validated_data)
        instance.save()

        self.transfer_ownership(instance)

        return instance

    def verify_permission(self, instance, current_user, validated_data):
        """
        Verify the permission of the current user.

        Arguments:
          instance (HangEvent): The HangEvent instance.
          current_user (User): The current user.
          validated_data (dict): The validated data.
        """
        if not instance.attendees.filter(id=current_user.id).exists():
            raise serializers.ValidationError("Permission Denied.")

        if "attendees" in validated_data:
            self.verify_attendees_permission(instance, current_user, validated_data["attendees"])

        if "owner" in validated_data:
            self.verify_owner_permission(instance, current_user, validated_data["owner"])

    def verify_attendees_permission(self, instance, current_user, attendees):
        """
        Verify the permission of the attendees.

        Arguments:
          instance (HangEvent): The HangEvent instance.
          current_user (User): The current user.
          attendees (list): The list of attendees.
        """
        curr_attendees = set(instance.attendees.all())
        new_attendees = set(attendees.copy())

        curr_attendees.remove(current_user)
        if current_user in attendees:
            new_attendees.remove(current_user)

        if len(curr_attendees.union(new_attendees)) != len(curr_attendees) or (
                len(curr_attendees.intersection(new_attendees)) != len(curr_attendees) and
                instance.owner.id != current_user.id):
            raise serializers.ValidationError("Permission Denied.")

    def verify_owner_permission(self, instance, current_user, owner):
        """
        Verify the permission of the owner.

        Arguments:
          instance (HangEvent): The HangEvent instance.
          current_user (User): The current user.
          owner (User): The owner.
        """
        if instance.owner != owner and current_user != instance.owner:
            raise serializers.ValidationError("Permission Denied.")
        if not instance.attendees.filter(id=owner.id).exists():
            raise serializers.ValidationError("Owner is not in the GC.")

    def update_fields(self, instance, validated_data):
        """
        Update the fields of a HangEvent instance.

        Arguments:
          instance (HangEvent): The HangEvent instance.
          validated_data (dict): The validated data.

        Returns:
          HangEvent: The updated HangEvent instance.
        """
        for field in ('name', 'picture', 'description', 'scheduled_time_start', 'scheduled_time_end', 'longitude',
                      'latitude', 'budget', 'owner'):
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        if "attendees" in validated_data:
            instance.attendees.set(validated_data["attendees"])

        return instance

    def transfer_ownership(self, instance):
        """
        Transfer the ownership of a HangEvent instance.

        Arguments:
          instance (HangEvent): The HangEvent instance.
        """
        if not instance.attendees.filter(id=instance.owner.id).exists():
            if instance.attendees.exists():
                instance.owner = instance.attendees.first()
            else:
                instance.owner = None
            instance.save()
