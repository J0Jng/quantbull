"""
Configuration management for user service.
"""
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Service settings
    service_name: str = "user-service"
    service_version: str = "1.0.0"
    debug: bool = False
    
    # Database settings
    postgres_url: str = "postgresql://user:password@postgres:5432/quantbull"
    redis_url: str = "redis://redis:6379/0"
    
    # Celery settings
    celery_broker_url: Optional[str] = None
    celery_result_backend: Optional[str] = None
    
    # JWT settings
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # External service integrations
    wechat_appid: Optional[str] = None
    wechat_secret: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8005
    
    # Security settings
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_special: bool = False
    
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

