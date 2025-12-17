import logging
from datetime import datetime
from typing import List, Optional, Tuple

import tushare as ts
from sqlalchemy.dialects.postgresql import insert

from core.config import settings
from models.daily_quote import DailyQuote
from schemas.tushare import DailyQuoteItem

logger = logging.getLogger(__name__)

# 全局 Tushare API 实例
_tushare_api: Optional["DataApi"] = None #type: ignore


def get_tushare_api() -> "DataApi": #type: ignore
    """获取全局 Tushare API 实例"""
    global _tushare_api
    
    if _tushare_api is None:
        if not settings.tushare_token:
            raise ValueError("TUSHARE_TOKEN 未配置，请在环境变量或 .env 文件中设置")
        
        _tushare_api = ts.pro_api(settings.tushare_token)
        logger.info("Tushare API 初始化成功")
    
    return _tushare_api


def normalize_code(code: str) -> str:
    """标准化股票代码为 6 位字符串（不带 .SZ / .SH）"""
    code = code.strip().upper()
    
    # 移除后缀
    if code.endswith(".SZ") or code.endswith(".SH"):
        code = code[:-3]
    
    # 补齐到 6 位
    code = code.zfill(6)
    
    return code


def get_market_suffix(code: str) -> str:
    """根据股票代码获取市场后缀
    
    Args:
        code: 6位股票代码
        
    Returns:
        ".SZ" 或 ".SH"
    """
    if len(code) < 3:
        return ".SZ"
    
    prefix = code[:3]
    # 深圳：000, 001, 002, 003, 300
    if prefix in ["000", "001", "002", "003", "300"]:
        return ".SZ"
    # 上海：600, 601, 603, 605, 688
    else:
        return ".SH"


class TushareService:
    """Tushare 数据服务"""
    
    def __init__(self):
        self.api = get_tushare_api()
    
    def fetch_daily(
        self,
        codes: List[str],
        start_date: str,
        end_date: str,
    ) -> Tuple[List[DailyQuoteItem], List[str]]:
        """获取日线行情数据
        
        Args:
            codes: 股票代码列表
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
            
        Returns:
            (成功数据列表, 失败代码列表)
        """
        success_items: List[DailyQuoteItem] = []
        failed_codes: List[str] = []
        
        for code in codes:
            try:
                # 标准化代码
                normalized_code = normalize_code(code)
                ts_code = normalized_code + get_market_suffix(normalized_code)
                
                # 调用 Tushare API
                df = self.api.daily(
                    ts_code=ts_code,
                    start_date=start_date,
                    end_date=end_date,
                )
                
                # 处理空数据
                if df is None or df.empty:
                    logger.warning(f"未获取到数据: {code} ({ts_code})")
                    failed_codes.append(code)
                    continue
                
                # 转换为标准格式
                for _, row in df.iterrows():
                    item = DailyQuoteItem(
                        code=normalized_code,
                        trade_date=str(row["trade_date"]),
                        open=float(row["open"]),
                        high=float(row["high"]),
                        low=float(row["low"]),
                        close=float(row["close"]),
                        vol=int(row["vol"]),
                        amount=float(row["amount"]),
                    )
                    success_items.append(item)
                
                logger.info(f"成功获取 {code} ({ts_code}) 数据: {len(df)} 条")
                
            except Exception as e:
                logger.error(f"获取 {code} 数据失败: {e}")
                failed_codes.append(code)
        
        return success_items, failed_codes
    
    def fetch_stock_basic(self) -> List[dict]:
        """获取股票基础信息"""
        try:
            df = self.api.stock_basic(
                exchange="",
                list_status="L",
                fields="ts_code,symbol,name,area,industry,list_date",
            )
            
            if df is None or df.empty:
                return []
            
            return df.to_dict("records")
        except Exception as e:
            logger.error(f"获取股票基础信息失败: {e}")
            return []
    
    def fetch_fund_daily(
        self,
        codes: List[str],
        start_date: str,
        end_date: str,
    ) -> Tuple[List[DailyQuoteItem], List[str]]:
        """获取 ETF 日线行情"""
        success_items: List[DailyQuoteItem] = []
        failed_codes: List[str] = []
        
        for code in codes:
            try:
                normalized_code = normalize_code(code)
                ts_code = normalized_code + get_market_suffix(normalized_code)
                
                df = self.api.fund_daily(
                    ts_code=ts_code,
                    start_date=start_date,
                    end_date=end_date,
                )
                
                if df is None or df.empty:
                    logger.warning(f"未获取到 ETF 数据: {code}")
                    failed_codes.append(code)
                    continue
                
                for _, row in df.iterrows():
                    item = DailyQuoteItem(
                        code=normalized_code,
                        trade_date=str(row["trade_date"]),
                        open=float(row["open"]),
                        high=float(row["high"]),
                        low=float(row["low"]),
                        close=float(row["close"]),
                        vol=int(row["vol"]),
                        amount=float(row["amount"]),
                    )
                    success_items.append(item)
                
            except Exception as e:
                logger.error(f"获取 ETF {code} 数据失败: {e}")
                failed_codes.append(code)
        
        return success_items, failed_codes
    
    def fetch_index_daily(
        self,
        index_code: str,
        start_date: str,
        end_date: str,
    ) -> List[DailyQuoteItem]:
        """获取指数日线行情"""
        try:
            df = self.api.index_daily(
                ts_code=index_code,
                start_date=start_date,
                end_date=end_date,
            )
            
            if df is None or df.empty:
                return []
            
            items = []
            for _, row in df.iterrows():
                item = DailyQuoteItem(
                    code=index_code,
                    trade_date=str(row["trade_date"]),
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    vol=int(row["vol"]),
                    amount=float(row["amount"]),
                )
                items.append(item)
            
            return items
        except Exception as e:
            logger.error(f"获取指数 {index_code} 数据失败: {e}")
            return []
    
    def fetch_fina_indicator(
        self,
        code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[dict]:
        """获取主要财务指标"""
        try:
            normalized_code = normalize_code(code)
            ts_code = normalized_code + get_market_suffix(normalized_code)
            
            params = {"ts_code": ts_code}
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
            
            df = self.api.fina_indicator(**params)
            
            if df is None or df.empty:
                return []
            
            return df.to_dict("records")
        except Exception as e:
            logger.error(f"获取财务指标 {code} 失败: {e}")
            return []

