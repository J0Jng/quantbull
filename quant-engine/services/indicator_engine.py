"""指标计算引擎 - 适配 indicator/ 模块到 quant-engine

将 data_loader 返回的 DataFrame 转换为 indicator/calculate_indicator.py 所需格式，
并返回计算后的完整指标 DataFrame。
"""
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from core.logger import get_logger

logger = get_logger(__name__)

# 将 indicator 目录加入 sys.path
# 本地开发: indicator/ 在项目根目录
# Docker 容器: indicator/ 被挂载到 /app/indicator
INDICATOR_DIR_LOCAL = Path(__file__).parent.parent.parent / "indicator"
INDICATOR_DIR_DOCKER = Path("/app/indicator")

if INDICATOR_DIR_DOCKER.exists():
    INDICATOR_DIR = INDICATOR_DIR_DOCKER
elif INDICATOR_DIR_LOCAL.exists():
    INDICATOR_DIR = INDICATOR_DIR_LOCAL
else:
    # 尝试本地路径
    INDICATOR_DIR = INDICATOR_DIR_LOCAL

if str(INDICATOR_DIR) not in sys.path:
    sys.path.insert(0, str(INDICATOR_DIR))


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    将 data_loader 返回的 DataFrame 适配为 indicator 模块所需格式
    
    输入：
        df: index=DatetimeIndex, columns=[open, high, low, close, volume]
    
    输出：
        df: columns=[date, open, high, low, close, volume, p_change, amount]
        date 为字符串 YYYY-MM-DD，按日期升序排列
    """
    df = df.copy()
    
    # 确保索引为 DatetimeIndex
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    
    # 去除时区信息
    df.index = df.index.tz_localize(None)
    
    # 按日期升序排列
    df = df.sort_index()
    
    # 生成 date 列（字符串格式 YYYY-MM-DD）
    df["date"] = df.index.strftime("%Y-%m-%d")
    
    # 确保数值列为 float64 类型（TA-Lib 需要）
    numeric_cols = ["open", "high", "low", "close", "volume"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(np.float64)
    
    # 生成 p_change 列（百分比涨跌幅）
    df["p_change"] = df["close"].pct_change() * 100
    df["p_change"] = df["p_change"].fillna(0.0).astype(np.float64)
    
    # 生成 amount 列（成交额近似值 = close * volume）
    if "amount" not in df.columns:
        df["amount"] = (df["close"] * df["volume"]).astype(np.float64)
    else:
        df["amount"] = df["amount"].astype(np.float64)
    
    # 处理 NaN 和 inf
    df = df.replace([np.inf, -np.inf], 0.0)
    df = df.fillna(0.0)
    
    return df


def calculate_indicators(
    df: pd.DataFrame,
    end_date: Optional[str] = None,
    threshold: int = 120,
    calc_threshold: Optional[int] = None
) -> pd.DataFrame:
    """
    计算技术指标
    
    Args:
        df: 已适配的 DataFrame（需含 date, open, high, low, close, volume, p_change, amount）
        end_date: 截止日期，格式 YYYY-MM-DD
        threshold: 指标计算阈值
        calc_threshold: 计算阈值
    
    Returns:
        包含所有技术指标的 DataFrame
    """
    try:
        from calculate_indicator import get_indicators
    except ImportError as e:
        logger.error(f"无法导入 calculate_indicator 模块: {e}")
        raise ImportError(
            "无法导入 indicator/calculate_indicator.py，"
            "请确保 TA-Lib 已正确安装"
        )
    
    df = prepare_dataframe(df)
    
    logger.info(f"计算技术指标: {len(df)} 条数据, end_date={end_date}, threshold={threshold}")
    
    result_df = get_indicators(
        df,
        end_date=end_date,
        threshold=threshold,
        calc_threshold=calc_threshold
    )
    
    return result_df


def get_indicator_value(
    df: pd.DataFrame,
    expression: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> pd.Series:
    """
    根据表达式获取指标值的时间序列
    
    Args:
        df: 包含所有指标的 DataFrame
        expression: 指标表达式（列名或简单算术表达式）
        start_date: 开始日期
        end_date: 结束日期
    
    Returns:
        指标值的 Series，index 为日期字符串
    """
    # 日期过滤
    if start_date:
        df = df[df["date"] >= start_date]
    if end_date:
        df = df[df["date"] <= end_date]
    
    # 白名单列名（允许在表达式中使用的列）
    ALLOWED_COLUMNS = {
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
        "cr", "cr-ma1", "cr-ma2", "cr-ma3",
        # VR
        "vr", "vr_6_sma",
        # DMA
        "dma", "dma_10_sma", "ma10", "ma50",
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
        # MA - 各种周期移动平均线
        "ma5", "ma6", "ma12", "ma20", "ma24", "ma30", "ma60", "ma120", "ma200", "ma250",
        "MA_5", "MA_6", "MA_10", "MA_12", "MA_20", "MA_24", "MA_30", "MA_60", "MA_120", "MA_200", "MA_250",
        # EMA
        "ema5", "ema10", "ema12", "ema20", "ema26", "ema60",
        "EMA_5", "EMA_10", "EMA_12", "EMA_20", "EMA_26", "EMA_60",
        # VOL MA
        "vol_5", "vol_10",
        # BIAS
        "bias", "bias_12", "bias_24",
    }
    
    # 情况1：expression 直接是列名
    if expression in df.columns:
        result = df.set_index("date")[expression]
        return result.fillna(0.0)
    
    # 情况2：表达式计算（白名单验证）
    # 解析表达式中的标识符
    import re
    identifiers = set(re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', expression))
    
    # 验证所有标识符都在白名单中
    invalid_ids = identifiers - ALLOWED_COLUMNS
    if invalid_ids:
        raise ValueError(f"表达式包含不允许的标识符: {invalid_ids}")
    
    # 验证所有标识符都存在于 df 中
    missing_cols = identifiers - set(df.columns)
    if missing_cols:
        raise ValueError(f"表达式引用了不存在的列: {missing_cols}")
    
    # 使用 pandas.eval 安全计算
    try:
        result = df.eval(expression)
        if isinstance(result, pd.DataFrame):
            raise ValueError("表达式结果必须是单列，不能是 DataFrame")
        
        result_series = pd.Series(result.values, index=df["date"].values)
        return result_series.fillna(0.0)
    except Exception as e:
        raise ValueError(f"表达式计算失败: {e}")


# 内设因子清单（在 seed 时使用）
BUILTIN_INDICATORS = [
    # RSI 系列
    {"name": "rsi", "expression": "rsi", "description": "相对强弱指数 (14日)", "category": "momentum"},
    {"name": "rsi_6", "expression": "rsi_6", "description": "相对强弱指数 (6日)", "category": "momentum"},
    {"name": "rsi_12", "expression": "rsi_12", "description": "相对强弱指数 (12日)", "category": "momentum"},
    {"name": "rsi_24", "expression": "rsi_24", "description": "相对强弱指数 (24日)", "category": "momentum"},
    # MACD 系列
    {"name": "macd", "expression": "macd", "description": "MACD 线", "category": "trend"},
    {"name": "macds", "expression": "macds", "description": "MACD 信号线", "category": "trend"},
    {"name": "macdh", "expression": "macdh", "description": "MACD 柱状图", "category": "trend"},
    # ATR
    {"name": "atr", "expression": "atr", "description": "平均真实波幅 (14日)", "category": "volatility"},
    # BOLL
    {"name": "boll", "expression": "boll", "description": "布林带中轨", "category": "volatility"},
    {"name": "boll_ub", "expression": "boll_ub", "description": "布林带上轨", "category": "volatility"},
    {"name": "boll_lb", "expression": "boll_lb", "description": "布林带下轨", "category": "volatility"},
    # KDJ
    {"name": "kdjk", "expression": "kdjk", "description": "KDJ K值", "category": "momentum"},
    {"name": "kdjd", "expression": "kdjd", "description": "KDJ D值", "category": "momentum"},
    {"name": "kdjj", "expression": "kdjj", "description": "KDJ J值", "category": "momentum"},
    # WR
    {"name": "wr_14", "expression": "wr_14", "description": "威廉指标 (14日)", "category": "momentum"},
    # CCI
    {"name": "cci", "expression": "cci", "description": "商品通道指数 (14日)", "category": "momentum"},
    # DMI
    {"name": "adx", "expression": "adx", "description": "平均趋向指数", "category": "trend"},
    # VR
    {"name": "vr", "expression": "vr", "description": "成交量变异率", "category": "volume"},
    # OBV
    {"name": "obv", "expression": "obv", "description": "能量潮指标", "category": "volume"},
    # ROC
    {"name": "roc", "expression": "roc", "description": "变动率指标 (12日)", "category": "momentum"},
    # PSY
    {"name": "psy", "expression": "psy", "description": "心理线指标 (12日)", "category": "sentiment"},
    # Supertrend
    {"name": "supertrend", "expression": "supertrend", "description": "超级趋势指标", "category": "trend"},
]
