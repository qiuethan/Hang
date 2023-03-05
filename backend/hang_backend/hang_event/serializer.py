from rest_framework import serializers

from hang_event.models import HangEvent, Task


class TaskSerializer(serializers.ModelSerializer):
    event = serializers.PrimaryKeyRelatedField(queryset=HangEvent.objects.all())

    class Meta:
        model = Task
        fields = ('id', 'event', 'name', 'completed')
        read_only_fields = ("id", "event")


class HangEventSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    def validate_longitude(self, value):
        if value is not None and not (-180 <= value <= 180):
            raise serializers.ValidationError("Invalid longitude value.")
        return value

    def validate_latitude(self, value):
        if value is not None and not (-90 <= value <= 90):
            raise serializers.ValidationError("Invalid latitude value.")
        return value

    def validate_owner(self, value):
        attendees = self.initial_data["attendees"]
        if value.id not in attendees:
            raise serializers.ValidationError("Owner must be included in the list of attendees.")
        return value

    class Meta:
        model = HangEvent
        fields = (
            'id', 'name', 'owner', 'picture', 'description', 'scheduled_time_start', 'scheduled_time_end', 'longitude',
            'latitude', 'budget', 'attendees', 'tasks', 'created_at', 'updated_at')

    def update(self, instance, validated_data):
        current_user = self.context["request"].user

        # Verifies if the user is in Hang event.
        if not instance.attendees.filter(id=current_user.id).exists():
            raise serializers.ValidationError("Permission Denied.")

        if "attendees" in validated_data:
            # User can only add more attendees / leave a Hang event; owner can remove user.
            attendees = validated_data["attendees"]
            curr_attendees = set(instance.attendees.all())
            new_attendees = set(attendees.copy())

            curr_attendees.remove(current_user)
            if current_user in attendees:
                new_attendees.remove(current_user)

            if len(curr_attendees.intersection(new_attendees)) != len(curr_attendees) and \
                    instance.owner.id != current_user.id:
                raise serializers.ValidationError("Permission Denied.")

        if "owner" in validated_data:
            # Only owner can transfer ownership.
            owner = validated_data["owner"]
            if instance.owner != owner and current_user != instance.owner:
                raise serializers.ValidationError("Permission Denied.")
            if not instance.attendees.filter(id=owner.id).exists():
                raise serializers.ValidationError("Owner is not in the GC.")

        # Update fields.
        instance.name = validated_data.get('name', instance.name)
        instance.picture = validated_data.get('picture', instance.picture)
        instance.description = validated_data.get('description', instance.description)
        instance.scheduled_time_start = validated_data.get('scheduled_time_start', instance.scheduled_time_start)
        instance.scheduled_time_end = validated_data.get('scheduled_time_end', instance.scheduled_time_end)
        instance.longitude = validated_data.get('longitude', instance.longitude)
        instance.latitude = validated_data.get('latitude', instance.latitude)
        instance.budget = validated_data.get('budget', instance.budget)
        instance.owner = validated_data.get("owner", instance.owner)
        instance.attendees.set(validated_data.get("attendees", instance.attendees.all()))
        instance.save()

        # Transfer ownership if the owner leaves.
        if not instance.attendees.filter(id=instance.owner.id).exists():
            if instance.attendees.exists():
                instance.owner = instance.attendees.first()
            else:
                instance.owner = None

        instance.save()
        return instance
