"""
Configuration management for AI service.
"""
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Service settings
    service_name: str = "ai-service"
    service_version: str = "1.0.0"
    debug: bool = False
    
    # Database settings
    postgres_url: str = "postgresql://user:password@postgres:5432/quantbull"
    redis_url: str = "redis://redis:6379/0"
    
    # Celery settings
    celery_broker_url: Optional[str] = None
    celery_result_backend: Optional[str] = None
    
    # LLM Providers
    deepseek_api_key: Optional[str] = None
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    qwen_api_key: Optional[str] = None
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    # Local Model
    local_model_path: Optional[str] = None
    local_model_enabled: bool = False
    
    # Vector DB
    milvus_host: str = "milvus"
    milvus_port: int = 19530
    
    # Digital Human API
    digital_human_api_key: Optional[str] = None
    digital_human_api_secret: Optional[str] = None
    digital_human_provider: str = "silicone"  # silicone or tencent
    
    # Content generation settings
    max_generation_length: int = 4000
    default_temperature: float = 0.7
    default_max_tokens: int = 2000
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8002
    
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

