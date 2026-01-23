from datetime import datetime
from typing import Generator, Optional, List
from enum import Enum
import uuid

from sqlmodel import Field, Session, SQLModel, create_engine, select

from core.config import settings


def _get_connect_args() -> dict:
    if settings.database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


auth_engine = create_engine(settings.database_url, connect_args=_get_connect_args(), echo=False)


# ==================== Enums ====================

class ProductType(str, Enum):
    factor = "factor"
    strategy = "strategy"
    fund = "fund"
    advisor = "advisor"
    course = "course"
    book = "book"
    talent = "talent"


# ==================== Models ====================

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    password_hash: str = Field(nullable=False)
    role: str = Field(default="user", nullable=False)
    ai_tokens: int = Field(default=1000, nullable=False)
    email: Optional[str] = Field(default=None)
    phone: Optional[str] = Field(default=None)
    qualified_investor: bool = Field(default=False, nullable=False)
    investor_certified_at: Optional[datetime] = Field(default=None)
    investor_risk_level: Optional[str] = Field(default=None)
    investor_asset_type: Optional[str] = Field(default=None)
    investor_tags: Optional[str] = Field(default=None)
    investor_real_name: Optional[str] = Field(default=None)
    investor_id_card_hash: Optional[str] = Field(default=None)
    investor_id_card_last4: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Product(SQLModel, table=True):
    """商品模型"""
    id: str = Field(default_factory=lambda: f"prod_{uuid.uuid4().hex[:24]}", primary_key=True)
    type: str = Field(index=True, nullable=False)  # ProductType enum value
    name: str = Field(nullable=False)
    price: float = Field(nullable=False)
    original_price: Optional[float] = Field(default=None)  # 原价
    img: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    
    # 课程/商品详情字段
    duration: Optional[str] = Field(default=None)  # 课时/时长，如 "12课时（每课时45分钟）"
    target_audience: Optional[str] = Field(default=None)  # 适合人群
    learning_method: Optional[str] = Field(default=None)  # 学习方式
    start_time: Optional[str] = Field(default=None)  # 开课时间
    instructor: Optional[str] = Field(default=None)  # 讲师信息
    outline: Optional[str] = Field(default=None)  # 课程大纲（JSON字符串）
    detail_content: Optional[str] = Field(default=None)  # 课程/商品详细介绍
    faq: Optional[str] = Field(default=None)  # 常见问题（JSON字符串）
    
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


def init_db() -> None:
    """Create tables if they do not exist."""
    SQLModel.metadata.create_all(auth_engine)


def get_session() -> Generator[Session, None, None]:
    with Session(auth_engine) as session:
        yield session


def get_user_by_username(session: Session, username: str) -> Optional[User]:
    stmt = select(User).where(User.username == username)
    return session.exec(stmt).first()


