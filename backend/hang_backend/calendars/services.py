from calendars.models import ManualTimeRange, RepeatingTimeRange, ImportedTimeRange
from hang_events.models import HangEvent


class TimeRangeService:
    @staticmethod
    def merge_overlapping_ranges(sorted_ranges):
        merged_ranges = []
        for start, end in sorted_ranges:
            if not merged_ranges or merged_ranges[-1][1] < start:
                merged_ranges.append((start, end))
            else:
                merged_ranges[-1] = (merged_ranges[-1][0], max(merged_ranges[-1][1], end))
        return merged_ranges

    @staticmethod
    def merge_free_and_busy_times(sorted_free_ranges, sorted_busy_ranges):
        merged_ranges = []
        j = 0
        free_end = None
        for i in range(len(sorted_busy_ranges)):
            start, end = sorted_busy_ranges[i]
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
        manual_time_ranges = ManualTimeRange.objects.filter(calendar__user=user)
        repeating_time_ranges = RepeatingTimeRange.objects.filter(calendar__user=user)
        imported_time_ranges = ImportedTimeRange.objects.filter(calendar__user=user)

        busy_ranges = [(r.start_time, r.end_time) for r in imported_time_ranges]
        busy_ranges.extend([(r.start_time, r.end_time) for r in manual_time_ranges.filter(type="busy")])
        busy_ranges.extend([(e.scheduled_time_start, e.scheduled_time_end) for e in
                            HangEvent.objects.filter(attendees=user.id).all()])
        for r in repeating_time_ranges:
            busy_ranges.extend(r.decompress(start_time))

        free_ranges = [(r.start_time, r.end_time) for r in manual_time_ranges.filter(type="free")]

        busy_ranges = sorted(busy_ranges, key=lambda x: x[0])
        free_ranges = sorted(free_ranges, key=lambda x: x[0])

        merged_busy_ranges = TimeRangeService.merge_overlapping_ranges(busy_ranges)
        merged_ranges = TimeRangeService.merge_free_and_busy_times(free_ranges, merged_busy_ranges)

        return merged_ranges
