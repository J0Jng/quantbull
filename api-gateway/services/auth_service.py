from typing import Optional

import httpx
from fastapi import HTTPException, status

from core.config import settings
from core.logger import get_logger
from schemas.auth import TokenData

logger = get_logger(__name__)


class AuthService:
    """认证服务：委托 user-service 处理登录和鉴权"""

    @staticmethod
    async def login_with_form(username: str, password: str) -> dict:
        url = f"{settings.user_service_url.rstrip('/')}/api/auth/login"
        async with httpx.AsyncClient(timeout=settings.user_service_timeout) as client:
            response = await client.post(url, data={"username": username, "password": password})
        return AuthService._handle_login_response(response)

    @staticmethod
    async def login_with_json(username: str, password: str) -> dict:
        url = f"{settings.user_service_url.rstrip('/')}/api/auth/login/json"
        async with httpx.AsyncClient(timeout=settings.user_service_timeout) as client:
            response = await client.post(url, json={"username": username, "password": password})
        return AuthService._handle_login_response(response)

    @staticmethod
    async def verify_token(token: str) -> Optional[TokenData]:
        url = f"{settings.user_service_url.rstrip('/')}/api/auth/verify"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            async with httpx.AsyncClient(timeout=settings.user_service_timeout) as client:
                response = await client.get(url, headers=headers)
        except Exception as exc:  # pragma: no cover - network errors
            logger.error(f"verify token failed: {exc}")
            return None

        if response.status_code != 200:
            logger.warning(f"verify token failed with status {response.status_code}: {response.text}")
            return None

        payload = response.json()
        if not isinstance(payload, dict):
            return None

        data = payload.get("data") or {}
        user_id = data.get("user_id")
        username = data.get("username")
        if payload.get("code") != 0 or user_id is None or not isinstance(username, str):
            return None

        try:
            return TokenData(username=username, user_id=int(user_id))
        except (TypeError, ValueError):
            return None

    @staticmethod
    async def verify_raw(token: str) -> dict:
        """直接透传 user-service 的 verify 响应，保持错误码与结构一致。"""
        url = f"{settings.user_service_url.rstrip('/')}/api/auth/verify"
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient(timeout=settings.user_service_timeout) as client:
            response = await client.get(url, headers=headers)
        return AuthService._handle_passthrough_response(response)

    @staticmethod
    async def register(username: str, password: str) -> dict:
        """用户注册，透传 user-service 响应。"""
        url = f"{settings.user_service_url.rstrip('/')}/api/auth/register"
        async with httpx.AsyncClient(timeout=settings.user_service_timeout) as client:
            response = await client.post(url, json={"username": username, "password": password})
        return AuthService._handle_passthrough_response(response)

    @staticmethod
    def _handle_login_response(response: httpx.Response) -> dict:
        try:
            payload = response.json()
        except Exception:
            payload = {"message": response.text}

        if response.status_code != 200:
            message = payload.get("message") if isinstance(payload, dict) else response.text
            raise HTTPException(status_code=response.status_code, detail=message or "login failed")

        if not isinstance(payload, dict) or payload.get("code") != 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=(payload.get("message") if isinstance(payload, dict) else "authentication failed"),
            )

        return payload

    @staticmethod
    def _handle_passthrough_response(response: httpx.Response) -> dict:
        try:
            payload = response.json()
        except Exception:
            payload = {"message": response.text}

        if response.status_code >= 400:
            message = payload.get("message") if isinstance(payload, dict) else response.text
            raise HTTPException(status_code=response.status_code, detail=message or "request failed")

        return payload
