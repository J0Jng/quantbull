# Frontend Web

量化牛牛主站（Web），采用 Vue3 + Element Plus 构建。

## 目录结构

```
frontend-web/
├── src/
│   ├── main.js              # 入口文件
│   ├── App.vue              # 根组件
│   ├── router/              # 路由配置
│   │   ├── index.js
│   │   └── routes.js
│   ├── store/               # 状态管理 (Pinia)
│   │   ├── index.js
│   │   ├── user.js
│   │   └── market.js
│   ├── views/               # 页面组件
│   │   ├── Home.vue         # 首页
│   │   ├── Dashboard.vue    # 仪表盘
│   │   ├── News/            # 新闻中心
│   │   │   ├── index.vue
│   │   │   └── detail.vue
│   │   ├── QuantLab/        # 量化实验室
│   │   │   ├── index.vue
│   │   │   ├── StrategyEditor.vue  # 策略编辑器
│   │   │   └── Backtest.vue        # 回测页面
│   │   ├── DailyReport/     # 投资日刊
│   │   │   └── index.vue
│   │   └── Video/           # 视频中心
│   │       └── index.vue
│   ├── components/          # 公共组件
│   │   ├── Chart/           # 图表组件
│   │   ├── Table/           # 表格组件
│   │   └── Editor/          # 编辑器组件
│   ├── api/                 # API接口
│   │   ├── index.js
│   │   ├── market.js
│   │   ├── news.js
│   │   └── quant.js
│   ├── utils/               # 工具函数
│   │   ├── request.js       # HTTP请求封装
│   │   └── common.js
│   ├── assets/              # 静态资源
│   │   ├── images/
│   │   └── styles/
│   └── constants/           # 常量定义
│       └── index.js
├── public/                  # 公共资源
├── package.json
├── vite.config.js
├── .env.development
├── .env.production
└── Dockerfile
```

