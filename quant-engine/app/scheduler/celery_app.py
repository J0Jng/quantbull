"""
Celery application configuration for quant engine service.
"""
from celery import Celery

from app.config import settings

# Create Celery instance
celery_app = Celery(
    "quant-engine",
    broker=settings.celery_broker_url or settings.redis_url,
    backend=settings.celery_result_backend or settings.redis_url,
    include=[
        "app.scheduler.tasks.quant_tasks",
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
        "app.scheduler.tasks.quant_tasks.*": {"queue": "quant"},
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
        "calculate-factors-daily": {
            "task": "app.scheduler.tasks.quant_tasks.calculate_factors_daily",
            "schedule": {"hour": 16, "minute": 30},  # Daily at 16:30 (after market close)
            "options": {"queue": "quant"},
        },
        "run-scheduled-backtests": {
            "task": "app.scheduler.tasks.quant_tasks.run_scheduled_backtests",
            "schedule": 86400.0,  # Daily
            "options": {"queue": "quant"},
        },
        "update-stock-scores": {
            "task": "app.scheduler.tasks.quant_tasks.update_stock_scores",
            "schedule": {"hour": 16, "minute": 0},  # Daily at 16:00
            "options": {"queue": "quant"},
        },
    },
)

