"""配对交易策略（Z-Score）

使用方式：
    POST /api/backtest/run
    {
      "universe_mode": "manual",
      "symbols": ["601398", "601939"],
      "start_date": "2024-01-01",
      "end_date": "2024-12-31",
      "strategy_mode": "builtin",
      "strategy_name": "pairs_trading_zscore",
      "initial_cash": 1000000,
      "parameters": {
        "lookback": 60,
        "entry_z": 2.0,
        "exit_z": 0.5,
        "allow_short": true
      }
    }

计算两标的价差的 z-score 进行交易：
- spread = log(A.close) - log(B.close)
- z-score 超阈值开仓，回归均值平仓

仅支持 2 标的
"""
import backtrader as bt
import numpy as np
from strategies.portfolio_base import PortfolioStrategyBase
from core.logger import get_logger

logger = get_logger(__name__)


class PairsTradingZscoreStrategy(PortfolioStrategyBase):
    """
    配对交易策略 - Z-Score
    
    参数：
        lookback: z-score 计算回看期（默认 60）
        entry_z: 开仓阈值（默认 2.0）
        exit_z: 平仓阈值（默认 0.5）
        allow_short: 是否允许做空（默认 True）
    
    逻辑：
        spread = log(A) - log(B)
        z > entry_z: 做空 A，做多 B（spread 会回归）
        z < -entry_z: 做多 A，做空 B
        |z| < exit_z: 平仓
    """
    
    params = (
        ("lookback", 60),
        ("entry_z", 2.0),
        ("exit_z", 0.5),
        ("allow_short", True),
        ("rebalance_frequency", "D"),  # 配对交易通常每日检查
        ("allocation", "equal_weight"),
    )
    
    def __init__(self):
        super().__init__()
        
        if len(self.datas) != 2:
            logger.warning(f"配对交易策略需要恰好 2 个标的，当前有 {len(self.datas)} 个")
        
        self.order = None
        self.trade_count = 0  # 记录交易次数
        self.position_state = 0  # 0: 无仓位, 1: 做多价差, -1: 做空价差
        self.pending_state = None  # 待确认的状态
        
        if not self.params.allow_short:
            logger.warning("对冲不可用（allow_short=False），策略降级：仅做 A 的多头信号")
    
    def notify_order(self, order):
        """订单状态通知 - 在此更新position_state"""
        if order.status == order.Completed:
            # 订单成功执行，更新状态
            if self.pending_state is not None:
                self.position_state = self.pending_state
                self.pending_state = None
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            # 订单失败，重置
            self.pending_state = None
        
        if order.status in [order.Completed, order.Canceled, order.Rejected]:
            self.order = None
    
    def calculate_spread(self):
        """计算价差 log(A) - log(B)"""
        if len(self.datas) != 2:
            return None
        
        a = self.datas[0]
        b = self.datas[1]
        
        if a.close[0] <= 0 or b.close[0] <= 0:
            return None
        
        return np.log(a.close[0]) - np.log(b.close[0])
    
    def calculate_zscore(self):
        """计算价差的 z-score"""
        if len(self.datas) != 2:
            return None
        
        a = self.datas[0]
        b = self.datas[1]
        
        lookback = self.params.lookback
        if len(a) < lookback or len(b) < lookback:
            return None
        
        # 计算历史价差
        spreads = []
        for i in range(lookback):
            if a.close[-i] > 0 and b.close[-i] > 0:
                spreads.append(np.log(a.close[-i]) - np.log(b.close[-i]))
        
        if len(spreads) < 2:
            return None
        
        spread_mean = np.mean(spreads)
        spread_std = np.std(spreads)
        
        if spread_std == 0:
            return 0.0
        
        current_spread = self.calculate_spread()
        if current_spread is None:
            return None
        
        return (current_spread - spread_mean) / spread_std
    
    def next(self):
        if self.order:
            return
        
        if len(self.datas) != 2:
            # 非配对模式，不操作
            return
        
        z = self.calculate_zscore()
        if z is None:
            return
        
        a = self.datas[0]
        b = self.datas[1]
        
        allow_short = self.params.allow_short
        entry_z = self.params.entry_z
        exit_z = self.params.exit_z
        
        # 当前仓位状态
        pos_a = self.getposition(a).size
        pos_b = self.getposition(b).size
        
        if self.position_state == 0:
            # 无仓位，检查开仓信号
            if z > entry_z:
                # 价差过高，做空价差：做空 A，做多 B
                if allow_short:
                    self.order_target_percent(a, target=-0.3)  # 降低至30%避免保证金不足
                    self.order_target_percent(b, target=0.3)
                    self.pending_state = -1
                    self.trade_count += 1
                else:
                    # 降级：不做操作
                    pass
            elif z < -entry_z:
                # 价差过低，做多价差：做多 A，做空 B
                if allow_short:
                    self.order_target_percent(a, target=0.3)
                    self.order_target_percent(b, target=-0.3)
                    self.pending_state = 1
                    self.trade_count += 1
                else:
                    # 降级：只做多 A
                    self.order_target_percent(a, target=0.6)
                    self.pending_state = 1
                    self.trade_count += 1
        else:
            # 有仓位，检查平仓信号
            if abs(z) < exit_z:
                # 回归均值，平仓
                self.order_target_percent(a, target=0.0)
                self.order_target_percent(b, target=0.0)
                self.pending_state = 0


# 为了兼容 strategy_loader 的查找逻辑
Strategy = PairsTradingZscoreStrategy
