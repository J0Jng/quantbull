"""
Tushare 实时行情服务
~~~~~~~~~~~~~~~~~~

使用 Tushare API 获取 A 股实时行情数据（使用 get_realtime_quotes 接口）。

使用示例:
    ```python
    from core.config import settings
    from services.eastmoney_spider import TushareQuoteService
    
    # 1. 设置环境变量
    # export TUSHARE_TOKEN='your_token_here'
    
    # 2. 创建服务实例
    service = TushareQuoteService(token=settings.tushare_token)
    
    # 3. 批量获取行情
    success_items, failed_codes = service.fetch_quotes(['000001', '600000', '159915'])
    
    # 4. 查看结果
    for item in success_items:
        print(f"{item.code} {item.name}: ¥{item.price} ({item.pct_change:+.2f}%)")
    ```

字段说明:
    - price: 最新价（元）
    - pct_change: 涨跌幅（百分比，如 2.5 表示 +2.5%）
    - turnover: 成交额（元）
    - update_time: 数据更新时间
    
依赖:
    pip install tushare>=1.2.89

注意:
    使用 Tushare 旧版 get_realtime_quotes 接口，无需积分即可使用。
    仅需注册获取 token 即可调用。
"""

import logging
from datetime import datetime
from typing import List, Optional, Tuple

import tushare as ts

from schemas.quote import QuoteItem

logger = logging.getLogger(__name__)


