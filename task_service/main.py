from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from .task_manager import manager
from .task_store import store
from .handlers import register_default_handlers
from .core.response import success, error
from .core.handlers import http_exception_handler, validation_exception_handler, generic_exception_handler

app = FastAPI(title="task-service", version="0.1.0")


class CreateTaskRequest(BaseModel):
    task_type: str
    payload: Optional[dict] = {}


class TaskResponse(BaseModel):
    task_id: str


@app.on_event("startup")
async def startup_event():
    # register built-in handlers
    register_default_handlers(manager)

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
    rec = store.get(task_id)
    if not rec:
        raise HTTPException(status_code=404, detail="task not found")
    return success({
        "task_id": rec.task_id,
        "status": rec.status,
        "progress": float(rec.progress),
        "result_url": rec.result_url,
        "error_code": rec.error_code,
        "error_message": rec.error_message,
    })


@app.get("/healthz")
async def healthz():
    return success({"status": "ok"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("task_service.main:app", host="0.0.0.0", port=9000, reload=False)
