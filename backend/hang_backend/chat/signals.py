from django.db.models.signals import post_save
from django.dispatch import receiver

from chat.models import Message, UserMessage, MessageChannelUsers, GroupChat
from hang_event.models import HangEvent
from notifications.models import Notification
from real_time_ws.utils import send_rtws_message


def get_message_prefix(content):
    if len(content) > 35:
        prefix = content[:35]
        content = prefix + "..."
    return content


@receiver(post_save)
def message_post_save(sender, instance, created, **kwargs):
    if not issubclass(sender, Message) or not created:
        return
    mcu_set = MessageChannelUsers.objects.filter(message_channel=instance.message_channel).all()
    sender = instance.user if isinstance(instance, UserMessage) else None
    for mcu in mcu_set:
        if mcu.user == sender:
            continue
        if mcu.has_read:
            if instance.message_channel.channel_type == "DM":
                Notification.create_notification(user=mcu.user,
                                                         title=instance.message_channel.users.exclude(
                                                             id=mcu.user.id).get().username,
                                                         description=get_message_prefix(instance.content))
                send_rtws_message(mcu.user, "direct_message")
            elif instance.message_channel.channel_type == "GC":
                Notification.create_notification(user=mcu.user,
                                                         title=GroupChat.objects.get(
                                                             id=instance.message_channel_id).name,
                                                         description=get_message_prefix(instance.content))
                send_rtws_message(mcu.user, "group_chat")
            else:
                Notification.create_notification(user=mcu.user,
                                                         title=HangEvent.objects.get(
                                                             message_channel_id=instance.message_channel_id).name,
                                                         description=get_message_prefix(instance.content))
                send_rtws_message(mcu.user, "hang_event")
        mcu.has_read = False
        mcu.save()
