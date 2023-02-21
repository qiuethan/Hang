from rest_framework.generics import GenericAPIView

from common.util.generics import mixins


class ListIDAPIView(mixins.ListIDModelMixin, GenericAPIView):
    """
    Concrete view for listing a queryset.
    """

    def get(self, request, *args, **kwargs):
        return self.list(request)
