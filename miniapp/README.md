# MiniApp

量化牛牛微信小程序，采用 Uni-app 框架构建。

## 目录结构

```
miniapp/
├── src/
│   ├── main.js              # 入口文件
│   ├── App.vue              # 根组件
│   ├── manifest.json        # 小程序配置
│   ├── pages.json           # 页面配置
│   ├── uni.scss             # 全局样式
│   ├── pages/               # 页面
│   │   ├── index/           # 首页
│   │   │   └── index.vue
│   │   ├── news/            # 新闻列表
│   │   │   ├── index.vue
│   │   │   └── detail.vue
│   │   ├── daily-report/    # 投资日刊
│   │   │   └── index.vue
│   │   ├── video/           # 视频中心
│   │   │   ├── index.vue
│   │   │   └── detail.vue
│   │   ├── watchlist/       # 自选股
│   │   │   └── index.vue
│   │   └── profile/         # 个人中心
│   │       └── index.vue
│   ├── components/          # 组件
│   │   ├── NewsCard.vue
│   │   ├── StockCard.vue
│   │   └── VideoPlayer.vue
│   ├── api/                 # API接口
│   │   ├── index.js
│   │   └── request.js
│   ├── store/               # 状态管理
│   │   └── index.js
│   ├── utils/               # 工具函数
│   │   └── common.js
│   └── static/              # 静态资源
│       └── images/
├── package.json
├── vite.config.js
└── .env.example
```

