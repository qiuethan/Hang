from django.db.models.signals import post_save, m2m_changed, pre_delete
from django.dispatch import receiver

from real_time_ws.models import RTWSSendMessageOnUpdate


@receiver(post_save)
def handle_model_save(sender, instance, created, **kwargs):
    if issubclass(type(instance), RTWSSendMessageOnUpdate):
        instance.send_rtws_message()


@receiver(pre_delete)
def handle_model_delete(sender, instance, **kwargs):
    if issubclass(type(instance), RTWSSendMessageOnUpdate):
        instance.send_rtws_message()


@receiver(m2m_changed)
def handle_m2m_field_change(sender, instance, action, reverse, model, pk_set, **kwargs):
    if issubclass(type(instance), RTWSSendMessageOnUpdate):
        instance.send_rtws_message()
