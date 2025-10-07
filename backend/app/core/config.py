"""
Configuration settings for Planning Explorer API
"""
from typing import Optional, Dict
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    api_title: str = "Planning Explorer API"
    api_version: str = "1.0.0"
    api_description: str = "UK's first AI-native planning intelligence platform API"
    debug: bool = False

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    # Elasticsearch Configuration
    elasticsearch_node: str = Field(..., alias="ELASTICSEARCH_NODE")
    elasticsearch_username: str = Field(..., alias="ELASTICSEARCH_USERNAME")
    elasticsearch_password: str = Field(..., alias="ELASTICSEARCH_PASSWORD")
    elasticsearch_index: str = "planning_applications"
    elasticsearch_timeout: int = 60  # Increased from 30 to 60 for vector search operations
    elasticsearch_max_retries: int = 3

    # Database Configuration
    database_url: str = Field(default="sqlite:///./planning_explorer.db", alias="DATABASE_URL")

    # Supabase Configuration (Legacy - will be removed)
    supabase_url: Optional[str] = Field(default=None, alias="SUPABASE_URL")
    supabase_key: Optional[str] = Field(default=None, alias="SUPABASE_ANON_KEY")
    supabase_service_key: Optional[str] = Field(default=None, alias="SUPABASE_SERVICE_ROLE_KEY")

    # JWT Configuration
    secret_key: str = Field(default="your-secret-key-change-in-production", alias="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # AI Configuration
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")

    # pSEO Configuration
    context7_api_key: Optional[str] = Field(default=None, alias="CONTEXT7_API_KEY")
    firecrawl_api_key: Optional[str] = Field(default=None, alias="FIRECRAWL_API_KEY")
    anthropic_base_url: Optional[str] = Field(default=None, alias="ANTHROPIC_BASE_URL")
    anthropic_auth_token: Optional[str] = Field(default=None, alias="ANTHROPIC_AUTH_TOKEN")
    pseo_max_concurrent: int = Field(default=3, alias="PSEO_MAX_CONCURRENT")
    pseo_batch_size: int = Field(default=10, alias="PSEO_BATCH_SIZE")
    pseo_output_dir: str = Field(default="./outputs/pseo", alias="PSEO_OUTPUT_DIR")
    pseo_min_word_count: int = Field(default=2500, alias="PSEO_MIN_WORD_COUNT")
    pseo_max_word_count: int = Field(default=3500, alias="PSEO_MAX_WORD_COUNT")

    # Performance Configuration
    max_connections: int = 100
    request_timeout: int = 30

    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "json"

    # CORS Configuration
    cors_origins: list = ["http://localhost:3000", "https://planningexplorer.uk"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_allow_headers: list = ["*"]

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds

    # Cache Configuration
    cache_ttl: int = 300  # 5 minutes

    # Email Configuration
    smtp_server: Optional[str] = Field(default=None, alias="SMTP_SERVER")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, alias="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, alias="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(default=True, alias="SMTP_USE_TLS")
    from_email: str = Field(default="noreply@planningexplorer.uk", alias="FROM_EMAIL")

    # Background Jobs Configuration
    redis_url: Optional[str] = Field(default=None, alias="REDIS_URL")
    celery_broker_url: Optional[str] = Field(default=None, alias="CELERY_BROKER_URL")
    celery_result_backend: Optional[str] = Field(default=None, alias="CELERY_RESULT_BACKEND")

    # Subscription Tiers Configuration
    free_tier_api_limit: int = Field(default=1000, alias="FREE_TIER_API_LIMIT")
    free_tier_saved_searches: int = Field(default=10, alias="FREE_TIER_SAVED_SEARCHES")
    free_tier_alerts: int = Field(default=5, alias="FREE_TIER_ALERTS")

    professional_tier_api_limit: int = Field(default=10000, alias="PROFESSIONAL_TIER_API_LIMIT")
    professional_tier_saved_searches: int = Field(default=100, alias="PROFESSIONAL_TIER_SAVED_SEARCHES")
    professional_tier_alerts: int = Field(default=50, alias="PROFESSIONAL_TIER_ALERTS")

    enterprise_tier_api_limit: int = Field(default=100000, alias="ENTERPRISE_TIER_API_LIMIT")
    enterprise_tier_saved_searches: int = Field(default=1000, alias="ENTERPRISE_TIER_SAVED_SEARCHES")
    enterprise_tier_alerts: int = Field(default=500, alias="ENTERPRISE_TIER_ALERTS")

    # Notification Configuration
    enable_email_notifications: bool = Field(default=True, alias="ENABLE_EMAIL_NOTIFICATIONS")
    enable_push_notifications: bool = Field(default=True, alias="ENABLE_PUSH_NOTIFICATIONS")
    notification_batch_size: int = Field(default=100, alias="NOTIFICATION_BATCH_SIZE")

    # Report Generation Configuration
    report_generation_timeout: int = Field(default=300, alias="REPORT_GENERATION_TIMEOUT")  # 5 minutes
    max_report_size_mb: int = Field(default=50, alias="MAX_REPORT_SIZE_MB")
    report_storage_path: str = Field(default="/tmp/reports", alias="REPORT_STORAGE_PATH")

    # AI Personalization Configuration
    enable_ai_personalization: bool = Field(default=True, alias="ENABLE_AI_PERSONALIZATION")
    min_user_interactions: int = Field(default=10, alias="MIN_USER_INTERACTIONS")
    personalization_update_interval: int = Field(default=24, alias="PERSONALIZATION_UPDATE_INTERVAL")  # hours

    def get_tier_limits(self, tier: str) -> Dict[str, int]:
        """Get limits for a specific subscription tier"""
        tier_configs = {
            "free": {
                "api_calls": self.free_tier_api_limit,
                "saved_searches": self.free_tier_saved_searches,
                "alerts": self.free_tier_alerts
            },
            "professional": {
                "api_calls": self.professional_tier_api_limit,
                "saved_searches": self.professional_tier_saved_searches,
                "alerts": self.professional_tier_alerts
            },
            "enterprise": {
                "api_calls": self.enterprise_tier_api_limit,
                "saved_searches": self.enterprise_tier_saved_searches,
                "alerts": self.enterprise_tier_alerts
            }
        }
        return tier_configs.get(tier, tier_configs["free"])

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()