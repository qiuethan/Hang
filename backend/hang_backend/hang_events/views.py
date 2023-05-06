from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from rest_framework import permissions, status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import GoogleAuthenticationToken
from hang_backend import settings
from hang_events.models import Task, HangEvent, generate_unique_invitation_code
from hang_events.serializers import HangEventSerializer, TaskSerializer


class HangEventViewSet(viewsets.ModelViewSet):
    """ViewSet for listing, creating, retrieving, updating, and destroying HangEvents."""
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = HangEventSerializer

    def get_queryset(self):
        return self.request.user.hang_events.filter(archived=False).all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if self.request.user != instance.owner:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        hang_event = HangEvent.objects.filter(archived=False).get(pk=pk)
        if request.user != hang_event.owner:
            return Response(status=status.HTTP_403_FORBIDDEN)
        hang_event.archived = True
        hang_event.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InvitationCodeViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = HangEventSerializer

    def get_queryset(self):
        return self.request.user.hang_events_owned.filter(archived=False).all()

    @action(detail=False, methods=["post"])
    def join(self, request, pk=None):
        invitation_code = request.data.get("invitation_code")
        hang_event = HangEvent.add_user_through_invitation_code(invitation_code, request.user)
        serializer = self.get_serializer(hang_event)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def regenerate(self, request, pk=None):
        hang_event = self.get_object()

        if request.user != hang_event.owner:
            return Response({"error": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)

        hang_event.invitation_code = generate_unique_invitation_code()
        hang_event.save()
        return Response({"invitation_code": hang_event.invitation_code}, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        hang_event = self.get_object()

        if request.user != hang_event.owner:
            return Response({"error": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)

        return Response({"invitation_code": hang_event.invitation_code}, status=status.HTTP_200_OK)


class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(event__attendees__username=self.request.user.username, event__archived=False).all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# TODO
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
            'attendees': attendees
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


class ArchivedHangEventViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = HangEventSerializer

    def get_queryset(self):
        return HangEvent.objects.filter(attendees=self.request.user, archived=True).all()

    @action(detail=True, methods=["post"])
    def unarchive(self, request, *args, **kwargs):
        hang_event = self.get_object()
        if request.user != hang_event.owner:
            return Response(status=status.HTTP_403_FORBIDDEN)
        hang_event.archived = False
        hang_event.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
