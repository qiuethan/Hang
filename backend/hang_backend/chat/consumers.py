# chat/consumers.py
import calendar
import json
import time
from json import JSONDecodeError

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User

from .models import Message, MessageChannel


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        username = self.scope['url_route']['kwargs']['room_name']

        if self.scope['user'].is_anonymous or username != self.scope['user'].username:
            self.close(403)

        self.user = User.objects.get(username=username)

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.user.username,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.user.username,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data=None, bytes_data=None):
        try:
            text_data_json = json.loads(text_data)

            if text_data_json['type'] == 'send':
                channel = text_data_json['channel']
                message = text_data_json['message']
                try:
                    message_channel = MessageChannel.objects.get(id=channel)
                    if not message_channel.users.filter(username=self.user.username).exists():
                        raise MessageChannel.DoesNotExist()
                except MessageChannel.DoesNotExist:
                    async_to_sync(self.channel_layer.group_send)(
                        self.channel_name,
                        {
                            'type': 'status',
                            'message': 'message channel does not exist',
                        }
                    )
                    return
                except MessageChannel.MultipleObjectsReturned:
                    async_to_sync(self.channel_layer.group_send)(
                        self.channel_name,
                        {
                            'type': 'status',
                            'message': 'internal server error',
                        }
                    )
                    return

                msg_obj = Message(user=self.user, content=message, message_channel=message_channel)
                msg_obj.save()
                msg_time = int(calendar.timegm(msg_obj.created_at.timetuple()))

                async_to_sync(self.channel_layer.group_send)(
                    self.channel_name,
                    {
                        'type': 'status',
                        'message': 'success',
                    }
                )

                for e in message_channel.users.all():
                    async_to_sync(self.channel_layer.group_send)(
                        e.username,
                        {
                            'type': 'receive_message',
                            'channel': channel,
                            'user': self.user.username,
                            'message': message,
                            'time': msg_time,
                        }
                    )
            elif text_data_json['type'] == 'load':
                channel = text_data_json['channel']
                before = text_data_json['before']
                try:
                    message_channel = MessageChannel.objects.get(id=channel)
                    if not message_channel.users.filter(username=self.user.username).exists():
                        raise MessageChannel.DoesNotExist()
                except MessageChannel.DoesNotExist:
                    async_to_sync(self.channel_layer.group_send)(
                        self.channel_name,
                        {
                            'type': 'status',
                            'message': 'message channel does not exist',
                        }
                    )
                    return
                except MessageChannel.MultipleObjectsReturned:
                    async_to_sync(self.channel_layer.group_send)(
                        self.channel_name,
                        {
                            'type': 'status',
                            'message': 'internal server error',
                        }
                    )
                    return

                messages = message_channel.message_set.all().filter(
                    id__lte=before).order_by('-id')

                msg_list = []
                for e in messages[:min(20, len(messages))]:
                    msg_list.append({
                        'id': e.id,
                        'user': e.user.username,
                        'message': e.content,
                        'time': int(time.mktime(e.created_at.timetuple()))
                    }
                    )

                async_to_sync(self.channel_layer.send)(
                    self.channel_name,
                    {
                        'type': 'load_message',
                        'messages': msg_list,
                    }
                )
        except (JSONDecodeError, KeyError):
            async_to_sync(self.channel_layer.group_send)(
                self.channel_name,
                {
                    'type': 'status',
                    'message': 'invalid json',
                }
            )

    def status(self, event):
        self.send(text_data=json.dumps({
            'type': 'status',
            'message': event['message'],
        }))

    def receive_message(self, event):
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': 'receive_message',
            'channel': event['channel'],
            'user': event['user'],
            'message': event['message'],
            'time': event['time'],
        }))

    def load_message(self, event):
        self.send(text_data=json.dumps({
            'type': 'load_message',
            'messages': event['messages'],
        }))
