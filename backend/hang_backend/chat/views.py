from rest_framework import generics, permissions

from .models import DirectMessage, GroupChat
from .serializers import DirectMessageSerializer, \
    GroupChatSerializer


class ListCreateDirectMessageView(generics.ListCreateAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = DirectMessageSerializer

    def get_queryset(self):
        return DirectMessage.objects.filter(users=self.request.user).all()


class RetrieveDirectMessageView(generics.RetrieveAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = DirectMessageSerializer

    def get_queryset(self):
        return DirectMessage.objects.filter(users=self.request.user).all()


class ListCreateGroupChatView(generics.ListCreateAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = GroupChatSerializer

    def get_queryset(self):
        return GroupChat.objects.filter(users=self.request.user).all()


class RetrieveUpdateDestroyGroupChatView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = GroupChatSerializer

    def get_queryset(self):
        return GroupChat.objects.filter(users=self.request.user).all()
