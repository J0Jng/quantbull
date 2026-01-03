#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
低回撤上涨策略

原始文件：strategy/low_backtrace_increase.py
迁入 quant-engine/legacy_strategies/
"""

import logging

logger = logging.getLogger(__name__)

__author__ = 'myh '
__date__ = '2023/3/10 '


def check(code_name, data, date=None, threshold=60):
    """
    低回撤上涨信号检测
    
    条件：
    1. 期间涨幅 > 50%
    2. 期间最大回撤 < 20%
    3. 无单日跌幅超过 7%
    
    Args:
        code_name: 股票代码元组 (code, name) 或仅 code
        data: DataFrame，需含 date/close/open/p_change 等列
        date: 截止日期
        threshold: 回看周期（默认 60 日）
    
    Returns:
        bool: 是否满足低回撤上涨条件
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

    if data.iloc[0]['close'] == 0:
        return False

    start_close = data.iloc[0]['close']
    end_close = data.iloc[-1]['close']
    ratio_increase = (end_close - start_close) / start_close
    
    # 期间涨幅必须超过 50%
    if ratio_increase < 0.5:
        return False

    # 检查回撤：单日跌幅超7% 或 高开低走超7%
    max_drop = 0
    max_intraday_drop = 0
    for _p_change, _close, _open in zip(data['p_change'].values, data['close'].values, data['open'].values):
        # 单日跌幅超 7%
        if _p_change < -7:
            return False
        max_drop = min(max_drop, _p_change)
        
        # 高开低走超 7%
        if _open > 0:
            intraday_drop = (_close - _open) / _open
            if intraday_drop < -0.07:
                return False
            max_intraday_drop = min(max_intraday_drop, intraday_drop)
    
    return True
