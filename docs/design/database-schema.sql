-- =====================================================
-- 量化牛牛（QuantBull）数据库设计脚本
-- 数据库: PostgreSQL 15+
-- 创建时间: 2024-12
-- =====================================================

-- =====================================================
-- 1. 用户相关表
-- =====================================================

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(100),
    avatar_url VARCHAR(500),
    phone VARCHAR(20),
    role VARCHAR(20) DEFAULT 'user', -- user, admin, vip
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, banned
    vip_expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_status ON users(status);

-- =====================================================
-- 2. 新闻和文章相关表
-- =====================================================

-- 新闻来源表
CREATE TABLE IF NOT EXISTS news_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL, -- 财联社、东方财富等
    code VARCHAR(50) UNIQUE NOT NULL,
    url VARCHAR(500),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 新闻表
CREATE TABLE IF NOT EXISTS news (
    id BIGSERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES news_sources(id),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,
    author VARCHAR(100),
    url VARCHAR(500),
    publish_time TIMESTAMP NOT NULL,
    collect_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    category VARCHAR(50), -- 财经、科技、政策等
    tags TEXT[], -- 标签数组
    related_stocks TEXT[], -- 关联股票代码数组
    sentiment_score DECIMAL(5,2), -- 情感分析得分 -1到1
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'published', -- draft, published, archived
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_news_publish_time ON news(publish_time DESC);
CREATE INDEX idx_news_category ON news(category);
CREATE INDEX idx_news_status ON news(status);
CREATE INDEX idx_news_related_stocks ON news USING GIN(related_stocks);
CREATE INDEX idx_news_tags ON news USING GIN(tags);
-- 全文检索索引
CREATE INDEX idx_news_content_search ON news USING GIN(to_tsvector('english', title || ' ' || content));

-- 文章表（AI生成的深度文章）
CREATE TABLE IF NOT EXISTS articles (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,
    cover_image_url VARCHAR(500),
    author VARCHAR(100) DEFAULT 'AI',
    category VARCHAR(50),
    tags TEXT[],
    related_news_ids BIGINT[], -- 关联的新闻ID
    related_stocks TEXT[],
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'draft', -- draft, reviewed, published, archived
    reviewed_by INTEGER REFERENCES users(id),
    reviewed_at TIMESTAMP,
    publish_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_articles_publish_time ON articles(publish_time DESC);
CREATE INDEX idx_articles_status ON articles(status);
CREATE INDEX idx_articles_category ON articles(category);
CREATE INDEX idx_articles_related_stocks ON articles USING GIN(related_stocks);

-- =====================================================
-- 3. 投资日刊相关表
-- =====================================================

-- 投资日刊表
CREATE TABLE IF NOT EXISTS daily_reports (
    id BIGSERIAL PRIMARY KEY,
    report_date DATE NOT NULL UNIQUE, -- 报告日期
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    market_overview TEXT, -- 市场综述
    recommended_etfs JSONB, -- 推荐的ETF列表 [{code, name, reason, score}]
    recommended_stocks JSONB, -- 推荐的股票列表 [{code, name, reason, score, factors}]
    market_analysis TEXT, -- 市场分析
    risk_warning TEXT, -- 风险提示
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'draft', -- draft, generating, published
    generated_by VARCHAR(50) DEFAULT 'AI', -- AI生成标识
    generated_at TIMESTAMP,
    publish_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_daily_reports_date ON daily_reports(report_date DESC);
CREATE INDEX idx_daily_reports_status ON daily_reports(status);

-- =====================================================
-- 4. 量化策略相关表
-- =====================================================

-- 策略表
CREATE TABLE IF NOT EXISTS strategies (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    code TEXT NOT NULL, -- 策略代码（Python）
    language VARCHAR(20) DEFAULT 'python', -- python, backtrader
    category VARCHAR(50), -- 技术指标、因子、ETF轮动等
    parameters JSONB, -- 策略参数
    status VARCHAR(20) DEFAULT 'draft', -- draft, active, paused, archived
    is_public BOOLEAN DEFAULT FALSE, -- 是否公开
    view_count INTEGER DEFAULT 0,
    use_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_strategies_user_id ON strategies(user_id);
CREATE INDEX idx_strategies_status ON strategies(status);
CREATE INDEX idx_strategies_category ON strategies(category);
CREATE INDEX idx_strategies_is_public ON strategies(is_public);

-- 回测记录表
CREATE TABLE IF NOT EXISTS backtests (
    id BIGSERIAL PRIMARY KEY,
    strategy_id BIGINT REFERENCES strategies(id),
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(200),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital DECIMAL(20,2) NOT NULL,
    final_capital DECIMAL(20,2),
    total_return DECIMAL(10,4), -- 总收益率
    annual_return DECIMAL(10,4), -- 年化收益率
    sharpe_ratio DECIMAL(10,4), -- 夏普比率
    max_drawdown DECIMAL(10,4), -- 最大回撤
    win_rate DECIMAL(5,4), -- 胜率
    total_trades INTEGER, -- 总交易次数
    parameters JSONB, -- 回测参数
    results JSONB, -- 详细结果（持仓、交易记录等）
    status VARCHAR(20) DEFAULT 'running', -- running, completed, failed
    error_message TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_backtests_strategy_id ON backtests(strategy_id);
CREATE INDEX idx_backtests_user_id ON backtests(user_id);
CREATE INDEX idx_backtests_status ON backtests(status);
CREATE INDEX idx_backtests_start_date ON backtests(start_date DESC);

-- =====================================================
-- 5. 公司和股票相关表
-- =====================================================

-- 公司信息表
CREATE TABLE IF NOT EXISTS companies (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL, -- 股票代码
    name VARCHAR(200) NOT NULL, -- 公司名称
    full_name VARCHAR(500), -- 公司全称
    industry VARCHAR(100), -- 所属行业
    market VARCHAR(20), -- 市场：SH, SZ, BJ
    list_date DATE, -- 上市日期
    introduction TEXT, -- 公司简介
    main_business TEXT, -- 主营业务
    website VARCHAR(500),
    address TEXT,
    total_shares BIGINT, -- 总股本
    float_shares BIGINT, -- 流通股本
    market_cap DECIMAL(20,2), -- 市值
    status VARCHAR(20) DEFAULT 'active', -- active, suspended, delisted
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_companies_code ON companies(code);
CREATE INDEX idx_companies_industry ON companies(industry);
CREATE INDEX idx_companies_market ON companies(market);

-- ETF信息表
CREATE TABLE IF NOT EXISTS etfs (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    full_name VARCHAR(500),
    category VARCHAR(50), -- 股票型、债券型、货币型等
    market VARCHAR(20),
    fund_company VARCHAR(200), -- 基金公司
    list_date DATE,
    introduction TEXT,
    underlying_index VARCHAR(200), -- 跟踪指数
    total_assets DECIMAL(20,2), -- 基金规模
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_etfs_code ON etfs(code);
CREATE INDEX idx_etfs_category ON etfs(category);

-- =====================================================
-- 6. 视频相关表
-- =====================================================

-- 视频资源表
CREATE TABLE IF NOT EXISTS videos (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    video_url VARCHAR(500) NOT NULL,
    cover_image_url VARCHAR(500),
    thumbnail_url VARCHAR(500),
    duration INTEGER, -- 视频时长（秒）
    resolution VARCHAR(20), -- 分辨率
    file_size BIGINT, -- 文件大小（字节）
    format VARCHAR(20), -- 视频格式
    category VARCHAR(50), -- 市场解读、策略讲解等
    related_content_type VARCHAR(50), -- news, article, daily_report
    related_content_id BIGINT, -- 关联内容ID
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'processing', -- processing, ready, published, archived
    generated_by VARCHAR(50) DEFAULT 'AI', -- AI生成标识
    generation_task_id VARCHAR(100), -- 生成任务ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_videos_status ON videos(status);
CREATE INDEX idx_videos_category ON videos(category);
CREATE INDEX idx_videos_related_content ON videos(related_content_type, related_content_id);

-- =====================================================
-- 7. 用户行为相关表
-- =====================================================

-- 用户自选股表
CREATE TABLE IF NOT EXISTS user_watchlists (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    stock_code VARCHAR(20) NOT NULL,
    add_reason TEXT,
    price_when_added DECIMAL(10,2), -- 加入时的价格
    target_price DECIMAL(10,2), -- 目标价
    alert_price DECIMAL(10,2), -- 提醒价
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, stock_code)
);

CREATE INDEX idx_user_watchlists_user_id ON user_watchlists(user_id);
CREATE INDEX idx_user_watchlists_stock_code ON user_watchlists(stock_code);

-- 内容浏览记录表
CREATE TABLE IF NOT EXISTS content_views (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    content_type VARCHAR(50) NOT NULL, -- news, article, daily_report, video
    content_id BIGINT NOT NULL,
    view_duration INTEGER, -- 浏览时长（秒）
    view_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_content_views_user_id ON content_views(user_id);
CREATE INDEX idx_content_views_content ON content_views(content_type, content_id);
CREATE INDEX idx_content_views_view_at ON content_views(view_at DESC);

-- 用户点赞表
CREATE TABLE IF NOT EXISTS user_likes (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    content_type VARCHAR(50) NOT NULL,
    content_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, content_type, content_id)
);

CREATE INDEX idx_user_likes_user_id ON user_likes(user_id);
CREATE INDEX idx_user_likes_content ON user_likes(content_type, content_id);

-- =====================================================
-- 8. 系统配置相关表
-- =====================================================

-- Prompt模板表
CREATE TABLE IF NOT EXISTS prompt_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL UNIQUE,
    category VARCHAR(50), -- news_generation, strategy_generation, daily_report等
    template TEXT NOT NULL,
    variables TEXT[], -- 模板变量列表
    description TEXT,
    version VARCHAR(20) DEFAULT '1.0',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_prompt_templates_category ON prompt_templates(category);
CREATE INDEX idx_prompt_templates_is_active ON prompt_templates(is_active);

-- 系统配置表
CREATE TABLE IF NOT EXISTS system_configs (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    config_type VARCHAR(50), -- string, int, float, json, bool
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES users(id)
);

-- =====================================================
-- 9. 微信公众号相关表
-- =====================================================

-- 微信推送记录表
CREATE TABLE IF NOT EXISTS wechat_push_logs (
    id BIGSERIAL PRIMARY KEY,
    content_type VARCHAR(50) NOT NULL, -- daily_report, article, news
    content_id BIGINT NOT NULL,
    push_type VARCHAR(50) NOT NULL, -- template_message, article, news
    target_users JSONB, -- 推送目标用户列表
    push_status VARCHAR(20) DEFAULT 'pending', -- pending, sent, failed
    sent_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    error_message TEXT,
    scheduled_at TIMESTAMP,
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_wechat_push_logs_status ON wechat_push_logs(push_status);
CREATE INDEX idx_wechat_push_logs_scheduled_at ON wechat_push_logs(scheduled_at);

-- =====================================================
-- 10. 时间戳触发器函数
-- =====================================================

-- 自动更新updated_at字段的触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要自动更新updated_at的表创建触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_news_updated_at BEFORE UPDATE ON news
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_articles_updated_at BEFORE UPDATE ON articles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_daily_reports_updated_at BEFORE UPDATE ON daily_reports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_strategies_updated_at BEFORE UPDATE ON strategies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_etfs_updated_at BEFORE UPDATE ON etfs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_videos_updated_at BEFORE UPDATE ON videos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 11. TDengine 表结构（SQL语句，需在TDengine中执行）
-- =====================================================

/*
-- TDengine 数据库和表创建（在TDengine中执行）

-- 创建数据库
CREATE DATABASE IF NOT EXISTS quantbull 
    KEEP 365d  -- 数据保留365天
    DAYS 10    -- 数据保存10天以上开始压缩
    REPLICA 1  -- 副本数
    BLOCKS 6   -- 块数
    CACHE 64   -- 缓存大小(MB)
    WAL_LEVEL 1;

USE quantbull;

-- 创建超级表：行情数据
CREATE STABLE IF NOT EXISTS market_data (
    ts TIMESTAMP,
    code NCHAR(20),
    name NCHAR(100),
    open DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE,
    volume BIGINT,
    amount DOUBLE,
    change_pct DOUBLE,
    turnover_rate DOUBLE
) TAGS (
    market NCHAR(10)  -- SH, SZ, BJ
);

-- 创建超级表：K线数据
CREATE STABLE IF NOT EXISTS kline_data (
    ts TIMESTAMP,
    code NCHAR(20),
    open DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE,
    volume BIGINT,
    amount DOUBLE,
    turnover_rate DOUBLE
) TAGS (
    market NCHAR(10),
    period NCHAR(10)  -- 1m, 5m, 15m, 30m, 1h, 1d
);

-- 创建超级表：实时行情
CREATE STABLE IF NOT EXISTS realtime_quotes (
    ts TIMESTAMP,
    code NCHAR(20),
    price DOUBLE,
    change DOUBLE,
    change_pct DOUBLE,
    volume BIGINT,
    amount DOUBLE,
    bid_price1 DOUBLE,
    bid_volume1 INT,
    ask_price1 DOUBLE,
    ask_volume1 INT
) TAGS (
    market NCHAR(10)
);

-- 示例：为某股票创建子表（自动创建，这里仅作说明）
-- CREATE TABLE IF NOT EXISTS stock_000001 USING market_data TAGS ('SH');
*/

-- =====================================================
-- 12. 初始化数据
-- =====================================================

-- 插入新闻来源
INSERT INTO news_sources (name, code, url, status) VALUES
    ('财联社', 'cls', 'https://www.cls.cn', 'active'),
    ('东方财富', 'eastmoney', 'http://www.eastmoney.com', 'active'),
    ('同花顺', '10jqka', 'http://www.10jqka.com.cn', 'active')
ON CONFLICT (code) DO NOTHING;

-- 插入系统配置
INSERT INTO system_configs (config_key, config_value, config_type, description) VALUES
    ('system.name', '量化牛牛', 'string', '系统名称'),
    ('system.version', '1.0.0', 'string', '系统版本'),
    ('market.trading_hours', '{"start": "09:30", "end": "15:00"}', 'json', '交易时间配置')
ON CONFLICT (config_key) DO NOTHING;

-- =====================================================
-- 文档结束
-- =====================================================

