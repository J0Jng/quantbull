"""
Celery application configuration for user service.
"""
from celery import Celery

from app.config import settings

# Create Celery instance
celery_app = Celery(
    "user-service",
    broker=settings.celery_broker_url or settings.redis_url,
    backend=settings.celery_result_backend or settings.redis_url,
    include=[
        "app.scheduler.tasks.user_tasks",
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
        "app.scheduler.tasks.user_tasks.*": {"queue": "users"},
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
        "sync-wechat-users": {
            "task": "app.scheduler.tasks.user_tasks.sync_wechat_users",
            "schedule": 3600.0,  # Every hour
            "options": {"queue": "users"},
        },
        "clean-expired-tokens": {
            "task": "app.scheduler.tasks.user_tasks.clean_expired_tokens",
            "schedule": 3600.0,  # Every hour
            "options": {"queue": "users"},
        },
        "clean-inactive-users": {
            "task": "app.scheduler.tasks.user_tasks.clean_inactive_users",
            "schedule": 86400.0,  # Daily
            "options": {"queue": "users"},
        },
    },
)

