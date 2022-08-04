from rest_framework import generics, permissions

from hang_event.serializer import HangEventSerializer


class ListCreateHangEventView(generics.ListCreateAPIView):
    permission_classes = {
        permissions.IsAuthenticated,
    }
    serializer_class = HangEventSerializer

    def get_queryset(self):
        return self.request.user.hang_events.all()


class RetrieveUpdateDestroyHangEventView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = {
        permissions.IsAuthenticated,
    }
    serializer_class = HangEventSerializer

    def get_queryset(self):
        return self.request.user.hang_events.all()
