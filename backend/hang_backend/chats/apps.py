from django.apps import AppConfig, apps
from django.db.models.signals import post_save, pre_save, post_delete, pre_delete


class ChatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chats"

    def ready(self):
        from .signals import (
            message_created_notify_chat,
            message_edited_notify_chat,
            message_deleted_notify_chat,
            message_reacted_added_notify_chat,
            message_reaction_removed_notify_chat,
            message_saved_create_notifications
        )
        from .models import Message, Reaction

        models = apps.get_models()
        for model in models:
            if issubclass(model, Message):
                post_save.connect(message_created_notify_chat, sender=model)
                pre_save.connect(message_edited_notify_chat, sender=model)
                post_save.connect(message_saved_create_notifications, sender=model)

        post_delete.connect(message_deleted_notify_chat, sender=Message)
        post_save.connect(message_reacted_added_notify_chat, sender=Reaction)
        post_delete.connect(message_reaction_removed_notify_chat, sender=Reaction)
