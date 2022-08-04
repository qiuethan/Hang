from django.urls import path
from knox import views as knox_views

from hang_event.views import ListCreateHangEventView, RetrieveUpdateDestroyHangEventView

app_name = "hang_event"

urlpatterns = [
    path("hang_event", ListCreateHangEventView.as_view()),
    path("hang_event/<int:pk>", RetrieveUpdateDestroyHangEventView.as_view()),
]
