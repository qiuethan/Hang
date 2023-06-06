"""
ICS4U
Paul Chen
Module for managing Hang Events in the application. This module consists of ViewSets for HangEvent, InvitationCode,
Task, AddHangEventToGoogleCalendar, and ArchivedHangEvent functionalities.
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
    """
    A view set for managing Hang Events. It supports operations to list, create, retrieve, update, and delete Hang Events.

    Attributes:
        permission_classes (list): Permission classes applicable for this viewset.
        serializer_class (Serializer): The serializer class used for this viewset.
    """
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = HangEventSerializer

    def get_queryset(self):
        """
        Get the queryset of HangEvents that are not archived and are associated with the current user.

        Returns:
            QuerySet: The queryset of HangEvents for the current user.
        """
        return self.request.user.hang_events.filter(archived=False).all()

    def destroy(self, request, *args, **kwargs):
        """
        Destroy the instance of the HangEvent if the current user is the owner.

        Arguments:
            request (Request): The incoming request.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The response with appropriate status code.
        """
        instance = self.get_object()
        if self.request.user != instance.owner:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        """
        Archive a HangEvent object if the request user is the owner.

        Arguments:
            request (Request): The incoming request.
            pk (int, optional): Primary key of the HangEvent to archive.

        Returns:
            Response: The response with appropriate status code.
        """
        hang_event = HangEvent.objects.filter(archived=False).get(pk=pk)
        if request.user != hang_event.owner:
            return Response(status=status.HTTP_403_FORBIDDEN)
        hang_event.archived = True
        hang_event.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class InvitationCodeViewSet(viewsets.GenericViewSet):
    """
    A view set for managing Invitation Codes for Hang Events. It supports operations to join, regenerate, and retrieve Invitation Codes.

    Attributes:
        permission_classes (list): Permission classes applicable for this viewset.
        serializer_class (Serializer): The serializer class used for this viewset.
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = HangEventSerializer

    def get_queryset(self):
        """
        Get the queryset of HangEvents that are owned by the current user and are not archived.

        Returns:
            QuerySet: The queryset of HangEvents for the current user.
        """
        return self.request.user.hang_events_owned.filter(archived=False).all()

    @action(detail=False, methods=["post"])
    def join(self, request, pk=None):
        """
        Join a HangEvent through an invitation code.

        Arguments:
            request (Request): The incoming request.
            pk (int, optional): Primary key of the HangEvent to join.

        Returns:
            Response: The response with the serialized HangEvent and status code.
        """
        invitation_code = request.data.get("invitation_code")
        hang_event = HangEvent.add_user_through_invitation_code(invitation_code, request.user)
        serializer = self.get_serializer(hang_event)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def regenerate(self, request, pk=None):
        """
        Regenerate the invitation code for a HangEvent.

        Arguments:
            request (Request): The incoming request.
            pk (int, optional): Primary key of the HangEvent.

        Returns:
            Response: The response with the new invitation code and status code.
        """
        hang_event = self.get_object()
        if request.user != hang_event.owner:
            return Response({"error": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)
        hang_event.invitation_code = generate_unique_invitation_code()
        hang_event.save()
        return Response({"invitation_code": hang_event.invitation_code}, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """
        Retrieve the invitation code for a HangEvent.

        Arguments:
            request (Request): The incoming request.
            pk (int, optional): Primary key of the HangEvent.

        Returns:
            Response: The response with the invitation code and status code.
        """
        hang_event = self.get_object()
        if request.user != hang_event.owner:
            return Response({"error": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)
        return Response({"invitation_code": hang_event.invitation_code}, status=status.HTTP_200_OK)


class TaskViewSet(viewsets.ModelViewSet):
    """
    A view set for managing Tasks. It supports operations to list, create, retrieve, update, and delete Tasks.

    Attributes:
        permission_classes (list): Permission classes applicable for this viewset.
        serializer_class (Serializer): The serializer class used for this viewset.
    """
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = TaskSerializer

    def get_queryset(self):
        """
        Get the queryset of Tasks that are associated with a HangEvent that the current user is attending and is not archived.

        Returns:
            QuerySet: The queryset of Tasks for the current user.
        """
        return Task.objects.filter(event__attendees__username=self.request.user.username, event__archived=False).all()

    def perform_create(self, serializer):
        """
        Save a Task instance when creating a Task.

        Arguments:
            serializer (Serializer): The serializer containing the Task data.

        Returns:
            None
        """
        serializer.save()


class AddHangEventToGoogleCalendarView(APIView):
    """
    A view to add a HangEvent to a user's Google Calendar.

    Attributes:
        permission_classes (list): Permission classes applicable for this view.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        """
        Add a HangEvent to the authenticated user's Google Calendar.

        Arguments:
            request (Request): The incoming request.
            pk (int): Primary key of the HangEvent to add to the calendar.

        Returns:
            Response: The response with appropriate status code.
        """
        hang_event = get_object_or_404(HangEvent, id=pk)
        user = request.user

        if hang_event.archived:
            return Response({"error": "You are already an attendee of this HangEvent"},
                            status=status.HTTP_400_BAD_REQUEST)

        if hang_event.owner != user:
            return Response({"detail": "Unauthorized: user is not the owner of the HangEvent"},
                            status=status.HTTP_403_FORBIDDEN)

        if hang_event.google_calendar_event_id is not None:
            return Response({"detail": "Error: google_calendar_event_id field is not null"},
                            status=status.HTTP_400_BAD_REQUEST)

        authentication_token = get_object_or_404(GoogleAuthenticationToken, user=user)
        authentication_token.refresh_access_token()

        credentials = Credentials(token=authentication_token.access_token)
        service = build('calendar', 'v3', credentials=credentials)

        event_body = hang_event.to_google_calendar_event_data()

        try:
            event = service.events().insert(calendarId='primary', body=event_body).execute()
        except HttpError as e:
            return Response({"detail": f"An error occurred while creating the event: {e}"},
                            status=status.HTTP_400_BAD_REQUEST)

        hang_event.google_calendar_event_id = event['id']
        hang_event.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ArchivedHangEventViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    A view set for managing archived Hang Events. It supports operations to list and unarchive Hang Events.

    Attributes:
        permission_classes (list): Permission classes applicable for this viewset.
        serializer_class (Serializer): The serializer class used for this viewset.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = HangEventSerializer

    def get_queryset(self):
        """
        Get the queryset of HangEvents that the current user is attending and are archived.

        Returns:
            QuerySet: The queryset of archived HangEvents for the current user.
        """
        return HangEvent.objects.filter(attendees=self.request.user, archived=True).all()

    @action(detail=True, methods=["post"])
    def unarchive(self, request, *args, **kwargs):
        """
        Unarchive a HangEvent object if the request user is the owner.

        Arguments:
            request (Request): The incoming request.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The response with appropriate status code.
        """
        hang_event = self.get_object()
        if request.user != hang_event.owner:
            return Response(status=status.HTTP_403_FORBIDDEN)
        hang_event.archived = False
        hang_event.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
