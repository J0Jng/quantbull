"""
Configuration management
"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    # Gateway settings
    service_name: str = "gateway"
    debug: bool = False
    
    # Service endpoints
    data_service_url: str = "http://data-service:8001"
    ai_service_url: str = "http://ai-service:8002"
    quant_engine_url: str = "http://quant-engine:8003"
    content_service_url: str = "http://content-service:8004"
    
    # Auth settings
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    
    class Config:
        env_file = ".env"

settings = Settings()

