from django.contrib.auth.models import User
from rest_framework import generics, permissions

from common.util.update_db import udbgenerics
from notifications.utils import update_db_send_notification
from real_time_ws.utils import update_db_send_rtws_message
from .models import DirectMessage, GroupChat
from .serializers import DirectMessageSerializer, \
    GroupChatSerializer


class ListCreateDirectMessageView(udbgenerics.UpdateDBListCreateAPIView):
    """View that can list/create DMs."""
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = DirectMessageSerializer
    update_db_actions = [update_db_send_rtws_message]
    rtws_update_actions = ["direct_message"]

    def get_queryset(self):
        return DirectMessage.objects.filter(users=self.request.user).order_by("-message_last_sent").all()

    def get_rtws_users(self, data):
        return {User.objects.get(id=user) for user in data["users"]}


class RetrieveDirectMessageView(generics.RetrieveAPIView):
    """View that can retrieve a DM by id."""
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = DirectMessageSerializer

    def get_queryset(self):
        return DirectMessage.objects.filter(users=self.request.user).all()


class ListCreateGroupChatView(udbgenerics.UpdateDBListCreateAPIView):
    """View that can list/create GCs."""
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = GroupChatSerializer
    update_db_actions = [update_db_send_rtws_message, update_db_send_notification]
    rtws_update_actions = ["group_chat"]

    def get_queryset(self):
        return GroupChat.objects.filter(users=self.request.user).order_by("-message_last_sent").all()

    def get_rtws_users(self, data):
        return {User.objects.get(id=user) for user in data["users"]}

    def get_notification_messages(self, *serializers, current_user=None, request_type=None):
        notifications = []
        if request_type == "POST":
            users = set()
            group_chat_name = "placeholder_name"
            for serializer in serializers:
                for user in serializer.data["users"]:
                    users.add(User.objects.get(id=user))
                group_chat_name = serializer.data["name"]
            users.remove(current_user)
            for user in users:
                notifications.append({
                    "user": user,
                    "title": current_user.username,
                    "description": f"{current_user.username} has added you to \"{group_chat_name}\""
                })
            return notifications


class RetrieveUpdateGroupChatView(udbgenerics.UpdateDBRetrieveUpdateAPIView):
    """View that can retrieve/update/delete a GC by id."""
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = GroupChatSerializer
    update_db_actions = [update_db_send_rtws_message]
    rtws_update_actions = ["group_chat"]

    def get_queryset(self):
        return GroupChat.objects.filter(users=self.request.user).all()

    def get_rtws_users(self, data):
        return {User.objects.get(id=user) for user in data["users"]}
