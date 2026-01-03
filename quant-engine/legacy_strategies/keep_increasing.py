#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
持续上涨策略（MA30 向上）

原始文件：strategy/keep_increasing.py
迁入 quant-engine/legacy_strategies/
"""

import numpy as np
import talib as tl
import logging

logger = logging.getLogger(__name__)

__author__ = 'myh '
__date__ = '2023/3/10 '


def check(code_name, data, date=None, threshold=30):
    """
    持续上涨（均线多头）信号检测
    
    条件：
    1. 30日前的30日均线 < 20日前的30日均线 < 10日前的30日均线 < 当日的30日均线
    2. 当日的30日均线 / 30日前的30日均线 > 1.2
    
    Args:
        code_name: 股票代码元组 (code, name) 或仅 code
        data: DataFrame，需含 date/close 等列
        date: 截止日期
        threshold: 回看周期（默认 30 日）
    
    Returns:
        bool: 是否满足持续上涨条件
    """
    if date is None:
        end_date = code_name[0] if isinstance(code_name, (list, tuple)) else None
    else:
        end_date = date.strftime("%Y-%m-%d")
    
    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask].copy()
    
    # 需要至少 threshold + 30 条数据（30用于计算MA30，threshold用于分析）
    required_len = threshold + 30
    if len(data.index) < required_len:
        return False

    # 计算30日均线（需要转换为float64）
    data.loc[:, 'ma30'] = tl.MA(data['close'].values.astype(np.float64), timeperiod=30)
    data['ma30'].values[np.isnan(data['ma30'].values)] = 0.0

    # 取最后 threshold 条数据进行分析
    data = data.tail(n=threshold)
    
    # 确保取出的数据MA30都已计算完成（非0）
    if data.iloc[0]['ma30'] == 0:
        return False

    step1 = round(threshold / 3)
    step2 = round(threshold * 2 / 3)
    
    ma30_0 = data.iloc[0]['ma30']
    ma30_step1 = data.iloc[step1]['ma30']
    ma30_step2 = data.iloc[step2]['ma30']
    ma30_last = data.iloc[-1]['ma30']
    ratio = ma30_last / ma30_0 if ma30_0 > 0 else 0
    
    logger.info(f"[keep_increasing] {data.iloc[-1]['date']}: MA30[0]={ma30_0:.2f}, MA30[{step1}]={ma30_step1:.2f}, MA30[{step2}]={ma30_step2:.2f}, MA30[-1]={ma30_last:.2f}, ratio={ratio:.3f}")

    if (ma30_0 < ma30_step1 < ma30_step2 < ma30_last and ratio > 1.2):
        logger.info(f"  -> ✓ 信号触发！均线持续上涨且涨幅>{(ratio-1)*100:.1f}%")
        return True
    else:
        if ratio <= 1.2:
            logger.info(f"  -> 不满足条件: ratio={ratio:.3f} <= 1.2")
        else:
            logger.info(f"  -> 不满足条件: 均线未持续上涨")
        return False
