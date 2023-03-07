from django.urls import path

from . import views

app_name = "chats"

# Register URLs.
urlpatterns = [
    path("direct_message", views.ListCreateDirectMessageView.as_view(), name="DirectMessage"),
    path("direct_message/<str:pk>", views.RetrieveDirectMessageView.as_view(), name="DirectMessage"),
    path("group_chat", views.ListCreateGroupChatView.as_view(), name="GroupChat"),
    path("group_chat/<str:pk>", views.RetrieveUpdateGroupChatView.as_view(), name="GroupChat"),
    path("read_group_chat/<str:message_channel>", views.ReadMessageChannelView.as_view(), name="ReadGroupChat"),
]
