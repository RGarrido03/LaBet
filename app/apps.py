from django.apps import AppConfig
from django_web_components import component


class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"

    def ready(self):
        from . import components  # noqa
