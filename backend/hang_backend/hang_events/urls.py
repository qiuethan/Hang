"""
ICS4U
Paul Chen
This module defines the urls for the hang_events package.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

from hang_events.views import AddHangEventToGoogleCalendarView, HangEventViewSet, InvitationCodeViewSet, TaskViewSet, \
    ArchivedHangEventViewSet

app_name = "hang_events"

router = DefaultRouter()
router.register(r'unarchived', HangEventViewSet, basename='hang_events')
router.register(r'archived', ArchivedHangEventViewSet, basename='hang_events_archived')
router.register(r'invitation_codes', InvitationCodeViewSet, basename='invitation_codes')
router.register(r'tasks', TaskViewSet, basename='tasks')

urlpatterns = [
    path("google_calendar/<int:pk>/", AddHangEventToGoogleCalendarView.as_view()),
]

urlpatterns += router.urls
