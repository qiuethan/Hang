from django.contrib.auth.models import User
from django.core import exceptions
from django.db import models


class MessageChannel(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    channel_type = models.CharField(max_length=2, choices=(("DM", "Direct Message"), ("GC", "Group Chat")))
    users = models.ManyToManyField(User, related_name="message_channels")
    created_at = models.DateTimeField(auto_now_add=True)


class DirectMessage(MessageChannel):
    def clean(self):
        if self.users.count() != 2:
            raise exceptions.ValidationError("A DM can only contain two users.")


class GroupChat(MessageChannel):
    name = models.CharField(max_length=75)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name="message_channels_owned")


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="messages")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = models.CharField(max_length=2000)
    message_channel = models.ForeignKey(MessageChannel, on_delete=models.CASCADE, related_name="messages")
