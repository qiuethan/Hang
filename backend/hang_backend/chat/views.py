import json
import random
import string

from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from rest_framework import generics, permissions

from .models import MessageChannel
from .serializers import CreateDMSerializer


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
            dm = request.user.messagechannel_set.all().filter(channel_type=0).get(users=user)

            cid = dm.id
        except MessageChannel.DoesNotExist:
            def generate_random_string():
                return ''.join(
                    [random.choice(string.ascii_letters) for _ in range(10)])

            ss = generate_random_string()
            while MessageChannel.objects.filter(id=ss).exists():
                ss = generate_random_string()

            m = MessageChannel(id=ss, channel_type=0)
            m.save()

            m.users.add(request.user)
            m.users.add(user)

            cid = ss
        except MessageChannel.MultipleObjectsReturned:
            return JsonResponse({"email": ["Cannot create a DM with yourself."]})
        return HttpResponse(cid)


class ListMessageChannelsView(generics.ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, **kwargs):
        message_channels = request.user.messagechannel_set.all()
        ret = []
        for mc in message_channels:
            ret.append({
                "id": mc.id,
                "users": [u.username for u in mc.users.all()],
                "channel_type": mc.channel_type
            })
        return HttpResponse(json.dumps(ret))
