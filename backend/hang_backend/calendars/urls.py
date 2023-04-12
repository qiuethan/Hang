from django.urls import path
from .views import ManualTimeRangeCreateView, get_calendar_list, \
    GoogleCalendarSyncView, BusyTimeRangesView, FreeTimeRangesView, UsersFreeDuringRangeView

app_name = "calendars"

urlpatterns = [
    path('time_range', ManualTimeRangeCreateView.as_view(), name='time_range_create'),
    path('google_calendar_list', get_calendar_list, name='calendar_list'),
    path('google_calendar_sync', GoogleCalendarSyncView.as_view(), name='google_calendar_sync'),
    path('get_busy_times/<int:user_id>', BusyTimeRangesView.as_view(), name='get_busy_times'),
    path('get_free_times', FreeTimeRangesView.as_view(), name='get_free_times'),
    path('get_free_users', UsersFreeDuringRangeView.as_view(), name='get_free_users')
]
