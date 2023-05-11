from dateutil.parser import parse
from rest_framework.pagination import BasePagination
from rest_framework.response import Response


class DateBasedPagination(BasePagination):
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

