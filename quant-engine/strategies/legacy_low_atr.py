"""Legacy 低ATR成长策略（Low ATR Growth）

基于 legacy_strategies/low_atr.py 的 check_low_increase 函数。
策略逻辑：波动率低但涨幅大于1.1倍时买入。

使用方式：
    POST /api/backtest/run
    {
        "stock_code": "000001",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "strategy_mode": "builtin",
        "strategy_name": "legacy_low_atr",
        "parameters": {
            "threshold": 10,
            "hold_bars": 15
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

from legacy_strategies.low_atr import check_low_increase
from strategies.legacy_signal_wrapper import LegacySignalWrapper


class LegacyLowAtrStrategy(LegacySignalWrapper):
    """
    低ATR成长策略
    
    策略逻辑：
    - 必须至少上市交易 250 日
    - 最近 threshold 日的最高收盘价比最低收盘价高 1.1 倍
    - ATR（平均波动率）< 10%
    - 持有 hold_bars 根 K 线后卖出
    
    注意：此策略需要至少 250 日历史数据
    """
    
    params = (
        ("signal_func", check_low_increase),
        ("signal_module", "low_atr"),
        ("signal_func_name", "check_low_increase"),
        ("threshold", 10),
        ("hold_bars", 15),
        ("printlog", False),
        ("data_buffer", 300),
        ("code_name", ("000001", "测试股票")),
        ("stop_loss", 0.05),
        ("take_profit", 0.15),
    )


# 导出策略类
Strategy = LegacyLowAtrStrategy
