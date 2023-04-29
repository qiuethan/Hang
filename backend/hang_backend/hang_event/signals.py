from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save
from django.dispatch import receiver
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from accounts.models import GoogleAuthenticationToken
from hang_backend import settings
from .models import HangEvent


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

