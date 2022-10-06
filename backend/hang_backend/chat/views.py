from rest_framework import generics, permissions

from .models import DirectMessage, GroupChat
from .serializers import DirectMessageSerializer, \
    GroupChatSerializer


class ListCreateDirectMessageView(generics.ListCreateAPIView):
    """View that can list/create DMs."""
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = DirectMessageSerializer

    def get_queryset(self):
        return DirectMessage.objects.filter(users=self.request.user).all()


class RetrieveDirectMessageView(generics.RetrieveAPIView):
    """View that can retrieve a DM by id."""
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = DirectMessageSerializer

    def get_queryset(self):
        return DirectMessage.objects.filter(users=self.request.user).all()


class ListCreateGroupChatView(generics.ListCreateAPIView):
    """View that can list/create GCs."""
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = GroupChatSerializer

    def get_queryset(self):
        return GroupChat.objects.filter(users=self.request.user).all()


class RetrieveUpdateDestroyGroupChatView(generics.RetrieveUpdateDestroyAPIView):
    """View that can retrieve/update/delete a DM by id."""
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = GroupChatSerializer

    def get_queryset(self):
        return GroupChat.objects.filter(users=self.request.user).all()
