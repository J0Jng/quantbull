"""Data Service 客户端（调用 data-service 获取行情数据）"""
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
        # 假设 data-service 运行在 8001 端口
        self.base_url = f"http://localhost:8001/api"
        self.timeout = 30.0
    
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
                # 假设 data-service 提供此接口
                response = await client.get(
                    f"{self.base_url}/market/overview",
                    params={"date": date}
                )
                response.raise_for_status()
                data = response.json()
                
                return MarketOverview(
                    indices=data.get("indices", {}),
                    total_turnover=data.get("total_turnover", 0.0),
                    rising_count=data.get("rising_count", 0),
                    falling_count=data.get("falling_count", 0),
                    flat_count=data.get("flat_count", 0),
                )
        except httpx.HTTPError as e:
            logger.error(f"获取市场概览失败: {e}")
            # 返回模拟数据（开发环境）
            if settings.env == "local":
                logger.warning("使用模拟市场概览数据")
                return MarketOverview(
                    indices={"sh_index": 3000.0, "sz_index": 10000.0},
                    total_turnover=500000000000.0,
                    rising_count=2000,
                    falling_count=1500,
                    flat_count=500,
                )
            raise
    
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
                # 假设 data-service 提供此接口
                response = await client.get(
                    f"{self.base_url}/etf/list",
                    params={"date": date, "limit": limit}
                )
                response.raise_for_status()
                data = response.json()
                
                return [
                    ETFData(
                        code=item["code"],
                        name=item["name"],
                        change_pct=item.get("change_pct", 0.0),
                        turnover=item.get("turnover", 0.0),
                        volume=item.get("volume", 0.0),
                        category=item.get("category"),
                    )
                    for item in data.get("etf_list", [])
                ]
        except httpx.HTTPError as e:
            logger.error(f"获取 ETF 列表失败: {e}")
            # 返回模拟数据（开发环境）
            if settings.env == "local":
                logger.warning("使用模拟 ETF 数据")
                return [
                    ETFData(
                        code="510300",
                        name="沪深300ETF",
                        change_pct=1.5,
                        turnover=1000000000.0,
                        volume=50000000.0,
                        category="宽基",
                    ),
                    ETFData(
                        code="159919",
                        name="300ETF",
                        change_pct=1.2,
                        turnover=800000000.0,
                        volume=40000000.0,
                        category="宽基",
                    ),
                ]
            raise
    
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
                # 假设 data-service 提供此接口
                response = await client.get(
                    f"{self.base_url}/stock/list",
                    params={
                        "date": date,
                        "limit": limit,
                        "min_turnover": min_turnover,
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                return [
                    StockData(
                        code=item["code"],
                        name=item["name"],
                        change_pct=item.get("change_pct", 0.0),
                        turnover=item.get("turnover", 0.0),
                        turnover_rate=item.get("turnover_rate", 0.0),
                        industry=item.get("industry"),
                    )
                    for item in data.get("stock_list", [])
                ]
        except httpx.HTTPError as e:
            logger.error(f"获取股票列表失败: {e}")
            # 返回模拟数据（开发环境）
            if settings.env == "local":
                logger.warning("使用模拟股票数据")
                return [
                    StockData(
                        code="000001",
                        name="平安银行",
                        change_pct=2.5,
                        turnover=500000000.0,
                        turnover_rate=1.2,
                        industry="银行",
                    ),
                    StockData(
                        code="000002",
                        name="万科A",
                        change_pct=-1.2,
                        turnover=300000000.0,
                        turnover_rate=0.8,
                        industry="房地产",
                    ),
                ]
            raise
    
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
