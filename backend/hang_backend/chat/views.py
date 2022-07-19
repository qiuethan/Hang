import random
import string

from django.http import JsonResponse
from rest_framework import generics, permissions

from .models import MessageChannel
from .serializers import CreateDMSerializer, MessageChannelFullSerializer, CreateGCSerializer


class CreateDMView(generics.CreateAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = CreateDMSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data

        try:
            dm = request.user.messagechannel_set.all().filter(channel_type="DM").get(users=user)
        except MessageChannel.DoesNotExist:
            def generate_random_string():
                return ''.join(
                    [random.choice(string.ascii_letters) for _ in range(10)])

            ss = generate_random_string()
            while MessageChannel.objects.filter(id=ss).exists():
                ss = generate_random_string()

            dm = MessageChannel(id=ss, name=f"DM {user.username} {request.user.username}", channel_type="DM")
            dm.save()

            dm.users.add(request.user)
            dm.users.add(user)
        except MessageChannel.MultipleObjectsReturned:
            return JsonResponse({"email": ["Cannot create a DM with yourself."]})
        return JsonResponse(MessageChannelFullSerializer(dm).data)


class CreateGCView(generics.CreateAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = CreateGCSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        def generate_random_string():
            return ''.join(
                [random.choice(string.ascii_letters) for _ in range(10)])

        ss = generate_random_string()
        while MessageChannel.objects.filter(id=ss).exists():
            ss = generate_random_string()

        gc = MessageChannel(id=ss, name=serializer.validated_data["name"], channel_type="GC")
        gc.save()

        gc.users.add(request.user)

        for user in serializer.validated_data["users"]:
            gc.users.add(user)

        return JsonResponse(MessageChannelFullSerializer(gc).data)


# TODO add to gc


class ListMessageChannelsView(generics.ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, **kwargs):
        message_channels = request.user.messagechannel_set.all()

        ret = MessageChannelFullSerializer(message_channels, many=True)

        return JsonResponse(ret.data, safe=False)
