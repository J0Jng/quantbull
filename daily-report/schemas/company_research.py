"""公司研报 Schema 定义"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# ==================== 请求 Schema ====================

class CompanyResearchGenerateRequest(BaseModel):
    """生成公司研报请求"""
    company_name: str = Field(..., min_length=1, max_length=200, description="公司名称")
    stock_code: Optional[str] = Field(None, max_length=20, description="股票代码")
    rating: str = Field(default="hold", description="评级：buy/add/hold/reduce/sell")
    company_info: Optional[str] = Field(None, description="公司基本信息（可空，为空时自动构造）")
    report_type: str = Field(default="summary", description="报告类型：summary/analysis")
    include_risks: bool = Field(default=True, description="是否包含风险提示")
    tags: Optional[List[str]] = Field(default=None, description="标签列表")
    force: bool = Field(default=False, description="是否强制重新生成（true=跳过去重）")


class CompanyResearchQueryRequest(BaseModel):
    """查询公司研报请求"""
    limit: int = Field(default=20, ge=1, le=100, description="每页数量")
    offset: int = Field(default=0, ge=0, description="偏移量")
    rating: Optional[str] = Field(None, description="评级筛选")
    keyword: Optional[str] = Field(None, description="关键词搜索（company_name/stock_code/tags）")


# ==================== 响应 Schema ====================

class CompanyResearchReportResponse(BaseModel):
    """公司研报响应"""
    id: str = Field(..., description="研报 ID")
    company_name: str = Field(..., description="公司名称")
    stock_code: Optional[str] = Field(None, description="股票代码")
    rating: str = Field(..., description="评级")
    report_type: str = Field(..., description="报告类型")
    company_info: Optional[str] = Field(None, description="公司基本信息")
    report_content: str = Field(..., description="研报正文（markdown）")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    include_risks: bool = Field(..., description="是否包含风险提示")
    model: Optional[str] = Field(None, description="使用的模型")
    tokens_used: Optional[Dict[str, Any]] = Field(None, description="token 使用情况")
    sections: Optional[List[str]] = Field(None, description="研报章节")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class CompanyResearchListResponse(BaseModel):
    """公司研报列表响应"""
    total: int = Field(..., description="总数")
    items: List[CompanyResearchReportResponse] = Field(..., description="研报列表")
