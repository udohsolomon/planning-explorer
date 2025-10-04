-- ===========================================
-- Planning Explorer Comprehensive Database Schema
-- Supabase PostgreSQL Implementation
-- ===========================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ===========================================
-- USER MANAGEMENT TABLES
-- ===========================================

-- Enhanced user profiles with subscription management
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    company TEXT,
    role TEXT DEFAULT 'free' CHECK (role IN ('free', 'professional', 'enterprise', 'admin')),
    subscription_tier TEXT DEFAULT 'free' CHECK (subscription_tier IN ('free', 'professional', 'enterprise')),

    -- User preferences
    preferences JSONB DEFAULT '{}',

    -- Usage tracking
    api_calls_this_month INTEGER DEFAULT 0,
    searches_this_month INTEGER DEFAULT 0,
    reports_generated INTEGER DEFAULT 0,

    -- Subscription limits
    max_api_calls_per_month INTEGER DEFAULT 1000,
    max_saved_searches INTEGER DEFAULT 10,
    max_alerts INTEGER DEFAULT 5,

    -- User state
    onboarding_completed BOOLEAN DEFAULT false,
    email_verified BOOLEAN DEFAULT false,

    -- Timestamps
    last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User application settings
CREATE TABLE IF NOT EXISTS user_settings (
    user_id UUID PRIMARY KEY REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Search preferences
    default_search_radius DECIMAL(5,2) DEFAULT 5.0,
    preferred_authorities TEXT[] DEFAULT '{}',
    default_filters JSONB DEFAULT '{}',

    -- Display preferences
    results_per_page INTEGER DEFAULT 20 CHECK (results_per_page BETWEEN 5 AND 100),
    show_ai_insights BOOLEAN DEFAULT true,
    show_opportunity_scores BOOLEAN DEFAULT true,

    -- Map preferences
    map_view TEXT DEFAULT 'satellite' CHECK (map_view IN ('satellite', 'roadmap', 'hybrid', 'terrain')),
    show_heat_map BOOLEAN DEFAULT true,

    -- Notification preferences
    email_notifications BOOLEAN DEFAULT true,
    push_notifications BOOLEAN DEFAULT true,
    marketing_emails BOOLEAN DEFAULT false,

    -- Alert preferences
    daily_digest_enabled BOOLEAN DEFAULT true,
    weekly_summary_enabled BOOLEAN DEFAULT true,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===========================================
-- SAVED SEARCHES WITH AI ENHANCEMENT
-- ===========================================

CREATE TABLE IF NOT EXISTS saved_searches (
    search_id TEXT PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Search metadata
    name TEXT NOT NULL CHECK (length(name) >= 1 AND length(name) <= 100),
    description TEXT CHECK (length(description) <= 500),
    category TEXT DEFAULT 'general',

    -- Search parameters
    query TEXT,
    filters JSONB DEFAULT '{}',
    sort_by TEXT,
    sort_order TEXT DEFAULT 'desc' CHECK (sort_order IN ('asc', 'desc')),

    -- AI enhancements
    ai_suggestions JSONB DEFAULT '{}',
    ai_insights JSONB DEFAULT '{}',
    ai_confidence_score DECIMAL(3,2),

    -- Usage tracking
    last_used TIMESTAMP WITH TIME ZONE,
    use_count INTEGER DEFAULT 0,
    avg_results_count INTEGER DEFAULT 0,

    -- User preferences
    is_favorite BOOLEAN DEFAULT false,
    is_shared BOOLEAN DEFAULT false,
    share_token TEXT UNIQUE,

    -- Alert conversion
    converted_to_alert BOOLEAN DEFAULT false,
    alert_id TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_saved_searches_user_id ON saved_searches(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_searches_category ON saved_searches(category);
CREATE INDEX IF NOT EXISTS idx_saved_searches_last_used ON saved_searches(last_used DESC);

-- ===========================================
-- SMART ALERTS SYSTEM
-- ===========================================

CREATE TABLE IF NOT EXISTS user_alerts (
    alert_id TEXT PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    saved_search_id TEXT REFERENCES saved_searches(search_id) ON DELETE SET NULL,

    -- Alert metadata
    name TEXT NOT NULL CHECK (length(name) >= 1 AND length(name) <= 100),
    description TEXT CHECK (length(description) <= 500),

    -- Alert criteria
    query TEXT,
    filters JSONB DEFAULT '{}',
    location_filters JSONB DEFAULT '{}',
    ai_criteria JSONB DEFAULT '{}',

    -- Smart features
    ai_enhanced BOOLEAN DEFAULT false,
    smart_filtering BOOLEAN DEFAULT true,
    min_relevance_score DECIMAL(3,2) DEFAULT 0.5,

    -- Notification settings
    frequency TEXT DEFAULT 'daily' CHECK (frequency IN ('immediate', 'daily', 'weekly', 'monthly')),
    email_enabled BOOLEAN DEFAULT true,
    push_enabled BOOLEAN DEFAULT true,
    digest_enabled BOOLEAN DEFAULT true,

    -- Scheduling
    next_check TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_triggered TIMESTAMP WITH TIME ZONE,
    last_notification_sent TIMESTAMP WITH TIME ZONE,

    -- Status and metrics
    is_active BOOLEAN DEFAULT true,
    trigger_count INTEGER DEFAULT 0,
    false_positive_count INTEGER DEFAULT 0,
    user_feedback_score DECIMAL(3,2),

    -- Performance tracking
    avg_results_per_trigger INTEGER DEFAULT 0,
    total_notifications_sent INTEGER DEFAULT 0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Alert triggers and notifications
CREATE TABLE IF NOT EXISTS alert_triggers (
    trigger_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    alert_id TEXT REFERENCES user_alerts(alert_id) ON DELETE CASCADE,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Trigger details
    new_applications TEXT[] DEFAULT '{}',
    trigger_reason TEXT NOT NULL,
    relevance_scores JSONB DEFAULT '{}',
    ai_summary TEXT,

    -- Notification status
    notification_sent BOOLEAN DEFAULT false,
    notification_method TEXT[] DEFAULT '{}',
    notification_sent_at TIMESTAMP WITH TIME ZONE,

    -- User interaction
    viewed BOOLEAN DEFAULT false,
    clicked BOOLEAN DEFAULT false,
    user_rating INTEGER CHECK (user_rating BETWEEN 1 AND 5),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_user_alerts_user_id ON user_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_user_alerts_next_check ON user_alerts(next_check) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_alert_triggers_alert_id ON alert_triggers(alert_id);

-- ===========================================
-- REPORTS AND ANALYTICS SYSTEM
-- ===========================================

CREATE TABLE IF NOT EXISTS user_reports (
    report_id TEXT PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Report metadata
    name TEXT NOT NULL CHECK (length(name) >= 1 AND length(name) <= 100),
    description TEXT CHECK (length(description) <= 500),
    report_type TEXT NOT NULL CHECK (report_type IN ('market_analysis', 'opportunity_report', 'geographic_analysis', 'developer_profile', 'authority_performance', 'trend_analysis', 'custom')),
    template_id TEXT,

    -- Report parameters
    query TEXT,
    filters JSONB DEFAULT '{}',
    date_range JSONB DEFAULT '{}',
    location JSONB DEFAULT '{}',
    parameters JSONB DEFAULT '{}',

    -- Generation status
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'generating', 'completed', 'failed', 'expired')),
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage BETWEEN 0 AND 100),

    -- Content and files
    content JSONB DEFAULT '{}',
    summary TEXT,
    executive_summary TEXT,
    key_insights TEXT[],
    file_url TEXT,
    file_format TEXT DEFAULT 'pdf' CHECK (file_format IN ('pdf', 'excel', 'json', 'csv')),
    file_size_bytes BIGINT,

    -- AI analysis
    ai_generated BOOLEAN DEFAULT true,
    ai_model_used TEXT,
    ai_confidence_score DECIMAL(3,2),

    -- Performance metrics
    applications_analyzed INTEGER DEFAULT 0,
    data_points_processed INTEGER DEFAULT 0,
    generation_time_seconds DECIMAL(8,2),

    -- Sharing and access
    is_public BOOLEAN DEFAULT false,
    share_token TEXT UNIQUE,
    download_count INTEGER DEFAULT 0,

    -- Expiration and cleanup
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days'),
    auto_delete BOOLEAN DEFAULT true,

    -- Error handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    downloaded_at TIMESTAMP WITH TIME ZONE
);

-- Report templates for standardized reports
CREATE TABLE IF NOT EXISTS report_templates (
    template_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    report_type TEXT NOT NULL,
    template_content JSONB NOT NULL,
    parameters_schema JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES user_profiles(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_user_reports_user_id ON user_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_user_reports_status ON user_reports(status);
CREATE INDEX IF NOT EXISTS idx_user_reports_expires_at ON user_reports(expires_at);

-- ===========================================
-- AI PERSONALIZATION ENGINE
-- ===========================================

CREATE TABLE IF NOT EXISTS user_ai_preferences (
    preference_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Preference details
    preference_type TEXT NOT NULL CHECK (preference_type IN ('search_pattern', 'location_interest', 'application_type', 'developer_interest', 'content_preference', 'timing_pattern')),
    preference_data JSONB NOT NULL,

    -- AI metrics
    confidence_score DECIMAL(3,2) NOT NULL CHECK (confidence_score BETWEEN 0 AND 1),
    relevance_score DECIMAL(3,2) DEFAULT 0.5,
    usage_frequency INTEGER DEFAULT 1,

    -- Validation
    validated_by_user BOOLEAN DEFAULT false,
    user_feedback TEXT CHECK (user_feedback IN ('positive', 'negative', 'neutral')),

    -- Lifecycle
    is_active BOOLEAN DEFAULT true,
    last_used TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '90 days'),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User behavior tracking for AI learning
CREATE TABLE IF NOT EXISTS user_interactions (
    interaction_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Interaction details
    interaction_type TEXT NOT NULL CHECK (interaction_type IN ('search', 'view', 'save', 'alert_create', 'report_generate', 'click', 'download', 'share')),
    entity_type TEXT CHECK (entity_type IN ('application', 'search', 'report', 'alert')),
    entity_id TEXT,

    -- Context
    context_data JSONB DEFAULT '{}',
    search_query TEXT,
    filters_used JSONB DEFAULT '{}',

    -- Timing and session
    session_id TEXT,
    duration_seconds INTEGER,
    timestamp_utc TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- User feedback implicit signals
    result_clicked BOOLEAN DEFAULT false,
    time_spent_seconds INTEGER,
    scroll_depth_percentage INTEGER,

    -- Device and location context
    user_agent TEXT,
    ip_address INET,
    device_type TEXT,
    location_lat DECIMAL(10,8),
    location_lng DECIMAL(11,8),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for AI processing
CREATE INDEX IF NOT EXISTS idx_user_ai_preferences_user_id ON user_ai_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_user_ai_preferences_type ON user_ai_preferences(preference_type);
CREATE INDEX IF NOT EXISTS idx_user_interactions_user_id ON user_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_interactions_type ON user_interactions(interaction_type);
CREATE INDEX IF NOT EXISTS idx_user_interactions_timestamp ON user_interactions(timestamp_utc DESC);

-- ===========================================
-- NOTIFICATION SYSTEM
-- ===========================================

CREATE TABLE IF NOT EXISTS user_notifications (
    notification_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Notification content
    type TEXT NOT NULL CHECK (type IN ('alert', 'report_ready', 'system', 'marketing', 'digest', 'welcome', 'upgrade')),
    title TEXT NOT NULL CHECK (length(title) <= 200),
    message TEXT CHECK (length(message) <= 1000),
    data JSONB DEFAULT '{}',

    -- Delivery settings
    delivery_method TEXT DEFAULT 'in_app' CHECK (delivery_method IN ('in_app', 'email', 'push', 'sms')),
    priority TEXT DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),

    -- Status tracking
    is_read BOOLEAN DEFAULT false,
    is_sent BOOLEAN DEFAULT false,
    sent_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,

    -- Related entities
    related_entity_type TEXT,
    related_entity_id TEXT,

    -- Scheduling
    scheduled_for TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days'),

    -- Delivery tracking
    delivery_attempts INTEGER DEFAULT 0,
    delivery_status TEXT DEFAULT 'pending' CHECK (delivery_status IN ('pending', 'sent', 'failed', 'expired')),
    error_message TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Notification templates
CREATE TABLE IF NOT EXISTS notification_templates (
    template_id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    name TEXT NOT NULL,
    subject_template TEXT,
    body_template TEXT NOT NULL,
    data_schema JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_user_notifications_user_id ON user_notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_user_notifications_unread ON user_notifications(user_id, is_read, created_at DESC) WHERE is_read = false;
CREATE INDEX IF NOT EXISTS idx_user_notifications_scheduled ON user_notifications(scheduled_for) WHERE delivery_status = 'pending';

-- ===========================================
-- API USAGE AND BILLING TRACKING
-- ===========================================

CREATE TABLE IF NOT EXISTS api_usage (
    usage_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Request details
    endpoint TEXT NOT NULL,
    method TEXT NOT NULL CHECK (method IN ('GET', 'POST', 'PUT', 'DELETE', 'PATCH')),
    query_parameters JSONB DEFAULT '{}',
    request_size_bytes INTEGER,

    -- Response details
    response_time_ms INTEGER NOT NULL,
    response_status INTEGER NOT NULL,
    response_size_bytes INTEGER,
    results_returned INTEGER,

    -- Billing and limits
    billable BOOLEAN DEFAULT true,
    cost_credits DECIMAL(10,4) DEFAULT 0.0,
    tier_at_time TEXT NOT NULL,

    -- Performance metrics
    cache_hit BOOLEAN DEFAULT false,
    processing_time_ms INTEGER,

    -- Context
    user_agent TEXT,
    ip_address INET,
    session_id TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Monthly usage aggregation for performance
CREATE TABLE IF NOT EXISTS monthly_usage_summary (
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),

    -- Usage counts
    total_api_calls INTEGER DEFAULT 0,
    billable_api_calls INTEGER DEFAULT 0,
    total_credits_used DECIMAL(10,4) DEFAULT 0.0,

    -- Performance metrics
    avg_response_time_ms DECIMAL(8,2),
    cache_hit_rate DECIMAL(5,4),

    -- Feature usage
    searches_performed INTEGER DEFAULT 0,
    reports_generated INTEGER DEFAULT 0,
    alerts_triggered INTEGER DEFAULT 0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    PRIMARY KEY (user_id, year, month)
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_api_usage_user_id ON api_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_api_usage_created_at ON api_usage(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_monthly_usage_summary_date ON monthly_usage_summary(year DESC, month DESC);

-- ===========================================
-- SYSTEM TABLES
-- ===========================================

-- Application configuration
CREATE TABLE IF NOT EXISTS app_config (
    config_key TEXT PRIMARY KEY,
    config_value JSONB NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- System events and audit log
CREATE TABLE IF NOT EXISTS system_events (
    event_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    event_type TEXT NOT NULL,
    entity_type TEXT,
    entity_id TEXT,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE SET NULL,
    event_data JSONB DEFAULT '{}',
    severity TEXT DEFAULT 'info' CHECK (severity IN ('debug', 'info', 'warning', 'error', 'critical')),
    source TEXT DEFAULT 'api',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for system monitoring
CREATE INDEX IF NOT EXISTS idx_system_events_type ON system_events(event_type);
CREATE INDEX IF NOT EXISTS idx_system_events_created_at ON system_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_system_events_severity ON system_events(severity, created_at DESC);

-- ===========================================
-- ROW LEVEL SECURITY POLICIES
-- ===========================================

-- Enable RLS on all user-specific tables
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE saved_searches ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE alert_triggers ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_ai_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE monthly_usage_summary ENABLE ROW LEVEL SECURITY;

-- User profile policies
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = user_id);

-- Saved searches policies
CREATE POLICY "Users can manage own saved searches" ON saved_searches
    FOR ALL USING (auth.uid() = user_id);

-- User alerts policies
CREATE POLICY "Users can manage own alerts" ON user_alerts
    FOR ALL USING (auth.uid() = user_id);

-- User reports policies
CREATE POLICY "Users can manage own reports" ON user_reports
    FOR ALL USING (auth.uid() = user_id);

-- User notifications policies
CREATE POLICY "Users can view own notifications" ON user_notifications
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own notifications" ON user_notifications
    FOR UPDATE USING (auth.uid() = user_id);

-- API usage policies
CREATE POLICY "Users can view own usage" ON api_usage
    FOR SELECT USING (auth.uid() = user_id);

-- Admin policies (for users with admin role)
CREATE POLICY "Admins can view all data" ON user_profiles
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_profiles
            WHERE user_id = auth.uid() AND role = 'admin'
        )
    );

-- ===========================================
-- FUNCTIONS AND TRIGGERS
-- ===========================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to relevant tables
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_settings_updated_at BEFORE UPDATE ON user_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_saved_searches_updated_at BEFORE UPDATE ON saved_searches
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_alerts_updated_at BEFORE UPDATE ON user_alerts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_reports_updated_at BEFORE UPDATE ON user_reports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to automatically update user usage statistics
CREATE OR REPLACE FUNCTION update_user_usage_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Update user profile usage counters
    UPDATE user_profiles
    SET
        api_calls_this_month = api_calls_this_month + 1,
        last_active = NOW()
    WHERE user_id = NEW.user_id;

    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for API usage tracking
CREATE TRIGGER update_usage_stats AFTER INSERT ON api_usage
    FOR EACH ROW EXECUTE FUNCTION update_user_usage_stats();

-- Function to clean up expired data
CREATE OR REPLACE FUNCTION cleanup_expired_data()
RETURNS void AS $$
BEGIN
    -- Delete expired reports
    DELETE FROM user_reports
    WHERE expires_at < NOW() AND auto_delete = true;

    -- Delete expired notifications
    DELETE FROM user_notifications
    WHERE expires_at < NOW();

    -- Delete old AI preferences
    DELETE FROM user_ai_preferences
    WHERE expires_at < NOW() AND is_active = false;

    -- Delete old interaction data (keep 1 year)
    DELETE FROM user_interactions
    WHERE created_at < NOW() - INTERVAL '1 year';

    -- Delete old API usage data (keep 2 years)
    DELETE FROM api_usage
    WHERE created_at < NOW() - INTERVAL '2 years';
END;
$$ language 'plpgsql';

-- ===========================================
-- INITIAL DATA SEEDING
-- ===========================================

-- Insert default notification templates
INSERT INTO notification_templates (template_id, type, name, subject_template, body_template) VALUES
('welcome', 'welcome', 'Welcome Email', 'Welcome to Planning Explorer!', 'Welcome to Planning Explorer! We''re excited to have you on board.'),
('alert_triggered', 'alert', 'Alert Notification', 'New planning applications found', 'Your alert "{{alert_name}}" has found {{count}} new planning applications.'),
('report_ready', 'report_ready', 'Report Ready', 'Your report is ready', 'Your report "{{report_name}}" has been generated and is ready for download.'),
('daily_digest', 'digest', 'Daily Digest', 'Your daily planning digest', 'Here''s your daily summary of planning activity.'),
('upgrade_reminder', 'upgrade', 'Upgrade Reminder', 'Upgrade your Planning Explorer account', 'You''re approaching your plan limits. Consider upgrading for more features.');

-- Insert default report templates
INSERT INTO report_templates (template_id, name, description, report_type, template_content) VALUES
('market_analysis_basic', 'Basic Market Analysis', 'Standard market analysis report', 'market_analysis', '{"sections": ["summary", "trends", "statistics"]}'),
('opportunity_report_standard', 'Standard Opportunity Report', 'AI-powered opportunity analysis', 'opportunity_report', '{"sections": ["executive_summary", "opportunities", "risks", "recommendations"]}'),
('geographic_analysis_standard', 'Geographic Analysis', 'Location-based planning analysis', 'geographic_analysis', '{"sections": ["area_overview", "planning_activity", "development_patterns"]}');

-- Insert default app configuration
INSERT INTO app_config (config_key, config_value, description, is_public) VALUES
('feature_flags', '{"ai_personalization": true, "real_time_notifications": true, "advanced_reports": true}', 'Feature flags for enabling/disabling features', false),
('subscription_tiers', '{"free": {"api_calls": 1000, "saved_searches": 10, "alerts": 5}, "professional": {"api_calls": 10000, "saved_searches": 100, "alerts": 50}, "enterprise": {"api_calls": 100000, "saved_searches": 1000, "alerts": 500}}', 'Subscription tier limits', true),
('ai_settings', '{"min_confidence_threshold": 0.5, "personalization_enabled": true, "auto_suggestions": true}', 'AI system configuration', false);

-- ===========================================
-- PERFORMANCE OPTIMIZATIONS
-- ===========================================

-- Partial indexes for active records
CREATE INDEX IF NOT EXISTS idx_active_alerts ON user_alerts(user_id, next_check) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_pending_notifications ON user_notifications(scheduled_for) WHERE delivery_status = 'pending';
CREATE INDEX IF NOT EXISTS idx_active_ai_preferences ON user_ai_preferences(user_id, preference_type) WHERE is_active = true;

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_user_reports_user_status ON user_reports(user_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_saved_searches_user_category ON saved_searches(user_id, category, last_used DESC);
CREATE INDEX IF NOT EXISTS idx_api_usage_user_date ON api_usage(user_id, created_at DESC);

-- ===========================================
-- COMMENTS FOR DOCUMENTATION
-- ===========================================

COMMENT ON TABLE user_profiles IS 'Enhanced user profiles with subscription management and usage tracking';
COMMENT ON TABLE saved_searches IS 'User saved searches with AI enhancement and alert conversion';
COMMENT ON TABLE user_alerts IS 'Smart alerts system with AI-powered filtering and notifications';
COMMENT ON TABLE user_reports IS 'AI-generated reports and analytics with comprehensive metadata';
COMMENT ON TABLE user_ai_preferences IS 'AI personalization engine data and user preferences';
COMMENT ON TABLE user_notifications IS 'Comprehensive notification system with multiple delivery methods';
COMMENT ON TABLE api_usage IS 'Detailed API usage tracking for billing and analytics';

-- ===========================================
-- COMPLETION
-- ===========================================

-- Grant permissions to authenticated users
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Planning Explorer database schema created successfully!';
    RAISE NOTICE 'Tables created: %', (
        SELECT count(*)
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name LIKE 'user_%'
        OR table_name IN ('saved_searches', 'alert_triggers', 'api_usage', 'monthly_usage_summary', 'notification_templates', 'report_templates', 'app_config', 'system_events')
    );
END $$;