"""
Celery configuration for Content Service
"""
from celery import Celery
from app.config import settings

# Create Celery instance
celery_app = Celery(
    "content_service",
    broker=f"redis://redis:6379/0",
    backend=f"redis://redis:6379/1",
    include=[
        "app.crawler.tasks",
        "app.cleaner.tasks",
        "app.scheduler.tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    task_acks_late=True,
    broker_connection_retry_on_startup=True,
)

@celery_app.task(bind=True)
def test_task(self):
    """Test task to verify Celery is working"""
    return {"status": "success", "message": "Celery is working"}