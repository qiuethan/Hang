# chat/consumers.py
import time
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from chat.models import MessageChannel, Message


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']

        try:
            self.m = MessageChannel.objects.get(id=self.room_name)
        except MessageChannel.DoesNotExist:
            self.close(404)
        except MessageChannel.MultipleObjectsReturned:
            self.close(500)

        if self.scope['user'].is_anonymous or not self.m.users.filter(id=self.scope['user'].id).exists():
            self.close(403)
        #print(self.m.users.all() == self.request.user)

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)

        # if text_data_json['type'] == 'send':
        message = text_data_json['message']
        msg_obj = Message(content=message, message_channel=self.m)
        msg_obj.save()
        msg_time = int(time.mktime(msg_obj.created_at.timetuple()))
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_name,
            {
                'type': 'chat_message',
                'message': message,
                'time': msg_time,
            }
        )
        # elif text_data_json['type'] == 'load':
        #     before = text_data_json['before']

        #     req_time = timezone.make_aware(datetime.fromtimestamp(int(before)))

        #     messages = self.m.message_set.all().filter(
        #         created_at__lte=str(req_time)).order_by('-created_at')

        #     msg_list = []

        #     for e in messages[:min(20, len(messages))]:
        #         msg_list.append({'message': e.content, 'time': int(
        #             time.mktime(e.created_at.timetuple()))})

        #     print(msg_list)

    # Receive message from room group

    def chat_message(self, event):
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'user': self.scope['user'].username,
            'message': event['message'],
            'time': event['time'],
        }))
