import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medusa.settings')

app = Celery('medusa')

# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

# Celery Configuration
app.conf.update(
    broker_url=os.environ.get('CELERY_BROKER_URL', 'redis://medusa-redis:6379/0'),
    result_backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://medusa-redis:6379/0'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=60,  # 1 minute
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)
