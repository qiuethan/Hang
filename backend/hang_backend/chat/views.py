import time
import json
from datetime import datetime

from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest

from chat.models import MessageChannel, Message

# Create your views here.


def load_past_messages(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()
    chat_room = request.POST['room']
    before = request.POST['before']
    try:
        m = MessageChannel.objects.get(id=chat_room)
    except MessageChannel.DoesNotExist:
        m = MessageChannel(id=chat_room)
        m.save()
    except MessageChannel.MultipleObjectsReturned:
        pass

    req_time = timezone.make_aware(datetime.fromtimestamp(before))

    messages = m.message_set.all().filter(
        created_at__lte=str(req_time)).order_by('-created_at')

    msg_list = []

    for e in messages[:min(20, len(messages))]:
        msg_list.append({'message': e.content, 'time': int(
            time.mktime(e.created_at.timetuple()))})

    return HttpResponse(json.dumps(msg_list))
