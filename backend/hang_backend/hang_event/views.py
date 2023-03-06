from django.contrib.auth.models import User
from rest_framework import permissions, generics, status
from rest_framework.response import Response

from common.util.update_db import udbgenerics
from hang_event.models import Task
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
