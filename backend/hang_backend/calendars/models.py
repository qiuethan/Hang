"""
ICS4U
Paul Chen
This module defines the models for the calendars package.
"""

import json
from datetime import datetime, timedelta

from dateutil.parser import parse
from django.contrib.auth.models import User
from django.db import models
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from rest_framework import serializers

from accounts.models import GoogleAuthenticationToken
from real_time_ws.models import RTWSSendMessageOnUpdate


class ManualCalendar(models.Model):
    """
    Model that contains the user’s manual changes to their calendar
    (i.e. the ones that are not automatically imported from Google Calendar).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)


class ImportedCalendar(models.Model):
    """
    Model that contains the user’s calendar data that is imported from Google Calendar.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)


class GoogleCalendar(models.Model):
    """
    Represents the list of Google Calendars that are currently synced with the user’s ImportedCalendar.

    Attributes:
        calendar (ForeignKey[ImportedCalendar]): The ImportedCalendar associated with this GoogleCalendar.
        google_calendar_id (CharField): The unique ID of the Google Calendar.
        name (CharField): The name of the Google Calendar that will be displayed to the user.
    """
    calendar = models.ForeignKey(ImportedCalendar, on_delete=models.CASCADE)
    google_calendar_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    @staticmethod
    def fetch_free_busy_ranges(authentication_token, calendar_data_list):
        """
        Fetches free/busy time ranges for a given list of calendars.

        Arguments:
            authentication_token (GoogleAuthenticationToken): Token for Google API authentication.
            calendar_data_list (list): List of calendars for which to fetch time ranges.

        Returns:
            list[ImportedTimeRange]: List of ImportedTimeRange instances representing the free/busy time ranges.
        """
        # Initialize start time
        time_min = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        time_ranges = []

        # Authenticate and build service
        credentials = Credentials(token=authentication_token.access_token)
        service = build('calendar', 'v3', credentials=credentials)

        # Fetch free/busy time ranges for next 12 months
        for i in range(6):
            # Set end time for current month
            time_max = (datetime.utcnow() + timedelta(days=(i + 1) * 60)).replace(
                microsecond=0).isoformat() + "Z"

            # Prepare request data
            data = {
                "timeMin": time_min,
                "timeMax": time_max,
                "items": [{"id": cal_data['id']} for cal_data in calendar_data_list]
            }

            try:
                # Execute the query
                response = service.freebusy().query(body=data).execute()
            except HttpError as error:
                raise Exception(f"An error occurred: {error}")

            # Load response into dictionary
            result = json.loads(json.dumps(response))

            # Extract time ranges and append to list
            for cal_data in calendar_data_list:
                cal_id = cal_data['id']
                cal_info = result['calendars'][cal_id]
                for busy_range in cal_info['busy']:
                    time_ranges.append(
                        ImportedTimeRange(
                            start_time=parse(busy_range['start']),
                            end_time=parse(busy_range['end']),
                            calendar=authentication_token.user.importedcalendar
                        )
                    )
            # Set start time for next query to end time of this query
            time_min = time_max

        return time_ranges

    @staticmethod
    def sync_google_calendar(imported_calendar, calendar_data_list):
        """
        Synchronizes GoogleCalendar instances with given calendar data.

        Arguments:
            imported_calendar (ImportedCalendar): The ImportedCalendar to synchronize.
            calendar_data_list (list): List of calendars to sync.
        """
        # Delete existing GoogleCalendar instances related to the given ImportedCalendar
        GoogleCalendar.objects.filter(calendar=imported_calendar).delete()

        # Create new GoogleCalendar instances based on provided data
        for cal_data in calendar_data_list:
            GoogleCalendar.objects.create(
                calendar=imported_calendar,
                google_calendar_id=cal_data['id'],
                name=cal_data['name']
            )

    @staticmethod
    def fetch_calendar_data(user):
        """
        Fetches calendar data for a user from Google Calendar API.

        Arguments:
            user (User): The user to fetch calendar data for.

        Returns:
            list: List of dictionaries containing calendar data.
        """
        # Retrieve and refresh access token for the user
        try:
            access_token = GoogleAuthenticationToken.objects.get(user=user)
            access_token.refresh_access_token()
        except GoogleAuthenticationToken.DoesNotExist:
            raise serializers.ValidationError("Access token not found for the current user.")

        credentials = Credentials(token=access_token.access_token)

        # Fetch calendar list from Google Calendar API
        try:
            service = build('calendar', 'v3', credentials=credentials)
            calendar_list = service.calendarList().list().execute()
        except HttpError as error:
            raise serializers.ValidationError(f"Error fetching calendar data: {error}")

        # Get list of existing GoogleCalendar ids for the user
        existing_calendars = GoogleCalendar.objects.filter(calendar__user=user)
        existing_calendar_ids = [calendar.google_calendar_id for calendar in existing_calendars]

        # Prepare calendar data to return
        calendar_list_data = [
            {
                "google_calendar_id": item["id"],
                "name": item["summary"],
                "previous": item["id"] in existing_calendar_ids
            }
            for item in calendar_list["items"]
        ]
        return calendar_list_data


