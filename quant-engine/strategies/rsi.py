"""RSI 策略（Relative Strength Index）"""
from typing import Any

import backtrader as bt


class RSIStrategy(bt.Strategy):
    """RSI 策略
    
    策略逻辑：
    - RSI < 30 时买入（超卖）
    - RSI > 70 时卖出（超买）
    """
    
    params: tuple[tuple[str, Any], ...] = (
        ("rsi_period", 14),      # RSI 周期
        ("rsi_low", 30),          # RSI 低位阈值
        ("rsi_high", 70),         # RSI 高位阈值
        ("printlog", False),      # 是否打印日志
    )

    @property
    def rsi_period(self) -> int:
        return int(getattr(self.params, "rsi_period", 14))

    @property
    def rsi_low(self) -> int:
        return int(getattr(self.params, "rsi_low", 30))

    @property
    def rsi_high(self) -> int:
        return int(getattr(self.params, "rsi_high", 70))

    @property
    def printlog(self) -> bool:
        return bool(getattr(self.params, "printlog", False))
    
    def __init__(self):
        """初始化指标"""
        # 计算 RSI
        # 某些类型检查器会误报 "模块不可调用"，运行时正常
        self.rsi = bt.indicators.RSI(self.data.close, period=self.rsi_period)  # type: ignore[misc]
        
        # 订单和持仓跟踪
        self.order = None
        self.buyprice = None
        self.buycomm = None
    
    def log(self, txt, dt=None):
        """日志记录"""
        if self.printlog:
            dt = dt or bt.num2date(self.datas[0].datetime[0]).date()
            print(f"{dt.isoformat()}: {txt}")
    
    def notify_order(self, order):
        """订单状态通知"""
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f"买入执行, 价格: {order.executed.price:.2f}, "
                    f"成本: {order.executed.value:.2f}, "
                    f"手续费: {order.executed.comm:.2f}, "
                    f"RSI: {self.rsi[0]:.2f}"
                )
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(
                    f"卖出执行, 价格: {order.executed.price:.2f}, "
                    f"成本: {order.executed.value:.2f}, "
                    f"手续费: {order.executed.comm:.2f}, "
                    f"RSI: {self.rsi[0]:.2f}"
                )
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("订单取消/保证金不足/拒绝")
        
        self.order = None
    
    def notify_trade(self, trade):
        """交易通知"""
        if not trade.isclosed:
            return
        
        self.log(f"交易利润, 毛利润: {trade.pnl:.2f}, 净利润: {trade.pnlcomm:.2f}")
    
    def next(self):
        """每个 bar 执行"""
        # 如果有未完成的订单，不执行新逻辑
        if self.order:
            return
        
        # 检查是否有持仓
        if not self.position:
            # 没有持仓，检查买入信号（RSI < 低位阈值）
            if self.rsi[0] < self.rsi_low:
                self.log(
                    f"买入信号 (RSI 超卖), 价格: {self.data.close[0]:.2f}, "
                    f"RSI: {self.rsi[0]:.2f}"
                )
                self.order = self.buy()
        else:
            # 有持仓，检查卖出信号（RSI > 高位阈值）
            if self.rsi[0] > self.rsi_high:
                self.log(
                    f"卖出信号 (RSI 超买), 价格: {self.data.close[0]:.2f}, "
                    f"RSI: {self.rsi[0]:.2f}"
                )
                self.order = self.sell()
    
    def stop(self):
        """策略结束"""
        self.log(
            f"期末总资产: {self.broker.getvalue():.2f}, "
            f"总收益率: {(self.broker.getvalue() / self.broker.startingcash - 1) * 100:.2f}%",
            dt=bt.num2date(self.datas[0].datetime[0]).date()
        )


# 导出策略类
Strategy = RSIStrategy
