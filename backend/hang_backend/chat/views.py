import json
import random
import string

from django.contrib.auth.models import User
from django.http import HttpResponse
from rest_framework import generics, permissions

from .models import MessageChannel


class CreateDM(generics.CreateAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def post(self, request, *args, **kwargs):
        to = request.POST.get('to', None)

        to_u = User.objects.get(email=to)

        try:
            dm = request.user.messagechannel_set.all().filter(channel_type=0).get(users=to_u)

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
            m.users.add(to_u)

            cid = ss
        except MessageChannel.MultipleObjectsReturned:
            pass
        return HttpResponse(cid)


class ListMessageChannels(generics.ListAPIView):
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
        # print({{"id": mc.id, "users": mc.users, "channel_type": mc.channel_type} for mc in message_channels})

# def open_dm(request):
#     if request.method != 'POST':
#         return HttpResponseBadRequest()
#     print(request.user.is_authenticated)
#     print(request.user)
#     to = request.POST.get('to', None)
#     generate_random_string = lambda: ''.join([random.choice(string.ascii_letters) for _ in range(10)])
#     print(request.user)
#     return HttpResponse(str(request.user.username))

# while
# try:
#     m = MessageChannel.objects.get(id=room_name)
# except MessageChannel.DoesNotExist:
#     m = MessageChannel(id=room_name)
#     m.save()
# except MessageChannel.MultipleObjectsReturned:
#     pass
