"""基本面数据服务"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

from sqlmodel import Session, select

from core.database import SessionLocal
from models.industry_rank import IndustryRank
from models.sentiment_score import SentimentScore
from models.hot_score import HotScore
from schemas.fundamentals import (
    FundamentalsItem,
    IndustryRankItem,
    SentimentItem,
    HotScoreItem,
)
from services.tushare_service import TushareService, normalize_code, get_market_suffix

logger = logging.getLogger(__name__)

# 简单内存缓存
_cache: Dict[str, Any] = {}
_cache_expiry: Dict[str, datetime] = {}


def _is_cache_valid(key: str, ttl_minutes: int = 60) -> bool:
    """检查缓存是否有效"""
    if key not in _cache_expiry:
        return False
    return datetime.now() < _cache_expiry[key]


def _set_cache(key: str, data: Any, ttl_minutes: int = 60):
    """设置缓存"""
    _cache[key] = data
    _cache_expiry[key] = datetime.now() + timedelta(minutes=ttl_minutes)


def _get_cache(key: str) -> Any:
    """获取缓存"""
    return _cache.get(key)


class FundamentalsService:
    """基本面数据服务"""
    
    def __init__(self):
        self.tushare_service = TushareService()
    
    def load_industry_rank_from_db(self, month: str) -> List[IndustryRankItem]:
        """从数据库加载行业排名数据"""
        try:
            with SessionLocal() as session:
                statement = select(IndustryRank).where(IndustryRank.month == month).order_by(IndustryRank.rank)
                results = session.execute(statement).scalars().all()
                
                if not results:
                    logger.info(f"数据库中没有 {month} 的行业排名数据")
                    return []
                
                items = [
                    IndustryRankItem(
                        industry=row.industry,
                        rank=row.rank,
                        score=row.score,
                        avg_netprofit_yoy=row.avg_netprofit_yoy,
                        avg_revenue_yoy=row.avg_revenue_yoy,
                        avg_roe_yoy=row.avg_roe_yoy,
                        stock_count=row.stock_count,
                    )
                    for row in results
                ]
                logger.info(f"从数据库加载了 {len(items)} 个行业排名（{month}）")
                return items
        except Exception as e:
            logger.error(f"从数据库加载行业排名失败: {e}", exc_info=True)
            return []
    
    def save_industry_rank_to_db(self, month: str, items: List[IndustryRankItem]) -> bool:
        """保存行业排名数据到数据库（upsert）"""
        try:
            with SessionLocal() as session:
                # 先删除该月份的旧数据
                statement = select(IndustryRank).where(IndustryRank.month == month)
                old_records = session.execute(statement).scalars().all()
                for record in old_records:
                    session.delete(record)
                
                # 插入新数据
                for item in items:
                    db_item = IndustryRank(
                        month=month,
                        industry=item.industry,
                        rank=item.rank,
                        score=item.score,
                        avg_netprofit_yoy=item.avg_netprofit_yoy,
                        avg_revenue_yoy=item.avg_revenue_yoy,
                        avg_roe_yoy=item.avg_roe_yoy,
                        stock_count=item.stock_count,
                    )
                    session.add(db_item)
                
                session.commit()
                logger.info(f"成功保存 {len(items)} 个行业排名到数据库（{month}）")
                return True
        except Exception as e:
            logger.error(f"保存行业排名到数据库失败: {e}", exc_info=True)
            return False
    
    def _load_sentiment_from_db(self, codes: List[str], trade_date: str) -> Optional[List[SentimentItem]]:
        """从数据库加载情绪分数"""
        try:
            with SessionLocal() as session:
                normalized_codes = [normalize_code(c) for c in codes]
                statement = select(SentimentScore).where(
                    SentimentScore.code.in_(normalized_codes),
                    SentimentScore.trade_date == trade_date
                )
                results = session.execute(statement).scalars().all()
                
                if not results or len(results) < len(normalized_codes):
                    return None
                
                return [
                    SentimentItem(
                        code=row.code,
                        sentiment_score=row.sentiment_score,
                        discussion_volume=row.discussion_volume
                    )
                    for row in results
                ]
        except Exception as e:
            logger.warning(f"从数据库加载情绪分数失败: {e}")
            return None
    
    def _save_sentiment_to_db(self, items: List[SentimentItem], trade_date: str, detail_dict: Dict):
        """保存情绪分数到数据库"""
        try:
            with SessionLocal() as session:
                for item in items:
                    # 先查询是否存在
                    statement = select(SentimentScore).where(
                        SentimentScore.code == item.code,
                        SentimentScore.trade_date == trade_date
                    )
                    existing = session.execute(statement).scalar_one_or_none()
                    
                    detail = detail_dict.get(item.code, {})
                    
                    if existing:
                        # 更新
                        existing.sentiment_score = item.sentiment_score
                        existing.discussion_volume = item.discussion_volume
                        existing.hot_rank = detail.get("hot_rank", 0)
                        existing.updated_at = datetime.now()
                    else:
                        # 插入
                        db_item = SentimentScore(
                            code=item.code,
                            trade_date=trade_date,
                            sentiment_score=item.sentiment_score,
                            discussion_volume=item.discussion_volume,
                            hot_rank=detail.get("hot_rank", 0)
                        )
                        session.add(db_item)
                
                session.commit()
                logger.info(f"保存了 {len(items)} 条情绪分数到数据库（{trade_date}）")
        except Exception as e:
            logger.error(f"保存情绪分数到数据库失败: {e}", exc_info=True)
    
    def _load_hot_score_from_db(self, codes: List[str], trade_date: str) -> Optional[List[HotScoreItem]]:
        """从数据库加载热点分数"""
        try:
            with SessionLocal() as session:
                normalized_codes = [normalize_code(c) for c in codes]
                statement = select(HotScore).where(
                    HotScore.code.in_(normalized_codes),
                    HotScore.trade_date == trade_date
                )
                results = session.execute(statement).scalars().all()
                
                if not results or len(results) < len(normalized_codes):
                    return None
                
                return [
                    HotScoreItem(
                        code=row.code,
                        hot_score=row.hot_score
                    )
                    for row in results
                ]
        except Exception as e:
            logger.warning(f"从数据库加载热点分数失败: {e}")
            return None
    
    def _save_hot_score_to_db(self, items: List[HotScoreItem], trade_date: str, detail_dict: Dict):
        """保存热点分数到数据库"""
        try:
            with SessionLocal() as session:
                for item in items:
                    # 先查询是否存在
                    statement = select(HotScore).where(
                        HotScore.code == item.code,
                        HotScore.trade_date == trade_date
                    )
                    existing = session.execute(statement).scalar_one_or_none()
                    
                    detail = detail_dict.get(item.code, {})
                    concept_tags = ",".join(detail.get("concept_tags", []))
                    
                    if existing:
                        # 更新
                        existing.hot_score = item.hot_score
                        existing.concept_score = detail.get("concept_score", 0.0)
                        existing.limit_score = detail.get("limit_score", 0.0)
                        existing.up_stat = detail.get("up_stat", 0)
                        existing.concept_tags = concept_tags
                        existing.updated_at = datetime.now()
                    else:
                        # 插入
                        db_item = HotScore(
                            code=item.code,
                            trade_date=trade_date,
                            hot_score=item.hot_score,
                            concept_score=detail.get("concept_score", 0.0),
                            limit_score=detail.get("limit_score", 0.0),
                            up_stat=detail.get("up_stat", 0),
                            concept_tags=concept_tags
                        )
                        session.add(db_item)
                
                session.commit()
                logger.info(f"保存了 {len(items)} 条热点分数到数据库（{trade_date}）")
        except Exception as e:
            logger.error(f"保存热点分数到数据库失败: {e}", exc_info=True)
    
    def fetch_batch(
        self,
        codes: List[str],
        trade_date: Optional[str] = None
    ) -> Tuple[List[FundamentalsItem], List[str], List[str]]:
        """
        批量获取基本面数据
        
        Args:
            codes: 股票代码列表
            trade_date: 交易日期 YYYYMMDD
        
        Returns:
            (成功数据列表, 成功代码列表, 失败代码列表)
        """
        success_items: List[FundamentalsItem] = []
        success_codes: List[str] = []
        failed_codes: List[str] = []
        
        # 标准化代码
        normalized_codes = [normalize_code(c) for c in codes]
        
        # 1. 获取股票基础信息（行业、上市日期）
        stock_basic_cache_key = "stock_basic_all"
        if _is_cache_valid(stock_basic_cache_key, ttl_minutes=1440):  # 缓存1天
            stock_basic_dict = _get_cache(stock_basic_cache_key)
        else:
            stock_basic_list = self.tushare_service.fetch_stock_basic()
            stock_basic_dict = {}
            for item in stock_basic_list:
                symbol = item.get("symbol", "")
                if symbol:
                    stock_basic_dict[symbol] = item
            _set_cache(stock_basic_cache_key, stock_basic_dict, ttl_minutes=1440)
        
        # 2. 获取每日基本面（估值、市值）
        daily_basic_dict = self._fetch_daily_basic_batch(normalized_codes, trade_date)
        
        # 3. 获取财务指标（毛利率、负债率等）
        fina_dict = self._fetch_fina_indicator_batch(normalized_codes)
        
        # 4. 判断是否ST
        st_set = self._check_st_batch(normalized_codes, stock_basic_dict)
        
        # 5. 组装结果
        for code in normalized_codes:
            try:
                basic = stock_basic_dict.get(code, {})
                daily = daily_basic_dict.get(code, {})
                fina = fina_dict.get(code, {})
                
                item = FundamentalsItem(
                    code=code,
                    name=basic.get("name"),
                    industry=basic.get("industry"),
                    list_date=basic.get("list_date"),
                    is_st=code in st_set,
                    circ_mv=daily.get("circ_mv"),
                    total_mv=daily.get("total_mv"),
                    pe_ttm=daily.get("pe_ttm"),
                    pb=daily.get("pb"),
                    gross_margin=fina.get("grossprofit_margin"),
                    debt_to_assets=fina.get("debt_to_assets"),
                    roe_yoy=fina.get("roe_yoy"),
                    netprofit_yoy=fina.get("netprofit_yoy"),
                    revenue_yoy=fina.get("or_yoy"),  # 营收同比在tushare是 or_yoy
                )
                success_items.append(item)
                success_codes.append(code)
            except Exception as e:
                logger.warning(f"处理 {code} 基本面数据失败: {e}")
                failed_codes.append(code)
        
        return success_items, success_codes, failed_codes
    
    def _fetch_daily_basic_batch(
        self,
        codes: List[str],
        trade_date: Optional[str] = None
    ) -> Dict[str, dict]:
        """批量获取每日基本面（估值、市值）"""
        result = {}
        
        try:
            api = self.tushare_service.api
            
            # 确定查询日期
            if trade_date:
                query_date = trade_date
            else:
                query_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
            
            # 使用 trade_date 模式批量获取
            # tushare daily_basic 支持按日期获取全市场
            cache_key = f"daily_basic_{query_date}"
            if _is_cache_valid(cache_key, ttl_minutes=60):
                all_daily = _get_cache(cache_key)
            else:
                df = api.daily_basic(trade_date=query_date)
                all_daily = {}
                if df is not None and not df.empty:
                    for _, row in df.iterrows():
                        ts_code = str(row.get("ts_code", ""))
                        symbol = ts_code[:6] if len(ts_code) >= 6 else ts_code
                        all_daily[symbol] = {
                            "circ_mv": row.get("circ_mv"),
                            "total_mv": row.get("total_mv"),
                            "pe_ttm": row.get("pe_ttm"),
                            "pb": row.get("pb"),
                        }
                _set_cache(cache_key, all_daily, ttl_minutes=60)
            
            # 筛选需要的代码
            for code in codes:
                if code in all_daily:
                    result[code] = all_daily[code]
                    
        except Exception as e:
            logger.error(f"批量获取 daily_basic 失败: {e}")
        
        return result
    
    def _fetch_fina_indicator_batch(self, codes: List[str]) -> Dict[str, dict]:
        """批量获取财务指标"""
        result = {}
        
        for code in codes:
            cache_key = f"fina_{code}"
            if _is_cache_valid(cache_key, ttl_minutes=1440):  # 缓存1天
                result[code] = _get_cache(cache_key)
                continue
            
            try:
                fina_list = self.tushare_service.fetch_fina_indicator(code)
                if fina_list:
                    # 取最近一期
                    latest = fina_list[0]
                    fina_data = {
                        "grossprofit_margin": latest.get("grossprofit_margin"),
                        "debt_to_assets": latest.get("debt_to_assets"),
                        "roe_yoy": latest.get("roe_yoy"),
                        "netprofit_yoy": latest.get("netprofit_yoy"),
                        "or_yoy": latest.get("or_yoy"),
                    }
                    result[code] = fina_data
                    _set_cache(cache_key, fina_data, ttl_minutes=1440)
            except Exception as e:
                logger.warning(f"获取 {code} 财务指标失败: {e}")
        
        return result
    
    def _check_st_batch(
        self,
        codes: List[str],
        stock_basic_dict: Dict[str, dict]
    ) -> set:
        """批量检查是否ST（通过名称判断）"""
        st_set = set()
        
        for code in codes:
            basic = stock_basic_dict.get(code, {})
            name = basic.get("name", "")
            # 简单规则：名称包含 ST 或 *ST
            if "ST" in name.upper():
                st_set.add(code)
        
        return st_set
    
    def calculate_industry_rank(self, month: Optional[str] = None, force_recalculate: bool = False) -> List[IndustryRankItem]:
        """
        计算行业景气度排名
        
        优先从数据库读取，如果数据库没有或 force_recalculate=True 则重新计算。
        
        Args:
            month: 月份 YYYY-MM，不传则使用当前月
            force_recalculate: 是否强制重新计算（忽略数据库缓存）
        
        Returns:
            行业排名列表
        """
        # 确定月份
        if month:
            query_month = month
        else:
            query_month = datetime.now().strftime("%Y-%m")
        
        # 1. 如果不是强制重算，先从数据库读取
        if not force_recalculate:
            db_result = self.load_industry_rank_from_db(query_month)
            if db_result:
                return db_result
        
        # 2. 数据库没有数据或强制重算，执行计算
        logger.info(f"开始计算 {query_month} 的行业景气度排名...")
        
        try:
            # 获取全部股票基础信息
            stock_basic_list = self.tushare_service.fetch_stock_basic()
            
            # 按行业分组
            industry_stocks: Dict[str, List[str]] = {}
            for item in stock_basic_list:
                industry = item.get("industry", "")
                symbol = item.get("symbol", "")
                if industry and symbol:
                    if industry not in industry_stocks:
                        industry_stocks[industry] = []
                    industry_stocks[industry].append(symbol)
            
            # 计算每个行业的景气度
            industry_scores: List[Dict] = []
            logger.info(f"共 {len(industry_stocks)} 个行业需要计算")
            
            # 遍历所有行业（不再限制数量，由定时任务慢慢执行）
            for idx, (industry, stocks) in enumerate(industry_stocks.items(), 1):
                if len(stocks) < 3:  # 行业股票太少跳过
                    continue
                
                # 采样部分股票计算（避免请求过多）
                sample_stocks = stocks[:min(5, len(stocks))]  # 提高到10只获得更准确的结果
                
                if idx % 5 == 0:
                    logger.info(f"处理进度: {idx}/{len(industry_stocks)} - {industry}")
                
                fina_dict = self._fetch_fina_indicator_batch(sample_stocks)
                
                if not fina_dict:
                    continue
                
                # 计算平均增长率
                netprofit_yoys = []
                revenue_yoys = []
                roe_yoys = []
                
                for code, fina in fina_dict.items():
                    if fina.get("netprofit_yoy") is not None:
                        netprofit_yoys.append(fina["netprofit_yoy"])
                    if fina.get("or_yoy") is not None:
                        revenue_yoys.append(fina["or_yoy"])
                    if fina.get("roe_yoy") is not None:
                        roe_yoys.append(fina["roe_yoy"])
                
                avg_netprofit = sum(netprofit_yoys) / len(netprofit_yoys) if netprofit_yoys else 0
                avg_revenue = sum(revenue_yoys) / len(revenue_yoys) if revenue_yoys else 0
                avg_roe = sum(roe_yoys) / len(roe_yoys) if roe_yoys else 0
                
                # 综合分数 = (净利润yoy + 营收yoy + ROE yoy) / 3，归一化到 [-1, 1]
                raw_score = (avg_netprofit + avg_revenue + avg_roe) / 3
                score = max(-1.0, min(1.0, raw_score / 100))
                
                industry_scores.append({
                    "industry": industry,
                    "score": score,
                    "avg_netprofit_yoy": avg_netprofit,
                    "avg_revenue_yoy": avg_revenue,
                    "avg_roe_yoy": avg_roe,
                    "stock_count": len(stocks),
                })
            
            # 按分数排序
            industry_scores.sort(key=lambda x: x["score"], reverse=True)
            
            # 构建结果
            result = []
            for i, item in enumerate(industry_scores):
                result.append(IndustryRankItem(
                    industry=item["industry"],
                    rank=i + 1,
                    score=round(item["score"], 4),
                    avg_netprofit_yoy=round(item["avg_netprofit_yoy"], 2) if item["avg_netprofit_yoy"] else None,
                    avg_revenue_yoy=round(item["avg_revenue_yoy"], 2) if item["avg_revenue_yoy"] else None,
                    avg_roe_yoy=round(item["avg_roe_yoy"], 2) if item["avg_roe_yoy"] else None,
                    stock_count=item["stock_count"],
                ))
            
            logger.info(f"计算完成，共 {len(result)} 个行业")
            
            # 3. 保存到数据库
            self.save_industry_rank_to_db(query_month, result)
            
            return result
            
        except Exception as e:
            logger.error(f"计算行业景气度失败: {e}", exc_info=True)
            return []
    
    def get_sentiment_scores(
        self,
        codes: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[SentimentItem]:
        """
        获取舆情评分
        
        基于以下 Tushare 数据计算：
        1. 同花顺热度排名（讨论量）
        2. 龙虎榜上榜（机构/游资关注度）
        3. 资金流向（大单净流入）
        
        sentiment_score = normalize(热度分 + 龙虎榜分 + 资金流分)
        """
        # 确定查询日期并转换为YYYYMMDD格式
        if end_date:
            # 去除日期中的连字符，转换为YYYYMMDD格式
            query_date = end_date.replace("-", "")
        else:
            query_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        
        # 先尝试从数据库加载
        db_results = self._load_sentiment_from_db(codes, query_date)
        if db_results:
            logger.info(f"从数据库加载了 {len(db_results)} 条情绪分数数据")
            return db_results
        
        # 再检查内存缓存
        cache_key = f"sentiment_{query_date}_{len(codes)}"
        if _is_cache_valid(cache_key, ttl_minutes=1440):  # 24小时缓存
            cached = _get_cache(cache_key)
            return [cached.get(normalize_code(c), SentimentItem(code=normalize_code(c), sentiment_score=0.0, discussion_volume=0)) 
                    for c in codes]
        
        result_dict: Dict[str, Dict] = {}
        normalized_codes = [normalize_code(c) for c in codes]
        
        # 初始化结果
        for code in normalized_codes:
            result_dict[code] = {
                "code": code,
                "hot_rank": 0,
                "hot_score": 0.0,
                "top_list_score": 0.0,
                "money_flow_score": 0.0,
                "discussion_volume": 0
            }
        
        try:
            # 1. 获取同花顺热度排名
            ths_hot_list = self.tushare_service.fetch_ths_hot(query_date)
            for item in ths_hot_list:
                ts_code = item.get("ts_code", "")
                code = ts_code[:6] if len(ts_code) >= 6 else ts_code
                if code in result_dict:
                    rank = item.get("rank", 999)
                    # 热度分：排名越靠前分越高，前10名高分
                    hot_score = max(0, (100 - rank) / 100) if rank <= 100 else 0
                    result_dict[code]["hot_rank"] = rank
                    result_dict[code]["discussion_volume"] = item.get("hot", 0)
                    result_dict[code]["hot_score"] = hot_score
        except Exception as e:
            logger.warning(f"获取同花顺热度失败: {e}")
        
        try:
            # 2. 获取龙虎榜数据
            top_list = self.tushare_service.fetch_top_list(query_date)
            top_codes = set()
            for item in top_list:
                ts_code = item.get("ts_code", "")
                code = ts_code[:6] if len(ts_code) >= 6 else ts_code
                top_codes.add(code)
                if code in result_dict:
                    # 上龙虎榜加分
                    result_dict[code]["top_list_score"] = 0.3
                    # 如果是涨停原因，额外加分
                    reason = item.get("reason", "")
                    if "涨停" in reason:
                        result_dict[code]["top_list_score"] = 0.5
        except Exception as e:
            logger.warning(f"获取龙虎榜失败: {e}")
        
        try:
            # 3. 获取资金流向
            money_flow = self.tushare_service.fetch_moneyflow(query_date)
            for item in money_flow:
                ts_code = item.get("ts_code", "")
                code = ts_code[:6] if len(ts_code) >= 6 else ts_code
                if code in result_dict:
                    # 计算大单净流入比例
                    buy_lg = item.get("buy_lg_amount", 0) or 0
                    sell_lg = item.get("sell_lg_amount", 0) or 0
                    net_flow = buy_lg - sell_lg
                    # 归一化到 [-1, 1]
                    flow_score = max(-1, min(1, net_flow / 100000))  # 10亿为满分
                    result_dict[code]["money_flow_score"] = flow_score
        except Exception as e:
            logger.warning(f"获取资金流向失败: {e}")
        
        # 4. 计算综合舆情分数
        result = []
        for code in normalized_codes:
            data = result_dict.get(code, {})
            
            # 综合分 = 热度(40%) + 龙虎榜(30%) + 资金流(30%)
            hot_score = data.get("hot_score", 0)
            top_score = data.get("top_list_score", 0)
            flow_score = data.get("money_flow_score", 0)
            
            sentiment = 0.4 * hot_score + 0.3 * top_score + 0.3 * flow_score
            sentiment = max(-1.0, min(1.0, sentiment))
            
            result.append(SentimentItem(
                code=code,
                sentiment_score=round(sentiment, 4),
                discussion_volume=data.get("discussion_volume", 0)
            ))
        
        # 保存到数据库
        self._save_sentiment_to_db(result, query_date, result_dict)
        
        # 缓存
        _set_cache(cache_key, {item.code: item for item in result}, ttl_minutes=1440)  # 24小时缓存
        
        return result
    
    def get_hot_scores(self, codes: List[str]) -> List[HotScoreItem]:
        """
        获取热点/主线分数
        
        基于以下 Tushare 数据计算：
        1. 所属概念板块涨幅
        2. 涨停/连板统计
        3. 北向资金流入
        
        hot_score = normalize(概念强度 + 连板加成 + 北向加成)
        """
        query_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        
        # 先尝试从数据库加载
        db_results = self._load_hot_score_from_db(codes, query_date)
        if db_results:
            logger.info(f"从数据库加载了 {len(db_results)} 条热点分数数据")
            return db_results
        
        # 再检查内存缓存
        cache_key = f"hot_scores_{query_date}_{len(codes)}"
        if _is_cache_valid(cache_key, ttl_minutes=1440):  # 24小时缓存
            cached = _get_cache(cache_key)
            return [cached.get(normalize_code(c), HotScoreItem(code=normalize_code(c), hot_score=0.0)) 
                    for c in codes]
        
        result_dict: Dict[str, Dict] = {}
        normalized_codes = [normalize_code(c) for c in codes]
        
        # 初始化
        for code in normalized_codes:
            result_dict[code] = {
                "code": code,
                "concept_score": 0.0,
                "limit_score": 0.0,
                "concept_tags": []
            }
        
        try:
            # 1. 获取涨跌停数据
            limit_list = self.tushare_service.fetch_limit_list(query_date)
            for item in limit_list:
                ts_code = item.get("ts_code", "")
                code = ts_code[:6] if len(ts_code) >= 6 else ts_code
                if code in result_dict:
                    limit_type = item.get("limit", "")
                    up_stat = item.get("up_stat", 0) or 0  # 连板天数
                    
                    if limit_type == "U":  # 涨停
                        # 连板越多分越高
                        limit_score = min(1.0, 0.3 + up_stat * 0.15)
                        result_dict[code]["limit_score"] = limit_score
                        result_dict[code]["up_stat"] = up_stat
        except Exception as e:
            logger.warning(f"获取涨跌停数据失败: {e}")
        
        try:
            # 2. 获取个股所属概念（采样处理，避免请求过多）
            sample_codes = normalized_codes[:min(30, len(normalized_codes))]
            for code in sample_codes:
                concepts = self.tushare_service.fetch_stock_concepts(code)
                if concepts:
                    concept_names = [c.get("con_name", "") for c in concepts[:5]]
                    result_dict[code]["concept_tags"] = concept_names
                    # 概念数量加分（多概念=题材丰富）
                    result_dict[code]["concept_score"] = min(0.5, len(concepts) * 0.1)
        except Exception as e:
            logger.warning(f"获取概念数据失败: {e}")
        
        try:
            # 3. 龙虎榜上榜加成
            top_list = self.tushare_service.fetch_top_list(query_date)
            for item in top_list:
                ts_code = item.get("ts_code", "")
                code = ts_code[:6] if len(ts_code) >= 6 else ts_code
                if code in result_dict:
                    result_dict[code]["concept_score"] += 0.2
        except Exception as e:
            pass  # 龙虎榜数据可选
        
        try:
            # 4. 获取同花顺热度作为补充（如果前面数据都失败）
            ths_hot_list = self.tushare_service.fetch_ths_hot(query_date)
            for item in ths_hot_list:
                ts_code = item.get("ts_code", "")
                code = ts_code[:6] if len(ts_code) >= 6 else ts_code
                if code in result_dict:
                    rank = item.get("rank", 999)
                    # 如果没有其他分数，用热度排名作为补充
                    if result_dict[code]["limit_score"] == 0 and result_dict[code]["concept_score"] == 0:
                        # 前100名给予基础分数
                        if rank <= 100:
                            hot_based_score = max(0, (100 - rank) / 100) * 0.5
                            result_dict[code]["concept_score"] = hot_based_score
        except Exception as e:
            logger.warning(f"获取热度数据失败: {e}")
        
        # 5. 计算综合热点分数
        result = []
        for code in normalized_codes:
            data = result_dict.get(code, {})
            
            # 综合分 = 涨停/连板(50%) + 概念强度(50%)
            limit_score = data.get("limit_score", 0)
            concept_score = data.get("concept_score", 0)
            
            hot = 0.5 * limit_score + 0.5 * concept_score
            hot = max(0.0, min(1.0, hot))
            
            result.append(HotScoreItem(
                code=code,
                hot_score=round(hot, 4)
            ))
        
        # 保存到数据库
        self._save_hot_score_to_db(result, query_date, result_dict)
        
        # 缓存
        _set_cache(cache_key, {item.code: item for item in result}, ttl_minutes=1440)  # 24小时缓存
        
        return result
