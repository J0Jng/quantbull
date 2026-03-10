import httpx
from fastapi import HTTPException, status

from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)


class AuthService:
    """用户相关服务：透传 user-service 管理员接口"""

    @staticmethod
    def _build_auth_headers(authorization: str | None) -> dict:
        headers: dict[str, str] = {}
        if authorization:
            headers["Authorization"] = authorization
        return headers

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
    async def admin_list_users(limit: int = 100, offset: int = 0, authorization: str | None = None) -> dict:
        """管理员获取用户列表"""
        url = f"{settings.user_service_url.rstrip('/')}/api/admin/users?limit={limit}&offset={offset}"
        headers = AuthService._build_auth_headers(authorization)
        async with httpx.AsyncClient(timeout=settings.user_service_timeout, trust_env=False) as client:
            response = await client.get(url, headers=headers)
        return AuthService._handle_passthrough_response(response)

    @staticmethod
    async def admin_get_user(user_id: int, authorization: str | None = None) -> dict:
        """管理员获取单个用户详情"""
        url = f"{settings.user_service_url.rstrip('/')}/api/admin/users/{user_id}"
        headers = AuthService._build_auth_headers(authorization)
        async with httpx.AsyncClient(timeout=settings.user_service_timeout, trust_env=False) as client:
            response = await client.get(url, headers=headers)
        return AuthService._handle_passthrough_response(response)

    @staticmethod
    async def admin_create_user(username: str, password: str, role: str = "user", email: str | None = None, phone: str | None = None, authorization: str | None = None) -> dict:
        """管理员创建新用户"""
        url = f"{settings.user_service_url.rstrip('/')}/api/admin/users"
        body = {"username": username, "password": password, "role": role}
        if email is not None:
            body["email"] = email
        if phone is not None:
            body["phone"] = phone
        headers = AuthService._build_auth_headers(authorization)
        async with httpx.AsyncClient(timeout=settings.user_service_timeout, trust_env=False) as client:
            response = await client.post(url, json=body, headers=headers)
        return AuthService._handle_passthrough_response(response)

    @staticmethod
    async def admin_update_user(user_id: int, password: str | None = None, role: str | None = None, authorization: str | None = None) -> dict:
        """管理员更新用户信息"""
        url = f"{settings.user_service_url.rstrip('/')}/api/admin/users/{user_id}"
        body = {}
        if password is not None:
            body["password"] = password
        if role is not None:
            body["role"] = role
        headers = AuthService._build_auth_headers(authorization)
        async with httpx.AsyncClient(timeout=settings.user_service_timeout, trust_env=False) as client:
            response = await client.patch(url, json=body, headers=headers)
        return AuthService._handle_passthrough_response(response)

    @staticmethod
    async def admin_delete_user(user_id: int, authorization: str | None = None) -> dict:
        """管理员删除用户"""
        url = f"{settings.user_service_url.rstrip('/')}/api/admin/users/{user_id}"
        headers = AuthService._build_auth_headers(authorization)
        async with httpx.AsyncClient(timeout=settings.user_service_timeout, trust_env=False) as client:
            response = await client.delete(url, headers=headers)
        return AuthService._handle_passthrough_response(response)

    @staticmethod
    async def admin_update_user_ai_tokens(user_id: int, ai_tokens: int, authorization: str | None = None) -> dict:
        """管理员更新用户 AI Token 余额"""
        url = f"{settings.user_service_url.rstrip('/')}/api/admin/users/{user_id}/ai-tokens"
        headers = AuthService._build_auth_headers(authorization)
        async with httpx.AsyncClient(timeout=settings.user_service_timeout, trust_env=False) as client:
            response = await client.patch(url, json={"ai_tokens": ai_tokens}, headers=headers)
        return AuthService._handle_passthrough_response(response)
