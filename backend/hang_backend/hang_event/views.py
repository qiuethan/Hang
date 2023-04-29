import uuid

from django.contrib.auth.models import User
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from rest_framework import permissions, generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import GoogleAuthenticationToken
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
        return self.request.user.hang_events.filter(archived=False).all()

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
        return self.request.user.hang_events.filter(archived=False).all()

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


class JoinHangEventView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = HangEventSerializer

    def post(self, request, *args, **kwargs):
        invitation_code = request.data.get("invitation_code")
        if not invitation_code:
            return Response({"error": "Missing invitation code"}, status=status.HTTP_400_BAD_REQUEST)

        hang_event = get_object_or_404(HangEvent, invitation_code=invitation_code)

        if hang_event.archived:
            return Response({"error": "This HangEvent has been archived"},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.user in hang_event.attendees.all():
            return Response({"error": "You are already an attendee of this HangEvent"},
                            status=status.HTTP_400_BAD_REQUEST)

        hang_event.attendees.add(request.user)
        hang_event.save()
        serializer = self.get_serializer(hang_event)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GenerateNewInvitationCodeView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        queryset = self.request.user.hang_events_owned.filter(archived=False).all()
        return get_object_or_404(queryset, id=self.kwargs.get('pk'))

    def post(self, request, *args, **kwargs):
        hang_event = self.get_object()

        if request.user != hang_event.owner:
            return Response({"error": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)

        new_invitation_code = str(uuid.uuid4())[:10]
        while HangEvent.objects.filter(invitation_code=new_invitation_code).exists():
            new_invitation_code = str(uuid.uuid4())[:10]

        hang_event.invitation_code = new_invitation_code
        hang_event.save()
        return Response({"invitation_code": hang_event.invitation_code}, status=status.HTTP_200_OK)


class GetInvitationCodeView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = HangEventSerializer

    def get_object(self):
        queryset = self.request.user.hang_events_owned.filter(archived=False).all()
        return get_object_or_404(queryset, id=self.kwargs.get('pk'))

    def get(self, request, *args, **kwargs):
        hang_event = self.get_object()

        if request.user != hang_event.owner:
            return Response({"error": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)

        return Response({"invitation_code": hang_event.invitation_code}, status=status.HTTP_200_OK)


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
        return Task.objects.filter(event__attendees__username=self.request.user.username, event__archived=False).all()


class AddHangEventToGoogleCalendarView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        hang_event = get_object_or_404(HangEvent, id=pk)
        user = request.user

        if hang_event.archived:
            return Response({"error": "You are already an attendee of this HangEvent"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if the user is the owner of the HangEvent
        if hang_event.owner != user:
            return Response({"detail": "Unauthorized: user is not the owner of the HangEvent"},
                            status=status.HTTP_403_FORBIDDEN)

        # Check if the google_calendar_event_id field isn't null
        if hang_event.google_calendar_event_id is not None:
            return Response({"detail": "Error: google_calendar_event_id field is not null"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Get the user's Google Calendar access token
        google_calendar_access_token = get_object_or_404(GoogleAuthenticationToken, user=user)
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


class ArchiveHangEventView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, format=None):
        hang_event = HangEvent.objects.filter(archived=False).get(pk=pk)
        if request.user != hang_event.owner:
            return Response(status=status.HTTP_403_FORBIDDEN)
        hang_event.archived = True
        hang_event.save()
        return Response(status=status.HTTP_200_OK)


class UnarchiveHangEventView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, format=None):
        hang_event = HangEvent.objects.filter(archived=True).get(pk=pk)
        if request.user != hang_event.owner:
            return Response(status=status.HTTP_403_FORBIDDEN)
        hang_event.archived = False
        hang_event.save()
        return Response(status=status.HTTP_200_OK)


class ListArchivedHangEventView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        archived_hang_events = HangEvent.objects.filter(attendees=request.user, archived=True)
        serializer = HangEventSerializer(archived_hang_events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
