"""管理员相关接口 - 代理到 user-service"""
from typing import Optional

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel

from services.auth_service import AuthService

router = APIRouter()


class UserCreateRequest(BaseModel):
    """创建用户请求"""
    username: str
    password: str
    role: str = "user"
    email: Optional[str] = None
    phone: Optional[str] = None


class UserUpdateRequest(BaseModel):
    """更新用户请求"""
    password: Optional[str] = None
    role: Optional[str] = None


class UserAiTokensUpdateRequest(BaseModel):
    """更新用户 AI Token 请求"""
    ai_tokens: int


@router.get("/users", summary="获取用户列表", description="管理员获取所有用户列表（支持分页）")
async def list_users(
    request: Request,
    limit: int = Query(100, description="每页数量"),
    offset: int = Query(0, description="偏移量")
) -> dict:
    """获取用户列表 - 仅管理员可访问"""
    return await AuthService.admin_list_users(
        limit=limit,
        offset=offset,
        authorization=request.headers.get("authorization"),
    )


@router.get("/users/{user_id}", summary="获取用户详情", description="管理员获取指定用户的详细信息")
async def get_user(
    request: Request,
    user_id: int
) -> dict:
    """获取单个用户详情 - 仅管理员可访问"""
    return await AuthService.admin_get_user(user_id, authorization=request.headers.get("authorization"))


@router.post("/users", summary="创建用户", description="管理员创建新用户")
async def create_user(
    request: Request,
    user_data: UserCreateRequest
) -> dict:
    """创建新用户 - 仅管理员可访问"""
    return await AuthService.admin_create_user(
        user_data.username,
        user_data.password,
        user_data.role,
        user_data.email,
        user_data.phone,
        authorization=request.headers.get("authorization"),
    )


@router.patch("/users/{user_id}", summary="更新用户", description="管理员更新用户信息（重置密码、修改角色）")
async def update_user(
    request: Request,
    user_id: int,
    user_data: UserUpdateRequest
) -> dict:
    """更新用户信息 - 仅管理员可访问"""
    return await AuthService.admin_update_user(
        user_id,
        user_data.password,
        user_data.role,
        authorization=request.headers.get("authorization"),
    )


@router.delete("/users/{user_id}", summary="删除用户", description="管理员删除指定用户")
async def delete_user(
    request: Request,
    user_id: int
) -> dict:
    """删除用户 - 仅管理员可访问"""
    return await AuthService.admin_delete_user(user_id, authorization=request.headers.get("authorization"))


@router.patch("/users/{user_id}/ai-tokens", summary="更新用户 AI Token", description="管理员更新用户 AI Token 余额")
async def update_user_ai_tokens(
    request: Request,
    user_id: int,
    payload: UserAiTokensUpdateRequest
) -> dict:
    """更新用户 AI Token 余额 - 仅管理员可访问"""
    return await AuthService.admin_update_user_ai_tokens(
        user_id,
        payload.ai_tokens,
        authorization=request.headers.get("authorization"),
    )
