from rest_framework import viewsets, mixins, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.set_as_read()
        return super().update(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def unread(self, request):
        queryset = self.get_queryset().filter(read=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def read(self, request):
        queryset = self.get_queryset().filter(read=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
