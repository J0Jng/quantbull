"""数据加载服务 - 统一接口加载行情数据"""
import os
import re
import base64
import logging
from datetime import datetime
from typing import Literal, List, Dict, Optional, Tuple, Any

import pandas as pd
import httpx

from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)


# ==================== TDengine REST 辅助函数 ====================

def _tdengine_rest_request(sql: str, timeout: Optional[float] = None) -> dict:
    """
    通过 REST 接口执行 TDengine SQL 查询
    
    Args:
        sql: 要执行的 SQL 语句
        timeout: 请求超时时间
    
    Returns:
        TDengine REST 响应的 JSON 解析结果
    """
    url = (
        f"{settings.tdengine_rest_scheme}://"
        f"{settings.tdengine_host}:{settings.tdengine_rest_port}"
        f"{settings.tdengine_rest_path}"
    )
    
    # Basic Auth
    auth_str = f"{settings.tdengine_user}:{settings.tdengine_password}"
    auth_bytes = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
    headers = {
        "Authorization": f"Basic {auth_bytes}",
        "Content-Type": "text/plain"
    }
    
    if timeout is None:
        timeout = settings.tdengine_rest_timeout
    
    with httpx.Client(timeout=timeout) as client:
        response = client.post(url, content=sql, headers=headers)
        response.raise_for_status()
        return response.json()


def _parse_tdengine_response(resp: dict) -> Tuple[List[str], List[List[Any]]]:
    """
    解析 TDengine REST 响应，提取列名和数据行
    
    Returns:
        (column_names, data_rows)
    """
    # TDengine REST 响应格式：
    # {"code": 0, "column_meta": [["col", type, len], ...], "data": [[...], ...], "rows": n}
    # 或旧版本：{"status": "succ", "head": [...], "data": [...]}
    
    if resp.get("code") == 0:
        # 新版本格式
        column_meta = resp.get("column_meta", [])
        columns = [meta[0] for meta in column_meta]
        data = resp.get("data", [])
        return columns, data
    elif resp.get("status") == "succ":
        # 旧版本格式
        columns = resp.get("head", [])
        data = resp.get("data", [])
        return columns, data
    else:
        # 错误或未知格式
        return [], []


def _discover_tdengine_table() -> Tuple[Optional[str], Optional[str]]:
    """
    自动探测 TDengine 中的行情数据表
    
    Returns:
        (database_name, table_name) 如果发现合适的表，否则 (None, None)
    """
    target_db = settings.tdengine_database
    
    try:
        # 1. 查询可用数据库
        resp = _tdengine_rest_request("SHOW DATABASES")
        columns, data = _parse_tdengine_response(resp)
        
        if not data:
            logger.warning("TDengine 无可用数据库")
            return None, None
        
        # 找到数据库名所在列索引（通常是第一列 "name"）
        db_col_idx = 0
        if columns:
            for i, col in enumerate(columns):
                if col.lower() == "name":
                    db_col_idx = i
                    break
        
        available_dbs = [row[db_col_idx] for row in data if row[db_col_idx] not in ("information_schema", "performance_schema")]
        
        # 优先使用配置的数据库
        if target_db in available_dbs:
            use_db = target_db
        elif available_dbs:
            use_db = available_dbs[0]
            logger.warning(f"配置的数据库 '{target_db}' 不存在，使用: {use_db}")
        else:
            logger.warning("TDengine 无可用的用户数据库")
            return None, None
        
        # 2. 切换数据库
        _tdengine_rest_request(f"USE {use_db}")
        
        # 3. 获取表列表（优先超级表）
        candidates = []
        
        # 查询超级表
        try:
            resp = _tdengine_rest_request("SHOW STABLES")
            _, stable_data = _parse_tdengine_response(resp)
            for row in stable_data:
                candidates.append(row[0])
        except Exception:
            pass
        
        # 查询普通表
        try:
            resp = _tdengine_rest_request("SHOW TABLES")
            _, table_data = _parse_tdengine_response(resp)
            for row in table_data:
                candidates.append(row[0])
        except Exception:
            pass
        
        if not candidates:
            logger.warning(f"数据库 '{use_db}' 中没有表")
            return use_db, None
        
        # 4. 按优先级匹配表名
        priority_names = [
            "market_daily", "daily_kline", "kline_daily", "daily_quotes",
            "market_data", "kline", "bar", "quotes"
        ]
        
        candidates_lower = {c.lower(): c for c in candidates}
        
        for name in priority_names:
            if name in candidates_lower:
                return use_db, candidates_lower[name]
        
        # 无匹配，返回第一个（可能不是行情表）
        logger.warning(f"未匹配到预期行情表名，候选表: {candidates[:10]}")
        return use_db, None
        
    except Exception as e:
        logger.warning(f"探测 TDengine 表失败: {e}")
        return None, None


