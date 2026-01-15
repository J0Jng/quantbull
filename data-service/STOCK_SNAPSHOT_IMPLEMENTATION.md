# 股票数据中心：聚合快照功能实施文档

## 概述

实现了"股票数据中心：个股行情字段补齐 + DB 侧整合"功能，解决前端页面出现"未知/--"字段的问题。

## 核心变更

### 1. 后端改动（data-service）

#### 新增 Schema
**文件**: `schemas/stock.py`

新增两个类：
- `StockSnapshotItem`: 聚合快照数据项，包含所有前端需要的字段
- `StockSnapshotResponse`: 快照列表响应

字段说明：
```python
symbol: str          # 股票代码（6位）
code: str            # 股票代码（兼容字段）
name: str            # 股票名称（不再是"未知"）
industry: str        # 行业（不再是"未知"）
price: float         # 最新价格
latest_price: float  # 最新价格（兼容字段）
pct_change: float    # 涨跌幅
turnover_rate: float # 换手率
turnover: float      # 成交额（元）
update_time: str     # 更新时间（不再是"--"）
```

#### 新增 Service 方法
**文件**: `services/stock_service.py`

新增方法 `StockService.get_stock_snapshot_list()`：

**核心功能**：
1. **数据刷新**（可选）：`refresh=true` 时触发后台数据拉取
   - 调用 `get_stock_list()` 拉取并落库 `stock_basic`
   - 批量获取实时行情并落库 `realtime_quotes`

2. **DB 侧整合查询**：
   - 使用 SQL 窗口函数获取每个股票的最新实时行情
   - LEFT JOIN `stock_basic` 和最新的 `realtime_quotes`
   - 优先使用实时数据，若无实时数据则降级到基础数据

3. **字段降级策略**：
   ```python
   final_name = realtime_name if realtime_name else basic_name
   final_price = realtime_price if realtime_price is not None else basic_price
   final_pct_change = realtime_pct_change if realtime_pct_change is not None else basic_pct_change
   final_turnover = realtime_turnover if realtime_turnover is not None else (basic_amount * 1000)
   ```

4. **排序支持**：
   - `rise`: 按涨跌幅降序
   - `fall`: 按涨跌幅升序
   - `amount`/`volume`: 按成交额降序（默认）

#### 新增路由
**文件**: `routers/stock.py`

新增端点：
```
GET /api/stock/snapshot
```

**查询参数**：
- `date` (可选): 交易日期 YYYY-MM-DD
- `limit` (默认200): 返回数量
- `min_turnover` (默认0): 最小成交额过滤（元）
- `sort` (默认amount): 排序方式
- `refresh` (默认false): 是否触发数据刷新

### 2. 前端改动（frontend/niuniu）

#### 新增 Service 方法
**文件**: `services/marketService.js`

新增方法 `getStockSnapshotList(params)`：
- 调用 `/api/stock/snapshot` 接口
- 一次性获取所有需要的字段

#### 重构 StockDataPage
**文件**: `views/StockDataPage.vue`

**主要变更**：

1. **移除前端 merge 逻辑**：
   - 删除了 `getStockList()` + `getRealtimeQuotes()` 两次调用
   - 改为只调用 `getStockSnapshotList()`

2. **简化数据处理**：
   ```javascript
   // 旧逻辑（已删除）
   const result1 = await getStockList(...)
   const result2 = await getRealtimeQuotes(...)
   // 在浏览器里 merge 两份数据
   
   // 新逻辑
   const result = await getStockSnapshotList(...)
   // 直接使用聚合后的数据
   ```

3. **搜索优化**：
   - 搜索功能也使用快照接口
   - 从聚合结果中查找匹配股票

## 数据流

### 旧架构（已废弃）
```
前端 → /api/stock/list → stock_basic
     ↓
     → /api/quotes/realtime → realtime_quotes
     ↓
   浏览器 merge（存在字段缺失）
```

### 新架构
```
前端 → /api/stock/snapshot
     ↓
   后端 DB JOIN (stock_basic ⟕ realtime_quotes)
     ↓
   返回完整字段（无"未知/--"）
```

