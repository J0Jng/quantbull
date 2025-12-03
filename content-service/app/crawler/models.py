"""
Crawler data models
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class SourceType(str, Enum):
    ARTICLE = "article"
    VIDEO = "video"
    REPORT = "report"
    NEWS = "news"

class CrawlStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class CrawlSource(BaseModel):
    """Crawl source configuration"""
    id: str
    name: str
    url: str
    source_type: SourceType
    crawl_pattern: Optional[str] = None
    interval_minutes: int = 60
    is_active: bool = True
    last_crawl_time: Optional[datetime] = None
    config: Dict[str, Any] = Field(default_factory=dict)

class CrawlTask(BaseModel):
    """Crawl task definition"""
    task_id: str
    source_id: str
    status: CrawlStatus = CrawlStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    items_found: int = 0
    items_processed: int = 0
    error: Optional[str] = None
    result_urls: list[str] = Field(default_factory=list)