def _get_tdengine_table_columns(db: str, table: str) -> Dict[str, str]:
    """
    获取表的列名和类型映射
    
    Returns:
        {column_name_lower: column_type}
    """
    try:
        _tdengine_rest_request(f"USE {db}")
        resp = _tdengine_rest_request(f"DESCRIBE {table}")
        columns, data = _parse_tdengine_response(resp)
        
        # DESCRIBE 返回：field, type, length, note
        col_map = {}
        for row in data:
            col_name = row[0].lower()
            col_type = row[1].upper() if len(row) > 1 else "UNKNOWN"
            col_map[col_name] = col_type
        
        return col_map
        
    except Exception as e:
        logger.warning(f"获取表结构失败: {e}")
        return {}


def _resolve_tdengine_column(
    col_map: Dict[str, str],
    priority_names: List[str],
    env_var: str
) -> Optional[str]:
    """
    根据优先级列表和环境变量解析列名
    
    Args:
        col_map: 列名->类型映射（小写键）
        priority_names: 按优先级排序的候选列名
        env_var: 环境变量名（用于覆盖）
    
    Returns:
        匹配的列名（原始大小写），或 None
    """
    # 环境变量覆盖
    env_val = os.environ.get(env_var, "").strip().lower()
    if env_val and env_val in col_map:
        return env_val
    
    for name in priority_names:
        if name.lower() in col_map:
            return name.lower()
    
    return None


def normalize_stock_code(code: str) -> str:
    """标准化股票代码为 6 位字符串"""
    code = code.strip().upper()
    if code.endswith(".SZ") or code.endswith(".SH"):
        code = code[:-3]
    return code.zfill(6)


