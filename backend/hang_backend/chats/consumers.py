import abc
import json
import sys
import traceback

import emoji
from asgiref.sync import sync_to_async, async_to_sync
from channels.db import database_sync_to_async as dbsa
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from rest_framework import exceptions
from rest_framework.exceptions import ValidationError

from .models import UserMessage, Reaction
from .serializers import AuthenticateWebsocketSerializer, MessageSerializer, UserMessageSerializer


def send_to_message_channel(action_name, message_channel, data):
    """
    Function that sends a message to all users in a MessageChannel.

    Args:
        action_name (str): Name of the action.
        message_channel (MessageChannel): The message channel.
        data (dict): The data to be sent.
    """
    # Sends the message to all users.
    for user in list(message_channel.users.all()):
        async_to_sync(get_channel_layer().group_send)(
            "chats." + user.username,
            {
                "type": "action",
                "action": action_name,
                "content": data,
            }
        )


class ChatAction(abc.ABC):
    """
    Abstract base class for chat actions.
    """
    name = None  # Name of the chat action.
    needs_authentication = False  # Whether the chat action needs authentication.

    def __init__(self, chat_consumer, data):
        """
        Initializes a ChatAction object.

        Args:
            chat_consumer (ChatConsumer): The chat consumer.
            data (dict): The data for the action.
        """
        self.chat_consumer = chat_consumer
        self.data = data

    async def run(self):
        """
        Runs the ChatAction.
        """
        try:
            # Throws an error if the ChatAction needs authentication and the user is not authenticated.
            if self.needs_authentication and not self.chat_consumer.authenticated:
                raise exceptions.PermissionDenied("User is not authenticated.")

            # Runs the ChatAction.
            await self.action()
            message = "success"
        except Exception as e:
            traceback.print_exc()
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
        """
        Abstract method representing the body code of the ChatAction.
        """
        pass

    async def reply_to_sender(self, data):
        """
        Function that sends a message to the sender of the ChatAction.

        Args:
            data (dict): The data to be sent.
        """
        await self.chat_consumer.channel_layer.send(
            self.chat_consumer.channel_name,
            {
                "type": "action",
                "action": self.name,
                "content": data,
            }
        )


# ChatAction subclasses

class AuthenticateAction(ChatAction):
    """
    ChatAction that allows a user to authenticate themselves in a MessageChannel.
    """
    name = "authenticate"
    needs_authentication = False

    async def action(self):
        """
        Performs the authentication action.
        """
        # Verifies the data.
        serializer = AuthenticateWebsocketSerializer(data=self.data, context={"user": self.chat_consumer.user})
        await sync_to_async(serializer.is_valid)(raise_exception=True)

        # Adds the user to their own MessageChannel.
        await self.chat_consumer.channel_layer.group_add(
            "chats." + self.chat_consumer.user.username,
            self.chat_consumer.channel_name
        )

        self.chat_consumer.authenticated = True


class SendMessageAction(ChatAction):
    """
    ChatAction that allows a user to send a message to a MessageChannel.
    """
    name = "send_message"
    needs_authentication = True

    async def action(self):
        """
        Sends a message to the MessageChannel.
        """
        # Verifies the message.
        serializer = UserMessageSerializer(data=self.data, context={"user": self.chat_consumer.user})
        await sync_to_async(serializer.is_valid)(raise_exception=True)

        # Saves the message.
        await dbsa(serializer.save)()


class LoadMessageAction(ChatAction):
    """
    ChatAction that allows a user to load past messages.
    """
    name = "load_message"
    needs_authentication = True

    async def action(self):
        """
        Loads past messages from the MessageChannel.
        """
        # Gets the MessageChannel by id.
        message_channel = await dbsa(self.chat_consumer.user.message_channels.get)(
            id=self.data["message_channel"])

        # If the user provides a "message_id" field, load 20 messages sent before said id.
        if "message_id" in self.data:
            messages = message_channel.messages.filter(id__lte=self.data["message_id"]).order_by("-id")
            num_messages = min(20, await dbsa(messages.count)())
            messages = await dbsa(messages.__getitem__)(slice(num_messages))

        # If the user does not provide a "message_id", load the 20 last sent messages.
        else:
            messages = message_channel.messages.order_by("-id")
            num_messages = min(20, await dbsa(messages.count)())
            messages = await dbsa(messages.__getitem__)(slice(num_messages))

        # Save and send messages.
        serializer = MessageSerializer(messages, many=True)
        await self.reply_to_sender(await dbsa(getattr)(serializer, "data"))


