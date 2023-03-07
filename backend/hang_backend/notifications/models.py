from django.contrib.auth.models import User
from django.db import models

from real_time_ws.utils import send_rtws_message


class NotificationManager(models.Manager):
    def create_notification(self, user, title, description):
        notification = Notification.objects.create(user=user, title=title, description=description)
        notification.save()
        send_rtws_message(user, "notification")
        return notification


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    objects = NotificationManager()
