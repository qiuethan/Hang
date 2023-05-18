import random
import string

from django.contrib.auth.models import User
from django.core import exceptions
from django.db import models

from real_time_ws.models import RTWSSendMessageOnUpdate


class MessageChannelManager(models.Manager):
    """Manager for MessageChannels that allows for the creation of DirectMessages and GroupChats."""

    def create_direct_message(self, user1, user2):
        direct_message = DirectMessageChannel(id=MessageChannelManager.generate_unique_message_channel_id(),
                                              channel_type="DM")
        direct_message.save()

        direct_message.users.add(user1)
        direct_message.users.add(user2)
        return direct_message

    def create_group_chat(self, name, owner, users):
        group_chat = GroupMessageChannel(id=MessageChannelManager.generate_unique_message_channel_id(),
                                         name=name,
                                         owner=owner,
                                         channel_type="GC")
        group_chat.save()

        group_chat.users.add(owner)
        group_chat.users.add(*users)
        return group_chat

    def create_hang_event_message_channel(self, hang_event):
        hang_event_message_channel = HangEventMessageChannel(
            id=MessageChannelManager.generate_unique_message_channel_id(),
            channel_type="HE")
        hang_event_message_channel.save()

        hang_event_message_channel.users.set(hang_event.attendees.all())
        return hang_event_message_channel

    @staticmethod
    def generate_random_string():
        """Utility method to generate a random string."""
        return "".join([random.choice(string.ascii_letters) for _ in range(10)])

    @staticmethod
    def generate_unique_message_channel_id():
        """Utility method to generate a random id for a MessageChannel."""
        message_channel_id = MessageChannelManager.generate_random_string()
        while MessageChannel.objects.filter(id=message_channel_id).exists():
            message_channel_id = MessageChannelManager.generate_random_string()
        return message_channel_id


class MessageChannel(models.Model):
    """Model that represents a MessageChannel."""
    id = models.CharField(max_length=10, primary_key=True)
    channel_type = models.CharField(max_length=2,
                                    choices=(("DM", "Direct Message"), ("GC", "Group Chat"), ("HE", "Hang Event")))
    users = models.ManyToManyField(User, related_name="message_channels", through="MessageChannelUsers")
    created_at = models.DateTimeField(auto_now_add=True)
    message_last_sent = models.DateTimeField(auto_now_add=True)

    objects = MessageChannelManager()

    def has_read_message_channel(self, user):
        mc_users = MessageChannelUsers.objects.filter(message_channel=self, user=user)
        if not mc_users.exists():
            return None
        obj = mc_users.get()
        return obj.has_read

    def read_message_channel(self, user):
        mc_users = MessageChannelUsers.objects.filter(message_channel=self, user=user)
        if not mc_users.exists():
            raise exceptions.ValidationError("MessageChannelUsers does not exist")
        obj = mc_users.get()
        obj.has_read = True
        obj.save()

    def contains_user(self, user):
        return self.users.contains(user)

    def contains_message(self, message):
        return self == message.message_channel


class MessageChannelUsers(models.Model, RTWSSendMessageOnUpdate):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message_channel = models.ForeignKey(MessageChannel, on_delete=models.CASCADE)
    has_read = models.BooleanField(default=True)

    rtws_message_content = "message_channel"

    def get_rtws_users(self):
        return [self.user] + list(self.message_channel.users.all())


class DirectMessageChannel(MessageChannel, RTWSSendMessageOnUpdate):
    """Model that represents a DM."""

    rtws_message_content = "message_channel"

    def get_rtws_users(self):
        return list(self.users.all())


class GroupMessageChannel(MessageChannel, RTWSSendMessageOnUpdate):
    """Model that represents a Group Chat."""
    name = models.CharField(max_length=75)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name="message_channels_owned", null=True)

    rtws_message_content = "message_channel"

    def get_rtws_users(self):
        return list(self.users.all())

    def update_users(self, current_user, new_users):
        existing_users = set(self.users.all())
        new_users = set(new_users)

        added_users = new_users - existing_users
        removed_users = existing_users - new_users

        for user in added_users:
            SystemMessage.objects.create(message_channel=self,
                                         content=f"{current_user.username} has added {user.username} to group chat {self.name}")

        for user in removed_users:
            SystemMessage.objects.create(message_channel=self,
                                         content=f"{current_user.username} has removed {user.username} from group chat {self.name}")

        self.users.set(new_users)

    def update_owner(self, current_user, new_owner):
        if self.owner != new_owner:
            SystemMessage.objects.create(message_channel=self,
                                         content=f"{current_user.username} has transferred ownership to {new_owner.username}")
            self.owner = new_owner
            self.save()

    def update_name(self, current_user, new_name):
        if self.name != new_name:
            SystemMessage.objects.create(message_channel=self,
                                         content=f"{current_user.username} has renamed the group chat {self.name} to {new_name}")
            self.name = new_name
            self.save()


class HangEventMessageChannel(MessageChannel, RTWSSendMessageOnUpdate):
    """Model that represents a HangEventMessageChannel."""
    rtws_message_content = "message_channel"

    def get_rtws_users(self):
        return list(self.users.all())


class Message(models.Model):
    """Model that represents a message."""
    type = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    message_channel = models.ForeignKey(MessageChannel, on_delete=models.CASCADE, related_name="messages")
    content = models.CharField(max_length=2000)


class UserMessage(Message):
    """Model that represents a user-sent message."""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="messages", null=True)
    reply = models.ForeignKey("self", on_delete=models.SET_NULL, related_name="replies", null=True)

    def __init__(self, *args, **kwargs):
        self._meta.get_field('type').default = "user_message"
        super(UserMessage, self).__init__(*args, **kwargs)


class SystemMessage(Message):
    """Model that represents a system-sent message."""

    def __init__(self, *args, **kwargs):
        self._meta.get_field('type').default = "system_message"
        super(SystemMessage, self).__init__(*args, **kwargs)


class Reaction(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    emoji = models.CharField(max_length=2)
