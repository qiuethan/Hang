import random
import string

from django.contrib.auth.models import User
from django.core import exceptions
from django.db import models

from chats.models import MessageChannel, HangEventMessageChannel, SystemMessage
from real_time_ws.models import RTWSSendMessageOnUpdate


def generate_random_string():
    """Utility method to generate a random string."""
    return "".join([random.choice(string.ascii_letters) for _ in range(10)])


def generate_unique_invitation_code():
    """Utility method to generate a random id for a MessageChannel."""
    code = generate_random_string()
    while HangEvent.objects.filter(invitation_code=code).exists():
        code = generate_random_string()
    return code


class HangEvent(models.Model, RTWSSendMessageOnUpdate):
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
    invitation_code = models.CharField(max_length=10,
                                       default=generate_unique_invitation_code,
                                       unique=True)
    message_channel = models.OneToOneField(HangEventMessageChannel, on_delete=models.CASCADE, default=None, null=True)
    archived = models.BooleanField(default=False)

    rtws_message_content = "hang_event"

    def get_rtws_users(self):
        return list(self.attendees.all())

    def __init__(self, *args, **kwargs):
        super(HangEvent, self).__init__(*args, **kwargs)
        for field in self._meta.fields:
            if field.name in ["name", "owner", "description", "scheduled_time_start", "scheduled_time_end", "address"]:
                setattr(self, f"_old_{field.name}", getattr(self, field.name))

    def save(self, *args, **kwargs):
        is_new = not self.pk
        super(HangEvent, self).save(*args, **kwargs)

        if is_new:
            message_channel = MessageChannel.objects.create_hang_event_message_channel(self)
            self.message_channel = message_channel
            self.save()

    @staticmethod
    def add_user_through_invitation_code(invitation_code, user):
        hang_event = HangEvent.objects.filter(invitation_code=invitation_code).get()

        if hang_event.archived:
            raise exceptions.ValidationError("This HangEvent has been archived")

        if user in hang_event.attendees.all():
            raise exceptions.ValidationError("You are already an attendee of this HangEvent")

        hang_event.attendees.add(user)
        hang_event.save()
        return hang_event


class Task(models.Model, RTWSSendMessageOnUpdate):
    event = models.ForeignKey(HangEvent, related_name="tasks", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    completed = models.BooleanField(default=False)

    rtws_message_content = "hang_event"

    def get_rtws_users(self):
        return list(self.event.attendees.all())
