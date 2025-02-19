import os
from celery import Celery

# Set default settings for Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

app = Celery("project")

# Load task modules from all registered Django apps
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.broker_connection_retry_on_startup = True
# Autodiscover tasks from installed apps
app.autodiscover_tasks()

