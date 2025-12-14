"""指标提取服务 - 从 Backtrader 回测结果提取指标和 AI 评价数据"""
import numpy as np
from typing import Optional

import backtrader as bt

from core.logger import get_logger
from schemas.backtest import AIReviewData

logger = get_logger(__name__)


class MetricsExtractor:
    """指标提取器"""
    
    def __init__(self, cerebro: bt.Cerebro, strategy: bt.Strategy):
        """
        初始化指标提取器
        
        Args:
            cerebro: Backtrader Cerebro 实例
            strategy: 策略实例
        """
        self.cerebro = cerebro
        self.strategy = strategy
    
    def extract_basic_metrics(self) -> dict:
        """
        提取基础回测指标
        
        Returns:
            包含基础指标的字典
        """
        try:
            # 获取回测结果
            results = self.cerebro.run()
            if not results:
                raise ValueError("回测未产生结果")
            
            # 获取策略实例（可能有多个，取第一个）
            strategy_instance = results[0][0] if isinstance(results[0], list) else results[0]
            
            # 获取初始和最终资产
            initial_cash = self.cerebro.broker.getcash()
            final_value = self.cerebro.broker.getvalue()
            
            # 计算总收益率
            total_return = (final_value / initial_cash - 1) * 100 if initial_cash > 0 else 0
            
            # 获取净值曲线
            equity_curve = self._get_equity_curve(strategy_instance)
            
            # 计算年化收益率
            trading_days = len(equity_curve)
            years = trading_days / 252.0  # 假设一年252个交易日
            annual_return = ((final_value / initial_cash) ** (1 / years) - 1) * 100 if years > 0 and initial_cash > 0 else None
            
            # 计算夏普比率
            sharpe_ratio = self._calculate_sharpe_ratio(equity_curve)
            
            # 计算最大回撤
            max_drawdown = self._calculate_max_drawdown(equity_curve)
            
            return {
                "initial_cash": initial_cash,
                "final_value": final_value,
                "total_return": round(total_return, 4),
                "annual_return": round(annual_return, 4) if annual_return else None,
                "sharpe_ratio": round(sharpe_ratio, 4) if sharpe_ratio else None,
                "max_drawdown": round(max_drawdown, 4),
                "trading_days": trading_days
            }
            
        except Exception as e:
            logger.error(f"提取基础指标失败: {e}", exc_info=True)
            raise
    
    def extract_ai_review_data(self) -> AIReviewData:
        """
        提取 AI 评价所需的结构化数据
        
        Returns:
            AIReviewData 对象
        """
        try:
            results = self.cerebro.run()
            strategy_instance = results[0][0] if isinstance(results[0], list) else results[0]
            
            # 获取交易记录
            trades = self._get_trades(strategy_instance)
            
            # 计算策略类型
            strategy_type = self._classify_strategy_type(trades)
            
            # 计算平均持仓天数
            holding_periods = self._calculate_holding_periods(trades)
            holding_period_days_avg = np.mean(holding_periods) if holding_periods else 0
            
            # 交易次数
            trade_count = len(trades)
            
            # 计算胜率
            win_rate = self._calculate_win_rate(trades)
            
            # 计算盈亏比
            profit_loss_ratio = self._calculate_profit_loss_ratio(trades)
            
            # 计算波动率
            equity_curve = self._get_equity_curve(strategy_instance)
            volatility = self._calculate_volatility(equity_curve)
            
            # 最大连续亏损
            max_consecutive_loss = self._calculate_max_consecutive_loss(trades)
            
            # 回撤持续时间
            drawdown_duration_days = self._calculate_drawdown_duration(equity_curve)
            
            # 收益回撤比
            metrics = self.extract_basic_metrics()
            annual_return = metrics.get("annual_return", 0) or 0
            max_drawdown = abs(metrics.get("max_drawdown", 0))
            return_over_drawdown = annual_return / max_drawdown if max_drawdown > 0 else 0
            
            return AIReviewData(
                strategy_type=strategy_type,
                holding_period_days_avg=round(holding_period_days_avg, 2),
                trade_count=trade_count,
                win_rate=round(win_rate, 4),
                profit_loss_ratio=round(profit_loss_ratio, 4),
                volatility=round(volatility, 4),
                max_consecutive_loss=max_consecutive_loss,
                drawdown_duration_days=drawdown_duration_days,
                return_over_drawdown=round(return_over_drawdown, 4)
            )
            
        except Exception as e:
            logger.error(f"提取 AI 评价数据失败: {e}", exc_info=True)
            raise
    
    def _get_equity_curve(self, strategy: bt.Strategy) -> list[float]:
        """获取净值曲线"""
        # 注意：Backtrader 不直接提供历史净值曲线
        # 这里返回一个简化的净值曲线（基于最终结果）
        # 实际应用中，需要在策略中记录每日净值
        initial_cash = self.cerebro.broker.startingcash
        final_value = self.cerebro.broker.getvalue()
        
        # 返回初始和最终值（简化实现）
        # 实际应该从策略的观察者（Observer）中获取
        return [initial_cash, final_value]
    
    def _calculate_sharpe_ratio(self, equity_curve: list[float]) -> Optional[float]:
        """计算夏普比率"""
        if len(equity_curve) < 2:
            return None
        
        returns = np.diff(equity_curve) / equity_curve[:-1]
        if len(returns) == 0 or np.std(returns) == 0:
            return None
        
        # 年化夏普比率（假设252个交易日）
        mean_return = np.mean(returns) * 252
        std_return = np.std(returns) * np.sqrt(252)
        
        if std_return == 0:
            return None
        
        sharpe = mean_return / std_return
        return sharpe
    
    def _calculate_max_drawdown(self, equity_curve: list[float]) -> float:
        """计算最大回撤（百分比）"""
        if len(equity_curve) < 2:
            return 0.0
        
        peak = equity_curve[0]
        max_dd = 0.0
        
        for value in equity_curve:
            if value > peak:
                peak = value
            dd = (peak - value) / peak if peak > 0 else 0
            if dd > max_dd:
                max_dd = dd
        
        return max_dd * 100  # 转换为百分比
    
    def _get_trades(self, strategy: bt.Strategy) -> list[dict]:
        """获取交易记录"""
        trades = []
        
        # Backtrader 的 broker 可能没有直接的 trades 属性
        # 尝试从 broker 获取交易记录
        try:
            # 方法1：尝试从 broker 的 trades 属性获取
            if hasattr(self.cerebro.broker, 'trades'):
                for trade in self.cerebro.broker.trades:
                    if hasattr(trade, 'isclosed') and trade.isclosed:
                        trades.append({
                            "entry_date": trade.dtopen.strftime("%Y-%m-%d") if hasattr(trade, 'dtopen') and trade.dtopen else None,
                            "exit_date": trade.dtclose.strftime("%Y-%m-%d") if hasattr(trade, 'dtclose') and trade.dtclose else None,
                            "entry_price": trade.price if hasattr(trade, 'price') else 0,
                            "exit_price": trade.price if hasattr(trade, 'price') else 0,
                            "size": trade.size if hasattr(trade, 'size') else 0,
                            "profit": trade.pnl if hasattr(trade, 'pnl') else 0,
                            "profit_comm": trade.pnlcomm if hasattr(trade, 'pnlcomm') else 0,
                            "is_long": trade.size > 0 if hasattr(trade, 'size') else True
                        })
        except (AttributeError, TypeError):
            # 如果无法获取交易记录，返回空列表
            logger.warning("无法从 broker 获取交易记录，返回空列表")
            pass
        
        return trades
    
    def _classify_strategy_type(self, trades: list[dict]) -> str:
        """分类策略类型"""
        if not trades:
            return "unknown"
        
        # 计算平均持仓周期
        periods = self._calculate_holding_periods(trades)
        if not periods:
            return "unknown"
        
        avg_period = np.mean(periods)
        
        # 根据持仓周期分类
        if avg_period < 5:
            return "scalping"  # 超短线
        elif avg_period < 20:
            return "day_trading"  # 日内/短线
        elif avg_period < 60:
            return "swing_trading"  # 波段
        else:
            return "trend_following"  # 趋势跟踪
    
    def _calculate_holding_periods(self, trades: list[dict]) -> list[float]:
        """计算持仓周期（天数）"""
        periods = []
        for trade in trades:
            entry_date = trade.get("entry_date")
            exit_date = trade.get("exit_date")
            if entry_date and exit_date:
                try:
                    from datetime import datetime
                    entry = datetime.strptime(entry_date, "%Y-%m-%d")
                    exit = datetime.strptime(exit_date, "%Y-%m-%d")
                    days = (exit - entry).days
                    if days > 0:
                        periods.append(float(days))
                except Exception:
                    pass
        return periods
    
    def _calculate_win_rate(self, trades: list[dict]) -> float:
        """计算胜率（0-1）"""
        if not trades:
            return 0.0
        
        wins = sum(1 for t in trades if t.get("profit", 0) > 0 or t.get("profit_comm", 0) > 0)
        return wins / len(trades)
    
    def _calculate_profit_loss_ratio(self, trades: list[dict]) -> float:
        """计算盈亏比"""
        if not trades:
            return 0.0
        
        # 使用 profit_comm（包含手续费）或 profit
        profits = [
            t.get("profit_comm", t.get("profit", 0)) 
            for t in trades 
            if t.get("profit_comm", t.get("profit", 0)) > 0
        ]
        losses = [
            abs(t.get("profit_comm", t.get("profit", 0))) 
            for t in trades 
            if t.get("profit_comm", t.get("profit", 0)) < 0
        ]
        
        if not profits or not losses:
            return 0.0
        
        avg_profit = np.mean(profits)
        avg_loss = np.mean(losses)
        
        return avg_profit / avg_loss if avg_loss > 0 else 0.0
    
    def _calculate_volatility(self, equity_curve: list[float]) -> float:
        """计算波动率"""
        if len(equity_curve) < 2:
            return 0.0
        
        returns = np.diff(equity_curve) / equity_curve[:-1]
        return np.std(returns) * np.sqrt(252) * 100  # 年化波动率（百分比）
    
    def _calculate_max_consecutive_loss(self, trades: list[dict]) -> int:
        """计算最大连续亏损次数"""
        if not trades:
            return 0
        
        max_consecutive = 0
        current_consecutive = 0
        
        for trade in trades:
            profit = trade.get("profit_comm", trade.get("profit", 0))
            if profit < 0:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return max_consecutive
    
    def _calculate_drawdown_duration(self, equity_curve: list[float]) -> int:
        """计算最大回撤持续时间（天）"""
        if len(equity_curve) < 2:
            return 0
        
        peak = equity_curve[0]
        peak_idx = 0
        max_duration = 0
        current_duration = 0
        
        for i, value in enumerate(equity_curve):
            if value > peak:
                peak = value
                peak_idx = i
                current_duration = 0
            else:
                if value < peak:
                    current_duration = i - peak_idx
                    max_duration = max(max_duration, current_duration)
        
        return max_duration
