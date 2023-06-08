"""
ICS4U
Paul Chen
This module defines the models for the hang_events package.
"""

import random
import string

from django.contrib.auth.models import User
from django.core import exceptions
from django.db import models

from chats.models import MessageChannel, HangEventMessageChannel, SystemMessage
from real_time_ws.models import RTWSSendMessageOnUpdate


def generate_random_string():
    """
    Generates a random string of 10 characters.

    Returns:
      str: A random string of 10 characters.
    """
    return "".join([random.choice(string.ascii_letters) for _ in range(10)])


def generate_unique_invitation_code():
    """
    Generates a unique invitation code for a HangEvent.

    Returns:
      str: A unique invitation code.
    """
    code = generate_random_string()
    while HangEvent.objects.filter(invitation_code=code).exists():
        code = generate_random_string()
    return code


class HangEvent(models.Model, RTWSSendMessageOnUpdate):
    """
    Model that represents an event that users are planning.

    Attributes:
      name (str): The name of the event.
      owner (User): The user who owns the event.
      picture (str): The picture associated with the event.
      description (str): The description of the event.
      scheduled_time_start (datetime): The start time of the event.
      scheduled_time_end (datetime): The end time of the event.
      longitude (float): The longitude of the event location.
      latitude (float): The latitude of the event location.
      address (str): The address of the event location.
      budget (float): The budget for the event.
      attendees (User): The users attending the event.
      created_at (datetime): The time the event was created.
      updated_at (datetime): The time the event was last updated.
      google_calendar_event_id (str): The ID of the event in Google Calendar.
      invitation_code (str): The unique invitation code for the event.
      message_channel (HangEventMessageChannel): The message channel associated with the event.
      archived (bool): Whether the event is archived or not.
    """
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="hang_events_owned")
    picture = models.CharField(max_length=2000000)
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
        """In order to be able to send notifications"""
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
        """
        Adds a user to a HangEvent using an invitation code.

        Arguments:
          invitation_code (str): The invitation code for the HangEvent.
          user (User): The user to be added to the HangEvent.

        Returns:
          HangEvent: The HangEvent to which the user was added.

        Raises:
          ValidationError: If the HangEvent is archived or the user is already an attendee.
        """
        hang_event = HangEvent.objects.filter(invitation_code=invitation_code).get()

        if hang_event.archived:
            raise exceptions.ValidationError("This HangEvent has been archived")

        if user in hang_event.attendees.all():
            raise exceptions.ValidationError("You are already an attendee of this HangEvent")

        hang_event.attendees.add(user)
        hang_event.save()
        return hang_event

    def to_google_calendar_event_data(self):
        """
        Converts the HangEvent to a dictionary suitable for creating a Google Calendar event.

        Returns:
          dict: A dictionary containing the HangEvent data in a format suitable for Google Calendar.
        """
        return {
            'summary': self.name,
            'location': self.address,
            'description': self.description,
            'start': {
                'dateTime': self.scheduled_time_start.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': self.scheduled_time_end.isoformat(),
                'timeZone': 'UTC',
            },
            'attendees': [{'email': attendee.email} for attendee in self.attendees.all()]
        }


class Task(models.Model, RTWSSendMessageOnUpdate):
    """
    Represents a task associated with a HangEvent.

    Attributes:
      event (HangEvent): The event associated with the task.
      name (str): The name of the task.
      completed (bool): Whether the task is completed or not.
    """
    event = models.ForeignKey(HangEvent, related_name="tasks", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    completed = models.BooleanField(default=False)

    rtws_message_content = "hang_event"

    def get_rtws_users(self):
        return list(self.event.attendees.all())
