import os
from celery import Celery
print("RUNNING CELERY")
# Set default settings for Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

app = Celery("project")

# Load task modules from all registered Django apps
app.config_from_object("django.conf:settings", namespace="CELERY")

# Autodiscover tasks from installed apps
app.autodiscover_tasks()
