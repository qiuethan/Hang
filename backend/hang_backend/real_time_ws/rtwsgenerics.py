# Concrete view classes that provide method handlers
# by composing the mixin classes with the base view.
from rest_framework import mixins
from rest_framework.generics import GenericAPIView

from real_time_ws import rtwsmixins


# Classes below fulfill the same purpose as DRF's generic API classes,
# but they also send updates to the real time websocket.

class RTWSCreateAPIView(rtwsmixins.RTWSCreateModelMixin,
                        GenericAPIView):
    """
    Concrete view for creating a model instance.
    """

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RTWSDestroyAPIView(rtwsmixins.RTWSDestroyModelMixin,
                         GenericAPIView):
    """
    Concrete view for deleting a model instance.
    """

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class RTWSUpdateAPIView(rtwsmixins.RTWSUpdateModelMixin,
                        GenericAPIView):
    """
    Concrete view for updating a model instance.
    """

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class RTWSListCreateAPIView(mixins.ListModelMixin,
                            rtwsmixins.RTWSCreateModelMixin,
                            GenericAPIView):
    """
    Concrete view for listing a queryset or creating a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RTWSRetrieveUpdateAPIView(mixins.RetrieveModelMixin,
                                rtwsmixins.RTWSUpdateModelMixin,
                                GenericAPIView):
    """
    Concrete view for retrieving, updating a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class RTWSRetrieveDestroyAPIView(mixins.RetrieveModelMixin,
                                 rtwsmixins.RTWSDestroyModelMixin,
                                 GenericAPIView):
    """
    Concrete view for retrieving or deleting a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class RTWSRetrieveUpdateDestroyAPIView(mixins.RetrieveModelMixin,
                                       rtwsmixins.RTWSUpdateModelMixin,
                                       rtwsmixins.RTWSDestroyModelMixin,
                                       GenericAPIView):
    """
    Concrete view for retrieving, updating or deleting a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
