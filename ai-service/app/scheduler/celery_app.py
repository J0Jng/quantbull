"""
Celery application configuration for AI service.
"""
from celery import Celery

from app.config import settings

# Create Celery instance
celery_app = Celery(
    "ai-service",
    broker=settings.celery_broker_url or settings.redis_url,
    backend=settings.celery_result_backend or settings.redis_url,
    include=[
        "app.scheduler.tasks.ai_tasks",
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
        "app.scheduler.tasks.ai_tasks.*": {"queue": "ai"},
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
        "generate-daily-report": {
            "task": "app.scheduler.tasks.ai_tasks.generate_daily_report",
            "schedule": {"hour": 16, "minute": 0},  # Daily at 16:00 (after market close)
            "options": {"queue": "ai"},
        },
        "sync-prompt-templates": {
            "task": "app.scheduler.tasks.ai_tasks.sync_prompt_templates",
            "schedule": 3600.0,  # Every hour
            "options": {"queue": "ai"},
        },
        "clean-old-generations": {
            "task": "app.scheduler.tasks.ai_tasks.clean_old_generations",
            "schedule": 86400.0,  # Daily
            "options": {"queue": "ai"},
        },
    },
)

