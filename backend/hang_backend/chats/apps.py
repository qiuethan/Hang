from django.apps import AppConfig, apps
from django.db.models.signals import post_save, pre_save, post_delete, pre_delete


class ChatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chats"

    def ready(self):
        from .signals import (
            message_created,
            message_updated,
            message_deleted,
            message_reacted,
            reaction_removed,
            message_post_save
        )
        from .models import Message, Reaction

        models = apps.get_models()
        for model in models:
            if issubclass(model, Message):
                post_save.connect(message_created, sender=model)
                pre_save.connect(message_updated, sender=model)
                post_save.connect(message_post_save, sender=model)

        post_delete.connect(message_deleted, sender=Message)
        post_save.connect(message_reacted, sender=Reaction)
        post_delete.connect(reaction_removed, sender=Reaction)
