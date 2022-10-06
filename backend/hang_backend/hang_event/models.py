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
    budget = models.FloatField(default=None, null=True)
    attendees = models.ManyToManyField(User, related_name="hang_events")
    needs = models.JSONField()
    tasks = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
