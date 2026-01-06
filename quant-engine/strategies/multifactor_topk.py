"""多因子选股策略（最小可跑版本）

使用方式：
    POST /api/backtest/run
    {
      "universe_mode": "manual",
      "symbols": ["000001", "600000", "600036", "000002", "601398"],
      "start_date": "2024-01-01",
      "end_date": "2024-12-31",
      "strategy_mode": "builtin",
      "strategy_name": "multifactor_topk",
      "initial_cash": 1000000,
      "parameters": {
        "top_k": 3,
        "lookback": 60,
        "rebalance_frequency": "M"
      }
    }

使用价格可得的横截面因子做最小闭环：
- 因子1：近 N 日动量（收益率）
- 因子2：近 N 日波动率（反向，低波优选）
- 综合分：score = z(mom) - z(vol)

每次调仓选 top_k 等权持有
"""
import backtrader as bt
import numpy as np
from strategies.portfolio_base import PortfolioStrategyBase


class MultifactorTopkStrategy(PortfolioStrategyBase):
    """
    多因子选股策略
    
    参数：
        lookback: 因子计算回看期（默认 60）
        top_k: 选股数量（默认 10）
        rebalance_frequency: 再平衡频率 D/W/M（默认 M）
    
    因子：
        - 动量因子：近 lookback 日收益率
        - 波动因子：近 lookback 日波动率（反向）
    
    选股：
        综合分 = z-score(动量) - z-score(波动)
        选综合分最高的 top_k 只
    """
    
    params = (
        ("lookback", 60),
        ("top_k", 10),
        ("rebalance_frequency", "M"),
        ("allocation", "equal_weight"),
        ("allow_short", False),
    )
    
    def __init__(self):
        super().__init__()
        self.order = None
        self.last_selection = []  # 记录最后一次选股结果
    
    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Rejected]:
            self.order = None
    
    def calculate_factors(self):
        """计算所有标的的因子值"""
        factors = []
        
        for d in self.datas:
            if len(d) < self.params.lookback:
                continue
            
            # 动量因子：收益率
            mom = self.calculate_momentum(d, self.params.lookback)
            
            # 波动因子：波动率
            vol = self.calculate_volatility(d, self.params.lookback)
            
            factors.append({
                "data": d,
                "symbol": d._name,
                "momentum": mom,
                "volatility": vol,
            })
        
        return factors
    
    def rank_by_score(self, factors):
        """按综合分排序"""
        if not factors:
            return []
        
        # 计算 z-score
        moms = np.array([f["momentum"] for f in factors])
        vols = np.array([f["volatility"] for f in factors])
        
        # 避免除零
        mom_std = np.std(moms) if np.std(moms) > 0 else 1.0
        vol_std = np.std(vols) if np.std(vols) > 0 else 1.0
        
        z_mom = (moms - np.mean(moms)) / mom_std
        z_vol = (vols - np.mean(vols)) / vol_std
        
        # 综合分：高动量 + 低波动
        scores = z_mom - z_vol
        
        # 添加分数
        for i, f in enumerate(factors):
            f["z_mom"] = z_mom[i]
            f["z_vol"] = z_vol[i]
            f["score"] = scores[i]
        
        # 按分数降序排序
        factors.sort(key=lambda x: x["score"], reverse=True)
        
        return factors
    
    def next(self):
        if self.order:
            return
        
        if len(self.datas) == 1:
            # 单标的不适用多因子选股，直接买入持有
            d = self.datas[0]
            if not self.getposition(d).size:
                self.order = self.buy(d)
            return
        
        if not self.is_rebalance_day():
            return
        
        # 计算因子
        factors = self.calculate_factors()
        
        if not factors:
            self.close_all_positions()
            self.mark_rebalance()
            return
        
        # 排序选股
        ranked = self.rank_by_score(factors)
        top_k = ranked[:self.params.top_k]
        
        # 记录选股结果
        self.last_selection = [
            {"symbol": f["symbol"], "score": round(f["score"], 4)}
            for f in top_k
        ]
        
        # 等权持有
        selected_datas = [f["data"] for f in top_k]
        weights = self.calculate_equal_weight(selected_datas)
        self.rebalance_to_weights(weights)
        
        self.mark_rebalance()


# 为了兼容 strategy_loader 的查找逻辑
Strategy = MultifactorTopkStrategy
