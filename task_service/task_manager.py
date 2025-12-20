import asyncio
import uuid
from typing import Callable, Any, Dict

from .task_store import TaskRecord, store


HandlerType = Callable[[dict, Callable[[float], None]], Any]


class TaskManager:
    def __init__(self):
        # handler registry keyed by task_type
        self._handlers: Dict[str, HandlerType] = {}

    def register_handler(self, task_type: str, handler: HandlerType):
        self._handlers[task_type] = handler

    def create_task(self, task_type: str, payload: dict) -> str:
        task_id = str(uuid.uuid4())
        record = TaskRecord(task_id=task_id, status="pending", progress=0.0, meta={"task_type": task_type, "payload": payload})
        store.create(record)

        # schedule background execution
        handler = self._handlers.get(task_type)
        if handler is None:
            # mark failed immediately
            store.update(task_id, status="failed", error_code="no_handler", error_message=f"No handler for {task_type}")
            return task_id

        asyncio.create_task(self._run(task_id, handler, payload))
        return task_id

    async def _run(self, task_id: str, handler: HandlerType, payload: dict):
        def update_progress(p: float):
            # clamp
            p_clamped = max(0.0, min(1.0, float(p)))
            store.update(task_id, progress=p_clamped, status="running")

        store.update(task_id, status="running", progress=0.0)
        try:
            result = await _maybe_await(handler(payload, update_progress))
            # handler can return result_url or dict
            result_url = None
            if isinstance(result, str):
                result_url = result
            elif isinstance(result, dict):
                result_url = result.get("result_url")

            store.update(task_id, status="success", progress=1.0, result_url=result_url)
        except Exception as e:
            store.update(task_id, status="failed", error_message=str(e), error_code=getattr(e, "code", "exception"))


async def _maybe_await(v):
    if asyncio.iscoroutine(v):
        return await v
    return v


# singleton manager
manager = TaskManager()
