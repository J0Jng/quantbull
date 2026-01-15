# 股票数据页面"暂无数据"问题排查指南

## 问题现象

页面显示：
- ✅ 大盘指数有数据
- ❌ 个股行情显示"暂无数据"
- ❌ 热门板块显示"暂无数据"
- ❌ 涨跌分布显示"统计数据加载中..."

## 根本原因

**数据库中没有股票数据**（首次使用或数据过期）

## 解决方案

### 方案1：自动刷新（已实现）

**前端已自动处理**：页面加载时会自动检测，如果数据库无数据则自动触发后台刷新。

**无需手动操作**，只需：
1. 刷新页面（F5）
2. 等待 5-10 秒（后台拉取数据）
3. 数据自动显示

### 方案2：手动刷新按钮

点击页面上的 **"刷新数据"** 按钮，会强制从后台拉取最新数据。

### 方案3：直接调用接口（开发测试）

```bash
# 触发数据刷新
curl "http://localhost:8000/api/stock/snapshot?refresh=true&limit=200"
```

## 数据刷新流程

当 `refresh=true` 时，后端会：

1. **拉取股票基础信息**（Tushare daily 接口）
   - 获取当日全市场股票数据
   - 包含：代码、名称、行业、价格、涨跌幅、换手率
   - 落库到 `stock_basic` 表

2. **拉取实时行情**（Tushare get_realtime_quotes 接口）
   - 批量获取股票实时数据
   - 包含：价格、涨跌幅、成交额、更新时间
   - 落库到 `realtime_quotes` 表

3. **返回聚合结果**
   - DB 侧 JOIN 两个表
   - 优先使用实时数据
   - 返回完整字段

## 预期耗时

| 操作 | 耗时 | 说明 |
|------|------|------|
| 首次刷新（200只股票） | 5-10秒 | 需要调用 Tushare API |
| 后续查询 | <100ms | 直接从数据库读取 |
| 手动刷新 | 5-10秒 | 重新拉取最新数据 |

## 验证数据是否存在

### 检查数据库

```sql
-- 检查股票基础信息表
SELECT COUNT(*), MAX(trade_date) FROM stock_basic;

-- 检查实时行情表
SELECT COUNT(*), MAX(update_time) FROM realtime_quotes;

-- 检查最新数据
SELECT * FROM stock_basic 
WHERE trade_date = (SELECT MAX(trade_date) FROM stock_basic)
LIMIT 10;
```

### 检查后端日志

```bash
# 查看 data-service 日志
docker-compose logs -f data-service

# 关键日志：
# - "触发数据刷新"
# - "开始获取 YYYYMMDD 的股票日行情"
# - "生成 N 条股票数据"
# - "成功保存 N 条股票数据到数据库"
# - "刷新了 N 条实时行情数据"
# - "返回 N 条聚合快照数据"
```

### 检查前端控制台

打开浏览器开发者工具（F12），查看 Console：

```javascript
// 关键日志：
// - "数据库无数据，触发后台刷新..."
// - Network 面板中看到 /api/stock/snapshot?refresh=true
```

## 常见错误及解决

### 错误1：Tushare Token 未配置

**现象**：
```
ERROR: TUSHARE_TOKEN environment variable is not set
```

**解决**：
```bash
# 在 .env 文件中添加
TUSHARE_TOKEN=your_token_here

# 或在 docker-compose.yml 中配置
environment:
  - TUSHARE_TOKEN=your_token_here

# 重启服务
docker-compose restart data-service
```

### 错误2：Tushare API 限流

**现象**：
```
ERROR: 接口限流，请稍后再试
```

**解决**：
- 等待 1 分钟后重试
- Tushare 免费版有调用频率限制
- 升级到付费版可提高限额

### 错误3：数据库连接失败

**现象**：
```
ERROR: could not connect to server: Connection refused
```

**解决**：
```bash
# 检查 PostgreSQL 是否运行
docker-compose ps

# 重启数据库
docker-compose restart postgres

# 检查连接配置
docker-compose logs postgres
```

### 错误4：交易日判断错误

**现象**：
- 周末/节假日无数据

**原因**：
- 非交易日 Tushare 返回空数据

**解决**：
- 后端会自动查找最近交易日（回溯 10 天）
- 如果仍无数据，说明 API 异常
- 检查 Tushare 服务状态

## 数据更新策略

### 建议配置

**开发环境**：
- 手动刷新（点击按钮）
- 或首次加载自动刷新

**生产环境**：
1. **定时任务**（推荐）
   ```bash
   # 每日盘后更新基础数据（15:30）
   30 15 * * 1-5 curl "http://localhost:8000/api/stock/snapshot?refresh=true"
   
   # 或使用 Celery 定时任务
   ```

2. **盘中实时更新**
   ```bash
   # 每分钟更新实时行情（交易时段 9:30-15:00）
   */1 9-15 * * 1-5 curl "http://localhost:8000/api/quotes/realtime" -X POST -d '{"codes": [...]}'
   ```

3. **缓存策略**
   - 页面缓存 5 分钟
   - 避免频繁请求后端

## 性能优化建议

### 如果数据加载慢

1. **添加数据库索引**（已存在）
   ```sql
   CREATE INDEX idx_stock_trade_date ON stock_basic(trade_date);
   CREATE INDEX idx_stock_symbol ON stock_basic(symbol);
   CREATE INDEX idx_realtime_update_time ON realtime_quotes(update_time);
   ```

2. **使用物化表**
   ```sql
   -- 创建物化表
   CREATE MATERIALIZED VIEW stock_snapshot_mv AS
   SELECT ... FROM stock_basic LEFT JOIN realtime_quotes ...;
   
   -- 定时刷新（每分钟）
   REFRESH MATERIALIZED VIEW stock_snapshot_mv;
   ```

3. **增加 Redis 缓存**
   - 缓存热门股票数据
   - TTL 设置为 1 分钟

## 快速诊断命令

```bash
# 1. 检查服务状态
docker-compose ps

# 2. 检查数据库数据量
docker-compose exec postgres psql -U postgres -d quantbull -c "SELECT COUNT(*) FROM stock_basic;"

# 3. 触发数据刷新
curl "http://localhost:8000/api/stock/snapshot?refresh=true&limit=10"

# 4. 查看后端日志
docker-compose logs -f data-service | grep -E "刷新|股票|错误"

# 5. 检查前端页面
# 打开 http://localhost:3000/stock-data
# F12 打开控制台查看错误
```

## 预期结果

数据刷新成功后，页面应显示：

- ✅ **个股行情**：显示 100-200 只股票
  - 代码、名称、行业、价格、涨跌幅、换手率、成交额、更新时间
  - 无"未知/--"字段

- ✅ **热门板块**：显示前 5 个行业
  - 行业名称、平均涨跌幅、领涨股

- ✅ **涨跌分布**：显示市场统计
  - 涨停、上涨、平盘、下跌、跌停的家数和比例

## 联系支持

如果以上方法都无法解决，请提供：

1. 浏览器控制台截图（F12 → Console）
2. Network 面板截图（F12 → Network）
3. 后端日志：`docker-compose logs data-service`
4. 数据库查询结果：`SELECT COUNT(*) FROM stock_basic;`

---

**最后更新**: 2026-01-15
