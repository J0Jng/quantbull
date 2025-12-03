"""
Task scheduler modules using Celery for async and scheduled tasks.
"""
from app.scheduler.celery_app import celery_app
from app.scheduler.tasks import ai_tasks

__all__ = ["celery_app", "ai_tasks"]

