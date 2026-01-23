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
            logger.warning(f"verify token failed with status {response.status_code}")
            return None

        payload = response.json()
        if not isinstance(payload, dict):
            return None

        data = payload.get("data") or {}
        user_id = data.get("user_id")
        username = data.get("username")
        role = data.get("role", "user")
        qualified_investor = data.get("qualified_investor")
        investor_tags = data.get("investor_tags")
        investor_certified_at = data.get("investor_certified_at")
        email = data.get("email")
        phone = data.get("phone")
        created_at = data.get("created_at")
        if payload.get("code") != 0 or user_id is None or not isinstance(username, str):
            return None

        try:
            return TokenData(
                username=username,
                user_id=int(user_id),
                role=role,
                qualified_investor=qualified_investor if isinstance(qualified_investor, bool) else None,
                investor_tags=investor_tags if isinstance(investor_tags, list) else None,
                investor_certified_at=investor_certified_at if isinstance(investor_certified_at, str) else None,
                email=email if isinstance(email, str) else None,
                phone=phone if isinstance(phone, str) else None,
                created_at=created_at if isinstance(created_at, str) else None,
            )
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
    async def register(username: str, password: str, phone: str, email: Optional[str] = None) -> dict:
        """用户注册，透传 user-service 响应。"""
        url = f"{settings.user_service_url.rstrip('/')}/api/auth/register"
        async with httpx.AsyncClient(timeout=settings.user_service_timeout) as client:
            response = await client.post(url, json={"username": username, "password": password, "phone": phone, "email": email})
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
            message = (payload.get("message") or payload.get("detail") or response.text or "request failed")
            raise HTTPException(status_code=response.status_code, detail=message)

        return payload

    # ==================== 管理员接口 ====================

    @staticmethod
    async def admin_list_users(token: str, limit: int = 100, offset: int = 0) -> dict:
        """管理员获取用户列表"""
        url = f"{settings.user_service_url.rstrip('/')}/api/admin/users?limit={limit}&offset={offset}"
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient(timeout=settings.user_service_timeout) as client:
            response = await client.get(url, headers=headers)
        return AuthService._handle_passthrough_response(response)

    @staticmethod
    async def admin_get_user(token: str, user_id: int) -> dict:
        """管理员获取单个用户详情"""
        url = f"{settings.user_service_url.rstrip('/')}/api/admin/users/{user_id}"
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient(timeout=settings.user_service_timeout) as client:
            response = await client.get(url, headers=headers)
        return AuthService._handle_passthrough_response(response)

    @staticmethod
    async def admin_create_user(token: str, username: str, password: str, role: str = "user") -> dict:
        """管理员创建新用户"""
        url = f"{settings.user_service_url.rstrip('/')}/api/admin/users"
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient(timeout=settings.user_service_timeout) as client:
            response = await client.post(url, headers=headers, json={"username": username, "password": password, "role": role})
        return AuthService._handle_passthrough_response(response)

    @staticmethod
    async def admin_update_user(token: str, user_id: int, password: Optional[str] = None, role: Optional[str] = None) -> dict:
        """管理员更新用户信息"""
        url = f"{settings.user_service_url.rstrip('/')}/api/admin/users/{user_id}"
        headers = {"Authorization": f"Bearer {token}"}
        body = {}
        if password is not None:
            body["password"] = password
        if role is not None:
            body["role"] = role
        async with httpx.AsyncClient(timeout=settings.user_service_timeout) as client:
            response = await client.patch(url, headers=headers, json=body)
        return AuthService._handle_passthrough_response(response)

    @staticmethod
    async def admin_delete_user(token: str, user_id: int) -> dict:
        """管理员删除用户"""
        url = f"{settings.user_service_url.rstrip('/')}/api/admin/users/{user_id}"
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient(timeout=settings.user_service_timeout) as client:
            response = await client.delete(url, headers=headers)
        return AuthService._handle_passthrough_response(response)

    @staticmethod
    async def admin_update_user_ai_tokens(token: str, user_id: int, ai_tokens: int) -> dict:
        """管理员更新用户 AI Token 余额"""
        url = f"{settings.user_service_url.rstrip('/')}/api/admin/users/{user_id}/ai-tokens"
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient(timeout=settings.user_service_timeout) as client:
            response = await client.patch(url, headers=headers, json={"ai_tokens": ai_tokens})
        return AuthService._handle_passthrough_response(response)
