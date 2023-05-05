from rest_framework import permissions, viewsets, mixins, generics

from .models import DirectMessage, GroupChat, MessageChannel
from .serializers import DirectMessageSerializer, GroupChatSerializer, ReadMessageChannelSerializer


class DirectMessageViewSet(mixins.ListModelMixin,
                           mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    """ViewSet that can list/create/retrieve DMs."""
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = DirectMessageSerializer

    def get_queryset(self):
        return DirectMessage.objects.filter(users=self.request.user).order_by("-message_last_sent").all()


class GroupChatViewSet(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       viewsets.GenericViewSet):
    """ViewSet that can list/create/retrieve/update GCs."""
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = GroupChatSerializer

    def get_queryset(self):
        return GroupChat.objects.filter(users=self.request.user).order_by("-message_last_sent").all()


class ReadMessageChannelView(generics.UpdateAPIView):
    """View that can retrieve/update/delete a GC by id."""
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = ReadMessageChannelSerializer

    def get_queryset(self):
        return MessageChannel.objects.filter(users=self.request.user).all()
