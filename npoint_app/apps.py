from django.apps import AppConfig


class NpointAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'npoint_app'

class NpointAppConfig(AppConfig):
    name = 'npoint_app'
    def ready(self):
        import npoint_app.signals  # noqa
