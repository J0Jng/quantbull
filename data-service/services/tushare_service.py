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

    # ==================== 概念板块相关 ====================
    
    def fetch_concept_list(self) -> List[dict]:
        """获取概念板块列表
        
        Returns:
            概念列表，包含 code(概念代码), name(概念名称)
        """
        try:
            df = self.api.concept()
            if df is None or df.empty:
                return []
            return df.to_dict("records")
        except Exception as e:
            logger.error(f"获取概念列表失败: {e}")
            return []
    
    def fetch_concept_detail(self, concept_id: str) -> List[dict]:
        """获取概念板块成分股
        
        Args:
            concept_id: 概念代码（如 TS0）
            
        Returns:
            成分股列表，包含 ts_code, name 等
        """
        try:
            df = self.api.concept_detail(id=concept_id)
            if df is None or df.empty:
                return []
            return df.to_dict("records")
        except Exception as e:
            logger.error(f"获取概念成分股 {concept_id} 失败: {e}")
            return []
    
    def fetch_stock_concepts(self, code: str) -> List[dict]:
        """获取个股所属概念板块
        
        通过遍历概念板块查找（Tushare无直接接口）
        注意：此方法较慢，建议使用缓存
        """
        try:
            normalized_code = normalize_code(code)
            ts_code = normalized_code + get_market_suffix(normalized_code)
            
            # 使用 ths_member 接口（同花顺概念成分）
            df = self.api.ths_member(ts_code=ts_code)
            if df is None or df.empty:
                return []
            return df.to_dict("records")
        except Exception as e:
            logger.warning(f"获取个股概念 {code} 失败: {e}")
            return []
    
    def fetch_ths_index_daily(self, ts_code: str, trade_date: str) -> Optional[dict]:
        """获取同花顺概念/行业指数日行情
        
        Args:
            ts_code: 同花顺指数代码
            trade_date: 交易日期 YYYYMMDD
        """
        try:
            df = self.api.ths_daily(ts_code=ts_code, trade_date=trade_date)
            if df is None or df.empty:
                return None
            return df.iloc[0].to_dict()
        except Exception as e:
            logger.warning(f"获取同花顺指数 {ts_code} 日行情失败: {e}")
            return None

    # ==================== 龙虎榜相关 ====================
    
    def fetch_top_list(self, trade_date: str) -> List[dict]:
        """获取龙虎榜数据
        
        Args:
            trade_date: 交易日期 YYYYMMDD
            
        Returns:
            龙虎榜列表，包含 ts_code, name, reason, buy/sell 等
        """
        try:
            df = self.api.top_list(trade_date=trade_date)
            if df is None or df.empty:
                return []
            return df.to_dict("records")
        except Exception as e:
            logger.error(f"获取龙虎榜 {trade_date} 失败: {e}")
            return []
    
    def fetch_top_inst(self, trade_date: str) -> List[dict]:
        """获取龙虎榜机构交易明细
        
        Args:
            trade_date: 交易日期 YYYYMMDD
            
        Returns:
            机构买卖明细
        """
        try:
            df = self.api.top_inst(trade_date=trade_date)
            if df is None or df.empty:
                return []
            return df.to_dict("records")
        except Exception as e:
            logger.error(f"获取龙虎榜机构明细 {trade_date} 失败: {e}")
            return []
    
    def fetch_top_list_multi_days(self, days: int = 5) -> List[dict]:
        """获取多日龙虎榜汇总数据
        
        Args:
            days: 天数（5 或 20）
            
        Returns:
            汇总后的龙虎榜列表，按净买入额排序
        """
        from datetime import datetime, timedelta
        from collections import defaultdict
        
        try:
            # 计算日期范围（跳过周末）
            end_date = datetime.now()
            trade_dates = []
            current = end_date
            
            while len(trade_dates) < days:
                # 跳过周末
                if current.weekday() < 5:  # 0-4 是周一到周五
                    trade_dates.append(current.strftime("%Y%m%d"))
                current -= timedelta(days=1)
            
            # 汇总数据
            stock_summary = defaultdict(lambda: {
                "ts_code": "",
                "name": "",
                "close": 0,
                "pct_change": 0,
                "total_buy": 0,
                "total_sell": 0,
                "net_amount": 0,
                "appear_count": 0,
                "reasons": set()
            })
            
            # 获取每天的龙虎榜数据
            for trade_date in trade_dates:
                daily_data = self.fetch_top_list(trade_date)
                for item in daily_data:
                    ts_code = item.get("ts_code", "")
                    if not ts_code:
                        continue
                    
                    summary = stock_summary[ts_code]
                    summary["ts_code"] = ts_code
                    summary["name"] = item.get("name", "")
                    summary["close"] = item.get("close", 0)  # 使用最新价格
                    summary["pct_change"] += item.get("pct_change", 0) or 0
                    summary["total_buy"] += item.get("l_buy", 0) or 0
                    summary["total_sell"] += item.get("l_sell", 0) or 0
                    summary["net_amount"] += item.get("net_amount", 0) or 0
                    summary["appear_count"] += 1
                    if item.get("reason"):
                        summary["reasons"].add(item.get("reason"))
            
            # 转换为列表并排序
            result = []
            for ts_code, data in stock_summary.items():
                result.append({
                    "ts_code": data["ts_code"],
                    "name": data["name"],
                    "close": data["close"],
                    "pct_change": round(data["pct_change"], 2),
                    "total_buy": round(data["total_buy"], 2),
                    "total_sell": round(data["total_sell"], 2),
                    "net_amount": round(data["net_amount"], 2),
                    "appear_count": data["appear_count"],
                    "reason": f"{days}日上榜{data['appear_count']}次" if data["appear_count"] > 1 else list(data["reasons"])[0] if data["reasons"] else ""
                })
            
            # 按净买入额降序排序
            result.sort(key=lambda x: x["net_amount"], reverse=True)
            return result[:20]  # 返回前20条
            
        except Exception as e:
            logger.error(f"获取{days}日龙虎榜汇总失败: {e}")
            return []
    
    def fetch_limit_list(self, trade_date: str) -> List[dict]:
        """获取涨跌停股票列表
        
        Args:
            trade_date: 交易日期 YYYYMMDD
            
        Returns:
            涨跌停列表，包含 ts_code, name, limit(U涨停/D跌停), up_stat(连板天数)等
        """
        try:
            df = self.api.limit_list_d(trade_date=trade_date)
            if df is None or df.empty:
                return []
            return df.to_dict("records")
        except Exception as e:
            logger.warning(f"获取涨跌停列表 {trade_date} 失败: {e}")
            return []
    
    def fetch_moneyflow(self, trade_date: str) -> List[dict]:
        """获取个股资金流向
        
        Args:
            trade_date: 交易日期 YYYYMMDD
            
        Returns:
            资金流向数据，包含 buy_sm_amount(小单买入), sell_lg_amount(大单卖出) 等
        """
        try:
            df = self.api.moneyflow(trade_date=trade_date)
            if df is None or df.empty:
                return []
            return df.to_dict("records")
        except Exception as e:
            logger.warning(f"获取资金流向 {trade_date} 失败: {e}")
            return []
    
    def fetch_moneyflow_hsgt(self, start_date: str, end_date: str) -> List[dict]:
        """获取北向资金流向
        
        Args:
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
            
        Returns:
            北向资金数据
        """
        try:
            df = self.api.moneyflow_hsgt(start_date=start_date, end_date=end_date)
            if df is None or df.empty:
                return []
            return df.to_dict("records")
        except Exception as e:
            logger.warning(f"获取北向资金失败: {e}")
            return []
    
    # ==================== 同花顺热度 ====================
    
    def fetch_ths_hot(self, trade_date: Optional[str] = None) -> List[dict]:
        """获取同花顺热度排名（人气榜）
        
        Args:
            trade_date: 交易日期，不传则为最新
            
        Returns:
            热度排名数据
        """
        try:
            params = {}
            if trade_date:
                params["trade_date"] = trade_date
            df = self.api.ths_hot(**params)
            if df is None or df.empty:
                return []
            return df.to_dict("records")
        except Exception as e:
            logger.warning(f"获取同花顺热度失败: {e}")
            return []


