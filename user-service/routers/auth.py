from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session

from auth.dependencies import get_current_user, require_admin
from auth.security import create_access_token, hash_password, verify_password
from models import User, create_user as create_user_model, get_session, get_user_by_username
from routers.admin import validate_password, validate_username

router = APIRouter(prefix="/api/auth", tags=["auth"])


class Envelope(BaseModel):
    code: int
    message: str
    data: dict | list | None


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    phone: Optional[str] = None


class UserInfo(BaseModel):
    id: int
    username: str
    role: str
    email: Optional[str] = None
    phone: Optional[str] = None

    @classmethod
    def from_user(cls, user: User) -> "UserInfo":
        if user.id is None:
            raise ValueError("User ID cannot be None")
        return cls(
            id=user.id,
            username=user.username,
            role=user.role,
            email=user.email,
            phone=user.phone,
        )


@router.post("/login")
@router.post("/login/json")
async def login_json(payload: LoginRequest, session: Session = Depends(get_session)) -> Envelope:
    user = get_user_by_username(session, payload.username)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid username or password")
    if user.id is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="invalid user id")

    token = create_access_token(subject=user.username, user_id=user.id, role=user.role)
    return Envelope(
        code=0,
        message="ok",
        data={
            "access_token": token,
            "token_type": "bearer",
            "user": UserInfo.from_user(user).model_dump(),
        },
    )


@router.get("/me")
async def me(current_user: User = Depends(get_current_user)) -> Envelope:
    return Envelope(code=0, message="ok", data=UserInfo.from_user(current_user).model_dump())


@router.get("/verify")
async def verify(current_user: User = Depends(get_current_user)) -> Envelope:
    return Envelope(
        code=0,
        message="ok",
        data={
            "valid": True,
            "user": UserInfo.from_user(current_user).model_dump(),
        },
    )


@router.post("/register")
async def register_by_admin(
    payload: RegisterRequest,
    session: Session = Depends(get_session),
    _: User = Depends(require_admin),
) -> Envelope:
    validate_username(payload.username)
    validate_password(payload.password)
    if get_user_by_username(session, payload.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user already exists")

    user = create_user_model(
        session,
        payload.username,
        hash_password(payload.password),
        role="user",
        email=payload.email,
        phone=payload.phone,
    )
    return Envelope(code=0, message="ok", data=UserInfo.from_user(user).model_dump())