from celery import Celery

from .config import settings


celery_app = Celery(
    "task_service",
    broker=settings.celery_broker_url or settings.redis_url,
    backend=settings.celery_result_backend or settings.redis_url,
    include=["task_service.handlers"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_default_queue="task-service",
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    broker_connection_retry_on_startup=True,
)


def register_celery_tasks():
    # Importing registers tasks through decorators
    from . import handlers  # noqa: F401


__all__ = ["celery_app", "register_celery_tasks"]
