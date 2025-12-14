import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import requests
from lxml import etree

from schemas.quote import QuoteItem

logger = logging.getLogger(__name__)


class EastMoneySpider:
    """东方财富实时行情爬虫"""
    
    BASE_URL = "http://push2.eastmoney.com/api/qt/stock/get"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "http://quote.eastmoney.com/",
    }
    
    # 市场代码映射
    MARKET_MAP = {
        "000": "0",  # 深圳主板
        "001": "0",  # 深圳主板
        "002": "0",  # 深圳中小板
        "003": "0",  # 深圳主板
        "300": "0",  # 深圳创业板
        "600": "1",  # 上海主板
        "601": "1",  # 上海主板
        "603": "1",  # 上海主板
        "605": "1",  # 上海主板
        "688": "1",  # 上海科创板
    }
    
    def _get_market_code(self, stock_code: str) -> Optional[str]:
        """根据股票代码判断市场
        
        Args:
            stock_code: 股票代码，如 "000001", "600000"
            
        Returns:
            市场代码："0" 表示深圳，"1" 表示上海，None 表示不支持
        """
        if len(stock_code) < 3:
            return None
        
        prefix = stock_code[:3]
        return self.MARKET_MAP.get(prefix)
    
    def _build_secid(self, stock_code: str) -> Optional[str]:
        """构建 secid 参数
        
        Args:
            stock_code: 股票代码
            
        Returns:
            secid 格式：如 "0.000001" 或 "1.600000"
        """
        market_code = self._get_market_code(stock_code)
        if market_code is None:
            return None
        return f"{market_code}.{stock_code}"
    
    def _parse_price(self, value: str) -> float:
        """解析价格字符串为浮点数"""
        try:
            return float(value.strip())
        except (ValueError, AttributeError):
            return 0.0
    
    def _fetch_single_quote(self, stock_code: str) -> Optional[QuoteItem]:
        """获取单个股票的实时行情
        
        Args:
            stock_code: 股票代码
            
        Returns:
            QuoteItem 对象，失败返回 None
        """
        secid = self._build_secid(stock_code)
        if secid is None:
            logger.warning(f"不支持的股票代码: {stock_code}")
            return None
        
        try:
            params = {
                "secid": secid,
                "fields": "f57,f58,f107,f137,f46,f43,f44,f45,f47,f48,f60,f170,f116",
            }
            
            response = requests.get(
                self.BASE_URL,
                params=params,
                headers=self.HEADERS,
                timeout=10,
            )
            response.raise_for_status()
            
            data = response.json()
            
            # 解析响应数据
            if data.get("rc") != 0:
                logger.warning(f"API 返回错误: {data.get('msg', 'Unknown error')} for {stock_code}")
                return None
            
            quote_data = data.get("data", {})
            if not quote_data:
                logger.warning(f"未获取到数据: {stock_code}")
                return None
            
            # 字段映射（根据东方财富 API 实际返回字段）
            # f58: 股票名称
            # f43: 最新价（单位：分，需要除以100）
            # f170: 涨跌幅（单位：分，需要除以100，如 -18 表示 -0.18%）
            # f47: 成交额（单位：万元，需要乘以10000转换为元）
            
            name = str(quote_data.get("f58", "")).strip()
            
            # 价格处理：API 返回的是以分为单位，需要除以100
            price_raw = quote_data.get("f43")
            if price_raw is None:
                logger.warning(f"价格数据为空: {stock_code}, quote_data keys: {list(quote_data.keys())}")
                return None
            
            # 转换为浮点数并除以100（从分转换为元）
            try:
                price = float(price_raw) / 100.0
            except (ValueError, TypeError) as e:
                logger.error(f"价格转换失败 {stock_code}: {price_raw}, error: {e}")
                return None
            
            # 涨跌幅处理：API 返回的是以分为单位，需要除以100
            pct_change_raw = quote_data.get("f170", 0)
            try:
                pct_change = float(pct_change_raw) / 100.0
            except (ValueError, TypeError):
                pct_change = 0.0
            
            # 成交额处理：API 返回的是万元，需要乘以10000转换为元
            turnover_raw = quote_data.get("f47", 0)
            try:
                turnover = float(turnover_raw) * 10000.0
            except (ValueError, TypeError):
                turnover = 0.0
            
            # 如果名称为空，说明数据无效
            if not name:
                logger.warning(f"数据无效: {stock_code}, name为空")
                return None
            
            return QuoteItem(
                code=stock_code,
                name=name,
                price=price,
                pct_change=pct_change,
                turnover=turnover,
                update_time=datetime.now(),
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"请求异常 {stock_code}: {e}")
            return None
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"解析异常 {stock_code}: {e}")
            return None
        except Exception as e:
            logger.error(f"未知异常 {stock_code}: {e}")
            return None
    
    def fetch_quotes(self, stock_codes: List[str]) -> Tuple[List[QuoteItem], List[str]]:
        """批量获取股票实时行情
        
        Args:
            stock_codes: 股票代码列表
            
        Returns:
            (成功列表, 失败代码列表)
        """
        success_items: List[QuoteItem] = []
        failed_codes: List[str] = []
        
        for code in stock_codes:
            # 清理代码格式
            code = code.strip().zfill(6)  # 补齐到6位
            
            quote = self._fetch_single_quote(code)
            if quote:
                success_items.append(quote)
            else:
                failed_codes.append(code)
        
        return success_items, failed_codes

