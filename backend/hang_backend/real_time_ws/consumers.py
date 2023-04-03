import json

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError

from chat.serializers import AuthenticateWebsocketSerializer


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
            "real_time_ws." + self.user.username,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        try:
            if not self.authenticated:
                serializer = AuthenticateWebsocketSerializer(data=data["content"], context={"user": self.user})
                await sync_to_async(serializer.is_valid)(raise_exception=True)

                await self.channel_layer.group_add(
                    "real_time_ws." + self.user.username,
                    self.channel_name
                )

                self.authenticated = True

                await self.channel_layer.send(
                    self.channel_name,
                    {
                        "type": "status",
                        "message": "success",
                    }
                )
            else:
                await self.channel_layer.send(
                    self.channel_name,
                    {
                        "type": "status",
                        "message": "success",
                    }
                )
        except ValidationError:
            pass

    async def status(self, event):
        await self.send(text_data=json.dumps({
            "type": "status",
            "message": event["message"],
        }))

    async def update(self, event):
        await self.send(text_data=json.dumps({
            "type": "update",
            "content": event["content"],
        }))
