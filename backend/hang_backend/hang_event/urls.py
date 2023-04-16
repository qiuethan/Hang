from django.urls import path

from hang_event.views import ListCreateHangEventView, RetrieveUpdateDestroyHangEventView, \
    CreateTaskView, RetrieveUpdateDestroyTaskView, AddHangEventToGoogleCalendarView, JoinHangEventView, \
    GenerateNewInvitationCodeView, GetInvitationCodeView, ArchiveHangEventView, UnarchiveHangEventView, \
    ListArchivedHangEventView

app_name = "hang_event"

# Register Hang Event URLs.
urlpatterns = [
    path("hang_event", ListCreateHangEventView.as_view()),
    path("hang_event/<int:pk>", RetrieveUpdateDestroyHangEventView.as_view()),
    path('join', JoinHangEventView.as_view(), name='join_hang_event'),
    path('get_invitation_code/<int:pk>', GetInvitationCodeView.as_view(), name='get_invitation_code'),
    path('generate_invitation_code/<int:pk>', GenerateNewInvitationCodeView.as_view(),
         name='generate_new_invitation_code'),
    path("add_hang_event_to_google_calendar/<int:pk>", AddHangEventToGoogleCalendarView.as_view()),
    path("task", CreateTaskView.as_view()),
    path("task/<int:pk>", RetrieveUpdateDestroyTaskView.as_view()),
    path('archive_hang_event/<int:pk>', ArchiveHangEventView.as_view(), name='archive_hang_event'),
    path('unarchive_hang_event/<int:pk>', UnarchiveHangEventView.as_view(), name='unarchive_hang_event'),
    path('archived_hang_event', ListArchivedHangEventView.as_view(), name='list_archived_hang_events'),
]
