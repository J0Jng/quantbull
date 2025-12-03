# API Gateway Service

API网关服务，负责统一入口、路由转发、鉴权、限流等功能。

## 目录结构

```
gateway/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口
│   ├── config.py            # 配置管理
│   ├── middleware/          # 中间件
│   │   ├── __init__.py
│   │   ├── auth.py          # 认证中间件
│   │   ├── rate_limit.py    # 限流中间件
│   │   └── cors.py          # CORS处理
│   ├── routes/              # 路由定义
│   │   ├── __init__.py
│   │   ├── health.py        # 健康检查
│   │   └── proxy.py         # 服务代理路由
│   └── utils/
│       ├── __init__.py
│       ├── logging.py       # 日志配置
│       └── response.py      # 统一响应格式
├── requirements.txt
├── Dockerfile
└── .env.example
```

