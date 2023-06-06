"""
ICS4U
Paul Chen
This module defines the viewset for the Notification model.
"""

from rest_framework import viewsets, mixins, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    """
    A viewset for viewing, updating, and retrieving Notifications.

    Attributes:
      permission_classes (list): The permission classes required for accessing this viewset.
      serializer_class (Serializer): The serializer class used for this viewset, NotificationSerializer.
    """

    # Defining the permissions and serializer class for the viewset
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        """
        Returns the Notifications associated with the authenticated user.

        Returns:
          QuerySet: A queryset of Notification instances for the authenticated user.
        """
        return Notification.objects.filter(user=self.request.user).all()

    def update(self, request, *args, **kwargs):
        """
        Marks a notification as read when updating.

        Arguments:
          request (Request): The HTTP request.
          *args: Additional positional arguments.
          **kwargs: Additional keyword arguments.

        Returns:
          Response: The response of the update action from the superclass.
        """
        instance = self.get_object()
        instance.set_as_read()
        return super().update(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """
        Returns the unread Notifications of the authenticated user.

        Arguments:
          request (Request): The HTTP request.

        Returns:
          Response: The HTTP response containing serialized data of unread notifications.
        """
        queryset = self.get_queryset().filter(read=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def read(self, request):
        """
        Returns the read Notifications of the authenticated user.

        Arguments:
          request (Request): The HTTP request.

        Returns:
          Response: The HTTP response containing serialized data of read notifications.
        """
        queryset = self.get_queryset().filter(read=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
