from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination

from common.util.update_db import udbgenerics
from notifications.models import Notification
from notifications.serializer import NotificationSerializer
from real_time_ws.utils import update_db_send_rtws_message


class RetrieveUpdateNotificationView(udbgenerics.UpdateDBRetrieveUpdateAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    update_db_actions = [update_db_send_rtws_message]
    rtws_update_actions = ["notification"]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).all()

    def get_rtws_users(self, data):
        return {self.request.user}


class ListUnreadNotificationView(generics.ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).filter(read=False).all()


class ListReadNotificationView(generics.ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).filter(read=True).all()
