from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class MessageChannel(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    users = models.ManyToManyField(User)
    channel_type = models.IntegerField()  # 0: dm


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = models.CharField(max_length=2000)
    message_channel = models.ForeignKey(
        MessageChannel, on_delete=models.CASCADE)

# Email verif
# group chats
# friend requests
