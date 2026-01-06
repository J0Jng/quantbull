"""轮动策略（动量 Top1）

使用方式：
    POST /api/backtest/run
    {
      "universe_mode": "manual",
      "symbols": ["000001", "600000", "600036", "000002"],
      "start_date": "2024-01-01",
      "end_date": "2024-12-31",
      "strategy_mode": "builtin",
      "strategy_name": "rotation_momentum_top1",
      "initial_cash": 1000000,
      "parameters": {
        "lookback": 60,
        "rebalance_frequency": "M"
      }
    }

每次调仓选近 lookback 收益最高的 1 个持有。
这是最简版本的轮动策略，使用价格动量作为轮动信号。
"""
import backtrader as bt
from strategies.portfolio_base import PortfolioStrategyBase


class RotationMomentumTop1Strategy(PortfolioStrategyBase):
    """
    动量轮动策略 - Top1
    
    参数：
        lookback: 动量计算回看期（默认 60）
        rebalance_frequency: 再平衡频率 D/W/M（默认 M）
    
    逻辑：
        每次调仓选近 lookback 日收益最高的 1 只标的全仓持有
    """
    
    params = (
        ("lookback", 60),
        ("rebalance_frequency", "M"),
        ("allocation", "equal_weight"),
        ("allow_short", False),
    )
    
    def __init__(self):
        super().__init__()
        self.order = None
        self.last_selected_symbol = None  # 记录最后选中的标的
    
    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Rejected]:
            self.order = None
    
    def find_top_momentum(self):
        """找出动量最高的标的"""
        best_data = None
        best_mom = float("-inf")
        
        for d in self.datas:
            if len(d) < self.params.lookback:
                continue
            
            mom = self.calculate_momentum(d, self.params.lookback)
            if mom > best_mom:
                best_mom = mom
                best_data = d
        
        return best_data
    
    def next(self):
        if self.order:
            return
        
        if len(self.datas) == 1:
            # 单标的直接买入持有
            d = self.datas[0]
            if not self.getposition(d).size:
                self.order = self.buy(d)
            return
        
        if not self.is_rebalance_day():
            return
        
        # 找出动量最高的
        top_data = self.find_top_momentum()
        
        if top_data:
            self.last_selected_symbol = top_data._name
            # 只持有这一只
            weights = {top_data._name: 1.0}
            self.rebalance_to_weights(weights)
        else:
            self.last_selected_symbol = None
            self.close_all_positions()
        
        self.mark_rebalance()


# 为了兼容 strategy_loader 的查找逻辑
Strategy = RotationMomentumTop1Strategy