class TushareQuoteService:
    """Tushare 实时行情服务
    
    使用 Tushare get_realtime_quotes 接口获取股票实时行情数据。
    此接口为旧版免费接口，无需积分，注册即可使用。
    支持批量查询，自动处理代码格式和错误。
    """
    
    # 交易所后缀映射（根据股票代码前缀判断）
    EXCHANGE_MAP = {
        "000": "SZ",  # 深圳主板
        "001": "SZ",  # 深圳主板
        "002": "SZ",  # 深圳中小板
        "003": "SZ",  # 深圳主板
        "300": "SZ",  # 深圳创业板
        "301": "SZ",  # 深圳创业板
        "600": "SH",  # 上海主板
        "601": "SH",  # 上海主板
        "603": "SH",  # 上海主板
        "605": "SH",  # 上海主板
        "688": "SH",  # 上海科创板
        # ETF 前缀
        "15": "SZ",   # 深圳 ETF (159xxx)
        "16": "SZ",   # 深圳 ETF (16xxxx)
        "51": "SH",   # 上海 ETF (512xxx, 515xxx, 516xxx, 517xxx, 518xxx)
        "56": "SH",   # 上海 ETF (563xxx, 566xxx, 567xxx, 568xxx, 569xxx)
    }
    
    def __init__(self, token: str):
        """初始化 Tushare 服务
        
        Args:
            token: Tushare API token
            
        Raises:
            ValueError: token 为空时抛出
        """
        if not token or token.strip() == "":
            error_msg = (
                "Tushare Token 未配置！请设置环境变量：\n"
                "export TUSHARE_TOKEN='your_token_here'\n"
                "获取 Token: https://tushare.pro/register"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.token = token
        # 设置 Tushare token
        ts.set_token(token)
        self.pro = ts.pro_api()
        logger.info("Tushare 服务初始化成功")
    
    def _normalize_code(self, code: str) -> str:
        """标准化股票代码为 6 位格式
        
        Args:
            code: 股票代码，可能是 5 位或 6 位
            
        Returns:
            6 位标准代码
        """
        return code.strip().zfill(6)
    
    def _get_ts_code(self, stock_code: str) -> Optional[str]:
        """将 6 位代码转换为 Tushare 格式（带交易所后缀）
        
        Args:
            stock_code: 6 位股票代码，如 "000001", "600000"
            
        Returns:
            Tushare 格式代码，如 "000001.SZ", "600000.SH"，不支持返回 None
        """
        if len(stock_code) < 3:
            return None
        
        # 先检查 3 位前缀
        prefix3 = stock_code[:3]
        if prefix3 in self.EXCHANGE_MAP:
            exchange = self.EXCHANGE_MAP[prefix3]
            return f"{stock_code}.{exchange}"
        
        # 检查 2 位前缀（ETF）
        prefix2 = stock_code[:2]
        if prefix2 in self.EXCHANGE_MAP:
            exchange = self.EXCHANGE_MAP[prefix2]
            return f"{stock_code}.{exchange}"
        
        logger.warning(f"无法识别股票代码前缀: {stock_code}")
        return None
    
    def _parse_quote_item(self, row: dict, original_code: str) -> Optional[QuoteItem]:
        """解析 Tushare 返回的数据为 QuoteItem
        
        Tushare get_realtime_quotes 字段说明:
        - code: 股票代码（6 位）
        - name: 股票名称
        - price: 最新价（元）
        - pre_close: 昨收价（元）
        - amount: 成交额（手，需要根据股价计算或直接使用）
        
        注意：接口返回的 amount 单位实际是「手」(100股)，不是金额
        需要根据 price * volume 来计算成交额
        
        Args:
            row: Tushare 返回的数据行
            original_code: 原始 6 位代码（用于失败时记录）
            
        Returns:
            QuoteItem 对象，解析失败返回 None
        """
        try:
            # 提取必需字段
            code = row.get("code", "")
            name = row.get("name", "").strip()
            price = row.get("price")
            pre_close = row.get("pre_close")  # 昨收价，用于计算涨跌幅
            volume = row.get("volume")  # 成交量（手）
            
            # 验证必需字段
            if not code or not name:
                logger.warning(f"数据缺少必需字段 {original_code}: code={code}, name={name}")
                return None
            
            # 价格转换
            if price is None or price == "" or price == "0.00":
                logger.warning(f"价格数据无效 {original_code}: price={price}")
                return None
            
            try:
                price_float = float(price)
            except (ValueError, TypeError) as e:
                logger.error(f"价格转换失败 {original_code}: {price}, error: {e}")
                return None
            
            # 计算涨跌幅：(当前价 - 昨收价) / 昨收价 * 100
            pct_change_float = 0.0
            try:
                if pre_close and pre_close != "" and pre_close != "0.00":
                    pre_close_float = float(pre_close)
                    if pre_close_float > 0:
                        pct_change_float = ((price_float - pre_close_float) / pre_close_float) * 100.0
            except (ValueError, TypeError) as e:
                logger.warning(f"涨跌幅计算失败 {original_code}: pre_close={pre_close}, error={e}")
            
            # 成交额计算：成交量(手) * 每手股数(100) * 均价
            # 这里简化使用 volume * 100 * price 作为粗略估算
            # 注意：get_realtime_quotes 的 volume 单位是手 (1手=100股)
            turnover_float = 0.0
            try:
                if volume and volume != "" and volume != "0":
                    volume_float = float(volume)  # 单位：手
                    turnover_float = volume_float * 100.0 * price_float  # 手 * 100股/手 * 价格
            except (ValueError, TypeError) as e:
                logger.warning(f"成交额计算失败 {original_code}: volume={volume}, error={e}")
                turnover_float = 0.0
            
            return QuoteItem(
                code=original_code,  # 使用原始 6 位代码
                name=name,
                price=price_float,
                pct_change=pct_change_float,
                turnover=turnover_float,
                update_time=datetime.now(),
            )
            
        except Exception as e:
            logger.error(f"解析数据异常 {original_code}: {e}, row={row}")
            return None
    
    def fetch_quotes(self, stock_codes: List[str]) -> Tuple[List[QuoteItem], List[str]]:
        """批量获取股票实时行情
        
        Args:
            stock_codes: 股票代码列表（6 位代码，如 ['000001', '600000']）
            
        Returns:
            (成功列表, 失败代码列表)
            - 成功列表: QuoteItem 对象列表
            - 失败代码列表: 无法获取数据的股票代码
        """
        if not stock_codes:
            logger.warning("股票代码列表为空")
            return [], []
        
        success_items: List[QuoteItem] = []
        failed_codes: List[str] = []
        
        # 标准化代码并转换为 Tushare 格式
        code_mapping = {}  # ts_code -> original_code
        ts_codes = []
        
        for code in stock_codes:
            normalized = self._normalize_code(code)
            ts_code = self._get_ts_code(normalized)
            
            if ts_code is None:
                logger.warning(f"不支持的股票代码: {code}")
                failed_codes.append(normalized)
                continue
            
            ts_codes.append(ts_code)
            code_mapping[ts_code] = normalized
        
        if not ts_codes:
            logger.warning("没有有效的股票代码")
            return [], failed_codes
        
        logger.info(f"开始获取 {len(ts_codes)} 支股票实时行情: {ts_codes}")
        
        try:
            # 调用 Tushare get_realtime_quotes 接口（旧版接口，支持批量查询）
            # 注意：此接口使用 6 位代码列表，不需要交易所后缀
            code_list = [code_mapping[ts_code] for ts_code in ts_codes]
            
            df = ts.get_realtime_quotes(code_list)
            
            if df is None or df.empty:
                logger.warning(f"未获取到任何数据，全部标记为失败")
                failed_codes.extend(code_mapping.values())
                return [], failed_codes
            
            logger.info(f"获取到 {len(df)} 条数据")
            
            # 记录已成功的代码
            received_codes = set()
            
            # 解析每一行数据
            for _, row in df.iterrows():
                row_dict = row.to_dict()
                code = row_dict.get("code", "")
                
                # 标准化代码
                normalized_code = self._normalize_code(code)
                
                if normalized_code not in code_mapping.values():
                    logger.warning(f"返回了未请求的代码: {code}")
                    continue
                
                received_codes.add(normalized_code)
                
                quote_item = self._parse_quote_item(row_dict, normalized_code)
                if quote_item:
                    success_items.append(quote_item)
                else:
                    failed_codes.append(normalized_code)
            
            # 找出未返回数据的代码
            for original_code in code_mapping.values():
                if original_code not in received_codes:
                    logger.warning(f"未返回数据: {original_code}")
                    failed_codes.append(original_code)
            
            logger.info(f"成功: {len(success_items)}, 失败: {len(failed_codes)}")
            
        except Exception as e:
            logger.error(f"Tushare API 调用异常: {e}")
            # API 调用失败，所有代码都标记为失败
            failed_codes.extend(code_mapping.values())
        
        return success_items, failed_codes

