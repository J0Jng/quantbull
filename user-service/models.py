from datetime import datetime
from typing import Generator, Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select

from core.config import settings


def _get_connect_args() -> dict:
    if settings.database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


auth_engine = create_engine(settings.database_url, connect_args=_get_connect_args(), echo=False)


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    password_hash: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


def init_db() -> None:
    """Create tables if they do not exist."""
    SQLModel.metadata.create_all(auth_engine)


def get_session() -> Generator[Session, None, None]:
    with Session(auth_engine) as session:
        yield session


def get_user_by_username(session: Session, username: str) -> Optional[User]:
    stmt = select(User).where(User.username == username)
    return session.exec(stmt).first()


def create_user(session: Session, username: str, password_hash: str) -> User:
    user = User(username=username, password_hash=password_hash)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def seed_admin_user(session: Session, username: str, password_hash: str) -> None:
    existing = get_user_by_username(session, username)
    if existing:
        return
    create_user(session, username, password_hash)
