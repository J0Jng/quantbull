from typing import Optional

from pydantic import BaseModel, Field, field_validator


class FactorCreateRequest(BaseModel):
    """创建因子请求"""
    name: str = Field(..., description="因子名称", min_length=1, max_length=100)
    description: str = Field(default="", description="因子描述", max_length=1000)
    category: str = Field(default="technical", description="因子类别：technical/fundamental/macro")
    formula: Optional[str] = Field(default=None, description="因子公式")
    parameters: dict = Field(default_factory=dict, description="因子参数")
    
    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """验证因子类别"""
        allowed = ["technical", "fundamental", "macro"]
        if v not in allowed:
            raise ValueError(f"因子类别必须是: {', '.join(allowed)}")
        return v


class FactorUpdateRequest(BaseModel):
    """更新因子请求"""
    name: Optional[str] = Field(default=None, description="因子名称", min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, description="因子描述", max_length=1000)
    category: Optional[str] = Field(default=None, description="因子类别")
    formula: Optional[str] = Field(default=None, description="因子公式")
    parameters: Optional[dict] = Field(default=None, description="因子参数")


class FactorResponse(BaseModel):
    """因子响应"""
    id: str = Field(..., description="因子ID")
    name: str = Field(..., description="因子名称")
    description: str = Field(..., description="因子描述")
    category: str = Field(..., description="因子类别")
    formula: Optional[str] = Field(default=None, description="因子公式")
    parameters: dict = Field(..., description="因子参数")
    created_at: str = Field(..., description="创建时间")


class FactorListResponse(BaseModel):
    """因子列表响应"""
    total: int = Field(..., description="总数")
    factors: list[FactorResponse] = Field(..., description="因子列表")


class FactorCalculateRequest(BaseModel):
    """计算因子请求"""
    factor_id: str = Field(..., description="因子ID")
    symbol: str = Field(..., description="股票代码", min_length=1)
    start_date: str = Field(..., description="开始日期（YYYY-MM-DD）")
    end_date: str = Field(..., description="结束日期（YYYY-MM-DD）")
    parameters: Optional[dict] = Field(default=None, description="因子参数（覆盖默认参数）")
    
    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        """验证日期格式"""
        try:
            from datetime import date
            date.fromisoformat(v)
        except ValueError:
            raise ValueError("日期格式必须为 YYYY-MM-DD")
        return v


class FactorCalculateResponse(BaseModel):
    """计算因子响应"""
    factor_id: str = Field(..., description="因子ID")
    symbol: str = Field(..., description="股票代码")
    start_date: str = Field(..., description="开始日期")
    end_date: str = Field(..., description="结束日期")
    values: list[dict] = Field(..., description="因子值列表，格式：[{date: 'YYYY-MM-DD', value: float}]")
    total_points: int = Field(..., description="数据点总数")
