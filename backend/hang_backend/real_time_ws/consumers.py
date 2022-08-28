import json

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from django.contrib.auth.models import User

from chat.serializers import AuthenticateWebsocketSerializer


def send_message(user, action, content):
    channel_layer = get_channel_layer()
    channel_layer.group_send(
        user.username,
        {
            "type": "action",
            "action": action,
            "content": content,
        }
    )


class RealTimeWSConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.authenticated = False

    async def connect(self):
        username = self.scope["url_route"]["kwargs"]["room_name"]
        self.user = await database_sync_to_async(User.objects.get)(username=username)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user.username,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        if not self.authenticated:
            serializer = AuthenticateWebsocketSerializer(data=text_data, context={"user": self.user})
            await sync_to_async(serializer.is_valid)(raise_exception=True)

            await self.channel_layer.group_add(
                self.user.username,
                self.channel_name
            )

            self.authenticated = True

    async def action(self, event):
        await self.send(text_data=json.dumps({
            "action": event["action"],
            "content": event["content"],
        }))
