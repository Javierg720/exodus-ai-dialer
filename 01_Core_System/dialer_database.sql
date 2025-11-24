-- Exodus Dialer Database Schema
-- SQLite database for campaign management, lead tracking, and call logging
-- Created: 2025-11-23

-- ============================================================================
-- CAMPAIGNS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    
    -- Dialing Configuration
    dial_method TEXT DEFAULT 'PROGRESSIVE' CHECK(dial_method IN ('PROGRESSIVE', 'PREDICTIVE', 'POWER', 'PREVIEW')),
    dial_ratio REAL DEFAULT 3.0,
    max_dial_ratio REAL DEFAULT 5.0,
    max_attempts INTEGER DEFAULT 3,
    retry_delay INTEGER DEFAULT 3600,  -- Seconds between retry attempts
    call_timeout INTEGER DEFAULT 30,   -- Seconds before timing out a call
    
    -- Working Hours (TCPA Compliance)
    working_hours_start TEXT DEFAULT '09:00',
    working_hours_end TEXT DEFAULT '21:00',
    timezone TEXT DEFAULT 'America/New_York',
    
    -- Voice Settings
    tts_voice TEXT DEFAULT 'en-US-JennyNeural',
    tts_speed REAL DEFAULT 1.0,
    tts_pitch REAL DEFAULT 1.0,
    interrupt_sensitivity REAL DEFAULT 0.5,  -- 0.0 = never interrupt, 1.0 = very sensitive
    
    -- Provider Configuration
    stt_provider TEXT DEFAULT 'deepgram',
    llm_provider TEXT DEFAULT 'groq',
    tts_provider TEXT DEFAULT 'edge',
    
    -- Campaign Status
    status TEXT DEFAULT 'PAUSED' CHECK(status IN ('ACTIVE', 'PAUSED', 'COMPLETED')),
    enable_recording INTEGER DEFAULT 1,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for active campaigns lookup
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);

-- ============================================================================
-- LEADS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    
    -- Contact Information
    phone_number TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    company TEXT,
    
    -- Location Information (for timezone/TCPA compliance)
    city TEXT,
    state TEXT,
    zip_code TEXT,
    timezone TEXT DEFAULT 'America/New_York',
    
    -- Lead Status
    status TEXT DEFAULT 'NEW' CHECK(status IN ('NEW', 'CALLING', 'COMPLETED', 'CALLBACK', 'DNC', 'FAILED')),
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    
    -- Call Scheduling
    last_call_time TIMESTAMP,
    next_call_time TIMESTAMP,
    
    -- Custom Data
    custom_data TEXT,  -- JSON field for custom lead data
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
);

-- Indexes for lead querying performance
CREATE INDEX IF NOT EXISTS idx_leads_campaign_status ON leads(campaign_id, status);
CREATE INDEX IF NOT EXISTS idx_leads_phone ON leads(phone_number);
CREATE INDEX IF NOT EXISTS idx_leads_next_call ON leads(next_call_time);
CREATE INDEX IF NOT EXISTS idx_leads_attempts ON leads(attempts);

-- Unique constraint: one lead per phone number per campaign
CREATE UNIQUE INDEX IF NOT EXISTS idx_leads_campaign_phone ON leads(campaign_id, phone_number);

-- ============================================================================
-- CALL LOG TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS call_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER NOT NULL,
    campaign_id INTEGER NOT NULL,
    call_uuid TEXT NOT NULL UNIQUE,
    bot_port INTEGER,
    
    -- Call Timing
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_seconds INTEGER DEFAULT 0,
    
    -- Call Outcome
    call_status TEXT CHECK(call_status IN ('ANSWERED', 'NO_ANSWER', 'BUSY', 'FAILED', 'ABANDONED')),
    disposition_code TEXT,
    was_dropped INTEGER DEFAULT 0,  -- 1 if no bot available (TCPA concern)
    
    -- Recording & Transcript
    recording_url TEXT,
    transcription_text TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
);

-- Indexes for call log queries
CREATE INDEX IF NOT EXISTS idx_call_log_lead ON call_log(lead_id);
CREATE INDEX IF NOT EXISTS idx_call_log_campaign ON call_log(campaign_id);
CREATE INDEX IF NOT EXISTS idx_call_log_uuid ON call_log(call_uuid);
CREATE INDEX IF NOT EXISTS idx_call_log_start_time ON call_log(start_time);
CREATE INDEX IF NOT EXISTS idx_call_log_status ON call_log(call_status);
CREATE INDEX IF NOT EXISTS idx_call_log_dropped ON call_log(was_dropped);

-- ============================================================================
-- DISPOSITIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS dispositions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    
    -- Disposition Behavior
    terminates_lead INTEGER DEFAULT 0,      -- 1 = Don't call again
    requires_callback INTEGER DEFAULT 0,    -- 1 = Schedule callback
    callback_delay_days INTEGER DEFAULT 3,  -- Days until callback
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Default dispositions
INSERT OR IGNORE INTO dispositions (code, name, description, terminates_lead, requires_callback, callback_delay_days) VALUES
    ('INTERESTED', 'Interested', 'Lead expressed interest in product/service', 0, 1, 3),
    ('NOT_INTERESTED', 'Not Interested', 'Lead not interested', 1, 0, NULL),
    ('CALLBACK', 'Callback Requested', 'Lead requested callback later', 0, 1, 1),
    ('DNC', 'Do Not Call', 'Lead requested to be added to DNC list', 1, 0, NULL),
    ('WRONG_NUMBER', 'Wrong Number', 'Phone number is incorrect', 1, 0, NULL),
    ('NO_ANSWER', 'No Answer', 'Call was not answered', 0, 0, NULL),
    ('BUSY', 'Busy', 'Line was busy', 0, 0, NULL),
    ('VOICEMAIL', 'Voicemail', 'Reached voicemail', 0, 1, 1),
    ('SALE', 'Sale Completed', 'Successful sale/conversion', 1, 0, NULL);

