"""
Authentication middleware for Planning Explorer API
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.core.config import settings
from app.db.supabase import supabase_client
from app.models.user import UserProfile

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)


class AuthenticationError(HTTPException):
    """Custom authentication error"""

    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationError(HTTPException):
    """Custom authorization error"""

    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class AuthMiddleware:
    """Authentication and authorization middleware"""

    def __init__(self):
        self.algorithm = settings.algorithm
        self.secret_key = settings.secret_key

    async def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify JWT token and return user data

        Args:
            token: JWT access token

        Returns:
            Dict containing user data

        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            # First try to decode with our secret (for locally issued tokens)
            try:
                payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
                user_id = payload.get("sub")
                if user_id is None:
                    raise AuthenticationError("Invalid token payload")

                # Get user from database
                user_profile = await supabase_client.get_user_profile(user_id)
                if not user_profile:
                    raise AuthenticationError("User not found")

                return {
                    "user_id": user_id,
                    "user_profile": user_profile,
                    "token_payload": payload
                }

            except JWTError:
                # If local decode fails, try Supabase token validation
                supabase_user = await supabase_client.get_user_by_token(token)
                if not supabase_user or not supabase_user.get("success"):
                    raise AuthenticationError("Invalid or expired token")

                user_data = supabase_user["user"]
                user_id = user_data.id

                # Get or create user profile
                user_profile = await supabase_client.get_user_profile(user_id)
                if not user_profile:
                    # Create profile if it doesn't exist
                    user_profile = await supabase_client.create_user_profile(
                        user_id=user_id,
                        email=user_data.email,
                        full_name=user_data.user_metadata.get("full_name"),
                        company=user_data.user_metadata.get("company")
                    )

                return {
                    "user_id": user_id,
                    "user_profile": user_profile,
                    "supabase_user": user_data
                }

        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise AuthenticationError("Token verification failed")

    async def create_access_token(self, user_id: str, extra_data: Optional[Dict] = None) -> str:
        """
        Create JWT access token

        Args:
            user_id: User identifier
            extra_data: Additional data to include in token

        Returns:
            JWT access token string
        """
        try:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

            payload = {
                "sub": user_id,
                "exp": expire,
                "iat": datetime.utcnow(),
                "type": "access"
            }

            if extra_data:
                payload.update(extra_data)

            return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

        except Exception as e:
            logger.error(f"Token creation failed: {str(e)}")
            raise AuthenticationError("Token creation failed")

    def check_role_permission(self, user_role: str, required_role: str) -> bool:
        """
        Check if user role has required permissions

        Args:
            user_role: User's current role
            required_role: Required role for operation

        Returns:
            bool: True if user has permission
        """
        role_hierarchy = {
            "free": 1,
            "professional": 2,
            "enterprise": 3,
            "admin": 4
        }

        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 1)

        return user_level >= required_level

    def check_subscription_tier(self, user_tier: str, required_tier: str) -> bool:
        """
        Check if user subscription tier meets requirements

        Args:
            user_tier: User's current subscription tier
            required_tier: Required subscription tier

        Returns:
            bool: True if user has required tier or higher
        """
        tier_hierarchy = {
            "free": 0,
            "professional": 1,
            "enterprise": 2
        }

        user_level = tier_hierarchy.get(user_tier, 0)
        required_level = tier_hierarchy.get(required_tier, 0)

        return user_level >= required_level

    async def check_feature_access(self, user_profile: UserProfile, feature: str) -> bool:
        """
        Check if user has access to a specific feature based on subscription

        Args:
            user_profile: User profile
            feature: Feature name

        Returns:
            bool: True if user has access
        """
        feature_requirements = {
            "advanced_search": "free",
            "saved_searches": "free",
            "basic_alerts": "free",
            "ai_insights": "professional",
            "custom_reports": "professional",
            "advanced_alerts": "professional",
            "api_access": "professional",
            "bulk_exports": "enterprise",
            "custom_integrations": "enterprise",
            "priority_support": "enterprise"
        }

        required_tier = feature_requirements.get(feature, "enterprise")
        return self.check_subscription_tier(user_profile.subscription_tier, required_tier)

    async def check_usage_limits(self, user_profile: UserProfile, resource_type: str) -> bool:
        """
        Check if user has exceeded usage limits for a resource type

        Args:
            user_profile: User profile
            resource_type: Type of resource (saved_searches, alerts, api_calls)

        Returns:
            bool: True if within limits
        """
        if resource_type == "saved_searches":
            current_count = len(await supabase_client.get_user_saved_searches(user_profile.user_id))
            return current_count < user_profile.max_saved_searches
        elif resource_type == "alerts":
            current_count = len(await supabase_client.get_user_alerts(user_profile.user_id))
            return current_count < user_profile.max_alerts
        elif resource_type == "api_calls":
            return user_profile.api_calls_this_month < user_profile.max_api_calls_per_month

        return True

    async def check_rate_limit(self, user_id: str, endpoint: str) -> bool:
        """
        Check if user has exceeded rate limits

        Args:
            user_id: User identifier
            endpoint: API endpoint being accessed

        Returns:
            bool: True if within limits, False if exceeded
        """
        try:
            # Get user profile to check limits
            user_profile = await supabase_client.get_user_profile(user_id)
            if not user_profile:
                return False

            # Check monthly API call limit
            current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            # Count API calls this month
            # This would be implemented with a proper rate limiting service in production
            if user_profile.api_calls_this_month >= user_profile.max_api_calls_per_month:
                return False

            return True

        except Exception as e:
            logger.error(f"Rate limit check failed: {str(e)}")
            return True  # Allow request if check fails


# Global auth middleware instance
auth_middleware = AuthMiddleware()


# Dependency functions for FastAPI
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    Get current authenticated user

    Returns:
        Dict containing user data

    Raises:
        AuthenticationError: If authentication fails
    """
    if not credentials:
        raise AuthenticationError("Authentication required")

    return await auth_middleware.verify_token(credentials.credentials)