class EditMessageAction(ChatAction):
    """
    ChatAction that allows a user to edit their past messages.
    """
    name = "edit_message"
    needs_authentication = True

    async def action(self):
        """
        Edits a past message.
        """
        # Retrieves a message by id.
        serializer = UserMessageSerializer(await dbsa(UserMessage.objects.get)(id=self.data["id"]),
                                           data=self.data,
                                           context={"user": self.chat_consumer.user}, partial=True)
        await sync_to_async(serializer.is_valid)(raise_exception=True)

        # Re-saves the updated message.
        await dbsa(serializer.save)()


class DeleteMessageAction(ChatAction):
    """
    ChatAction that allows a user to delete a past message.
    """
    name = "delete_message"
    needs_authentication = True

    async def action(self):
        """
        Deletes a past message.
        """
        # Deletes a message.
        message = await dbsa(self.chat_consumer.user.messages.get)(id=self.data["id"])
        await dbsa(message.delete)()


class AddReactionAction(ChatAction):
    """
    ChatAction that allows a user to add a reaction to a message.
    """
    name = "add_reaction"
    needs_authentication = True

    async def action(self):
        """
        Adds a reaction to a message.
        """
        message = await dbsa(UserMessage.objects.get)(id=self.data["id"])

        # Checks if user can see message.
        message_channel_id = (await sync_to_async(getattr)(message, "message_channel")).id
        if not await dbsa(self.chat_consumer.user.message_channels.filter(id=message_channel_id).exists)():
            raise ValidationError("Message does not exist.")

        # Ensure that emoji is valid.
        if not emoji.is_emoji(self.data["emoji"]):
            raise ValidationError("Reactions must be valid emojis.")

        # Check if reaction already exists.
        if await dbsa(message.reactions.filter(user=self.chat_consumer.user, emoji=self.data["emoji"]).exists)():
            raise ValidationError("Reaction already exists.")

        # Add reaction.
        reaction = Reaction(user=self.chat_consumer.user, emoji=self.data["emoji"], message=message)
        await dbsa(reaction.save)()
        await dbsa(message.reactions.add)(reaction)


class RemoveReactionAction(ChatAction):
    """
    ChatAction that allows a user to remove their reaction from a message.
    """
    name = "remove_reaction"
    needs_authentication = True

    async def action(self):
        """
        Removes the user's reaction from a message.
        """
        message = await dbsa(UserMessage.objects.get)(id=self.data["id"])

        # Checks if user can see message.
        message_channel_id = (await sync_to_async(getattr)(message, "message_channel")).id
        if not await dbsa(self.chat_consumer.user.message_channels.filter(id=message_channel_id).exists)():
            raise ValidationError("Message does not exist.")

        # Ensure that emoji is valid.
        if not emoji.is_emoji(self.data["emoji"]):
            raise ValidationError("Reactions must be valid emojis.")

        # Check if reaction doesn't exist.
        if not await dbsa(message.reactions.filter(user=self.chat_consumer.user, emoji=self.data["emoji"]).exists)():
            raise ValidationError("Reaction doesn't exist.")

        # Delete user's reaction.
        await dbsa(message.reactions.filter(user=self.chat_consumer.user, emoji=self.data["emoji"]).delete)()


class PingAction(ChatAction):
    """
    ChatAction that allows a user to ping the websocket to prevent it from sleeping.
    """
    name = "ping"
    needs_authentication = True

    async def action(self):
        """
        Performs the ping action.
        """
        pass


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Websocket consumer for chat functionality.
    """
    # ChatActions.
    chat_actions = [AuthenticateAction, SendMessageAction, LoadMessageAction, EditMessageAction, DeleteMessageAction,
                    AddReactionAction, RemoveReactionAction, PingAction]

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.authenticated = False

    async def connect(self):
        """
        Connects the user to the WebSocket.
        """
        username = self.scope["url_route"]["kwargs"]["room_name"]
        self.user = await dbsa(User.objects.get)(username=username)
        await self.accept()

    async def disconnect(self, close_code):
        """
        Disconnects the user from the WebSocket.
        """
        await self.channel_layer.group_discard(
            "chats." + self.user.username,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        """
        Receives and processes incoming messages.
        """
        try:
            # Load the data the user sent, and run the corresponding action.
            data = json.loads(text_data)
            action = list(filter(lambda x: x.name == data["action"], self.chat_actions))[0]
            await action(self, data["content"]).run()
        except Exception as e:
            # Otherwise throw a generic error.
            traceback.print_exception(*sys.exc_info())
            await self.channel_layer.send(
                self.channel_name,
                {
                    "type": "status",
                    "message": f"Internal server error: {e}.",
                }
            )

    async def status(self, event):
        """
        Sends a status message to the WebSocket.
        """
        await self.send(text_data=json.dumps({
            "type": "status",
            "message": event["message"],
        }))

    async def action(self, event):
        """
        Sends an action message to the WebSocket.
        """
        await self.send(text_data=json.dumps({
            "action": event["action"],
            "content": event["content"],
        }))