from rest_framework.response import Response


class ListIDModelMixin:
    """
    List a queryset.
    """

    def list(self, request):
        return Response(self.get_queryset().values_list("pk", flat=True))