async def get_current_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> UserProfile:
    """
    Get current user profile

    Returns:
        UserProfile model
    """
    return current_user["user_profile"]


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    Get current user if authenticated, None otherwise

    Returns:
        Dict containing user data or None
    """
    if not credentials:
        return None

    try:
        return await auth_middleware.verify_token(credentials.credentials)
    except AuthenticationError:
        return None


def require_role(required_role: str):
    """
    Dependency factory for role-based access control

    Args:
        required_role: Minimum required role

    Returns:
        Dependency function
    """

    async def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_profile = current_user["user_profile"]

        if not auth_middleware.check_role_permission(user_profile.role, required_role):
            raise AuthorizationError(f"Required role: {required_role}")

        return current_user

    return role_checker


def require_subscription(min_tier: str):
    """
    Dependency factory for subscription-based access control

    Args:
        min_tier: Minimum subscription tier required

    Returns:
        Dependency function
    """

    async def subscription_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_profile = current_user["user_profile"]

        if not auth_middleware.check_subscription_tier(user_profile.subscription_tier, min_tier):
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"This feature requires {min_tier} subscription or higher. Current tier: {user_profile.subscription_tier}"
            )

        return current_user

    return subscription_checker


def require_feature_access(feature: str):
    """
    Dependency factory for feature-based access control

    Args:
        feature: Feature name that requires access check

    Returns:
        Dependency function
    """

    async def feature_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_profile = current_user["user_profile"]

        if not await auth_middleware.check_feature_access(user_profile, feature):
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"This feature is not available in your current subscription plan."
            )

        return current_user

    return feature_checker


def check_usage_limits(resource_type: str):
    """
    Dependency factory for usage limit checks

    Args:
        resource_type: Type of resource to check limits for

    Returns:
        Dependency function
    """

    async def limit_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_profile = current_user["user_profile"]

        if not await auth_middleware.check_usage_limits(user_profile, resource_type):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Usage limit exceeded for {resource_type}. Please upgrade your plan for higher limits."
            )

        return current_user

    return limit_checker


async def check_rate_limits(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Check rate limits for current user

    Args:
        request: FastAPI request object
        current_user: Current authenticated user

    Returns:
        Dict containing user data

    Raises:
        HTTPException: If rate limit exceeded
    """
    user_id = current_user["user_id"]
    endpoint = request.url.path

    if not await auth_middleware.check_rate_limit(user_id, endpoint):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please upgrade your plan for higher limits."
        )

    return current_user


# Middleware for logging API usage
async def log_api_request(
    request: Request,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Log API request for analytics and billing

    Args:
        request: FastAPI request object
        current_user: Current user if authenticated
    """
    try:
        if current_user:
            user_id = current_user["user_id"]

            # Log API usage
            usage_data = {
                "endpoint": request.url.path,
                "method": request.method,
                "query_parameters": dict(request.query_params),
                "billable": True,  # Most endpoints are billable
                "cost_credits": 1.0  # Default cost
            }

            await supabase_client.log_api_usage(user_id, usage_data)

            # Update user profile API call count
            user_profile = current_user["user_profile"]
            await supabase_client.update_user_profile(
                user_id,
                {"api_calls_this_month": user_profile.api_calls_this_month + 1}
            )

    except Exception as e:
        logger.error(f"Failed to log API request: {str(e)}")
        # Don't fail the request if logging fails


async def track_user_interaction(
    interaction_type: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    request: Optional[Request] = None,
    current_user: Optional[Dict[str, Any]] = None
):
    """
    Track user interaction for AI personalization

    Args:
        interaction_type: Type of interaction
        entity_type: Type of entity interacted with
        entity_id: ID of entity
        request: Request object
        current_user: Current user data
    """
    try:
        if current_user:
            user_id = current_user["user_id"]

            interaction_data = {
                "interaction_type": interaction_type,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "context_data": {},
                "session_id": request.headers.get("x-session-id") if request else None,
                "timestamp_utc": datetime.utcnow().isoformat()
            }

            if request:
                interaction_data["context_data"] = {
                    "endpoint": request.url.path,
                    "method": request.method,
                    "query_params": dict(request.query_params),
                    "user_agent": request.headers.get("user-agent"),
                    "ip_address": request.client.host if request.client else None
                }

            await supabase_client.log_user_event(
                user_id=user_id,
                event_data={
                    "event_type": interaction_type,
                    "event_data": interaction_data
                }
            )

    except Exception as e:
        logger.error(f"Failed to track user interaction: {str(e)}")
        # Don't fail the request if tracking fails


# Convenience dependencies
async def get_professional_user(current_user: Dict[str, Any] = Depends(require_subscription("professional"))) -> UserProfile:
    """Get current user - requires professional subscription"""
    return current_user["user_profile"]


async def get_enterprise_user(current_user: Dict[str, Any] = Depends(require_subscription("enterprise"))) -> UserProfile:
    """Get current user - requires enterprise subscription"""
    return current_user["user_profile"]


async def get_admin_user(current_user: Dict[str, Any] = Depends(require_role("admin"))) -> UserProfile:
    """Get current user - requires admin role"""
    return current_user["user_profile"]