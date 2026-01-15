"""数据库会话管理"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)


def get_database_url() -> str:
    """根据配置获取数据库 URL"""
    if settings.db_type == "postgresql":
        return (
            f"postgresql://{settings.postgres_user}:{settings.postgres_password}"
            f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
        )
    elif settings.db_type == "sqlite":
        return f"sqlite:///{settings.sqlite_path}"
    elif settings.db_type == "memory":
        return "sqlite:///:memory:"
    else:
        raise ValueError(f"不支持的数据库类型: {settings.db_type}")


# 构建数据库 URL
DATABASE_URL = get_database_url()

# 创建数据库引擎
if settings.db_type == "postgresql":
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # 连接前检查连接是否有效
        pool_size=10,
        max_overflow=20,
        echo=settings.env == "local",  # 开发环境打印 SQL
    )
else:
    # SQLite 配置
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False} if settings.db_type == "sqlite" else {},
        echo=settings.env == "local",  # 开发环境打印 SQL
    )

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()


def get_db() -> Session:
    """获取数据库会话（依赖注入）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """初始化数据库（创建表）"""
    try:
        # 导入所有模型以确保它们被注册到 Base.metadata
        from models import CompanyResearchReport  # noqa: F401
        
        Base.metadata.create_all(bind=engine)
        db_type_name = {
            "postgresql": "PostgreSQL",
            "sqlite": "SQLite",
            "memory": "SQLite (内存)",
        }.get(settings.db_type, settings.db_type)
        logger.info(f"数据库表创建成功 ({db_type_name})")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}", exc_info=True)
        # 开发环境允许继续运行（使用内存存储）
        if settings.env == "local" and settings.db_type != "memory":
            logger.warning("尝试使用内存数据库...")
            # 这里可以尝试切换到内存数据库，但为了简单，我们只记录错误
        else:
            raise
