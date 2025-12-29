from datetime import datetime
from typing import Any, Dict, Optional

from sqlmodel import select

from .db import get_session
from .models import Task, TaskStatus


class TaskRepository:
    @staticmethod
    def create(task_type: str, payload: Optional[Dict[str, Any]]) -> Task:
        task = Task(task_type=task_type, payload=payload or {}, status=TaskStatus.pending)
        with get_session() as session:
            session.add(task)
            session.commit()
            session.refresh(task)
            return task

    @staticmethod
    def get(task_id: str) -> Optional[Task]:
        with get_session() as session:
            stmt = select(Task).where(Task.id == task_id)
            result = session.exec(stmt).first()
            return result

    @staticmethod
    def mark_running(task_id: str, progress: float = 0.0) -> None:
        TaskRepository._update(task_id, status=TaskStatus.running, progress=progress)

    @staticmethod
    def mark_progress(task_id: str, progress: float) -> None:
        TaskRepository._update(task_id, progress=max(0.0, min(1.0, float(progress))))

    @staticmethod
    def mark_success(task_id: str, result_url: Optional[str] = None, result: Optional[Dict[str, Any]] = None) -> None:
        TaskRepository._update(
            task_id,
            status=TaskStatus.success,
            progress=1.0,
            result_url=result_url,
            result=result,
        )

    @staticmethod
    def mark_failed(task_id: str, error_message: str, error_code: str = "error") -> None:
        TaskRepository._update(task_id, status=TaskStatus.failed, error_message=error_message, error_code=error_code)

    @staticmethod
    def _update(task_id: str, **fields) -> None:
        with get_session() as session:
            task = session.get(Task, task_id)
            if not task:
                return
            for k, v in fields.items():
                setattr(task, k, v)
            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()
