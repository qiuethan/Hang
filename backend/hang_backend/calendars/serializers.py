import requests
from rest_framework import serializers

from .models import ManualTimeRange, GoogleCalendarAccessToken, ImportedCalendar, GoogleCalendarCalendars, \
    ImportedTimeRange, RepeatingTimeRange, ManualCalendar


class ManualTimeRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManualTimeRange
        fields = ['type', 'start_time', 'end_time']

    def validate_time_divisible_by_15(self, time):
        if time.minute % 15 != 0 or time.second != 0 or time.microsecond != 0:
            raise serializers.ValidationError("The time must end with a number of minutes divisible by 15 and have "
                                              "zero seconds and microseconds.")
        return time

    def validate_start_time(self, value):
        return self.validate_time_divisible_by_15(value)

    def validate_end_time(self, value):
        return self.validate_time_divisible_by_15(value)

    def create(self, validated_data):
        calendar = self.context['calendar']
        new_range = ManualTimeRange(**validated_data, calendar=calendar)

        overlapping_ranges = ManualTimeRange.objects.filter(
            calendar=calendar,
            start_time__lt=new_range.end_time,
            end_time__gt=new_range.start_time
        )

        for overlap in overlapping_ranges:
            if overlap.type != new_range.type:
                temp_start = overlap.start_time
                temp_end = overlap.end_time
                temp_type = overlap.type

                overlap.delete()

                if temp_start < new_range.start_time:
                    ManualTimeRange.objects.create(calendar=calendar, start_time=temp_start,
                                                   end_time=new_range.start_time, type=temp_type)
                if new_range.end_time < temp_end:
                    ManualTimeRange.objects.create(calendar=calendar, start_time=new_range.end_time,
                                                   end_time=temp_end, type=temp_type)
            else:
                new_range.start_time = min(new_range.start_time, overlap.start_time)
                new_range.end_time = max(new_range.end_time, overlap.end_time)
                overlap.delete()

        new_range.save()
        return new_range


class GoogleCalendarAccessTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoogleCalendarAccessToken
        fields = '__all__'
        read_only_fields = ('access_token', 'user')

    @staticmethod
    def fetch_calendar_data(user):
        try:
            access_token = GoogleCalendarAccessToken.objects.get(user=user)
            access_token.refresh_access_token()
        except GoogleCalendarAccessToken.DoesNotExist:
            raise serializers.ValidationError("Access token not found for the current user.")

        url = f'https://www.googleapis.com/calendar/v3/users/me/calendarList?access_token={access_token.access_token}'
        response = requests.get(url)

        if response.status_code != 200:
            raise serializers.ValidationError("Error fetching calendar data.")

        imported_calendar = ImportedCalendar.objects.get(user=user)

        existing_calendars = GoogleCalendarCalendars.objects.filter(calendar=imported_calendar)
        existing_calendar_ids = [calendar.google_calendar_id for calendar in existing_calendars]

        calendar_data = response.json()
        calendar_list = [
            {
                "google_calendar_id": item["id"],
                "name": item["summary"],
                "previous": item["id"] in existing_calendar_ids
            }
            for item in calendar_data["items"]
        ]
        return calendar_list


class GoogleCalendarCalendarsSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=255)


class GoogleCalendarCalendarsListSerializer(serializers.Serializer):
    calendar_data = serializers.ListField(
        child=GoogleCalendarCalendarsSerializer(),
        min_length=1,
        allow_empty=False
    )


class TimeRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportedTimeRange
        fields = ['start_time', 'end_time']


class RepeatingTimeRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepeatingTimeRange
        fields = ("id", "start_time", "end_time", "repeat_interval", "repeat_count")
        read_only_fields = ("id",)

    def create(self, validated_data):
        start_time = validated_data.get('start_time')
        end_time = validated_data.get('end_time')
        repeat_interval = validated_data.get('repeat_interval')
        repeat_count = validated_data.get('repeat_count')

        repeating_time_range = RepeatingTimeRange(
            calendar=ManualCalendar.objects.get(user=self.context["request"].user),
            start_time=start_time,
            end_time=end_time,
            repeat_interval=repeat_interval,
            repeat_count=repeat_count
        )

        repeating_time_range.save()
        return repeating_time_range
