"""Legacy 信号策略包装器

将 legacy_strategies/ 中的 pandas 布尔信号函数包装为 Backtrader 可运行的策略。
支持通过参数指定具体的信号函数、持仓周期等。
"""
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

import backtrader as bt
import pandas as pd
import numpy as np

# 将 legacy_strategies 目录加入 sys.path
LEGACY_DIR = Path(__file__).parent.parent / "legacy_strategies"
if str(LEGACY_DIR) not in sys.path:
    sys.path.insert(0, str(LEGACY_DIR))


class LegacySignalWrapper(bt.Strategy):
    """
    Legacy 信号策略包装器
    
    将 pandas 布尔信号函数包装为 Backtrader 策略。
    
    参数：
        signal_func: 信号函数，签名为 func(code_name, data, date, **kwargs) -> bool
        signal_module: 信号模块名（用于动态导入）
        signal_func_name: 信号函数名（用于动态导入）
        threshold: 回看周期
        hold_bars: 持仓周期（买入后持有多少根 K 线后卖出）
        printlog: 是否打印日志
        data_buffer: 数据缓冲区大小（需要多少历史数据）
    """
    
    params = (
        ("signal_func", None),  # 直接传入函数
        ("signal_module", None),  # 信号模块名
        ("signal_func_name", "check"),  # 信号函数名
        ("threshold", 60),  # 回看周期
        ("hold_bars", 10),  # 持仓周期
        ("printlog", False),  # 是否打印日志
        ("data_buffer", 300),  # 数据缓冲区大小
        ("code_name", ("000001", "测试股票")),  # 股票代码
        # 可选：止损止盈
        ("stop_loss", None),  # 止损比例，如 0.05 表示 5%
        ("take_profit", None),  # 止盈比例，如 0.1 表示 10%
        # 信号函数额外参数（用于支持可配置的策略参数）
        ("limit_down_pct", -9.5),  # 跌停阈值（百分数）
        ("vol_ratio_max", 0.5),  # 地量阈值
        ("min_amount", 200000000),  # 最小成交额
    )
    
    def __init__(self):
        """初始化策略"""
        # 解析信号函数
        self._signal_func = self._resolve_signal_func()
        
        # 订单和持仓跟踪
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.bars_since_buy = 0
    
    def _resolve_signal_func(self) -> Callable:
        """解析信号函数"""
        # 情况1：直接传入函数
        if self.params.signal_func is not None:
            return self.params.signal_func
        
        # 情况2：通过模块名和函数名动态导入
        if self.params.signal_module:
            try:
                module = __import__(self.params.signal_module)
                func = getattr(module, self.params.signal_func_name)
                return func
            except (ImportError, AttributeError) as e:
                raise ValueError(
                    f"无法导入信号函数: {self.params.signal_module}.{self.params.signal_func_name}, "
                    f"错误: {e}"
                )
        
        raise ValueError("必须提供 signal_func 或 signal_module 参数")
    
    def _build_dataframe(self) -> pd.DataFrame:
        """
        从 Backtrader 数据源构建 pandas DataFrame
        
        构建包含以下列的 DataFrame：
        - date: 字符串格式 YYYY-MM-DD
        - open, high, low, close, volume
        - p_change: 百分比涨跌幅
        - amount: 成交额（近似值）
        """
        # 确定数据长度
        data_len = min(len(self.data), self.params.data_buffer)
        
        if data_len < 2:
            return pd.DataFrame()
        
        # 构建数据列表
        records = []
        for i in range(-data_len + 1, 1):  # 从最早到当前
            try:
                dt = bt.num2date(self.data.datetime[i])
                date_str = dt.strftime("%Y-%m-%d")
                
                open_price = self.data.open[i]
                high_price = self.data.high[i]
                low_price = self.data.low[i]
                close_price = self.data.close[i]
                volume = self.data.volume[i]
                
                records.append({
                    "date": date_str,
                    "open": open_price,
                    "high": high_price,
                    "low": low_price,
                    "close": close_price,
                    "volume": volume,
                })
            except IndexError:
                continue
        
        if not records:
            return pd.DataFrame()
        
        df = pd.DataFrame(records)
        
        # 计算 p_change（百分数形式，如 -9.5 表示跌 9.5%）
        df["p_change"] = df["close"].pct_change() * 100
        df["p_change"] = df["p_change"].fillna(0.0)
        
        # 计算 amount（成交额）
        # 注意：Tushare 返回的 volume 单位是"手"（1手=100股），需要转换为股数再乘以价格
        # amount = close * volume * 100（手转股）
        df["amount"] = df["close"] * df["volume"] * 100
        
        # 处理 NaN
        df = df.fillna(0.0)
        
        return df
    
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
                self.bars_since_buy = 0
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
        
        current_date = bt.num2date(self.datas[0].datetime[0]).date()
        
        # 有持仓时的逻辑
        if self.position:
            self.bars_since_buy += 1
            
            # 检查止损
            if self.params.stop_loss and self.buyprice:
                current_price = self.data.close[0]
                loss_pct = (current_price - self.buyprice) / self.buyprice
                if loss_pct < -self.params.stop_loss:
                    self.log(f"触发止损, 当前价格: {current_price:.2f}, 亏损: {loss_pct*100:.2f}%")
                    self.order = self.sell()
                    return
            
            # 检查止盈
            if self.params.take_profit and self.buyprice:
                current_price = self.data.close[0]
                profit_pct = (current_price - self.buyprice) / self.buyprice
                if profit_pct > self.params.take_profit:
                    self.log(f"触发止盈, 当前价格: {current_price:.2f}, 盈利: {profit_pct*100:.2f}%")
                    self.order = self.sell()
                    return
            
            # 检查持仓周期
            if self.bars_since_buy >= self.params.hold_bars:
                self.log(f"持仓周期到期 ({self.params.hold_bars} bars), 卖出")
                self.order = self.sell()
                return
        
        else:
            # 无持仓时，检查买入信号
            df = self._build_dataframe()
            
            if df.empty or len(df) < self.params.threshold:
                # 数据不足时记录日志（便于调试）
                if self.params.printlog:
                    self.log(f"[SKIP] 数据不足: len(df)={len(df) if not df.empty else 0}, threshold={self.params.threshold}")
                return
            
            # 调用 legacy 信号函数
            try:
                signal = self._signal_func(
                    self.params.code_name,
                    df,
                    date=current_date,
                    threshold=self.params.threshold,
                    limit_down_pct=self.params.limit_down_pct,
                    vol_ratio_max=self.params.vol_ratio_max,
                    min_amount=self.params.min_amount,
                )
            except TypeError:
                # 兼容不支持新参数的旧信号函数
                signal = self._signal_func(
                    self.params.code_name,
                    df,
                    date=current_date,
                    threshold=self.params.threshold,
                )
            except Exception as e:
                self.log(f"信号函数执行错误: {e}")
                return
            
            # 调试日志：记录每日关键数据（仅在 printlog=True 时）
            if self.params.printlog and len(df) > 0:
                last_row = df.iloc[-1]
                # 额外添加 open/close 信息用于调试
                self.log(
                    f"[CHECK] p_change={last_row.get('p_change', 0):.2f}%, "
                    f"amount={last_row.get('amount', 0)/1e8:.2f}亿, "
                    f"open={last_row.get('open', 0):.2f}, close={last_row.get('close', 0):.2f}, "
                    f"signal={signal}"
                )
            
            if signal:
                self.log(f"买入信号, 价格: {self.data.close[0]:.2f}")
                self.order = self.buy()
    
    def stop(self):
        """策略结束"""
        self.log(
            f"期末总资产: {self.broker.getvalue():.2f}, "
            f"总收益率: {(self.broker.getvalue() / self.broker.startingcash - 1) * 100:.2f}%",
            dt=bt.num2date(self.datas[0].datetime[0]).date()
        )


