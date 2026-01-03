"""数据加载服务 - 统一接口加载行情数据"""
import logging
from datetime import datetime
from typing import Literal

import pandas as pd
import httpx

from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)


def load_market_data(
    stock_code: str,
    start_date: str,
    end_date: str,
    source: Literal["tdengine", "tushare"] = "tushare"
) -> pd.DataFrame:
    """
    统一接口加载行情数据
    
    Args:
        stock_code: 股票代码（如：000001）
        start_date: 开始日期（YYYY-MM-DD）
        end_date: 结束日期（YYYY-MM-DD）
        source: 数据源（tdengine 或 tushare）
    
    Returns:
        DataFrame with columns: ['date', 'open', 'high', 'low', 'close', 'volume']
        日期格式为 datetime，索引为日期
    """
    if source == "tushare":
        return _load_from_tushare(stock_code, start_date, end_date)
    elif source == "tdengine":
        return _load_from_tdengine(stock_code, start_date, end_date)
    else:
        raise ValueError(f"不支持的数据源: {source}")


def _load_from_tushare(
    stock_code: str,
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """
    从 Tushare 加载数据
    
    注意：这里通过调用 data-service 的 API 获取数据
    如果 data-service 不可用，可以回退到直接调用 Tushare API
    """
    try:
        # 尝试从 data-service 获取数据
        data_service_url = getattr(settings, "data_service_url")
        
        # 转换日期格式：YYYY-MM-DD -> YYYYMMDD
        start_date_ts = start_date.replace("-", "")
        end_date_ts = end_date.replace("-", "")
        
        # 标准化股票代码（移除后缀）
        code = stock_code.strip().upper()
        if code.endswith(".SZ") or code.endswith(".SH"):
            code = code[:-3]
        code = code.zfill(6)
        
        # 调用 data-service API
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{data_service_url}/api/tushare/daily",
                json={
                    "codes": [code],
                    "start_date": start_date_ts,
                    "end_date": end_date_ts
                }
            )
            response.raise_for_status()
            
            # 解析响应
            try:
                data = response.json()
            except Exception as json_err:
                logger.error(f"解析响应 JSON 失败: {json_err}, 响应内容: {response.text[:500]}")
                raise ValueError(f"data-service 返回无效响应: {json_err}")
            
            # 检查响应格式
            if not isinstance(data, dict):
                logger.error(f"响应格式错误，期望字典，实际: {type(data)}, 内容: {str(data)[:200]}")
                raise ValueError(f"data-service 返回格式错误: 期望字典，实际 {type(data).__name__}")
            
            # data-service 使用统一响应格式: {code, message, data}
            # 实际数据在 data.data 中
            if "data" in data and isinstance(data["data"], dict):
                result_data = data["data"]
            else:
                result_data = data
            
            if not result_data.get("data"):
                failed = result_data.get("failed_codes", [])
                if failed:
                    raise ValueError(f"未获取到数据: {stock_code}，失败代码: {failed}")
                raise ValueError(f"未获取到数据: {stock_code}")
            
            # 转换为 DataFrame
            records = []
            for item in result_data["data"]:
                trade_date = datetime.strptime(item["trade_date"], "%Y%m%d").date()
                records.append({
                    "date": trade_date,
                    "open": float(item["open"]),
                    "high": float(item["high"]),
                    "low": float(item["low"]),
                    "close": float(item["close"]),
                    "volume": int(item["vol"])
                })
            
            df = pd.DataFrame(records)
            df.set_index("date", inplace=True)
            df.sort_index(inplace=True)
            
            logger.info(f"从 data-service 加载数据成功: {stock_code}, {len(df)} 条")
            return df
            
    except Exception as e:
        logger.warning(f"从 data-service 加载数据失败: {e}，尝试直接调用 Tushare")
        # 回退到直接调用 Tushare（需要配置 token 和安装 tushare 包）
        try:
            return _load_from_tushare_direct(stock_code, start_date, end_date)
        except ImportError:
            raise ValueError(
                "无法加载行情数据：\n"
                "1. 请确保 data-service 服务运行在 http://localhost:8001\n"
                "2. 或者安装 tushare 包：pip install tushare\n"
                "3. 并在配置中设置 TUSHARE_TOKEN 环境变量"
            )


def _load_from_tushare_direct(
    stock_code: str,
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """直接调用 Tushare API（需要配置 token）"""
    try:
        import tushare as ts
        
        # 获取 Tushare token（从环境变量或配置）
        tushare_token = getattr(settings, "tushare_token", None)
        if not tushare_token:
            raise ValueError("Tushare token 未配置，无法直接调用 Tushare API")
        
        pro = ts.pro_api(tushare_token)
        
        # 标准化代码并添加市场后缀
        code = stock_code.strip().upper()
        if code.endswith(".SZ") or code.endswith(".SH"):
            code = code[:-3]
        code = code.zfill(6)
        
        # 判断市场
        if code[:3] in ["000", "001", "002", "003", "300"]:
            ts_code = code + ".SZ"
        else:
            ts_code = code + ".SH"
        
        # 转换日期格式
        start_date_ts = start_date.replace("-", "")
        end_date_ts = end_date.replace("-", "")
        
        # 获取数据
        df = pro.daily(ts_code=ts_code, start_date=start_date_ts, end_date=end_date_ts)
        
        if df is None or df.empty:
            raise ValueError(f"未获取到数据: {stock_code}")
        
        # 转换为标准格式
        df["trade_date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d")
        df = df.rename(columns={
            "trade_date": "date",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "vol": "volume"
        })
        df = df[["date", "open", "high", "low", "close", "volume"]]
        df.set_index("date", inplace=True)
        df.sort_index(inplace=True)
        
        logger.info(f"从 Tushare 直接加载数据成功: {stock_code}, {len(df)} 条")
        return df
        
    except ImportError as e:
        logger.error(f"Tushare 模块未安装: {e}")
        raise ValueError(
            "无法加载行情数据：Tushare 模块未安装。\n"
            "请运行：pip install tushare\n"
            "或确保 data-service 服务正常运行"
        )
    except Exception as e:
        logger.error(f"从 Tushare 加载数据失败: {e}")
        raise ValueError(f"无法加载行情数据: {e}")


def _load_from_tdengine(
    stock_code: str,
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """
    从 TDengine 加载数据
    
    注意：这是占位实现，实际需要连接 TDengine 数据库
    """
    # TODO: 实现 TDengine 数据加载
    # 示例代码结构：
    # import taos
    # conn = taos.connect(host=settings.tdengine_host, ...)
    # cursor = conn.cursor()
    # cursor.execute(f"SELECT * FROM market_data WHERE code='{stock_code}' ...")
    # data = cursor.fetchall()
    # ...
    
    raise NotImplementedError("TDengine 数据源暂未实现，请使用 tushare")


def normalize_stock_code(code: str) -> str:
    """标准化股票代码为 6 位字符串"""
    code = code.strip().upper()
    if code.endswith(".SZ") or code.endswith(".SH"):
        code = code[:-3]
    return code.zfill(6)
