# 架构总览

## 微服务架构说明

量化牛牛（QuantBull）采用微服务架构，各服务独立部署、可扩展。

### 服务列表

1. **gateway** - API网关
   - 统一入口
   - 路由转发
   - 鉴权授权
   - 限流熔断

2. **data-service** - 数据中台
   - 行情数据采集
   - 新闻快讯抓取
   - 数据清洗存储
   - 定时任务调度

3. **ai-service** - AI中台
   - LLM网关管理
   - Prompt工程
   - AI内容生成
   - 向量检索

4. **quant-engine** - 量化引擎
   - 策略回测
   - 因子计算
   - 股票筛选
   - ETF轮动

5. **content-service** - 内容服务
   - 内容管理
   - 审核发布
   - 公众号推送
   - H5页面生成

6. **frontend-web** - Web前端
   - Vue3 + Element Plus
   - 仪表盘
   - 量化实验室
   - 内容展示

7. **miniapp** - 微信小程序
   - Uni-app框架
   - 新闻浏览
   - 投资日刊
   - 视频播放

## 技术选型

- **后端框架**: FastAPI
- **数据库**: PostgreSQL, TDengine, Redis, Milvus
- **消息队列**: Celery + Redis
- **容器化**: Docker + Docker Compose
- **前端**: Vue3, Uni-app

## 数据流

1. 数据采集 → data-service → 存储（PostgreSQL/TDengine）
2. 数据查询 → gateway → data-service
3. AI生成 → gateway → ai-service → LLM → 生成内容
4. 内容发布 → gateway → content-service → 存储
5. 策略回测 → gateway → quant-engine → data-service

