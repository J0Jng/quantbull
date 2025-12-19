## API 接口

### 1. POST /api/tushare/daily

获取日线行情数据（支持批量查询）

**请求体：**
```json
{
  "codes": ["000001", "600000"],
  "start_date": "20250101",
  "end_date": "20251231"
}
```

**响应：**
```json
{
  "data": [
    {
      "code": "000001",
      "trade_date": "20251213",
      "open": 12.10,
      "high": 12.50,
      "low": 12.00,
      "close": 12.34,
      "vol": 12345678,
      "amount": 123456789.0
    }
  ],
  "success_codes": ["000001", "600000"],
  "failed_codes": []
}
```

**字段说明：**
- `code`: 股票代码（6位，不带 .SZ/.SH）
- `trade_date`: 交易日期（YYYYMMDD）
- `open/high/low/close`: 开盘/最高/最低/收盘价（元）
- `vol`: 成交量（手）
- `amount`: 成交额（元）

**特性：**
- 自动保存到数据库（upsert）
- 单个股票失败不影响整体
- 支持批量查询

### 2. GET /api/tushare/stock_basic

获取股票基础信息

**请求：**
```
GET /api/tushare/stock_basic?exchange=
```

**响应：**
```json
{
  "data": [
    {
      "ts_code": "000001.SZ",
      "symbol": "000001",
      "name": "平安银行",
      "area": "深圳",
      "industry": "银行",
      "list_date": "19910403"
    }
  ]
}
```

### 3. POST /api/tushare/fund_daily

获取 ETF 日线行情

**请求体：**（与 daily 接口相同）
```json
{
  "codes": ["159919", "510300"],
  "start_date": "20250101",
  "end_date": "20251231"
}
```

### 4. POST /api/quotes/realtime

获取沪深 A 股实时行情数据，支持批量查询。

**请求体：**
```json
{
  "codes": ["000001", "600000", "000002"]
}
```

**响应：**
```json
{
  "data": [
    {
      "code": "000001",
      "name": "平安银行",
      "price": 12.34,
      "pct_change": 1.23,
      "turnover": 123456789.0,
      "update_time": "2025-12-13T15:00:00"
    }
  ],
  "success_codes": ["000001", "600000"],
  "failed_codes": ["000002"]
}
```

## 支持的股票代码

- **深圳市场**：000, 001, 002, 003, 300 开头
- **上海市场**：600, 601, 603, 605, 688 开头

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 股票代码（6位） |
| name | string | 股票名称 |
| price | float | 最新价（元） |
| pct_change | float | 涨跌幅（百分比，如 1.23 表示 1.23%） |
| turnover | float | 成交额（元） |
| update_time | datetime | 更新时间（ISO 格式） |

## 数据库

### 表结构：daily_quotes

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键（自增） |
| code | str | 股票代码（索引） |
| trade_date | date | 交易日期（索引） |
| open | float | 开盘价 |
| high | float | 最高价 |
| low | float | 最低价 |
| close | float | 收盘价 |
| vol | int | 成交量（手） |
| amount | float | 成交额（元） |

**约束：**
- 唯一约束：`(code, trade_date)`
- 使用 upsert（存在即更新）

## 数据库

数据会自动保存到 PostgreSQL 数据库的 `realtime_quotes` 表中。

**表结构：**
- `id`: 主键（自增）
- `code`: 股票代码（索引）
- `name`: 股票名称
- `price`: 最新价
- `pct_change`: 涨跌幅
- `turnover`: 成交额
- `update_time`: 更新时间（索引）
- 唯一约束：`(code, update_time)`