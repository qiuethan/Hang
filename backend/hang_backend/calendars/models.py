import json
from datetime import datetime, timedelta

from dateutil.parser import parse
from django.contrib.auth.models import User
from django.db import models
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from rest_framework import serializers

from accounts.models import GoogleAuthenticationToken
from real_time_ws.models import RTWSSendMessageOnUpdate


class ManualCalendar(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)


class ImportedCalendar(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)


class GoogleCalendar(models.Model):
    calendar = models.ForeignKey(ImportedCalendar, on_delete=models.CASCADE)
    google_calendar_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    @staticmethod
    def fetch_free_busy_ranges(authentication_token, calendar_data_list):
        time_min = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        time_ranges = []

        credentials = Credentials(token=authentication_token.access_token)
        service = build('calendar', 'v3', credentials=credentials)

        for i in range(6):
            time_max = (datetime.utcnow() + timedelta(days=(i + 1) * 60)).replace(
                microsecond=0).isoformat() + "Z"

            data = {
                "timeMin": time_min,
                "timeMax": time_max,
                "items": [{"id": cal_data['id']} for cal_data in calendar_data_list]
            }
            try:
                response = service.freebusy().query(body=data).execute()
            except HttpError as error:
                raise Exception(f"An error occurred: {error}")

            result = json.loads(json.dumps(response))

            for cal_data in calendar_data_list:
                cal_id = cal_data['id']
                cal_info = result['calendars'][cal_id]
                for busy_range in cal_info['busy']:
                    time_ranges.append(
                        ImportedTimeRange(
                            start_time=parse(busy_range['start']),
                            end_time=parse(busy_range['end']),
                            calendar=authentication_token.user.importedcalendar
                        )
                    )
            time_min = time_max

        return time_ranges

    @staticmethod
    def sync_google_calendar(imported_calendar, calendar_data_list):
        # Delete existing GoogleCalendarCalendars and add new ones
        GoogleCalendar.objects.filter(calendar=imported_calendar).delete()
        for cal_data in calendar_data_list:
            GoogleCalendar.objects.create(
                calendar=imported_calendar,
                google_calendar_id=cal_data['id'],
                name=cal_data['name']
            )

    @staticmethod
    def fetch_calendar_data(user):
        try:
            access_token = GoogleAuthenticationToken.objects.get(user=user)
            access_token.refresh_access_token()
        except GoogleAuthenticationToken.DoesNotExist:
            raise serializers.ValidationError("Access token not found for the current user.")

        credentials = Credentials(token=access_token.access_token)

        try:
            service = build('calendar', 'v3', credentials=credentials)
            calendar_list = service.calendarList().list().execute()
        except HttpError as error:
            raise serializers.ValidationError(f"Error fetching calendar data: {error}")

        existing_calendars = GoogleCalendar.objects.filter(calendar__user=user)
        existing_calendar_ids = [calendar.google_calendar_id for calendar in existing_calendars]

        calendar_list_data = [
            {
                "google_calendar_id": item["id"],
                "name": item["summary"],
                "previous": item["id"] in existing_calendar_ids
            }
            for item in calendar_list["items"]
        ]
        return calendar_list_data


class ManualTimeRange(models.Model, RTWSSendMessageOnUpdate):
    calendar = models.ForeignKey(ManualCalendar, on_delete=models.CASCADE)
    type = models.CharField(max_length=4, choices=(("busy", "busy"), ("free", "free")))
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    rtws_message_content = "calendar"

    def get_rtws_users(self):
        return [self.calendar.user]


class RepeatingTimeRange(models.Model, RTWSSendMessageOnUpdate):
    calendar = models.ForeignKey(ManualCalendar, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    repeat_interval = models.IntegerField()  # Repeat every x weeks
    repeat_count = models.IntegerField()  # Number of times the event repeats

    rtws_message_content = "calendar"

    def get_rtws_users(self):
        return [self.calendar.user]

    def decompress(self, decompress_start_time):
        start_time = self.start_time
        end_time = self.end_time
        if self.repeat_count == -1:
            # Calculate the number of intervals needed to reach decompress_start_time
            intervals_to_reach_start = max(0, (decompress_start_time - start_time).days // (7 * self.repeat_interval))
            start_time += timedelta(weeks=intervals_to_reach_start * self.repeat_interval)
            end_time += timedelta(weeks=intervals_to_reach_start * self.repeat_interval)
        else:
            # Calculate the final range start_time and end_time
            final_end_time = end_time + timedelta(weeks=self.repeat_interval * (self.repeat_count - 1))

            # If decompress_start_time is after the final range, return an empty list
            if decompress_start_time > final_end_time:
                return []

        decompressed_ranges = []
        while len(decompressed_ranges) < 60:
            if start_time >= decompress_start_time:
                decompressed_ranges.append((start_time, end_time))

            start_time += timedelta(weeks=self.repeat_interval)
            end_time += timedelta(weeks=self.repeat_interval)

            if self.repeat_count != -1 and start_time > final_end_time:
                break

        return decompressed_ranges


class ImportedTimeRange(models.Model, RTWSSendMessageOnUpdate):
    calendar = models.ForeignKey(ImportedCalendar, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    rtws_message_content = "calendar"

    def get_rtws_users(self):
        return [self.calendar.user]
