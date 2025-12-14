"""Pytest 配置和共享 fixtures"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
import pandas as pd
import numpy as np

from main import create_app


@pytest.fixture
def app():
    """创建 FastAPI 应用实例"""
    return create_app()


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
def sample_market_data():
    """生成模拟的行情数据"""
    # 生成30天的模拟数据
    dates = pd.date_range(start="2023-01-01", periods=30, freq="D")
    
    # 生成随机价格数据（基于随机游走）
    np.random.seed(42)  # 固定随机种子以便测试可重复
    base_price = 10.0
    returns = np.random.normal(0.001, 0.02, len(dates))  # 平均0.1%日收益率，2%波动率
    prices = base_price * np.exp(np.cumsum(returns))
    
    # 生成 OHLC 数据
    data = []
    for i, date in enumerate(dates):
        close = prices[i]
        high = close * (1 + abs(np.random.normal(0, 0.01)))
        low = close * (1 - abs(np.random.normal(0, 0.01)))
        open_price = close * (1 + np.random.normal(0, 0.005))
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


@pytest.fixture
def sample_strategy_code():
    """示例策略代码"""
    return """
import backtrader as bt

class TestStrategy(bt.Strategy):
    params = (
        ("period", 5),
    )
    
    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=self.params.period)
        self.order = None
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        self.order = None
    
    def next(self):
        if self.order:
            return
        
        if not self.position:
            if self.data.close[0] > self.sma[0]:
                self.order = self.buy()
        else:
            if self.data.close[0] < self.sma[0]:
                self.order = self.sell()
"""


@pytest.fixture
def invalid_strategy_code():
    """无效的策略代码（语法错误）"""
    return """
import backtrader as bt

class TestStrategy(bt.Strategy):
    def next(self):
        # 语法错误：缺少引号
        print(hello world)
"""
