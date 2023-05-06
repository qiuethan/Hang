from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from real_time_ws.models import RTWSSendMessageOnUpdate


@receiver(post_save)
def handle_model_save(sender, instance, created, **kwargs):
    if issubclass(type(instance), RTWSSendMessageOnUpdate):
        instance.send_rtws_message()


@receiver(m2m_changed)
def handle_m2m_field_change(sender, instance, action, reverse, model, pk_set, **kwargs):
    if issubclass(type(instance), RTWSSendMessageOnUpdate):
        if action in ['post_add', 'post_remove', 'post_clear']:
            instance.send_rtws_message()
