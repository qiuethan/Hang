from rest_framework import status
from rest_framework.response import Response
from rest_framework.settings import api_settings


class UpdateDBGenericMixin:
    def perform_update_db_actions(self, *serializers, current_user=None, request_type=None):
        for action in self.update_db_actions:
            action(self, *serializers, current_user=current_user, request_type=request_type)


class UpdateDBCreateModelMixin(UpdateDBGenericMixin):
    """
    Create a model instance and sends message to the real time websocket.
    """

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        self.perform_update_db_actions(serializer, current_user=request.user, request_type="POST")
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}


class UpdateDBDestroyModelMixin(UpdateDBGenericMixin):
    """
    Destroy a model instance and sends message to the real time websocket.
    """

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        self.perform_update_db_actions(serializer, current_user=request.user, request_type="DELETE")
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()


class UpdateDBUpdateModelMixin(UpdateDBGenericMixin):
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
        self.perform_update_db_actions(serializer, self.get_serializer(instance), current_user=request.user,
                                       request_type="PATCH")
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
