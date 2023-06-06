"""
ICS4U
Paul Chen
This module contains signal handlers that respond to changes in instances of classes inheriting from RTWSSendMessageOnUpdate.
"""

from django.db.models.signals import post_save, m2m_changed, pre_delete
from django.dispatch import receiver

from real_time_ws.models import RTWSSendMessageOnUpdate


@receiver(post_save)
def handle_model_save(sender, instance, created, **kwargs):
    """
    Sends RTWS messages when a model is updated.
    """
    if issubclass(type(instance), RTWSSendMessageOnUpdate):
        instance.send_rtws_message()


@receiver(pre_delete)
def handle_model_delete(sender, instance, **kwargs):
    """
    Sends RTWS messages when a model is deleted.
    """
    if issubclass(type(instance), RTWSSendMessageOnUpdate):
        instance.send_rtws_message()


@receiver(m2m_changed)
def handle_m2m_field_change(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Sends RTWS messages when an m2m field is changed in a model.
    """
    if issubclass(type(instance), RTWSSendMessageOnUpdate):
        instance.send_rtws_message()
