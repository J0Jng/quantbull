"""
商品管理路由
提供商品的 CRUD 接口，支持管理员管理和普通用户浏览
数据存储在数据库中
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlmodel import Session

from auth.jwt import verify_token
from models import (
    get_session, 
    get_user_by_username, 
    User, 
    Product,
    ProductType,
    get_product_by_id,
    get_products as db_get_products,
    create_product as db_create_product,
    update_product as db_update_product,
    delete_product as db_delete_product
)

router = APIRouter(prefix="/api/products", tags=["products"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


# ==================== Schemas ====================

class Envelope(BaseModel):
    code: int
    message: str
    data: dict | list | None


class CreateProductRequest(BaseModel):
    type: ProductType
    name: str
    price: float
    original_price: Optional[float] = None  # 原价
    img: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[str] = None  # 课时/时长
    target_audience: Optional[str] = None  # 适合人群
    learning_method: Optional[str] = None  # 学习方式
    start_time: Optional[str] = None  # 开课时间
    instructor: Optional[str] = None  # 讲师
    outline: Optional[str] = None  # 课程大纲（JSON字符串）
    detail_content: Optional[str] = None  # 详细介绍
    faq: Optional[str] = None  # 常见问题（JSON字符串）
    is_active: bool = True


class UpdateProductRequest(BaseModel):
    type: Optional[ProductType] = None
    name: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    img: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[str] = None
    target_audience: Optional[str] = None
    learning_method: Optional[str] = None
    start_time: Optional[str] = None
    instructor: Optional[str] = None
    outline: Optional[str] = None
    detail_content: Optional[str] = None
    faq: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: str
    type: str
    name: str
    price: float
    original_price: Optional[float]
    img: Optional[str]
    description: Optional[str]
    duration: Optional[str]
    target_audience: Optional[str]
    learning_method: Optional[str]
    start_time: Optional[str]
    instructor: Optional[str]
    outline: Optional[str]
    detail_content: Optional[str]
    faq: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str

    @classmethod
    def from_product(cls, product: Product) -> "ProductResponse":
        return cls(
            id=product.id,
            type=product.type,
            name=product.name,
            price=product.price,
            original_price=product.original_price,
            img=product.img,
            description=product.description,
            duration=product.duration,
            target_audience=product.target_audience,
            learning_method=product.learning_method,
            start_time=product.start_time,
            instructor=product.instructor,
            outline=product.outline,
            detail_content=product.detail_content,
            faq=product.faq,
            is_active=product.is_active,
            created_at=product.created_at.isoformat() + "Z",
            updated_at=product.updated_at.isoformat() + "Z"
        )


# ==================== Dependencies ====================

def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> Optional[User]:
    """可选的用户认证：返回用户对象或 None"""
    if not token:
        return None
    payload = verify_token(token)
    if not payload:
        return None
    user = get_user_by_username(session, payload["username"])
    return user


def require_admin(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> User:
    """依赖函数：要求当前用户必须是管理员"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token"
        )
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token"
        )
    
    user = get_user_by_username(session, payload["username"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user not found"
        )
    
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="forbidden"
        )
    
    return user


# ==================== Endpoints ====================

@router.get("")
async def list_products(
    type: Optional[ProductType] = Query(None, description="过滤商品类型"),
    include_inactive: bool = Query(False, description="是否包含下架商品（仅管理员可用）"),
    limit: int = Query(100, ge=1, le=500, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    session: Session = Depends(get_session)
) -> Envelope:
    """
    获取商品列表
    - 允许匿名访问
    - include_inactive 参数仅对管理员有效
    """
    # 非管理员时强制 include_inactive = False
    is_admin = current_user and current_user.role == "admin"
    if not is_admin:
        include_inactive = False
    
    # 从数据库获取商品
    products = db_get_products(
        session,
        product_type=type.value if type else None,
        include_inactive=include_inactive,
        limit=limit,
        offset=offset
    )
    
    # 转换为响应格式
    product_list = [ProductResponse.from_product(p).model_dump() for p in products]
    
    return Envelope(code=0, message="ok", data=product_list)


@router.get("/{product_id}")
async def get_product(
    product_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    session: Session = Depends(get_session)
) -> Envelope:
    """
    获取单个商品详情
    - 允许匿名访问
    - 下架商品仅管理员可见
    """
    product = get_product_by_id(session, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="product not found"
        )
    
    # 非管理员不能查看下架商品
    is_admin = current_user and current_user.role == "admin"
    if not product.is_active and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="product not found"
        )
    
    return Envelope(code=0, message="ok", data=ProductResponse.from_product(product).model_dump())


@router.post("")
async def create_product(
    request: CreateProductRequest,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session)
) -> Envelope:
    """
    创建商品（仅管理员）
    """
    product = db_create_product(
        session,
        product_type=request.type.value,
        name=request.name,
        price=request.price,
        img=request.img,
        description=request.description,
        is_active=request.is_active,
        original_price=request.original_price,
        duration=request.duration,
        target_audience=request.target_audience,
        learning_method=request.learning_method,
        start_time=request.start_time,
        instructor=request.instructor,
        outline=request.outline,
        detail_content=request.detail_content,
        faq=request.faq
    )
    
    return Envelope(code=0, message="ok", data=ProductResponse.from_product(product).model_dump())


@router.patch("/{product_id}")
async def update_product(
    product_id: str,
    request: UpdateProductRequest,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session)
) -> Envelope:
    """
    更新商品（仅管理员）
    - 支持部分更新
    """
    product = get_product_by_id(session, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="product not found"
        )
    
    # 构建更新参数
    update_data = request.model_dump(exclude_unset=True)
    if "type" in update_data and update_data["type"] is not None:
        update_data["type"] = update_data["type"].value
    
    product = db_update_product(session, product, **update_data)
    
    return Envelope(code=0, message="ok", data=ProductResponse.from_product(product).model_dump())


@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session)
) -> Envelope:
    """
    删除商品（仅管理员）
    - 软删除：将 is_active 设为 False
    """
    product = get_product_by_id(session, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="product not found"
        )
    
    # 软删除
    db_delete_product(session, product)
    
    return Envelope(code=0, message="ok", data={"deleted_product_id": product_id})
