"""
Scheduler Celery tasks
"""
from celery import Celery
from celery.schedules import crontab
from app.celery_app import celery_app
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name="scheduler.schedule_crawl")
def schedule_crawl(source_id: str = None):
    """Schedule crawling tasks"""
    logger.info(f"Scheduling crawl for source: {source_id}")
    
    if source_id:
        # Schedule specific source
        from app.crawler.tasks import start_crawler
        start_crawler.delay(source_id)
    else:
        # Schedule all active sources
        # This would query database for active sources
        # For now, just log
        logger.info("Scheduling all active sources")
    
    return {"scheduled": True, "time": datetime.utcnow().isoformat()}

@celery_app.task(name="scheduler.schedule_cleanup")
def schedule_cleanup(days_old: int = 30):
    """Schedule cleanup of old data"""
    logger.info(f"Scheduling cleanup for data older than {days_old} days")
    
    # Calculate cutoff date
    cutoff_date = datetime.utcnow() - timedelta(days=days_old)
    
    # This would cleanup old crawl logs, temp files, etc.
    # For now, just log
    logger.info(f"Would cleanup data older than {cutoff_date}")
    
    return {
        "cleanup_scheduled": True,
        "cutoff_date": cutoff_date.isoformat(),
        "days_old": days_old
    }

@celery_app.task(name="scheduler.schedule_wechat_push")
def schedule_wechat_push(content_id: str, schedule_time: str = None):
    """Schedule WeChat content push"""
    logger.info(f"Scheduling WeChat push for content: {content_id}")
    
    # This would schedule a WeChat push for the content
    # For now, just log
    if schedule_time:
        logger.info(f"Scheduled for: {schedule_time}")
    
    return {
        "wechat_push_scheduled": True,
        "content_id": content_id,
        "scheduled_time": schedule_time or datetime.utcnow().isoformat()
    }

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    'hourly-crawl': {
        'task': 'scheduler.schedule_crawl',
        'schedule': crontab(minute=0, hour='*/1'),  # Every hour
        'args': (None,),  # Crawl all sources
    },
    'daily-cleanup': {
        'task': 'scheduler.schedule_cleanup',
        'schedule': crontab(minute=0, hour=2),  # 2 AM daily
        'args': (30,),  # Cleanup 30+ days old
    },
    'weekly-report': {
        'task': 'scheduler.schedule_wechat_push',
        'schedule': crontab(minute=0, hour=9, day_of_week='mon'),  # 9 AM Monday
        'args': ('weekly_report', '09:00'),
    },
}