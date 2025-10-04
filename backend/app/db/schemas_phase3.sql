-- ==========================================
-- Planning Explorer Phase 3 Complete Database Schema
-- Supabase PostgreSQL Implementation with AI Features
-- ==========================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ==========================================
-- ENHANCED USER MANAGEMENT TABLES
-- ==========================================

-- Enhanced user profiles with subscription management and AI features
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    company TEXT,
    role TEXT DEFAULT 'free' CHECK (role IN ('free', 'professional', 'enterprise', 'admin')),
    subscription_tier TEXT DEFAULT 'free' CHECK (subscription_tier IN ('free', 'professional', 'enterprise')),

    -- User preferences and personalization
    preferences JSONB DEFAULT '{}',
    ai_preferences JSONB DEFAULT '{}',
    personalization_enabled BOOLEAN DEFAULT true,

    -- Usage tracking and limits
    api_calls_this_month INTEGER DEFAULT 0,
    searches_this_month INTEGER DEFAULT 0,
    reports_generated INTEGER DEFAULT 0,
    max_api_calls_per_month INTEGER DEFAULT 1000,
    max_saved_searches INTEGER DEFAULT 10,
    max_alerts INTEGER DEFAULT 5,

    -- User state and onboarding
    onboarding_completed BOOLEAN DEFAULT false,
    onboarding_step INTEGER DEFAULT 0,
    onboarding_data JSONB DEFAULT '{}',
    email_verified BOOLEAN DEFAULT false,
    terms_accepted_at TIMESTAMP WITH TIME ZONE,

    -- Activity and engagement
    last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    login_count INTEGER DEFAULT 0,
    engagement_score DECIMAL(5,2) DEFAULT 0.0,

    -- AI learning metrics
    ai_interaction_count INTEGER DEFAULT 0,
    ai_feedback_score DECIMAL(3,2) DEFAULT 0.0,
    user_segment TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User application settings with AI preferences
