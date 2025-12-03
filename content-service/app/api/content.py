"""
Content API endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class CrawlRequest(BaseModel):
    source_url: str
    source_type: str = "article"
    schedule: bool = False
    schedule_time: Optional[datetime] = None

class CleanRequest(BaseModel):
    content: str
    content_type: str = "html"

@router.post("/crawl")
async def start_crawling(request: CrawlRequest, background_tasks: BackgroundTasks):
    """Start content crawling"""
    from app.crawler.tasks import crawl_article, crawl_video
    
    if request.source_type == "article":
        task = crawl_article.delay(request.source_url)
    elif request.source_type == "video":
        task = crawl_video.delay(request.source_url)
    else:
        raise HTTPException(status_code=400, detail="Unsupported content type")
    
    return {
        "status": "started",
        "task_id": task.id,
        "source_url": request.source_url,
        "source_type": request.source_type
    }

@router.post("/clean")
async def clean_content(request: CleanRequest):
    """Clean and normalize content"""
    from app.cleaner.tasks import clean_content
    
    task = clean_content.delay({
        "type": request.content_type,
        "text": request.content,
        "html": request.content if request.content_type == "html" else None
    })
    
    return {
        "status": "processing",
        "task_id": task.id,
        "content_type": request.content_type
    }

@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get task status"""
    from celery.result import AsyncResult
    from app.celery_app import celery_app
    
    result = AsyncResult(task_id, app=celery_app)
    
    return {
        "task_id": task_id,
        "status": result.state,
        "result": result.result if result.ready() else None,
        "ready": result.ready()
    }

@router.get("/schedules")
async def get_scheduled_tasks():
    """Get scheduled tasks"""
    from app.celery_app import celery_app
    
    # Get scheduled tasks from Celery beat
    schedules = celery_app.conf.beat_schedule
    
    return {
        "schedules": [
            {
                "name": name,
                "task": schedule['task'],
                "schedule": str(schedule['schedule']),
                "args": schedule.get('args', [])
            }
            for name, schedule in schedules.items()
        ]
    }