"""
Celery task modules for user service.
"""
from app.scheduler.tasks import user_tasks

__all__ = ["user_tasks"]

