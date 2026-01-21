from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AliasChoices


class Settings(BaseSettings):
    """Quant Engine 服务配置"""
    env: str = "local"
    log_level: str = "INFO"
    
    # 服务端口
    port: int = 8003
    host: str = "0.0.0.0"
    
    # 数据库配置
    database_url: str = Field(
        default="",
        validation_alias=AliasChoices("DATABASE_URL", "QUANT_ENGINE_DATABASE_URL"),
        description="SQLAlchemy URL for PostgreSQL",
    )
    postgres_host: str = ""
    postgres_port: int = 5432
    postgres_user: str = ""
    postgres_password: str = ""
    postgres_db: str = ""
    
    # TDengine 配置（时间序列数据库）
    tdengine_host: str = ""
    tdengine_port: int = 6030
    tdengine_user: str = ""
    tdengine_password: str = ""
    tdengine_database: str = ""
    
    # TDengine REST 接口配置
    tdengine_rest_port: int = 6041
    tdengine_rest_path: str = ""
    tdengine_rest_scheme: str = ""
    tdengine_rest_timeout: float = 10.0
    
    # Redis 配置
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    
    # 回测配置
    default_commission: float = 0.001  # 默认手续费率
    default_slippage: float = 0.0  # 默认滑点
    default_cash: float = 100000.0  # 默认初始资金
    
    # 因子库配置
    factor_cache_ttl: int = 3600  # 因子缓存时间（秒）
    
    # 策略配置
    max_strategy_execution_time: int = 300  # 最大策略执行时间（秒）
    
    # 数据服务配置
    data_service_url: str = "http://data-service:8001"  # data-service 服务地址
    
    # Tushare 配置（可选，用于直接调用 Tushare API）
    tushare_token: str = ""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
