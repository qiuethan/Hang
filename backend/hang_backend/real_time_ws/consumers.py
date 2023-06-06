"""
ICS4U
Paul Chen
This module defines the RealTimeWSConsumer, a WebSocket consumer for real-time updates.
"""

import json

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError

from chats.serializers import AuthenticateWebsocketSerializer


class RealTimeWSConsumer(AsyncWebsocketConsumer):
    """
    Handles WebSocket connections for real-time updates.

    Attributes:
      user (User): The user connected to the WebSocket.
      authenticated (bool): Whether the WebSocket connection is authenticated.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.authenticated = False

    async def connect(self):
        """
        Handles new WebSocket connections. Retrieves the associated user.
        """
        username = self.scope["url_route"]["kwargs"]["room_name"]
        self.user = await database_sync_to_async(User.objects.get)(username=username)
        await self.accept()

    async def disconnect(self, close_code):
        """
        Handles disconnection of WebSocket. Removes the user from the corresponding channel layer group.

        Arguments:
          close_code (int): The WebSocket closing code.
        """
        await self.channel_layer.group_discard(
            "real_time_ws." + self.user.username,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        """
        Handles incoming WebSocket messages.

        Arguments:
          text_data (str): The text data of the WebSocket message.
          bytes_data (bytes): The binary data of the WebSocket message, unused here.
        """
        data = json.loads(text_data)
        try:
            if not self.authenticated:
                # Authenticate the websocket connection
                serializer = AuthenticateWebsocketSerializer(data=data["content"], context={"user": self.user})
                await sync_to_async(serializer.is_valid)(raise_exception=True)

                # Add the authenticated websocket to the user's group
                await self.channel_layer.group_add(
                    "real_time_ws." + self.user.username,
                    self.channel_name
                )

                self.authenticated = True

                # Send success status
                await self.channel_layer.send(
                    self.channel_name,
                    {
                        "type": "status",
                        "message": "success",
                    }
                )
            else:
                # For already authenticated connections, send success status
                await self.channel_layer.send(
                    self.channel_name,
                    {
                        "type": "status",
                        "message": "success",
                    }
                )
        except ValidationError:
            # Ignore validation errors
            pass

    async def status(self, event):
        """
        Handles 'status' type events.

        Arguments:
          event (dict): The event dictionary.
        """
        await self.send(text_data=json.dumps({
            "type": "status",
            "message": event["message"],
        }))

    async def update(self, event):
        """
        Handles 'update' type events.

        Arguments:
          event (dict): The event dictionary.
        """
        await self.send(text_data=json.dumps({
            "type": "update",
            "content": event["content"],
        }))
