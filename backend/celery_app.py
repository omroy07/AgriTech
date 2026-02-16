import os
from celery import Celery

# Redis URL from environment or default
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config.get('REDIS_URL', 'redis://localhost:6379/0'),
        backend=app.config.get('REDIS_URL', 'redis://localhost:6379/0')
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

# Simple instance for module-level imports
celery_app = Celery(
    'agritech',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['backend.tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Kolkata',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    worker_prefetch_multiplier=1,
    beat_schedule={
        'update-market-prices-every-hour': {
            'task': 'tasks.update_market_prices',
            'schedule': 3600.0,  # 1 hour
        },
        'hourly-freshness-pricing': {
            'task': 'tasks.hourly_freshness_pricing_update',
            'schedule': 3600.0,
        },
        'pathogen-propagation-simulation': {
            'task': 'tasks.pathogen_propagation_run',
            'schedule': 1800.0, # Every 30 mins
        }
    }
)
