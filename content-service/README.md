# Content Service

内容服务，负责内容审核、存储、展示、公众号推送等。

## 快速开始

```bash
### 本地开发

# 给启动脚本执行权限
chmod +x start.sh

# 启动所有服务
./start.sh

# 或者使用 make
make start

## 目录结构

```
content-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口
│   ├── config.py            # 配置管理
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   ├── article.py       # 文章模型
│   │   ├── video.py         # 视频模型
│   │   └── daily_report.py  # 投资日刊模型
│   ├── services/            # 业务服务
│   │   ├── __init__.py
│   │   ├── content.py       # 内容管理服务
│   │   ├── audit.py         # 内容审核服务
│   │   ├── wechat.py        # 微信公众号服务
│   │   └── storage.py       # 内容存储服务
│   ├── templates/           # H5页面模板
│   │   ├── article.html     # 文章页面
│   │   ├── daily_report.html # 投资日刊页面
│   │   └── video.html       # 视频页面
│   ├── storage/             # 存储层
│   │   ├── __init__.py
│   │   ├── oss.py           # 对象存储
│   │   └── db.py            # 数据库操作
│   ├── api/                 # API接口
│   │   ├── __init__.py
│   │   ├── content.py       # 内容API
│   │   ├── h5.py            # H5页面API
│   │   └── wechat.py        # 微信推送API
│   └── utils/
│       ├── __init__.py
│       └── logger.py
├── requirements.txt
├── Dockerfile
└── .env.example
```

