"""
Content cleaner Celery tasks
"""
from celery import current_task
from app.celery_app import celery_app
import logging
from typing import Dict, Any
import html

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="cleaner.clean_content")
def clean_content(self, content: Dict[str, Any]):
    """Clean and normalize content"""
    try:
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Starting cleaning'}
        )
        
        content_type = content.get('type', 'text')
        
        # Sanitize HTML
        if 'html' in content:
            current_task.update_state(
                state='PROGRESS',
                meta={'current': 30, 'total': 100, 'status': 'Sanitizing HTML'}
            )
            content['html'] = sanitize_html(content['html'])
        
        # Clean text
        if 'text' in content:
            current_task.update_state(
                state='PROGRESS',
                meta={'current': 60, 'total': 100, 'status': 'Cleaning text'}
            )
            content['text'] = html.escape(content['text'])
        
        # Extract metadata
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 90, 'total': 100, 'status': 'Extracting metadata'}
        )
        
        # Add cleaning metadata
        content['cleaned_at'] = datetime.utcnow().isoformat()
        content['cleaned'] = True
        
        return {
            'status': 'success',
            'content_type': content_type,
            'cleaned_content': content
        }
        
    except Exception as e:
        logger.error(f"Content cleaning failed: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }

@celery_app.task(name="cleaner.sanitize_html")
def sanitize_html(html_content: str) -> str:
    """Sanitize HTML content"""
    # Implement HTML sanitization logic here
    # For now, return as-is (in production use a library like bleach)
    return html_content

@celery_app.task(name="cleaner.extract_keywords")
def extract_keywords(text: str, max_keywords: int = 10) -> list:
    """Extract keywords from text"""
    # Implement keyword extraction logic here
    # For now, return mock keywords
    words = text.split()[:max_keywords]
    return list(set(words))