"""Kronos 多维度轮动策略

多维度选股 + 动态仓位管理 + 交易规则与风控

"D" = 每日轮动
"W" = 每周轮动
"M" = 每月轮动

使用方式：
    POST /api/backtest/run
    {
      "universe_mode": "stock_etf_pool",
      "universe_params": {"stock_limit": 100, "etf_limit": 30},
      "start_date": "2024-01-01",
      "end_date": "2024-12-31",
      "strategy_mode": "builtin",
      "strategy_name": "kronos_multidim_rotation",
      "initial_cash": 1000000,
      "rebalance_frequency": "D",
      "parameters": {
        "top_stocks": 10,
        "top_etfs": 5,
        "lookback": 60,
        "w_tech": 0.30,
        "w_industry": 0.25,
        "w_hot": 0.20,
        "w_fund": 0.15,
        "w_sent": 0.10,
        "risk_capital": 0.95,
        "max_leverage": 1.0,
        "force_cash": false
      }
    }

维度权重（默认）：
    技术面 30% + 行业景气 25% + 热点主线 20% + 基本面 15% + 舆情 10%

风控规则：
    - 股票止损 2%，ETF 止损 2.5%
    - 分阶段止盈：+2% 减30%，+3.5% 再减30%，+5% 再减20%，剩余20% 移动止损
    - 高波动市场暂停止损执行（ATR > 90%分位）
    - 空仓条件：市场技术分 < -0.5 或 force_cash=True
"""
import backtrader as bt
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from strategies.portfolio_base import PortfolioStrategyBase


class OBV(bt.Indicator):
    """
    On-Balance Volume (OBV) 指标
    
    计算逻辑：
    - 如果收盘价上涨，OBV += 当日成交量
    - 如果收盘价下跌，OBV -= 当日成交量
    - 如果收盘价不变，OBV 不变
    """
    lines = ('obv',)
    params = (('period', 1),)
    
    def __init__(self):
        # 需要至少2个数据点才能比较价格变化
        self.addminperiod(1)
    
    def once(self, start, end):
        """批量计算模式（优化性能）"""
        obv_array = self.lines.obv.array
        close_array = self.data.close.array
        volume_array = self.data.volume.array
        
        # 初始化第一个值
        obv_array[start] = volume_array[start]
        
        # 批量计算
        for i in range(start + 1, end):
            if close_array[i] > close_array[i - 1]:
                # 价格上涨
                obv_array[i] = obv_array[i - 1] + volume_array[i]
            elif close_array[i] < close_array[i - 1]:
                # 价格下跌
                obv_array[i] = obv_array[i - 1] - volume_array[i]
            else:
                # 价格不变
                obv_array[i] = obv_array[i - 1]
    
    def next(self):
        """逐步计算模式（实时模式）"""
        if len(self) == 1:
            # 第一个数据点，初始化为当日成交量
            self.lines.obv[0] = self.data.volume[0]
        else:
            # 计算价格变化
            if self.data.close[0] > self.data.close[-1]:
                # 价格上涨，加上成交量
                self.lines.obv[0] = self.lines.obv[-1] + self.data.volume[0]
            elif self.data.close[0] < self.data.close[-1]:
                # 价格下跌，减去成交量
                self.lines.obv[0] = self.lines.obv[-1] - self.data.volume[0]
            else:
                # 价格不变
                self.lines.obv[0] = self.lines.obv[-1]


