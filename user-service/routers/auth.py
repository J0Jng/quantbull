import re
import time
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from sqlmodel import Session

from auth.jwt import create_access_token, hash_password, hash_phone, verify_password, verify_token
from core.config import settings
from models import create_user, get_session, get_user_by_username

router = APIRouter(prefix="/api/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{3,32}$")
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PHONE_PATTERN = re.compile(r"^[0-9+\-()\s]{7,20}$")

LOGIN_ATTEMPTS = defaultdict(list)
REGISTER_ATTEMPTS = defaultdict(list)
LOGIN_WINDOW_SECONDS = 300
LOGIN_MAX_ATTEMPTS = 5
REGISTER_WINDOW_SECONDS = 3600
REGISTER_MAX_ATTEMPTS = 5


def get_client_ip(request: Request) -> str:
    client_host = request.client.host if request.client else "unknown"
    trust_forwarded = settings.env == "local" or client_host in set(settings.trusted_proxies)
    if trust_forwarded:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return client_host


def _check_rate_limit(store: dict, key: str, window_seconds: int, max_attempts: int, message: str) -> None:
    now = time.time()
    attempts = [ts for ts in store[key] if now - ts < window_seconds]
    store[key] = attempts
    if len(attempts) >= max_attempts:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=message)


def _record_attempt(store: dict, key: str) -> None:
    store[key].append(time.time())


def validate_username(username: str) -> None:
    if not USERNAME_PATTERN.match(username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid username")


def validate_password(password: str) -> None:
    if len(password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="password too short")
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="password too weak")


def validate_phone(phone: str) -> None:
    if not PHONE_PATTERN.match(phone):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid phone")


def validate_email(email: str) -> None:
    if email and not EMAIL_PATTERN.match(email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid email")


class LoginPayload(BaseModel):
    username: str
    password: str


class RegisterPayload(BaseModel):
    username: str
    password: str
    phone: str
    email: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = settings.access_token_expire_seconds
    user_id: int


class Envelope(BaseModel):
    code: int
    message: str
    data: dict


@router.post("/login")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
) -> Envelope:
    client_ip = get_client_ip(request)
    limit_key = f"{client_ip}:{form_data.username}"
    _check_rate_limit(LOGIN_ATTEMPTS, limit_key, LOGIN_WINDOW_SECONDS, LOGIN_MAX_ATTEMPTS, "too many login attempts")
    user = get_user_by_username(session, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        _record_attempt(LOGIN_ATTEMPTS, limit_key)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid username or password")

    if user.id is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="user id is missing")
    LOGIN_ATTEMPTS.pop(limit_key, None)
    token = create_access_token(subject=user.username, user_id=user.id)
    payload = TokenResponse(access_token=token, user_id=user.id)
    return Envelope(code=0, message="ok", data=payload.model_dump())


@router.post("/login/json")
async def login_json(request: Request, payload: LoginPayload, session: Session = Depends(get_session)) -> Envelope:
    if not payload.username or not payload.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="missing credentials")
    client_ip = get_client_ip(request)
    limit_key = f"{client_ip}:{payload.username}"
    _check_rate_limit(LOGIN_ATTEMPTS, limit_key, LOGIN_WINDOW_SECONDS, LOGIN_MAX_ATTEMPTS, "too many login attempts")
    user = get_user_by_username(session, payload.username)
    if not user or not verify_password(payload.password, user.password_hash):
        _record_attempt(LOGIN_ATTEMPTS, limit_key)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid username or password")

    if user.id is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="user id is missing")
    LOGIN_ATTEMPTS.pop(limit_key, None)
    token = create_access_token(subject=user.username, user_id=user.id)
    body = TokenResponse(access_token=token, user_id=user.id)
    return Envelope(code=0, message="ok", data=body.model_dump())


@router.get("/verify")
async def verify(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> Envelope:
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")

    user = get_user_by_username(session, payload["username"])
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user not found")

    tags = []
    if user.investor_tags:
        try:
            import json
            tags = json.loads(user.investor_tags)
        except Exception:
            tags = []

    return Envelope(
        code=0,
        message="ok",
        data={
            "user_id": user.id,
            "username": user.username,
            "role": user.role,
            "qualified_investor": bool(user.qualified_investor),
            "investor_tags": tags,
            "investor_certified_at": user.investor_certified_at.isoformat() if user.investor_certified_at else None,
            "email": user.email,
            "phone": user.phone,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        },
    )


@router.post("/register")
async def register(payload: RegisterPayload, request: Request, session: Session = Depends(get_session)) -> Envelope:
    """注册成功后直接返回访问令牌，免去二次登录。"""
    client_ip = get_client_ip(request)
    _check_rate_limit(REGISTER_ATTEMPTS, client_ip, REGISTER_WINDOW_SECONDS, REGISTER_MAX_ATTEMPTS, "too many register attempts")
    validate_username(payload.username)
    validate_password(payload.password)
    validate_phone(payload.phone)
    validate_email(payload.email)
    if get_user_by_username(session, payload.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user already exists")

    _record_attempt(REGISTER_ATTEMPTS, client_ip)

    password_hash = hash_password(payload.password)
    phone_hash = hash_phone(payload.phone)
    user = create_user(session, payload.username, password_hash, email=payload.email, phone=phone_hash)

    if user.id is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="user id is missing")

    token = create_access_token(subject=user.username, user_id=user.id)
    body = TokenResponse(access_token=token, user_id=user.id)
    return Envelope(code=0, message="ok", data=body.model_dump())
