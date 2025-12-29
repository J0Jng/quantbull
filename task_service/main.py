from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from .db import init_db
from .task_manager import manager
from .task_repository import TaskRepository
from .core.response import success
from .core.handlers import http_exception_handler, validation_exception_handler, generic_exception_handler

app = FastAPI(title="task-service", version="0.1.0")


class CreateTaskRequest(BaseModel):
    task_type: str
    payload: Optional[dict] = {}


class TaskResponse(BaseModel):
    task_id: str


@app.on_event("startup")
async def startup_event():
    init_db()

    # 注册异常处理，保证所有响应遵循 envelope
    from fastapi.exceptions import HTTPException as StarletteHTTPException, RequestValidationError
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)


@app.post("/api/tasks")
async def create_task(req: CreateTaskRequest):
    task_id = manager.create_task(req.task_type, req.payload or {})
    return success({"task_id": task_id})


@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    rec = TaskRepository.get(task_id)
    if not rec:
        raise HTTPException(status_code=404, detail="task not found")
    return success({
        "task_id": rec.id,
        "status": rec.status.value if hasattr(rec.status, "value") else str(rec.status),
        "progress": float(rec.progress),
        "result_url": rec.result_url,
        "result": rec.result,
        "error_code": rec.error_code,
        "error_message": rec.error_message,
        "task_type": rec.task_type,
        "created_at": rec.created_at.isoformat(),
        "updated_at": rec.updated_at.isoformat(),
    })


@app.get("/healthz")
async def healthz():
    return success({"status": "ok"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("task_service.main:app", host="0.0.0.0", port=9000, reload=False)
