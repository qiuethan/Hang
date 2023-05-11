from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ManualTimeRangeView, \
    GoogleCalendarSyncView, BusyTimeRangesView, FreeTimeRangesView, UsersFreeDuringRangeView, RepeatingTimeRangeViewSet, \
    GoogleCalendarListView

app_name = "calendars"

router = DefaultRouter()
router.register(r'repeating_time_ranges', RepeatingTimeRangeViewSet, basename='repeating_time_ranges')

urlpatterns = [
    path('time_ranges/', ManualTimeRangeView.as_view(), name='time_range_create'),
    path('google_calendar/', GoogleCalendarListView.as_view(), name='google_calendar'),
    path('google_calendar/sync/', GoogleCalendarSyncView.as_view(), name='google_calendar_sync'),
    path('busy_times/<int:user_id>/', BusyTimeRangesView.as_view(), name='busy_times'),
    path('free_times', FreeTimeRangesView.as_view(), name='free_times'),
    path('free_users', UsersFreeDuringRangeView.as_view(), name='free_users')
]

urlpatterns += router.urls
