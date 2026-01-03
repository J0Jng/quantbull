#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
海龟交易法则策略

原始文件：strategy/turtle_trade.py
迁入 quant-engine/legacy_strategies/
"""

import logging

logger = logging.getLogger(__name__)

__author__ = 'myh '
__date__ = '2023/3/10 '

# 总市值
BALANCE = 200000


def check_enter(code_name, data, date=None, threshold=60):
    """
    海龟交易法则入场信号
    
    条件：最后一个交易日收市价为指定区间内最高价
    1. 当日收盘价 >= 最近 N 日最高收盘价
    
    Args:
        code_name: 股票代码元组 (code, name) 或仅 code
        data: DataFrame，需含 date/close 等列
        date: 截止日期
        threshold: 回看周期（默认 60 日）
    
    Returns:
        bool: 是否满足海龟入场条件
    """
    if date is None:
        end_date = code_name[0] if isinstance(code_name, (list, tuple)) else None
    else:
        end_date = date.strftime("%Y-%m-%d")
    
    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask].copy()
    
    if len(data.index) < threshold:
        return False

    data = data.tail(n=threshold)

    # 海龟交易：当前收盘价突破前N-1日最高价
    last_close = data.iloc[-1]['close']
    previous_data = data.iloc[:-1]  # 排除最后一天
    
    if len(previous_data) == 0:
        return False
    
    max_price = previous_data['close'].max()

    logger.info(f"[turtle_trade] {data.iloc[-1]['date']}: 当前={last_close:.2f}, 前{threshold-1}日最高={max_price:.2f}")

    if last_close >= max_price:
        logger.info(f"  -> ✓ 信号触发！突破前期高点")
        return True

    return False
