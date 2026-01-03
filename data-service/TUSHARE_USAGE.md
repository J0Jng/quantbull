# Tushare 实时行情服务使用指南

## 概述

data-service 已经从东方财富爬虫迁移到 Tushare API，提供更稳定可靠的实时行情数据。

**使用的接口**: `ts.get_realtime_quotes()` - Tushare 旧版免费实时行情接口，无需积分，注册即可使用。

## 前置条件

### 1. 注册 Tushare 账号

访问 [https://tushare.pro/register](https://tushare.pro/register) 注册账号并获取 API Token。

### 2. 安装依赖

```bash
pip install tushare>=1.2.89
```

依赖已包含在 `requirements.txt` 中。

## 配置

### 环境变量配置（推荐）

在运行服务前设置环境变量：

```bash
# Linux/Mac
export TUSHARE_TOKEN='your_token_here'

# Windows PowerShell
$env:TUSHARE_TOKEN='your_token_here'

# Windows CMD
set TUSHARE_TOKEN=your_token_here
```

### .env 文件配置

在 data-service 目录创建 `.env` 文件：

```ini
TUSHARE_TOKEN=your_token_here
```

### Docker 配置

在 `docker-compose.yml` 中添加环境变量：

```yaml
services:
  data-service:
    environment:
      - TUSHARE_TOKEN=${TUSHARE_TOKEN}
```

## 使用示例

### 1. 直接使用服务类

```python
from core.config import settings
from services.eastmoney_spider import TushareQuoteService

# 验证 token
settings.validate_tushare_token()

# 创建服务实例
service = TushareQuoteService(token=settings.tushare_token)

# 批量获取行情
stock_codes = ['000001', '600000', '159915']  # 6 位代码
success_items, failed_codes = service.fetch_quotes(stock_codes)

# 输出结果
for item in success_items:
    print(f"{item.code} {item.name}: ¥{item.price:.2f} ({item.pct_change:+.2f}%)")
    print(f"  成交额: ¥{item.turnover:,.0f}")

if failed_codes:
    print(f"失败: {failed_codes}")
```

### 2. HTTP API 调用

```bash
curl -X POST "http://localhost:8000/quotes/realtime" \
  -H "Content-Type: application/json" \
  -d '{
    "codes": ["000001", "600000", "159915"]
  }'
```

响应示例：

```json
{
  "data": [
    {
      "code": "000001",
      "name": "平安银行",
      "price": 12.35,
      "pct_change": 1.23,
      "turnover": 523456789.0,
      "update_time": "2026-01-02T10:30:00"
    }
  ],
  "success_codes": ["000001", "600000"],
  "failed_codes": ["159915"]
}
```

## 数据字段说明

| 字段 | 类型 | 单位 | 说明 |
|------|------|------|------|
| code | string | - | 6 位股票代码（如 "000001"） |
| name | string | - | 股票名称 |
| price | float | 元 | 最新价 |
| pct_change | float | % | 涨跌幅（如 2.5 表示 +2.5%） |
| turnover | float | 元 | 成交额（从万元转换） |
| update_time | datetime | - | 数据更新时间 |

**注意**: `get_realtime_quotes` 接口返回的成交额单位为万元，代码自动转换为元。

## 支持的股票代码

服务自动识别交易所并转换格式：

| 前缀 | 交易所 | 示例 | Tushare 格式 |
|------|--------|------|--------------|
| 000/001/002/003 | 深圳主板/中小板 | 000001 | 000001.SZ |
| 300/301 | 深圳创业板 | 300750 | 300750.SZ |
| 600/601/603/605 | 上海主板 | 600000 | 600000.SH |
| 688 | 上海科创板 | 688001 | 688001.SH |
| 15/16 | 深圳 ETF | 159915 | 159915.SZ |
| 51/56 | 上海 ETF | 512100 | 512100.SH |

## 错误处理

### Token 未配置

```
ValueError: TUSHARE_TOKEN 未配置！请通过以下方式之一设置：
1. 环境变量：export TUSHARE_TOKEN='your_token_here'
2. .env 文件：TUSHARE_TOKEN=your_token_here
获取 Token：https://tushare.pro/register
```

**解决方案**：按提示设置环境变量或 .env 文件。

### API 调用失败

如果单个或部分股票获取失败，会在 `failed_codes` 中返回，不会影响其他股票。

查看日志获取详细错误信息：

```python
import logging
logging.basicConfig(level=logging.INFO)
```

### 限流问题

Tushare 免费版有调用频率限制（120 次/分钟）。如遇限流：

1. 升级到 Tushare Pro 积分会员
2. 添加请求间隔（如需大量请求）
3. 使用批量接口（已实现，一次请求支持多个代码）

## 迁移说明

从东方财富爬虫迁移到 Tushare 的主要变化：

1. **类名变更**：`EastMoneySpider` → `TushareQuoteService`
2. **需要 Token**：必须配置 `TUSHARE_TOKEN` 环境变量
3. **更稳定**：官方 API 支持，无需担心网页结构变化
4. **批量查询**：一次 API 调用获取多支股票，更高效
5. **数据准确性**：Tushare 数据更准确且有历史回测支持

## 常见问题

**Q: 如何获取 Tushare Token？**

A: 访问 https://tushare.pro/register 注册并在"我的 Token"页面获取。

**Q: 免费版有什么限制？**

A: 使用的 `get_realtime_quotes` 是免费接口，无调用频率限制，仅需注册获取 token。

**Q: 是否支持历史数据？**

A: 当前仅支持实时行情，如需历史数据可使用 Tushare Pro 的其他接口（需要积分）。

**Q: 数据延迟多少？**

A: `get_realtime_quotes` 接口提供实时数据，延迟通常在秒级（免费接口）。

## 相关链接

- [Tushare 官网](https://tushare.pro)
- [get_realtime_quotes 文档](https://tushare.pro/document/old/2?doc_id=old_109)
- [Tushare API 文档](https://tushare.pro/document/2)
