-- Planning Explorer Supabase Database Setup
-- Complete schema for user management and AI personalization

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- =============================================
-- CORE USER TABLES
-- =============================================

-- Enhanced user profiles
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    company TEXT,
    role TEXT DEFAULT 'free',
    subscription_tier TEXT DEFAULT 'free' CHECK (subscription_tier IN ('free', 'professional', 'enterprise')),
    preferences JSONB DEFAULT '{}',
    api_calls_this_month INTEGER DEFAULT 0,
    max_api_calls_per_month INTEGER DEFAULT 1000,
    max_saved_searches INTEGER DEFAULT 10,
    max_alerts INTEGER DEFAULT 5,
    onboarding_completed BOOLEAN DEFAULT false,
    last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Saved searches with AI enhancement
CREATE TABLE IF NOT EXISTS saved_searches (
    search_id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    query TEXT,
    filters JSONB DEFAULT '{}',
    ai_suggestions JSONB DEFAULT '{}',
    last_used TIMESTAMP WITH TIME ZONE,
    use_count INTEGER DEFAULT 0,
    is_favorite BOOLEAN DEFAULT false,
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Smart alerts system
CREATE TABLE IF NOT EXISTS user_alerts (
    alert_id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    query TEXT,
    filters JSONB DEFAULT '{}',
    ai_criteria JSONB DEFAULT '{}',
    frequency TEXT DEFAULT 'daily' CHECK (frequency IN ('instant', 'daily', 'weekly')),
    is_active BOOLEAN DEFAULT true,
    last_triggered TIMESTAMP WITH TIME ZONE,
    trigger_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Reports and analytics
CREATE TABLE IF NOT EXISTS user_reports (
    report_id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    report_type TEXT NOT NULL,
    template_id TEXT,
    parameters JSONB DEFAULT '{}',
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    content JSONB,
    generated_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================
-- AI PERSONALIZATION TABLES
-- =============================================

-- AI personalization data
CREATE TABLE IF NOT EXISTS user_ai_preferences (
    preference_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    preference_type TEXT NOT NULL,
    preference_data JSONB DEFAULT '{}',
    confidence_score DECIMAL(3,2) DEFAULT 0.0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User interactions for AI learning
CREATE TABLE IF NOT EXISTS user_interactions (
    interaction_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    interaction_type TEXT NOT NULL,
    context JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User behavior profiles for AI
CREATE TABLE IF NOT EXISTS user_behavior_profiles (
    profile_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    behavior_data JSONB DEFAULT '{}',
    engagement_score DECIMAL(5,2) DEFAULT 0.0,
    user_segment TEXT,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI-generated recommendations
CREATE TABLE IF NOT EXISTS user_recommendations (
    recommendation_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    recommendation_type TEXT NOT NULL,
    content JSONB DEFAULT '{}',
    confidence_score DECIMAL(3,2) DEFAULT 0.0,
    is_viewed BOOLEAN DEFAULT false,
    is_acted_upon BOOLEAN DEFAULT false,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User feedback for AI learning
CREATE TABLE IF NOT EXISTS user_feedback (
    feedback_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    feedback_type TEXT NOT NULL,
    target_id TEXT,
    feedback_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================
-- NOTIFICATION AND TRACKING TABLES
-- =============================================

-- Notification system
CREATE TABLE IF NOT EXISTS user_notifications (
    notification_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT,
    data JSONB DEFAULT '{}',
    is_read BOOLEAN DEFAULT false,
    delivery_method TEXT DEFAULT 'in_app' CHECK (delivery_method IN ('in_app', 'email', 'push')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API usage tracking
CREATE TABLE IF NOT EXISTS api_usage (
    usage_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    endpoint TEXT NOT NULL,
    method TEXT NOT NULL,
    response_time_ms INTEGER,
    status_code INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================
-- FUNCTIONS AND TRIGGERS
-- =============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_profiles;
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to create user profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.user_profiles (user_id, email, full_name)
    VALUES (NEW.id, NEW.email, COALESCE(NEW.raw_user_meta_data->>'full_name', ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile on user signup
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- =============================================
-- ROW LEVEL SECURITY POLICIES
-- =============================================

-- Enable RLS on all tables
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE saved_searches ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_ai_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_behavior_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_feedback ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view their own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can update their own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can insert their own profile" ON user_profiles;

-- User profiles policies
CREATE POLICY "Users can view their own profile" ON user_profiles
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update their own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Saved searches policies
DROP POLICY IF EXISTS "Users can manage their own searches" ON saved_searches;
DROP POLICY IF EXISTS "Users can view public searches" ON saved_searches;
CREATE POLICY "Users can manage their own searches" ON saved_searches
    FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can view public searches" ON saved_searches
    FOR SELECT USING (is_public = true OR auth.uid() = user_id);

-- User alerts policies
DROP POLICY IF EXISTS "Users can manage their own alerts" ON user_alerts;
CREATE POLICY "Users can manage their own alerts" ON user_alerts
    FOR ALL USING (auth.uid() = user_id);

-- User reports policies
DROP POLICY IF EXISTS "Users can manage their own reports" ON user_reports;
CREATE POLICY "Users can manage their own reports" ON user_reports
    FOR ALL USING (auth.uid() = user_id);

-- AI preferences policies
DROP POLICY IF EXISTS "Users can manage their own AI preferences" ON user_ai_preferences;
CREATE POLICY "Users can manage their own AI preferences" ON user_ai_preferences
    FOR ALL USING (auth.uid() = user_id);

-- Notifications policies
DROP POLICY IF EXISTS "Users can manage their own notifications" ON user_notifications;
CREATE POLICY "Users can manage their own notifications" ON user_notifications
    FOR ALL USING (auth.uid() = user_id);

-- API usage policies
DROP POLICY IF EXISTS "Users can view their own API usage" ON api_usage;
CREATE POLICY "Users can view their own API usage" ON api_usage
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "System can insert API usage" ON api_usage
    FOR INSERT WITH CHECK (true);

-- User interactions policies
DROP POLICY IF EXISTS "Users can manage their own interactions" ON user_interactions;
CREATE POLICY "Users can manage their own interactions" ON user_interactions
    FOR ALL USING (auth.uid() = user_id);

-- Behavior profiles policies
DROP POLICY IF EXISTS "Users can view their own behavior profile" ON user_behavior_profiles;
CREATE POLICY "Users can view their own behavior profile" ON user_behavior_profiles
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "System can manage behavior profiles" ON user_behavior_profiles
    FOR ALL USING (true);

-- Recommendations policies
DROP POLICY IF EXISTS "Users can manage their own recommendations" ON user_recommendations;
CREATE POLICY "Users can manage their own recommendations" ON user_recommendations
    FOR ALL USING (auth.uid() = user_id);

-- Feedback policies
DROP POLICY IF EXISTS "Users can manage their own feedback" ON user_feedback;
CREATE POLICY "Users can manage their own feedback" ON user_feedback
    FOR ALL USING (auth.uid() = user_id);

-- =============================================
-- PERFORMANCE INDEXES
-- =============================================

-- User profiles indexes
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_subscription_tier ON user_profiles(subscription_tier);
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);

-- Saved searches indexes
CREATE INDEX IF NOT EXISTS idx_saved_searches_user_id ON saved_searches(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_searches_created_at ON saved_searches(created_at);
CREATE INDEX IF NOT EXISTS idx_saved_searches_is_public ON saved_searches(is_public);

-- User alerts indexes
CREATE INDEX IF NOT EXISTS idx_user_alerts_user_id ON user_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_user_alerts_is_active ON user_alerts(is_active);

-- User reports indexes
CREATE INDEX IF NOT EXISTS idx_user_reports_user_id ON user_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_user_reports_status ON user_reports(status);

-- Notifications indexes
CREATE INDEX IF NOT EXISTS idx_user_notifications_user_id ON user_notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_user_notifications_is_read ON user_notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_user_notifications_created_at ON user_notifications(created_at);

-- API usage indexes
CREATE INDEX IF NOT EXISTS idx_api_usage_user_id ON api_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_api_usage_created_at ON api_usage(created_at);

-- AI-related indexes
CREATE INDEX IF NOT EXISTS idx_user_interactions_user_id ON user_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_interactions_type ON user_interactions(interaction_type);
CREATE INDEX IF NOT EXISTS idx_user_recommendations_user_id ON user_recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_user_recommendations_type ON user_recommendations(recommendation_type);

-- =============================================
-- SAMPLE DATA (Optional)
-- =============================================

-- Insert sample subscription tier configurations
INSERT INTO user_profiles (user_id, email, full_name, subscription_tier, max_api_calls_per_month, max_saved_searches, max_alerts)
VALUES
    ('00000000-0000-0000-0000-000000000001'::uuid, 'demo@planningexplorer.uk', 'Demo User', 'free', 1000, 10, 5)
ON CONFLICT (user_id) DO NOTHING;

-- =============================================
-- COMPLETION MESSAGE
-- =============================================

-- Verify setup
DO $$
BEGIN
    RAISE NOTICE 'Planning Explorer Supabase setup completed successfully!';
    RAISE NOTICE 'Tables created: %', (
        SELECT count(*) FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name LIKE 'user_%'
    );
END $$;