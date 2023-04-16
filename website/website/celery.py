import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')

app = Celery('website')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# To run Celery
# celery -A website worker -l INFO


app.conf.beat_schedule = {
    'start-every-day-at-7-13-19-hours': {
        'task': 'flats.tasks.task_send_flat_changes',
        'schedule': crontab(minute=0, hour='7,13,19')   # каждый день в 7,13,19 часов
        # 'schedule': 10.0  # каждые 10 секунд
        # 'args': (16, 16)
    },
}

# To start the celery beat service
# celery -A website beat -l INFO
