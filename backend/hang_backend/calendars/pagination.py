"""
ICS4U
Paul Chen
This module provides a custom pagination class for Django REST framework. The pagination is based on dates, allowing for chronological navigation through data.
"""

from dateutil.parser import parse
from rest_framework.pagination import BasePagination
from rest_framework.response import Response


class DateBasedPagination(BasePagination):
    """
    A custom pagination class that provides date-based pagination for a given queryset.

    Attributes:
      page_size (int): The maximum number of items to be returned in one page.
      start_time (datetime): The starting point for pagination.
    """
    page_size = 50

    def __init__(self, start_time):
        """
        Initialize the DateBasedPagination instance with a start_time.

        Arguments:
          start_time (datetime): The starting point for pagination.
        """
        self.start_time = start_time

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate the queryset based on start_time and page size.

        Arguments:
          queryset (QuerySet): The queryset to be paginated.
          request (Request): The request object.
          view (View, optional): The view that the request was made to.

        Returns:
          list: The paginated data.
        """
        self.request = request  # Store the request for later use

        # Sort the queryset by start_time
        queryset = sorted(queryset, key=lambda x: parse(x['start_time']))

        # Find the start index for pagination
        start_index = len(queryset)
        for idx, item in enumerate(queryset):
            item_start_time = parse(item['start_time'])
            if item_start_time >= self.start_time:
                start_index = idx
                break

        # Slice the queryset to get the paginated data
        paginated_data = queryset[start_index: start_index + self.page_size]

        # Check if there are more pages
        self.has_next_page = len(queryset) > start_index + self.page_size
        self.has_previous_page = start_index > 0

        # Store the start times for the next and previous pages
        self.previous_start_date = queryset[max(0, start_index - self.page_size - 1)][
            'start_time'] if self.has_previous_page else None
        self.next_start_date = queryset[start_index + self.page_size]['start_time'] if self.has_next_page else None

        return paginated_data

    def get_paginated_response(self, data):
        """
        Return a Response with the paginated data and next/previous page start times.
        """
        # Prepare the response data
        response_data = {
            'results': data,
            'next': self.next_start_date if self.next_start_date else None,
            'prev': self.previous_start_date if self.previous_start_date else None
        }

        return Response(response_data)
