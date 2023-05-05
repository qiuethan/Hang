from django.urls import path
from rest_framework.routers import DefaultRouter

from chat.views import ReadMessageChannelView, \
    DirectMessageViewSet, GroupChatViewSet

app_name = "chats"

router = DefaultRouter()
router.register(r'direct_message', DirectMessageViewSet, basename='direct_message')
router.register(r'group_chat', GroupChatViewSet, basename='group_chat')

# Register URLs.
urlpatterns = [
    path("message_channel/<str:pk>/read/", ReadMessageChannelView.as_view(), name="ReadMessageChannel"),
]

urlpatterns += router.urls