class KronosMultidimRotationStrategy(PortfolioStrategyBase):
    """
    Kronos 多维度轮动策略
    
    核心逻辑：
    1. 多维度打分选股（技术面+行业+热点+基本面+舆情）
    2. 动态仓位管理（基于波动率和预测夏普）
    3. 严格风控（止盈止损+移动止损+波动过滤）
    """
    
    params = (
        # 选股参数
        ("top_stocks", 10),          # 股票持仓数量
        ("top_etfs", 5),             # ETF 持仓数量
        ("lookback", 60),            # 指标回看期
        ("rebalance_frequency", "D"), # 再平衡频率
        ("allocation", "score_weighted"), # 权重分配方式
        ("allow_short", False),
        
        # 维度权重
        ("w_tech", 0.30),            # 技术面权重
        ("w_industry", 0.25),        # 行业景气权重
        ("w_hot", 0.20),             # 热点主线权重
        ("w_fund", 0.15),            # 基本面权重
        ("w_sent", 0.10),            # 舆情权重
        
        # 动态仓位参数
        ("risk_capital", 0.95),      # 风险资本比例
        ("max_leverage", 1.0),       # 最大杠杆
        ("max_stock_weight", 0.10),  # 单只股票最大权重
        ("max_etf_weight", 0.15),    # 单只 ETF 最大权重
        
        # 风控参数
        ("stock_stop_loss", 0.02),   # 股票止损比例
        ("etf_stop_loss", 0.025),    # ETF 止损比例
        ("force_cash", False),       # 强制空仓
        ("market_bear_threshold", -0.5), # 市场熊市阈值
        
        # 止盈参数（分阶段）
        ("tp_stage1", 0.02),         # 第一阶段止盈 +2%
        ("tp_stage1_ratio", 0.30),   # 减仓 30%
        ("tp_stage2", 0.035),        # 第二阶段止盈 +3.5%
        ("tp_stage2_ratio", 0.30),   # 减仓 30%
        ("tp_stage3", 0.05),         # 第三阶段止盈 +5%
        ("tp_stage3_ratio", 0.20),   # 减仓 20%
        ("trailing_atr_mult", 1.5),  # 移动止损 ATR 倍数
        
        # 高波动调整
        ("high_vol_tp_adjust", 0.005), # 高波动止盈上调
        ("trend_strong_tp_adjust", 0.01), # 趋势强止盈上调
        ("trend_weak_tp_adjust", -0.005), # 趋势弱止盈下调
        
        # 基本面过滤
        ("min_circ_mv", 500000),     # 最小流通市值（万元）= 50亿
        ("max_pe", None),            # 最大 PE（None 表示按行业均值 * 1.5）
        ("max_pb", 3.0),             # 最大 PB
        ("min_gross_margin", 20.0),  # 最小毛利率
        ("max_debt_ratio", 60.0),    # 最大资产负债率
        ("min_list_days", 60),       # 最小上市天数
        
        # 技术面多空阈值
        ("tech_threshold", 0.33),    # 技术面信号阈值
        
        # 注入的外部数据（由 backtest_service 传入）
        ("fundamentals_by_symbol", {}),
        ("industry_scores_by_symbol", {}),
        ("sentiment_by_symbol", {}),
        ("hot_by_symbol", {}),
        ("symbol_type_map", {}),
        ("kronos_predictions", {}),  # 外部预测数据
        
        # 数据缓冲
        ("data_buffer", 300),
    )
    
    def __init__(self):
        super().__init__()
        
        # 交易状态
        self.order = None
        self.last_selection = []
        self.trade_count = 0
        
        # 持仓成本与止盈状态
        self.entry_prices: Dict[str, float] = {}
        self.tp_stage: Dict[str, int] = {}  # 止盈阶段 0-3
        self.trailing_stop: Dict[str, float] = {}  # 移动止损价
        self.position_sizes: Dict[str, float] = {}  # 原始持仓比例
        
        # 每日净值记录（用于指标提取）
        self.daily_values: List[float] = []
        self.daily_dates: List[str] = []
        
        # ATR 历史（用于计算分位数）
        self.atr_history: List[float] = []
        
        # 技术指标（预计算）
        self.indicators: Dict[str, Dict] = {}
        self._init_indicators()
    
    def _init_indicators(self):
        """初始化技术指标"""
        for d in self.datas:
            name = d._name
            
            # 检查数据长度，避免指标初始化失败
            # Backtrader 的 len(d) 在 __init__ 阶段可能返回 0
            # 所以只能在这里创建指标，让 Backtrader 自动管理 minperiod
            
            self.indicators[name] = {
                # 趋势指标
                "ma20": bt.indicators.SimpleMovingAverage(d.close, period=20),
                "ma60": bt.indicators.SimpleMovingAverage(d.close, period=60),
                "macd": bt.indicators.MACDHisto(d.close),
                
                # 动量指标
                "rsi": bt.indicators.RelativeStrengthIndex(d.close, period=14),
                "roc": bt.indicators.RateOfChange100(d.close, period=12),
                
                # 波动指标
                "atr": bt.indicators.AverageTrueRange(d, period=14),
                "boll": bt.indicators.BollingerBands(d.close, period=20),
                
                # 量能指标
                "obv": OBV(d),
                "volume_ma": bt.indicators.SimpleMovingAverage(d.volume, period=20),
            }
    
    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.trade_count += 1
            if order.isbuy():
                # 记录买入价格
                self.entry_prices[order.data._name] = order.executed.price
                self.tp_stage[order.data._name] = 0
            self.order = None
        elif order.status in [order.Canceled, order.Rejected, order.Margin]:
            self.order = None
    
    def next(self):
        # 记录每日净值
        current_value = self.broker.getvalue()
        self.daily_values.append(current_value)
        current_date = self.datas[0].datetime.date(0)
        self.daily_dates.append(current_date.strftime("%Y-%m-%d"))
        
        # 更新 ATR 历史
        if len(self.datas) > 0 and len(self.datas[0]) > 14:
            market_atr = self._calculate_market_atr()
            self.atr_history.append(market_atr)
        
        # 检查强制空仓
        if self.params.force_cash:
            self.close_all_positions()
            return
        
        # 检查市场整体技术面（用第一个数据作为市场代理）
        market_tech_score = self._calculate_market_tech_score()
        if market_tech_score < self.params.market_bear_threshold:
            self.close_all_positions()
            return
        
        # 执行风控检查（止损/止盈）
        self._check_risk_management()
        
        # 再平衡日逻辑
        if self.is_rebalance_day():
            self._rebalance()
            self.mark_rebalance()
    
    def _calculate_market_tech_score(self) -> float:
        """计算市场整体技术面分数"""
        if len(self.datas) == 0:
            return 0.0
        
        # 使用所有标的的平均技术分
        scores = []
        for d in self.datas:
            if len(d) < self.params.lookback:
                continue
            score = self._calculate_tech_score(d)
            if score is not None:
                scores.append(score)
        
        return np.mean(scores) if scores else 0.0
    
    def _calculate_market_atr(self) -> float:
        """计算市场整体 ATR"""
        atrs = []
        for d in self.datas:
            name = d._name
            if name in self.indicators and len(d) > 14:
                atr = self.indicators[name]["atr"][0]
                close = d.close[0]
                if close > 0:
                    atrs.append(atr / close)  # 归一化
        return np.mean(atrs) if atrs else 0.0
    
    def _is_high_volatility(self) -> bool:
        """判断是否高波动市场（ATR > 90%分位）"""
        if len(self.atr_history) < 60:
            return False
        current_atr = self.atr_history[-1]
        percentile_90 = np.percentile(self.atr_history[-252:], 90)  # 最近一年
        return current_atr > percentile_90
    
    def _calculate_tech_score(self, data) -> Optional[float]:
        """
        计算单个标的的技术面分数
        
        使用 10 个核心指标，映射到 [-1, +1]
        覆盖：动量/趋势/波动/量能/资金流向
        """
        name = data._name
        if name not in self.indicators:
            return None
        
        if len(data) < self.params.lookback:
            return None
        
        ind = self.indicators[name]
        scores = []
        
        try:
            # 1. 动量：RSI（50为中性）
            rsi = ind["rsi"][0]
            rsi_score = (rsi - 50) / 50  # 映射到 [-1, 1]
            rsi_score = max(-1, min(1, rsi_score))
            scores.append(rsi_score)
            
            # 2. 动量：ROC
            roc = ind["roc"][0]
            roc_score = np.tanh(roc / 10)  # 使用 tanh 平滑
            scores.append(roc_score)
            
            # 3. 趋势：价格 vs MA20
            ma20 = ind["ma20"][0]
            if ma20 > 0:
                price_ma20_score = (data.close[0] - ma20) / ma20
                price_ma20_score = max(-1, min(1, price_ma20_score * 10))
                scores.append(price_ma20_score)
            
            # 4. 趋势：MA20 vs MA60
            ma60 = ind["ma60"][0]
            if ma60 > 0:
                ma_cross_score = (ma20 - ma60) / ma60
                ma_cross_score = max(-1, min(1, ma_cross_score * 10))
                scores.append(ma_cross_score)
            
            # 5. 趋势：MACD（使用 histo 值）
            macd_histo = ind["macd"].histo[0]
            macd_score = np.tanh(macd_histo * 0.5)
            scores.append(macd_score)
            
            # 6. 波动：布林带位置
            boll_mid = ind["boll"].mid[0]
            boll_top = ind["boll"].top[0]
            boll_bot = ind["boll"].bot[0]
            if boll_top != boll_bot:
                boll_pos = (data.close[0] - boll_mid) / (boll_top - boll_mid) if boll_top > boll_mid else 0
                boll_score = max(-1, min(1, boll_pos))
                scores.append(boll_score)
            
            # 7. 量能：成交量 vs MA
            vol_ma = ind["volume_ma"][0]
            if vol_ma > 0:
                vol_ratio = data.volume[0] / vol_ma
                vol_score = np.tanh((vol_ratio - 1) * 2)
                scores.append(vol_score)
            
            # 8. 资金流向：OBV 变化率
            obv = ind["obv"][0]
            if len(data) > 5:
                obv_prev = ind["obv"][-5]
                if obv_prev != 0:
                    obv_change = (obv - obv_prev) / abs(obv_prev)
                    obv_score = np.tanh(obv_change * 5)
                    scores.append(obv_score)
            
            # 9. 近期涨幅（5日）
            if len(data) > 5:
                ret_5d = (data.close[0] / data.close[-5] - 1)
                ret_5d_score = np.tanh(ret_5d * 10)
                scores.append(ret_5d_score)
            
            # 10. 波动率相对变化
            atr = ind["atr"][0]
            if len(data) > 20 and data.close[0] > 0:
                atr_norm = atr / data.close[0]
                # 低波动加分
                atr_score = -np.tanh((atr_norm - 0.02) * 50)
                scores.append(atr_score)
            
            if not scores:
                return None
            
            return np.mean(scores)
            
        except Exception:
            return None
    
    def _pass_fundamental_filter(self, symbol: str) -> bool:
        """检查是否通过基本面过滤"""
        fund = self.params.fundamentals_by_symbol.get(symbol, {})
        symbol_type = self.params.symbol_type_map.get(symbol, "stock")
        
        # ETF 不做基本面过滤
        if symbol_type == "etf":
            return True
        
        # 剔除 ST
        if fund.get("is_st", False):
            return False
        
        # 检查上市天数
        list_date_str = fund.get("list_date")
        if list_date_str:
            try:
                list_date = datetime.strptime(str(list_date_str), "%Y%m%d")
                days_listed = (datetime.now() - list_date).days
                if days_listed < self.params.min_list_days:
                    return False
            except:
                pass
        
        # 检查流通市值
        circ_mv = fund.get("circ_mv")
        if circ_mv is not None and circ_mv < self.params.min_circ_mv:
            return False
        
        # 检查 PB
        pb = fund.get("pb")
        if pb is not None and self.params.max_pb is not None and pb > self.params.max_pb:
            return False
        
        # 检查毛利率
        gross_margin = fund.get("gross_margin")
        if gross_margin is not None and gross_margin < self.params.min_gross_margin:
            return False
        
        # 检查资产负债率
        debt_ratio = fund.get("debt_to_assets")
        if debt_ratio is not None and debt_ratio > self.params.max_debt_ratio:
            return False
        
        return True
    
    def _calculate_composite_score(self, data) -> Optional[float]:
        """
        计算综合得分
        
        综合分 = 技术面(30%) + 行业景气(25%) + 热点主线(20%) + 基本面(15%) + 舆情(10%)
        """
        symbol = data._name
        
        # 技术面分数
        tech_score = self._calculate_tech_score(data)
        if tech_score is None:
            return None
        
        # 行业景气度分数
        industry_score = self.params.industry_scores_by_symbol.get(symbol, 0.0)
        
        # 热点分数
        hot_score = self.params.hot_by_symbol.get(symbol, 0.0)
        
        # 基本面分数（基于财务指标）
        fund_score = self._calculate_fundamental_score(symbol)
        
        # 舆情分数
        sentiment_data = self.params.sentiment_by_symbol.get(symbol, {})
        sentiment_score = sentiment_data.get("sentiment_score", 0.0) if isinstance(sentiment_data, dict) else 0.0
        
        # 加权综合
        composite = (
            self.params.w_tech * tech_score +
            self.params.w_industry * industry_score +
            self.params.w_hot * hot_score +
            self.params.w_fund * fund_score +
            self.params.w_sent * sentiment_score
        )
        
        return composite
    
    def _calculate_fundamental_score(self, symbol: str) -> float:
        """计算基本面分数（基于财务增长指标）"""
        fund = self.params.fundamentals_by_symbol.get(symbol, {})
        
        scores = []
        
        # 净利润增长
        netprofit_yoy = fund.get("netprofit_yoy")
        if netprofit_yoy is not None:
            score = np.tanh(netprofit_yoy / 50)
            scores.append(score)
        
        # 营收增长
        revenue_yoy = fund.get("revenue_yoy")
        if revenue_yoy is not None:
            score = np.tanh(revenue_yoy / 50)
            scores.append(score)
        
        # ROE 增长
        roe_yoy = fund.get("roe_yoy")
        if roe_yoy is not None:
            score = np.tanh(roe_yoy / 30)
            scores.append(score)
        
        # 毛利率
        gross_margin = fund.get("gross_margin")
        if gross_margin is not None:
            score = np.tanh((gross_margin - 20) / 30)
            scores.append(score)
        
        return np.mean(scores) if scores else 0.0
    
    def _calculate_position_size(self, symbol: str, composite_score: float) -> float:
        """
        计算动态仓位大小
        
        公式：position_size = min(risk_capital * pred_sharpe / (pred_vol * sqrt(252)), max_leverage * equity)
        """
        symbol_type = self.params.symbol_type_map.get(symbol, "stock")
        
        # 从外部预测获取（如果有）
        predictions = self.params.kronos_predictions.get(symbol, {})
        pred_sharpe = predictions.get("pred_sharpe")
        pred_vol = predictions.get("pred_vol")
        
        # 降级：使用历史估算
        if pred_sharpe is None or pred_vol is None:
            data = self.get_data_by_name(symbol)
            if data is not None and len(data) >= self.params.lookback:
                hist_returns = [(data.close[-i] / data.close[-i-1] - 1) for i in range(1, min(60, len(data)))]
                if hist_returns:
                    pred_vol = np.std(hist_returns) * np.sqrt(252)
                    pred_sharpe = (np.mean(hist_returns) * 252) / pred_vol if pred_vol > 0 else 0.5
        
        if pred_vol is None or pred_vol <= 0:
            pred_vol = 0.25  # 默认 25% 年化波动
        if pred_sharpe is None:
            pred_sharpe = 0.5  # 默认夏普
        
        # 计算仓位
        equity = self.broker.getvalue()
        risk_capital = self.params.risk_capital * equity
        
        position_value = risk_capital * abs(pred_sharpe) / (pred_vol * np.sqrt(252))
        position_value = min(position_value, self.params.max_leverage * equity)
        
        # 转换为权重
        weight = position_value / equity if equity > 0 else 0
        
        # 应用单标的上限
        max_weight = self.params.max_etf_weight if symbol_type == "etf" else self.params.max_stock_weight
        weight = min(weight, max_weight)
        
        return weight
    
    def _rebalance(self):
        """执行再平衡"""
        # 1. 计算所有标的的综合分
        candidates = []
        
        for d in self.datas:
            symbol = d._name
            
            # 基本面过滤
            if not self._pass_fundamental_filter(symbol):
                continue
            
            # 数据不足跳过
            if len(d) < self.params.lookback:
                continue
            
            # 计算综合分
            score = self._calculate_composite_score(d)
            if score is None:
                continue
            
            symbol_type = self.params.symbol_type_map.get(symbol, "stock")
            
            candidates.append({
                "data": d,
                "symbol": symbol,
                "score": score,
                "type": symbol_type
            })
        
        # 2. 分别选股票和 ETF
        stocks = [c for c in candidates if c["type"] == "stock"]
        etfs = [c for c in candidates if c["type"] == "etf"]
        
        stocks.sort(key=lambda x: x["score"], reverse=True)
        etfs.sort(key=lambda x: x["score"], reverse=True)
        
        top_stocks = stocks[:self.params.top_stocks]
        top_etfs = etfs[:self.params.top_etfs]
        
        selected = top_stocks + top_etfs
        
        # 记录选股结果
        self.last_selection = [
            {"symbol": c["symbol"], "score": round(c["score"], 4), "type": c["type"]}
            for c in selected
        ]
        
        if not selected:
            self.close_all_positions()
            return
        
        # 3. 计算权重
        weights = {}
        total_score = sum(abs(c["score"]) for c in selected)
        
        for c in selected:
            symbol = c["symbol"]
            
            # 基础权重（按分数加权）
            if total_score > 0:
                base_weight = abs(c["score"]) / total_score
            else:
                base_weight = 1.0 / len(selected)
            
            # 动态仓位调整
            dynamic_weight = self._calculate_position_size(symbol, c["score"])
            
            # 取较小值
            weight = min(base_weight, dynamic_weight)
            
            # 应用单标的上限
            max_weight = self.params.max_etf_weight if c["type"] == "etf" else self.params.max_stock_weight
            weight = min(weight, max_weight)
            
            weights[symbol] = weight
        
        # 4. 归一化权重（确保总和 <= risk_capital）
        total_weight = sum(weights.values())
        if total_weight > self.params.risk_capital:
            scale = self.params.risk_capital / total_weight
            weights = {k: v * scale for k, v in weights.items()}
        
        # 5. 记录原始权重（用于止盈计算）
        for symbol, weight in weights.items():
            self.position_sizes[symbol] = weight
        
        # 6. 执行再平衡
        self.rebalance_to_weights(weights)
    
    def _check_risk_management(self):
        """检查风控规则（止损/止盈）"""
        is_high_vol = self._is_high_volatility()
        
        for d in self.datas:
            symbol = d._name
            pos = self.getposition(d)
            
            if pos.size == 0:
                continue
            
            entry_price = self.entry_prices.get(symbol)
            if entry_price is None or entry_price <= 0:
                continue
            
            current_price = d.close[0]
            pnl_pct = (current_price - entry_price) / entry_price
            
            symbol_type = self.params.symbol_type_map.get(symbol, "stock")
            
            # 止损检查（高波动时暂停）
            if not is_high_vol:
                stop_loss = self.params.etf_stop_loss if symbol_type == "etf" else self.params.stock_stop_loss
                if pnl_pct <= -stop_loss:
                    self.order_target_percent(d, target=0.0)
                    continue
            
            # 分阶段止盈
            current_stage = self.tp_stage.get(symbol, 0)
            original_weight = self.position_sizes.get(symbol, 0)
            
            # 动态调整止盈阈值
            tp1 = self.params.tp_stage1
            tp2 = self.params.tp_stage2
            tp3 = self.params.tp_stage3
            
            if is_high_vol:
                tp1 += self.params.high_vol_tp_adjust
                tp2 += self.params.high_vol_tp_adjust
                tp3 += self.params.high_vol_tp_adjust
            
            # 趋势强度调整（使用 MACD histo 值）
            if symbol in self.indicators:
                macd_histo = self.indicators[symbol]["macd"].histo[0]
                # 归一化 MACD 强度
                macd_strength = np.tanh(macd_histo * 0.5)
                
                if macd_strength > 0.3:
                    tp1 += self.params.trend_strong_tp_adjust
                    tp2 += self.params.trend_strong_tp_adjust
                    tp3 += self.params.trend_strong_tp_adjust
                elif macd_strength < -0.3:
                    tp1 += self.params.trend_weak_tp_adjust
                    tp2 += self.params.trend_weak_tp_adjust
                    tp3 += self.params.trend_weak_tp_adjust
            
            # 阶段止盈
            if current_stage == 0 and pnl_pct >= tp1:
                # 减仓 30%
                new_weight = original_weight * (1 - self.params.tp_stage1_ratio)
                self.order_target_percent(d, target=new_weight)
                self.tp_stage[symbol] = 1
                self.position_sizes[symbol] = new_weight
            
            elif current_stage == 1 and pnl_pct >= tp2:
                # 再减仓 30%（相对于原始）
                new_weight = original_weight * (1 - self.params.tp_stage1_ratio - self.params.tp_stage2_ratio)
                self.order_target_percent(d, target=new_weight)
                self.tp_stage[symbol] = 2
                self.position_sizes[symbol] = new_weight
            
            elif current_stage == 2 and pnl_pct >= tp3:
                # 再减仓 20%（相对于原始），剩余 20% 用移动止损
                new_weight = original_weight * (1 - self.params.tp_stage1_ratio - self.params.tp_stage2_ratio - self.params.tp_stage3_ratio)
                self.order_target_percent(d, target=new_weight)
                self.tp_stage[symbol] = 3
                self.position_sizes[symbol] = new_weight
                # 设置移动止损起始价
                self.trailing_stop[symbol] = current_price
            
            elif current_stage == 3:
                # 移动止损
                trailing_price = self.trailing_stop.get(symbol, entry_price)
                
                # 更新追踪价格
                if current_price > trailing_price:
                    self.trailing_stop[symbol] = current_price
                    trailing_price = current_price
                
                # 计算止损位
                if symbol in self.indicators:
                    atr = self.indicators[symbol]["atr"][0]
                    stop_distance = atr * self.params.trailing_atr_mult
                    stop_price = trailing_price - stop_distance
                    
                    if current_price <= stop_price:
                        self.order_target_percent(d, target=0.0)
                        # 清理状态
                        self.tp_stage[symbol] = 0
                        self.trailing_stop.pop(symbol, None)
                        self.entry_prices.pop(symbol, None)
                        self.position_sizes.pop(symbol, None)
    
    def stop(self):
        """策略结束时的清理"""
        pass


# 为了兼容 strategy_loader 的查找逻辑
Strategy = KronosMultidimRotationStrategy
