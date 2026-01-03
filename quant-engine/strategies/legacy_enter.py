"""Legacy 放量上涨策略（Volume Breakout）

基于 legacy_strategies/enter.py 的 check_volume 函数。
策略逻辑：当日放量上涨（涨幅>2%，成交量>=5日均量2倍，成交额>=2亿）时买入。

使用方式：
    POST /api/backtest/run
    {
        "stock_code": "000001",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "strategy_mode": "builtin",
        "strategy_name": "legacy_enter",
        "parameters": {
            "threshold": 60,
            "hold_bars": 10
        }
    }
"""
import sys
from pathlib import Path

import backtrader as bt

# 将 legacy_strategies 目录加入 sys.path
LEGACY_DIR = Path(__file__).parent.parent / "legacy_strategies"
if str(LEGACY_DIR) not in sys.path:
    sys.path.insert(0, str(LEGACY_DIR))

from legacy_strategies.enter import check_volume
from strategies.legacy_signal_wrapper import LegacySignalWrapper


class LegacyEnterStrategy(LegacySignalWrapper):
    """
    放量上涨策略
    
    策略逻辑：
    - 当日涨幅 > 2% 且收盘价 > 开盘价
    - 成交量 >= 5日均量的 2 倍
    - 成交额 >= 2 亿
    - 持有 hold_bars 根 K 线后卖出
    """
    
    params = (
        ("signal_func", check_volume),
        ("signal_module", "enter"),
        ("signal_func_name", "check_volume"),
        ("threshold", 60),
        ("hold_bars", 10),
        ("printlog", False),
        ("data_buffer", 300),
        ("code_name", ("000001", "测试股票")),
        ("stop_loss", None),
        ("take_profit", None),
    )


# 导出策略类
Strategy = LegacyEnterStrategy
