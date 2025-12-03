"""
Configuration management
"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    service_name: str = "content-service"
    debug: bool = False
    
    # Database
    postgres_url: str = "postgresql://user:password@postgres:5432/quantbull"
    
    # Redis
    redis_url: str = "redis://redis:6379/0"
    redis_result_backend: str = "redis://redis:6379/1"
    
    # OSS Storage
    oss_endpoint: str = ""
    oss_access_key: str = ""
    oss_secret_key: str = ""
    oss_bucket: str = ""
    
    # WeChat
    wechat_appid: str = ""
    wechat_secret: str = ""
    
    # Celery
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"
    
    class Config:
        env_file = ".env"

settings = Settings()