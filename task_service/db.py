from contextlib import contextmanager
from sqlmodel import SQLModel, Session, create_engine

from .config import settings


engine = create_engine(settings.database_url, echo=False, pool_pre_ping=True, pool_size=5, max_overflow=10)


def init_db() -> None:
    """Create tables if they do not exist."""
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session() -> Session:
    with Session(engine) as session:
        yield session
