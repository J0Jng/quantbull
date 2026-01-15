from typing import Optional

from pydantic import BaseModel, Field, field_validator


ALLOWED_DATA_SOURCES = ["price", "fundamental", "tdengine"]

# 白名单列名（与 indicator_engine 保持一致）
ALLOWED_EXPRESSION_COLUMNS = {
    # 基础价格
    "open", "high", "low", "close", "volume", "amount", "p_change",
    # MACD
    "macd", "macds", "macdh",
    # KDJ
    "kdjk", "kdjd", "kdjj",
    # BOLL
    "boll", "boll_ub", "boll_lb",
    # RSI
    "rsi", "rsi_6", "rsi_12", "rsi_24",
    # ATR
    "atr", "tr",
    # DMI
    "pdi", "mdi", "dx", "adx", "adxr",
    # WR
    "wr_6", "wr_10", "wr_14",
    # CCI
    "cci", "cci_84",
    # TRIX
    "trix", "trix_20_sma",
    # CR
    "cr",
    # VR
    "vr", "vr_6_sma",
    # MA / EMA（兼容大小写与常用别名）
    "ma5", "ma10", "ma20", "ma30", "ma50", "ma60", "ma120", "ma200", "ma250",
    "MA_5", "MA_10", "MA_20", "MA_30", "MA_50", "MA_60", "MA_120", "MA_200", "MA_250",
    "ema5", "ema10", "ema12", "ema20", "ema26", "ema60",
    "EMA_5", "EMA_10", "EMA_12", "EMA_20", "EMA_26", "EMA_60",
    # DMA
    "dma", "dma_10_sma",
    # TEMA
    "tema",
    # MFI
    "mfi", "mfisma",
    # VWMA
    "vwma", "mvwma",
    # PPO
    "ppo", "ppos", "ppoh",
    # StochRSI
    "stochrsi_k", "stochrsi_d",
    # WT
    "wt1", "wt2",
    # Supertrend
    "supertrend", "supertrend_ub", "supertrend_lb",
    # ROC
    "roc", "rocma", "rocema",
    # OBV
    "obv",
    # SAR
    "sar",
    # PSY
    "psy", "psyma",
    # BRAR
    "ar", "br",
}


class FactorCreateRequest(BaseModel):
    """创建因子请求"""

    name: str = Field(..., description="因子名称", min_length=1, max_length=100)
    code: Optional[str] = Field(default=None, description="因子代码（唯一标识，可自动生成）", max_length=50)
    description: str = Field(default="", description="因子描述", max_length=1000)
    expression: str = Field(..., description="因子表达式/公式", min_length=1)
    data_source: str = Field(default="price", description="数据来源：price/fundamental/tdengine")
    category: Optional[str] = Field(default="technical", description="因子类别：technical/fundamental/macro")
    formula: Optional[str] = Field(default=None, description="兼容旧字段：因子公式")
    parameters: dict = Field(default_factory=dict, description="因子参数")

    @field_validator("data_source")
    @classmethod
    def validate_data_source(cls, v: str) -> str:
        allowed = ALLOWED_DATA_SOURCES
        if v not in allowed:
            raise ValueError(f"data_source 必须是: {', '.join(allowed)}")
        return v
    
    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        allowed = ["technical", "fundamental", "macro"]
        if v and v not in allowed:
            raise ValueError(f"category 必须是: {', '.join(allowed)}")
        return v


class FactorUpdateRequest(BaseModel):
    """更新因子请求"""

    name: Optional[str] = Field(default=None, description="因子名称", min_length=1, max_length=100)
    code: Optional[str] = Field(default=None, description="因子代码", max_length=50)
    description: Optional[str] = Field(default=None, description="因子描述", max_length=1000)
    expression: Optional[str] = Field(default=None, description="因子表达式/公式")
    data_source: Optional[str] = Field(default=None, description="数据来源")
    category: Optional[str] = Field(default=None, description="因子类别")
    formula: Optional[str] = Field(default=None, description="因子公式（兼容旧字段）")
    parameters: Optional[dict] = Field(default=None, description="因子参数")

    @field_validator("data_source")
    @classmethod
    def validate_data_source(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed = ALLOWED_DATA_SOURCES
        if v not in allowed:
            raise ValueError(f"data_source 必须是: {', '.join(allowed)}")
        return v
    
    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed = ["technical", "fundamental", "macro"]
        if v not in allowed:
            raise ValueError(f"category 必须是: {', '.join(allowed)}")
        return v


class FactorResponse(BaseModel):
    """因子响应"""

    id: str = Field(..., description="因子ID")
    name: str = Field(..., description="因子名称")
    code: str = Field(..., description="因子代码")
    description: str = Field(..., description="因子描述")
    expression: str = Field(..., description="因子表达式/公式")
    data_source: str = Field(..., description="数据来源")
    category: Optional[str] = Field(default=None, description="因子类别")
    formula: Optional[str] = Field(default=None, description="因子公式（兼容旧字段）")
    parameters: dict = Field(..., description="因子参数")
    created_at: str = Field(..., description="创建时间")
    updated_at: Optional[str] = Field(default=None, description="更新时间")


class FactorListResponse(BaseModel):
    """因子列表响应"""
    total: int = Field(..., description="总数")
    factors: list[FactorResponse] = Field(..., description="因子列表")


class FactorValidateRequest(BaseModel):
    """验证因子表达式请求"""
    expression: str = Field(..., description="因子表达式", min_length=1)
    data_source: Optional[str] = Field(default="price", description="数据来源")
    parameters: Optional[dict] = Field(default=None, description="因子参数")


class FactorValidateResponse(BaseModel):
    """验证因子表达式响应"""
    valid: bool = Field(..., description="是否有效")
    expression: str = Field(default="", description="原始表达式")
    errors: list[str] = Field(default_factory=list, description="错误列表")
    warnings: list[str] = Field(default_factory=list, description="警告列表")
    suggested_fix: Optional[str] = Field(default=None, description="建议修复表达式")
    message: str = Field(default="", description="验证消息")


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
    
    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        """验证并清理股票代码"""
        # 移除 .SZ/.SH 后缀，只保留6位数字
        cleaned = v.replace(".SZ", "").replace(".SH", "").replace(".sz", "").replace(".sh", "").strip()
        if len(cleaned) == 6 and cleaned.isdigit():
            return cleaned
        # 如果已经是6位数字，直接返回
        if len(v) == 6 and v.isdigit():
            return v
        return v  # 其他情况保持原样


class FactorCalculateResponse(BaseModel):
    """计算因子响应"""
    factor_id: str = Field(..., description="因子ID")
    symbol: str = Field(..., description="股票代码")
    start_date: str = Field(..., description="开始日期")
    end_date: str = Field(..., description="结束日期")
    values: list[dict] = Field(..., description="因子值列表，格式：[{date: 'YYYY-MM-DD', value: float}]")
    total_points: int = Field(..., description="数据点总数")
