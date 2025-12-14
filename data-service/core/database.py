from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine, Session

from core.config import settings


# 同步引擎（用于 SQLModel）
sync_database_url = settings.database_url.replace("postgresql+psycopg2://", "postgresql://")
engine = create_engine(sync_database_url, echo=False)

# 异步引擎（用于异步操作）
async_database_url = settings.database_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")
async_engine = create_async_engine(async_database_url, echo=False)

# 同步会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


def get_session() -> Session:
    """同步数据库会话依赖注入"""
    with SessionLocal() as session:
        yield session


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """异步数据库会话依赖注入"""
    async with AsyncSessionLocal() as session:
        yield session


def init_db() -> None:
    """初始化数据库表（失败时仅记录警告，不阻止应用启动）"""
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # 导入所有模型以确保表被注册
        from models import RealtimeQuote, DailyQuote  # noqa: F401
        
        SQLModel.metadata.create_all(engine)
        logger.info("数据库表初始化成功")
    except Exception as e:
        logger.warning(f"数据库初始化失败（应用将继续运行）: {e}")
        logger.warning("请确保 PostgreSQL 服务已启动，或检查 DATABASE_URL 配置")

