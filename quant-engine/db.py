from contextlib import contextmanager
from sqlmodel import SQLModel, Session, create_engine

from core.config import settings


def _build_database_url() -> str:
    return (
        f"postgresql+psycopg://{settings.postgres_user}:{settings.postgres_password}"
        f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
    )


engine = create_engine(_build_database_url(), echo=False, pool_pre_ping=True, pool_size=5, max_overflow=10)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session() -> Session:
    with Session(engine) as session:
        yield session
