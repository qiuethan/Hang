from django.contrib.auth.models import User
from django.db import models


class ManualCalendar(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)


class ImportedCalendar(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)


class GoogleCalendarAccessToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=512)


class GoogleCalendarCalendars(models.Model):
    calendar = models.ForeignKey(ImportedCalendar, on_delete=models.CASCADE)
    google_calendar_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)


class ManualTimeRange(models.Model):
    calendar = models.ForeignKey(ManualCalendar, on_delete=models.CASCADE)
    type = models.CharField(max_length=4, choices=(("busy", "busy"), ("free", "free")))
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


class ImportedTimeRange(models.Model):
    calendar = models.ForeignKey(ImportedCalendar, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
