"""
Dependency injection and configuration validation for Planning Explorer API
"""
import asyncio
import logging
from typing import AsyncGenerator, Optional, Dict, Any
from functools import lru_cache

from fastapi import Depends, HTTPException, status
from elasticsearch import AsyncElasticsearch

from app.core.config import settings
from app.db.supabase import supabase_client, SupabaseClient
from app.db.elasticsearch import es_client
from app.middleware.auth import get_current_user, get_optional_user

logger = logging.getLogger(__name__)


class ConfigurationValidator:
    """Validates application configuration and environment variables"""

    def __init__(self):
        self.validation_errors = []
        self.warnings = []

    def validate_environment(self) -> bool:
        """
        Validate all required environment variables and configuration

        Returns:
            bool: True if configuration is valid
        """
        self.validation_errors.clear()
        self.warnings.clear()

        # Required settings validation
        required_settings = {
            "supabase_url": settings.supabase_url,
            "supabase_key": settings.supabase_key,
            "elasticsearch_node": settings.elasticsearch_node,
            "secret_key": settings.secret_key
        }

        for name, value in required_settings.items():
            if not value or value == "your-secret-key-change-in-production":
                self.validation_errors.append(f"Missing or default value for {name}")

        # Optional but recommended settings
        recommended_settings = {
            "openai_api_key": settings.openai_api_key,
            "anthropic_api_key": settings.anthropic_api_key,
            "smtp_server": settings.smtp_server
        }

        for name, value in recommended_settings.items():
            if not value:
                self.warnings.append(f"Missing optional setting: {name}")

        # Validate security settings in production
        if not settings.debug:
            if settings.secret_key == "your-secret-key-change-in-production":
                self.validation_errors.append("Default secret key detected in production mode")

            if "localhost" in settings.cors_origins or "*" in settings.cors_origins:
                self.warnings.append("Permissive CORS origins detected in production")

        # Validate rate limits
        if settings.rate_limit_requests <= 0:
            self.validation_errors.append("Rate limit requests must be positive")

        if settings.rate_limit_period <= 0:
            self.validation_errors.append("Rate limit period must be positive")

        # Validate subscription tier limits
        if settings.free_tier_api_limit >= settings.professional_tier_api_limit:
            self.validation_errors.append("Professional tier API limit must be higher than free tier")

        if settings.professional_tier_api_limit >= settings.enterprise_tier_api_limit:
            self.validation_errors.append("Enterprise tier API limit must be higher than professional tier")

        # Log validation results
        if self.validation_errors:
            for error in self.validation_errors:
                logger.error(f"Configuration Error: {error}")

        if self.warnings:
            for warning in self.warnings:
                logger.warning(f"Configuration Warning: {warning}")

        return len(self.validation_errors) == 0

    def get_validation_report(self) -> Dict[str, Any]:
        """Get detailed validation report"""
        return {
            "valid": len(self.validation_errors) == 0,
            "errors": self.validation_errors,
            "warnings": self.warnings,
            "environment": {
                "debug_mode": settings.debug,
                "api_version": settings.api_version,
                "cors_origins": settings.cors_origins,
                "rate_limit": f"{settings.rate_limit_requests}/{settings.rate_limit_period}s",
                "max_connections": settings.max_connections
            }
        }


# Global configuration validator
config_validator = ConfigurationValidator()


@lru_cache()
def get_config_validator() -> ConfigurationValidator:
    """Get configuration validator instance"""
    return config_validator


async def get_database_dependencies() -> Dict[str, Any]:
    """
    Get database connection dependencies

    Returns:
        Dict containing database clients
    """
    try:
        # Ensure connections are established
        await supabase_client.ensure_connection()
        await es_client.ensure_connection()

        return {
            "supabase": supabase_client,
            "elasticsearch": es_client
        }
    except Exception as e:
        logger.error(f"Failed to get database dependencies: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database services unavailable"
        )


async def get_supabase_client() -> SupabaseClient:
    """
    Get Supabase client dependency

    Returns:
        SupabaseClient: Configured Supabase client
    """
    try:
        await supabase_client.ensure_connection()
        return supabase_client
    except Exception as e:
        logger.error(f"Supabase client unavailable: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="User database service unavailable"
        )


async def get_elasticsearch_client() -> AsyncElasticsearch:
    """
    Get Elasticsearch client dependency

    Returns:
        AsyncElasticsearch: Configured Elasticsearch client
    """
    try:
        await es_client.ensure_connection()
        return es_client.client
    except Exception as e:
        logger.error(f"Elasticsearch client unavailable: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Search service unavailable"
        )


class RateLimitTracker:
    """Track rate limits per user/IP"""

    def __init__(self):
        self.request_counts = {}
        self.last_reset = {}

    async def check_rate_limit(
        self,
        identifier: str,
        limit: int,
        window: int,
        current_time: float
    ) -> bool:
        """
        Check if request is within rate limit

        Args:
            identifier: User ID or IP address
            limit: Maximum requests allowed
            window: Time window in seconds
            current_time: Current timestamp

        Returns:
            bool: True if within limit
        """
        # Reset counter if window has passed
        if identifier not in self.last_reset or current_time - self.last_reset[identifier] >= window:
            self.request_counts[identifier] = 0
            self.last_reset[identifier] = current_time

        # Check limit
        current_count = self.request_counts.get(identifier, 0)
        if current_count >= limit:
            return False

        # Increment counter
        self.request_counts[identifier] = current_count + 1
        return True

    async def get_remaining_requests(self, identifier: str, limit: int) -> int:
        """Get remaining requests for identifier"""
        current_count = self.request_counts.get(identifier, 0)
        return max(0, limit - current_count)


