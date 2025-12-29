import asyncio
import os
from typing import Any, Callable, Dict

import httpx

from .celery_app import celery_app
from .task_repository import TaskRepository

HandlerType = Callable[[Dict[str, Any], Callable[[float], None]], Any]

# registry keeps business executors out of FastAPI thread pool
handler_registry: Dict[str, HandlerType] = {}


def register_handler(task_type: str, handler: HandlerType) -> None:
    handler_registry[task_type] = handler


def register_default_handlers():
    register_handler("backtest", backtest_handler)


def _resolve_handler(task_type: str) -> HandlerType | None:
    return handler_registry.get(task_type)


def _coerce_result(res: Any) -> Dict[str, Any]:
    if res is None:
        return {}
    if isinstance(res, dict):
        return res
    return {"result": res}


def _run_sync_or_async(handler: HandlerType, payload: Dict[str, Any], update_progress: Callable[[float], None]) -> Any:
    result = handler(payload, update_progress)
    if asyncio.iscoroutine(result):
        return asyncio.run(result)
    return result


@celery_app.task(
    name="task_service.execute",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
    soft_time_limit=int(os.getenv("TASK_SOFT_TIME_LIMIT", "300")),
    time_limit=int(os.getenv("TASK_HARD_TIME_LIMIT", "330")),
)
def execute_task(self, task_id: str, task_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Entry point executed by Celery workers."""
    handler = _resolve_handler(task_type)
    if not handler:
        TaskRepository.mark_failed(task_id, f"No handler registered for {task_type}", error_code="no_handler")
        return {}

    TaskRepository.mark_running(task_id, progress=0.0)

    def update_progress(progress: float) -> None:
        TaskRepository.mark_progress(task_id, progress)

    try:
        payload_with_ids = dict(payload or {})
        payload_with_ids.setdefault("task_id", task_id)
        res = _run_sync_or_async(handler, payload_with_ids, update_progress)
        result_dict = _coerce_result(res)
        TaskRepository.mark_success(
            task_id,
            result_url=result_dict.get("result_url"),
            result=result_dict,
        )
        return result_dict
    except Exception as exc:  # pragma: no cover - defensive
        TaskRepository.mark_failed(task_id, error_message=str(exc), error_code=getattr(exc, "code", "exception"))
        raise


def backtest_handler(payload: Dict[str, Any], update_progress: Callable[[float], None]) -> Dict[str, Any]:
    """Forward backtest execution to quant-engine (or another executor) via HTTP.

    This keeps business logic out of task-service while providing a real async worker.
    """

    exec_url = os.getenv("QUANT_ENGINE_EXEC_URL", "http://quant-engine:8003/api/backtest/run_sync")
    timeout = float(os.getenv("BACKTEST_TIMEOUT", "120"))

    update_progress(0.05)
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(exec_url, json=payload)
        resp.raise_for_status()
        data = resp.json() if resp.content else {}

    update_progress(1.0)
    result_url = data.get("result_url") or data.get("backtest_id")
    return {"result_url": result_url, "result": data}


# ensure built-in handlers are available both in API and Celery worker processes
register_default_handlers()
