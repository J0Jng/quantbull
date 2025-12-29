"""双均线交叉策略（Moving Average Crossover）"""
import backtrader as bt
from backtrader.indicators import CrossOver, SMA


class MACrossStrategy(bt.Strategy):
    """双均线交叉策略
    
    策略逻辑：
    - 当短期均线上穿长期均线时买入
    - 当短期均线下穿长期均线时卖出
    """
    
    params = (
        ("fast_period", 5),   # 短期均线周期
        ("slow_period", 20),  # 长期均线周期
        ("printlog", False),  # 是否打印日志
    )
    
    def __init__(self):
        """初始化指标"""
        # 计算移动平均线
        self.fast_ma = SMA(
            self.data.close,
            period=self.params.fast_period  # type: ignore[attr-defined]
        )
        self.slow_ma = SMA(
            self.data.close,
            period=self.params.slow_period  # type: ignore[attr-defined]
        )
        
        # 交叉信号
        self.crossover = CrossOver(self.fast_ma, self.slow_ma)
        
        # 订单和持仓跟踪
        self.order = None
        self.buyprice = None
        self.buycomm = None
    
    def log(self, txt, dt=None):
        """日志记录"""
        if self.params.printlog:
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
                    f"手续费: {order.executed.comm:.2f}"
                )
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(
                    f"卖出执行, 价格: {order.executed.price:.2f}, "
                    f"成本: {order.executed.value:.2f}, "
                    f"手续费: {order.executed.comm:.2f}"
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
            # 没有持仓，检查买入信号（金叉）
            if self.crossover > 0:
                self.log(f"买入信号, 价格: {self.data.close[0]:.2f}")
                self.order = self.buy()
        else:
            # 有持仓，检查卖出信号（死叉）
            if self.crossover < 0:
                self.log(f"卖出信号, 价格: {self.data.close[0]:.2f}")
                self.order = self.sell()
    
    def stop(self):
        """策略结束"""
        self.log(
            f"期末总资产: {self.broker.getvalue():.2f}, "
            f"总收益率: {(self.broker.getvalue() / self.broker.startingcash - 1) * 100:.2f}%",
            dt=bt.num2date(self.datas[0].datetime[0]).date()
        )


# 导出策略类
Strategy = MACrossStrategy