CREATE TABLE IF NOT EXISTS user_settings (
    user_id UUID PRIMARY KEY REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Search preferences
    default_search_radius DECIMAL(5,2) DEFAULT 5.0,
    preferred_authorities TEXT[] DEFAULT '{}',
    default_filters JSONB DEFAULT '{}',
    search_history_enabled BOOLEAN DEFAULT true,

    -- AI and personalization preferences
    ai_suggestions_enabled BOOLEAN DEFAULT true,
    ai_insights_enabled BOOLEAN DEFAULT true,
    auto_recommendations BOOLEAN DEFAULT true,
    personalization_level TEXT DEFAULT 'medium' CHECK (personalization_level IN ('low', 'medium', 'high')),

    -- Display preferences
    results_per_page INTEGER DEFAULT 20 CHECK (results_per_page BETWEEN 5 AND 100),
    show_ai_insights BOOLEAN DEFAULT true,
    show_opportunity_scores BOOLEAN DEFAULT true,
    show_trend_analysis BOOLEAN DEFAULT true,

    -- Map preferences
    map_view TEXT DEFAULT 'satellite' CHECK (map_view IN ('satellite', 'roadmap', 'hybrid', 'terrain')),
    show_heat_map BOOLEAN DEFAULT true,
    show_clustering BOOLEAN DEFAULT true,

    -- Notification preferences
    email_notifications BOOLEAN DEFAULT true,
    push_notifications BOOLEAN DEFAULT true,
    marketing_emails BOOLEAN DEFAULT false,
    ai_digest_enabled BOOLEAN DEFAULT true,

    -- Alert preferences
    daily_digest_enabled BOOLEAN DEFAULT true,
    weekly_summary_enabled BOOLEAN DEFAULT true,
    smart_alert_filtering BOOLEAN DEFAULT true,

    -- Privacy preferences
    data_sharing_enabled BOOLEAN DEFAULT false,
    analytics_tracking BOOLEAN DEFAULT true,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- SAVED SEARCHES WITH AI ENHANCEMENT
-- ==========================================

CREATE TABLE IF NOT EXISTS saved_searches (
    search_id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Search metadata
    name TEXT NOT NULL CHECK (length(name) >= 1 AND length(name) <= 100),
    description TEXT CHECK (length(description) <= 500),
    category TEXT DEFAULT 'general',
    tags TEXT[] DEFAULT '{}',

    -- Search parameters
    query TEXT,
    filters JSONB DEFAULT '{}',
    location_filters JSONB DEFAULT '{}',
    sort_by TEXT,
    sort_order TEXT DEFAULT 'desc' CHECK (sort_order IN ('asc', 'desc')),

    -- AI enhancements
    ai_suggestions JSONB DEFAULT '{}',
    ai_insights JSONB DEFAULT '{}',
    ai_confidence_score DECIMAL(3,2),
    ai_enhanced BOOLEAN DEFAULT false,

    -- Usage tracking and performance
    last_used TIMESTAMP WITH TIME ZONE,
    use_count INTEGER DEFAULT 0,
    avg_results_count INTEGER DEFAULT 0,
    avg_response_time_ms INTEGER DEFAULT 0,

    -- User preferences and sharing
    is_favorite BOOLEAN DEFAULT false,
    is_public BOOLEAN DEFAULT false,
    share_token TEXT UNIQUE,
    shared_count INTEGER DEFAULT 0,

    -- Alert conversion and automation
    converted_to_alert BOOLEAN DEFAULT false,
    alert_id TEXT,
    auto_alert_suggested BOOLEAN DEFAULT false,

    -- Performance metrics
    cache_enabled BOOLEAN DEFAULT true,
    last_cache_update TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- SMART ALERTS SYSTEM WITH AI
-- ==========================================

CREATE TABLE IF NOT EXISTS user_alerts (
    alert_id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    saved_search_id TEXT REFERENCES saved_searches(search_id) ON DELETE SET NULL,

    -- Alert metadata
    name TEXT NOT NULL CHECK (length(name) >= 1 AND length(name) <= 100),
    description TEXT CHECK (length(description) <= 500),
    category TEXT DEFAULT 'general',

    -- Alert criteria
    query TEXT,
    filters JSONB DEFAULT '{}',
    location_filters JSONB DEFAULT '{}',
    ai_criteria JSONB DEFAULT '{}',

    -- AI-powered smart features
    ai_enhanced BOOLEAN DEFAULT false,
    smart_filtering BOOLEAN DEFAULT true,
    min_relevance_score DECIMAL(3,2) DEFAULT 0.5,
    ai_learning_enabled BOOLEAN DEFAULT true,

    -- Notification settings
    frequency TEXT DEFAULT 'daily' CHECK (frequency IN ('instant', 'daily', 'weekly', 'monthly')),
    email_enabled BOOLEAN DEFAULT true,
    push_enabled BOOLEAN DEFAULT true,
    digest_enabled BOOLEAN DEFAULT true,
    max_results_per_notification INTEGER DEFAULT 10,

    -- Scheduling and timing
    next_check TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    check_interval_minutes INTEGER DEFAULT 1440,
    last_triggered TIMESTAMP WITH TIME ZONE,
    last_notification_sent TIMESTAMP WITH TIME ZONE,

    -- Status and performance
    is_active BOOLEAN DEFAULT true,
    trigger_count INTEGER DEFAULT 0,
    false_positive_count INTEGER DEFAULT 0,
    user_feedback_score DECIMAL(3,2),
    effectiveness_score DECIMAL(3,2) DEFAULT 0.5,

    -- AI learning metrics
    ai_accuracy_score DECIMAL(3,2),
    user_satisfaction_score DECIMAL(3,2),
    avg_results_per_trigger INTEGER DEFAULT 0,
    total_notifications_sent INTEGER DEFAULT 0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Alert triggers and notifications with AI analysis
CREATE TABLE IF NOT EXISTS alert_triggers (
    trigger_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    alert_id TEXT REFERENCES user_alerts(alert_id) ON DELETE CASCADE,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Trigger details
    new_applications TEXT[] DEFAULT '{}',
    trigger_reason TEXT NOT NULL,
    ai_analysis JSONB DEFAULT '{}',
    relevance_scores JSONB DEFAULT '{}',
    opportunity_scores JSONB DEFAULT '{}',
    ai_summary TEXT,

    -- Notification status
    notification_sent BOOLEAN DEFAULT false,
    notification_method TEXT[] DEFAULT '{}',
    notification_sent_at TIMESTAMP WITH TIME ZONE,
    notification_data JSONB DEFAULT '{}',

    -- User interaction tracking
    viewed BOOLEAN DEFAULT false,
    viewed_at TIMESTAMP WITH TIME ZONE,
    clicked BOOLEAN DEFAULT false,
    clicked_at TIMESTAMP WITH TIME ZONE,
    user_rating INTEGER CHECK (user_rating BETWEEN 1 AND 5),
    user_feedback TEXT,

    -- AI metrics
    ai_confidence DECIMAL(3,2),
    predicted_user_interest DECIMAL(3,2),
    actual_user_engagement DECIMAL(3,2),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- REPORTS AND ANALYTICS WITH AI
-- ==========================================

CREATE TABLE IF NOT EXISTS user_reports (
    report_id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Report metadata
    name TEXT NOT NULL CHECK (length(name) >= 1 AND length(name) <= 100),
    description TEXT CHECK (length(description) <= 500),
    report_type TEXT NOT NULL CHECK (report_type IN ('market_analysis', 'opportunity_report', 'geographic_analysis', 'developer_profile', 'authority_performance', 'trend_analysis', 'ai_insights', 'custom')),
    template_id TEXT,

    -- Report parameters
    query TEXT,
    filters JSONB DEFAULT '{}',
    date_range JSONB DEFAULT '{}',
    location JSONB DEFAULT '{}',
    parameters JSONB DEFAULT '{}',

    -- Generation status
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'expired')),
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage BETWEEN 0 AND 100),
    processing_stages JSONB DEFAULT '[]',

    -- Content and analysis
    content JSONB DEFAULT '{}',
    summary TEXT,
    executive_summary TEXT,
    key_insights TEXT[],
    ai_insights JSONB DEFAULT '{}',
    recommendations TEXT[],

    -- File management
    file_url TEXT,
    file_format TEXT DEFAULT 'pdf' CHECK (file_format IN ('pdf', 'excel', 'json', 'csv')),
    file_size_bytes BIGINT,
    file_path TEXT,

    -- AI analysis
    ai_generated BOOLEAN DEFAULT true,
    ai_model_used TEXT,
    ai_confidence_score DECIMAL(3,2),
    ai_processing_time_seconds DECIMAL(8,2),

    -- Performance metrics
    applications_analyzed INTEGER DEFAULT 0,
    data_points_processed INTEGER DEFAULT 0,
    generation_time_seconds DECIMAL(8,2),
    data_quality_score DECIMAL(3,2),

    -- Sharing and access
    is_public BOOLEAN DEFAULT false,
    share_token TEXT UNIQUE,
    download_count INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,

    -- Expiration and cleanup
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days'),
    auto_delete BOOLEAN DEFAULT true,

    -- Error handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    downloaded_at TIMESTAMP WITH TIME ZONE
);

-- ==========================================
-- AI PERSONALIZATION ENGINE
-- ==========================================

CREATE TABLE IF NOT EXISTS user_ai_preferences (
    preference_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Preference details
    preference_type TEXT NOT NULL CHECK (preference_type IN ('search_pattern', 'location_interest', 'application_type', 'developer_interest', 'content_preference', 'timing_pattern', 'geographic_focus', 'industry_focus')),
    preference_data JSONB NOT NULL,
    preference_source TEXT DEFAULT 'system' CHECK (preference_source IN ('explicit', 'implicit', 'system')),

    -- AI metrics
    confidence_score DECIMAL(3,2) NOT NULL CHECK (confidence_score BETWEEN 0 AND 1),
    relevance_score DECIMAL(3,2) DEFAULT 0.5,
    usage_frequency INTEGER DEFAULT 1,
    decay_factor DECIMAL(3,2) DEFAULT 0.95,

    -- Validation and feedback
    validated_by_user BOOLEAN DEFAULT false,
    user_feedback TEXT CHECK (user_feedback IN ('positive', 'negative', 'neutral')),
    feedback_count INTEGER DEFAULT 0,

    -- Lifecycle management
    is_active BOOLEAN DEFAULT true,
    last_used TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '90 days'),
    auto_renewal BOOLEAN DEFAULT true,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User behavior tracking for advanced AI learning
CREATE TABLE IF NOT EXISTS user_interactions (
    interaction_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Interaction details
    interaction_type TEXT NOT NULL CHECK (interaction_type IN ('search', 'view', 'save', 'alert_create', 'report_generate', 'click', 'download', 'share', 'feedback', 'bookmark')),
    entity_type TEXT CHECK (entity_type IN ('application', 'search', 'report', 'alert', 'recommendation')),
    entity_id TEXT,

    -- Context and environment
    context_data JSONB DEFAULT '{}',
    search_query TEXT,
    filters_used JSONB DEFAULT '{}',
    page_context TEXT,
    user_journey_stage TEXT,

    -- Timing and session tracking
    session_id TEXT,
    duration_seconds INTEGER,
    timestamp_utc TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sequence_number INTEGER,

    -- User behavior signals
    result_clicked BOOLEAN DEFAULT false,
    time_spent_seconds INTEGER,
    scroll_depth_percentage INTEGER,
    mouse_movement_data JSONB DEFAULT '{}',
    attention_score DECIMAL(3,2),

    -- Device and environment context
    user_agent TEXT,
    ip_address INET,
    device_type TEXT,
    screen_resolution TEXT,
    location_lat DECIMAL(10,8),
    location_lng DECIMAL(11,8),
    timezone TEXT,

    -- AI processing flags
    processed_for_ml BOOLEAN DEFAULT false,
    ai_weight DECIMAL(3,2) DEFAULT 1.0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User behavior profiles for advanced AI
CREATE TABLE IF NOT EXISTS user_behavior_profiles (
    profile_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Behavior analysis
    behavior_data JSONB DEFAULT '{}',
    engagement_score DECIMAL(5,2) DEFAULT 0.0,
    activity_patterns JSONB DEFAULT '{}',
    search_patterns JSONB DEFAULT '{}',
    temporal_patterns JSONB DEFAULT '{}',
    geographic_patterns JSONB DEFAULT '{}',

    -- User segmentation
    user_segment TEXT,
    segment_confidence DECIMAL(3,2),
    persona_type TEXT,
    experience_level TEXT CHECK (experience_level IN ('beginner', 'intermediate', 'advanced', 'expert')),

    -- Predictive metrics
    churn_risk_score DECIMAL(3,2),
    upgrade_propensity DECIMAL(3,2),
    feature_adoption_score DECIMAL(3,2),
    content_affinity_scores JSONB DEFAULT '{}',

    -- Model versioning
    profile_version INTEGER DEFAULT 1,
    model_version TEXT,
    last_model_update TIMESTAMP WITH TIME ZONE,

    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI-generated recommendations
CREATE TABLE IF NOT EXISTS user_recommendations (
    recommendation_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Recommendation details
    recommendation_type TEXT NOT NULL CHECK (recommendation_type IN ('search_suggestion', 'alert_suggestion', 'content_suggestion', 'feature_suggestion', 'upgrade_suggestion', 'location_suggestion')),
    title TEXT NOT NULL,
    description TEXT,
    content JSONB DEFAULT '{}',
    action_data JSONB DEFAULT '{}',

    -- AI metrics
    confidence_score DECIMAL(3,2) DEFAULT 0.0 CHECK (confidence_score BETWEEN 0 AND 1),
    relevance_score DECIMAL(3,2) DEFAULT 0.0,
    priority_score DECIMAL(3,2) DEFAULT 0.5,
    predicted_ctr DECIMAL(3,2),

    -- User interaction tracking
    is_viewed BOOLEAN DEFAULT false,
    viewed_at TIMESTAMP WITH TIME ZONE,
    is_acted_upon BOOLEAN DEFAULT false,
    action_taken_at TIMESTAMP WITH TIME ZONE,
    user_feedback TEXT CHECK (user_feedback IN ('positive', 'negative', 'neutral', 'dismissed')),
    feedback_at TIMESTAMP WITH TIME ZONE,

    -- Recommendation context
    context_data JSONB DEFAULT '{}',
    trigger_event TEXT,
    recommendation_source TEXT,

    -- Lifecycle management
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '7 days'),
    is_persistent BOOLEAN DEFAULT false,
    display_count INTEGER DEFAULT 0,
    max_displays INTEGER DEFAULT 3,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User feedback for AI learning
CREATE TABLE IF NOT EXISTS user_feedback (
    feedback_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Feedback details
    feedback_type TEXT NOT NULL CHECK (feedback_type IN ('rating', 'comment', 'bug_report', 'feature_request', 'ai_feedback', 'content_feedback')),
    target_type TEXT CHECK (target_type IN ('search_result', 'recommendation', 'alert', 'report', 'feature', 'ui_element')),
    target_id TEXT,

    -- Feedback content
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    feedback_data JSONB DEFAULT '{}',
    categories TEXT[] DEFAULT '{}',

    -- Processing and analysis
    sentiment_score DECIMAL(3,2),
    processed BOOLEAN DEFAULT false,
    ai_analyzed BOOLEAN DEFAULT false,
    analysis_results JSONB DEFAULT '{}',

    -- Context
    session_id TEXT,
    page_context TEXT,
    user_journey_stage TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- NOTIFICATION SYSTEM WITH AI
-- ==========================================

CREATE TABLE IF NOT EXISTS user_notifications (
    notification_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Notification content
    type TEXT NOT NULL CHECK (type IN ('alert', 'report_ready', 'system', 'marketing', 'digest', 'welcome', 'upgrade', 'ai_insight', 'recommendation')),
    title TEXT NOT NULL CHECK (length(title) <= 200),
    message TEXT CHECK (length(message) <= 1000),
    data JSONB DEFAULT '{}',
    action_data JSONB DEFAULT '{}',

    -- AI personalization
    personalized BOOLEAN DEFAULT false,
    ai_generated BOOLEAN DEFAULT false,
    personalization_data JSONB DEFAULT '{}',

    -- Delivery settings
    delivery_method TEXT DEFAULT 'in_app' CHECK (delivery_method IN ('in_app', 'email', 'push', 'sms')),
    priority TEXT DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    channel_preferences JSONB DEFAULT '{}',

    -- Status tracking
    is_read BOOLEAN DEFAULT false,
    is_sent BOOLEAN DEFAULT false,
    sent_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,
    clicked BOOLEAN DEFAULT false,
    clicked_at TIMESTAMP WITH TIME ZONE,

    -- Related entities
    related_entity_type TEXT,
    related_entity_id TEXT,

    -- Scheduling and timing
    scheduled_for TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    optimal_send_time TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days'),

    -- Delivery tracking
    delivery_attempts INTEGER DEFAULT 0,
    delivery_status TEXT DEFAULT 'pending' CHECK (delivery_status IN ('pending', 'sent', 'failed', 'expired')),
    error_message TEXT,

    -- AI metrics
    predicted_engagement DECIMAL(3,2),
    actual_engagement DECIMAL(3,2),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- API USAGE AND ANALYTICS
-- ==========================================

CREATE TABLE IF NOT EXISTS api_usage (
    usage_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Request details
    endpoint TEXT NOT NULL,
    method TEXT NOT NULL CHECK (method IN ('GET', 'POST', 'PUT', 'DELETE', 'PATCH')),
    query_parameters JSONB DEFAULT '{}',
    request_size_bytes INTEGER,
    request_headers JSONB DEFAULT '{}',

    -- Response details
    response_time_ms INTEGER NOT NULL,
    response_status INTEGER NOT NULL,
    response_size_bytes INTEGER,
    results_returned INTEGER,
    cache_hit BOOLEAN DEFAULT false,

    -- AI features used
    ai_features_used TEXT[] DEFAULT '{}',
    ai_processing_time_ms INTEGER DEFAULT 0,
    ai_model_versions JSONB DEFAULT '{}',

    -- Billing and limits
    billable BOOLEAN DEFAULT true,
    cost_credits DECIMAL(10,4) DEFAULT 0.0,
    tier_at_time TEXT NOT NULL,

    -- Performance metrics
    processing_time_ms INTEGER,
    database_time_ms INTEGER,
    external_api_time_ms INTEGER,

    -- Context and tracking
    user_agent TEXT,
    ip_address INET,
    session_id TEXT,
    trace_id TEXT,

    -- Geographic context
    location_lat DECIMAL(10,8),
    location_lng DECIMAL(11,8),
    country_code TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User sessions for behavior tracking
CREATE TABLE IF NOT EXISTS user_sessions (
    session_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Session metadata
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    is_active BOOLEAN DEFAULT true,

    -- Activity tracking
    pages_visited INTEGER DEFAULT 0,
    actions_performed INTEGER DEFAULT 0,
    searches_performed INTEGER DEFAULT 0,
    features_used TEXT[] DEFAULT '{}',

    -- Session data
    session_data JSONB DEFAULT '{}',
    user_journey JSONB DEFAULT '[]',
    conversion_events JSONB DEFAULT '[]',

    -- Device and environment
    device_info JSONB DEFAULT '{}',
    browser_info JSONB DEFAULT '{}',
    location_data JSONB DEFAULT '{}',

    -- Quality metrics
    engagement_score DECIMAL(3,2),
    bounce_rate DECIMAL(3,2),
    time_to_first_action INTEGER,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- INDEXES FOR PERFORMANCE
-- ==========================================

-- User profiles indexes
CREATE INDEX IF NOT EXISTS idx_user_profiles_subscription_tier ON user_profiles(subscription_tier);
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_segment ON user_profiles(user_segment);
CREATE INDEX IF NOT EXISTS idx_user_profiles_last_active ON user_profiles(last_active DESC);

-- Saved searches indexes
CREATE INDEX IF NOT EXISTS idx_saved_searches_user_id ON saved_searches(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_searches_category ON saved_searches(category);
CREATE INDEX IF NOT EXISTS idx_saved_searches_last_used ON saved_searches(last_used DESC);
CREATE INDEX IF NOT EXISTS idx_saved_searches_ai_enhanced ON saved_searches(ai_enhanced, user_id);

-- User alerts indexes
CREATE INDEX IF NOT EXISTS idx_user_alerts_user_id ON user_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_user_alerts_next_check ON user_alerts(next_check) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_user_alerts_ai_enhanced ON user_alerts(ai_enhanced, user_id);
CREATE INDEX IF NOT EXISTS idx_alert_triggers_alert_id ON alert_triggers(alert_id);

-- User reports indexes
CREATE INDEX IF NOT EXISTS idx_user_reports_user_id ON user_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_user_reports_status ON user_reports(status);
CREATE INDEX IF NOT EXISTS idx_user_reports_type ON user_reports(report_type);
CREATE INDEX IF NOT EXISTS idx_user_reports_expires_at ON user_reports(expires_at);

-- AI and personalization indexes
CREATE INDEX IF NOT EXISTS idx_user_ai_preferences_user_id ON user_ai_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_user_ai_preferences_type ON user_ai_preferences(preference_type);
CREATE INDEX IF NOT EXISTS idx_user_ai_preferences_active ON user_ai_preferences(user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_user_interactions_user_id ON user_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_interactions_type ON user_interactions(interaction_type);
CREATE INDEX IF NOT EXISTS idx_user_interactions_timestamp ON user_interactions(timestamp_utc DESC);
CREATE INDEX IF NOT EXISTS idx_user_behavior_profiles_user_id ON user_behavior_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_recommendations_user_id ON user_recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_user_recommendations_active ON user_recommendations(user_id, expires_at) WHERE expires_at > NOW();

-- Notifications indexes
CREATE INDEX IF NOT EXISTS idx_user_notifications_user_id ON user_notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_user_notifications_unread ON user_notifications(user_id, is_read, created_at DESC) WHERE is_read = false;
CREATE INDEX IF NOT EXISTS idx_user_notifications_scheduled ON user_notifications(scheduled_for) WHERE delivery_status = 'pending';

-- API usage indexes
CREATE INDEX IF NOT EXISTS idx_api_usage_user_id ON api_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_api_usage_created_at ON api_usage(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_started_at ON user_sessions(started_at DESC);

-- ==========================================
-- ROW LEVEL SECURITY POLICIES
-- ==========================================

-- Enable RLS on all user-specific tables
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE saved_searches ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE alert_triggers ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_ai_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_behavior_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;

-- User profiles policies
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- User settings policies
CREATE POLICY "Users can manage own settings" ON user_settings
    FOR ALL USING (auth.uid() = user_id);

-- Saved searches policies
CREATE POLICY "Users can manage own saved searches" ON saved_searches
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view public searches" ON saved_searches
    FOR SELECT USING (is_public = true OR auth.uid() = user_id);

-- User alerts policies
CREATE POLICY "Users can manage own alerts" ON user_alerts
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own alert triggers" ON alert_triggers
    FOR SELECT USING (auth.uid() = user_id);

-- User reports policies
CREATE POLICY "Users can manage own reports" ON user_reports
    FOR ALL USING (auth.uid() = user_id);

-- AI preferences policies
CREATE POLICY "Users can manage own AI preferences" ON user_ai_preferences
    FOR ALL USING (auth.uid() = user_id);

-- User interactions policies
CREATE POLICY "Users can insert own interactions" ON user_interactions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own interactions" ON user_interactions
    FOR SELECT USING (auth.uid() = user_id);

-- Behavior profiles policies
CREATE POLICY "Users can view own behavior profile" ON user_behavior_profiles
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Service role can manage behavior profiles" ON user_behavior_profiles
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- Recommendations policies
CREATE POLICY "Users can view own recommendations" ON user_recommendations
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own recommendations" ON user_recommendations
    FOR UPDATE USING (auth.uid() = user_id);

-- Feedback policies
CREATE POLICY "Users can manage own feedback" ON user_feedback
    FOR ALL USING (auth.uid() = user_id);

-- Notifications policies
CREATE POLICY "Users can view own notifications" ON user_notifications
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own notifications" ON user_notifications
    FOR UPDATE USING (auth.uid() = user_id);

-- API usage policies
CREATE POLICY "Users can view own usage" ON api_usage
    FOR SELECT USING (auth.uid() = user_id);

-- Sessions policies
CREATE POLICY "Users can manage own sessions" ON user_sessions
    FOR ALL USING (auth.uid() = user_id);

-- Admin policies
CREATE POLICY "Admins can view all profiles" ON user_profiles
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_profiles
            WHERE user_id = auth.uid() AND role = 'admin'
        )
    );

-- ==========================================
-- FUNCTIONS AND TRIGGERS
-- ==========================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
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

CREATE TRIGGER update_user_sessions_updated_at BEFORE UPDATE ON user_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to handle new user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.user_profiles (user_id, email, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name')
    );

    INSERT INTO public.user_settings (user_id)
    VALUES (NEW.id);

    INSERT INTO public.user_behavior_profiles (user_id, behavior_data)
    VALUES (NEW.id, '{"signup_date": "' || NOW() || '"}');

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger for new user creation
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Function to update user engagement scores
CREATE OR REPLACE FUNCTION update_user_engagement_score()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE user_behavior_profiles
    SET
        engagement_score = (
            SELECT
                COALESCE(
                    AVG(CASE
                        WHEN interaction_type = 'search' THEN 1.0
                        WHEN interaction_type = 'save' THEN 2.0
                        WHEN interaction_type = 'alert_create' THEN 3.0
                        WHEN interaction_type = 'report_generate' THEN 4.0
                        WHEN interaction_type = 'share' THEN 2.5
                        ELSE 0.5
                    END), 0.0
                )
            FROM user_interactions
            WHERE user_id = NEW.user_id
            AND created_at > NOW() - INTERVAL '30 days'
        ),
        last_updated = NOW()
    WHERE user_id = NEW.user_id;

    -- Update user profile engagement score
    UPDATE user_profiles
    SET engagement_score = (
        SELECT engagement_score FROM user_behavior_profiles
        WHERE user_id = NEW.user_id
    )
    WHERE user_id = NEW.user_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for engagement score updates
CREATE TRIGGER update_engagement_score_trigger
    AFTER INSERT ON user_interactions
    FOR EACH ROW EXECUTE FUNCTION update_user_engagement_score();

-- Function to update API usage statistics
CREATE OR REPLACE FUNCTION update_api_usage_stats()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE user_profiles
    SET
        api_calls_this_month = api_calls_this_month + 1,
        last_active = NOW()
    WHERE user_id = NEW.user_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for API usage tracking
CREATE TRIGGER update_usage_stats AFTER INSERT ON api_usage
    FOR EACH ROW EXECUTE FUNCTION update_api_usage_stats();

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

    -- Delete expired recommendations
    DELETE FROM user_recommendations
    WHERE expires_at < NOW() AND is_persistent = false;

    -- Delete old AI preferences
    DELETE FROM user_ai_preferences
    WHERE expires_at < NOW() AND is_active = false;

    -- Delete old interaction data (keep 1 year)
    DELETE FROM user_interactions
    WHERE created_at < NOW() - INTERVAL '1 year';

    -- Delete old API usage data (keep 2 years)
    DELETE FROM api_usage
    WHERE created_at < NOW() - INTERVAL '2 years';

    -- Delete old sessions (keep 6 months)
    DELETE FROM user_sessions
    WHERE started_at < NOW() - INTERVAL '6 months';
END;
$$ LANGUAGE plpgsql;

-- ==========================================
-- INITIAL DATA AND CONFIGURATION
-- ==========================================

-- Insert default configurations
INSERT INTO app_config (config_key, config_value, description, is_public) VALUES
('feature_flags', '{"ai_personalization": true, "real_time_notifications": true, "advanced_reports": true, "smart_alerts": true}', 'Feature flags for enabling/disabling features', false),
('subscription_tiers', '{"free": {"api_calls": 1000, "saved_searches": 10, "alerts": 5}, "professional": {"api_calls": 10000, "saved_searches": 100, "alerts": 50}, "enterprise": {"api_calls": 100000, "saved_searches": 1000, "alerts": 500}}', 'Subscription tier limits', true),
('ai_settings', '{"min_confidence_threshold": 0.5, "personalization_enabled": true, "auto_suggestions": true, "recommendation_refresh_hours": 24}', 'AI system configuration', false),
('notification_settings', '{"max_daily_notifications": 50, "digest_enabled": true, "ai_optimization": true}', 'Notification system settings', false)
ON CONFLICT (config_key) DO UPDATE SET
    config_value = EXCLUDED.config_value,
    updated_at = NOW();

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Planning Explorer Phase 3 database schema created successfully!';
    RAISE NOTICE 'All AI features, personalization, and user management tables are ready.';
END $$;