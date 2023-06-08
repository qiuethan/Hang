"""
ICS4U
Paul Chen
This module defines the signals for the chats package.
"""

from chats.consumers import send_to_message_channel
from chats.models import UserMessage, MessageChannelUsers, GroupMessageChannel
from chats.serializers import MessageSerializer
from hang_events.models import HangEvent
from notifications.models import Notification


def get_message_prefix(content):
    """Truncate the message content to a maximum of 35 characters."""
    if len(content) > 35:
        prefix = content[:35]
        content = prefix + "..."
    return content


def message_created_notify_chat(sender, instance, created, **kwargs):
    """Send a message to the chat websocket when a new message is created."""
    if created:
        send_to_message_channel("send_message", instance.message_channel, MessageSerializer(instance).data)


def message_edited_notify_chat(sender, instance, **kwargs):
    """Send a message to the chat websocket when a message is edited."""
    if instance.pk is not None:
        orig = sender.objects.get(pk=instance.pk)
        if orig.content != instance.content:
            data = MessageSerializer(orig).data
            data["content"] = instance.content
            send_to_message_channel("edit_message", instance.message_channel, data)


def message_deleted_notify_chat(sender, instance, **kwargs):
    """Send a message to the chat websocket when a message is deleted."""
    send_to_message_channel("delete_message", instance.message_channel, {"id": instance.id})


def message_reaction_added_notify_chat(sender, instance, created, **kwargs):
    """Send a message to the chat websocket when a reaction is added to a message."""
    if created:
        send_to_message_channel("add_reaction",
                                instance.message.message_channel,
                                MessageSerializer(instance.message).data)


def message_reaction_removed_notify_chat(sender, instance, **kwargs):
    """Send a message to the chat websocket when a reaction is removed from a message."""
    send_to_message_channel("remove_reaction",
                            instance.message.message_channel,
                            MessageSerializer(instance.message).data)


def message_saved_create_notifications(sender, instance, created, **kwargs):
    """Create a notification when a message is saved."""
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
