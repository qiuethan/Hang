"""
ICS4U
Paul Chen
This module contains views for managing calendar and time range data.
"""

from datetime import datetime

from dateutil.tz import tz
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import views, status, generics, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import GoogleAuthenticationToken
from .models import ManualCalendar, ManualTimeRange, ImportedCalendar, ImportedTimeRange, \
    GoogleCalendar, RepeatingTimeRange
from .pagination import DateBasedPagination
from .serializers import ManualTimeRangeSerializer, \
    TimeRangeSerializer, RepeatingTimeRangeSerializer, GoogleCalendarSerializer, FreeTimeRangesSerializer, \
    UserFreeDuringRangeSerializer
from .services import TimeRangeService


class ManualTimeRangeView(generics.CreateAPIView):
    """
    View for creating a manual time range.
    """
    permission_classes = [IsAuthenticated, ]
    serializer_class = ManualTimeRangeSerializer
    queryset = ManualTimeRange.objects.all()

    def get_serializer_context(self):
        return {'request': self.request, 'calendar': ManualCalendar.objects.get(user=self.request.user)}


class RepeatingTimeRangeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing repeating time ranges.
    """
    serializer_class = RepeatingTimeRangeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RepeatingTimeRange.objects.filter(calendar__user=self.request.user)

    def perform_create(self, serializer):
        calendar = get_object_or_404(ManualCalendar, user=self.request.user)
        serializer.save(manual_calendar=calendar)


class GoogleCalendarListView(APIView):
    """
    View for listing Google Calendars.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        calendar_list = GoogleCalendar.fetch_calendar_data(request.user)
        return Response(calendar_list)


class GoogleCalendarSyncView(views.APIView):
    """
    View for syncing Google Calendars.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GoogleCalendarSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        user = request.user
        authentication_token = GoogleAuthenticationToken.objects.get(user=user)
        authentication_token.refresh_access_token()

        imported_calendar = ImportedCalendar.objects.get(user=user)

        # Fetch free/busy times
        time_ranges = GoogleCalendar.fetch_free_busy_ranges(authentication_token, serializer.validated_data)

        # Merge and store time ranges
        qs = ImportedTimeRange.objects.filter(calendar=imported_calendar).all()
        for time_range in qs:
            if time_range.end_time < datetime.now(timezone.utc):
                time_ranges.append(time_range)
        time_ranges = sorted(time_ranges, key=lambda x: x.start_time)

        # If there's only one time range or none, delete all existing time ranges and save the new ones
        if len(time_ranges) <= 1:
            ImportedTimeRange.objects.filter(calendar=imported_calendar).delete()
            for obj in time_ranges:
                obj.save()
        else:
            # If there are multiple time ranges, merge overlapping ones
            merged_ranges = []
            current_range = time_ranges[0]

            for next_range in time_ranges[1:]:
                if current_range.end_time >= next_range.start_time:
                    current_range.end_time = max(current_range.end_time, next_range.end_time)
                else:
                    merged_ranges.append(current_range)
                    current_range = next_range

            merged_ranges.append(current_range)

            for time_range in merged_ranges:
                time_range.calendar = imported_calendar

            # Delete all existing time ranges and save the merged ones
            ImportedTimeRange.objects.filter(calendar=imported_calendar).delete()
            for obj in merged_ranges:
                obj.save()

        # Sync Google Calendars
        GoogleCalendar.sync_google_calendar(imported_calendar, serializer.validated_data)

        return Response(status=status.HTTP_204_NO_CONTENT)


class BusyTimeRangesView(APIView):
    """
    View for getting the busy time ranges of a user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, format=None):
        start_time = request.query_params.get('start_time')
        if start_time:
            start_time = datetime.fromisoformat(start_time).replace(tzinfo=tz.gettz())
        else:
            start_time = timezone.now()

        user = get_object_or_404(User, pk=user_id)
        if user != request.user and user not in request.user.profile.friends.all():
            return Response("Invalid Permissions", status=status.HTTP_400_BAD_REQUEST)

        merged_ranges = TimeRangeService.get_user_busy_ranges(user, start_time)

        serializer = TimeRangeSerializer([{"start_time": e[0], "end_time": e[1]} for e in merged_ranges], many=True)

        paginator = DateBasedPagination(start_time)
        page = paginator.paginate_queryset(serializer.data, request)
        return paginator.get_paginated_response(page)


class FreeTimeRangesView(APIView):
    """
    View for getting the free time ranges of a user.
    """
    def get(self, request):
        query_serializer = FreeTimeRangesSerializer(data=request.query_params, context={"request": request})
        query_serializer.is_valid(raise_exception=True)
        validated_data = query_serializer.validated_data

        start_time = validated_data['start_time']
        end_time = validated_data['end_time']

        busy_ranges = []
        for user in validated_data['users']:
            ranges = TimeRangeService.get_user_busy_ranges(user, start_time)
            for r in ranges:
                if r[0] < end_time and r[1] > start_time:
                    busy_ranges.append(r)

        busy_ranges = sorted(busy_ranges)
        free_ranges = TimeRangeService.get_free_times_from_busy_times(sorted_busy_ranges=busy_ranges,
                                                                      start_time=start_time,
                                                                      end_time=end_time)

        # Serialize the free time slots
        serializer = TimeRangeSerializer([{"start_time": e[0], "end_time": e[1]} for e in free_ranges], many=True)
        return Response(serializer.data)


class UsersFreeDuringRangeView(APIView):
    """
    View for getting the users who are free during a certain time range.
    """
    def get(self, request):
        serializer = UserFreeDuringRangeSerializer(data=request.query_params, context={"request": request})
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        start_time = validated_data['start_time']
        end_time = validated_data['end_time']

        free_users = []
        for user in validated_data['users']:
            ranges = TimeRangeService.get_user_busy_ranges(user, start_time)
            is_free = True
            for r in ranges:
                if start_time < r[1] and r[0] < end_time:
                    is_free = False
            if is_free:
                free_users.append(user)

        return Response(user.id for user in free_users)
