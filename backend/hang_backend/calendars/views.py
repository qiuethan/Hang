import json
from datetime import datetime, timedelta

import requests
from dateutil.parser import parse
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers, views, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.util.update_db import udbgenerics
from real_time_ws.utils import update_db_send_rtws_message, send_rtws_message
from .models import ManualCalendar, ManualTimeRange, GoogleCalendarAccessToken, ImportedCalendar, ImportedTimeRange, \
    GoogleCalendarCalendars
from .serializers import ManualTimeRangeSerializer, GoogleCalendarAccessTokenSerializer, \
    GoogleCalendarCalendarsListSerializer, TimeRangeSerializer


class ManualTimeRangeCreateView(udbgenerics.UpdateDBCreateAPIView):
    queryset = ManualTimeRange.objects.all()
    serializer_class = ManualTimeRangeSerializer
    permission_classes = [IsAuthenticated]
    update_db_actions = [update_db_send_rtws_message]
    rtws_update_actions = ["calendars"]

    # TODO:
    # - Make signin not necessary
    # - Repeating time ranges
    # - Add Hang Events to this calendar
    # - Add Hang Events to Google Calendar
    # - Add method to edit user profile
    # - Algorithms
    # - Add to Hang though link
    def get_serializer_context(self):
        try:
            calendar = ManualCalendar.objects.get(user=self.request.user)
        except ManualCalendar.DoesNotExist:
            raise NotFound("User not found.")

        return {'request': self.request, 'calendar': calendar}

    def get_rtws_users(self, data):
        return [self.request.user]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_calendar_list(request):
    try:
        calendar_list = GoogleCalendarAccessTokenSerializer.fetch_calendar_data(request.user)
        return Response(calendar_list)
    except serializers.ValidationError as e:
        return Response({"error": str(e)}, status=400)


class GoogleCalendarSyncView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GoogleCalendarCalendarsListSerializer(data=request.data)
        if serializer.is_valid():
            try:
                calendar_data_list = serializer.validated_data['calendar_data']
                user = request.user
                access_token = GoogleCalendarAccessToken.objects.get(user=user).access_token

                imported_calendar = ImportedCalendar.objects.get(user=user)

                # Fetch free/busy times
                time_min = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
                time_ranges = []

                for i in range(6):
                    time_max = (datetime.utcnow() + timedelta(days=(i + 1) * 60)).replace(
                        microsecond=0).isoformat() + "Z"
                    headers = {
                        'Authorization': f'Bearer {access_token}',
                        'Content-Type': 'application/json'
                    }
                    data = {
                        "timeMin": time_min,
                        "timeMax": time_max,
                        "items": [{"id": cal_data['id']} for cal_data in calendar_data_list]
                    }
                    response = requests.post('https://www.googleapis.com/calendar/v3/freeBusy', headers=headers,
                                             data=json.dumps(data))
                    result = json.loads(response.text)

                    for cal_data in calendar_data_list:
                        cal_id = cal_data['id']
                        cal_info = result['calendars'][cal_id]
                        for busy_range in cal_info['busy']:
                            time_ranges.append(
                                ImportedTimeRange(
                                    calendar=imported_calendar,
                                    start_time=parse(busy_range['start']),
                                    end_time=parse(busy_range['end'])
                                )
                            )
                    time_min = time_max

                # Delete existing GoogleCalendarCalendars and add new ones
                GoogleCalendarCalendars.objects.filter(calendar=imported_calendar).delete()
                for cal_data in calendar_data_list:
                    GoogleCalendarCalendars.objects.create(
                        calendar=imported_calendar,
                        google_calendar_id=cal_data['id'],
                        name=cal_data['name']
                    )

                qs = ImportedTimeRange.objects.filter(calendar=imported_calendar).all()
                for time_range in qs:
                    if time_range.end_time < datetime.now(timezone.utc):
                        time_ranges.append(time_range)
                time_ranges = sorted(time_ranges, key=lambda x: x.start_time)

                if len(time_ranges) <= 1:
                    ImportedTimeRange.objects.filter(calendar=imported_calendar).delete()
                    ImportedTimeRange.objects.bulk_create(time_ranges)

                    return Response(status=status.HTTP_204_NO_CONTENT)

                merged_ranges = []
                current_range = time_ranges[0]

                for next_range in time_ranges[1:]:
                    if current_range.end_time >= next_range.start_time:
                        current_range.end_time = max(current_range.end_time, next_range.end_time)
                    else:
                        merged_ranges.append(current_range)
                        current_range = next_range

                merged_ranges.append(current_range)

                ImportedTimeRange.objects.filter(calendar=imported_calendar).delete()
                ImportedTimeRange.objects.bulk_create(merged_ranges)

                send_rtws_message(self.request.user, "calendars")

                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BusyTimeRangesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, format=None):
        user = get_object_or_404(User, pk=user_id)

        if user != request.user and user not in request.user.userdetails.friends.all():
            return Response("Invalid Permissions", status=status.HTTP_400_BAD_REQUEST)

        manual_time_ranges = ManualTimeRange.objects.filter(calendar__user=user, end_time__gt=timezone.now())
        imported_time_ranges = ImportedTimeRange.objects.filter(calendar__user=user, end_time__gt=timezone.now())

        busy_ranges = [(r.start_time, r.end_time) for r in imported_time_ranges]
        busy_ranges.extend([(r.start_time, r.end_time) for r in manual_time_ranges.filter(type="busy")])

        free_ranges = [(r.start_time, r.end_time) for r in manual_time_ranges.filter(type="free")]

        busy_ranges = sorted(busy_ranges, key=lambda x: x[0])
        free_ranges = sorted(free_ranges, key=lambda x: x[0])

        merged_busy_ranges = []
        for start, end in busy_ranges:
            if not merged_busy_ranges or merged_busy_ranges[-1][1] < start:
                merged_busy_ranges.append((start, end))
            else:
                merged_busy_ranges[-1] = (merged_busy_ranges[-1][0], max(merged_busy_ranges[-1][1], end))

        merged_ranges = []
        j = 0
        free_end = None
        for i in range(len(merged_busy_ranges)):
            start, end = merged_busy_ranges[i]
            while j < len(free_ranges) and free_ranges[j][0] < end:
                if free_end is not None:
                    start = max(start, free_end)
                if start >= end:
                    break
                if start < free_ranges[j][1]:
                    if start < free_ranges[j][0]:
                        merged_ranges.append((start, free_ranges[j][0]))
                    start = free_ranges[j][1]
                if free_end is None:
                    free_end = free_ranges[j][1]
                else:
                    free_end = max(free_end, free_ranges[j][1])
                j += 1
            if free_end is not None:
                start = max(start, free_end)
            if start < end:
                merged_ranges.append((start, end))

        serializer = TimeRangeSerializer([{"start_time": e[0], "end_time": e[1]} for e in merged_ranges], many=True)

        paginator = PageNumberPagination()
        paginator.page_size = 50
        page = paginator.paginate_queryset(serializer.data, request)
        return paginator.get_paginated_response(page)
