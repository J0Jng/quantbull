from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class TaskRecord:
    task_id: str
    status: str  # pending | running | success | failed
    progress: float = 0.0
    result_url: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    meta: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # serialize datetimes as isoformat
        d["created_at"] = self.created_at.isoformat()
        d["updated_at"] = self.updated_at.isoformat()
        return d


class TaskStore:
    """In-memory store for tasks. Easy to replace with Redis later."""

    def __init__(self):
        self._store: Dict[str, TaskRecord] = {}

    def create(self, record: TaskRecord) -> None:
        self._store[record.task_id] = record

    def get(self, task_id: str) -> Optional[TaskRecord]:
        return self._store.get(task_id)

    def update(self, task_id: str, **kwargs) -> Optional[TaskRecord]:
        rec = self._store.get(task_id)
        if not rec:
            return None
        for k, v in kwargs.items():
            if hasattr(rec, k):
                setattr(rec, k, v)
        rec.updated_at = datetime.utcnow()
        return rec


# singleton store for the app
store = TaskStore()