## 验收标准

### ✅ 已实现

1. **字段完整性**：
   - 名称、行业、成交额、更新时间不再显示"未知/--"
   - 使用降级策略确保字段有值

2. **请求优化**：
   - 前端只调用一个聚合接口
   - 不再在浏览器端 merge 多个接口

3. **DB 侧整合**：
   - SQL JOIN 在数据库内完成
   - 使用窗口函数获取最新实时行情

4. **代码风格一致**：
   - 复用现有的 `SessionLocal`、`success()` 返回风格
   - 与项目其他服务保持一致

## 使用说明

### 初次使用
如果数据库为空，建议首次调用时加 `refresh=true`：

```bash
GET /api/stock/snapshot?refresh=true&limit=200
```

这会触发后台拉取并落库，然后返回聚合结果。

### 日常使用
正常查询（从数据库读取）：

```bash
GET /api/stock/snapshot?limit=200&sort=amount
```

### 前端调用示例
```javascript
import { getStockSnapshotList } from '@/services/marketService'

// 加载股票数据
const result = await getStockSnapshotList({
  limit: 200,
  sort: 'amount',
  min_turnover: 0
})

if (result.success) {
  const stocks = result.data
  // 直接使用，无需 merge
}
```

## 数据库表依赖

- `stock_basic`: 股票基础信息（symbol, name, industry, turnover_rate 等）
- `realtime_quotes`: 实时行情（code, price, pct_change, turnover, update_time）

两表通过 `stock_basic.symbol = realtime_quotes.code` 关联。

## 性能优化建议

1. **索引优化**（已存在）：
   - `stock_basic`: `idx_stock_trade_date`, `idx_stock_symbol`
   - `realtime_quotes`: `idx_update_time`

2. **缓存策略**（可选扩展）：
   - 在 service 层增加 5 分钟内存缓存
   - 避免短时间内重复 DB 查询

3. **物化表**（可选扩展）：
   - 创建 `stock_snapshot` 物化表
   - 定时刷新（如每分钟）
   - 查询直接读物化表（性能最佳）

## 故障排查

### 问题：返回数据为空
**原因**：数据库中无股票数据

**解决**：
```bash
# 带 refresh 参数触发数据拉取
curl "http://localhost:8000/api/stock/snapshot?refresh=true"
```

### 问题：实时行情字段为空
**原因**：`realtime_quotes` 表无数据

**解决**：
1. 确保 Tushare Token 已配置
2. 手动调用 `/api/quotes/realtime` 拉取实时行情
3. 或使用 `refresh=true` 参数

### 问题：名称/行业显示"未知"
**原因**：`stock_basic` 表中对应字段为空

**解决**：
1. 检查 Tushare API 是否返回完整数据
2. 触发 `get_stock_list()` 重新拉取并落库
3. 必要时手动补齐数据库

## 后续优化方向

1. **定时任务**：
   - 每日定时刷新 `stock_basic`（盘后）
   - 每分钟刷新 `realtime_quotes`（盘中）

2. **数据质量监控**：
   - 统计"未知"字段占比
   - 告警机制（低于阈值时触发）

3. **前端缓存**：
   - 在浏览器端缓存 5 分钟
   - 减少不必要的后端请求

4. **分页支持**：
   - 增加 `offset` 参数
   - 支持大数据量场景

## 相关文件清单

### 后端
- `data-service/schemas/stock.py` - 新增 Schema
- `data-service/services/stock_service.py` - 新增 Service 方法
- `data-service/routers/stock.py` - 新增路由
- `data-service/models/stock_basic.py` - 现有模型（无改动）
- `data-service/models/realtime_quote.py` - 现有模型（无改动）

### 前端
- `frontend/niuniu/src/services/marketService.js` - 新增 service 方法
- `frontend/niuniu/src/views/StockDataPage.vue` - 重构数据加载逻辑

---

**实施完成时间**: 2026-01-15
**实施人**: GitHub Copilot
