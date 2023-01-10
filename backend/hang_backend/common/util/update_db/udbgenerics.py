# Concrete view classes that provide method handlers
# by composing the mixin classes with the base view.
from rest_framework import mixins
from rest_framework.generics import GenericAPIView
from . import udbmixins


# Classes below fulfill the same purpose as DRF's generic API classes,
# but they also send updates to the real time websocket.

class UpdateDBCreateAPIView(udbmixins.UpdateDBCreateModelMixin,
                            GenericAPIView):
    """
    Concrete view for creating a model instance.
    """

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class UpdateDBDestroyAPIView(udbmixins.UpdateDBDestroyModelMixin,
                             GenericAPIView):
    """
    Concrete view for deleting a model instance.
    """

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class UpdateDBUpdateAPIView(udbmixins.UpdateDBUpdateModelMixin,
                            GenericAPIView):
    """
    Concrete view for updating a model instance.
    """

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class UpdateDBListCreateAPIView(mixins.ListModelMixin,
                                udbmixins.UpdateDBCreateModelMixin,
                                GenericAPIView):
    """
    Concrete view for listing a queryset or creating a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class UpdateDBRetrieveUpdateAPIView(mixins.RetrieveModelMixin,
                                    udbmixins.UpdateDBUpdateModelMixin,
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


class UpdateDBRetrieveDestroyAPIView(mixins.RetrieveModelMixin,
                                     udbmixins.UpdateDBDestroyModelMixin,
                                     GenericAPIView):
    """
    Concrete view for retrieving or deleting a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class UpdateDBRetrieveUpdateDestroyAPIView(mixins.RetrieveModelMixin,
                                           udbmixins.UpdateDBUpdateModelMixin,
                                           udbmixins.UpdateDBDestroyModelMixin,
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
