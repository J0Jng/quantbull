-- Initialize Content Service Database

-- Create tables for crawler module
CREATE TABLE IF NOT EXISTS crawl_sources (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    crawl_pattern TEXT,
    interval_minutes INTEGER DEFAULT 60,
    is_active BOOLEAN DEFAULT TRUE,
    last_crawl_time TIMESTAMP,
    config JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS crawl_tasks (
    task_id VARCHAR(255) PRIMARY KEY,
    source_id VARCHAR(255) REFERENCES crawl_sources(id),
    status VARCHAR(50) DEFAULT 'pending',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    items_found INTEGER DEFAULT 0,
    items_processed INTEGER DEFAULT 0,
    error TEXT,
    result_urls JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_crawl_sources_active ON crawl_sources(is_active);
CREATE INDEX IF NOT EXISTS idx_crawl_tasks_status ON crawl_tasks(status);
CREATE INDEX IF NOT EXISTS idx_crawl_tasks_source ON crawl_tasks(source_id);