# Global rate limit tracker
rate_limit_tracker = RateLimitTracker()


async def check_api_health() -> Dict[str, Any]:
    """
    Check API health status

    Returns:
        Dict with health information
    """
    health_status = {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time(),
        "services": {},
        "configuration": {
            "valid": config_validator.validate_environment(),
            "errors": config_validator.validation_errors,
            "warnings": config_validator.warnings
        }
    }

    # Check Supabase connection
    try:
        await supabase_client.ensure_connection()
        health_status["services"]["supabase"] = {
            "status": "healthy",
            "connected": True,
            "pool_size": getattr(supabase_client.pool, 'pool_size', 1) if supabase_client.pool else 1
        }
    except Exception as e:
        health_status["services"]["supabase"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"

    # Check Elasticsearch connection
    try:
        await es_client.ensure_connection()
        es_health = await es_client.health_check()
        health_status["services"]["elasticsearch"] = {
            "status": "healthy" if es_health else "unhealthy",
            "connected": es_health
        }
        if not es_health:
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["elasticsearch"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"

    # Check configuration
    if not health_status["configuration"]["valid"]:
        health_status["status"] = "unhealthy"

    return health_status


async def validate_request_permissions(
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user),
    endpoint_path: str = None,
    required_tier: Optional[str] = None,
    required_feature: Optional[str] = None
) -> Dict[str, Any]:
    """
    Validate request permissions and usage limits

    Args:
        current_user: Current authenticated user
        endpoint_path: API endpoint path
        required_tier: Required subscription tier
        required_feature: Required feature access

    Returns:
        Dict with user and permission info
    """
    # Anonymous access for public endpoints
    if not current_user and not required_tier and not required_feature:
        return {
            "user": None,
            "permissions": {
                "authenticated": False,
                "tier": "anonymous",
                "features": []
            }
        }

    # Authentication required
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    user_profile = current_user["user_profile"]

    # Check subscription tier
    if required_tier:
        tier_hierarchy = {"free": 0, "professional": 1, "enterprise": 2}
        user_level = tier_hierarchy.get(user_profile.subscription_tier, 0)
        required_level = tier_hierarchy.get(required_tier, 0)

        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"This feature requires {required_tier} subscription or higher"
            )

    # Check feature access
    if required_feature:
        feature_tiers = {
            "basic_search": "free",
            "saved_searches": "free",
            "basic_alerts": "free",
            "ai_insights": "professional",
            "custom_reports": "professional",
            "api_access": "professional",
            "bulk_exports": "enterprise",
            "custom_integrations": "enterprise"
        }

        required_feature_tier = feature_tiers.get(required_feature, "enterprise")
        tier_hierarchy = {"free": 0, "professional": 1, "enterprise": 2}
        user_level = tier_hierarchy.get(user_profile.subscription_tier, 0)
        required_level = tier_hierarchy.get(required_feature_tier, 0)

        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Feature '{required_feature}' requires {required_feature_tier} subscription or higher"
            )

    return {
        "user": current_user,
        "permissions": {
            "authenticated": True,
            "tier": user_profile.subscription_tier,
            "user_id": user_profile.user_id,
            "role": user_profile.role
        }
    }


# Dependency factories
def require_tier(tier: str):
    """Dependency factory for subscription tier requirements"""
    async def tier_dependency(
        validation_result: Dict[str, Any] = Depends(
            lambda: validate_request_permissions(required_tier=tier)
        )
    ):
        return validation_result
    return tier_dependency


def require_feature(feature: str):
    """Dependency factory for feature access requirements"""
    async def feature_dependency(
        validation_result: Dict[str, Any] = Depends(
            lambda: validate_request_permissions(required_feature=feature)
        )
    ):
        return validation_result
    return feature_dependency


# Convenience dependencies
async def get_professional_access(
    validation: Dict[str, Any] = Depends(require_tier("professional"))
) -> Dict[str, Any]:
    """Require professional tier access"""
    return validation


async def get_enterprise_access(
    validation: Dict[str, Any] = Depends(require_tier("enterprise"))
) -> Dict[str, Any]:
    """Require enterprise tier access"""
    return validation


async def get_ai_access(
    validation: Dict[str, Any] = Depends(require_feature("ai_insights"))
) -> Dict[str, Any]:
    """Require AI features access"""
    return validation


async def startup_validation():
    """Validate configuration during application startup"""
    logger.info("Validating application configuration...")

    if not config_validator.validate_environment():
        logger.error("Configuration validation failed!")
        for error in config_validator.validation_errors:
            logger.error(f"  ❌ {error}")
        raise RuntimeError("Invalid configuration detected")

    if config_validator.warnings:
        logger.warning("Configuration warnings detected:")
        for warning in config_validator.warnings:
            logger.warning(f"  ⚠️  {warning}")

    logger.info("✅ Configuration validation completed successfully")


# Export commonly used dependencies
__all__ = [
    "get_supabase_client",
    "get_elasticsearch_client",
    "get_database_dependencies",
    "check_api_health",
    "validate_request_permissions",
    "require_tier",
    "require_feature",
    "get_professional_access",
    "get_enterprise_access",
    "get_ai_access",
    "startup_validation",
    "config_validator",
    "rate_limit_tracker"
]