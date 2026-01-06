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
    role: str = Field(default="user", nullable=False)
    ai_tokens: int = Field(default=1000, nullable=False)
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


def create_user(session: Session, username: str, password_hash: str, role: str = "user") -> User:
    user = User(
        username=username,
        password_hash=password_hash,
        role=role,
        ai_tokens=settings.default_ai_tokens
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def seed_admin_user(session: Session, username: str, password_hash: str) -> None:
    existing = get_user_by_username(session, username)
    if existing:
        # 确保已存在的 admin 用户拥有 admin 角色
        if existing.role != "admin":
            existing.role = "admin"
            session.add(existing)
            session.commit()
        return
    create_user(session, username, password_hash, role="admin")


def migrate_add_role_column() -> None:
    """迁移：为 user 表添加 role 列（如果不存在）"""
    from sqlalchemy import text, inspect
    
    try:
        with auth_engine.connect() as conn:
            # 检查 role 列是否存在
            inspector = inspect(auth_engine)
            columns = [col['name'] for col in inspector.get_columns('user')]
            
            if "role" not in columns:
                # 根据数据库类型执行不同的 ALTER TABLE 语句
                if settings.database_url.startswith("sqlite"):
                    conn.execute(text("ALTER TABLE user ADD COLUMN role TEXT NOT NULL DEFAULT 'user'"))
                else:
                    # PostgreSQL 和其他数据库
                    conn.execute(text("ALTER TABLE \"user\" ADD COLUMN role VARCHAR NOT NULL DEFAULT 'user'"))
                conn.commit()
    except Exception as e:
        # 如果列已存在或其他错误，记录但不中断启动
        print(f"Migration note: {e}")


def migrate_add_ai_tokens_column() -> None:
    """迁移：为 user 表添加 ai_tokens 列（如果不存在）"""
    from sqlalchemy import text, inspect
    
    try:
        with auth_engine.connect() as conn:
            # 检查 ai_tokens 列是否存在
            inspector = inspect(auth_engine)
            columns = [col['name'] for col in inspector.get_columns('user')]
            
            if "ai_tokens" not in columns:
                default_tokens = settings.default_ai_tokens
                # 根据数据库类型执行不同的 ALTER TABLE 语句
                if settings.database_url.startswith("sqlite"):
                    conn.execute(text(f"ALTER TABLE user ADD COLUMN ai_tokens INTEGER NOT NULL DEFAULT {default_tokens}"))
                else:
                    # PostgreSQL 和其他数据库
                    conn.execute(text(f"ALTER TABLE \"user\" ADD COLUMN ai_tokens INTEGER NOT NULL DEFAULT {default_tokens}"))
                conn.commit()
                print(f"Migration: Added ai_tokens column with default value {default_tokens}")
    except Exception as e:
        # 如果列已存在或其他错误，记录但不中断启动
        print(f"Migration note: {e}")
