#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
放量上涨策略（入场信号）

原始文件：strategy/enter.py
迁入 quant-engine/legacy_strategies/
"""

import numpy as np
import talib as tl
import logging

logger = logging.getLogger(__name__)

__author__ = 'myh '
__date__ = '2023/3/10 '


def check_volume(code_name, data, date=None, threshold=60):
    """
    放量上涨信号检测
    
    买入条件（需同时满足）：
    1. 当日涨幅 >= 2% 且为阳线（收盘价 >= 开盘价）
    2. 当日成交额 >= 2亿
    3. 当日成交量 / 5日均量 >= 2倍（放量）
    
    Args:
        code_name: 股票代码元组 (code, name) 或仅 code
        data: DataFrame，需含 date/close/open/volume/p_change 等列
        date: 截止日期
        threshold: 历史数据阈值
    
    Returns:
        bool: 是否满足放量上涨条件
    """
    if date is None:
        end_date = code_name[0] if isinstance(code_name, (list, tuple)) else None
    else:
        end_date = date.strftime("%Y-%m-%d")
    
    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask].copy()
    
    # 至少需要5天数据用于计算5日均量
    if len(data.index) < 5:
        return False

    p_change = data.iloc[-1]['p_change']
    last_open = data.iloc[-1]['open']
    last_close = data.iloc[-1]['close']
    
    logger.info(f"[enter.check_volume] {data.iloc[-1]['date']}: p_change={p_change:.2f}%, open={last_open:.2f}, close={last_close:.2f}, close>open={last_close>last_open}")
    
    if p_change < 2 or last_close < last_open:
        logger.info(f"  -> 不满足条件: p_change<2 or close<open")
        return False

    # 计算5日均量
    data.loc[:, 'vol_ma5'] = tl.MA(data['volume'].values.astype(np.float64), timeperiod=5)
    data['vol_ma5'].values[np.isnan(data['vol_ma5'].values)] = 0.0

    # 获取最后一天的数据（当日）
    last_row = data.iloc[-1]
    last_close = last_row['close']
    last_vol = last_row['volume']
    last_vol_ma5 = last_row['vol_ma5']

    # 获取成交额（如果已经计算好则直接使用，否则计算）
    # 注意：volume 单位是"手"，需要乘100转换为股数
    if 'amount' in data.columns:
        amount = last_row['amount']
    else:
        amount = last_close * last_vol * 100

    # 成交额不低于2亿
    if amount < 200000000:
        logger.info(f"  -> 不满足条件: amount < 2亿 (实际{amount/1e8:.2f}亿)")
        return False

    # 计算成交量比率：当日成交量 / 5日均量
    vol_ratio = last_vol / last_vol_ma5 if last_vol_ma5 > 0 else 0
    
    logger.info(f"  -> vol={last_vol:.0f}, vol_ma5={last_vol_ma5:.0f}, ratio={vol_ratio:.2f}, amount={amount/1e8:.2f}亿")
    
    # 调试信息（可选）
    # print(f"[DEBUG] {last_row['date']}: vol={last_vol:.0f}, vol_ma5={last_vol_ma5:.0f}, ratio={vol_ratio:.2f}, p_change={p_change:.2f}%, amount={amount/1e8:.2f}亿")
    
    if vol_ratio >= 2:
        logger.info(f"  -> ✓ 信号触发！")
        return True
    else:
        logger.info(f"  -> 不满足条件: vol_ratio < 2")
        return False
