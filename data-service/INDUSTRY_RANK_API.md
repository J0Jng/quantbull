# 行业景气度排名接口说明

## 接口信息
- **路径**: `GET /api/fundamentals/industry/rank`
- **参数**: `month` (可选) - 月份格式 YYYY-MM，不传则使用当前月份
- **认证**: 无需认证（已添加到白名单）

## 当前状态 ✅
接口已可用并能够快速响应（< 1秒）。

## 返回示例
```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "month": "2026-01",
    "data": []
  }
}
```

## 重要说明

### 首次使用
- 接口返回的数据依赖于缓存机制
- 如果缓存不存在，将返回空数组 `[]`
- 数据缓存有效期为 24 小时

### 数据生成
计算行业景气度需要：
1. 获取全市场股票基础信息
2. 按行业分组
3. 为每个行业的样本股票获取财务指标
4. 计算平均增长率并排名

**首次完整计算预计需要 10-15 分钟**，主要耗时在 Tushare API 调用。

### 推荐使用方式

#### 方案 1: 定时任务预热缓存（推荐）
创建定时任务在每日固定时间（如凌晨）预热缓存：

```python
# 示例：使用 APScheduler
from apscheduler.schedulers.background import BackgroundScheduler

def preheat_industry_rank():
    """预热行业排名缓存"""
    try:
        service = FundamentalsService()
        # 注意：需要实现完整的计算逻辑
        result = service.calculate_industry_rank()
        print(f"预热完成，共 {len(result)} 个行业")
    except Exception as e:
        print(f"预热失败: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(preheat_industry_rank, 'cron', hour=2, minute=0)
scheduler.start()
```

#### 方案 2: 后台异步计算
当接口发现缓存不存在时，触发后台任务进行计算：

```python
from fastapi import BackgroundTasks

@router.get("/industry/rank")
async def get_industry_rank(
    background_tasks: BackgroundTasks,
    month: Optional[str] = None
):
    service = FundamentalsService()
    items = service.get_cached_industry_rank(month)
    
    if not items:
        # 触发后台计算
        background_tasks.add_task(service.calculate_and_cache_industry_rank, month)
        return IndustryRankResponse(
            month=month or datetime.now().strftime("%Y-%m"),
            data=[],
            message="数据正在计算中，请稍后重试"
        )
    
    return IndustryRankResponse(month=month, data=items)
```

#### 方案 3: 提供计算进度 API
添加一个接口让用户查询计算进度：

```python
@router.get("/industry/rank/status")
async def get_rank_calculation_status(month: Optional[str] = None):
    """查询行业排名计算状态"""
    # 返回: pending, calculating, completed, error
    pass
```

## 当前实现的临时方案
为避免首次请求超时，当前实现为：
- ✅ 如果有缓存，立即返回（< 1秒）
- ✅ 如果无缓存，返回空数组（< 1秒）
- ⚠️ 不会自动触发计算（需要手动预热或实现上述方案）

## 测试验证

### 测试接口可用性
```bash
# Windows PowerShell
Invoke-WebRequest -Uri "http://localhost:8000/api/fundamentals/industry/rank" -UseBasicParsing

# Linux/Mac
curl http://localhost:8000/api/fundamentals/industry/rank
```

### 预期响应
- HTTP 状态码: 200
- 响应时间: < 2秒
- 数据格式: 
  - `month`: 查询月份
  - `data`: 行业数组（可能为空）

## Docker 日志监控
```bash
# 查看服务日志
docker logs data-service --tail 50

# 持续监控
docker logs data-service -f
```

## 问题排查

### 1. 接口超时
- **原因**: 可能触发了完整计算
- **解决**: 重启服务或等待计算完成

### 2. 返回 401 未授权
- **原因**: 白名单配置未生效
- **解决**: 重新构建 api-gateway
  ```bash
  docker-compose build api-gateway
  docker-compose up -d api-gateway
  ```

### 3. 返回空数据
- **原因**: 正常情况，缓存不存在
- **解决**: 实现预热机制或手动触发计算

## 下一步优化建议

1. **实现后台任务系统**
   - 使用 Celery 或 FastAPI BackgroundTasks
   - 定时预热缓存
   - 提供计算进度查询

2. **优化计算性能**
   - 使用并发请求 Tushare API
   - 实现分批处理
   - 优化数据库查询

3. **改进缓存策略**
   - 使用 Redis 替代内存缓存
   - 实现缓存预加载
   - 添加缓存失效回调

4. **监控和告警**
   - 添加计算耗时监控
   - API 调用频率监控
   - 缓存命中率统计

## 相关文件
- 路由: `data-service/routers/fundamentals.py`
- 服务: `data-service/services/fundamentals_service.py`
- Schema: `data-service/schemas/fundamentals.py`
- 认证中间件: `api-gateway/middlewares/auth.py`
