"""均值回归策略（RSI）

使用方式：
    POST /api/backtest/run
    {
      "stock_code": "000001",
      "start_date": "2024-01-01",
      "end_date": "2024-12-31",
      "strategy_mode": "builtin",
      "strategy_name": "mean_reversion_rsi",
      "initial_cash": 1000000,
      "parameters": {
        "rsi_period": 14,
        "oversold": 30,
        "overbought": 70
      }
    }

支持单标的和多标的回测：
- 单标的：RSI < oversold 买入；RSI > overbought 清仓
- 多标的：再平衡日选 RSI < oversold 的集合等权持有
"""
import backtrader as bt
from strategies.portfolio_base import PortfolioStrategyBase


class MeanReversionRsiStrategy(PortfolioStrategyBase):
    """
    均值回归策略 - RSI 超买超卖
    
    参数：
        rsi_period: RSI 周期（默认 14）
        oversold: 超卖阈值（默认 30）
        overbought: 超买阈值（默认 70）
        rebalance_frequency: 再平衡频率 D/W/M（默认 M）
    
    信号：
        买入：RSI < oversold
        卖出：RSI > overbought
    """
    
    params = (
        ("rsi_period", 14),
        ("oversold", 30),
        ("overbought", 70),
        ("rebalance_frequency", "M"),
        ("allocation", "equal_weight"),
        ("allow_short", False),
        ("lookback", 60),
    )
    
    def __init__(self):
        super().__init__()
        
        # 为每个数据源创建 RSI 指标
        # 使用 id(d) 作为备用 key，避免 d._name 为空时的问题
        self.rsi = {}
        self._data_id_map = {}  # id(d) -> d._name 的映射
        
        for d in self.datas:
            key = d._name if d._name else id(d)
            self.rsi[key] = bt.indicators.RSI(d.close, period=self.params.rsi_period)
            self._data_id_map[id(d)] = key
        
        self.order = None
    
    def notify_order(self, order):
        """订单状态通知"""
        if order.status in [order.Completed, order.Canceled, order.Rejected]:
            self.order = None
    
    def get_rsi(self, data) -> float:
        """获取 RSI 值"""
        # 优先使用 _data_id_map 查找 key，兼容 name 为空的情况
        key = self._data_id_map.get(id(data), data._name)
        if key not in self.rsi:
            return 50.0  # 默认中性
        return self.rsi[key][0]
    
    def is_oversold(self, data) -> bool:
        """判断是否超卖"""
        return self.get_rsi(data) < self.params.oversold
    
    def is_overbought(self, data) -> bool:
        """判断是否超买"""
        return self.get_rsi(data) > self.params.overbought
    
    def next(self):
        if self.order:
            return
        
        if len(self.datas) == 1:
            self._next_single()
        else:
            self._next_multi()
    
    def _next_single(self):
        """单标的逻辑"""
        d = self.datas[0]
        pos = self.getposition(d).size
        rsi_value = self.get_rsi(d)
        
        if not pos:
            # 无持仓，超卖买入（全仓）
            if self.is_oversold(d):
                self.order = self.order_target_percent(d, target=0.95)
        else:
            # 有持仓，超买卖出（清仓）
            if self.is_overbought(d):
                self.order = self.order_target_percent(d, target=0.0)
    
    def _next_multi(self):
        """多标的逻辑"""
        if not self.is_rebalance_day():
            return
        
        # 找出所有超卖的标的
        oversold_datas = [d for d in self.datas if self.is_oversold(d)]
        
        if oversold_datas:
            weights = self.calculate_equal_weight(oversold_datas)
            self.rebalance_to_weights(weights)
        else:
            # 无超卖标的，清仓
            self.close_all_positions()
        
        self.mark_rebalance()


# 为了兼容 strategy_loader 的查找逻辑
Strategy = MeanReversionRsiStrategy
