"""
Configuration management for data service.
"""
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Service settings
    service_name: str = "data-service"
    service_version: str = "1.0.0"
    debug: bool = False
    
    # Database settings
    postgres_url: str = "postgresql://user:password@postgres:5432/quantbull"
    tdengine_url: Optional[str] = None
    redis_url: str = "redis://redis:6379/0"
    
    # Data sources
    tushare_token: Optional[str] = None
    cls_api_key: Optional[str] = None
    
    # Celery settings
    celery_broker_url: Optional[str] = None
    celery_result_backend: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8001
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    def __init__(self, **kwargs):
        """Initialize settings with defaults."""
        super().__init__(**kwargs)
        # Use redis_url for Celery if not explicitly set
        if not self.celery_broker_url:
            self.celery_broker_url = self.redis_url
        if not self.celery_result_backend:
            self.celery_result_backend = self.redis_url


settings = Settings()