def create_legacy_strategy(
    signal_module: str,
    signal_func_name: str = "check",
    strategy_name: str = None,
    default_threshold: int = 60,
    default_hold_bars: int = 10,
    default_data_buffer: int = 300,
) -> type:
    """
    工厂函数：创建特定 legacy 信号的 Backtrader 策略类
    
    Args:
        signal_module: legacy_strategies 下的模块名（如 "turtle_trade"）
        signal_func_name: 信号函数名（如 "check_enter"）
        strategy_name: 策略类名（可选）
        default_threshold: 默认回看周期
        default_hold_bars: 默认持仓周期
        default_data_buffer: 默认数据缓冲区大小
    
    Returns:
        Backtrader 策略类
    """
    class_name = strategy_name or f"Legacy{signal_module.title().replace('_', '')}Strategy"
    
    # 动态导入模块
    try:
        module = __import__(signal_module)
        signal_func = getattr(module, signal_func_name)
    except (ImportError, AttributeError) as e:
        raise ValueError(f"无法导入 {signal_module}.{signal_func_name}: {e}")
    
    # 创建策略类
    class LegacyStrategy(LegacySignalWrapper):
        params = (
            ("signal_func", signal_func),
            ("signal_module", signal_module),
            ("signal_func_name", signal_func_name),
            ("threshold", default_threshold),
            ("hold_bars", default_hold_bars),
            ("printlog", False),
            ("data_buffer", default_data_buffer),
            ("code_name", ("000001", "测试股票")),
            ("stop_loss", None),
            ("take_profit", None),
        )
    
    LegacyStrategy.__name__ = class_name
    LegacyStrategy.__qualname__ = class_name
    
    return LegacyStrategy


# 导出包装器
Strategy = LegacySignalWrapper
