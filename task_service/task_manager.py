from celery import signature

from .handlers import register_default_handlers
from .task_repository import TaskRepository


class TaskManager:
    def __init__(self):
        register_default_handlers()

    def create_task(self, task_type: str, payload: dict) -> str:
        task = TaskRepository.create(task_type, payload)

        # send to Celery worker; routing by task_type kept flat for now
        sig = signature("task_service.execute", args=[task.id, task_type, payload], queue="task-service")
        sig.delay()

        return task.id


# singleton manager
manager = TaskManager()
