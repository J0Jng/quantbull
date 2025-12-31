from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlmodel import Session

from auth.jwt import create_access_token, hash_password, verify_password, verify_token
from core.config import settings
from models import create_user, get_session, get_user_by_username

router = APIRouter(prefix="/api/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class LoginPayload(BaseModel):
    username: str
    password: str


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
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)) -> Envelope:
    user = get_user_by_username(session, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid username or password")

    if user.id is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="user id is missing")
    token = create_access_token(subject=user.username, user_id=user.id)
    payload = TokenResponse(access_token=token, user_id=user.id)
    return Envelope(code=0, message="ok", data=payload.model_dump())


@router.post("/login/json")
async def login_json(payload: LoginPayload, session: Session = Depends(get_session)) -> Envelope:
    user = get_user_by_username(session, payload.username)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid username or password")

    if user.id is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="user id is missing")
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

    return Envelope(code=0, message="ok", data={"user_id": user.id, "username": user.username})


@router.post("/register", include_in_schema=False)
async def register(payload: LoginPayload, session: Session = Depends(get_session)) -> Envelope:
    if get_user_by_username(session, payload.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user already exists")
    password_hash = hash_password(payload.password)
    user = create_user(session, payload.username, password_hash)
    return Envelope(code=0, message="ok", data={"user_id": user.id, "username": user.username})
