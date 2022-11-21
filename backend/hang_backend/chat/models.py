import random
import string

from django.contrib.auth.models import User
from django.core import exceptions
from django.db import models


class MessageChannelManager(models.Manager):
    """Manager for MessageChannels that allows for the creation of DirectMessages and GroupChats."""

    def create_direct_message(self, user1, user2):
        direct_message = DirectMessage(id=generate_message_channel_id(), channel_type="DM")
        direct_message.save()

        direct_message.users.add(user1)
        direct_message.users.add(user2)
        return direct_message

    def create_group_chat(self, name, owner, users):
        group_chat = GroupChat(id=generate_message_channel_id(), name=name, owner=owner,
                               channel_type="GC")
        group_chat.save()

        group_chat.users.add(owner)
        group_chat.users.add(*users)
        return group_chat


class MessageChannel(models.Model):
    """Model that represents a MessageChannel."""
    id = models.CharField(max_length=10, primary_key=True)
    channel_type = models.CharField(max_length=2, choices=(("DM", "Direct Message"), ("GC", "Group Chat")))
    users = models.ManyToManyField(User, related_name="message_channels")
    created_at = models.DateTimeField(auto_now_add=True)
    message_last_sent = models.DateTimeField(auto_now_add=True)

    objects = MessageChannelManager()


class DirectMessage(MessageChannel):
    """Model that represents a DM."""

    def clean(self):
        if self.users.count() != 2:
            raise exceptions.ValidationError("A DM can only contain two users.")


class GroupChat(MessageChannel):
    """Model that represents a GC."""
    name = models.CharField(max_length=75)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name="message_channels_owned", null=True)


def generate_random_string():
    """Utility method to generate a random string."""
    return "".join([random.choice(string.ascii_letters) for _ in range(10)])


def generate_message_channel_id():
    """Utility method to generate a random id for a MessageChannel."""
    message_channel_id = generate_random_string()
    while MessageChannel.objects.filter(id=message_channel_id).exists():
        message_channel_id = generate_random_string()
    return message_channel_id


class Message(models.Model):
    """Model that represents a Message."""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="messages", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = models.CharField(max_length=2000)
    message_channel = models.ForeignKey(MessageChannel, on_delete=models.CASCADE, related_name="messages")
    reply = models.ForeignKey("self", on_delete=models.SET_NULL, related_name="replies", null=True)


class Reaction(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    emoji = models.CharField(max_length=2)
