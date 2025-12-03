# 设计文档

本目录包含系统设计相关的详细文档。

## 文档列表

### 数据库设计

- **[database-schema.sql](./database-schema.sql)** - 完整的数据库表结构设计
  - PostgreSQL 表结构
  - TDengine 表结构说明
  - 索引和触发器
  - 初始化数据

### API网关设计

- **[gateway-routes.yaml](./gateway-routes.yaml)** - API网关路由配置
  - 路由规则定义
  - 鉴权配置
  - 限流策略
  - 熔断降级配置

## 使用说明

### 数据库初始化

```bash
# 连接PostgreSQL
psql -U quantbull -d quantbull -f database-schema.sql

# 或在Docker中执行
docker exec -i postgres psql -U quantbull -d quantbull < database-schema.sql
```

### 网关配置

网关配置使用YAML格式，可作为FastAPI网关服务的配置参考。实际实现时可根据框架转换为相应的配置格式。

