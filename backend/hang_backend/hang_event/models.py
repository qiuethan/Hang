import uuid

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from chat.models import MessageChannel, HangEventMessageChannel, SystemMessage


def generate_unique_invitation_code():
    unique_code = str(uuid.uuid4())[:10]
    while HangEvent.objects.filter(invitation_code=unique_code).exists():
        unique_code = str(uuid.uuid4())[:10]
    return unique_code


class HangEvent(models.Model):
    """Model for a Hang Event."""
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="hang_events_owned")
    picture = models.CharField(max_length=200)
    description = models.TextField()
    scheduled_time_start = models.DateTimeField()
    scheduled_time_end = models.DateTimeField()
    longitude = models.FloatField(default=None, null=True)
    latitude = models.FloatField(default=None, null=True)
    address = models.TextField()
    budget = models.FloatField(default=None, null=True)
    attendees = models.ManyToManyField(User, related_name="hang_events")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    google_calendar_event_id = models.CharField(max_length=256, default=None, null=True)
    invitation_code = models.CharField(max_length=10, default=generate_unique_invitation_code, unique=True)
    message_channel = models.OneToOneField(HangEventMessageChannel, on_delete=models.CASCADE, default=None, null=True)
    archived = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super(HangEvent, self).__init__(*args, **kwargs)
        for field in self._meta.fields:
            if field.name in ["name", "owner", "description", "scheduled_time_start", "scheduled_time_end", "address"]:
                setattr(self, f"_old_{field.name}", getattr(self, field.name))

    def save(self, *args, **kwargs):
        is_new = not self.pk
        super(HangEvent, self).save(*args, **kwargs)

        if is_new:
            message_channel = MessageChannel.objects.create_hang_event_message_channel(self)
            self.message_channel = message_channel
            self.save()


class Task(models.Model):
    event = models.ForeignKey(HangEvent, related_name="tasks", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    completed = models.BooleanField(default=False)


@receiver(m2m_changed, sender=HangEvent.attendees.through)
def update_hang_event_message_channel(sender, instance, action, pk_set, **kwargs):
    if action == "post_add" or action == "post_remove" or action == "post_clear":
        if hasattr(instance, "message_channel"):
            instance.message_channel.users.set(instance.attendees.all())


# Modify the signal receiver to apply the changes only to specific fields
@receiver(post_save, sender=HangEvent)
def send_hang_event_updated_message(sender, instance, created, **kwargs):
    if not created:
        tracked_fields = [
            "name", "owner", "description", "scheduled_time_start", "scheduled_time_end", "address"
        ]
        for field_name in tracked_fields:
            field = instance._meta.get_field(field_name)
            old_value = getattr(instance, f"_old_{field.name}")
            new_value = getattr(instance, field.name)
            if old_value != new_value:
                SystemMessage.objects.create(message_channel=instance.message_channel,
                                             content=f"Hang event {instance.name} updated: {field.name} changed from {str(old_value)} to {str(new_value)}")
                setattr(instance, f"_old_{field.name}", new_value)


# Add signal receivers for user added and removed messages
@receiver(m2m_changed, sender=HangEvent.attendees.through)
def send_hang_event_user_added_or_removed_message(sender, instance, action, pk_set, **kwargs):
    if action in ["post_add", "post_remove"]:
        for user_pk in pk_set:
            user = User.objects.get(pk=user_pk)
            if action == "post_add":
                SystemMessage.objects.create(f"{user.username} has joined the Hang event {instance.name}")
            else:
                SystemMessage.objects.create(f"{user.username} has left the Hang event {instance.name}")
