"""
ICS4U
Paul Chen
This module provides serializers for handling calendar data in a Django application. It includes serializers for different types of time ranges and Google Calendar data.
"""

from datetime import timedelta

from django.contrib.auth.models import User
from rest_framework import serializers

from hang_events.models import HangEvent
from .models import ManualTimeRange, ImportedTimeRange, RepeatingTimeRange


class TimeRangeSerializer(serializers.ModelSerializer):
    """
    Serializer for the ImportedTimeRange model. It serializes the start and end times of an imported time range.
    """
    class Meta:
        model = ImportedTimeRange
        fields = ['start_time', 'end_time']


class ManualTimeRangeSerializer(serializers.ModelSerializer):
    """
    Serializer for the ManualTimeRange model. It serializes the type, start time, and end time of a manual time range.
    """
    class Meta:
        model = ManualTimeRange
        fields = ['type', 'start_time', 'end_time']

    @staticmethod
    def validate_time_divisible_by_15(time):
        """
        Validates that the given time is divisible by 15 minutes.

        Arguments:
          time (datetime): The time to validate.

        Returns:
          datetime: The validated time.
        """
        if time.minute % 15 != 0 or time.second != 0 or time.microsecond != 0:
            raise serializers.ValidationError("The time must end with a number of minutes divisible by 15 and have "
                                              "zero seconds and microseconds.")
        return time

    def validate_start_time(self, value):
        """
        Validates the start time of a manual time range.

        Arguments:
          value (datetime): The start time to validate.

        Returns:
          datetime: The validated start time.
        """
        return self.validate_time_divisible_by_15(value)

    def validate_end_time(self, value):
        """
        Validates the end time of a manual time range.

        Arguments:
          value (datetime): The end time to validate.

        Returns:
          datetime: The validated end time.
        """
        return self.validate_time_divisible_by_15(value)

    def create(self, validated_data):
        """
        Creates a new ManualTimeRange instance.

        Arguments:
          validated_data (dict): The validated data for the new ManualTimeRange.

        Returns:
          ManualTimeRange: The created ManualTimeRange instance.
        """
        # Retrieve the calendar from the context
        calendar = self.context['calendar']
        new_range = ManualTimeRange(**validated_data, calendar=calendar)

        # Identify any time ranges that overlap with the new range
        overlapping_ranges = ManualTimeRange.objects.filter(
            calendar=calendar,
            start_time__lt=new_range.end_time,
            end_time__gt=new_range.start_time
        )

        # Process overlaps
        for overlap in overlapping_ranges:
            if overlap.type != new_range.type:
                temp_start = overlap.start_time
                temp_end = overlap.end_time
                temp_type = overlap.type

                overlap.delete()

                # If the old range partially overlaps with the new range, create new ranges for the non-overlapping parts
                if temp_start < new_range.start_time:
                    ManualTimeRange.objects.create(calendar=calendar, start_time=temp_start,
                                                   end_time=new_range.start_time, type=temp_type)
                if new_range.end_time < temp_end:
                    ManualTimeRange.objects.create(calendar=calendar, start_time=new_range.end_time,
                                                   end_time=temp_end, type=temp_type)
            else:
                # If the old range fully overlaps with the new range and they are of the same type, merge them
                new_range.start_time = min(new_range.start_time, overlap.start_time)
                new_range.end_time = max(new_range.end_time, overlap.end_time)
                overlap.delete()

        new_range.save()
        return new_range


class RepeatingTimeRangeSerializer(serializers.ModelSerializer):
    """
    Serializer for the RepeatingTimeRange model. It serializes the start time, end time, repeat interval, and repeat count of a repeating time range.
    """
    class Meta:
        model = RepeatingTimeRange
        fields = ("id", "start_time", "end_time", "repeat_interval", "repeat_count")
        read_only_fields = ("id",)

    def create(self, validated_data):
        """
        Creates a new RepeatingTimeRange instance.

        Arguments:
          validated_data (dict): The validated data for the new RepeatingTimeRange.

        Returns:
          RepeatingTimeRange: The created RepeatingTimeRange instance.
        """
        validated_data["calendar"] = validated_data["manual_calendar"]
        del validated_data["manual_calendar"]
        repeating_time_range = RepeatingTimeRange(**validated_data)

        repeating_time_range.save()
        return repeating_time_range


class GoogleCalendarSerializer(serializers.Serializer):
    """
    Serializer for Google Calendar data. It serializes the ID and name of a Google Calendar.
    """
    id = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=255)


class FreeTimeRangesSerializer(serializers.Serializer):
    """
    Serializer for free time ranges. It serializes the hang event, users, start time, and end time of a free time range.
    """
    hang_event = serializers.PrimaryKeyRelatedField(queryset=HangEvent.objects.all())
    users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()

    def validate(self, data):
        """
        Validates the data for a free time range.

        Arguments:
          data (dict): The data to validate.

        Returns:
          dict: The validated data.
        """
        event = data['hang_event']
        # Ensure the user has the necessary permissions
        if self.context["request"].user not in event.attendees.all() \
                or not all(event.attendees.filter(id=user.id).exists() for user in (data['users'])) or \
                event.archived:
            raise serializers.ValidationError("Invalid Permissions")

        # Ensure the time range does not exceed one month
        time_difference = data['end_time'] - data['start_time']
        max_difference = timedelta(days=35)

        if time_difference > max_difference:
            raise serializers.ValidationError(
                "The time range between start_time and end_time cannot be more than a month."
            )

        return data


class UserFreeDuringRangeSerializer(serializers.Serializer):
    """
    Serializer for checking if a user is free during a certain time range. It serializes the hang event, users, start time, and end time.
    """
    hang_event = serializers.PrimaryKeyRelatedField(queryset=HangEvent.objects.all())
    users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, default=[])
    start_time = serializers.DateTimeField(required=True)
    end_time = serializers.DateTimeField(required=True)

    def validate(self, data):
        """
        Validates the data for a user's free time range.

        Arguments:
          data (dict): The data to validate.

        Returns:
          dict: The validated data.
        """
        event = data['hang_event']
        # Ensure the user has the necessary permissions
        if self.context["request"].user not in event.attendees.all() \
                or not all(event.attendees.filter(id=user.id).exists() for user in (data['users'])) or \
                event.archived:
            raise serializers.ValidationError("Invalid Permissions")
        # Ensure the time range does not exceed one month
        if data['end_time'] - data['start_time'] > timedelta(days=35):
            raise serializers.ValidationError(
                "The time range between start_time and end_time cannot be more than a month.")

        return data
