import threading
import time
from collections import defaultdict

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class RTWSSendMessageOnUpdate:
    _lock = threading.Lock()
    _next_send = defaultdict(dict)  # Dictionary to store the last sent time for each user
    _delay = 2

    def get_rtws_users(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def send_rtws_message(self):
        for user in self.get_rtws_users():
            with self._lock:
                # Check if a message has been sent recently
                curr_user = self._next_send.get(user.username)
                if curr_user is not None:
                    next_send = curr_user.get(self.rtws_message_content)
                    now = time.time()
                    if next_send is not None and now < next_send:
                        continue  # Skip sending the message

                # Update the last sent time for the user
                self._next_send[user.username][self.rtws_message_content] = time.time() + self._delay

                # Schedule the message to be sent after the specified delay
                threading.Thread(target=self._send_message_with_delay, args=(user,)).start()

    def _send_message_with_delay(self, user):
        time.sleep(self._delay)  # Wait for 2 seconds
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


