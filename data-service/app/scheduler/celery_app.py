"""
Celery application configuration.
"""
from celery import Celery

from app.config import settings

# Create Celery instance
celery_app = Celery(
    "data-service",
    broker=settings.celery_broker_url or settings.redis_url,
    backend=settings.celery_result_backend or settings.redis_url,
    include=[
        "app.scheduler.tasks.market_tasks",
        "app.scheduler.tasks.news_tasks",
    ],
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    
    # Task routing
    task_routes={
        "app.scheduler.tasks.market_tasks.*": {"queue": "market"},
        "app.scheduler.tasks.news_tasks.*": {"queue": "news"},
    },
    
    # Task execution
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Result settings
    result_expires=3600,  # Results expire after 1 hour
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # Beat schedule (for periodic tasks)
    beat_schedule={
        "collect-market-data-every-minute": {
            "task": "app.scheduler.tasks.market_tasks.collect_realtime_quotes",
            "schedule": 60.0,  # Every 60 seconds
            "options": {"queue": "market"},
        },
        "collect-news-every-5-minutes": {
            "task": "app.scheduler.tasks.news_tasks.collect_latest_news",
            "schedule": 300.0,  # Every 5 minutes
            "options": {"queue": "news"},
        },
    },
)

