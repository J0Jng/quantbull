#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
低 ATR 成长策略

原始文件：strategy/low_atr.py
迁入 quant-engine/legacy_strategies/
"""

import logging

logger = logging.getLogger(__name__)

__author__ = 'myh '
__date__ = '2023/3/10 '


def check_low_increase(code_name, data, date=None, ma_short=30, ma_long=250, threshold=10):
    """
    低 ATR 成长信号检测
    
    条件：
    1. 必须至少上市交易 250 日
    2. 最近 threshold 个交易日的最高收盘价必须比最低收盘价高 1.1 倍
    3. ATR（平均波动率）< 10%
    
    Args:
        code_name: 股票代码元组 (code, name) 或仅 code
        data: DataFrame，需含 date/close/p_change 等列
        date: 截止日期
        ma_short: 短期均线周期
        ma_long: 长期均线周期（需要的最小历史数据量）
        threshold: 回看周期（默认 10 日）
    
    Returns:
        bool: 是否满足低 ATR 成长条件
    """
    if date is None:
        end_date = code_name[0] if isinstance(code_name, (list, tuple)) else None
    else:
        end_date = date.strftime("%Y-%m-%d")
    
    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask].copy()
    
    if len(data.index) < ma_long:
        return False

    data = data.tail(n=threshold)
    inc_days = 0
    dec_days = 0
    days_count = len(data.index)
    if days_count < threshold:
        return False

    # 区间最低点
    lowest_row = 1000000
    # 区间最高点
    highest_row = 0

    total_change = 0.0
    for _close, _p_change in zip(data['close'].values, data['p_change'].values):
        if _p_change > 0:
            total_change += abs(_p_change)
            inc_days = inc_days + 1
        elif _p_change < 0:
            total_change += abs(_p_change)
            dec_days = dec_days + 1

        # 修复：使用 if 而不是 elif，确保最高和最低都能正确更新
        if _close > highest_row:
            highest_row = _close
        if _close < lowest_row:
            lowest_row = _close

    atr = total_change / days_count if days_count > 0 else 0
    
    if lowest_row == 0 or lowest_row == 1000000:
        logger.info(f"[low_atr] 数据异常: lowest={lowest_row}")
        return False

    ratio = (highest_row - lowest_row) / lowest_row
    
    logger.info(f"[low_atr] {data.iloc[-1]['date']}: ATR={atr:.2f}%, highest={highest_row:.2f}, lowest={lowest_row:.2f}, ratio={ratio:.3f}")
    
    if atr > 10:
        logger.info(f"  -> 不满足条件: ATR={atr:.2f}% > 10%")
        return False
    
    # ratio > 1.1 表示涨幅超过110%，这个阈值太高了
    # 应该是 ratio > 0.1（涨幅10%）更合理
    if ratio > 0.1:  # 涨幅超过10%
        logger.info(f"  -> ✓ 信号触发！ATR={atr:.2f}%, 涨幅={(ratio*100):.1f}%")
        return True
    else:
        logger.info(f"  -> 不满足条件: 涨幅={(ratio*100):.1f}% <= 10%")
        return False
