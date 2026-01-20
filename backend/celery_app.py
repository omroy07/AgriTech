import os
from celery import Celery

# Redis URL from environment or default
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Create Celery app
celery_app = Celery(
    'agritech',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['backend.tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Kolkata',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    worker_prefetch_multiplier=1,
)
