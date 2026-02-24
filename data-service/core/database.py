from typing import AsyncGenerator,Generator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker,Session
from sqlmodel import SQLModel, create_engine, Session

from core.config import settings

# 同步引擎（用于 SQLModel）
sync_database_url = settings.sync_database_url
engine = create_engine(sync_database_url, echo=True)

# 异步引擎（用于异步操作）
async_database_url = settings.database_url
async_engine = create_async_engine(async_database_url, echo=True)

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


def get_session() -> Generator[Session, None, None]:
    """同步数据库会话依赖注入"""
    with SessionLocal() as session:
        yield session


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """异步数据库会话依赖注入"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            # Ensure any open transaction is cleaned up before returning to pool.
            if session.in_transaction():
                await session.rollback()


async def init_db() -> None:
    """初始化数据库表（修复异步环境下的同步操作问题）"""
    import logging
    from sqlalchemy import inspect
    import asyncio  # 新增导入
    
    logger = logging.getLogger(__name__)
    
    try:
        # 导入所有模型以确保表被注册
        import models
        
        # 关键修复：在异步环境中通过线程池执行同步操作
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,  # 使用默认线程池
            lambda: SQLModel.metadata.create_all(engine)  # 同步操作封装为lambda
        )
        
        logger.info("数据库表初始化成功")
    except Exception as e:
        msg = str(e).lower()
        if "already exists" in msg or "duplicate" in msg:
            logger.info("数据库初始化：检测到已存在的对象（索引/表），已跳过重复创建")
        else:
            logger.warning(f"数据库初始化失败（应用将继续运行）: {e}")
            logger.warning("请确保 PostgreSQL 服务已启动，或检查 DATABASE_URL 配置")

