from django.apps import AppConfig as _AppConfig


class AppConfig(_AppConfig):
    name = 'DungeonFinder.actions'
    label = 'actions'

    def ready(self):
        import DungeonFinder.actions.hooks  # noqa
