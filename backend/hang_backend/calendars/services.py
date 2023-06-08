"""
ICS4U
Paul Chen
This module provides a service for managing time ranges. It includes functionalities for merging overlapping time ranges,
merging free and busy times, and deriving free times from busy times. It also includes a method to retrieve a user's busy time ranges.
"""

from calendars.models import ManualTimeRange, RepeatingTimeRange, ImportedTimeRange
from hang_events.models import HangEvent


class TimeRangeService:
    """
    A service for managing time ranges.
    """

    @staticmethod
    def merge_overlapping_ranges(sorted_ranges):
        """
        Merges overlapping time ranges.

        Arguments:
          sorted_ranges (list of tuples): A sorted list of tuples, each representing a time range with a start and end time.

        Returns:
          list of tuples: A list of merged time ranges where overlapping ranges have been combined.
        """
        merged_ranges = []
        for start, end in sorted_ranges:
            # If the merged_ranges list is empty or the end of the last range in the list is before the start of the current range
            if not merged_ranges or merged_ranges[-1][1] < start:
                merged_ranges.append((start, end))
            else:
                # If the current range overlaps with the last range in the list, merge them
                merged_ranges[-1] = (merged_ranges[-1][0], max(merged_ranges[-1][1], end))
        return merged_ranges

    @staticmethod
    def merge_free_and_busy_times(sorted_free_ranges, sorted_busy_ranges):
        """
        Merges free and busy time ranges.

        Arguments:
          sorted_free_ranges (list of tuples): A sorted list of tuples, each representing a free time range with a start and end time.
          sorted_busy_ranges (list of tuples): A sorted list of tuples, each representing a busy time range with a start and end time.

        Returns:
          list of tuples: A list of merged time ranges where free and busy times have been combined.
        """
        # Uses a two-pointers algorithm to merge time ranges.
        merged_ranges = []
        j = 0
        free_end = None
        for i in range(len(sorted_busy_ranges)):
            start, end = sorted_busy_ranges[i]
            # Iterate over the free ranges that overlap with the current busy range
            while j < len(sorted_free_ranges) and sorted_free_ranges[j][0] < end:
                if free_end is not None:
                    start = max(start, free_end)
                if start >= end:
                    break
                if start < sorted_free_ranges[j][1]:
                    if start < sorted_free_ranges[j][0]:
                        merged_ranges.append((start, sorted_free_ranges[j][0]))
                    start = sorted_free_ranges[j][1]
                if free_end is None:
                    free_end = sorted_free_ranges[j][1]
                else:
                    free_end = max(free_end, sorted_free_ranges[j][1])
                j += 1
            if free_end is not None:
                start = max(start, free_end)
            if start < end:
                merged_ranges.append((start, end))
        return merged_ranges

    @staticmethod
    def get_free_times_from_busy_times(sorted_busy_ranges, start_time, end_time):
        """
        Derives free time ranges from busy time ranges within a given period.

        Arguments:
          sorted_busy_ranges (list of tuples): A sorted list of tuples, each representing a busy time range with a start and end time.
          start_time (datetime): The start time of the period to consider.
          end_time (datetime): The end time of the period to consider.

        Returns:
          list of tuples: A list of free time ranges derived from the busy time ranges within the given period.
        """
        free_ranges = []
        if sorted_busy_ranges:
            # Find time slots between the busy slots
            for i in range(len(sorted_busy_ranges) - 1):
                if sorted_busy_ranges[i][1] < sorted_busy_ranges[i + 1][0]:
                    free_ranges.append((sorted_busy_ranges[i][1], sorted_busy_ranges[i + 1][0]))

            # Check if there's a free slot before the first busy slot and after the last busy slot
            if start_time < sorted_busy_ranges[0][0]:
                free_ranges.insert(0, (start_time, sorted_busy_ranges[0][0]))
            if end_time > sorted_busy_ranges[-1][1]:
                free_ranges.append((sorted_busy_ranges[-1][1], end_time))

        elif start_time < end_time:
            # If there are no busy slots, the entire given period is free
            free_ranges.append((start_time, end_time))
        return free_ranges

    @staticmethod
    def get_user_busy_ranges(user, start_time):
        """
        Retrieves a user's busy time ranges.

        Arguments:
          user (User): The user to get the busy time ranges for.
          start_time (datetime): The start time of the period to consider.

        Returns:
          list of tuples: A list of the user's busy time ranges.
        """
        # Get the user's manual, repeating, and imported time ranges
        manual_time_ranges = ManualTimeRange.objects.filter(calendar__user=user)
        repeating_time_ranges = RepeatingTimeRange.objects.filter(calendar__user=user)
        imported_time_ranges = ImportedTimeRange.objects.filter(calendar__user=user)

        # Get the start and end times of the user's busy time ranges
        busy_ranges = [(r.start_time, r.end_time) for r in imported_time_ranges]
        busy_ranges.extend([(r.start_time, r.end_time) for r in manual_time_ranges.filter(type="busy")])
        busy_ranges.extend([(e.scheduled_time_start, e.scheduled_time_end) for e in
                            HangEvent.objects.filter(attendees=user.id).all()])
        for r in repeating_time_ranges:
            busy_ranges.extend(r.decompress(start_time))

        # Get the start and end times of the user's free time ranges
        free_ranges = [(r.start_time, r.end_time) for r in manual_time_ranges.filter(type="free")]

        # Sort the busy and free time ranges by start time
        busy_ranges = sorted(busy_ranges, key=lambda x: x[0])
        free_ranges = sorted(free_ranges, key=lambda x: x[0])

        # Merge overlapping busy time ranges and merge free and busy time ranges
        merged_busy_ranges = TimeRangeService.merge_overlapping_ranges(busy_ranges)
        merged_ranges = TimeRangeService.merge_free_and_busy_times(free_ranges, merged_busy_ranges)

        return merged_ranges
