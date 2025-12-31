from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


ALLOWED_STATUSES = ["draft", "active", "archived"]


class StrategyCreateRequest(BaseModel):
    """创建策略请求"""

    name: str = Field(..., description="策略名称", min_length=1, max_length=100)
    description: str = Field(default="", description="策略描述", max_length=1000)
    code: str = Field(..., description="策略代码（Python）", min_length=10)
    factor_ids: List[str] = Field(..., description="关联的因子ID列表", min_length=1)
    parameters: dict = Field(default_factory=dict, description="策略参数")
    status: str = Field(default="draft", description="策略状态：draft/active/archived")

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("策略代码不能为空")
        return v.strip()

    @field_validator("factor_ids")
    @classmethod
    def validate_factor_ids(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("factor_ids 不允许为空")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = ALLOWED_STATUSES
        if v not in allowed:
            raise ValueError(f"status 必须是: {', '.join(allowed)}")
        return v


class StrategyUpdateRequest(BaseModel):
    """更新策略请求"""

    name: Optional[str] = Field(default=None, description="策略名称", min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, description="策略描述", max_length=1000)
    code: Optional[str] = Field(default=None, description="策略代码（Python）", min_length=10)
    factor_ids: Optional[List[str]] = Field(default=None, description="关联的因子ID列表")
    parameters: Optional[dict] = Field(default=None, description="策略参数")
    status: Optional[str] = Field(default=None, description="状态：draft/active/archived")

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v.strip():
            raise ValueError("策略代码不能为空")
        return v.strip()

    @field_validator("factor_ids")
    @classmethod
    def validate_factor_ids(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None and len(v) == 0:
            raise ValueError("factor_ids 不允许为空")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed = ALLOWED_STATUSES
        if v not in allowed:
            raise ValueError(f"status 必须是: {', '.join(allowed)}")
        return v


class StrategyResponse(BaseModel):
    """策略响应"""

    id: str = Field(..., description="策略ID")
    name: str = Field(..., description="策略名称")
    description: str = Field(..., description="策略描述")
    code: str = Field(..., description="策略代码")
    factor_ids: List[str] = Field(..., description="关联因子")
    parameters: dict = Field(..., description="策略参数")
    status: str = Field(..., description="状态")
    created_at: str = Field(..., description="创建时间")
    updated_at: Optional[str] = Field(default=None, description="更新时间")


class StrategyListResponse(BaseModel):
    """策略列表响应"""
    total: int = Field(..., description="总数")
    strategies: list[StrategyResponse] = Field(..., description="策略列表")


class StrategyValidateRequest(BaseModel):
    """策略验证请求"""
    code: str = Field(..., description="策略代码（Python）", min_length=10)
    
    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        """验证策略代码不为空"""
        if not v.strip():
            raise ValueError("策略代码不能为空")
        return v.strip()


class StrategyValidateResponse(BaseModel):
    """策略验证响应"""
    valid: bool = Field(..., description="是否有效")
    errors: list[str] = Field(default_factory=list, description="错误列表")
    warnings: list[str] = Field(default_factory=list, description="警告列表")
    message: str = Field(..., description="验证消息")
