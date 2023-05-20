from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver

from chats.consumers import send_to_message_channel
from chats.models import Message, UserMessage, MessageChannelUsers, GroupMessageChannel, Reaction
from chats.serializers import UserMessageSerializer, MessageSerializer
from hang_events.models import HangEvent
from notifications.models import Notification


def get_message_prefix(content):
    if len(content) > 35:
        prefix = content[:35]
        content = prefix + "..."
    return content


def message_created_notify_chat(sender, instance, created, **kwargs):
    if created:
        send_to_message_channel("send_message", instance.message_channel, MessageSerializer(instance).data)


def message_edited_notify_chat(sender, instance, **kwargs):
    if instance.pk is not None:
        orig = sender.objects.get(pk=instance.pk)
        if orig.content != instance.content:
            data = MessageSerializer(orig).data
            data["content"] = instance.content
            send_to_message_channel("edit_message", instance.message_channel, data)


def message_deleted_notify_chat(sender, instance, **kwargs):
    send_to_message_channel("delete_message", instance.message_channel, {"id": instance.id})


def message_reacted_added_notify_chat(sender, instance, created, **kwargs):
    if created:
        send_to_message_channel("add_reaction",
                                instance.message.message_channel,
                                MessageSerializer(instance.message).data)


def message_reaction_removed_notify_chat(sender, instance, **kwargs):
    send_to_message_channel("remove_reaction",
                            instance.message.message_channel,
                            MessageSerializer(instance.message).data)


def message_saved_create_notifications(sender, instance, created, **kwargs):
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
            elif instance.message_channel.channel_type == "GC":
                Notification.create_notification(user=mcu.user,
                                                 title=GroupMessageChannel.objects.get(
                                                     id=instance.message_channel_id).name,
                                                 description=get_message_prefix(instance.content))
            else:
                Notification.create_notification(user=mcu.user,
                                                 title=HangEvent.objects.get(
                                                     message_channel_id=instance.message_channel_id).name,
                                                 description=get_message_prefix(instance.content))
        mcu.has_read = False
        mcu.save()
