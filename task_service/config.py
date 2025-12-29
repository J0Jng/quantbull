from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Service settings driven by environment variables."""

    model_config = SettingsConfigDict(env_prefix="TASK_SERVICE_", case_sensitive=False)

    database_url: str = Field(
        default="postgresql+psycopg://quantbull:change_me@postgres:5432/quantbull_db",
        description="SQLAlchemy URL for PostgreSQL used to persist task metadata.",
    )
    redis_url: str = Field(
        default="redis://redis:6379/0",
        description="Redis URL used as Celery broker and result backend.",
    )
    celery_broker_url: str | None = Field(
        default=None, description="Optional broker override; falls back to redis_url."
    )
    celery_result_backend: str | None = Field(
        default=None, description="Optional result backend override; falls back to redis_url."
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
