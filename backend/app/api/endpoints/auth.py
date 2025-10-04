"""
Authentication endpoints for Planning Explorer API
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials

from app.db.supabase import supabase_client
from app.middleware.auth import auth_middleware, security, get_current_user_profile
from app.models.user import (
    UserRegistrationRequest, UserLoginRequest, AuthResponse, UserProfile,
    UserUpdateRequest, UserStatsResponse, UserRole
)

router = APIRouter()


@router.post("/auth/register", response_model=AuthResponse)
async def register_user(
    registration_data: UserRegistrationRequest,
    request: Request
):
    """
    Register a new user

    Creates a new user account with Supabase authentication and user profile.

    **Registration Requirements:**
    - Valid email address (used as username)
    - Password minimum 8 characters
    - Optional full name and company information
    - Default role is 'free' tier

    **Response includes:**
    - JWT access token for API authentication
    - User profile information
    - Token expiration details
    """
    try:
        # Prepare user metadata
        user_metadata = {
            "full_name": registration_data.full_name,
            "company": registration_data.company,
            "role": registration_data.role.value
        }

        # Register user with Supabase
        result = await supabase_client.sign_up_user(
            email=registration_data.email,
            password=registration_data.password,
            user_data=user_metadata
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Registration failed")
            )

        user = result["user"]
        session = result["session"]

        # Get user profile
        user_profile = await supabase_client.get_user_profile(user.id)

        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user profile"
            )

        # Create local access token
        access_token = await auth_middleware.create_access_token(
            user_id=user.id,
            extra_data={"email": user.email, "role": user_profile.role}
        )

        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=3600,  # 1 hour
            user=user_profile,
            refresh_token=session.refresh_token if session else None
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/auth/login", response_model=AuthResponse)
async def login_user(
    login_data: UserLoginRequest,
    request: Request
):
    """
    Authenticate user and get access token

    Authenticates user credentials and returns JWT token for API access.

    **Login Process:**
    - Validates email and password with Supabase
    - Updates last login timestamp
    - Returns JWT access token
    - Includes user profile information
    """
    try:
        # Authenticate with Supabase
        result = await supabase_client.sign_in_user(
            email=login_data.email,
            password=login_data.password
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        user = result["user"]
        session = result["session"]

        # Get user profile
        user_profile = await supabase_client.get_user_profile(user.id)

        if not user_profile:
            # Create profile if it doesn't exist (legacy users)
            user_profile = await supabase_client.create_user_profile(
                user_id=user.id,
                email=user.email,
                full_name=user.user_metadata.get("full_name"),
                company=user.user_metadata.get("company"),
                role=user.user_metadata.get("role", "free")
            )

        # Create local access token
        access_token = await auth_middleware.create_access_token(
            user_id=user.id,
            extra_data={"email": user.email, "role": user_profile.role}
        )

        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=3600,  # 1 hour
            user=user_profile,
            refresh_token=session.refresh_token if session else None
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/auth/logout")
async def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Sign out current user

    Invalidates the current session and access token.
    """
    try:
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )

        # Sign out with Supabase
        success = await supabase_client.sign_out_user(credentials.credentials)

        if success:
            return {"message": "Successfully logged out"}
        else:
            return {"message": "Logout completed (token may have been expired)"}

    except Exception as e:
        # Don't fail logout even if there's an error
        return {"message": "Logout completed"}


@router.get("/auth/user", response_model=UserProfile)
async def get_current_user(
    current_user_profile: UserProfile = Depends(get_current_user_profile)
):
    """
    Get current user profile

    Returns detailed profile information for the authenticated user.

    **Includes:**
    - Personal information (name, email, company)
    - Subscription role and limits
    - Usage statistics
    - Preferences and settings
    """
    return current_user_profile


@router.put("/auth/user", response_model=UserProfile)
async def update_user_profile(
    update_data: UserUpdateRequest,
    current_user_profile: UserProfile = Depends(get_current_user_profile)
):
    """
    Update current user profile

    Updates user profile information including personal details and preferences.

    **Updatable Fields:**
    - Full name
    - Company name
    - Phone number
    - Notification preferences
    """
    try:
        # Prepare update data
        update_dict = update_data.dict(exclude_unset=True)

        if not update_dict:
            return current_user_profile

        # Update profile in database
        updated_profile = await supabase_client.update_user_profile(
            user_id=current_user_profile.user_id,
            data=update_dict
        )

        if not updated_profile:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user profile"
            )

        return updated_profile

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile update failed: {str(e)}"
        )


@router.get("/auth/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user_profile: UserProfile = Depends(get_current_user_profile)
):
    """
    Get user account statistics

    Returns comprehensive statistics about user activity and usage.

    **Statistics Include:**
    - Total searches performed
    - Saved searches and alerts
    - Reports generated
    - API usage this month
    - Subscription plan utilization
    """
    try:
        # Get user statistics from database
        stats = await supabase_client.get_user_stats(current_user_profile.user_id)

        # Calculate plan usage
        plan_usage = {
            "api_calls": {
                "used": current_user_profile.api_calls_this_month,
                "limit": current_user_profile.max_api_calls_per_month,
                "percentage": (current_user_profile.api_calls_this_month / current_user_profile.max_api_calls_per_month * 100) if current_user_profile.max_api_calls_per_month > 0 else 0
            },
            "saved_searches": {
                "used": stats.get("saved_searches", 0),
                "limit": current_user_profile.max_saved_searches
            },
            "alerts": {
                "used": stats.get("active_alerts", 0),
                "limit": current_user_profile.max_alerts
            }
        }

        return UserStatsResponse(
            total_searches=current_user_profile.searches_this_month + stats.get("saved_searches", 0),
            saved_searches=stats.get("saved_searches", 0),
            active_alerts=stats.get("active_alerts", 0),
            reports_generated=stats.get("reports_generated", 0),
            api_calls_this_month=current_user_profile.api_calls_this_month,
            plan_usage=plan_usage,
            created_at=current_user_profile.created_at,
            last_login=current_user_profile.last_login
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user statistics: {str(e)}"
        )


@router.post("/auth/refresh")
async def refresh_token(
    refresh_token: str
):
    """
    Refresh access token

    Uses refresh token to get a new access token without re-authentication.
    """
    try:
        # This would be implemented with Supabase refresh token logic
        # For now, return an error message
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Token refresh not implemented yet. Please login again."
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )


@router.delete("/auth/account")
async def delete_account(
    current_user_profile: UserProfile = Depends(get_current_user_profile),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Delete user account

    **WARNING:** This permanently deletes the user account and all associated data.

    **Data Deleted:**
    - User profile and settings
    - Saved searches and alerts
    - Generated reports
    - API usage history
    - All user-specific data

    This action cannot be undone.
    """
    try:
        # This would implement complete account deletion
        # For now, return a placeholder response
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Account deletion not implemented yet. Please contact support."
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Account deletion failed: {str(e)}"
        )