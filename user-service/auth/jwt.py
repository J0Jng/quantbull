from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from core.config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, user_id: int, expires_seconds: Optional[int] = None) -> str:
    expire_seconds = expires_seconds or settings.access_token_expire_seconds
    expire = datetime.now(timezone.utc) + timedelta(seconds=expire_seconds)
    to_encode: Dict[str, Any] = {"sub": subject, "user_id": user_id, "exp": expire}
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        username = payload.get("sub")
        user_id = payload.get("user_id")
        if not isinstance(username, str) or user_id is None:
            return None
        return {"username": username, "user_id": int(user_id)}
    except JWTError:
        return None
