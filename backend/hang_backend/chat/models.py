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
    users = models.ManyToManyField(User, related_name="message_channels", through="MessageChannelUsers")
    created_at = models.DateTimeField(auto_now_add=True)
    message_last_sent = models.DateTimeField(auto_now_add=True)

    objects = MessageChannelManager()


class MessageChannelUsers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message_channel = models.ForeignKey(MessageChannel, on_delete=models.CASCADE)
    has_read = models.BooleanField(default=True)


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
    """Model that represents a message."""
    type = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    message_channel = models.ForeignKey(MessageChannel, on_delete=models.CASCADE, related_name="messages")


class UserMessage(Message):
    """Model that represents a user-sent message."""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="messages", null=True)
    reply = models.ForeignKey("self", on_delete=models.SET_NULL, related_name="replies", null=True)
    content = models.CharField(max_length=2000)


class SystemMessage(Message):
    """Model that represents a system-sent message."""
    pass


class GroupChatNameChangedMessage(SystemMessage):
    """Model that represents a system-sent message about the change in a GroupChat's name."""
    new_name = models.CharField(max_length=50)


class GroupChatUserAddedMessage(SystemMessage):
    """Model that represents a system-sent message about the addition of a user to a GroupChat."""
    adder = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="gc_user_added_msg_adder", null=True)
    user_added = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="gc_user_added_msg_user_added",
                                   null=True)


class GroupChatUserRemovedMessage(SystemMessage):
    """Model that represents a system-sent message about the removal of a user to a GroupChat."""
    remover = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="gc_user_removed_msg_remover", null=True)
    user_removed = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="gc_user_removed_msg_user_removed",
                                     null=True)


class Reaction(models.Model):
    message = models.ForeignKey(UserMessage, on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    emoji = models.CharField(max_length=2)
