"""Legacy 低回撤上涨策略（Low Drawdown Rise）

基于 legacy_strategies/low_backtrace_increase.py 的 check 函数。
策略逻辑：期间涨幅>50%且回撤<20%时买入。

使用方式：
    POST /api/backtest/run
    {
        "stock_code": "000001",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "strategy_mode": "builtin",
        "strategy_name": "legacy_low_backtrace",
        "parameters": {
            "threshold": 60,
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

from legacy_strategies.low_backtrace_increase import check
from strategies.legacy_signal_wrapper import LegacySignalWrapper


class LegacyLowBacktraceStrategy(LegacySignalWrapper):
    """
    低回撤上涨策略
    
    策略逻辑：
    - 期间涨幅 > 50%
    - 无单日跌幅超过 7%
    - 无高开低走超过 7%
    - 持有 hold_bars 根 K 线后卖出
    """
    
    params = (
        ("signal_func", check),
        ("signal_module", "low_backtrace_increase"),
        ("signal_func_name", "check"),
        ("threshold", 60),
        ("hold_bars", 15),
        ("printlog", False),
        ("data_buffer", 300),
        ("code_name", ("000001", "测试股票")),
        ("stop_loss", 0.07),
        ("take_profit", 0.2),
    )


# 导出策略类
Strategy = LegacyLowBacktraceStrategy
