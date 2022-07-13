# chat/consumers.py
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User

from .models import Message, MessageChannel
from .serializers import MessageSerializer


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

                message_channel = self.get_message_channel(channel)
                if message_channel is None:
                    return

                msg_obj = Message(user=self.user, content=message, message_channel=message_channel)
                msg_obj.save()
                self.success()

                for e in message_channel.users.all():
                    async_to_sync(self.channel_layer.group_send)(
                        e.username,
                        {
                            'type': 'receive_message',
                            'message': MessageSerializer(msg_obj).data,
                        }
                    )
            elif text_data_json['type'] == 'load':
                channel = text_data_json['channel']
                before = text_data_json.get('before', Message.objects.latest('id').id + 1000000000)

                message_channel = self.get_message_channel(channel)
                if message_channel is None:
                    return

                messages = message_channel.message_set.all().filter(
                    id__lte=before).order_by('-id')

                msg_list = []
                for e in messages[:min(20, len(messages))]:
                    msg_list.append(MessageSerializer(e).data)

                async_to_sync(self.channel_layer.send)(
                    self.channel_name,
                    {
                        'type': 'load_message',
                        'messages': msg_list,
                    }
                )

                self.success()
            elif text_data_json['type'] == 'edit':
                message_id = text_data_json['message_id']
                new_message = text_data_json['new_message']

                message = self.get_message(message_id)
                if message is None:
                    return

                message_channel_id = message.message_channel_id

                if message.user.id != self.user.id:
                    self.error('cannot modify another user\'s message')
                message.content = new_message
                message.save()

                message_channel = self.get_message_channel(message_channel_id)
                if message_channel is None:
                    return

                self.success()

                for e in message_channel.users.all():
                    async_to_sync(self.channel_layer.group_send)(
                        e.username,
                        {
                            'type': 'edit_message',
                            'message': MessageSerializer(message).data
                        }
                    )
            elif text_data_json['type'] == 'delete':
                message_id = text_data_json['message_id']

                message = self.get_message(message_id)
                if message is None:
                    return

                message_channel_id = message.message_channel_id

                if message.user.id != self.user.id:
                    self.error('cannot modify another user\'s message')
                    return
                message.delete()

                message_channel = self.get_message_channel(message_channel_id)
                if message_channel is None:
                    return

                self.success()

                for e in message_channel.users.all():
                    async_to_sync(self.channel_layer.group_send)(
                        e.username,
                        {
                            'type': 'delete_message',
                            'id': message_id,
                        }
                    )

        except (json.JSONDecodeError, KeyError):
            self.error('invalid json')

    def get_message_channel(self, channel_id):
        try:
            message_channel = MessageChannel.objects.get(id=channel_id)
            if not message_channel.users.filter(username=self.user.username).exists():
                raise MessageChannel.DoesNotExist()
            return message_channel
        except MessageChannel.DoesNotExist:
            self.error('message channel does not exist')
        except MessageChannel.MultipleObjectsReturned:
            self.error('internal server error')
        return None

    def get_message(self, message_id):
        try:
            message = Message.objects.get(id=message_id)
            if message.user.id != self.user.id:
                raise Message.DoesNotExist()
            return message
        except Message.DoesNotExist:
            self.error('message does not exist')
        return None

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

    def status(self, event):
        self.send(text_data=json.dumps({
            'type': 'status',
            'message': event['message'],
        }))

    def receive_message(self, event):
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': 'receive_message',
            'message': event['message'],
        }))

    def load_message(self, event):
        self.send(text_data=json.dumps({
            'type': 'load_message',
            'messages': event['messages'],
        }))

    def edit_message(self, event):
        self.send(text_data=json.dumps({
            'type': 'edit_message',
            'message': event['message'],
        }))

    def delete_message(self, event):
        self.send(text_data=json.dumps({
            'type': 'delete_message',
            'id': event['id'],
        }))
