from django.contrib.auth.models import User
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from rest_framework import permissions, generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from calendars.models import GoogleCalendarAccessToken
from common.util.update_db import udbgenerics
from hang_backend import settings
from hang_event.models import Task, HangEvent
from hang_event.serializer import HangEventSerializer, TaskSerializer
from notifications.utils import update_db_send_notification
from real_time_ws.utils import update_db_send_rtws_message


class ListCreateHangEventView(udbgenerics.UpdateDBListCreateAPIView):
    """View to list/create HangEvents."""
    permission_classes = {
        permissions.IsAuthenticated,
    }
    serializer_class = HangEventSerializer
    update_db_actions = [update_db_send_rtws_message, update_db_send_notification]
    rtws_update_actions = ["hang_event"]

    def get_queryset(self):
        return self.request.user.hang_events.all()

    def get_rtws_users(self, data):
        return {User.objects.get(id=user) for user in data["attendees"]}

    def get_notification_messages(self, *serializers, current_user, request_type):
        notifications = []
        if request_type == "POST":
            assert len(serializers) == 1
            users = set([User.objects.get(id=user) for user in serializers[0].data["attendees"]])
            users.remove(current_user)
            for user in users:
                notifications.append({
                    "user": user,
                    "title": serializers[0].data["name"],
                    "description": f"{current_user} has added you to event {serializers[0].data['name']}"
                })
        return notifications


class RetrieveUpdateDestroyHangEventView(udbgenerics.UpdateDBRetrieveUpdateDestroyAPIView):
    """View to retrieve/update/destroy HangEvents."""
    permission_classes = {
        permissions.IsAuthenticated,
    }
    serializer_class = HangEventSerializer
    update_db_actions = [update_db_send_rtws_message, update_db_send_notification]
    rtws_update_actions = ["hang_event"]

    def get_queryset(self):
        return self.request.user.hang_events.all()

    def get_rtws_users(self, data):
        return {User.objects.get(id=user) for user in data["attendees"]}

    def get_notification_messages(self, *serializers, current_user, request_type):
        notifications = []
        if request_type == "PATCH":
            assert len(serializers) == 2
            users = set(serializers[1].data["attendees"]).difference(serializers[0].data["attendees"])
            for user in users:
                notifications.append({
                    "user": User.objects.get(id=user),
                    "title": serializers[0].data["name"],
                    "description": f"{current_user} has added you to event {serializers[1].data['name']}"
                })
        return notifications

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if self.request.user != instance.owner:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)


class CreateTaskView(generics.CreateAPIView):
    permission_classes = {
        permissions.IsAuthenticated,
    }
    serializer_class = TaskSerializer


class RetrieveUpdateDestroyTaskView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = {
        permissions.IsAuthenticated,
    }
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(event__attendees__username=self.request.user.username).all()


class AddHangEventToGoogleCalendarView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        hang_event = get_object_or_404(HangEvent, id=pk)
        user = request.user

        # Check if the user is the owner of the HangEvent
        if hang_event.owner != user:
            return Response({"detail": "Unauthorized: user is not the owner of the HangEvent"},
                            status=status.HTTP_403_FORBIDDEN)

        # Check if the google_calendar_event_id field isn't null
        if hang_event.google_calendar_event_id is not None:
            return Response({"detail": "Error: google_calendar_event_id field is not null"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Get the user's Google Calendar access token
        google_calendar_access_token = get_object_or_404(GoogleCalendarAccessToken, user=user)
        google_calendar_access_token.refresh_access_token()

        # Create a Google Calendar event
        credentials = Credentials.from_authorized_user_info(info={
            'access_token': google_calendar_access_token.access_token,
            'refresh_token': google_calendar_access_token.refresh_token,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'client_id': settings.GOOGLE_CLIENT_ID
        })

        service = build('calendar', 'v3', credentials=credentials)

        attendees = [{'email': attendee.email} for attendee in hang_event.attendees.all()]

        event_body = {
            'summary': hang_event.name,
            'location': hang_event.address,
            'description': hang_event.description,
            'start': {
                'dateTime': hang_event.scheduled_time_start.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': hang_event.scheduled_time_end.isoformat(),
                'timeZone': 'UTC',
            },
            'attendees': attendees,
            'colorId': '8',  # Light green color
        }

        try:
            event = service.events().insert(calendarId='primary', body=event_body).execute()
        except HttpError as e:
            return Response({"detail": f"An error occurred while creating the event: {e}"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Set the google_calendar_event_id of the HangEvent to the returned event's id
        hang_event.google_calendar_event_id = event['id']
        hang_event.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
