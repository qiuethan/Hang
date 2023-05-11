from django.contrib.auth.models import User
from django.db import models

from real_time_ws.models import RTWSSendMessageOnUpdate


class Notification(models.Model, RTWSSendMessageOnUpdate):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    rtws_message_content = "notification"

    def get_rtws_users(self):
        return [self.user]

    @classmethod
    def create_notification(cls, user, title, description):
        notification = cls(user=user, title=title, description=description)
        notification.save()
        return notification

    def set_as_read(self):
        self.read = True
        self.save()