def create_user(
    session: Session,
    username: str,
    password_hash: str,
    role: str = "user",
    email: Optional[str] = None,
    phone: Optional[str] = None,
) -> User:
    user = User(
        username=username,
        password_hash=password_hash,
        role=role,
        ai_tokens=settings.default_ai_tokens,
        email=email,
        phone=phone,
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


def migrate_product_detail_columns() -> None:
    """迁移：为 product 表添加商品详情相关列（如果不存在）"""
    from sqlalchemy import text, inspect
    
    new_columns = [
        ("original_price", "REAL", None),
        ("duration", "TEXT", None),
        ("target_audience", "TEXT", None),
        ("learning_method", "TEXT", None),
        ("start_time", "TEXT", None),
        ("instructor", "TEXT", None),
        ("outline", "TEXT", None),
        ("detail_content", "TEXT", None),
        ("faq", "TEXT", None),
    ]
    
    try:
        with auth_engine.connect() as conn:
            inspector = inspect(auth_engine)
            try:
                columns = [col['name'] for col in inspector.get_columns('product')]
            except Exception:
                # 表不存在，跳过迁移
                return
            
            for col_name, col_type, default_val in new_columns:
                if col_name not in columns:
                    try:
                        if settings.database_url.startswith("sqlite"):
                            if default_val is not None:
                                conn.execute(text(f"ALTER TABLE product ADD COLUMN {col_name} {col_type} DEFAULT {default_val}"))
                            else:
                                conn.execute(text(f"ALTER TABLE product ADD COLUMN {col_name} {col_type}"))
                        else:
                            # PostgreSQL
                            pg_type = "DOUBLE PRECISION" if col_type == "REAL" else "VARCHAR"
                            if default_val is not None:
                                conn.execute(text(f"ALTER TABLE product ADD COLUMN {col_name} {pg_type} DEFAULT {default_val}"))
                            else:
                                conn.execute(text(f"ALTER TABLE product ADD COLUMN {col_name} {pg_type}"))
                        conn.commit()
                        print(f"Migration: Added {col_name} column to product table")
                    except Exception as e:
                        print(f"Migration note for {col_name}: {e}")
    except Exception as e:
        print(f"Product migration note: {e}")


def migrate_add_investor_columns() -> None:
    """迁移：为 user 表添加合格投资者相关列（如果不存在）"""
    from sqlalchemy import text, inspect

    new_columns = [
        ("qualified_investor", "BOOLEAN", "0"),
        ("investor_certified_at", "TEXT", None),
        ("investor_risk_level", "TEXT", None),
        ("investor_asset_type", "TEXT", None),
        ("investor_tags", "TEXT", None),
        ("investor_real_name", "TEXT", None),
        ("investor_id_card_hash", "TEXT", None),
        ("investor_id_card_last4", "TEXT", None),
    ]

    try:
        with auth_engine.connect() as conn:
            inspector = inspect(auth_engine)
            columns = [col['name'] for col in inspector.get_columns('user')]

            for col_name, col_type, default_val in new_columns:
                if col_name in columns:
                    continue

                try:
                    if settings.database_url.startswith("sqlite"):
                        if default_val is not None:
                            conn.execute(text(f"ALTER TABLE user ADD COLUMN {col_name} {col_type} NOT NULL DEFAULT {default_val}"))
                        else:
                            conn.execute(text(f"ALTER TABLE user ADD COLUMN {col_name} {col_type}"))
                    else:
                        # PostgreSQL
                        pg_type = "BOOLEAN" if col_type == "BOOLEAN" else "TIMESTAMP" if col_name == "investor_certified_at" else "VARCHAR"
                        if default_val is not None:
                            pg_default = "FALSE" if col_type == "BOOLEAN" else default_val
                            conn.execute(text(f"ALTER TABLE \"user\" ADD COLUMN {col_name} {pg_type} NOT NULL DEFAULT {pg_default}"))
                        else:
                            conn.execute(text(f"ALTER TABLE \"user\" ADD COLUMN {col_name} {pg_type}"))
                    conn.commit()
                    print(f"Migration: Added {col_name} column to user table")
                except Exception as e:
                    conn.rollback()
                    print(f"Migration note for {col_name}: {e}")
    except Exception as e:
        print(f"Investor migration note: {e}")


def migrate_add_user_profile_columns() -> None:
    """迁移：为 user 表添加 email/phone 列（如果不存在）"""
    from sqlalchemy import text, inspect

    new_columns = [
        ("email", "TEXT"),
        ("phone", "TEXT"),
    ]

    try:
        with auth_engine.connect() as conn:
            inspector = inspect(auth_engine)
            columns = [col['name'] for col in inspector.get_columns('user')]

            for col_name, col_type in new_columns:
                if col_name in columns:
                    continue
                try:
                    if settings.database_url.startswith("sqlite"):
                        conn.execute(text(f"ALTER TABLE user ADD COLUMN {col_name} {col_type}"))
                    else:
                        conn.execute(text(f"ALTER TABLE \"user\" ADD COLUMN {col_name} VARCHAR"))
                    conn.commit()
                    print(f"Migration: Added {col_name} column to user table")
                except Exception as e:
                    conn.rollback()
                    print(f"Migration note for {col_name}: {e}")
    except Exception as e:
        print(f"User profile migration note: {e}")


# ==================== Product CRUD ====================

def get_product_by_id(session: Session, product_id: str) -> Optional[Product]:
    """根据 ID 获取商品"""
    return session.get(Product, product_id)


def get_products(
    session: Session,
    product_type: Optional[str] = None,
    include_inactive: bool = False,
    limit: int = 100,
    offset: int = 0
) -> List[Product]:
    """获取商品列表"""
    stmt = select(Product)
    
    if not include_inactive:
        stmt = stmt.where(Product.is_active == True)
    
    if product_type:
        stmt = stmt.where(Product.type == product_type)
    
    stmt = stmt.offset(offset).limit(limit)
    return list(session.exec(stmt).all())


def create_product(
    session: Session,
    product_type: str,
    name: str,
    price: float,
    img: Optional[str] = None,
    description: Optional[str] = None,
    is_active: bool = True,
    original_price: Optional[float] = None,
    duration: Optional[str] = None,
    target_audience: Optional[str] = None,
    learning_method: Optional[str] = None,
    start_time: Optional[str] = None,
    instructor: Optional[str] = None,
    outline: Optional[str] = None,
    detail_content: Optional[str] = None,
    faq: Optional[str] = None
) -> Product:
    """创建商品"""
    now = datetime.utcnow()
    product = Product(
        type=product_type,
        name=name,
        price=price,
        img=img,
        description=description,
        is_active=is_active,
        original_price=original_price,
        duration=duration,
        target_audience=target_audience,
        learning_method=learning_method,
        start_time=start_time,
        instructor=instructor,
        outline=outline,
        detail_content=detail_content,
        faq=faq,
        created_at=now,
        updated_at=now
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def update_product(
    session: Session,
    product: Product,
    **kwargs
) -> Product:
    """更新商品"""
    for key, value in kwargs.items():
        if hasattr(product, key) and value is not None:
            setattr(product, key, value)
    product.updated_at = datetime.utcnow()
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def delete_product(session: Session, product: Product) -> None:
    """软删除商品（设置 is_active = False）"""
    product.is_active = False
    product.updated_at = datetime.utcnow()
    session.add(product)
    session.commit()


def seed_products(session: Session) -> None:
    """初始化示例商品数据（如果数据库为空）"""
    # 检查是否已有商品
    existing = session.exec(select(Product).limit(1)).first()
    if existing:
        return
    
    sample_products = [
        # 因子
        {"type": "factor", "name": "量价因子合集 - 超100个经典A股量价因子（可直接回测）", "price": 1299.0, "img": "https://picsum.photos/400/300?random=1", "description": "包含100+个经过验证的A股量价因子，涵盖动量、波动率、换手率等多个维度。"},
        {"type": "factor", "name": "基本面因子库 - 财务/估值/成长类因子（附计算代码）", "price": 999.0, "img": "https://picsum.photos/400/300?random=2", "description": "完整的基本面因子库，包含ROE、PE、PB等财务指标因子。"},
        {"type": "factor", "name": "另类因子 - 舆情/资金流/产业链因子（实时更新）", "price": 1599.0, "img": "https://picsum.photos/400/300?random=3", "description": "基于另类数据的因子，包含新闻舆情、资金流向、产业链关联等。"},
        {"type": "factor", "name": "因子挖掘工具 - 自动化因子生成与有效性检验平台", "price": 2999.0, "img": "https://picsum.photos/400/300?random=4", "description": "自动化因子挖掘平台，支持因子生成、回测、有效性检验。"},
        # 策略
        {"type": "strategy", "name": "双均线择时策略 - 年化收益25%+（附Python源码）", "price": 699.0, "img": "https://picsum.photos/400/300?random=5", "description": "经典双均线策略，附带完整Python实现和历史回测结果。"},
        {"type": "strategy", "name": "多因子选股策略 - 沪深300增强（回测胜率78%）", "price": 1899.0, "img": "https://picsum.photos/400/300?random=6", "description": "多因子选股策略，经过严格的历史回测验证。"},
        {"type": "strategy", "name": "ETF套利策略 - 无风险套利（日内交易版）", "price": 1499.0, "img": "https://picsum.photos/400/300?random=7", "description": "ETF套利策略，利用ETF与成分股之间的价差进行套利。"},
        {"type": "strategy", "name": "商品CTA策略 - 趋势跟踪（适配期货市场）", "price": 2499.0, "img": "https://picsum.photos/400/300?random=8", "description": "商品期货CTA策略，基于趋势跟踪的量化交易策略。"},
        # 基金
        {"type": "fund", "name": "量化增强专户基金 - 最低起投100万", "price": 1000000.0, "img": "https://picsum.photos/400/300?random=9", "description": "专业量化增强策略，仅限合格投资者。"},
        {"type": "fund", "name": "量化FOF基金 - 多策略组合（年化18%）", "price": 500000.0, "img": "https://picsum.photos/400/300?random=10", "description": "多策略组合FOF基金，分散风险，稳健收益。"},
        # 投顾
        {"type": "advisor", "name": "1v1量化投顾服务 - 定制化资产配置方案（月付）", "price": 3999.0, "img": "https://picsum.photos/400/300?random=11", "description": "一对一专属投顾服务，提供定制化资产配置方案。"},
        {"type": "advisor", "name": "量化组合投顾 - 季度调仓（年付优惠）", "price": 19999.0, "img": "https://picsum.photos/400/300?random=12", "description": "专业量化组合投顾，季度调仓，年付优惠。"},
        {"type": "advisor", "name": "个性化策略定制 - 按需开发量化模型", "price": 50000.0, "img": "https://picsum.photos/400/300?random=13", "description": "根据客户需求定制开发量化交易模型。"},
        {"type": "advisor", "name": "量化风控咨询 - 策略风险评估与优化", "price": 8999.0, "img": "https://picsum.photos/400/300?random=14", "description": "专业量化风控咨询，策略风险评估与优化建议。"},
        # 课程
        {"type": "course", "name": "Python量化入门到精通 - 零基础学量化交易", "price": 599.0, "img": "https://picsum.photos/400/300?random=15", "description": "系统性课程，从零开始学习Python量化交易。"},
        {"type": "course", "name": "量化因子开发实战 - 从0到1构建有效因子", "price": 899.0, "img": "https://picsum.photos/400/300?random=16", "description": "实战课程，教你如何开发和验证量化因子。"},
        {"type": "course", "name": "量化策略回测实战 - 避免过拟合（附案例）", "price": 799.0, "img": "https://picsum.photos/400/300?random=17", "description": "回测实战课程，重点讲解如何避免过拟合。"},
        {"type": "course", "name": "量化策略实盘部署 - 自动交易对接教程", "price": 1299.0, "img": "https://picsum.photos/400/300?random=18", "description": "实盘部署教程，教你如何将策略部署到实盘环境。"},
        # 书籍
        {"type": "book", "name": "《量化投资分析（原书第3版）》- 精装版+配套源码", "price": 168.0, "img": "https://picsum.photos/400/300?random=19", "description": "量化投资经典教材，附配套源码。"},
        {"type": "book", "name": "《Python量化交易实战》- 进阶版（附实战案例）", "price": 128.0, "img": "https://picsum.photos/400/300?random=20", "description": "Python量化交易进阶书籍，附实战案例。"},
        {"type": "book", "name": "《因子投资：方法与实践》- 业内经典教材", "price": 148.0, "img": "https://picsum.photos/400/300?random=21", "description": "因子投资经典教材，业内人士必读。"},
        {"type": "book", "name": "《量化风控：模型与实践》- 金融机构内部教材", "price": 188.0, "img": "https://picsum.photos/400/300?random=22", "description": "量化风控专业教材，金融机构内部培训用书。"},
        # 人才
        {"type": "talent", "name": "量化研究员推荐 - 头部券商背景（全职/兼职）", "price": 5000.0, "img": "https://picsum.photos/400/300?random=23", "description": "推荐优质量化研究员人才，头部券商背景。"},
        {"type": "talent", "name": "量化人才猎头服务 - 定向猎聘量化总监/工程师", "price": 30000.0, "img": "https://picsum.photos/400/300?random=24", "description": "专业量化人才猎头服务，定向猎聘高端人才。"},
        {"type": "talent", "name": "企业量化人才内训 - 定制化培训方案", "price": 50000.0, "img": "https://picsum.photos/400/300?random=25", "description": "企业量化人才内训服务，提供定制化培训方案。"},
        {"type": "talent", "name": "量化实习推荐 - 公募/私募/券商实习岗位", "price": 1999.0, "img": "https://picsum.photos/400/300?random=26", "description": "量化实习岗位推荐，涵盖公募、私募、券商。"},
    ]
    
    for item in sample_products:
        create_product(
            session,
            product_type=item["type"],
            name=item["name"],
            price=item["price"],
            img=item.get("img"),
            description=item.get("description"),
            is_active=True
        )
    
    print(f"Seeded {len(sample_products)} products into database.")
