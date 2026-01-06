"""组合策略基类 - 提供多标的回测的通用工具"""
import backtrader as bt
from datetime import datetime
from typing import List, Dict, Optional
import numpy as np


class PortfolioStrategyBase(bt.Strategy):
    """
    组合策略基类
    
    提供多标的回测的通用功能：
    - 再平衡日判断
    - 目标仓位下单
    - 权重计算工具
    """
    
    params = (
        ("rebalance_frequency", "M"),  # D/W/M
        ("allocation", "equal_weight"),  # equal_weight / inverse_vol
        ("allow_short", False),
        ("lookback", 60),
    )
    
    def __init__(self):
        self.last_rebalance_date = None
        self.order = None
        
    def is_rebalance_day(self) -> bool:
        """判断当前是否为再平衡日"""
        current_date = self.datas[0].datetime.date(0)
        
        if self.last_rebalance_date is None:
            return True
        
        freq = self.params.rebalance_frequency
        
        if freq == "D":
            # 每天再平衡
            return True
        elif freq == "W":
            # 每周第一个交易日
            return current_date.weekday() < self.last_rebalance_date.weekday()
        elif freq == "M":
            # 每月第一个交易日
            return current_date.month != self.last_rebalance_date.month
        
        return False
    
    def mark_rebalance(self):
        """标记已完成再平衡"""
        self.last_rebalance_date = self.datas[0].datetime.date(0)
    
    def get_data_by_name(self, name: str) -> Optional[bt.feeds.PandasData]:
        """根据名称获取 data feed"""
        for d in self.datas:
            if d._name == name:
                return d
        return None
    
    def order_target_percent_safe(self, data, target: float):
        """
        安全的目标仓位下单
        
        Args:
            data: 数据源
            target: 目标仓位比例 (0.0 - 1.0)
        """
        if target < 0 and not self.params.allow_short:
            target = 0.0
        
        self.order_target_percent(data, target=target)
    
    def calculate_equal_weight(self, selected_datas: List) -> Dict:
        """计算等权重"""
        if not selected_datas:
            return {}
        weight = 1.0 / len(selected_datas)
        return {d._name: weight for d in selected_datas}
    
    def calculate_inverse_vol_weight(self, selected_datas: List, lookback: int = None) -> Dict:
        """计算反波动率权重（风险平价近似）"""
        if not selected_datas:
            return {}
        
        lookback = lookback or self.params.lookback
        
        vols = {}
        for d in selected_datas:
            if len(d) < lookback:
                continue
            closes = [d.close[-i] for i in range(lookback)]
            returns = np.diff(closes) / closes[:-1]
            vol = np.std(returns) if len(returns) > 1 else 1.0
            vols[d._name] = vol if vol > 0 else 0.0001  # 避免除零
        
        if not vols:
            return self.calculate_equal_weight(selected_datas)
        
        # 反波动率
        inv_vols = {k: 1.0 / v for k, v in vols.items()}
        total = sum(inv_vols.values())
        
        return {k: v / total for k, v in inv_vols.items()}
    
    def calculate_momentum(self, data, lookback: int = None) -> float:
        """计算动量（收益率）"""
        lookback = lookback or self.params.lookback
        if len(data) < lookback:
            return 0.0
        return (data.close[0] / data.close[-lookback] - 1.0) * 100
    
    def calculate_volatility(self, data, lookback: int = None) -> float:
        """计算波动率"""
        lookback = lookback or self.params.lookback
        if len(data) < lookback:
            return 0.0
        closes = [data.close[-i] for i in range(lookback)]
        returns = np.diff(closes) / closes[:-1]
        return np.std(returns) * np.sqrt(252) if len(returns) > 1 else 0.0
    
    def close_all_positions(self):
        """清空所有持仓"""
        for d in self.datas:
            if self.getposition(d).size != 0:
                self.order_target_percent(d, target=0.0)
    
    def rebalance_to_weights(self, weights: Dict):
        """
        按目标权重再平衡
        
        Args:
            weights: {symbol: weight} 字典
        """
        # 先处理需要减仓的
        for d in self.datas:
            target = weights.get(d._name, 0.0)
            current_pos = self.getposition(d).size
            if current_pos > 0 and target == 0:
                self.order_target_percent(d, target=0.0)
        
        # 再处理需要加仓的
        for d in self.datas:
            target = weights.get(d._name, 0.0)
            if target > 0:
                self.order_target_percent_safe(d, target=target)
