"""横截面特征服务 - 从 data-service 拉取基本面/行业/舆情等特征数据"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import httpx

from core.config import settings

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


class UniverseFeaturesService:
    """
    横截面特征服务
    
    从 data-service 拉取各类特征数据，供策略使用
    """
    
    def __init__(self, data_service_url: Optional[str] = None):
        self.data_service_url = data_service_url or getattr(settings, "data_service_url", "http://data-service:8001")
    
    def fetch_all_features(
        self,
        symbols: List[str],
        asof_date: Optional[str] = None,
        symbol_type_map: Optional[Dict[str, str]] = None
    ) -> Dict[str, Dict]:
        """
        获取所有横截面特征
        
        Args:
            symbols: 标的代码列表
            asof_date: 截止日期 YYYY-MM-DD
            symbol_type_map: {code: "stock"|"etf"} 类型映射
        
        Returns:
            {
                "fundamentals_by_symbol": {...},
                "industry_scores_by_symbol": {...},
                "sentiment_by_symbol": {...},
                "hot_by_symbol": {...},
                "symbol_type_map": {...}
            }
        """
        result = {
            "fundamentals_by_symbol": {},
            "industry_scores_by_symbol": {},
            "sentiment_by_symbol": {},
            "hot_by_symbol": {},
            "symbol_type_map": symbol_type_map or {}
        }
        
        trade_date = None
        if asof_date:
            trade_date = asof_date.replace("-", "")
        
        # 1. 获取基本面数据
        try:
            fundamentals = self._fetch_fundamentals(symbols, trade_date)
            result["fundamentals_by_symbol"] = fundamentals
            logger.info(f"获取基本面数据成功: {len(fundamentals)} 只")
        except Exception as e:
            logger.warning(f"获取基本面数据失败: {e}")
        
        # 2. 获取行业景气度分数
        try:
            industry_scores = self._fetch_industry_scores(asof_date)
            # 将行业分数映射到每个股票
            for symbol, fund_data in result["fundamentals_by_symbol"].items():
                industry = fund_data.get("industry")
                if industry and industry in industry_scores:
                    result["industry_scores_by_symbol"][symbol] = industry_scores[industry]
                else:
                    result["industry_scores_by_symbol"][symbol] = 0.0
            logger.info(f"行业景气度映射完成: {len(result['industry_scores_by_symbol'])} 只")
        except Exception as e:
            logger.warning(f"获取行业景气度失败: {e}")
        
        # 3. 获取舆情分数（MVP: 返回0）
        try:
            sentiment = self._fetch_sentiment(symbols, trade_date)
            result["sentiment_by_symbol"] = sentiment
        except Exception as e:
            logger.warning(f"获取舆情数据失败: {e}")
            # 降级: 全部返回0
            for symbol in symbols:
                result["sentiment_by_symbol"][symbol] = {"sentiment_score": 0.0, "discussion_volume": 0}
        
        # 4. 获取热点分数（MVP: 返回0）
        try:
            hot = self._fetch_hot_scores(symbols)
            result["hot_by_symbol"] = hot
        except Exception as e:
            logger.warning(f"获取热点数据失败: {e}")
            # 降级: 全部返回0
            for symbol in symbols:
                result["hot_by_symbol"][symbol] = 0.0
        
        return result
    
    def _fetch_fundamentals(self, symbols: List[str], trade_date: Optional[str] = None) -> Dict[str, Dict]:
        """获取基本面数据"""
        cache_key = f"fundamentals_{trade_date}_{len(symbols)}"
        if _is_cache_valid(cache_key, ttl_minutes=60):
            cached = _get_cache(cache_key)
            # 只返回请求的股票
            return {s: cached[s] for s in symbols if s in cached}
        
        result = {}
        try:
            # 增加超时时间到180秒，因为首次请求需要从Tushare获取全量数据
            with httpx.Client(timeout=180.0) as client:
                response = client.post(
                    f"{self.data_service_url}/api/fundamentals/batch",
                    json={"codes": symbols, "trade_date": trade_date}
                )
                response.raise_for_status()
                data = response.json()
                
                # 解析响应
                items = []
                if "data" in data:
                    if isinstance(data["data"], dict) and "data" in data["data"]:
                        items = data["data"]["data"]
                    elif isinstance(data["data"], list):
                        items = data["data"]
                
                for item in items:
                    code = item.get("code")
                    if code:
                        result[code] = item
                
                _set_cache(cache_key, result, ttl_minutes=60)
                
        except Exception as e:
            logger.error(f"从 data-service 获取基本面失败: {e}")
        
        return result
    
    def _fetch_industry_scores(self, asof_date: Optional[str] = None) -> Dict[str, float]:
        """获取行业景气度分数"""
        # 按月缓存
        if asof_date:
            month = asof_date[:7]  # YYYY-MM
        else:
            month = datetime.now().strftime("%Y-%m")
        
        cache_key = f"industry_scores_{month}"
        if _is_cache_valid(cache_key, ttl_minutes=1440):  # 缓存1天
            return _get_cache(cache_key)
        
        result = {}
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.get(
                    f"{self.data_service_url}/api/fundamentals/industry/rank",
                    params={"month": month}
                )
                response.raise_for_status()
                data = response.json()
                
                # 解析响应
                items = []
                if "data" in data:
                    if isinstance(data["data"], dict) and "data" in data["data"]:
                        items = data["data"]["data"]
                    elif isinstance(data["data"], list):
                        items = data["data"]
                
                for item in items:
                    industry = item.get("industry")
                    score = item.get("score", 0.0)
                    if industry:
                        result[industry] = score
                
                _set_cache(cache_key, result, ttl_minutes=1440)
                
        except Exception as e:
            logger.error(f"从 data-service 获取行业排名失败: {e}")
        
        return result
    
    def _fetch_sentiment(self, symbols: List[str], trade_date: Optional[str] = None) -> Dict[str, Dict]:
        """获取舆情分数"""
        result = {}
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.data_service_url}/api/fundamentals/sentiment/score",
                    json={"codes": symbols, "start_date": trade_date, "end_date": trade_date}
                )
                response.raise_for_status()
                data = response.json()
                
                # 解析响应
                items = []
                if "data" in data:
                    if isinstance(data["data"], dict) and "data" in data["data"]:
                        items = data["data"]["data"]
                    elif isinstance(data["data"], list):
                        items = data["data"]
                
                for item in items:
                    code = item.get("code")
                    if code:
                        result[code] = {
                            "sentiment_score": item.get("sentiment_score", 0.0),
                            "discussion_volume": item.get("discussion_volume", 0)
                        }
                
        except Exception as e:
            logger.warning(f"获取舆情数据失败: {e}")
        
        # 确保每个symbol都有数据（降级为0）
        for symbol in symbols:
            if symbol not in result:
                result[symbol] = {"sentiment_score": 0.0, "discussion_volume": 0}
        
        return result
    
    def _fetch_hot_scores(self, symbols: List[str]) -> Dict[str, float]:
        """获取热点分数"""
        result = {}
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.data_service_url}/api/fundamentals/hot/score",
                    json={"codes": symbols}
                )
                response.raise_for_status()
                data = response.json()
                
                # 解析响应
                items = []
                if "data" in data:
                    if isinstance(data["data"], dict) and "data" in data["data"]:
                        items = data["data"]["data"]
                    elif isinstance(data["data"], list):
                        items = data["data"]
                
                for item in items:
                    code = item.get("code")
                    if code:
                        result[code] = item.get("hot_score", 0.0)
                
        except Exception as e:
            logger.warning(f"获取热点数据失败: {e}")
        
        # 确保每个symbol都有数据（降级为0）
        for symbol in symbols:
            if symbol not in result:
                result[symbol] = 0.0
        
        return result
