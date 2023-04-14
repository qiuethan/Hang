from django.apps import AppConfig


class HangEventConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hang_event'

    def ready(self):
        import hang_event.signals