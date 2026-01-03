"""Legacy 持续上涨策略（Keep Increasing / MA30 Uptrend）

基于 legacy_strategies/keep_increasing.py 的 check 函数。
策略逻辑：30日均线持续向上且涨幅超过20%时买入。

使用方式：
    POST /api/backtest/run
    {
        "stock_code": "000001",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "strategy_mode": "builtin",
        "strategy_name": "legacy_keep_increasing",
        "parameters": {
            "threshold": 30,
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

from legacy_strategies.keep_increasing import check
from strategies.legacy_signal_wrapper import LegacySignalWrapper


class LegacyKeepIncreasingStrategy(LegacySignalWrapper):
    """
    持续上涨策略（均线多头）
    
    策略逻辑：
    - 30日前MA30 < 20日前MA30 < 10日前MA30 < 当日MA30
    - 当日MA30 / 30日前MA30 > 1.2（涨幅超过20%）
    - 持有 hold_bars 根 K 线后卖出
    """
    
    params = (
        ("signal_func", check),
        ("signal_module", "keep_increasing"),
        ("signal_func_name", "check"),
        ("threshold", 30),
        ("hold_bars", 10),
        ("printlog", False),
        ("data_buffer", 300),
        ("code_name", ("000001", "测试股票")),
        ("stop_loss", None),
        ("take_profit", None),
    )


# 导出策略类
Strategy = LegacyKeepIncreasingStrategy
