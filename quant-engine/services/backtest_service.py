"""回测服务 - 使用 Backtrader 执行回测"""
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, List

import backtrader as bt
import pandas as pd

from core.logger import get_logger
from schemas.backtest import BacktestRequest, BacktestResponse
from services.data_loader import load_market_data, load_market_data_multi, resolve_universe, normalize_stock_code
from services.strategy_loader import load_strategy
from services.metrics_extractor import MetricsExtractor
from services.backtest_repository import BacktestRepository
from services.universe_features_service import UniverseFeaturesService

logger = get_logger(__name__)


class BacktestService:
    """回测服务"""

    def __init__(self):
        """初始化回测服务"""
        self.backtests: dict[str, dict] = {}  # legacy in-memory store; will be deprecated

    async def run_backtest(self, request: BacktestRequest, *, backtest_id: Optional[str] = None, task_id: Optional[str] = None) -> BacktestResponse:
        """
        执行回测
        
        使用 Backtrader 执行策略回测，支持：
        - Custom 策略（AI 生成）
        - Builtin 策略（系统内置）
        - 多种数据源（Tushare、TDengine）
        - 单标的 / 多标的（组合）回测
        - AI 评价数据提取
        """
        try:
            # 判断是否为多标的回测
            is_multi = request.is_multi_symbol()
            
            if is_multi:
                return await self._run_multi_backtest(request, backtest_id=backtest_id, task_id=task_id)
            else:
                return await self._run_single_backtest(request, backtest_id=backtest_id, task_id=task_id)
                
        except Exception as e:
            logger.error(f"回测执行失败: {e}", exc_info=True)
            if backtest_id is not None:
                BacktestRepository.mark_failed(backtest_id, str(e), error_code=getattr(e, "code", "exception"))
            raise

    async def _run_single_backtest(self, request: BacktestRequest, *, backtest_id: Optional[str] = None, task_id: Optional[str] = None) -> BacktestResponse:
        """单标的回测（原有逻辑）"""
        stock_code = request.stock_code or (request.symbols[0] if request.symbols else None)
        if not stock_code:
            raise ValueError("单标的回测需要提供 stock_code")
        
        logger.info(
            f"开始单标的回测: {stock_code}, "
            f"{request.start_date} - {request.end_date}, "
            f"策略模式: {request.strategy_mode}"
        )
        
        backtest_id = backtest_id or f"backtest_{uuid.uuid4().hex[:8]}"

        # 确保存在记录并标记 running
        existing = BacktestRepository.get(backtest_id)
        if not existing:
            BacktestRepository.create_stub(request, backtest_id=backtest_id, task_id=task_id)
        else:
            if task_id:
                BacktestRepository.link_task(backtest_id, task_id)
        BacktestRepository.mark_running(backtest_id)
        
        # 1. 加载行情数据（向前扩展预热期）
        data_buffer = request.parameters.get("data_buffer", 300) if request.parameters else 300
        start_dt = datetime.strptime(request.start_date, "%Y-%m-%d")
        warmup_days = int(data_buffer * 1.5)
        extended_start = (start_dt - timedelta(days=warmup_days)).strftime("%Y-%m-%d")
        
        logger.info(f"加载行情数据: {request.data_source}, 预热扩展: {extended_start} -> {request.start_date}")
        df = load_market_data(
            stock_code=stock_code,
            start_date=extended_start,
            end_date=request.end_date,
            source=request.data_source
        )
        
        if df.empty:
            raise ValueError(f"未获取到行情数据: {stock_code}")
        
        logger.info(f"加载数据成功: {len(df)} 条记录")
        
        # 2. 加载策略
        logger.info(f"加载策略: {request.strategy_mode}")
        strategy_class = load_strategy(
            mode=request.strategy_mode,
            strategy_code=request.strategy_code,
            strategy_name=request.strategy_name,
            parameters=request.parameters
        )
        
        # 验证数据长度
        min_data_points = 70  # 最少需要70个数据点
        if len(df) < min_data_points:
            raise ValueError(f"数据不足: {len(df)} 个数据点 < {min_data_points}（回测需要足够的预热期）")
        
        logger.info(f"数据验证通过: {len(df)} 个数据点")
        
        # 3. 创建 Backtrader Cerebro 引擎
        cerebro = bt.Cerebro()
        
        # 4. 添加数据（设置 name 以便策略中引用）
        data = self._create_backtrader_data(df)
        cerebro.adddata(data, name=stock_code)
        
        # 5. 添加观察者
        cerebro.addobserver(bt.observers.Value)
        
        # 6. 添加策略
        cerebro.addstrategy(strategy_class, **request.parameters)
        
        # 7. 设置初始资金
        cerebro.broker.setcash(request.initial_cash)
        
        # 8. 设置手续费
        cerebro.broker.setcommission(commission=request.commission)
        
        # 9. 允许做空（部分策略需要，如配对交易）
        allow_short = request.parameters.get("allow_short", False) if request.parameters else False
        if allow_short:
            cerebro.broker.set_shortcash(False)
        
        # 10. 设置滑点
        if request.slippage > 0:
            cerebro.broker.set_slippage_perc(
                perc=request.slippage * 100,
                slip_open=True,
                slip_limit=True,
                slip_match=True,
                slip_out=False
            )
        
        # 10. 执行回测
        logger.info("执行回测...")
        results = cerebro.run()
        
        if not results:
            raise ValueError("回测未产生结果")
        
        # 11. 提取指标
        strategy_instance = results[0][0] if isinstance(results[0], list) else results[0]
        extractor = MetricsExtractor(cerebro, strategy_instance)
        metrics = extractor.extract_basic_metrics()
        daily_nav = self._extract_daily_nav(df, cerebro, strategy_instance)
        
        # 提取 AI 评价数据
        ai_review = None
        if request.enable_ai_review:
            try:
                ai_review = extractor.extract_ai_review_data()
            except Exception as e:
                logger.warning(f"提取 AI 评价数据失败: {e}")
        
        # 12. 构建响应
        response = BacktestResponse(
            success=True,
            backtest_id=backtest_id,
            metrics=metrics,
            daily_nav=daily_nav,
            ai_review=ai_review,
            message="回测完成"
        )

        BacktestRepository.mark_success(
            backtest_id,
            metrics=metrics,
            equity_curve=daily_nav,
            message="回测完成",
        )
        
        annual_return = metrics.get('annual_return', 0) or 0
        logger.info(
            f"回测完成: {backtest_id}, "
            f"总收益率: {metrics.get('total_return', 0):.2f}%, "
            f"年化收益率: {annual_return:.2f}%"
        )
        
        return response

    async def _run_multi_backtest(self, request: BacktestRequest, *, backtest_id: Optional[str] = None, task_id: Optional[str] = None) -> BacktestResponse:
        """多标的/组合回测"""
        logger.info(
            f"开始多标的回测: {len(request.symbols or [])} 只标的, "
            f"{request.start_date} - {request.end_date}, "
            f"策略: {request.strategy_name}, "
            f"再平衡: {request.rebalance_frequency}, "
            f"分配: {request.allocation}"
        )
        
        backtest_id = backtest_id or f"backtest_{uuid.uuid4().hex[:8]}"

        # 确保存在记录并标记 running
        existing = BacktestRepository.get(backtest_id)
        if not existing:
            BacktestRepository.create_stub(request, backtest_id=backtest_id, task_id=task_id)
        else:
            if task_id:
                BacktestRepository.link_task(backtest_id, task_id)
        BacktestRepository.mark_running(backtest_id)
        
        # 1. 解析股票池
        universe_symbols, symbol_type_map = resolve_universe(
            universe_mode=request.universe_mode,
            universe_params=request.universe_params,
            symbols=request.symbols
        )
        
        if not universe_symbols:
            raise ValueError("未获取到有效的标的列表")
        
        logger.info(f"股票池: {len(universe_symbols)} 只标的, 类型分布: stocks={len([s for s,t in symbol_type_map.items() if t=='stock'])}, etfs={len([s for s,t in symbol_type_map.items() if t=='etf'])}")
        
        # 2. 加载行情数据（向前扩展预热期）
        data_buffer = request.parameters.get("data_buffer", 300) if request.parameters else 300
        start_dt = datetime.strptime(request.start_date, "%Y-%m-%d")
        warmup_days = int(data_buffer * 1.5)
        extended_start = (start_dt - timedelta(days=warmup_days)).strftime("%Y-%m-%d")
        
        logger.info(f"批量加载行情数据, 预热扩展: {extended_start} -> {request.start_date}")
        dfs = load_market_data_multi(
            symbols=universe_symbols,
            start_date=extended_start,
            end_date=request.end_date,
            source=request.data_source,
            symbol_type_map=symbol_type_map,
        )
        
        if not dfs:
            raise ValueError("未获取到任何标的的行情数据")
        
        missing_symbols = list(set(universe_symbols) - set(dfs.keys()))
        loaded_symbols = list(dfs.keys())
        logger.info(f"数据加载完成: {len(loaded_symbols)} 只有数据, {len(missing_symbols)} 只缺失")
        
        # 3. 加载策略
        logger.info(f"加载策略: {request.strategy_mode}")
        strategy_class = load_strategy(
            mode=request.strategy_mode,
            strategy_code=request.strategy_code,
            strategy_name=request.strategy_name,
            parameters=request.parameters
        )
        
        # 3.5 拉取横截面特征（如果是 kronos 策略或参数中要求）
        features_data = {}
        if request.strategy_name == "kronos_multidim_rotation" or request.parameters.get("fetch_features", False):
            try:
                logger.info("开始拉取横截面特征数据...")
                features_service = UniverseFeaturesService()
                features_data = features_service.fetch_all_features(
                    symbols=loaded_symbols,
                    asof_date=request.start_date,
                    symbol_type_map=symbol_type_map
                )
                logger.info(f"横截面特征拉取完成: fundamentals={len(features_data.get('fundamentals_by_symbol', {}))}")
            except Exception as e:
                logger.warning(f"拉取横截面特征失败，策略将使用降级模式: {e}")
                features_data = {
                    "fundamentals_by_symbol": {},
                    "industry_scores_by_symbol": {},
                    "sentiment_by_symbol": {},
                    "hot_by_symbol": {},
                    "symbol_type_map": symbol_type_map
                }
        
        # 4. 创建 Backtrader Cerebro 引擎
        cerebro = bt.Cerebro()
        
        # 5. 添加多个数据源（过滤掉数据不足的标的）
        min_data_points = 70  # 最少需要70个数据点（MA60需要60，留10个余量）
        valid_count = 0
        skipped_count = 0
        
        for symbol, df in dfs.items():
            if len(df) < min_data_points:
                logger.warning(f"跳过 {symbol}: 数据点不足 {len(df)} < {min_data_points}")
                skipped_count += 1
                continue
            
            data = self._create_backtrader_data(df)
            cerebro.adddata(data, name=symbol)
            valid_count += 1
        
        if valid_count == 0:
            raise ValueError(f"没有符合数据长度要求的标的（需要至少{min_data_points}个数据点）")
        
        logger.info(f"添加数据源: {valid_count} 只有效, {skipped_count} 只数据不足被跳过")
        
        # 6. 添加观察者
        cerebro.addobserver(bt.observers.Value)
        
        # 7. 添加策略（传递组合相关参数 + 横截面特征）
        strategy_params = {**request.parameters}
        strategy_params["rebalance_frequency"] = request.rebalance_frequency
        strategy_params["allocation"] = request.allocation
        strategy_params["allow_short"] = request.allow_short
        
        # 注入横截面特征数据
        if features_data:
            strategy_params["fundamentals_by_symbol"] = features_data.get("fundamentals_by_symbol", {})
            strategy_params["industry_scores_by_symbol"] = features_data.get("industry_scores_by_symbol", {})
            strategy_params["sentiment_by_symbol"] = features_data.get("sentiment_by_symbol", {})
            strategy_params["hot_by_symbol"] = features_data.get("hot_by_symbol", {})
            strategy_params["symbol_type_map"] = features_data.get("symbol_type_map", symbol_type_map)
        else:
            strategy_params["symbol_type_map"] = symbol_type_map
        
        cerebro.addstrategy(strategy_class, **strategy_params)
        
        # 8. 设置初始资金
        cerebro.broker.setcash(request.initial_cash)
        
        # 9. 设置手续费
        cerebro.broker.setcommission(commission=request.commission)
        
        # 10. 允许做空（配对交易等策略需要）
        if request.allow_short:
            # 设置允许卖空，取消现金不足检查
            cerebro.broker.set_shortcash(False)  # 做空不占用现金
        
        # 11. 设置滑点
        if request.slippage > 0:
            cerebro.broker.set_slippage_perc(
                perc=request.slippage * 100,
                slip_open=True,
                slip_limit=True,
                slip_match=True,
                slip_out=False
            )
        
        # 11. 执行回测
        logger.info("执行多标的回测...")
        results = cerebro.run()
        
        if not results:
            raise ValueError("回测未产生结果")
        
        # 12. 提取指标
        strategy_instance = results[0][0] if isinstance(results[0], list) else results[0]
        extractor = MetricsExtractor(cerebro, strategy_instance)
        metrics = extractor.extract_basic_metrics()
        
        # 添加组合回测特有的指标
        metrics["universe_symbols"] = loaded_symbols
        metrics["missing_symbols"] = missing_symbols
        metrics["rebalance_frequency"] = request.rebalance_frequency
        metrics["allocation"] = request.allocation
        
        # 提取策略特有的指标（如 last_selection, last_selected_symbol 等）
        if hasattr(strategy_instance, "last_selection"):
            metrics["last_selection"] = strategy_instance.last_selection
        if hasattr(strategy_instance, "last_selected_symbol"):
            metrics["last_selected_symbol"] = strategy_instance.last_selected_symbol
        if hasattr(strategy_instance, "trade_count"):
            metrics["trade_count"] = strategy_instance.trade_count
        
        # 使用第一个标的的数据提取净值曲线（简化）
        first_df = list(dfs.values())[0]
        daily_nav = self._extract_daily_nav(first_df, cerebro, strategy_instance)
        
        # 提取 AI 评价数据
        ai_review = None
        if request.enable_ai_review:
            try:
                ai_review = extractor.extract_ai_review_data()
            except Exception as e:
                logger.warning(f"提取 AI 评价数据失败: {e}")
        
        # 13. 构建响应
        response = BacktestResponse(
            success=True,
            backtest_id=backtest_id,
            metrics=metrics,
            daily_nav=daily_nav,
            ai_review=ai_review,
            message=f"多标的回测完成: {len(loaded_symbols)} 只标的"
        )

        BacktestRepository.mark_success(
            backtest_id,
            metrics=metrics,
            equity_curve=daily_nav,
            message=f"多标的回测完成: {len(loaded_symbols)} 只标的",
        )
        
        annual_return = metrics.get('annual_return', 0) or 0
        logger.info(
            f"多标的回测完成: {backtest_id}, "
            f"总收益率: {metrics.get('total_return', 0):.2f}%, "
            f"年化收益率: {annual_return:.2f}%"
        )
        
        return response
    
    def _create_backtrader_data(self, df: pd.DataFrame) -> bt.feeds.PandasData:
        """
        将 DataFrame 转换为 Backtrader 数据源
        
        Args:
            df: DataFrame with columns: ['open', 'high', 'low', 'close', 'volume']
                索引为日期（datetime）
        
        Returns:
            Backtrader PandasData feed
        """
        # 确保索引是 datetime 且有序（Backtrader 以索引为 datetime）
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        df.index = df.index.tz_localize(None)
        df = df.sort_index()

        # 列名兼容处理（大小写与常见别名）
        col_map = {c.lower(): c for c in df.columns}
        alias = {
            "open": col_map.get("open") or col_map.get("o"),
            "high": col_map.get("high") or col_map.get("h"),
            "low": col_map.get("low") or col_map.get("l"),
            "close": col_map.get("close") or col_map.get("c"),
            "volume": col_map.get("volume") or col_map.get("vol") or col_map.get("amount"),
        }
        missing = [k for k, v in alias.items() if v is None]
        if missing:
            raise ValueError(f"数据缺少必要列: {','.join(missing)}")

        df = df.rename(columns={alias["open"]: "open", alias["high"]: "high", alias["low"]: "low", alias["close"]: "close", alias["volume"]: "volume"})

        # 如果没有 volume，创建一个虚拟的
        if "volume" not in df.columns:
            df["volume"] = 0

        # 创建 Backtrader 数据源
        data = bt.feeds.PandasData(
            dataname=df,
            datetime=None,  # 使用索引作为日期
            open="open",
            high="high",
            low="low",
            close="close",
            volume="volume",
            openinterest=-1,  # 不使用持仓量
            timeframe=bt.TimeFrame.Days,
            compression=1,
        )

        return data
    
    def _extract_daily_nav(
        self,
        df: pd.DataFrame,
        cerebro: bt.Cerebro,
        strategy: bt.Strategy
    ) -> list[dict]:
        """
        提取每日净值曲线
        
        优先使用策略内部记录的每日净值（daily_values + daily_dates），
        如果没有则使用简化方法估算。
        """
        # 获取初始资金
        initial_cash = cerebro.broker.startingcash
        
        # 优先使用策略内部记录的净值
        if hasattr(strategy, 'daily_values') and hasattr(strategy, 'daily_dates'):
            if strategy.daily_values and strategy.daily_dates:
                daily_nav = []
                for i, (date_str, value) in enumerate(zip(strategy.daily_dates, strategy.daily_values)):
                    nav = value / initial_cash if initial_cash > 0 else 1.0
                    daily_nav.append({
                        "date": date_str,
                        "nav": round(nav, 6)
                    })
                return daily_nav
        
        # 退化方案：基于价格变化估算
        final_value = cerebro.broker.getvalue()
        
        # 获取价格数据
        dates = sorted(df.index.tolist())
        closes = df["close"].values
        
        if len(dates) == 0:
            return []
        
        # 计算价格变化率
        price_returns = pd.Series(closes).pct_change().fillna(0)
        
        # 简化：假设策略跟随价格变化
        daily_nav = []
        current_nav = 1.0
        
        for i, date in enumerate(dates):
            if i > 0:
                # 使用价格变化率作为净值变化率（简化）
                current_nav *= (1 + price_returns.iloc[i])
            
            daily_nav.append({
                "date": date.strftime("%Y-%m-%d"),
                "nav": round(current_nav, 6)
            })
        
        # 调整到最终净值（归一化）
        if len(daily_nav) > 0 and daily_nav[-1]["nav"] > 0:
            final_nav_ratio = final_value / initial_cash
            scale_factor = final_nav_ratio / daily_nav[-1]["nav"]
            for item in daily_nav:
                item["nav"] = round(item["nav"] * scale_factor, 6)
        
        return daily_nav
    
    async def get_backtest(self, backtest_id: str) -> Optional[dict]:
        """获取回测结果（持久化版本）"""
        rec = BacktestRepository.get(backtest_id)
        if not rec:
            return None
        return self._to_dict(rec)

    async def list_backtests(self, limit: int = 10, offset: int = 0) -> list[dict]:
        """列出回测记录（持久化版本）"""
        recs = BacktestRepository.list(limit=limit, offset=offset)
        return [self._to_dict(r) for r in recs]

    def _to_dict(self, rec) -> dict:
        return {
            "backtest_id": rec.id,
            "task_id": rec.task_id,
            "status": rec.status,
            "message": rec.message,
            "metrics": rec.metrics,
            "daily_nav": rec.equity_curve,
            "ai_review": None,
            "params": rec.params,
            "stock_code": rec.stock_code,
            "start_date": rec.start_date,
            "end_date": rec.end_date,
            "created_at": rec.created_at.isoformat() if rec.created_at else None,
            "updated_at": rec.updated_at.isoformat() if rec.updated_at else None,
        }
