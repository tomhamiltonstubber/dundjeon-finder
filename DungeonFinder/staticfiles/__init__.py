from django.apps import AppConfig


class StaticFilesConfig(AppConfig):
    name = 'DungeonFinder.staticfiles'
    label = 'DungeonFinder.sw_staticfiles'


default_app_config = 'DungeonFinder.staticfiles.StaticFilesConfig'
