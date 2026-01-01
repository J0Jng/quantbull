"""Data Service 客户端（调用 data-service 获取行情数据）"""
import os
import httpx
from typing import Optional
from datetime import datetime

from core.config import settings
from core.logger import get_logger
from schemas.daily_report import MarketDataInput, MarketOverview, ETFData, StockData

logger = get_logger(__name__)


class DataServiceClient:
    """Data Service 客户端"""
    
    def __init__(self):
        """初始化客户端"""
        # 优先读取环境变量 DATA_SERVICE_URL（docker-compose 提供）
        data_service_url = os.getenv('DATA_SERVICE_URL', '') or getattr(settings, 'data_service_url', '')
        
        if data_service_url:
            # 使用完整 URL，确保拼上 /api
            self.base_url = data_service_url.rstrip('/') + '/api'
        else:
            # fallback 到 host/port 配置
            data_service_host = getattr(settings, 'data_service_host', 'data-service')
            data_service_port = getattr(settings, 'data_service_port', 8001)
            self.base_url = f"http://{data_service_host}:{data_service_port}/api"
        
        self.timeout = 60.0  # 增加超时时间，因为 tushare 请求可能较慢
        logger.info(f"Data Service 客户端初始化: {self.base_url}")
    
    async def get_market_overview(self, date: str) -> MarketOverview:
        """
        获取市场概览数据
        
        Args:
            date: 日期 YYYY-MM-DD
            
        Returns:
            MarketOverview: 市场概览数据
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/market/overview",
                    params={"date": date}
                )
                response.raise_for_status()
                result = response.json()
                
                # 处理统一响应格式 {"code": 0, "message": "ok", "data": {...}}
                if isinstance(result, dict) and "data" in result:
                    data = result["data"]
                else:
                    data = result
                
                # 构建市场概览数据
                # data-service 返回: {"trade_date", "market_status", "indices": [...], "total_turnover"}
                indices_data = {}
                if "indices" in data and isinstance(data["indices"], list):
                    for idx in data["indices"]:
                        # data-service 使用 symbol/close/pct_change
                        symbol = idx.get("symbol", idx.get("code", "unknown"))
                        close = idx.get("close", idx.get("latest_price", 0.0))
                        indices_data[symbol] = close
                
                return MarketOverview(
                    indices=indices_data,
                    total_turnover=data.get("total_turnover", 0.0),
                    # data-service 可能不提供这些字段，默认为 0
                    rising_count=data.get("rising_count", 0),
                    falling_count=data.get("falling_count", 0),
                    flat_count=data.get("flat_count", 0),
                )
        except httpx.HTTPError as e:
            logger.error(f"获取市场概览失败: {e}")
            raise Exception(f"无法获取市场数据：{str(e)}。请确保 data-service 服务正常运行，且当天有交易数据。")
    
    async def get_etf_list(self, date: str, limit: int = 100) -> list[ETFData]:
        """
        获取 ETF 列表
        
        Args:
            date: 日期 YYYY-MM-DD
            limit: 返回数量限制
            
        Returns:
            List[ETFData]: ETF 列表
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/etf/list",
                    params={"date": date, "limit": limit}
                )
                response.raise_for_status()
                result = response.json()
                
                # 处理统一响应格式
                if isinstance(result, dict) and "data" in result:
                    data = result["data"]
                else:
                    data = result
                
                # 兼容 data 为 list 的情况（data-service 直接返回 List[ETFItem]）
                if isinstance(data, list):
                    etf_list = data
                else:
                    etf_list = data.get("etf_list", data.get("etfs", []))
                    if not isinstance(etf_list, list):
                        etf_list = []
                
                return [
                    ETFData(
                        # data-service 使用 symbol，daily-report 使用 code
                        code=item.get("code", item.get("symbol", item.get("ts_code", ""))),
                        name=item.get("name", ""),
                        # data-service 使用 pct_change，daily-report 使用 change_pct
                        change_pct=float(item.get("change_pct", item.get("pct_change", item.get("pct_chg", 0.0)))),
                        # data-service 可能没有 turnover，使用 volume 或默认值
                        turnover=float(item.get("turnover", item.get("amount", item.get("volume", 0.0)))),
                        volume=float(item.get("volume", item.get("vol", 0.0))),
                        category=item.get("category", item.get("fund_type")),
                    )
                    for item in etf_list
                ]
        except httpx.HTTPError as e:
            logger.error(f"获取 ETF 列表失败: {e}")
            raise Exception(f"无法获取 ETF 数据：{str(e)}。请确保 data-service 服务正常运行，且当天有交易数据。")
    
    async def get_stock_list(
        self, 
        date: str, 
        limit: int = 500,
        min_turnover: float = 100000000.0  # 最小成交额过滤
    ) -> list[StockData]:
        """
        获取股票列表
        
        Args:
            date: 日期 YYYY-MM-DD
            limit: 返回数量限制
            min_turnover: 最小成交额过滤
            
        Returns:
            List[StockData]: 股票列表
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/stock/list",
                    params={
                        "date": date,
                        "limit": limit,
                        "min_turnover": min_turnover,
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                # 处理统一响应格式
                if isinstance(result, dict) and "data" in result:
                    data = result["data"]
                else:
                    data = result
                
                # 兼容 data 为 list 的情况（data-service 直接返回 List[StockItem]）
                if isinstance(data, list):
                    stock_list = data
                else:
                    stock_list = data.get("stock_list", data.get("stocks", []))
                    if not isinstance(stock_list, list):
                        stock_list = []
                
                return [
                    StockData(
                        # data-service 使用 symbol，daily-report 使用 code
                        code=item.get("code", item.get("symbol", item.get("ts_code", ""))),
                        name=item.get("name", ""),
                        # data-service 使用 pct_change，daily-report 使用 change_pct
                        change_pct=float(item.get("change_pct", item.get("pct_change", item.get("pct_chg", 0.0)))),
                        # data-service 可能没有 turnover/amount
                        turnover=float(item.get("turnover", item.get("amount", 0.0))),
                        turnover_rate=float(item.get("turnover_rate", item.get("turnover_rate_f", 0.0))),
                        industry=item.get("industry", item.get("industry_name")),
                    )
                    for item in stock_list
                ]
        except httpx.HTTPError as e:
            logger.error(f"获取股票列表失败: {e}")
            raise Exception(f"无法获取股票数据：{str(e)}。请确保 data-service 服务正常运行，且当天有交易数据。")
    
    async def fetch_market_data(self, date: str) -> MarketDataInput:
        """
        聚合获取所有市场数据
        
        Args:
            date: 日期 YYYY-MM-DD
            
        Returns:
            MarketDataInput: 聚合的市场数据
        """
        logger.info(f"开始获取 {date} 的市场数据")
        
        # 并行获取数据
        market_overview = await self.get_market_overview(date)
        etf_list = await self.get_etf_list(date)
        stock_list = await self.get_stock_list(date)
        
        logger.info(
            f"获取市场数据完成: "
            f"ETF {len(etf_list)} 只, "
            f"股票 {len(stock_list)} 只"
        )
        
        return MarketDataInput(
            market_overview=market_overview,
            etf_list=etf_list,
            stock_list=stock_list,
            report_date=date,
        )
