# 微博财经新闻定时刷新 & 数据库存储 - 快速使用指南

## 🎯 新增功能

### 1️⃣ 定时刷新（APScheduler）
- ✅ 每 5 分钟自动预加载微博新闻
- ✅ 减少用户请求延迟
- ✅ 自动保存到数据库
- ✅ 可配置刷新间隔

### 2️⃣ 数据库存储（PostgreSQL）
- ✅ 新闻自动持久化存储
- ✅ 支持历史查询（1-168 小时）
- ✅ 支持关键词搜索
- ✅ 自动去重更新

## 🚀 快速开始

### 1. 数据库迁移（自动）

数据库表会在服务启动时自动创建，无需手动迁移。

```powershell
# 启动服务即可自动创建 weibo_news 表
docker-compose up -d data-service
```

**表结构：weibo_news**
- `id`: 自增主键
- `weibo_id`: 微博唯一标识（唯一索引）
- `title`: 新闻标题
- `summary`: 新闻摘要
- `source`, `author`, `url`, `img_url`: 元数据
- `publish_timestamp`: 发布时间戳（索引，用于排序）
- `created_at`, `updated_at`: 入库和更新时间

### 2. 验证定时任务

```powershell
# 查看定时任务日志
docker-compose logs -f data-service | Select-String "定时"

# 期望输出：
# INFO:__main__:微博新闻定时刷新任务已启动
# INFO:root:开始定时刷新微博新闻缓存...
# INFO:root:定时刷新完成，获取 X 条新闻
# INFO:root:成功保存 X 条新闻到数据库
```

### 3. 测试新接口

#### 测试历史查询接口

```powershell
# 查询最近 24 小时的新闻
Invoke-WebRequest -Uri "http://localhost:8000/api/news/weibo/history?limit=10&hours=24" | Select-Object -ExpandProperty Content

# 查询最近 7 天（168小时）的新闻
Invoke-WebRequest -Uri "http://localhost:8000/api/news/weibo/history?limit=20&hours=168" | Select-Object -ExpandProperty Content

# 关键词搜索历史新闻
Invoke-WebRequest -Uri "http://localhost:8000/api/news/weibo/history?limit=10&keyword=央行&hours=48" | Select-Object -ExpandProperty Content
```

#### 验证数据库存储

```powershell
# 等待 5 分钟后，定时任务会自动运行并保存数据
# 然后查询历史接口，应该能看到数据

# 或者手动触发一次抓取
Invoke-WebRequest -Uri "http://localhost:8000/api/news/weibo/media?limit=20" | Select-Object -ExpandProperty Content

# 然后立即查询历史
Invoke-WebRequest -Uri "http://localhost:8000/api/news/weibo/history?limit=10" | Select-Object -ExpandProperty Content
```

## 📊 API 对比

| 接口 | 数据来源 | 适用场景 | 响应速度 |
|------|---------|---------|----------|
| `/api/news/weibo/media` | 实时抓取 + 缓存 | 获取最新新闻 | 快（缓存命中）或慢（首次抓取） |
| `/api/news/weibo/history` | 数据库查询 | 历史查询、趋势分析 | 快（< 100ms） |

## ⚙️ 配置调整

### 修改定时刷新间隔

编辑 [data-service/main.py](../main.py#L38-L48)：

```python
# 默认 5 分钟
scheduler.start(interval_minutes=5)

# 改为 10 分钟
scheduler.start(interval_minutes=10)

# 改为 1 分钟（不推荐，可能触发限流）
scheduler.start(interval_minutes=1)
```

### 调整历史查询时间范围

```python
# 默认查询最近 24 小时
GET /api/news/weibo/history?hours=24

# 查询最近 1 小时
GET /api/news/weibo/history?hours=1

# 查询最近 7 天
GET /api/news/weibo/history?hours=168
```

## 🔍 监控与排查

### 检查定时任务状态

```powershell
# 查看完整日志
docker-compose logs -f data-service

# 只看定时任务相关日志
docker-compose logs data-service | Select-String "定时|刷新|保存"
```

### 检查数据库存储

```sql
-- 连接到 PostgreSQL
-- 查询新闻总数
SELECT COUNT(*) FROM weibo_news;

-- 查询最新 10 条新闻
SELECT title, author, publish_time, created_at 
FROM weibo_news 
ORDER BY publish_timestamp DESC 
LIMIT 10;

-- 查询某个关键词的新闻
SELECT title, summary 
FROM weibo_news 
WHERE title LIKE '%央行%' OR summary LIKE '%央行%'
ORDER BY publish_timestamp DESC;
```

### 常见问题

#### 问题 1：定时任务未启动

**解决方案**：
```powershell
# 查看日志中是否有错误
docker-compose logs data-service | Select-String "定时任务|scheduler"

# 如果看到"定时任务启动失败"，检查 APScheduler 是否正确安装
docker-compose exec data-service pip list | Select-String "apscheduler"
```

#### 问题 2：数据未保存到数据库

**解决方案**：
```powershell
# 检查数据库连接
docker-compose logs data-service | Select-String "database|PostgreSQL"

# 检查是否有保存失败的日志
docker-compose logs data-service | Select-String "保存.*失败"
```

#### 问题 3：历史查询返回空列表

**原因**：数据库中没有数据（定时任务未运行或抓取失败）

**解决方案**：
1. 等待 5 分钟，让定时任务运行一次
2. 或手动触发一次抓取：`GET /api/news/weibo/media`
3. 检查定时任务日志是否有错误

## 📈 性能优化建议

### 1. 调整定时刷新间隔

```python
# 根据流量调整
# 高流量：interval_minutes=3  （更频繁刷新）
# 中流量：interval_minutes=5  （默认）
# 低流量：interval_minutes=10 （减少抓取频率）
```

### 2. 数据库索引优化

```sql
-- 如果查询慢，可以添加复合索引
CREATE INDEX idx_weibo_news_author_timestamp 
ON weibo_news(author, publish_timestamp DESC);

CREATE INDEX idx_weibo_news_title_gin 
ON weibo_news USING gin(to_tsvector('chinese', title));
```

### 3. 清理历史数据

```sql
-- 定期清理 30 天前的数据
DELETE FROM weibo_news 
WHERE created_at < NOW() - INTERVAL '30 days';
```

## ✅ 功能验收

- [x] 服务启动时自动启动定时任务
- [x] 每 5 分钟自动刷新新闻
- [x] 新闻自动保存到数据库
- [x] 历史查询接口可用
- [x] 关键词过滤生效
- [x] 时间范围查询正确
- [x] 数据自动去重

## 📚 相关文档

- [完整功能文档](WEIBO_MEDIA_NEWS.md)
- [数据库模型](../models/weibo_news.py)
- [定时任务调度器](../scheduler_weibo_news.py)
- [聚合服务](../services/weibo_media_service.py)
- [新闻接口](../routers/news.py)

---

**创建时间**：2026-01-21
