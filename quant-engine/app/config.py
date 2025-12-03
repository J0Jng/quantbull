"""
Configuration management for quant engine service.
"""
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Service settings
    service_name: str = "quant-engine"
    service_version: str = "1.0.0"
    debug: bool = False
    
    # Database settings
    postgres_url: str = "postgresql://user:password@postgres:5432/quantbull"
    redis_url: str = "redis://redis:6379/0"
    
    # Celery settings
    celery_broker_url: Optional[str] = None
    celery_result_backend: Optional[str] = None
    
    # Data Service URL
    data_service_url: str = "http://data-service:8001"
    
    # Backtest settings
    initial_capital: float = 1000000.0
    commission_rate: float = 0.001
    slippage_rate: float = 0.001
    
    # Factor calculation settings
    factor_window_days: int = 252  # Trading days in a year
    
    # Strategy settings
    max_positions: int = 10
    rebalance_frequency: str = "daily"  # daily, weekly, monthly
    
    # Performance settings
    enable_parallel_backtest: bool = True
    max_workers: int = 4
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8003
    
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

