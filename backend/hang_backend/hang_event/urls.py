from django.urls import path

from hang_event.views import ListCreateHangEventView, RetrieveUpdateDestroyHangEventView

app_name = "hang_event"

# Register Hang Event URLs.
urlpatterns = [
    path("hang_event", ListCreateHangEventView.as_view()),
    path("hang_event/<int:pk>", RetrieveUpdateDestroyHangEventView.as_view()),
]
