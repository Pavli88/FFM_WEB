from django.core.management.base import BaseCommand
from django.core.cache import cache

from robots.models import *

class Command(BaseCommand):
    help = 'Refreshes my cache'

    def handle_noargs(self, **options):
        cache.set('key', queryset)