"""
ICS4U
Paul Chen
This module defines the RTWSSendMessageOnUpdate mixin for sending real-time WebSocket messages on updates.
"""

import threading
import time
from collections import defaultdict

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class RTWSSendMessageOnUpdate:
    """
    Mixin to send WebSocket messages to users upon updates.

    Attributes:
      _lock (Lock): A threading lock for controlling access to shared data.
      _need_send (defaultdict): A dictionary storing whether each user needs to be sent a message.
      _sending (defaultdict): A dictionary storing whether a message is currently being sent to each user.
      _delay (int): The delay between subsequent messages in seconds.
    """

    _lock = threading.Lock()
    _need_send = defaultdict(lambda: defaultdict(lambda: False))  # Dictionary to store whether a user needs to be sent a message
    _sending = defaultdict(lambda: defaultdict(lambda: False))  # Dictionary to store whether a message is being sent to a user
    _delay = 1

    def get_rtws_users(self):
        """
        Method to get the users to send real-time WebSocket messages to.
        Subclasses need to implement this method.

        Raises:
          NotImplementedError: If this method is not overridden in a subclass.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def send_rtws_message(self):
        """
        Initiates sending of real-time WebSocket messages to users.
        """
        for user in self.get_rtws_users():
            with self._lock:
                self._need_send[user.username][self.rtws_message_content] = True
                if not self._sending[user.username][self.rtws_message_content]:
                    threading.Thread(target=self._send_message_with_delay, args=(user,)).start()

    def _send_message_with_delay(self, user):
        """
        Sends a real-time WebSocket message to a user with a delay.

        Arguments:
          user (User): The user to send the message to.
        """
        self._sending[user.username][self.rtws_message_content] = True
        while self._need_send[user.username][self.rtws_message_content]:
            self._need_send[user.username][self.rtws_message_content] = False
            with self._lock:
                # Send the message
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "real_time_ws." + user.username,
                    {
                        "type": "update",
                        "content": self.rtws_message_content,
                    }
                )
            time.sleep(self._delay)  # Wait for the specified delay
        self._sending[user.username][self.rtws_message_content] = False
