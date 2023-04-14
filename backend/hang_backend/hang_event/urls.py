from django.urls import path

from hang_event.views import ListCreateHangEventView, RetrieveUpdateDestroyHangEventView, \
    CreateTaskView, RetrieveUpdateDestroyTaskView, AddHangEventToGoogleCalendarView

app_name = "hang_event"

# Register Hang Event URLs.
urlpatterns = [
    path("hang_event", ListCreateHangEventView.as_view()),
    path("hang_event/<int:pk>", RetrieveUpdateDestroyHangEventView.as_view()),
    path("add_hang_event_to_google_calendar/<int:pk>", AddHangEventToGoogleCalendarView.as_view()),
    path("task", CreateTaskView.as_view()),
    path("task/<int:pk>", RetrieveUpdateDestroyTaskView.as_view()),
]
