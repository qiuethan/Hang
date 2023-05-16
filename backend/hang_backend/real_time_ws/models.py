import threading
import time
from collections import defaultdict

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class RTWSSendMessageOnUpdate:
    _lock = threading.Lock()
    _need_send = defaultdict(lambda: defaultdict(lambda: False))  # Dictionary to store the last sent time for each user
    _sending = defaultdict(lambda: defaultdict(lambda: False))
    _delay = 1

    def get_rtws_users(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def send_rtws_message(self):
        for user in self.get_rtws_users():
            with self._lock:
                self._need_send[user.username][self.rtws_message_content] = True
                if not self._sending[user.username][self.rtws_message_content]:
                    threading.Thread(target=self._send_message_with_delay, args=(user,)).start()

    def _send_message_with_delay(self, user):
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
            time.sleep(self._delay)  # Wait for 2 seconds
        self._sending[user.username][self.rtws_message_content] = False