-- ============================================================================
-- DNC (Do Not Call) LIST
-- ============================================================================
CREATE TABLE IF NOT EXISTS dnc_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number TEXT NOT NULL UNIQUE,
    reason TEXT,
    added_by TEXT DEFAULT 'system',
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast DNC lookups
CREATE INDEX IF NOT EXISTS idx_dnc_phone ON dnc_list(phone_number);

-- ============================================================================
-- BOT INSTANCES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS bot_instances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    port INTEGER NOT NULL UNIQUE,
    status TEXT DEFAULT 'IDLE' CHECK(status IN ('IDLE', 'BUSY', 'OFFLINE')),
    current_call_uuid TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_health_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for bot status lookup
CREATE INDEX IF NOT EXISTS idx_bot_instances_status ON bot_instances(status);
CREATE INDEX IF NOT EXISTS idx_bot_instances_port ON bot_instances(port);

-- ============================================================================
-- VIEWS FOR REPORTING
-- ============================================================================

-- Today's statistics view
CREATE VIEW IF NOT EXISTS v_todays_stats AS
SELECT
    c.id as campaign_id,
    c.name as campaign_name,
    COUNT(DISTINCT cl.id) as total_calls,
    SUM(CASE WHEN cl.call_status = 'ANSWERED' THEN 1 ELSE 0 END) as answered,
    SUM(CASE WHEN cl.call_status = 'NO_ANSWER' THEN 1 ELSE 0 END) as no_answer,
    SUM(CASE WHEN cl.call_status = 'BUSY' THEN 1 ELSE 0 END) as busy,
    SUM(CASE WHEN cl.call_status = 'FAILED' THEN 1 ELSE 0 END) as failed,
    SUM(CASE WHEN cl.was_dropped = 1 THEN 1 ELSE 0 END) as dropped,
    ROUND(AVG(CASE WHEN cl.call_status = 'ANSWERED' THEN cl.duration_seconds END), 1) as avg_duration
FROM campaigns c
LEFT JOIN call_log cl ON c.id = cl.campaign_id
    AND DATE(cl.start_time) = DATE('now')
GROUP BY c.id, c.name;

-- Lead status summary view
CREATE VIEW IF NOT EXISTS v_lead_summary AS
SELECT
    c.id as campaign_id,
    c.name as campaign_name,
    COUNT(l.id) as total_leads,
    SUM(CASE WHEN l.status = 'NEW' THEN 1 ELSE 0 END) as new_leads,
    SUM(CASE WHEN l.status = 'CALLING' THEN 1 ELSE 0 END) as calling,
    SUM(CASE WHEN l.status = 'COMPLETED' THEN 1 ELSE 0 END) as completed,
    SUM(CASE WHEN l.status = 'CALLBACK' THEN 1 ELSE 0 END) as callbacks,
    SUM(CASE WHEN l.status = 'DNC' THEN 1 ELSE 0 END) as dnc,
    SUM(CASE WHEN l.status = 'FAILED' THEN 1 ELSE 0 END) as failed
FROM campaigns c
LEFT JOIN leads l ON c.id = l.campaign_id
GROUP BY c.id, c.name;

-- TCPA compliance view (30-day drop rate)
CREATE VIEW IF NOT EXISTS v_tcpa_compliance AS
SELECT
    c.id as campaign_id,
    c.name as campaign_name,
    COUNT(CASE WHEN cl.call_status = 'ANSWERED' THEN 1 END) as total_answered,
    COUNT(CASE WHEN cl.was_dropped = 1 THEN 1 END) as total_dropped,
    ROUND(
        CAST(COUNT(CASE WHEN cl.was_dropped = 1 THEN 1 END) AS REAL) /
        NULLIF(COUNT(CASE WHEN cl.call_status = 'ANSWERED' THEN 1 END), 0) * 100,
        2
    ) as drop_rate_percent
FROM campaigns c
LEFT JOIN call_log cl ON c.id = cl.campaign_id
    AND cl.start_time >= datetime('now', '-30 days')
GROUP BY c.id, c.name;

-- ============================================================================
-- TRIGGERS FOR AUTO-UPDATING TIMESTAMPS
-- ============================================================================

-- Update campaigns.updated_at on any change
CREATE TRIGGER IF NOT EXISTS update_campaigns_timestamp
AFTER UPDATE ON campaigns
FOR EACH ROW
BEGIN
    UPDATE campaigns SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Update leads.updated_at on any change
CREATE TRIGGER IF NOT EXISTS update_leads_timestamp
AFTER UPDATE ON leads
FOR EACH ROW
BEGIN
    UPDATE leads SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ============================================================================
-- DATABASE METADATA
-- ============================================================================

CREATE TABLE IF NOT EXISTS db_metadata (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT OR REPLACE INTO db_metadata (key, value) VALUES
    ('schema_version', '1.0'),
    ('created_at', datetime('now')),
    ('description', 'Exodus Dialer Database - Campaign Management and Call Tracking');
