import abc
import json

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async as dbsa
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User

from .exceptions import ChatActionError
from .models import Message, MessageChannel
from .serializers import AuthenticateWebsocketSerializer, MessageSerializer


class ChatAction(abc.ABC):
    """
    Generic action for chat websocket.
    """
    name = None  # Name of websocket.
    needs_authentication = False  # Whether the websocket needs authentication.

    def __init__(self, chat_consumer, data):
        self.chat_consumer = chat_consumer
        self.data = data

    async def run(self):
        """
        Runs the ChatAction.
        """
        try:
            # Throws an error if the ChatAction needs authentication and the user is not authenticated.
            if self.needs_authentication and not self.chat_consumer.authenticated:
                raise ChatActionError("User is not authenticated.")

            # Runs the ChatAction.
            await self.action()
            message = "success"
        except ChatActionError as e:
            # If the ChatAction is invalid, change message to the error.
            message = str(e)

        # Send status message to user.
        await self.chat_consumer.channel_layer.send(
            self.chat_consumer.channel_name,
            {
                "type": "status",
                "message": message,
            }
        )

    @abc.abstractmethod
    async def action(self):
        """Body code of the ChatAction."""
        pass

    async def reply_to_sender(self, data):
        """Function that sends a message to the sender of the ChatAction."""
        await self.chat_consumer.channel_layer.send(
            self.chat_consumer.channel_name,
            {
                "type": "action",
                "action": self.name,
                "content": data,
            }
        )

    async def send_to_message_channel(self, message_channel_id, data):
        """Function that sends a message to all users in a MessageChannel."""
        # Verifies that the MessageChannel exists.
        if not await dbsa((await dbsa(MessageChannel.objects.filter)(
                id=message_channel_id, users=self.chat_consumer.user)).exists)():
            raise ChatActionError("Message channel does not exist.")

        # Sends the message to all users.
        message_channel = await dbsa(MessageChannel.objects.get)(id=message_channel_id)
        users = await dbsa(message_channel.users.all)()
        users_list = await sync_to_async(list)(users)
        for user in users_list:
            await self.chat_consumer.channel_layer.group_send(
                "chat." + user.username,
                {
                    "type": "action",
                    "action": self.name,
                    "content": data,
                }
            )


class AuthenticateAction(ChatAction):
    """ChatAction that allows a user to authenticate themselves in a MessageChannel."""
    name = "authenticate"
    needs_authentication = False

    async def action(self):
        # Verifies the data.
        serializer = AuthenticateWebsocketSerializer(data=self.data, context={"user": self.chat_consumer.user})
        await sync_to_async(serializer.is_valid)(raise_exception=True)

        # Adds the user to their own MessageChannel.
        await self.chat_consumer.channel_layer.group_add(
            "chat." + self.chat_consumer.user.username,
            self.chat_consumer.channel_name
        )

        self.chat_consumer.authenticated = True


class SendMessageAction(ChatAction):
    """ChatAction that allows a user to send a message to a MessageChannel."""
    name = "send_message"
    needs_authentication = True

    async def action(self):
        # Verifies the message.
        serializer = MessageSerializer(data=self.data, context={"user": self.chat_consumer.user})
        await sync_to_async(serializer.is_valid)(raise_exception=True)

        # Saves the message.
        message = await dbsa(serializer.save)()

        # Sends the message to all users in the MessageChannel.
        await self.send_to_message_channel(message_channel_id=message.message_channel.id, data=serializer.data)


class LoadMessageAction(ChatAction):
    """ChatAction that allows a user to load past messages."""
    name = "load_message"
    needs_authentication = True

    async def action(self):
        # Gets the MessageChannel by id.
        message_channel = await dbsa(self.chat_consumer.user.message_channels.get)(
            id=self.data["message_channel"])

        # If the user provides a "message_id" field, load 20 messages sent before said id.
        if "message_id" in self.data:
            messages = message_channel.messages.filter(id__lte=self.data["message_id"]).order_by("-id")
            num_messages = min(20, await dbsa(messages.count)())
            messages = await dbsa(messages.__getitem__)(slice(num_messages))

        # If the user does not, load the 20 last sent messages.
        else:
            messages = message_channel.messages.order_by("-id")
            num_messages = min(20, await dbsa(messages.count)())
            messages = await dbsa(messages.__getitem__)(slice(num_messages))

        # Save and send messages.
        serializer = MessageSerializer(messages, many=True)
        await self.reply_to_sender(await dbsa(getattr)(serializer, "data"))


class EditMessageAction(ChatAction):
    """ChatAction that allows a user to edit their past messages."""
    name = "edit_message"
    needs_authentication = True

    async def action(self):
        # Retrieves a message by id.
        serializer = MessageSerializer(await dbsa(Message.objects.get)(id=self.data["id"]),
                                       data=self.data,
                                       context={"user": self.chat_consumer.user}, partial=True)
        await sync_to_async(serializer.is_valid)(raise_exception=True)

        # Re-saves the updated message.
        message = await dbsa(serializer.save)()

        # Sends a message to all users in the MessageChannel.
        await self.send_to_message_channel(
            message_channel_id=(await sync_to_async(getattr)(message, "message_channel")).id,
            data=await sync_to_async(getattr)(serializer, "data"))


class DeleteMessageAction(ChatAction):
    """ChatAction that allows a user to delete a past message."""
    name = "delete_message"
    needs_authentication = True

    async def action(self):
        # Deletes a message.
        message = await dbsa(self.chat_consumer.user.messages.get)(id=self.data["id"])
        await self.send_to_message_channel(
            message_channel_id=(await sync_to_async(getattr)(message, "message_channel")).id,
            data={"id": self.data["id"]})
        await dbsa(message.delete)()


class ChatConsumer(AsyncWebsocketConsumer):
    """Websocket for Chat."""
    # ChatActions.
    chat_actions = [AuthenticateAction, SendMessageAction, LoadMessageAction, EditMessageAction, DeleteMessageAction]

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.authenticated = False

    async def connect(self):
        """Connects user to WS."""
        username = self.scope["url_route"]["kwargs"]["room_name"]
        self.user = await dbsa(User.objects.get)(username=username)
        await self.accept()

    async def disconnect(self, close_code):
        """Disconnects user from WS."""
        await self.channel_layer.group_discard(
            "chat." + self.user.username,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        """Runs everytime a message is received."""
        try:
            # Load the data the user sent, and run the corresponding action.
            data = json.loads(text_data)
            action = list(filter(lambda x: x.name == data["action"], self.chat_actions))[0]
            await action(self, data["content"]).run()
        except (Exception,) as e:
            # Otherwise throw a generic error.
            # traceback.print_exception(*sys.exc_info())
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
