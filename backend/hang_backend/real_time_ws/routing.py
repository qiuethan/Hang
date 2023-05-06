# chats/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/real_time_ws/(?P<room_name>\w+)/$", consumers.RealTimeWSConsumer.as_asgi()),
]
