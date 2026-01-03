"""Legacy 回踩年线策略（MA250 Backtrace）

基于 legacy_strategies/backtrace_ma250.py 的 check 函数。
策略逻辑：价格突破年线后回踩，缩量且低点高于年线时买入。

使用方式：
    POST /api/backtest/run
    {
        "stock_code": "000001",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "strategy_mode": "builtin",
        "strategy_name": "legacy_backtrace_ma250",
        "parameters": {
            "threshold": 60,
            "hold_bars": 20,
            "data_buffer": 400,
            "printlog": true
        }
    }
    
    注意：此策略需要至少 400 天历史数据（250天MA + 60天回看 + 缓冲）
"""
import sys
from pathlib import Path

import backtrader as bt

# 将 legacy_strategies 目录加入 sys.path
LEGACY_DIR = Path(__file__).parent.parent / "legacy_strategies"
if str(LEGACY_DIR) not in sys.path:
    sys.path.insert(0, str(LEGACY_DIR))

from legacy_strategies.backtrace_ma250 import check
from strategies.legacy_signal_wrapper import LegacySignalWrapper


class LegacyBacktraceMa250Strategy(LegacySignalWrapper):
    """
    回踩年线策略
    
    策略逻辑：
    - 前段由年线(250日)以下向上突破
    - 后段在年线以上运行，最低价日与最高价日相差10-50日
    - 回踩伴随缩量：最高价日交易量/后段最低价日交易量>2
    - 持有 hold_bars 根 K 线后卖出
    
    注意：此策略需要至少 250+60 日历史数据
    """
    
    params = (
        ("signal_func", check),
        ("signal_module", "backtrace_ma250"),
        ("signal_func_name", "check"),
        ("threshold", 60),
        ("hold_bars", 20),  # 中线策略，持仓周期更长
        ("printlog", True),  # 开启日志便于调试
        ("data_buffer", 400),  # 需要足够的历史数据：250(MA)+60(threshold)+50(buffer)
        ("code_name", ("000001", "测试股票")),
        ("stop_loss", 0.08),  # 默认 8% 止损
        ("take_profit", 0.2),  # 默认 20% 止盈
    )


# 导出策略类
Strategy = LegacyBacktraceMa250Strategy
