from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def send_rtws_message(user, content):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "real_time_ws." + user.username,
        {
            "type": "update",
            "content": content,
        }
    )


def update_db_send_rtws_message(mixin, *serializers, current_user=None, request_type=None):
    users = set()
    if current_user is not None:
        users.add(current_user)
    for s in serializers:
        user_set = mixin.get_rtws_users(s.data)
        for user in user_set:
            users.add(user)
    for user in users:
        for update_action in mixin.rtws_update_actions:
            send_rtws_message(user, update_action)
