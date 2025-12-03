"""
Content Service - Main Application Entry
"""
from fastapi import FastAPI
from app.config import settings
from app.api import router as api_router
from app.celery_app import celery_app

app = FastAPI(
    title="QuantBull Content Service",
    version="1.0.0",
    description="Content management and distribution service"
)

# Include API routers
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "content-service"}

@app.get("/status")
async def status_check():
    """Detailed status check endpoint"""
    from celery.result import AsyncResult
    # Test Celery connection
    try:
        # Send a test task
        result = celery_app.send_task('app.tasks.test_task')
        task_result = AsyncResult(result.id, app=celery_app)
        celery_status = "connected" if task_result.state != "FAILURE" else "disconnected"
    except Exception:
        celery_status = "disconnected"
    
    return {
        "status": "healthy",
        "service": "content-service",
        "version": "1.0.0",
        "celery": celery_status,
        "modules": ["crawler", "cleaner", "scheduler", "storage", "api"]
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "QuantBull Content Service",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "status": "/status"
        }
    }