def resolve_universe(
    universe_mode: Literal["manual", "stock_pool", "stock_etf_pool"],
    universe_params: dict,
    symbols: Optional[List[str]] = None
) -> tuple[List[str], Dict[str, str]]:
    """
    解析股票池，返回标的列表和类型映射
    
    Args:
        universe_mode: 股票池模式 (manual / stock_pool / stock_etf_pool)
        universe_params: 股票池参数 (limit, min_turnover, etf_limit 等)
        symbols: 手动指定的标的列表
    
    Returns:
        (标准化后的标的代码列表, symbol_type_map: {code: "stock"|"etf"})
    """
    symbol_type_map: Dict[str, str] = {}

    request_timeout = float(os.getenv("DATA_SERVICE_TIMEOUT", "120"))
    
    if universe_mode == "manual":
        if not symbols:
            raise ValueError("manual 模式下必须提供 symbols")
        codes = [normalize_stock_code(s) for s in symbols]
        # 默认当作股票
        for c in codes:
            symbol_type_map[c] = "stock"
        return codes, symbol_type_map
    
    elif universe_mode == "stock_pool":
        # 调用 data-service GET /api/stock/list 获取候选池
        try:
            data_service_url = getattr(settings, "data_service_url")
            limit = universe_params.get("limit", 100)
            min_turnover = universe_params.get("min_turnover", 0)
            
            with httpx.Client(timeout=request_timeout) as client:
                response = client.get(
                    f"{data_service_url}/api/stock/list",
                    params={"limit": limit, "min_turnover": min_turnover}
                )
                response.raise_for_status()
                data = response.json()
                
                # 解析响应：data-service 返回 {code, message, data: [...]}
                if "data" in data and isinstance(data["data"], list):
                    stock_list = data["data"]
                elif isinstance(data, list):
                    stock_list = data
                else:
                    stock_list = []
                
                codes = []
                for item in stock_list:
                    symbol = item.get("symbol") or item.get("code")
                    if symbol:
                        normalized = normalize_stock_code(symbol)
                        codes.append(normalized)
                        symbol_type_map[normalized] = "stock"
                
                if not codes:
                    logger.warning("stock_pool 模式未获取到股票列表，请检查 data-service")
                else:
                    logger.info(f"从 stock_pool 获取 {len(codes)} 只股票")
                
                return codes, symbol_type_map
                
        except Exception as e:
            logger.error(f"获取股票池失败: {e}")
            raise ValueError(f"获取股票池失败: {e}")
    
    elif universe_mode == "stock_etf_pool":
        # 同时获取股票池和ETF池
        try:
            data_service_url = getattr(settings, "data_service_url")
            stock_limit = universe_params.get("stock_limit", universe_params.get("limit", 100))
            etf_limit = universe_params.get("etf_limit", 30)
            min_turnover = universe_params.get("min_turnover", 0)
            
            codes = []
            
            # 使用更长的超时时间和重试机制
            pool_timeout = float(os.getenv("DATA_SERVICE_POOL_TIMEOUT", "300"))  # 5分钟
            max_retries = int(os.getenv("DATA_SERVICE_MAX_RETRIES", "3"))
            
            def fetch_with_retry(url: str, params: dict, name: str) -> list:
                """带重试的请求"""
                for attempt in range(max_retries):
                    try:
                        with httpx.Client(timeout=pool_timeout) as client:
                            response = client.get(url, params=params)
                            response.raise_for_status()
                            data = response.json()
                            
                            if "data" in data and isinstance(data["data"], list):
                                return data["data"]
                            elif isinstance(data, list):
                                return data
                            return []
                    except Exception as e:
                        logger.warning(f"获取{name}失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                        if attempt < max_retries - 1:
                            import time
                            time.sleep(2 ** attempt)  # 指数退避
                return []
            
            # 获取股票池
            stock_list = fetch_with_retry(
                f"{data_service_url}/api/stock/list",
                {"limit": stock_limit, "min_turnover": min_turnover},
                "股票池"
            )
            for item in stock_list:
                symbol = item.get("symbol") or item.get("code")
                if symbol:
                    normalized = normalize_stock_code(symbol)
                    codes.append(normalized)
                    symbol_type_map[normalized] = "stock"
            logger.info(f"从 stock_pool 获取 {len([c for c in codes if symbol_type_map.get(c) == 'stock'])} 只股票")
            
            # 获取ETF池
            etf_list = fetch_with_retry(
                f"{data_service_url}/api/etf/list",
                {"limit": etf_limit},
                "ETF池"
            )
            for item in etf_list:
                symbol = item.get("symbol") or item.get("code") or item.get("ts_code", "")[:6]
                if symbol:
                    normalized = normalize_stock_code(symbol)
                    if normalized not in symbol_type_map:  # 避免重复
                        codes.append(normalized)
                        symbol_type_map[normalized] = "etf"
            logger.info(f"从 etf_pool 获取 {len([c for c in codes if symbol_type_map.get(c) == 'etf'])} 只ETF")
            
            # 如果至少有股票数据，即使 ETF 失败也继续
            if not codes:
                raise ValueError("stock_etf_pool 模式未获取到任何标的（股票和ETF均为空）")
            
            return codes, symbol_type_map
                
        except Exception as e:
            logger.error(f"获取 stock_etf_pool 失败: {e}")
            raise ValueError(f"获取 stock_etf_pool 失败: {e}")
    
    else:
        raise ValueError(f"不支持的 universe_mode: {universe_mode}")


def load_market_data_multi(
    symbols: List[str],
    start_date: str,
    end_date: str,
    source: Literal["tdengine", "tushare"] = "tushare",
    symbol_type_map: Optional[Dict[str, str]] = None,
) -> Dict[str, pd.DataFrame]:
    """
    批量加载多标的行情数据
    
    Args:
        symbols: 标的代码列表
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        source: 数据源
    
    Returns:
        {symbol: DataFrame} 字典，只包含有数据的标的
    """
    if source != "tushare":
        raise ValueError(f"load_market_data_multi 暂只支持 tushare 数据源")
    
    # 标准化代码
    normalized_symbols = [normalize_stock_code(s) for s in symbols]
    
    try:
        data_service_url = getattr(settings, "data_service_url")
        start_date_ts = start_date.replace("-", "")
        end_date_ts = end_date.replace("-", "")

        # data-service 内部逐只代码调用 Tushare，单次 codes 过大容易超时。
        # 默认用较小 batch，并允许用环境变量覆盖。
        batch_size = int(os.getenv("DATA_SERVICE_BATCH_SIZE", "20"))
        batch_size = max(1, min(100, batch_size))
        request_timeout = float(os.getenv("DATA_SERVICE_TIMEOUT", "120"))
        
        def _iter_chunks(values: List[str], chunk_size: int) -> List[List[str]]:
            return [values[i : i + chunk_size] for i in range(0, len(values), chunk_size)]

        def _extract_payload(response_json: object) -> tuple[list, list]:
            if not isinstance(response_json, dict):
                return [], []
            # 兼容两种格式：
            # 1) 直接返回 {data: [...], failed_codes: [...], success_codes: [...]}
            # 2) 统一 envelope {code, message, data: {...}}
            payload = response_json
            if "data" in payload and isinstance(payload.get("data"), dict):
                payload = payload["data"]
            items = payload.get("data", []) if isinstance(payload, dict) else []
            failed = payload.get("failed_codes", []) if isinstance(payload, dict) else []
            return items or [], failed or []

        def _fetch_endpoint(endpoint: str, codes: List[str]) -> tuple[list, list]:
            all_items: list = []
            all_failed: list = []
            if not codes:
                return all_items, all_failed
            with httpx.Client(timeout=request_timeout) as client:
                for chunk in _iter_chunks(codes, batch_size):
                    response = client.post(
                        f"{data_service_url}{endpoint}",
                        json={
                            "codes": chunk,
                            "start_date": start_date_ts,
                            "end_date": end_date_ts,
                        },
                    )
                    response.raise_for_status()
                    items, failed = _extract_payload(response.json())
                    all_items.extend(items)
                    all_failed.extend(failed)
            return all_items, list(dict.fromkeys(all_failed))

        # 分流：ETF 走 fund_daily，股票走 daily（避免 ETF 获取失败 & 便于后续扩展）
        stock_codes: List[str] = []
        etf_codes: List[str] = []
        if symbol_type_map:
            for code in normalized_symbols:
                if symbol_type_map.get(code) == "etf":
                    etf_codes.append(code)
                else:
                    stock_codes.append(code)
        else:
            stock_codes = normalized_symbols

        stock_items, stock_failed = _fetch_endpoint("/api/tushare/daily", stock_codes)
        etf_items, etf_failed = _fetch_endpoint("/api/tushare/fund_daily", etf_codes)

        items = stock_items + etf_items
        failed_codes = list(dict.fromkeys(stock_failed + etf_failed))

        if failed_codes:
            logger.warning(f"部分标的数据获取失败: {failed_codes}")
            
        # 按 code 分组
        grouped: Dict[str, List[dict]] = {}
        for item in items:
            code = item.get("code") if isinstance(item, dict) else None
            if code:
                if code not in grouped:
                    grouped[code] = []
                grouped[code].append(item)
            
        # 转换为 DataFrame
        result: Dict[str, pd.DataFrame] = {}
        for code, records in grouped.items():
            df_records = []
            for rec in records:
                trade_date = datetime.strptime(rec["trade_date"], "%Y%m%d").date()
                df_records.append({
                    "date": trade_date,
                    "open": float(rec["open"]),
                    "high": float(rec["high"]),
                    "low": float(rec["low"]),
                    "close": float(rec["close"]),
                    "volume": int(rec["vol"]),
                })

            df = pd.DataFrame(df_records)
            df.set_index("date", inplace=True)
            df.sort_index(inplace=True)
            result[code] = df

        # 记录缺失的标的
        missing = set(normalized_symbols) - set(result.keys())
        if missing:
            logger.warning(f"以下标的无数据: {list(missing)}")

        logger.info(f"批量加载数据成功: {len(result)}/{len(normalized_symbols)} 只标的有数据")
        return result
            
    except Exception as e:
        logger.error(f"批量加载数据失败: {e}")
        raise ValueError(f"批量加载数据失败: {e}")


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
    从 TDengine 加载行情数据
    
    支持自动探测表名和字段映射，也可通过环境变量覆盖：
    - TDENGINE_KLINE_TABLE: 指定行情表名
    - TDENGINE_TIME_COL: 时间列名
    - TDENGINE_CODE_COL: 股票代码列名
    - TDENGINE_OPEN_COL / HIGH_COL / LOW_COL / CLOSE_COL / VOLUME_COL: OHLCV列名
    
    Args:
        stock_code: 股票代码（如：000001）
        start_date: 开始日期（YYYY-MM-DD）
        end_date: 结束日期（YYYY-MM-DD）
    
    Returns:
        DataFrame with index=date, columns=[open,high,low,close,volume], 按日期升序
        空数据返回空 DataFrame
    """
    empty_df = pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    empty_df.index.name = "date"
    
    # 1. 标准化股票代码（必须为6位数字）
    code = stock_code.strip().upper()
    if code.endswith(".SZ") or code.endswith(".SH"):
        code = code[:-3]
    code = code.zfill(6)
    
    # 严格校验：必须是6位数字
    if not re.match(r"^\d{6}$", code):
        logger.warning(f"TDengine: 无效股票代码 '{stock_code}'，跳过")
        return empty_df
    
    # 2. 校验日期格式
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(date_pattern, start_date) or not re.match(date_pattern, end_date):
        logger.warning(f"TDengine: 日期格式错误 start={start_date}, end={end_date}，期望 YYYY-MM-DD")
        return empty_df
    
    try:
        # 3. 确定表名
        env_table = os.environ.get("TDENGINE_KLINE_TABLE", "").strip()
        
        if env_table:
            # 环境变量指定表名
            use_db = settings.tdengine_database
            use_table = env_table
            logger.debug(f"TDengine: 使用环境变量指定的表 {use_db}.{use_table}")
        else:
            # 自动探测
            use_db, use_table = _discover_tdengine_table()
            if not use_table:
                logger.warning(
                    "TDengine: 未找到行情数据表。请设置环境变量 TDENGINE_KLINE_TABLE 指定表名。"
                    f" 候选数据库: {use_db or '无'}"
                )
                return empty_df
        
        # 4. 获取表结构
        col_map = _get_tdengine_table_columns(use_db, use_table)  # type: ignore[arg-type]
        if not col_map:
            logger.warning(f"TDengine: 无法获取表 {use_db}.{use_table} 的结构")
            return empty_df
        
        # 5. 解析字段映射
        time_col = _resolve_tdengine_column(
            col_map, ["ts", "time", "datetime", "trade_date"], "TDENGINE_TIME_COL"
        )
        code_col = _resolve_tdengine_column(
            col_map, ["code", "symbol", "ts_code", "stock_code"], "TDENGINE_CODE_COL"
        )
        open_col = _resolve_tdengine_column(
            col_map, ["open", "open_price"], "TDENGINE_OPEN_COL"
        )
        high_col = _resolve_tdengine_column(
            col_map, ["high", "high_price"], "TDENGINE_HIGH_COL"
        )
        low_col = _resolve_tdengine_column(
            col_map, ["low", "low_price"], "TDENGINE_LOW_COL"
        )
        close_col = _resolve_tdengine_column(
            col_map, ["close", "close_price"], "TDENGINE_CLOSE_COL"
        )
        volume_col = _resolve_tdengine_column(
            col_map, ["volume", "vol"], "TDENGINE_VOLUME_COL"
        )
        
        # 检查必需字段
        missing_fields = []
        if not time_col:
            missing_fields.append("时间列(ts/time/datetime/trade_date)")
        if not open_col:
            missing_fields.append("open")
        if not high_col:
            missing_fields.append("high")
        if not low_col:
            missing_fields.append("low")
        if not close_col:
            missing_fields.append("close")
        if not volume_col:
            missing_fields.append("volume/vol")
        
        if missing_fields:
            logger.warning(
                f"TDengine: 表 {use_table} 缺少必需字段: {missing_fields}。"
                f" 当前列: {list(col_map.keys())}。"
                " 可通过 TDENGINE_*_COL 环境变量指定列名。"
            )
            return empty_df
        
        # 6. 构建查询 SQL
        time_type = col_map.get(time_col or "ts", "TIMESTAMP").upper()
        
        # 根据时间列类型格式化时间条件
        if "TIMESTAMP" in time_type:
            start_ts = f"'{start_date} 00:00:00'"
            end_ts = f"'{end_date} 23:59:59'"
        else:
            # DATE 或字符串类型
            start_ts = f"'{start_date}'"
            end_ts = f"'{end_date}'"
        
        # 构建 WHERE 子句
        where_clauses = [f"{time_col} >= {start_ts}", f"{time_col} <= {end_ts}"]
        
        # 代码过滤（如果有代码列）
        if code_col:
            # 尝试多种代码格式匹配
            code_with_sz = f"{code}.SZ"
            code_with_sh = f"{code}.SH"
            where_clauses.append(
                f"({code_col} = '{code}' OR {code_col} = '{code_with_sz}' OR {code_col} = '{code_with_sh}')"
            )
        else:
            # 无代码列，可能是子表模式，在日志说明
            logger.info(f"TDengine: 表 {use_table} 无代码列，假设为单标的子表或全量查询")
        
        where_sql = " AND ".join(where_clauses)
        
        sql = (
            f"SELECT {time_col}, {open_col}, {high_col}, {low_col}, {close_col}, {volume_col} "
            f"FROM {use_db}.{use_table} "
            f"WHERE {where_sql} "
            f"ORDER BY {time_col} ASC"
        )
        
        logger.debug(f"TDengine SQL: {sql}")
        
        # 7. 执行查询
        resp = _tdengine_rest_request(sql, timeout=settings.tdengine_rest_timeout)
        
        # 解析响应
        if resp.get("code") != 0 and resp.get("status") != "succ":
            desc = resp.get("desc") or resp.get("message") or str(resp)[:300]
            logger.warning(f"TDengine 查询失败: {desc}")
            return empty_df
        
        _, data = _parse_tdengine_response(resp)
        
        if not data:
            logger.info(f"TDengine: {stock_code} 在 {start_date} ~ {end_date} 无数据")
            return empty_df
        
        # 8. 转换为 DataFrame
        records = []
        for row in data:
            try:
                # 解析时间
                ts_val = row[0]
                if isinstance(ts_val, str):
                    # 尝试多种格式
                    for fmt in ["%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y%m%d"]:
                        try:
                            dt = datetime.strptime(ts_val.split(".")[0] if "." in ts_val else ts_val, fmt.split(".")[0])
                            break
                        except ValueError:
                            continue
                    else:
                        continue
                elif isinstance(ts_val, (int, float)):
                    # 毫秒时间戳
                    if ts_val > 1e12:
                        dt = datetime.fromtimestamp(ts_val / 1000)
                    else:
                        dt = datetime.fromtimestamp(ts_val)
                else:
                    dt = ts_val
                
                records.append({
                    "date": dt.date() if hasattr(dt, "date") else dt,
                    "open": float(row[1]),
                    "high": float(row[2]),
                    "low": float(row[3]),
                    "close": float(row[4]),
                    "volume": int(float(row[5]))
                })
            except (ValueError, TypeError, IndexError) as e:
                logger.debug(f"TDengine: 跳过无效行 {row}: {e}")
                continue
        
        if not records:
            logger.info(f"TDengine: {stock_code} 解析后无有效数据")
            return empty_df
        
        df = pd.DataFrame(records)
        df.set_index("date", inplace=True)
        df.sort_index(inplace=True)
        
        # 去除重复日期（保留最后一条）
        df = df[~df.index.duplicated(keep="last")]
        
        logger.info(f"TDengine: 加载 {stock_code} 成功，{len(df)} 条记录")
        return df
        
    except httpx.ConnectError as e:
        logger.warning(f"TDengine: 连接失败 ({settings.tdengine_host}:{settings.tdengine_rest_port}): {e}")
        return empty_df
    except httpx.HTTPStatusError as e:
        logger.warning(f"TDengine: HTTP 错误 {e.response.status_code}: {e.response.text[:300]}")
        return empty_df
    except Exception as e:
        logger.warning(f"TDengine: 加载数据异常: {e}")
        return empty_df
