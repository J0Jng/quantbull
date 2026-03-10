from typing import Any

import httpx

from core.config import settings


class AuthService:
    async def verify_access_token(self, authorization: str | None) -> dict[str, Any] | None:
        if not authorization or not authorization.lower().startswith("bearer "):
            return None

        verify_url = f"{settings.user_service_url.rstrip('/')}/api/auth/verify"
        headers = {"Authorization": authorization}

        async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
            response = await client.get(verify_url, headers=headers)

        if response.status_code != 200:
            return None

        try:
            payload = response.json()
        except Exception:
            return None

        data = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(data, dict):
            return None

        if not data.get("valid"):
            return None

        user = data.get("user")
        return user if isinstance(user, dict) else None


auth_service = AuthService()