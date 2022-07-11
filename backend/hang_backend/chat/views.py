import json
import random
import string
import time
from datetime import datetime

from .models import MessageChannel
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound, HttpResponseServerError
from django.utils import timezone
from rest_framework import generics, permissions


# Create your views here.


class LoadMessage(generics.CreateAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request):
        chat_room = request.GET['room']
        before = int(request.GET['before'])
        try:
            m = MessageChannel.objects.get(id=chat_room)
        except MessageChannel.DoesNotExist:
            return HttpResponseNotFound()
        except MessageChannel.MultipleObjectsReturned:
            return HttpResponseServerError()

        if request.user.is_anonymous or not m.users.filter(id=request.user.id).exists():
            return HttpResponseForbidden()

        req_time = timezone.make_aware(datetime.fromtimestamp(before))

        messages = m.message_set.all().filter(
            created_at__lte=str(req_time)).order_by('-created_at')

        msg_list = []

        for e in messages[:min(20, len(messages))]:
            msg_list.append({
                'id': e.id,
                'user': e.user.username,
                'message': e.content,
                'time': int(time.mktime(e.created_at.timetuple()))
            }
            )
        return HttpResponse(json.dumps(msg_list))


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


class ListMessageChannels(generics.CreateAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request):
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

        return HttpResponse(0)

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
