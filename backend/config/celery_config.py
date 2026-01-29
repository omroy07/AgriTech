"""
Celery Configuration
Configures Celery for async task processing
"""

from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize Celery
celery_app = Celery(
    'agritech',
    broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Kolkata',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Auto-discover tasks
celery_app.autodiscover_tasks(['backend.tasks'])

# Task routes (optional - for organizing tasks by queue)
celery_app.conf.task_routes = {
    'backend.tasks.report_tasks.generate_and_send_report': {'queue': 'reports'},
    'backend.tasks.report_tasks.generate_pdf_report': {'queue': 'pdf'},
    'backend.tasks.report_tasks.send_email_report': {'queue': 'email'},
}

if __name__ == '__main__':
    celery_app.start()
