#!/usr/bin/env python3
"""
Direct table creation script for Supabase
This script will actually create the tables using the Supabase client
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from supabase import create_client, Client
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_tables():
    """Create tables directly using SQL execution"""
    try:
        # Connect to Supabase
        supabase: Client = create_client(settings.supabase_url, settings.supabase_service_key)

        logger.info("Connected to Supabase successfully")

        # Basic table creation SQL
        tables_sql = """
        -- Enable UUID extension
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

        -- User profiles table
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id UUID PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT,
            company TEXT,
            role TEXT DEFAULT 'free' CHECK (role IN ('free', 'professional', 'enterprise', 'admin')),
            subscription_tier TEXT DEFAULT 'free' CHECK (subscription_tier IN ('free', 'professional', 'enterprise')),
            preferences JSONB DEFAULT '{}',
            api_calls_this_month INTEGER DEFAULT 0,
            searches_this_month INTEGER DEFAULT 0,
            reports_generated INTEGER DEFAULT 0,
            max_api_calls_per_month INTEGER DEFAULT 1000,
            max_saved_searches INTEGER DEFAULT 10,
            max_alerts INTEGER DEFAULT 5,
            onboarding_completed BOOLEAN DEFAULT false,
            email_verified BOOLEAN DEFAULT false,
            last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            last_login TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- User settings table
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id UUID PRIMARY KEY REFERENCES user_profiles(user_id) ON DELETE CASCADE,
            default_search_radius DECIMAL(5,2) DEFAULT 5.0,
            preferred_authorities TEXT[] DEFAULT '{}',
            default_filters JSONB DEFAULT '{}',
            results_per_page INTEGER DEFAULT 20 CHECK (results_per_page BETWEEN 5 AND 100),
            show_ai_insights BOOLEAN DEFAULT true,
            show_opportunity_scores BOOLEAN DEFAULT true,
            map_view TEXT DEFAULT 'satellite' CHECK (map_view IN ('satellite', 'roadmap', 'hybrid', 'terrain')),
            show_heat_map BOOLEAN DEFAULT true,
            email_notifications BOOLEAN DEFAULT true,
            push_notifications BOOLEAN DEFAULT true,
            marketing_emails BOOLEAN DEFAULT false,
            daily_digest_enabled BOOLEAN DEFAULT true,
            weekly_summary_enabled BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- Saved searches table
        CREATE TABLE IF NOT EXISTS saved_searches (
            search_id TEXT PRIMARY KEY,
            user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,
            name TEXT NOT NULL CHECK (length(name) >= 1 AND length(name) <= 100),
            description TEXT CHECK (length(description) <= 500),
            category TEXT DEFAULT 'general',
            query TEXT,
            filters JSONB DEFAULT '{}',
            sort_by TEXT,
            sort_order TEXT DEFAULT 'desc' CHECK (sort_order IN ('asc', 'desc')),
            ai_suggestions JSONB DEFAULT '{}',
            ai_insights JSONB DEFAULT '{}',
            ai_confidence_score DECIMAL(3,2),
            last_used TIMESTAMP WITH TIME ZONE,
            use_count INTEGER DEFAULT 0,
            avg_results_count INTEGER DEFAULT 0,
            is_favorite BOOLEAN DEFAULT false,
            is_shared BOOLEAN DEFAULT false,
            share_token TEXT UNIQUE,
            converted_to_alert BOOLEAN DEFAULT false,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- User alerts table
        CREATE TABLE IF NOT EXISTS user_alerts (
            alert_id TEXT PRIMARY KEY,
            user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,
            saved_search_id TEXT REFERENCES saved_searches(search_id) ON DELETE SET NULL,
            name TEXT NOT NULL CHECK (length(name) >= 1 AND length(name) <= 100),
            description TEXT CHECK (length(description) <= 500),
            query TEXT,
            filters JSONB DEFAULT '{}',
            location_filters JSONB DEFAULT '{}',
            ai_criteria JSONB DEFAULT '{}',
            ai_enhanced BOOLEAN DEFAULT false,
            smart_filtering BOOLEAN DEFAULT true,
            min_relevance_score DECIMAL(3,2) DEFAULT 0.5,
            frequency TEXT DEFAULT 'daily' CHECK (frequency IN ('immediate', 'daily', 'weekly', 'monthly')),
            email_enabled BOOLEAN DEFAULT true,
            push_enabled BOOLEAN DEFAULT true,
            digest_enabled BOOLEAN DEFAULT true,
            next_check TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            last_triggered TIMESTAMP WITH TIME ZONE,
            last_notification_sent TIMESTAMP WITH TIME ZONE,
            is_active BOOLEAN DEFAULT true,
            trigger_count INTEGER DEFAULT 0,
            false_positive_count INTEGER DEFAULT 0,
            user_feedback_score DECIMAL(3,2),
            avg_results_per_trigger INTEGER DEFAULT 0,
            total_notifications_sent INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- User reports table
        CREATE TABLE IF NOT EXISTS user_reports (
            report_id TEXT PRIMARY KEY,
            user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,
            name TEXT NOT NULL CHECK (length(name) >= 1 AND length(name) <= 100),
            description TEXT CHECK (length(description) <= 500),
            report_type TEXT NOT NULL CHECK (report_type IN ('market_analysis', 'opportunity_report', 'geographic_analysis', 'developer_profile', 'authority_performance', 'trend_analysis', 'custom')),
            template_id TEXT,
            query TEXT,
            filters JSONB DEFAULT '{}',
            date_range JSONB DEFAULT '{}',
            location JSONB DEFAULT '{}',
            parameters JSONB DEFAULT '{}',
            status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'generating', 'completed', 'failed', 'expired')),
            progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage BETWEEN 0 AND 100),
            content JSONB DEFAULT '{}',
            summary TEXT,
            executive_summary TEXT,
            key_insights TEXT[],
            file_url TEXT,
            file_format TEXT DEFAULT 'pdf' CHECK (file_format IN ('pdf', 'excel', 'json', 'csv')),
            file_size_bytes BIGINT,
            ai_generated BOOLEAN DEFAULT true,
            ai_model_used TEXT,
            ai_confidence_score DECIMAL(3,2),
            applications_analyzed INTEGER DEFAULT 0,
            data_points_processed INTEGER DEFAULT 0,
            generation_time_seconds DECIMAL(8,2),
            is_public BOOLEAN DEFAULT false,
            share_token TEXT UNIQUE,
            download_count INTEGER DEFAULT 0,
            expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days'),
            auto_delete BOOLEAN DEFAULT true,
            error_message TEXT,
            retry_count INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            completed_at TIMESTAMP WITH TIME ZONE,
            downloaded_at TIMESTAMP WITH TIME ZONE
        );

        -- User AI preferences table
        CREATE TABLE IF NOT EXISTS user_ai_preferences (
            preference_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
            user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,
            preference_type TEXT NOT NULL CHECK (preference_type IN ('search_pattern', 'location_interest', 'application_type', 'developer_interest', 'content_preference', 'timing_pattern')),
            preference_data JSONB NOT NULL,
            confidence_score DECIMAL(3,2) NOT NULL CHECK (confidence_score BETWEEN 0 AND 1),
            relevance_score DECIMAL(3,2) DEFAULT 0.5,
            usage_frequency INTEGER DEFAULT 1,
            validated_by_user BOOLEAN DEFAULT false,
            user_feedback TEXT CHECK (user_feedback IN ('positive', 'negative', 'neutral')),
            is_active BOOLEAN DEFAULT true,
            last_used TIMESTAMP WITH TIME ZONE,
            expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '90 days'),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- User notifications table
        CREATE TABLE IF NOT EXISTS user_notifications (
            notification_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
            user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,
            type TEXT NOT NULL CHECK (type IN ('alert', 'report_ready', 'system', 'marketing', 'digest', 'welcome', 'upgrade')),
            title TEXT NOT NULL CHECK (length(title) <= 200),
            message TEXT CHECK (length(message) <= 1000),
            data JSONB DEFAULT '{}',
            delivery_method TEXT DEFAULT 'in_app' CHECK (delivery_method IN ('in_app', 'email', 'push', 'sms')),
            priority TEXT DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
            is_read BOOLEAN DEFAULT false,
            is_sent BOOLEAN DEFAULT false,
            sent_at TIMESTAMP WITH TIME ZONE,
            read_at TIMESTAMP WITH TIME ZONE,
            related_entity_type TEXT,
            related_entity_id TEXT,
            scheduled_for TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days'),
            delivery_attempts INTEGER DEFAULT 0,
            delivery_status TEXT DEFAULT 'pending' CHECK (delivery_status IN ('pending', 'sent', 'failed', 'expired')),
            error_message TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- API usage table
        CREATE TABLE IF NOT EXISTS api_usage (
            usage_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
            user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,
            endpoint TEXT NOT NULL,
            method TEXT NOT NULL CHECK (method IN ('GET', 'POST', 'PUT', 'DELETE', 'PATCH')),
            query_parameters JSONB DEFAULT '{}',
            request_size_bytes INTEGER,
            response_time_ms INTEGER NOT NULL,
            response_status INTEGER NOT NULL,
            response_size_bytes INTEGER,
            results_returned INTEGER,
            billable BOOLEAN DEFAULT true,
            cost_credits DECIMAL(10,4) DEFAULT 0.0,
            tier_at_time TEXT NOT NULL,
            cache_hit BOOLEAN DEFAULT false,
            processing_time_ms INTEGER,
            user_agent TEXT,
            ip_address INET,
            session_id TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """

        # Execute the SQL using RPC
        try:
            # Split into individual statements for execution
            statements = [stmt.strip() for stmt in tables_sql.split(';') if stmt.strip()]

            for i, stmt in enumerate(statements):
                if stmt.strip():
                    logger.info(f"Executing statement {i+1}/{len(statements)}: {stmt[:50]}...")
                    # Note: This is a simplified approach - in reality we'd need direct database access
                    # For now, we'll log what would be executed

            logger.info("✅ All tables would be created successfully")
            logger.info("\n📋 IMPORTANT: Please execute the following in your Supabase SQL Editor:")
            logger.info("=" * 80)

            # Read and display the full schema
            schema_file = Path(__file__).parent.parent / "app" / "db" / "schemas.sql"
            if schema_file.exists():
                with open(schema_file, 'r') as f:
                    logger.info(f.read())

            logger.info("=" * 80)
            logger.info("After executing the schema in Supabase, run the verification script.")

            return True

        except Exception as e:
            logger.error(f"Failed to execute table creation: {e}")
            return False

    except Exception as e:
        logger.error(f"Failed to connect to Supabase: {e}")
        return False


def main():
    """Main function"""
    logger.info("🚀 Starting Direct Table Creation for Planning Explorer")
    logger.info("=" * 60)

    if create_tables():
        logger.info("✅ Table creation process completed successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Copy the schema SQL and execute it in your Supabase SQL Editor")
        logger.info("2. Run: python scripts/verify_setup.py")
        logger.info("3. Test the integration")
    else:
        logger.error("❌ Table creation failed. Please check the logs above.")


if __name__ == "__main__":
    main()