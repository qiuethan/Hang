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
from rest_framework.pagination import BasePagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.util.update_db import udbgenerics
from hang_event.models import HangEvent
from real_time_ws.utils import update_db_send_rtws_message, send_rtws_message
from .models import ManualCalendar, ManualTimeRange, GoogleCalendarAccessToken, ImportedCalendar, ImportedTimeRange, \
    GoogleCalendarCalendars
from .serializers import ManualTimeRangeSerializer, GoogleCalendarAccessTokenSerializer, \
    GoogleCalendarCalendarsListSerializer, TimeRangeSerializer


# TODO:
# - Repeating time ranges
# - Add Hang Events to Google Calendar
# - Algorithms
# - Add to Hang though link
# - API methods: given a list of users, give free times and given a free time give a list of free users
class ManualTimeRangeCreateView(udbgenerics.UpdateDBCreateAPIView):
    queryset = ManualTimeRange.objects.all()
    serializer_class = ManualTimeRangeSerializer
    permission_classes = [IsAuthenticated]
    update_db_actions = [update_db_send_rtws_message]
    rtws_update_actions = ["calendars"]

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


class CustomDateBasedPagination(BasePagination):
    page_size = 50

    def paginate_queryset(self, queryset, request, view=None):
        # Sort the queryset by start_time
        self.request = request
        queryset = sorted(queryset, key=lambda x: parse(x['start_time']))

        start_index = 0
        for idx, item in enumerate(queryset):
            item_start_time = parse(item['start_time'])
            if item_start_time >= self.start_time:
                start_index = idx
                break

        paginated_data = queryset[start_index: start_index + self.page_size]
        self.has_next_page = len(queryset) > start_index + self.page_size
        self.has_previous_page = start_index > 0
        self.previous_start_date = queryset[max(0, start_index - self.page_size - 1)][
            'start_time'] if self.has_previous_page else None
        self.next_start_date = queryset[start_index + self.page_size]['start_time'] if self.has_next_page else None
        return paginated_data

    def get_paginated_response(self, data):
        response_data = {
            'results': data,
        }

        if self.next_start_date:
            response_data['next'] = self.next_start_date
        else:
            response_data['next'] = None

        if self.previous_start_date:
            response_data['prev'] = self.previous_start_date
        else:
            response_data['prev'] = None

        return Response(response_data)


class BusyTimeRangesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, format=None):
        start_time = request.query_params.get('start_time')
        if start_time:
            try:
                start_time = parse(start_time).replace(tzinfo=timezone.utc)
            except ValueError:
                return Response("Invalid datetime format. Use ISO format (e.g., '2023-05-01T12:00:00Z').",
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            start_time = timezone.now()

        user = get_object_or_404(User, pk=user_id)

        if user != request.user and user not in request.user.userdetails.friends.all():
            return Response("Invalid Permissions", status=status.HTTP_400_BAD_REQUEST)

        manual_time_ranges = ManualTimeRange.objects.filter(calendar__user=user)
        imported_time_ranges = ImportedTimeRange.objects.filter(calendar__user=user)

        busy_ranges = [(r.start_time, r.end_time) for r in imported_time_ranges]
        busy_ranges.extend([(r.start_time, r.end_time) for r in manual_time_ranges.filter(type="busy")])
        busy_ranges.extend([(e.scheduled_time_start, e.scheduled_time_end) for e in
                            HangEvent.objects.filter(attendees=request.user).all()])

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

        paginator = CustomDateBasedPagination()
        paginator.start_time = start_time
        page = paginator.paginate_queryset(serializer.data, request)
        return paginator.get_paginated_response(page)
