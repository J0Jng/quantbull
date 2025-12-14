import asyncio
from typing import Optional, Tuple

import httpx
from fastapi import APIRouter, Request, HTTPException, status
from starlette.responses import Response

from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


class ProxyService:
    """代理服务 - 统一转发到下游微服务"""
    
    # 路由前缀到服务地址的映射
    ROUTE_MAPPING = {
        "/news": settings.ai_hub_url,
        "/data": settings.data_service_url,
        "/quant": settings.quant_engine_url,
        "/report": settings.daily_report_url,
    }
    
    @classmethod
    def get_target_url(cls, path: str) -> Tuple[str, str]:
        """根据路径获取目标服务地址和剩余路径"""
        # 移除开头的斜杠
        path = path.lstrip("/")
        
        # 查找匹配的路由前缀
        for prefix, base_url in cls.ROUTE_MAPPING.items():
            prefix_clean = prefix.lstrip("/")
            if path.startswith(prefix_clean):
                # 移除前缀，获取剩余路径
                remaining_path = path[len(prefix_clean):].lstrip("/")
                target_url = f"{base_url}/{remaining_path}" if remaining_path else base_url
                return target_url, remaining_path
        
        raise ValueError(f"无法匹配路由: {path}")
    
    @classmethod
    async def proxy_request(
        cls,
        request: Request,
        path: str,
        max_retries: int = None
    ) -> Response:
        """代理请求到下游服务（带重试机制）"""
        max_retries = max_retries or settings.proxy_max_retries
        timeout = settings.proxy_timeout
        
        # 获取目标 URL
        try:
            target_url, remaining_path = cls.get_target_url(path)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        
        # 构建完整 URL（包含查询参数）
        full_url = f"{target_url}?{request.url.query}" if request.url.query else target_url
        
        # 准备请求头（移除不需要的）
        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("connection", None)
        headers.pop("content-length", None)
        
        # 获取请求体
        body = None
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            try:
                body = await request.body()
            except Exception:
                pass
        
        # 重试逻辑
        last_exception = None
        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.request(
                        method=request.method,
                        url=full_url,
                        headers=headers,
                        content=body,
                        follow_redirects=True
                    )
                    
                    # 准备响应头
                    response_headers = dict(response.headers)
                    response_headers.pop("content-length", None)
                    response_headers.pop("connection", None)
                    
                    # 返回响应
                    return Response(
                        content=response.content,
                        status_code=response.status_code,
                        headers=response_headers,
                        media_type=response.headers.get("content-type", "application/json")
                    )
                    
            except httpx.TimeoutException:
                last_exception = f"请求超时（{timeout}秒）"
                if attempt < max_retries:
                    await asyncio.sleep(0.5 * (attempt + 1))  # 指数退避
                    continue
                logger.error(f"代理请求超时: {full_url} (尝试 {attempt + 1}/{max_retries + 1})")
                
            except httpx.HTTPStatusError as e:
                # 5xx 错误才重试
                if e.response.status_code >= 500 and attempt < max_retries:
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue
                # 其他错误直接返回
                response_headers = dict(e.response.headers)
                response_headers.pop("content-length", None)
                response_headers.pop("connection", None)
                return Response(
                    content=e.response.content,
                    status_code=e.response.status_code,
                    headers=response_headers,
                    media_type=e.response.headers.get("content-type", "application/json")
                )
                
            except Exception as e:
                last_exception = str(e)
                if attempt < max_retries:
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue
                logger.error(f"代理请求失败: {full_url}, 错误: {e}")
        
        # 所有重试都失败
        raise HTTPException(
            status_code=502,
            detail=f"下游服务不可用: {last_exception}"
        )


@router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    include_in_schema=False
)
async def proxy_handler(request: Request, path: str) -> Response:
    """统一代理处理器"""
    return await ProxyService.proxy_request(request, path)
