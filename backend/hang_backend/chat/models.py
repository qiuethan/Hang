from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class MessageChannel(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    users = models.ManyToManyField(User)
    channel_type = models.IntegerField()  # 0: dm

class Message(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = models.CharField(max_length=2000)
    message_channel = models.ForeignKey(
        MessageChannel, on_delete=models.CASCADE)

# add get channel list
# message id, editing, deleting
# group chats
# friend requests 