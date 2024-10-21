from django.apps import AppConfig
from django.core.cache import cache
from django.core import serializers
from django.conf import settings
import json


class MySiteConfig(AppConfig):
    name = 'mysite'

    def ready(self):
        print("Main application is ready to load initial processes")
        base_dir = settings.BASE_DIR

