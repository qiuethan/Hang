from datetime import datetime, timezone

import requests
from django.contrib.auth.models import User
from django.db import models

from hang_backend import settings


class ManualCalendar(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)


class ImportedCalendar(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)


class GoogleCalendarAccessToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=512)
    refresh_token = models.CharField(max_length=1024)
    last_generated = models.DateTimeField(default=datetime.now)

    def needs_refresh(self):
        refresh_threshold = 3600  # Set the time threshold for refreshing the token (in seconds)
        elapsed_time = (datetime.now(timezone.utc) - self.last_generated).total_seconds()
        return elapsed_time >= refresh_threshold

    def refresh_access_token(self):
        if self.needs_refresh():
            # Make a request to Google API to refresh the access token
            url = 'https://oauth2.googleapis.com/token'
            data = {
                'refresh_token': self.refresh_token,
                'client_id': settings.GOOGLE_CLIENT_ID,
                'client_secret': settings.GOOGLE_CLIENT_SECRET,
                'grant_type': 'refresh_token',
            }
            response = requests.post(url, data=data)
            response_json = response.json()
            access_token = response_json.get('access_token')

            if access_token:
                self.access_token = access_token
                self.last_generated = datetime.now()
                self.save()
            else:
                raise ValueError("Failed to refresh the access token")


class GoogleCalendarCalendars(models.Model):
    calendar = models.ForeignKey(ImportedCalendar, on_delete=models.CASCADE)
    google_calendar_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)


class ManualTimeRange(models.Model):
    calendar = models.ForeignKey(ManualCalendar, on_delete=models.CASCADE)
    type = models.CharField(max_length=4, choices=(("busy", "busy"), ("free", "free")))
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


class RepeatingTimeRange(models.Model):
    calendar = models.ForeignKey(ManualCalendar, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    repeat_interval = models.IntegerField()  # Repeat every x weeks
    repeat_count = models.IntegerField()  # Number of times the event repeats


class ImportedTimeRange(models.Model):
    calendar = models.ForeignKey(ImportedCalendar, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
