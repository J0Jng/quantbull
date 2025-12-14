from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = "local"
    log_level: str = "INFO"
    
    # 数据库配置
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/quantbull"
    
    # Tushare 配置
    tushare_token: str = ""
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

