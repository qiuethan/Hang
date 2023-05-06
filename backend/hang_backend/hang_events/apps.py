from django.apps import AppConfig


class HangEventConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hang_events'

    def ready(self):
        import hang_events.signals