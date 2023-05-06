"""
ASGI config for hang_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

import chats.routing
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import real_time_ws.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hang_backend.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket":
        URLRouter(
            chats.routing.websocket_urlpatterns + real_time_ws.routing.websocket_urlpatterns
        ),
})
