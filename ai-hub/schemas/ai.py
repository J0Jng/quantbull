from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ModelType(str, Enum):
    """支持的 AI 模型类型"""
    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    OPENAI = "openai"


class TaskType(str, Enum):
    """任务类型"""
    CODE = "code"  # 代码生成
    NEWS = "news"  # 新闻生成
    SUMMARY = "summary"  # 总结
    STRATEGY = "strategy"  # 策略生成
    GENERAL = "general"  # 通用对话


# ==================== 通用聊天 ====================
class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., description="用户消息", min_length=1)
    model: Optional[ModelType] = Field(default=None, description="指定模型，不指定则自动路由")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0, description="温度参数")
    max_tokens: Optional[int] = Field(default=None, ge=1, le=8192, description="最大生成token数")
    system_prompt: Optional[str] = Field(default=None, description="系统提示词")
    
    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("消息不能为空")
        return v.strip()


class ChatResponse(BaseModel):
    """聊天响应"""
    content: str = Field(..., description="AI 回复内容")
    model: str = Field(..., description="使用的模型")
    tokens_used: Optional[int] = Field(default=None, description="使用的token数")
    finish_reason: Optional[str] = Field(default=None, description="完成原因")


# ==================== 新闻生成 ====================
class NewsGenerationRequest(BaseModel):
    """新闻生成请求"""
    news_flash: str = Field(..., description="快讯内容", min_length=1)
    stock_code: Optional[str] = Field(default=None, description="股票代码")
    quote_data: Optional[dict] = Field(default=None, description="行情数据")
    target_length: int = Field(default=300, ge=100, le=1000, description="目标字数")
    model: Optional[ModelType] = Field(default=None, description="显式指定模型，不指定则自动路由到 DeepSeek")
    
    @field_validator("news_flash")
    @classmethod
    def validate_news_flash(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("快讯内容不能为空")
        return v.strip()


class NewsGenerationResponse(BaseModel):
    """新闻生成响应"""
    news_content: str = Field(..., description="生成的新闻内容")
    model: str = Field(..., description="使用的模型")
    word_count: int = Field(..., description="字数统计")
    tokens_used: Optional[int] = Field(default=None, description="使用的token数")


# ==================== 报告生成 ====================
class ReportGenerationRequest(BaseModel):
    """报告生成请求"""
    company_info: str = Field(..., description="公司信息", min_length=1)
    report_type: str = Field(default="summary", description="报告类型：summary/analysis")
    include_risks: bool = Field(default=True, description="是否包含风险因素")
    
    @field_validator("company_info")
    @classmethod
    def validate_company_info(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("公司信息不能为空")
        return v.strip()


class ReportGenerationResponse(BaseModel):
    """报告生成响应"""
    report_content: str = Field(..., description="生成的报告内容")
    model: str = Field(..., description="使用的模型")
    sections: list[str] = Field(default_factory=list, description="报告章节列表")


# ==================== 摘要生成 ====================
class SummaryGenerationRequest(BaseModel):
    """摘要生成请求"""
    content: str = Field(..., description="待摘要内容", min_length=1)
    summary_type: str = Field(default="structured", description="摘要类型：structured/bullet/paragraph")
    max_length: Optional[int] = Field(default=None, ge=50, le=2000, description="最大长度")
    model: Optional[ModelType] = Field(default=None, description="显式指定模型，不指定则自动路由到 Qwen")
    
    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("内容不能为空")
        return v.strip()


class SummaryGenerationResponse(BaseModel):
    """摘要生成响应"""
    summary: str = Field(..., description="生成的摘要")
    model: str = Field(..., description="使用的模型")
    tokens_used: Optional[int] = Field(default=None, description="使用的token数")
    sections: Optional[list[str]] = Field(default=None, description="结构化摘要的章节列表")


# ==================== 策略生成 ====================
class StrategyGenerationRequest(BaseModel):
    """策略生成请求"""
    user_description: str = Field(..., description="用户策略描述", min_length=1)
    framework: str = Field(default="backtrader", description="回测框架：backtrader/zipline")
    include_risk_control: bool = Field(default=True, description="是否包含风险控制")
    model: Optional[ModelType] = Field(default=None, description="显式指定模型，不指定则自动路由到 Qwen")
    
    @field_validator("user_description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("策略描述不能为空")
        return v.strip()


class StrategyGenerationResponse(BaseModel):
    """策略生成响应"""
    strategy_code: str = Field(..., description="生成的策略代码")
    model: str = Field(..., description="使用的模型")
    explanation: str = Field(..., description="策略说明")
    parameters: dict = Field(default_factory=dict, description="策略参数")
    tokens_used: Optional[int] = Field(default=None, description="使用的token数")


# ==================== 数字人生成 ====================
class DigitalHumanRequest(BaseModel):
    """数字人视频生成请求"""
    text: str = Field(..., description="口播文本", min_length=1)
    duration_limit: int = Field(default=40, ge=10, le=120, description="时长限制（秒）")
    voice_style: str = Field(default="professional", description="语音风格")
    
    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("口播文本不能为空")
        return v.strip()


class DigitalHumanResponse(BaseModel):
    """数字人视频生成响应"""
    video_url: Optional[str] = Field(default=None, description="视频URL")
    task_id: str = Field(..., description="任务ID")
    estimated_duration: int = Field(..., description="预计时长（秒）")
    status: str = Field(..., description="任务状态：pending/processing/completed/failed")


# ==================== 模型路由 ====================
class ModelRouteRequest(BaseModel):
    """模型路由请求"""
    task_type: TaskType = Field(..., description="任务类型")
    message: str = Field(..., description="消息内容", min_length=1)
    
    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("消息不能为空")
        return v.strip()


class ModelRouteResponse(BaseModel):
    """模型路由响应"""
    recommended_model: ModelType = Field(..., description="推荐的模型")
    reason: str = Field(..., description="推荐理由")
