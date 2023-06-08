"""
ICS4U
Paul Chen
This module defines the views and viewsets for the chats package.
"""
from rest_framework import permissions, viewsets, mixins, generics

from .models import DirectMessageChannel, GroupMessageChannel, MessageChannel
from .serializers import DirectMessageChannelSerializer, GroupMessageChannelSerializer, ReadMessageChannelSerializer


class DirectMessageChannelViewSet(mixins.ListModelMixin,
                                  mixins.CreateModelMixin,
                                  mixins.RetrieveModelMixin,
                                  viewsets.GenericViewSet):
    """ViewSet that can list/create/retrieve DMs."""
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = DirectMessageChannelSerializer

    def get_queryset(self):
        return DirectMessageChannel.objects.filter(users=self.request.user).order_by("-message_last_sent").all()


class GroupMessageChannelViewSet(mixins.ListModelMixin,
                                 mixins.CreateModelMixin,
                                 mixins.RetrieveModelMixin,
                                 mixins.UpdateModelMixin,
                                 viewsets.GenericViewSet):
    """ViewSet that can list/create/retrieve/update GCs."""
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = GroupMessageChannelSerializer

    def get_queryset(self):
        return GroupMessageChannel.objects.filter(users=self.request.user).order_by("-message_last_sent").all()


class ReadMessageChannelView(generics.UpdateAPIView):
    """View that allows a user to read a MessageChannel."""
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = ReadMessageChannelSerializer

    def get_queryset(self):
        return MessageChannel.objects.filter(users=self.request.user).all()
