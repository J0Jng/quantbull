from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlmodel import Session, select

from auth.jwt import hash_password, verify_token
from models import User, get_session, get_user_by_username, create_user as create_user_model

router = APIRouter(prefix="/api/admin", tags=["admin"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class Envelope(BaseModel):
    code: int
    message: str
    data: dict | list


class UserCreateRequest(BaseModel):
    username: str
    password: str
    role: str = "user"


class UserUpdateRequest(BaseModel):
    password: Optional[str] = None
    role: Optional[str] = None
    ai_tokens: Optional[int] = None


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    ai_tokens: int
    created_at: str

    @classmethod
    def from_user(cls, user: User) -> "UserResponse":
        if user.id is None:
            raise ValueError("User ID cannot be None")
        return cls(
            id=user.id,
            username=user.username,
            role=user.role,
            ai_tokens=user.ai_tokens,
            created_at=user.created_at.isoformat(),
        )


def require_admin(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    """依赖函数：要求当前用户必须是管理员"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    
    user = get_user_by_username(session, payload["username"])
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user not found")
    
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
    
    return user


@router.get("/users")
async def list_users(
    limit: int = 100,
    offset: int = 0,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session),
) -> Envelope:
    """列出所有用户（分页）"""
    stmt = select(User).limit(limit).offset(offset)
    users = session.exec(stmt).all()
    
    user_list = [UserResponse.from_user(u).model_dump() for u in users]
    
    return Envelope(code=0, message="ok", data=user_list)


@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session),
) -> Envelope:
    """获取单个用户详情"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    
    return Envelope(code=0, message="ok", data=UserResponse.from_user(user).model_dump())


@router.post("/users")
async def create_user_by_admin(
    payload: UserCreateRequest,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session),
) -> Envelope:
    """创建新用户"""
    if get_user_by_username(session, payload.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user already exists")
    
    password_hash = hash_password(payload.password)
    user = create_user_model(session, payload.username, password_hash, role=payload.role)
    
    return Envelope(code=0, message="ok", data=UserResponse.from_user(user).model_dump())


@router.patch("/users/{user_id}")
async def update_user(
    user_id: int,
    payload: UserUpdateRequest,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session),
) -> Envelope:
    """更新用户（支持重置密码、修改role）"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    
    if payload.password:
        user.password_hash = hash_password(payload.password)
    
    if payload.role is not None:
        user.role = payload.role
    
    if payload.ai_tokens is not None:
        if payload.ai_tokens < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ai_tokens cannot be negative")
        user.ai_tokens = payload.ai_tokens
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return Envelope(code=0, message="ok", data=UserResponse.from_user(user).model_dump())


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session),
) -> Envelope:
    """删除用户（防呆：不允许删除自己）"""
    if admin.id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="cannot delete yourself")
    
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    
    session.delete(user)
    session.commit()
    
    return Envelope(code=0, message="ok", data={"deleted_user_id": user_id})
