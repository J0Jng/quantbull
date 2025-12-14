"""测试工具函数"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def create_mock_market_data(
    stock_code: str,
    start_date: str,
    end_date: str,
    base_price: float = 10.0,
    volatility: float = 0.02
) -> pd.DataFrame:
    """
    创建模拟的行情数据
    
    Args:
        stock_code: 股票代码
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        base_price: 基础价格
        volatility: 波动率
    
    Returns:
        DataFrame with columns: ['open', 'high', 'low', 'close', 'volume']
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    # 生成交易日（排除周末）
    dates = pd.bdate_range(start=start, end=end)
    
    if len(dates) == 0:
        raise ValueError(f"日期范围无效: {start_date} - {end_date}")
    
    # 生成随机价格数据
    np.random.seed(hash(f"{stock_code}_{start_date}") % 2**32)
    returns = np.random.normal(0.001, volatility, len(dates))
    prices = base_price * np.exp(np.cumsum(returns))
    
    # 生成 OHLC 数据
    data = []
    for i, date in enumerate(dates):
        close = prices[i]
        # 生成合理的 high/low
        daily_range = close * volatility * np.random.uniform(0.5, 1.5)
        high = close + daily_range * np.random.uniform(0.3, 1.0)
        low = close - daily_range * np.random.uniform(0.3, 1.0)
        open_price = low + (high - low) * np.random.uniform(0.2, 0.8)
        volume = int(np.random.uniform(1000000, 10000000))
        
        data.append({
            "date": date.date(),
            "open": round(open_price, 2),
            "high": round(high, 2),
            "low": round(low, 2),
            "close": round(close, 2),
            "volume": volume
        })
    
    df = pd.DataFrame(data)
    df.set_index("date", inplace=True)
    return df


def mock_httpx_response(data: list) -> dict:
    """创建模拟的 HTTP 响应数据"""
    return {
        "data": data,
        "code": 0,
        "msg": "success"
    }
