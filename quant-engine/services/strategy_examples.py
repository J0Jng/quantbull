"""
策略示例代码库
提供离线可用的 Backtrader 策略示例
"""

# 均线交叉策略示例
MA_CROSSOVER_EXAMPLE = """import backtrader as bt


class MovingAverageCrossover(bt.Strategy):
    \"\"\"双均线交叉策略
    
    当快速均线上穿慢速均线时买入
    当快速均线下穿慢速均线时卖出
    \"\"\"
    params = (
        ('fast_period', 10),
        ('slow_period', 30),
    )
    
    def __init__(self):
        # 快速移动平均线
        self.fast_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.fast_period
        )
        # 慢速移动平均线
        self.slow_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.slow_period
        )
        # 金叉死叉信号（注意：是 bt.indicators.CrossOver）
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)
    
    def next(self):
        # 如果没有持仓且出现金叉信号
        if not self.position:
            if self.crossover > 0:
                self.buy()
        # 如果有持仓且出现死叉信号
        elif self.crossover < 0:
            self.close()
"""

# RSI 超买超卖策略示例
RSI_STRATEGY_EXAMPLE = """import backtrader as bt


class RSIOverboughtOversold(bt.Strategy):
    \"\"\"RSI 超买超卖策略
    
    当 RSI < 超卖阈值时买入
    当 RSI > 超买阈值时卖出
    \"\"\"
    params = (
        ('rsi_period', 14),
        ('oversold', 30),
        ('overbought', 70),
    )
    
    def __init__(self):
        # RSI 指标
        self.rsi = bt.indicators.RelativeStrengthIndex(
            self.data.close,
            period=self.params.rsi_period
        )
    
    def next(self):
        # 如果没有持仓且 RSI 进入超卖区
        if not self.position:
            if self.rsi < self.params.oversold:
                self.buy()
        # 如果有持仓且 RSI 进入超买区
        elif self.rsi > self.params.overbought:
            self.close()
"""

# 带风控的趋势跟踪策略示例
RISK_CONTROL_EXAMPLE = """import backtrader as bt


class TrendFollowingWithRisk(bt.Strategy):
    \"\"\"趋势跟踪策略（带止损止盈）
    
    基于均线方向判断趋势
    设置固定百分比的止损和止盈
    \"\"\"
    params = (
        ('ma_period', 20),
        ('stop_loss_pct', 0.05),   # 5% 止损
        ('take_profit_pct', 0.10),  # 10% 止盈
    )
    
    def __init__(self):
        # 移动平均线
        self.ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.ma_period
        )
        # 记录买入价格
        self.buy_price = None
        self.order = None
    
    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buy_price = order.executed.price
                self.log(f'买入执行, 价格: {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'卖出执行, 价格: {order.executed.price:.2f}')
                self.buy_price = None
        self.order = None
    
    def next(self):
        # 如果有未完成订单，等待
        if self.order:
            return
        
        current_price = self.data.close[0]
        
        # 没有持仓时：价格在均线上方买入
        if not self.position:
            if current_price > self.ma[0]:
                self.order = self.buy()
        
        # 有持仓时：检查止损止盈
        else:
            if self.buy_price:
                # 计算收益率
                pnl_pct = (current_price - self.buy_price) / self.buy_price
                
                # 止损：亏损超过阈值
                if pnl_pct <= -self.params.stop_loss_pct:
                    self.log(f'触发止损: {pnl_pct:.2%}')
                    self.order = self.close()
                
                # 止盈：盈利超过阈值
                elif pnl_pct >= self.params.take_profit_pct:
                    self.log(f'触发止盈: {pnl_pct:.2%}')
                    self.order = self.close()
                
                # 趋势反转：价格跌破均线
                elif current_price < self.ma[0]:
                    self.log('趋势反转')
                    self.order = self.close()
    
    def log(self, txt):
        \"\"\"日志输出\"\"\"
        dt = self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')
"""

# 仓位控制策略示例
POSITION_SIZING_EXAMPLE = """import backtrader as bt


class PositionSizingStrategy(bt.Strategy):
    \"\"\"仓位控制策略
    
    根据账户净值的固定比例分配仓位
    避免单次交易风险过大
    \"\"\"
    params = (
        ('ma_fast', 10),
        ('ma_slow', 30),
        ('risk_per_trade', 0.02),  # 单次交易风险比例 2%
    )
    
    def __init__(self):
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.params.ma_fast)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.params.ma_slow)
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)
    
    def next(self):
        if not self.position:
            if self.crossover > 0:
                # 计算买入数量：风险金额 / 单股价格
                portfolio_value = self.broker.getvalue()
                risk_amount = portfolio_value * self.params.risk_per_trade
                size = int(risk_amount / self.data.close[0] / 100) * 100  # 按手取整
                
                if size > 0:
                    self.buy(size=size)
        
        elif self.crossover < 0:
            self.close()
"""


def get_strategy_examples() -> list[dict]:
    """获取所有策略示例
    
    Returns:
        list[dict]: 策略示例列表，每个元素包含 id, name, description, code, default_parameters
    """
    examples = [
        {
            "id": "ma_crossover",
            "name": "双均线交叉策略",
            "description": "经典的双均线交叉策略，当快线上穿慢线时买入，下穿时卖出。适合趋势明显的市场。",
            "code": MA_CROSSOVER_EXAMPLE.strip(),
            "default_parameters": {
                "fast_period": 10,
                "slow_period": 30
            }
        },
        {
            "id": "rsi_strategy",
            "name": "RSI 超买超卖策略",
            "description": "基于 RSI 指标的反转策略，在超卖区买入，超买区卖出。适合震荡市场。",
            "code": RSI_STRATEGY_EXAMPLE.strip(),
            "default_parameters": {
                "rsi_period": 14,
                "oversold": 30,
                "overbought": 70
            }
        },
        {
            "id": "risk_control",
            "name": "趋势跟踪（带止损止盈）",
            "description": "趋势跟踪策略结合风险管理，设置固定百分比的止损和止盈点位。",
            "code": RISK_CONTROL_EXAMPLE.strip(),
            "default_parameters": {
                "ma_period": 20,
                "stop_loss_pct": 0.05,
                "take_profit_pct": 0.10
            }
        },
        {
            "id": "position_sizing",
            "name": "仓位控制策略",
            "description": "在均线交叉策略基础上增加仓位管理，根据账户净值比例控制单次交易风险。",
            "code": POSITION_SIZING_EXAMPLE.strip(),
            "default_parameters": {
                "ma_fast": 10,
                "ma_slow": 30,
                "risk_per_trade": 0.02
            }
        }
    ]
    
    return examples
