from rest_framework import status
from rest_framework.response import Response
from rest_framework.settings import api_settings

from real_time_ws.consumers import send_message


class RTWSGenericMixin:
    def send_rtws_message(self, users):
        for user in users:
            for update_action in self.update_actions:
                send_message(user, update_action)


class RTWSCreateModelMixin(RTWSGenericMixin):
    """
    Create a model instance and sends message to the real time websocket.
    """

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        self.send_rtws_message(self.get_users(serializer.data))
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}


class RTWSDestroyModelMixin(RTWSGenericMixin):
    """
    Destroy a model instance and sends message to the real time websocket.
    """

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        self.send_rtws_message(self.get_users(serializer.data))
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()


class RTWSUpdateModelMixin(RTWSGenericMixin):
    """
    Update a model instance and sends message to the real time websocket.
    """

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        self.send_rtws_message(
            self.get_users(serializer.data).union(self.get_users(self.get_serializer(instance).data)))
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
