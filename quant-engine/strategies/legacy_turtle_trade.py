"""Legacy 海龟交易策略（Turtle Trading）

基于 legacy_strategies/turtle_trade.py 的 check_enter 函数。
策略逻辑：当日收盘价 >= 最近 N 日最高收盘价时买入。

使用方式：
    POST /api/backtest/run
    {
        "stock_code": "000001",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "strategy_mode": "builtin",
        "strategy_name": "legacy_turtle_trade",
        "parameters": {
            "threshold": 60,   // 回看周期
            "hold_bars": 10    // 持仓周期
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

from legacy_strategies.turtle_trade import check_enter
from strategies.legacy_signal_wrapper import LegacySignalWrapper


class LegacyTurtleTradeStrategy(LegacySignalWrapper):
    """
    海龟交易策略
    
    策略逻辑：
    - 当日收盘价 >= 最近 threshold 日最高收盘价时买入
    - 持有 hold_bars 根 K 线后卖出
    - 支持止损/止盈参数
    """
    
    params = (
        ("signal_func", check_enter),
        ("signal_module", "turtle_trade"),
        ("signal_func_name", "check_enter"),
        ("threshold", 60),
        ("hold_bars", 10),
        ("printlog", False),
        ("data_buffer", 300),
        ("code_name", ("000001", "测试股票")),
        ("stop_loss", None),
        ("take_profit", None),
    )


# 导出策略类
Strategy = LegacyTurtleTradeStrategy
