"""
AI Token 扣减服务

负责调用 user-service 的 /api/ai/consume 接口扣减用户 token
"""
from typing import Any, Dict, Optional, Tuple

import httpx

from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)


class TokenConsumeError(Exception):
    """Token 扣减错误"""
    def __init__(self, message: str, required: int = 0, remaining: int = 0, status_code: int = 402):
        super().__init__(message)
        self.message = message
        self.required = required
        self.remaining = remaining
        self.status_code = status_code


class TokenService:
    """Token 扣减服务"""
    
    def __init__(self):
        self.user_service_url = settings.user_service_url
        self.timeout = settings.request_timeout
    
    async def consume_tokens(
        self,
        authorization: str,
        tokens: int,
        reason: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Tuple[bool, int]:
        """
        扣减用户 AI Token
        
        Args:
            authorization: Bearer token（完整的 Authorization 头值）
            tokens: 要扣减的 token 数量
            reason: 扣减原因
            request_id: 请求 ID（用于幂等）
            
        Returns:
            Tuple[bool, int]: (是否成功, 剩余 tokens)
            
        Raises:
            TokenConsumeError: 余额不足或其他扣减错误
        """
        if tokens <= 0:
            logger.warning(f"扣减 token 数量无效: {tokens}")
            return True, 0
        
        consume_url = f"{self.user_service_url}/api/tokens/consume"
        
        payload: Dict[str, Any] = {"tokens": tokens}
        if reason:
            payload["reason"] = reason
        if request_id:
            payload["request_id"] = request_id
        
        headers = {"Authorization": authorization}
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    consume_url,
                    json=payload,
                    headers=headers,
                )
                
                # 检查响应
                if response.status_code == 200:
                    data = response.json()
                    remaining = data.get("data", {}).get("remaining", 0)
                    logger.info(f"Token 扣减成功: consumed={tokens}, remaining={remaining}")
                    return True, remaining
                
                elif response.status_code == 402:
                    # 余额不足
                    data = response.json()
                    detail = data.get("detail", {})
                    if isinstance(detail, dict):
                        required = detail.get("required", tokens)
                        remaining = detail.get("remaining", 0)
                    else:
                        required = tokens
                        remaining = 0
                    
                    logger.warning(f"Token 余额不足: required={required}, remaining={remaining}")
                    raise TokenConsumeError(
                        message="Insufficient AI tokens",
                        required=required,
                        remaining=remaining,
                        status_code=402,
                    )
                
                elif response.status_code == 401:
                    logger.error("Token 扣减失败: 未授权")
                    raise TokenConsumeError(
                        message="Unauthorized",
                        status_code=401,
                    )
                
                else:
                    logger.error(f"Token 扣减失败: status={response.status_code}, body={response.text}")
                    raise TokenConsumeError(
                        message=f"Token consume failed: {response.status_code}",
                        status_code=response.status_code,
                    )
                    
        except httpx.TimeoutException:
            logger.error("Token 扣减超时")
            raise TokenConsumeError(
                message="Token service timeout",
                status_code=504,
            )
        except httpx.RequestError as e:
            logger.error(f"Token 扣减请求错误: {e}")
            raise TokenConsumeError(
                message=f"Token service error: {str(e)}",
                status_code=503,
            )


# 全局单例
token_service = TokenService()
