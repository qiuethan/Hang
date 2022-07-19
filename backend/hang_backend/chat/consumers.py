# chat/consumers.py
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User

from .models import Message, MessageChannel
from .serializers import MessageSerializer, SendMessageSerializer, LoadMessageSerializer, EditMessageSerializer, \
    DeleteMessageSerializer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        username = self.scope['url_route']['kwargs']['room_name']

        if self.scope['user'].is_anonymous or username != self.scope['user'].username:
            self.close(403)

        self.user = User.objects.get(username=username)

        async_to_sync(self.channel_layer.group_add)(
            self.user.username,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.user.username,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        try:
            text_data_json = json.loads(text_data)
            text_data_json['user'] = {'username': self.user.username}

            if text_data_json['type'] == 'send':
                self.send_message(text_data_json)
            elif text_data_json['type'] == 'load':
                self.load_message(text_data_json)
            elif text_data_json['type'] == 'edit':
                self.edit_message(text_data_json)
            elif text_data_json['type'] == 'delete':
                self.delete_message(text_data_json)

        except (json.JSONDecodeError, KeyError):
            self.error('Invalid json.')
        except (Exception,) as e:
            self.error('Internal server error.')

    def send_message(self, data):
        serializer = SendMessageSerializer(data=data)
        serializer.is_valid()

        if not serializer.is_valid():
            self.error(json.loads(json.dumps(serializer.errors)))
            return

        message = serializer.save()

        self.success()

        for e in message.message_channel.users.all():
            async_to_sync(self.channel_layer.group_send)(
                e.username,
                {
                    'type': 'action',
                    'action': 'send_message',
                    'content': {
                        'message': MessageSerializer(message).data,
                    },
                }
            )

    def load_message(self, data):
        serializer = LoadMessageSerializer(data=data)
        serializer.is_valid()

        if not serializer.is_valid():
            self.error(json.loads(json.dumps(serializer.errors)))
            return

        message_channel = serializer.validated_data['message_channel']
        message_id = serializer.validated_data['message_id']

        if message_id is None:
            messages = message_channel.message_set.all().order_by('-id')
        else:
            messages = message_channel.message_set.all().filter(
                id__lte=message_id).order_by('-id')

        msg_list = [MessageSerializer(e).data for e in messages[:min(20, len(messages))]]

        self.success()

        async_to_sync(self.channel_layer.send)(
            self.channel_name,
            {
                'type': 'action',
                'action': 'load_message',
                'content': {
                    'messages': msg_list,
                }
            }
        )

    def edit_message(self, data):
        serializer = EditMessageSerializer(data=data)
        serializer.is_valid()

        if not serializer.is_valid():
            self.error(json.loads(json.dumps(serializer.errors)))
            return

        message_id = serializer.validated_data['message_id']
        content = serializer.validated_data['content']
        message = Message.objects.get(id=message_id)

        message_channel_id = message.message_channel_id

        message.content = content
        message.save()

        self.success()

        for e in MessageChannel.objects.get(id=message_channel_id).users.all():
            async_to_sync(self.channel_layer.group_send)(
                e.username,
                {
                    'type': 'action',
                    'action': 'edit_message',
                    'content': {
                        'message': MessageSerializer(message).data
                    }
                }
            )

    def delete_message(self, data):
        serializer = DeleteMessageSerializer(data=data)
        serializer.is_valid()

        if not serializer.is_valid():
            self.error(json.loads(json.dumps(serializer.errors)))
            return

        message = Message.objects.get(id=serializer.validated_data['message_id'])
        message_channel = message.message_channel

        message.delete()

        self.success()

        for e in message_channel.users.all():
            async_to_sync(self.channel_layer.group_send)(
                e.username,
                {
                    'type': 'action',
                    'action': 'delete_message',
                    'content': {
                        'id': serializer.validated_data['message_id'],
                    }
                }
            )

    def status(self, event):
        self.send(text_data=json.dumps({
            'type': 'status',
            'message': event['message'],
        }))

    def success(self):
        async_to_sync(self.channel_layer.send)(
            self.channel_name,
            {
                'type': 'status',
                'message': 'success',
            }
        )

    def error(self, message):
        async_to_sync(self.channel_layer.send)(
            self.channel_name,
            {
                'type': 'status',
                'message': message,
            }
        )

    def action(self, event):
        self.send(text_data=json.dumps({
            'action': event['action'],
            'content': event['content'],
        }))
