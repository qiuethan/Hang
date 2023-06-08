"""
ICS4U
Paul Chen
This module defines the signals for the real_time_ws package.
"""

from django.db.models.signals import post_save, m2m_changed, pre_delete
from django.dispatch import receiver

from real_time_ws.models import RTWSSendMessageOnUpdate


@receiver(post_save)
def model_saved_notify_rtws(sender, instance, created, **kwargs):
    """Sends RTWS messages when a model is saved."""
    if issubclass(type(instance), RTWSSendMessageOnUpdate):
        instance.send_rtws_message()


@receiver(pre_delete)
def model_deleted_notify_rtws(sender, instance, **kwargs):
    """Sends RTWS messages when a model is deleted."""
    if issubclass(type(instance), RTWSSendMessageOnUpdate):
        instance.send_rtws_message()


@receiver(m2m_changed)
def m2m_field_changed_notify_rtws(sender, instance, action, reverse, model, pk_set, **kwargs):
    """Sends RTWS messages when a m2m field is changed in a model."""
    if issubclass(type(instance), RTWSSendMessageOnUpdate):
        instance.send_rtws_message()
