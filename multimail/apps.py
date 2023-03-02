from django.apps import AppConfig


class MultimailConfig(AppConfig):
    name = 'multimail'

    def ready(self):
        from . import signals
