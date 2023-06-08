"""
ICS4U
Paul Chen
This module defines the views and viewsets for the hang_events package.
"""

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
from hang_events.models import Task, HangEvent, generate_unique_invitation_code
from hang_events.serializers import HangEventSerializer, TaskSerializer


class HangEventViewSet(viewsets.ModelViewSet):
    """A ViewSet for managing Hang Events."""
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = HangEventSerializer

    def get_queryset(self):
        """Get the queryset of HangEvents that are not archived and are associated with the current user."""
        return self.request.user.hang_events.filter(archived=False).order_by("-scheduled_time_start").all()

    def destroy(self, request, *args, **kwargs):
        """Destroy the instance of the HangEvent if the current user is the owner."""
        instance = self.get_object()
        if self.request.user != instance.owner:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        """Archive a HangEvent object if the request user is the owner."""
        hang_event = HangEvent.objects.filter(archived=False).get(pk=pk)
        if request.user != hang_event.owner:
            return Response(status=status.HTTP_403_FORBIDDEN)
        hang_event.archived = True
        hang_event.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InvitationCodeViewSet(viewsets.GenericViewSet):
    """A ViewSet for managing invitation codes for Hang Events."""
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = HangEventSerializer

    def get_queryset(self):
        return self.request.user.hang_events_owned.filter(archived=False).all()

    @action(detail=False, methods=["post"])
    def join(self, request, pk=None):
        """Join a HangEvent through an invitation code."""
        invitation_code = request.data.get("invitation_code")
        hang_event = HangEvent.add_user_through_invitation_code(invitation_code, request.user)
        serializer = self.get_serializer(hang_event)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def regenerate(self, request, pk=None):
        """Regenerate the invitation code for a HangEvent."""
        hang_event = self.get_object()
        if request.user != hang_event.owner:
            return Response({"error": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)
        hang_event.invitation_code = generate_unique_invitation_code()
        hang_event.save()
        return Response({"invitation_code": hang_event.invitation_code}, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """Retrieve the invitation code for a HangEvent."""
        hang_event = self.get_object()
        if request.user != hang_event.owner:
            return Response({"error": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)
        return Response({"invitation_code": hang_event.invitation_code}, status=status.HTTP_200_OK)


class TaskViewSet(viewsets.ModelViewSet):
    """A ViewSet for managing Tasks."""
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = TaskSerializer

    def get_queryset(self):
        """
        Get the queryset of Tasks that are associated with a HangEvent that the
        current user is attending and is not archived.
        """
        return Task.objects.filter(event__attendees__username=self.request.user.username, event__archived=False).all()

    def perform_create(self, serializer):
        serializer.save()


class AddHangEventToGoogleCalendarView(APIView):
    """A view to add a HangEvent to a user's Google Calendar."""
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        hang_event = get_object_or_404(HangEvent, id=pk)
        user = request.user

        # Validate data
        if hang_event.archived:
            return Response({"error": "You are already an attendee of this HangEvent"},
                            status=status.HTTP_400_BAD_REQUEST)
        if hang_event.owner != user:
            return Response({"detail": "Unauthorized: user is not the owner of the HangEvent"},
                            status=status.HTTP_403_FORBIDDEN)
        if hang_event.google_calendar_event_id is not None:
            return Response({"detail": "Error: google_calendar_event_id field is not null"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Retrieve user credentials.
        authentication_token = get_object_or_404(GoogleAuthenticationToken, user=user)
        authentication_token.refresh_access_token()
        credentials = Credentials(token=authentication_token.access_token)

        # Create Google Calendar event.
        service = build('calendar', 'v3', credentials=credentials)
        event_body = hang_event.to_google_calendar_event_data()
        try:
            event = service.events().insert(calendarId='primary', body=event_body).execute()
        except HttpError as e:
            return Response({"detail": f"An error occurred while creating the event: {e}"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Save to HangEvent model instance.
        hang_event.google_calendar_event_id = event['id']
        hang_event.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ArchivedHangEventViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    A ViewSet for managing archived Hang Events.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = HangEventSerializer

    def get_queryset(self):
        """Get the queryset of HangEvents that the current user is attending and are archived."""
        return HangEvent.objects.filter(attendees=self.request.user, archived=True).all()

    @action(detail=True, methods=["post"])
    def unarchive(self, request, *args, **kwargs):
        """Unarchive a HangEvent object if the request user is the owner."""
        hang_event = self.get_object()
        if request.user != hang_event.owner:
            return Response(status=status.HTTP_403_FORBIDDEN)
        hang_event.archived = False
        hang_event.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
