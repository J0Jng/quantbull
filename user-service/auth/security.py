from datetime import datetime, timedelta, timezone
import hashlib
from typing import Any

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from core.config import settings


def hash_password(password: str) -> str:
    return hashlib.md5(password.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, stored_password_hash: str) -> bool:
    if not stored_password_hash:
        return False
    if plain_password == stored_password_hash:
        return True
    return hash_password(plain_password) == stored_password_hash


def create_access_token(subject: str, user_id: int, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    payload: dict[str, Any] = {
        "sub": subject,
        "user_id": user_id,
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except ExpiredSignatureError as exc:
        raise ValueError("token expired") from exc
    except InvalidTokenError as exc:
        raise ValueError("invalid token") from exc