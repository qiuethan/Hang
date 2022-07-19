# chat/consumers.py
import json

from asgiref.sync import sync_to_async, async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User

from .models import Message, MessageChannel
from .serializers import MessageSerializer, SendMessageSerializer, LoadMessageSerializer, EditMessageSerializer, \
    DeleteMessageSerializer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        username = self.scope['url_route']['kwargs']['room_name']

        if self.scope['user'].is_anonymous or username != self.scope['user'].username:
            await self.close(403)

        self.user = await database_sync_to_async(User.objects.get)(username=username)

        await self.channel_layer.group_add(
            self.user.username,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user.username,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        try:
            text_data_json = json.loads(text_data)
            text_data_json['user'] = {'username': self.user.username}

            await getattr(self, text_data_json['type'])(text_data_json)

        except (json.JSONDecodeError, KeyError):
            await self.error('Invalid json.')
        except (Exception,) as e:
            await self.error('Internal server error.')

    async def send_message(self, data):
        serializer = SendMessageSerializer(data=data)

        if not await database_sync_to_async(serializer.is_valid)():
            await self.error(json.loads(json.dumps(serializer.errors)))
            return

        message = await database_sync_to_async(serializer.save)()

        await self.success()

        message_serializer = await sync_to_async(MessageSerializer)(message)

        @sync_to_async
        def send_messages():
            for user in message.message_channel.users.all():
                async_to_sync(self.channel_layer.group_send)(
                    user.username,
                    {
                        'type': 'action',
                        'action': 'send_message',
                        'content': {
                            'message': message_serializer.data,
                        },
                    }
                )

        await send_messages()

    async def load_message(self, data):
        serializer = LoadMessageSerializer(data=data)

        if not await database_sync_to_async(serializer.is_valid)():
            await self.error(json.loads(json.dumps(serializer.errors)))
            return

        message_channel = serializer.validated_data['message_channel']
        message_id = serializer.validated_data['message_id']

        if message_id is None:
            messages = message_channel.message_set.all().order_by('-id')
        else:
            messages = message_channel.message_set.all().filter(
                id__lte=message_id).order_by('-id')

        @sync_to_async
        def generate_message_list():
            return [MessageSerializer(e).data for e in messages[:min(20, len(messages))]]

        message_list = await generate_message_list()

        await self.success()

        await self.channel_layer.send(
            self.channel_name,
            {
                'type': 'action',
                'action': 'load_message',
                'content': {
                    'messages': message_list,
                }
            }
        )

    async def edit_message(self, data):
        serializer = EditMessageSerializer(data=data)

        if not await database_sync_to_async(serializer.is_valid)():
            await self.error(json.loads(json.dumps(serializer.errors)))
            return

        message_id = serializer.validated_data['message_id']
        content = serializer.validated_data['content']
        message = await database_sync_to_async(Message.objects.get)(id=message_id)

        message_channel_id = message.message_channel_id

        message.content = content
        await database_sync_to_async(message.save)()

        await self.success()

        message_serializer = await sync_to_async(MessageSerializer)(message)

        @database_sync_to_async
        def send_messages():
            for user in MessageChannel.objects.get(id=message_channel_id).users.all():
                async_to_sync(self.channel_layer.group_send)(
                    user.username,
                    {
                        'type': 'action',
                        'action': 'edit_message',
                        'content': {
                            'message': message_serializer.data
                        }
                    }
                )

        await send_messages()

    async def delete_message(self, data):
        serializer = DeleteMessageSerializer(data=data)

        if not await sync_to_async(serializer.is_valid)():
            await self.error(json.loads(json.dumps(serializer.errors)))
            return

        @database_sync_to_async
        def delete_message_from_db():
            message = Message.objects.get(id=serializer.validated_data['message_id'])
            mc = message.message_channel
            message.delete()
            return mc

        message_channel = await delete_message_from_db()

        await self.success()

        @database_sync_to_async
        def send_messages():
            for user in message_channel.users.all():
                async_to_sync(self.channel_layer.group_send)(
                    user.username,
                    {
                        'type': 'action',
                        'action': 'delete_message',
                        'content': {
                            'id': serializer.validated_data['message_id'],
                        }
                    }
                )

        await send_messages()

    async def status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'status',
            'message': event['message'],
        }))

    async def action(self, event):
        await self.send(text_data=json.dumps({
            'action': event['action'],
            'content': event['content'],
        }))

    async def success(self):
        await self.channel_layer.send(
            self.channel_name,
            {
                'type': 'status',
                'message': 'success',
            }
        )

    async def error(self, message):
        await self.channel_layer.send(
            self.channel_name,
            {
                'type': 'status',
                'message': message,
            }
        )
