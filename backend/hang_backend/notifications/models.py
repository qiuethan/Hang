"""
ICS4U
Paul Chen
This module defines the models for the notifications package.
"""

from django.contrib.auth.models import User
from django.db import models
from real_time_ws.models import RTWSSendMessageOnUpdate


class Notification(models.Model, RTWSSendMessageOnUpdate):
    """
    Model that represents notifications for a given user, telling them about recent actions.

    Attributes:
      user (ForeignKey): The user to whom the notification belongs.
      title (CharField): The title of the notification.
      description (TextField): The full description of the notification.
      timestamp (DateTimeField): The time when the notification was created.
      read (BooleanField): The flag indicating if the notification has been read.
    """

    # Fields of the Notification model
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    # Content of real time websocket message
    rtws_message_content = "notification"

    def get_rtws_users(self):
        return [self.user]

    @classmethod
    def create_notification(cls, user, title, description):
        """
        Creates a new Notification instance and saves it to the database.

        Arguments:
          user (User): The user to whom the notification will belong.
          title (str): The title of the notification.
          description (str): The full description of the notification.

        Returns:
          Notification: The newly created Notification instance.
        """
        notification = cls(user=user, title=title, description=description)
        notification.save()
        return notification

    def set_as_read(self):
        """Marks the current notification as read."""
        self.read = True
        self.save()
