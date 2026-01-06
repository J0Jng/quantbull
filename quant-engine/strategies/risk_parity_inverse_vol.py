"""风险平价策略（反波动率权重）

使用方式：
    POST /api/backtest/run
    {
      "universe_mode": "manual",
      "symbols": ["000001", "600000", "000002", "600036"],
      "start_date": "2024-01-01",
      "end_date": "2024-12-31",
      "strategy_mode": "builtin",
      "strategy_name": "risk_parity_inverse_vol",
      "initial_cash": 1000000,
      "parameters": {
        "lookback": 60,
        "rebalance_frequency": "M"
      }
    }

使用 inverse-vol 作为风险平价的近似实现：
权重 w_i ∝ 1/vol_i，归一化后下单到目标仓位
"""
import backtrader as bt
from strategies.portfolio_base import PortfolioStrategyBase


class RiskParityInverseVolStrategy(PortfolioStrategyBase):
    """
    风险平价策略 - 反波动率权重
    
    参数：
        lookback: 波动率计算回看期（默认 60）
        rebalance_frequency: 再平衡频率 D/W/M（默认 M）
    
    逻辑：
        按 w_i ∝ 1/vol_i 归一化后分配仓位
        波动率越低，权重越高（风险平价的近似）
    """
    
    params = (
        ("lookback", 60),
        ("rebalance_frequency", "M"),
        ("allocation", "inverse_vol"),
        ("allow_short", False),
    )
    
    def __init__(self):
        super().__init__()
        self.order = None
    
    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Rejected]:
            self.order = None
    
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
        
        # 找出有足够数据的标的
        valid_datas = [d for d in self.datas if len(d) >= self.params.lookback]
        
        if not valid_datas:
            self.close_all_positions()
            self.mark_rebalance()
            return
        
        # 计算反波动率权重
        weights = self.calculate_inverse_vol_weight(valid_datas, self.params.lookback)
        
        if weights:
            self.rebalance_to_weights(weights)
        else:
            self.close_all_positions()
        
        self.mark_rebalance()


# 为了兼容 strategy_loader 的查找逻辑
Strategy = RiskParityInverseVolStrategy
