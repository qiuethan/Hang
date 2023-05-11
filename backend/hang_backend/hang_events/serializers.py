from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from hang_events.models import HangEvent, Task


class TaskSerializer(serializers.ModelSerializer):
    event = serializers.PrimaryKeyRelatedField(queryset=HangEvent.objects.all())

    class Meta:
        model = Task
        fields = ('id', 'event', 'name', 'completed')
        read_only_fields = ("id", "event")

    def validate_event(self, value):
        if value.archived:
            raise serializers.ValidationError("Cannot create a Task for an archived HangEvent.")
        return value


class HangEventSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    attendees = PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, many=True)

    class Meta:
        model = HangEvent
        fields = (
            'id', 'name', 'owner', 'picture', 'description', 'scheduled_time_start', 'scheduled_time_end', 'longitude',
            'latitude', 'address', 'budget', 'attendees', 'tasks', 'created_at', 'updated_at', 'message_channel')
        read_only_fields = ('message_channel',)

    def validate_longitude(self, value):
        if value is not None and not (-180 <= value <= 180):
            raise serializers.ValidationError("Invalid longitude value.")
        return value

    def validate_latitude(self, value):
        if value is not None and not (-90 <= value <= 90):
            raise serializers.ValidationError("Invalid latitude value.")
        return value

    def create(self, validated_data):
        current_user = self.context["request"].user
        validated_data["owner"] = current_user
        if "attendees" in validated_data:
            del validated_data["attendees"]

        hang_event = HangEvent.objects.create(**validated_data)
        hang_event.attendees.set([current_user])

        return hang_event

    def update(self, instance, validated_data):
        current_user = self.context["request"].user
        self.verify_permission(instance, current_user, validated_data)

        instance = self.update_fields(instance, validated_data)
        instance.save()

        self.transfer_ownership(instance)

        return instance

    def verify_permission(self, instance, current_user, validated_data):
        if not instance.attendees.filter(id=current_user.id).exists():
            raise serializers.ValidationError("Permission Denied.")

        if "attendees" in validated_data:
            self.verify_attendees_permission(instance, current_user, validated_data["attendees"])

        if "owner" in validated_data:
            self.verify_owner_permission(instance, current_user, validated_data["owner"])

    def verify_attendees_permission(self, instance, current_user, attendees):
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
        if instance.owner != owner and current_user != instance.owner:
            raise serializers.ValidationError("Permission Denied.")
        if not instance.attendees.filter(id=owner.id).exists():
            raise serializers.ValidationError("Owner is not in the GC.")

    def update_fields(self, instance, validated_data):
        for field in ('name', 'picture', 'description', 'scheduled_time_start', 'scheduled_time_end', 'longitude',
                      'latitude', 'budget', 'owner', 'attendees'):
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        return instance

    def transfer_ownership(self, instance):
        if not instance.attendees.filter(id=instance.owner.id).exists():
            if instance.attendees.exists():
                instance.owner = instance.attendees.first()
            else:
                instance.owner = None
            instance.save()
