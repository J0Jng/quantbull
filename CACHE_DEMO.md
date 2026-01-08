# 历史缓存数据自动使用 - 演示文档

## 功能说明

系统已实现**三层缓存架构**，确保在 API 限制情况下仍能快速响应：

```
请求 → 数据库缓存（持久化，24小时） → 内存缓存（快速，24小时） → Tushare API（实时）
```

## 缓存策略

### 1. 数据库持久化缓存（优先级最高）
- **有效期**: 24小时
- **存储位置**: PostgreSQL 数据库
- **表结构**:
  - `sentiment_score`: 情绪分数
  - `hot_score`: 热点分数
- **优势**: 
  - 重启服务后数据不丢失
  - 多实例可共享
  - 可追溯历史数据

### 2. 内存缓存（优先级次之）
- **有效期**: 24小时（1440分钟）
- **存储位置**: 服务进程内存
- **优势**: 访问速度极快

### 3. API 实时获取（优先级最低）
- 当缓存都失效时才调用
- 获取后自动保存到数据库和内存

## 实际演示

### 当前数据库中的数据

**情绪分数表 (sentiment_score)**:
```
 code  | trade_date | sentiment_score | discussion_volume |       created       
-------+------------+-----------------+-------------------+---------------------
000001 | 20260106   |            0.45 |              8520 | 2026-01-07 13:43:22
000002 | 20260106   |            0.72 |             15680 | 2026-01-07 13:43:22
600000 | 20260106   |            0.38 |              6230 | 2026-01-07 13:43:22
```

**热点分数表 (hot_score)**:
```
 code  | trade_date | hot_score | concept_score | limit_score |   concept_tags    
-------+------------+-----------+---------------+-------------+-------------------
000001 | 20260106   |      0.25 |          0.30 |        0.20 | 金融,银行
000002 | 20260106   |      0.68 |          0.60 |        0.75 | 房地产,深圳国资
600000 | 20260106   |      0.15 |          0.20 |        0.10 | 金融,银行,上海国资
```

## 测试验证

### 测试1: 查询情绪分数（从数据库读取）

**API 请求**:
```bash
curl -X 'POST' \
  'http://localhost:8000/api/fundamentals/sentiment/score' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
  "codes": ["000001", "000002", "600000"],
  "end_date": "2026-01-06"
}'
```

**响应结果** (从数据库直接返回，无需调用 Tushare):
```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "data": [
      {
        "code": "000001",
        "sentiment_score": 0.45,
        "discussion_volume": 8520
      },
      {
        "code": "000002",
        "sentiment_score": 0.72,
        "discussion_volume": 15680
      },
      {
        "code": "600000",
        "sentiment_score": 0.38,
        "discussion_volume": 6230
      }
    ]
  }
}
```

### 测试2: 查询热点分数（从数据库读取）

**API 请求**:
```bash
curl -X 'POST' \
  'http://localhost:8000/api/fundamentals/hot/score' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
  "codes": ["000001", "000002", "600000"]
}'
```

**响应结果**:
```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "data": [
      {
        "code": "000001",
        "hot_score": 0.25
      },
      {
        "code": "000002",
        "hot_score": 0.68
      },
      {
        "code": "600000",
        "hot_score": 0.15
      }
    ]
  }
}
```

## 日志验证

从数据库读取时的日志：
```
INFO | 从数据库加载了 3 条情绪分数数据
INFO | 从数据库加载了 3 条热点分数数据
```

从 API 获取并保存时的日志：
```
INFO | 保存了 3 条情绪分数到数据库（20260106）
INFO | 保存了 3 条热点分数到数据库（20260106）
```

## 缓存失效和更新

### 自动失效
- 24小时后自动失效
- 下次请求会重新从 Tushare 获取

### 手动清除（如需强制更新）

**清除情绪分数缓存**:
```bash
docker exec quantbull_postgres psql -U quantbull -d quantbull_db \
  -c "DELETE FROM sentiment_score WHERE trade_date='20260106';"
```

**清除热点分数缓存**:
```bash
docker exec quantbull_postgres psql -U quantbull -d quantbull_db \
  -c "DELETE FROM hot_score WHERE trade_date='20260106';"
```

**清除特定股票的缓存**:
```bash
docker exec quantbull_postgres psql -U quantbull -d quantbull_db \
  -c "DELETE FROM sentiment_score WHERE code='000001' AND trade_date='20260106';"
```

## 优势总结

✅ **避免 API 限流**: 24小时内重复查询不会调用 Tushare API  
✅ **响应速度快**: 数据库查询 < 50ms，远快于 API 调用  
✅ **数据持久化**: 服务重启后数据不丢失  
✅ **成本节约**: 减少 API 调用次数，节省积分  
✅ **自动管理**: 无需手动维护，自动更新和失效  

## 查询历史数据

### 查看所有缓存的日期
```bash
docker exec quantbull_postgres psql -U quantbull -d quantbull_db \
  -c "SELECT DISTINCT trade_date, COUNT(*) as stock_count FROM sentiment_score GROUP BY trade_date ORDER BY trade_date DESC;"
```

### 查看某日期的统计
```bash
docker exec quantbull_postgres psql -U quantbull -d quantbull_db \
  -c "SELECT 
    COUNT(*) as total,
    AVG(sentiment_score) as avg_sentiment,
    AVG(hot_score) as avg_hot_score
  FROM sentiment_score s 
  LEFT JOIN hot_score h ON s.code=h.code AND s.trade_date=h.trade_date 
  WHERE s.trade_date='20260106';"
```

## 监控和维护

### 查看缓存使用情况
```bash
docker exec quantbull_postgres psql -U quantbull -d quantbull_db \
  -c "SELECT 
    'sentiment_score' as table_name,
    COUNT(*) as record_count,
    COUNT(DISTINCT trade_date) as date_count,
    pg_size_pretty(pg_total_relation_size('sentiment_score')) as table_size
  FROM sentiment_score
  UNION ALL
  SELECT 
    'hot_score',
    COUNT(*),
    COUNT(DISTINCT trade_date),
    pg_size_pretty(pg_total_relation_size('hot_score'))
  FROM hot_score;"
```

### 定期清理过期数据（可选）
```bash
# 清理30天前的数据
docker exec quantbull_postgres psql -U quantbull -d quantbull_db \
  -c "DELETE FROM sentiment_score WHERE created_at < NOW() - INTERVAL '30 days';
      DELETE FROM hot_score WHERE created_at < NOW() - INTERVAL '30 days';"
```
