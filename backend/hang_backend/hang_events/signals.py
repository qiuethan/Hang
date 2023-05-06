from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save, m2m_changed, post_save
from django.dispatch import receiver
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from accounts.models import GoogleAuthenticationToken
from chats.models import SystemMessage
from hang_backend import settings
from .models import HangEvent


@receiver(m2m_changed, sender=HangEvent.attendees.through)
def update_hang_event_message_channel(sender, instance, action, pk_set, **kwargs):
    if action == "post_add" or action == "post_remove" or action == "post_clear":
        if hasattr(instance, "message_channel"):
            instance.message_channel.users.set(instance.attendees.all())


# Modify the signal receiver to apply the changes only to specific fields
@receiver(post_save, sender=HangEvent)
def send_hang_event_updated_message(sender, instance, created, **kwargs):
    if not created:
        tracked_fields = [
            "name", "owner", "description", "scheduled_time_start", "scheduled_time_end", "address"
        ]
        for field_name in tracked_fields:
            field = instance._meta.get_field(field_name)
            old_value = getattr(instance, f"_old_{field.name}")
            new_value = getattr(instance, field.name)
            if old_value != new_value:
                SystemMessage.objects.create(message_channel=instance.message_channel,
                                             content=f"Hang event {instance.name} updated: {field.name} changed from {str(old_value)} to {str(new_value)}")
                setattr(instance, f"_old_{field.name}", new_value)


# Add signal receivers for user added and removed messages
@receiver(m2m_changed, sender=HangEvent.attendees.through)
def send_hang_event_user_added_or_removed_message(sender, instance, action, pk_set, **kwargs):
    if action in ["post_add", "post_remove"]:
        for user_pk in pk_set:
            user = User.objects.get(pk=user_pk)
            if action == "post_add":
                SystemMessage.objects.create(message_channel=instance.message_channel,
                                             content=f"{user.username} has joined the Hang event {instance.name}")
            else:
                SystemMessage.objects.create(message_channel=instance.message_channel,
                                             content=f"{user.username} has left the Hang event {instance.name}")


@receiver(pre_save, sender=HangEvent)
def update_google_calendar_event(sender, instance, **kwargs):
    # Exit if not an update
    if not instance.pk:
        return

    # Get the old model instance
    old_instance = HangEvent.objects.get(pk=instance.pk)

    # If the google_calendar_event_id is None, exit
    if old_instance.google_calendar_event_id is None:
        return

    # Prepare the Google Calendar API client
    try:
        google_calendar_access_token = GoogleAuthenticationToken.objects.get(user=old_instance.owner)
    except GoogleAuthenticationToken.DoesNotExist:
        instance.google_calendar_event_id = None
        return

    credentials = Credentials.from_authorized_user_info(info={
        "access_token": google_calendar_access_token.access_token,
        "refresh_token": google_calendar_access_token.refresh_token,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET
    })
    service = build("calendar", "v3", credentials=credentials)

    # Delete the old event if the owner has changed
    if old_instance.owner != instance.owner:
        try:
            service.events().delete(calendarId="primary", eventId=old_instance.google_calendar_event_id).execute()
        except HttpError as error:
            raise ValidationError(f"An error occurred while deleting the old Google Calendar event: {error}")

        instance.google_calendar_event_id = None

    # If the new owner doesn't have a GoogleCalendarAccessToken, exit
    try:
        google_calendar_access_token = GoogleAuthenticationToken.objects.get(user=instance.owner)
    except GoogleAuthenticationToken.DoesNotExist:
        return

    credentials = Credentials.from_authorized_user_info(info={
        "access_token": google_calendar_access_token.access_token,
        "refresh_token": google_calendar_access_token.refresh_token,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET
    })
    service = build("calendar", "v3", credentials=credentials)

    # Prepare the event data
    event_data = {
        "summary": instance.name,
        "location": instance.address,
        "description": instance.description,
        "start": {
            "dateTime": instance.scheduled_time_start.isoformat(),
            "timeZone": "UTC",
        },
        "end": {
            "dateTime": instance.scheduled_time_end.isoformat(),
            "timeZone": "UTC",
        },
        "attendees": [{"email": attendee.email} for attendee in instance.attendees.all()],
    }

    # Create a new event if the owner has changed, otherwise update the existing event
    if instance.google_calendar_event_id is None:
        try:
            new_event = service.events().insert(calendarId="primary", body=event_data).execute()
            instance.google_calendar_event_id = new_event['id']
        except HttpError as error:
            raise ValidationError(f"An error occurred while creating the new Google Calendar event: {error}")
    else:
        try:
            event = service.events().update(calendarId="primary", eventId=instance.google_calendar_event_id,
                                            body=event_data).execute()
        except HttpError as error:
            raise ValidationError(f"An error occurred while updating the Google Calendar event: {error}")
