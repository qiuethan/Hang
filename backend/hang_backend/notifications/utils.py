from notifications.models import Notification


def update_db_send_notification(mixin, *serializers, current_user, request_type):
    notifications = mixin.get_notification_messages(*serializers, current_user=current_user, request_type=request_type)
    for data in notifications:
        Notification.create_notification(user=data["user"], title=data["title"],
                                                 description=data["description"])
