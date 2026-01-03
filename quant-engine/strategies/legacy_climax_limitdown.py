"""Legacy 地量跌停策略（Climax Limit Down）

基于 legacy_strategies/climax_limitdown.py 的 check 函数。
策略逻辑：跌停且地量时逆势买入。

使用方式：
    POST /api/backtest/run
    {
  "stock_code": "300750",
  "start_date": "2022-01-01",
  "end_date": "2023-12-31",
  "strategy_mode": "builtin",
  "strategy_name": "legacy_climax_limitdown",
  "parameters": {
    "threshold": 60,
    "hold_bars": 5,
    "printlog": true,
    "limit_down_pct": -5,
    "vol_ratio_max": 3
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

from legacy_strategies.climax_limitdown import check
from strategies.legacy_signal_wrapper import LegacySignalWrapper


class LegacyClimaxLimitdownStrategy(LegacySignalWrapper):
    """
    地量跌停策略（逆势买入）
    
    策略逻辑：
    - 当日跌幅 >= 9.5%（跌停）
    - 成交量萎缩（当日成交量 / 5日均量 < 0.5）
    - 成交额 >= 2 亿
    - 持有 hold_bars 根 K 线后卖出
    
    风险提示：此策略为逆势策略，风险较高
    """
    
    params = (
        ("signal_func", check),
        ("signal_module", "climax_limitdown"),
        ("signal_func_name", "check"),
        ("threshold", 60),
        ("hold_bars", 5),  # 短线策略
        ("printlog", False),
        ("data_buffer", 300),
        ("code_name", ("000001", "测试股票")),
        ("stop_loss", 0.1),  # 较宽的止损
        ("take_profit", 0.15),
        # 信号函数参数
        ("limit_down_pct", -9.5),  # 跌停阈值（百分数），可通过 parameters 覆盖
        ("vol_ratio_max", 0.5),  # 地量阈值
        ("min_amount", 200000000),  # 最小成交额
    )


# 导出策略类
Strategy = LegacyClimaxLimitdownStrategy
