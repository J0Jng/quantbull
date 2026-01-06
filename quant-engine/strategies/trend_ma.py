"""趋势跟踪策略（移动平均线）

使用方式：
    POST /api/backtest/run
    {
      "universe_mode": "manual",
      "symbols": ["000001", "600000", "000002", "600036"],
      "start_date": "2024-01-01",
      "end_date": "2024-12-31",
      "strategy_mode": "builtin",
      "strategy_name": "trend_ma",
      "initial_cash": 1000000,
      "parameters": {
        "fast_period": 20,
        "slow_period": 60,
        "rebalance_frequency": "M"
      }
    }

支持单标的和多标的回测：
- 单标的：趋势为真全仓，否则清仓
- 多标的：再平衡日，对信号为真的标的等权持有
"""
import backtrader as bt
from strategies.portfolio_base import PortfolioStrategyBase


class TrendMaStrategy(PortfolioStrategyBase):
    """
    趋势跟踪策略 - 双均线趋势判断
    
    参数：
        fast_period: 快线周期（默认 20）
        slow_period: 慢线周期（默认 60）
        rebalance_frequency: 再平衡频率 D/W/M（默认 M）
    
    信号：
        趋势为真：快线 > 慢线
        趋势为假：快线 <= 慢线
    """
    
    params = (
        ("fast_period", 20),
        ("slow_period", 60),
        ("rebalance_frequency", "M"),
        ("allocation", "equal_weight"),
        ("allow_short", False),
        ("lookback", 60),
    )
    
    def __init__(self):
        super().__init__()
        
        # 为每个数据源创建均线指标
        self.fast_ma = {}
        self.slow_ma = {}
        
        for d in self.datas:
            self.fast_ma[d._name] = bt.indicators.SMA(d.close, period=self.params.fast_period)
            self.slow_ma[d._name] = bt.indicators.SMA(d.close, period=self.params.slow_period)
        
        self.order = None
    
    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Rejected]:
            self.order = None
    
    def is_trend_up(self, data) -> bool:
        """判断是否处于上升趋势"""
        name = data._name
        if name not in self.fast_ma or name not in self.slow_ma:
            return False
        return self.fast_ma[name][0] > self.slow_ma[name][0]
    
    def next(self):
        # 等待订单完成
        if self.order:
            return
        
        # 单标的模式
        if len(self.datas) == 1:
            self._next_single()
        else:
            self._next_multi()
    
    def _next_single(self):
        """单标的逻辑"""
        d = self.datas[0]
        
        if self.is_trend_up(d):
            if not self.getposition(d).size:
                self.order = self.order_target_percent(d, target=0.95)
        else:
            if self.getposition(d).size:
                self.order = self.order_target_percent(d, target=0.0)
    
    def _next_multi(self):
        """多标的逻辑"""
        if not self.is_rebalance_day():
            return
        
        # 找出所有趋势向上的标的
        trend_up_datas = [d for d in self.datas if self.is_trend_up(d)]
        
        if trend_up_datas:
            # 等权分配
            weights = self.calculate_equal_weight(trend_up_datas)
            self.rebalance_to_weights(weights)
        else:
            # 无趋势向上的标的，清仓
            self.close_all_positions()
        
        self.mark_rebalance()


# 为了兼容 strategy_loader 的查找逻辑
Strategy = TrendMaStrategy
