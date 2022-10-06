from django.contrib.auth.models import User
from django.core import exceptions
from django.db import models


class MessageChannel(models.Model):
    """Model that represents a MessageChannel."""
    id = models.CharField(max_length=10, primary_key=True)
    channel_type = models.CharField(max_length=2, choices=(("DM", "Direct Message"), ("GC", "Group Chat")))
    users = models.ManyToManyField(User, related_name="message_channels")
    created_at = models.DateTimeField(auto_now_add=True)
    message_last_sent = models.DateTimeField(auto_now_add=True)


class DirectMessage(MessageChannel):
    """Model that represents a DM."""
    def clean(self):
        if self.users.count() != 2:
            raise exceptions.ValidationError("A DM can only contain two users.")


class GroupChat(MessageChannel):
    """Model that represents a GC."""
    name = models.CharField(max_length=75)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name="message_channels_owned")


class Message(models.Model):
    """Model that represents a Message."""
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="messages")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = models.CharField(max_length=2000)
    message_channel = models.ForeignKey(MessageChannel, on_delete=models.CASCADE, related_name="messages")
