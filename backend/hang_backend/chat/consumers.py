import abc
import json
import sys
import traceback

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User

from .exceptions import ChatActionError
from .models import Message, MessageChannel
from .serializers import AuthenticateWebsocketSerializer, MessageSerializer


class ChatAction(abc.ABC):
    name = None
    needs_authentication = False

    def __init__(self, chat_consumer, data):
        self.chat_consumer = chat_consumer
        self.data = data

    async def run(self):
        try:
            if self.needs_authentication and not self.chat_consumer.authenticated:
                raise ChatActionError("User is not authenticated.")
            result = await self.action()
            message = "success" if result is None else result
        except ChatActionError as e:
            message = str(e)
        await self.chat_consumer.channel_layer.send(
            self.chat_consumer.channel_name,
            {
                "type": "status",
                "message": message,
            }
        )

    @abc.abstractmethod
    async def action(self):
        pass

    async def send_to_message_channel(self, message_channel_id, data):
        if not await database_sync_to_async((await database_sync_to_async(MessageChannel.objects.filter)(
                id=message_channel_id, users=self.chat_consumer.user)).exists)():
            raise ChatActionError("Message channel does not exist.")
        message_channel = await database_sync_to_async(MessageChannel.objects.get)(id=message_channel_id)
        users = await database_sync_to_async(message_channel.users.all)()
        users_list = await sync_to_async(list)(users)
        for user in users_list:
            await self.chat_consumer.channel_layer.group_send(
                user.username,
                {
                    "type": "action",
                    "action": self.name,
                    "content": data,
                }
            )


class AuthenticateAction(ChatAction):
    name = "authenticate"
    needs_authentication = False

    async def action(self):
        serializer = AuthenticateWebsocketSerializer(data=self.data, context={"user": self.chat_consumer.user})
        await sync_to_async(serializer.is_valid)(raise_exception=True)

        await self.chat_consumer.channel_layer.group_add(
            self.chat_consumer.user.username,
            self.chat_consumer.channel_name
        )

        self.chat_consumer.authenticated = True


class SendMessageAction(ChatAction):
    name = "send_message"
    needs_authentication = True

    async def action(self):
        serializer = MessageSerializer(data=self.data, context={"user": self.chat_consumer.user})
        await sync_to_async(serializer.is_valid)(raise_exception=True)
        message = await database_sync_to_async(serializer.save)()

        await self.send_to_message_channel(message_channel_id=message.message_channel.id, data=serializer.data)


class LoadMessageAction(ChatAction):
    name = "load_message"
    needs_authentication = True

    async def action(self):
        message_channel = await database_sync_to_async(self.chat_consumer.user.message_channels.get)(
            id=self.data["message_channel_id"])
        if "message_id" in self.data:
            messages = message_channel.messages.filter(id__lte=self.data["message_id"]).order_by("-id")
            num_messages = min(20, await database_sync_to_async(messages.count)())
            messages = await database_sync_to_async(messages.__getitem__)(slice(num_messages))
        else:
            messages = message_channel.messages.order_by("-id")
            num_messages = min(20, await database_sync_to_async(messages.count)())
            messages = await database_sync_to_async(messages.__getitem__)(slice(num_messages))
        serializer = MessageSerializer(messages, many=True)
        return await database_sync_to_async(getattr)(serializer, "data")


class EditMessageAction(ChatAction):
    name = "edit_message"
    needs_authentication = True

    async def action(self):
        serializer = MessageSerializer(await database_sync_to_async(Message.objects.get)(id=self.data["id"]),
                                       data=self.data,
                                       context={"user": self.chat_consumer.user}, partial=True)
        await sync_to_async(serializer.is_valid)(raise_exception=True)
        message = await database_sync_to_async(serializer.save)()
        await self.send_to_message_channel(
            message_channel_id=(await sync_to_async(getattr)(message, "message_channel")).id,
            data=await sync_to_async(getattr)(serializer, "data"))


class DeleteMessageAction(ChatAction):
    name = "delete_message"
    needs_authentication = True

    async def action(self):
        message = await database_sync_to_async(self.chat_consumer.user.messages.get)(id=self.data["id"])
        await self.send_to_message_channel(
            message_channel_id=(await sync_to_async(getattr)(message, "message_channel")).id,
            data={"id": self.data["id"]})
        await database_sync_to_async(message.delete)()


class ChatConsumer(AsyncWebsocketConsumer):
    chat_actions = [AuthenticateAction, SendMessageAction, LoadMessageAction, EditMessageAction, DeleteMessageAction]

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
        try:
            data = json.loads(text_data)
            action = list(filter(lambda x: x.name == data["action"], self.chat_actions))[0]
            await action(self, data["content"]).run()
        except (json.JSONDecodeError, KeyError, IndexError):
            traceback.print_exception(*sys.exc_info())
            await self.channel_layer.send(
                self.channel_name,
                {
                    "type": "status",
                    "message": "Invalid json",
                }
            )
        except (Exception,) as e:
            traceback.print_exception(*sys.exc_info())
            await self.channel_layer.send(
                self.channel_name,
                {
                    "type": "status",
                    "message": f"Internal server error: {e}.",
                }
            )

    async def status(self, event):
        await self.send(text_data=json.dumps({
            "type": "status",
            "message": event["message"],
        }))

    async def action(self, event):
        await self.send(text_data=json.dumps({
            "action": event["action"],
            "content": event["content"],
        }))
