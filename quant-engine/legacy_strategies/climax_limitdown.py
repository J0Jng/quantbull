#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
地量跌停策略

原始文件：strategy/climax_limitdown.py
迁入 quant-engine/legacy_strategies/
"""

import numpy as np
import talib as tl

__author__ = 'myh '
__date__ = '2023/3/10 '


def check(code_name, data, date=None, threshold=60, limit_down_pct=-9.5, vol_ratio_max=0.5, min_amount=200000000):
    """
    地量跌停信号检测（逆势买入）
    
    条件：
    1. 当日跌幅 >= limit_down_pct（默认 -9.5% 即跌停）
    2. 成交量萎缩（当日成交量 / 5日均量 < vol_ratio_max）
    3. 成交额不低于 min_amount
    
    Args:
        code_name: 股票代码元组 (code, name) 或仅 code
        data: DataFrame，需含 date/close/volume/p_change 等列
        date: 截止日期
        threshold: 回看周期（默认 60 日）
        limit_down_pct: 跌停阈值，默认 -9.5（百分数）
        vol_ratio_max: 地量阈值，当日成交量/5日均量的最大值，默认 0.5
        min_amount: 最小成交额，默认 2 亿
    
    Returns:
        bool: 是否满足地量跌停条件
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

    p_change = data.iloc[-1]['p_change']
    if p_change > limit_down_pct:
        return False

    data.loc[:, 'vol_ma5'] = tl.MA(data['volume'].values, timeperiod=5)
    data['vol_ma5'].values[np.isnan(data['vol_ma5'].values)] = 0.0

    data = data.tail(n=threshold + 1)
    if len(data) < threshold + 1:
        return False

    # 最后一天收盘价
    last_close = data.iloc[-1]['close']
    # 最后一天成交量
    last_vol = data.iloc[-1]['volume']

    amount = last_close * last_vol

    # 成交额检查
    if amount < min_amount:
        return False

    data = data.head(n=threshold)
    mean_vol = data.iloc[-1]['vol_ma5']

    if mean_vol == 0:
        return False

    vol_ratio = last_vol / mean_vol
    
    # 地量条件：成交量萎缩
    if vol_ratio < vol_ratio_max:
        return True
    else:
        return False
