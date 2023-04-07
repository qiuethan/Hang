from django.urls import path
from .views import ManualTimeRangeCreateView, GoogleCalendarAccessTokenCreateView, get_calendar_list, \
    GoogleCalendarSyncView, BusyTimeRangesView

app_name = "calendars"

urlpatterns = [
    path('time_range/<int:user_id>', ManualTimeRangeCreateView.as_view(), name='time_range_create'),
    path('google_calendar_access_token', GoogleCalendarAccessTokenCreateView.as_view(), name='access_token_create'),
    path('google_calendar_list', get_calendar_list, name='calendar_list'),
    path('google_calendar_sync', GoogleCalendarSyncView.as_view(), name='google_calendar_sync'),
    path('get_busy_times/<int:user_id>', BusyTimeRangesView.as_view(), name='get_busy_times')
]
