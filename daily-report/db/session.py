"""数据库会话管理"""
import re
import time

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import OperationalError, ProgrammingError
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
    schema = settings.postgres_schema or "public"
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # 连接前检查连接是否有效
        pool_size=10,
        max_overflow=20,
        echo=settings.env == "local",  # 开发环境打印 SQL
        connect_args={"options": f"-c search_path={schema}"},
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
    def _validate_schema_name(name: str) -> str:
        name = (name or "").strip() or "public"
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            raise ValueError(f"非法的 POSTGRES_SCHEMA: {name!r}")
        return name

    # Postgres 在容器编排里可能尚未 ready；这里做有限重试避免启动后才报 UndefinedTable
    max_attempts = 8 if settings.db_type == "postgresql" else 1
    delay_seconds = 1.0

    for attempt in range(1, max_attempts + 1):
        try:
            # 导入所有模型以确保它们被注册到 Base.metadata
            from models import CompanyResearchReport, DailyInvestmentReport  # noqa: F401

            if settings.db_type == "postgresql":
                schema = _validate_schema_name(settings.postgres_schema)
                with engine.begin() as connection:
                    try:
                        connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
                    except ProgrammingError as e:
                        # 最小权限部署时，应用用户可能没有数据库级 CREATE 权限。
                        # 若 schema 已由管理员预先创建，则这里允许继续；后续 create_all 会在 schema 不存在时失败。
                        message = str(e).lower()
                        if "permission denied for database" in message or "insufficientprivilege" in message:
                            logger.warning(
                                "缺少创建 schema 的数据库级权限，跳过 CREATE SCHEMA；将继续尝试在现有 schema=%s 建表。错误: %s",
                                schema,
                                str(e).strip().splitlines()[-1] if str(e).strip() else "ProgrammingError",
                            )
                        else:
                            raise

            Base.metadata.create_all(bind=engine)

            db_type_name = {
                "postgresql": "PostgreSQL",
                "sqlite": "SQLite",
                "memory": "SQLite (内存)",
            }.get(settings.db_type, settings.db_type)
            logger.info(
                "数据库表创建成功 (%s, db=%s, schema=%s)",
                db_type_name,
                settings.postgres_db if settings.db_type == "postgresql" else settings.sqlite_path,
                settings.postgres_schema if settings.db_type == "postgresql" else "-",
            )
            return
        except OperationalError as e:
            # 仅对连接类错误重试；其他错误直接抛出
            if attempt >= max_attempts:
                logger.error("数据库初始化失败（已重试 %s 次）: %s", attempt, e, exc_info=True)
                raise
            logger.warning(
                "数据库暂不可用，%s/%s 秒后重试（%s/%s）: %s",
                delay_seconds,
                int(delay_seconds),
                attempt,
                max_attempts,
                str(e).strip().splitlines()[-1] if str(e).strip() else "OperationalError",
            )
            time.sleep(delay_seconds)
            delay_seconds = min(delay_seconds * 1.8, 8.0)
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}", exc_info=True)
            # 开发环境允许继续运行（使用内存存储）
            if settings.env == "local" and settings.db_type != "memory":
                logger.warning("数据库初始化失败，但处于 local 环境，继续启动（后续接口可能报表不存在）")
                return
            raise