class ManualTimeRange(models.Model, RTWSSendMessageOnUpdate):
    """
    Represents a time range on the user’s ManualCalendar.

    Attributes:
        calendar (ForeignKey[ManualCalendar]): The ManualCalendar associated with this time range.
        type (CharField): The type of the time range, either "busy" or "free".
        start_time (DateTimeField): The start time of the time range.
        end_time (DateTimeField): The end time of the time range.
    """
    calendar = models.ForeignKey(ManualCalendar, on_delete=models.CASCADE)
    type = models.CharField(max_length=4, choices=(("busy", "busy"), ("free", "free")))
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    rtws_message_content = "calendar"

    def get_rtws_users(self):
        return [self.calendar.user]


class RepeatingTimeRange(models.Model, RTWSSendMessageOnUpdate):
    """
    Model that represents a time range that repeats on the user’s ManualCalendar.

    Attributes:
        calendar (ManualCalendar): The ManualCalendar associated with this time range.
        start_time (datetime): The start time of the time range.
        end_time (datetime): The end time of the time range.
        repeat_interval (int): The interval in weeks at which the time range repeats.
        repeat_count (int): The number of times the time range repeats.
    """
    calendar = models.ForeignKey(ManualCalendar, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    repeat_interval = models.IntegerField()  # Repeat every x weeks
    repeat_count = models.IntegerField()  # Number of times the event repeats

    rtws_message_content = "calendar"

    def get_rtws_users(self):
        return [self.calendar.user]

    def decompress(self, decompress_start_time):
        """
        Decompresses the repeating time range into individual time ranges.

        Arguments:
            decompress_start_time (datetime): The start time from which to decompress the time ranges.

        Returns:
            list: A list of tuples, each representing a time range.
        """
        # Initialize start and end times
        start_time = self.start_time
        end_time = self.end_time

        # If repeat_count is -1, the event repeats indefinitely
        if self.repeat_count == -1:
            # Calculate the number of intervals needed to reach decompress_start_time
            intervals_to_reach_start = max(0, (decompress_start_time - start_time).days // (7 * self.repeat_interval))
            start_time += timedelta(weeks=intervals_to_reach_start * self.repeat_interval)
            end_time += timedelta(weeks=intervals_to_reach_start * self.repeat_interval)
        else:
            # Calculate the final range start_time and end_time
            final_end_time = end_time + timedelta(weeks=self.repeat_interval * (self.repeat_count - 1))

            # If decompress_start_time is after the final range, return an empty list
            if decompress_start_time > final_end_time:
                return []

        # Initialize list to hold decompressed ranges
        decompressed_ranges = []

        # Loop to generate decompressed ranges
        while len(decompressed_ranges) < 60:
            # Append current range to list if it is after the decompress start time
            if start_time >= decompress_start_time:
                decompressed_ranges.append((start_time, end_time))

            # Increment start and end times for next range
            start_time += timedelta(weeks=self.repeat_interval)
            end_time += timedelta(weeks=self.repeat_interval)

            # Break loop if we have reached the final end time
            if self.repeat_count != -1 and start_time > final_end_time:
                break

        return decompressed_ranges


class ImportedTimeRange(models.Model, RTWSSendMessageOnUpdate):
    """
    Model that represents a time range on the user’s ImportedCalendar.

    Attributes:
        calendar (ImportedCalendar): The ImportedCalendar associated with this time range.
        start_time (datetime): The start time of the time range.
        end_time (datetime): The end time of the time range.
    """
    calendar = models.ForeignKey(ImportedCalendar, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    rtws_message_content = "calendar"

    def get_rtws_users(self):
        return [self.calendar.user]
