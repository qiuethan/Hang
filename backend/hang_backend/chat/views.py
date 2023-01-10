from django.contrib.auth.models import User
from rest_framework import generics, permissions

from common.util.update_db import udbgenerics
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
        return DirectMessage.objects.filter(users=self.request.user).all()

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
    update_db_actions = [update_db_send_rtws_message]
    rtws_update_actions = ["group_chat"]

    def get_queryset(self):
        return GroupChat.objects.filter(users=self.request.user).all()

    def get_rtws_users(self, data):
        return {User.objects.get(id=user) for user in data["users"]}


class RetrieveUpdateGroupChatView(udbgenerics.UpdateDBRetrieveUpdateAPIView):
    """View that can retrieve/update/delete a DM by id."""
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
