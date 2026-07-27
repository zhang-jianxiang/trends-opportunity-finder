-- ============================================
-- Google Trends 数据分析系统 - 数据库表结构
-- 适用于 Neon / 任何标准 PostgreSQL
-- 在 Neon Console 的 SQL Editor 中执行此文件
-- ============================================

-- 关键词表
CREATE TABLE IF NOT EXISTS keywords (
    id BIGSERIAL PRIMARY KEY,
    keyword VARCHAR(255) NOT NULL UNIQUE,
    category VARCHAR(100) DEFAULT 'general',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 地区表
CREATE TABLE IF NOT EXISTS regions (
    id BIGSERIAL PRIMARY KEY,
    region_code VARCHAR(10) NOT NULL UNIQUE,
    region_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 趋势数据表（核心表）
CREATE TABLE IF NOT EXISTS trends_data (
    id BIGSERIAL PRIMARY KEY,
    keyword_id BIGINT REFERENCES keywords(id) ON DELETE CASCADE,
    region_id BIGINT REFERENCES regions(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    score INTEGER NOT NULL DEFAULT 0,
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(keyword_id, region_id, date)
);

-- 相关查询表
CREATE TABLE IF NOT EXISTS related_queries (
    id BIGSERIAL PRIMARY KEY,
    keyword_id BIGINT REFERENCES keywords(id) ON DELETE CASCADE,
    region_id BIGINT REFERENCES regions(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    query_type VARCHAR(20) NOT NULL,
    query_text VARCHAR(500) NOT NULL,
    value VARCHAR(50) DEFAULT '0',
    collected_at TIMESTAMPTZ DEFAULT NOW()
);

-- 趋势分析结果表
CREATE TABLE IF NOT EXISTS trend_analysis (
    id BIGSERIAL PRIMARY KEY,
    keyword_id BIGINT REFERENCES keywords(id) ON DELETE CASCADE,
    region_id BIGINT REFERENCES regions(id) ON DELETE CASCADE,
    analysis_date DATE NOT NULL,
    current_score INTEGER DEFAULT 0,
    avg_score_7d NUMERIC(8,2) DEFAULT 0,
    avg_score_30d NUMERIC(8,2) DEFAULT 0,
    score_change_pct NUMERIC(8,2) DEFAULT 0,
    trend_direction VARCHAR(20) DEFAULT 'stable',
    trend_strength NUMERIC(5,2) DEFAULT 0,
    volatility NUMERIC(8,4) DEFAULT 0,
    opportunity_score NUMERIC(5,2) DEFAULT 0,
    market_potential VARCHAR(20) DEFAULT 'low',
    is_anomaly BOOLEAN DEFAULT false,
    anomaly_score NUMERIC(8,4) DEFAULT 0,
    recommendation TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(keyword_id, region_id, analysis_date)
);

-- 市场机会表
CREATE TABLE IF NOT EXISTS opportunities (
    id BIGSERIAL PRIMARY KEY,
    keyword_id BIGINT REFERENCES keywords(id) ON DELETE CASCADE,
    region_id BIGINT REFERENCES regions(id) ON DELETE CASCADE,
    opportunity_type VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    score NUMERIC(5,2) NOT NULL DEFAULT 0,
    market_size VARCHAR(20) DEFAULT 'medium',
    competition_level VARCHAR(20) DEFAULT 'medium',
    trend_direction VARCHAR(20) DEFAULT 'stable',
    detected_date DATE NOT NULL DEFAULT CURRENT_DATE,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 采集日志表
CREATE TABLE IF NOT EXISTS collection_logs (
    id BIGSERIAL PRIMARY KEY,
    task_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    records_collected INTEGER DEFAULT 0,
    duration_seconds INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 索引优化
-- ============================================
CREATE INDEX IF NOT EXISTS idx_trends_data_keyword_date ON trends_data(keyword_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_trends_data_region_date ON trends_data(region_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_trends_data_date ON trends_data(date DESC);

CREATE INDEX IF NOT EXISTS idx_trend_analysis_score ON trend_analysis(opportunity_score DESC);
CREATE INDEX IF NOT EXISTS idx_trend_analysis_date ON trend_analysis(analysis_date DESC);
CREATE INDEX IF NOT EXISTS idx_trend_analysis_anomaly ON trend_analysis(is_anomaly) WHERE is_anomaly = true;

CREATE INDEX IF NOT EXISTS idx_opportunities_score ON opportunities(score DESC);
CREATE INDEX IF NOT EXISTS idx_opportunities_date ON opportunities(detected_date DESC);
CREATE INDEX IF NOT EXISTS idx_opportunities_status ON opportunities(status);

CREATE INDEX IF NOT EXISTS idx_collection_logs_status ON collection_logs(status, created_at DESC);

-- ============================================
-- 初始数据：地区表
-- ============================================
INSERT INTO regions (region_code, region_name) VALUES
    ('', 'Global'),
    ('US', 'United States'),
    ('CN', 'China'),
    ('GB', 'United Kingdom'),
    ('DE', 'Germany'),
    ('JP', 'Japan'),
    ('FR', 'France'),
    ('CA', 'Canada'),
    ('AU', 'Australia'),
    ('IN', 'India'),
    ('BR', 'Brazil'),
    ('KR', 'South Korea')
ON CONFLICT (region_code) DO NOTHING;

-- ============================================
-- 初始数据：关键词表
-- ============================================
INSERT INTO keywords (keyword, category) VALUES
    ('artificial intelligence', 'technology'),
    ('machine learning', 'technology'),
    ('digital health', 'health'),
    ('cryptocurrency', 'finance'),
    ('sustainable energy', 'environment'),
    ('remote work', 'lifestyle'),
    ('electric vehicles', 'technology'),
    ('social media', 'technology'),
    ('online learning', 'education'),
    ('fitness apps', 'health')
ON CONFLICT (keyword) DO NOTHING;

-- ============================================
-- 视图：最新趋势摘要（方便前端查询）
-- ============================================
CREATE OR REPLACE VIEW v_latest_trends AS
SELECT
    k.keyword,
    k.category,
    r.region_code,
    r.region_name,
    t.date,
    t.score,
    ta.trend_direction,
    ta.trend_strength,
    ta.opportunity_score,
    ta.market_potential,
    ta.is_anomaly,
    ta.recommendation
FROM trends_data t
JOIN keywords k ON t.keyword_id = k.id
JOIN regions r ON t.region_id = r.id
LEFT JOIN trend_analysis ta ON t.keyword_id = ta.keyword_id
    AND t.region_id = ta.region_id
    AND t.date = ta.analysis_date
WHERE t.date = (SELECT MAX(date) FROM trends_data)
ORDER BY ta.opportunity_score DESC NULLS LAST;

-- ============================================
-- 视图：活跃机会列表
-- ============================================
CREATE OR REPLACE VIEW v_active_opportunities AS
SELECT
    o.id,
    k.keyword,
    k.category,
    r.region_code,
    r.region_name,
    o.opportunity_type,
    o.title,
    o.description,
    o.score,
    o.market_size,
    o.competition_level,
    o.trend_direction,
    o.detected_date,
    o.status
FROM opportunities o
JOIN keywords k ON o.keyword_id = k.id
JOIN regions r ON o.region_id = r.id
WHERE o.status = 'active'
ORDER BY o.score DESC;
