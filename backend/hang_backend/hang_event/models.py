from django.contrib.auth.models import User
from django.db import models


class HangEvent(models.Model):
    """Model for a Hang Event."""
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="hang_events_owned")
    picture = models.CharField(max_length=200)
    description = models.TextField()
    scheduled_time_start = models.DateTimeField()
    scheduled_time_end = models.DateTimeField()
    longitude = models.FloatField(default=None, null=True)
    latitude = models.FloatField(default=None, null=True)
    address = models.TextField()
    budget = models.FloatField(default=None, null=True)
    attendees = models.ManyToManyField(User, related_name="hang_events")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    google_calendar_event_id = models.CharField(max_length=256, default=None, null=True)


class Task(models.Model):
    event = models.ForeignKey(HangEvent, related_name="tasks", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    completed = models.BooleanField(default=False)
