from django.urls import path

from notifications.views import RetrieveUpdateNotificationView, ListReadNotificationView, ListUnreadNotificationView

app_name = "notifications"

urlpatterns = [
    path("notifications/unread", ListUnreadNotificationView.as_view()),
    path("notifications/read", ListReadNotificationView.as_view()),
    path("notifications/<int:pk>", RetrieveUpdateNotificationView.as_view()),
]
