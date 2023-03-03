from rest_framework import permissions

from common.util.update_db import udbgenerics
from hang_event.serializer import HangEventSerializer
from real_time_ws.utils import update_db_send_rtws_message


class ListCreateHangEventView(udbgenerics.UpdateDBListCreateAPIView):
    """View to list/create HangEvents."""
    permission_classes = {
        permissions.IsAuthenticated,
    }
    serializer_class = HangEventSerializer
    update_db_actions = [update_db_send_rtws_message]
    rtws_update_actions = ["hang_event"]

    def get_queryset(self):
        return self.request.user.hang_events.all()


class RetrieveUpdateDestroyHangEventView(udbgenerics.UpdateDBRetrieveUpdateDestroyAPIView):
    """View to retrieve/update/destroy HangEvents."""
    permission_classes = {
        permissions.IsAuthenticated,
    }
    serializer_class = HangEventSerializer
    update_db_actions = [update_db_send_rtws_message]
    rtws_update_actions = ["hang_event"]

    def get_queryset(self):
        return self.request.user.hang_events.all()
