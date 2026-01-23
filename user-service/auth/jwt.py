from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from core.config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def _md5_hex(value: str) -> str:
    return hashlib.md5(value.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    """使用 MD5 进行存储加密。"""
    return _md5_hex(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """兼容历史 pbkdf2_sha256 与当前 MD5 存储。"""
    if "$" in hashed_password:
        return pwd_context.verify(plain_password, hashed_password)
    return _md5_hex(plain_password) == hashed_password


def hash_phone(phone: str) -> str:
    """手机号使用 MD5 进行存储加密。"""
    return _md5_hex(phone)


def create_access_token(subject: str, user_id: int, expires_seconds: Optional[int] = None) -> str:
    expire_seconds = expires_seconds or settings.access_token_expire_seconds
    expire = datetime.now(timezone.utc) + timedelta(seconds=expire_seconds)
    to_encode: Dict[str, Any] = {
        "sub": subject,
        "user_id": user_id,
        "exp": expire,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "jti": secrets.token_urlsafe(16),
    }
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
        )
        username = payload.get("sub")
        user_id = payload.get("user_id")
        if not isinstance(username, str) or user_id is None:
            return None
        return {"username": username, "user_id": int(user_id)}
    except JWTError:
        return None
