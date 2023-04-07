from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from calendars.models import ManualCalendar, ImportedCalendar
from .models import UserDetails


@receiver(post_save, sender=get_user_model())
def create_user_details(sender, instance, created, **kwargs):
    if created:
        UserDetails.objects.create(user=instance)
        ManualCalendar.objects.create(user=instance)
        ImportedCalendar.objects.create(user=instance)
