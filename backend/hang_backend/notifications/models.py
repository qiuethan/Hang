from django.contrib.auth.models import User
from django.db import models


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    @classmethod
    def create_notification(cls, user, title, description):
        notification = cls(user=user, title=title, description=description)
        notification.save()
        return notification

    def set_as_read(self):
        self.read = True
        self.save()
