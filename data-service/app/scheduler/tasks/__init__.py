"""
Celery task modules.
"""
from app.scheduler.tasks import market_tasks, news_tasks

__all__ = ["market_tasks", "news_tasks"]

