"""
ICS4U
Paul Chen
This module defines the urls for the chats package.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

from chats.views import ReadMessageChannelView, \
    DirectMessageChannelViewSet, GroupMessageChannelViewSet

app_name = "chats"

router = DefaultRouter()
router.register(r'direct_messages', DirectMessageChannelViewSet, basename='direct_messages')
router.register(r'group_chats', GroupMessageChannelViewSet, basename='group_chats')

# Register URLs.
urlpatterns = [
    path("message_channels/<str:pk>/read/", ReadMessageChannelView.as_view(), name="ReadMessageChannel"),
]

urlpatterns += router.urls
