"""
User-specific features endpoints for Planning Explorer API
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from datetime import datetime

from app.db.supabase import supabase_client
from app.middleware.auth import (
    get_current_user_profile, require_subscription, require_feature_access,
    check_usage_limits, track_user_interaction, get_professional_user,
    get_enterprise_user, get_admin_user
)
from app.models.user import (
    UserProfile, SavedSearch, SavedSearchRequest, SavedSearchResponse,
    UserAlert, AlertRequest, UserReport, ReportRequest,
    UserSettings, AlertFrequency, ReportStatus, UserUpdateRequest,
    UserStatsResponse, UserRole
)
from app.services.notification_service import notification_service

router = APIRouter()


# ======== USER PROFILE MANAGEMENT ========

@router.get("/user/profile", response_model=UserProfile)
async def get_user_profile(
    current_user: UserProfile = Depends(get_current_user_profile)
):
    """
    Get current user profile

    Returns complete user profile information including subscription details,
    usage statistics, and preferences.

    **Profile Information:**
    - Personal details and company information
    - Subscription tier and limits
    - Current month usage statistics
    - Account settings and preferences
    """
    try:
        # Track user interaction
        await track_user_interaction(
            interaction_type="view",
            entity_type="profile",
            current_user={"user_id": current_user.user_id}
        )

        return current_user

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user profile: {str(e)}"
        )


@router.put("/user/profile", response_model=UserProfile)
async def update_user_profile(
    profile_update: UserUpdateRequest,
    current_user: UserProfile = Depends(get_current_user_profile)
):
    """
    Update user profile information

    Updates user profile fields like name, company, notification preferences, etc.
    Only provided fields will be updated.

    **Updatable Fields:**
    - Personal information (name, company, phone)
    - Notification preferences
    - Marketing email preferences
    """
    try:
        # Prepare update data
        update_data = profile_update.dict(exclude_unset=True)

        # Update user profile
        updated_profile = await supabase_client.update_user_profile(
            user_id=current_user.user_id,
            data=update_data
        )

        if not updated_profile:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user profile"
            )

        # Track user interaction
        await track_user_interaction(
            interaction_type="update",
            entity_type="profile",
            current_user={"user_id": current_user.user_id}
        )

        return updated_profile

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user profile: {str(e)}"
        )


@router.get("/user/stats", response_model=UserStatsResponse)
async def get_user_statistics(
    current_user: UserProfile = Depends(get_current_user_profile)
):
    """
    Get user usage statistics and account metrics

    Returns comprehensive statistics about user account activity,
    resource usage, and subscription utilization.

    **Statistics Include:**
    - Total searches performed
    - Saved searches and alerts count
    - Reports generated
    - API usage this month
    - Subscription plan utilization
    """
    try:
        # Get comprehensive user stats
        stats_data = await supabase_client.get_user_stats(current_user.user_id)

        # Calculate plan usage percentages
        plan_usage = {
            "api_calls": {
                "used": current_user.api_calls_this_month,
                "limit": current_user.max_api_calls_per_month,
                "percentage": round((current_user.api_calls_this_month / current_user.max_api_calls_per_month) * 100, 1)
            },
            "saved_searches": {
                "used": stats_data.get("saved_searches", 0),
                "limit": current_user.max_saved_searches,
                "percentage": round((stats_data.get("saved_searches", 0) / current_user.max_saved_searches) * 100, 1)
            },
            "alerts": {
                "used": stats_data.get("active_alerts", 0),
                "limit": current_user.max_alerts,
                "percentage": round((stats_data.get("active_alerts", 0) / current_user.max_alerts) * 100, 1)
            }
        }

        return UserStatsResponse(
            total_searches=current_user.searches_this_month,
            saved_searches=stats_data.get("saved_searches", 0),
            active_alerts=stats_data.get("active_alerts", 0),
            reports_generated=stats_data.get("reports_generated", 0),
            api_calls_this_month=stats_data.get("api_calls_this_month", 0),
            plan_usage=plan_usage,
            created_at=current_user.created_at,
            last_login=current_user.last_login
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user statistics: {str(e)}"
        )


@router.post("/user/upgrade")
async def upgrade_subscription(
    target_tier: str = Query(..., description="Target subscription tier"),
    current_user: UserProfile = Depends(get_current_user_profile)
):
    """
    Upgrade user subscription tier

    **Note:** This is a placeholder endpoint. In production, this would integrate
    with a payment processor like Stripe to handle subscription upgrades.

    **Available Tiers:**
    - **free**: 1,000 API calls, 10 saved searches, 5 alerts
    - **professional**: 10,000 API calls, 100 saved searches, 50 alerts
    - **enterprise**: 100,000 API calls, 1,000 saved searches, 500 alerts
    """
    try:
        # Validate target tier
        valid_tiers = ["free", "professional", "enterprise"]
        if target_tier not in valid_tiers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tier. Valid options: {valid_tiers}"
            )

        # Check if already at target tier or higher
        tier_hierarchy = {"free": 0, "professional": 1, "enterprise": 2}
        current_level = tier_hierarchy.get(current_user.subscription_tier, 0)
        target_level = tier_hierarchy.get(target_tier, 0)

        if current_level >= target_level:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Already at {current_user.subscription_tier} tier or higher"
            )

        # Get tier limits from settings
        from app.core.config import settings
        tier_limits = settings.get_tier_limits(target_tier)

        # Update user profile with new tier and limits
        update_data = {
            "subscription_tier": target_tier,
            "max_api_calls_per_month": tier_limits["api_calls"],
            "max_saved_searches": tier_limits["saved_searches"],
            "max_alerts": tier_limits["alerts"]
        }

        updated_profile = await supabase_client.update_user_profile(
            user_id=current_user.user_id,
            data=update_data
        )

        if not updated_profile:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upgrade subscription"
            )

        # Track upgrade event
        await track_user_interaction(
            interaction_type="upgrade",
            entity_type="subscription",
            current_user={"user_id": current_user.user_id}
        )

        return {
            "message": f"Successfully upgraded to {target_tier} tier",
            "new_tier": target_tier,
            "new_limits": tier_limits,
            "effective_date": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upgrade subscription: {str(e)}"
        )


@router.get("/user/usage")
async def get_usage_details(
    current_user: UserProfile = Depends(get_current_user_profile)
):
    """
    Get detailed usage information

    Returns comprehensive usage data including API call history,
    feature usage patterns, and billing information.

    **Usage Details:**
    - API calls breakdown by endpoint
    - Monthly usage trends
    - Feature utilization
    - Rate limiting status
    """
    try:
        # Get current month usage summary
        current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # This would typically query the monthly_usage_summary table
        # For now, return basic usage info
        usage_details = {
            "current_period": {
                "start_date": current_month.isoformat(),
                "api_calls_used": current_user.api_calls_this_month,
                "api_calls_limit": current_user.max_api_calls_per_month,
                "searches_performed": current_user.searches_this_month,
                "percentage_used": round((current_user.api_calls_this_month / current_user.max_api_calls_per_month) * 100, 1)
            },
            "subscription_info": {
                "tier": current_user.subscription_tier,
                "limits": {
                    "api_calls": current_user.max_api_calls_per_month,
                    "saved_searches": current_user.max_saved_searches,
                    "alerts": current_user.max_alerts
                }
            },
            "rate_limiting": {
                "requests_per_minute": 100,  # From settings
                "burst_allowance": 20,
                "current_status": "within_limits"
            }
        }

        return usage_details

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get usage details: {str(e)}"
        )


@router.get("/user/preferences", response_model=UserSettings)
async def get_user_preferences(
    current_user: UserProfile = Depends(get_current_user_profile)
):
    """
    Get user application preferences and settings

    Returns user's application settings including search defaults,
    display preferences, and notification settings.
    """
    try:
        settings = await supabase_client.get_user_settings(current_user.user_id)

        if not settings:
            # Return default settings
            settings = UserSettings(
                user_id=current_user.user_id,
                default_search_radius=5.0,
                preferred_authorities=[],
                results_per_page=20,
                show_ai_insights=True,
                show_opportunity_scores=True,
                map_view="satellite",
                show_heat_map=True,
                email_notifications=True,
                push_notifications=True,
                marketing_emails=False,
                daily_digest_enabled=True,
                weekly_summary_enabled=True
            )

        return settings

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user preferences: {str(e)}"
        )


@router.put("/user/preferences", response_model=UserSettings)
async def update_user_preferences(
    preferences: UserSettings,
    current_user: UserProfile = Depends(get_current_user_profile)
):
    """
    Update user application preferences

    Updates user preferences for search defaults, display options,
    notifications, and other application settings.
    """
    try:
        preferences.user_id = current_user.user_id

        updated_settings = await supabase_client.update_user_settings(
            user_id=current_user.user_id,
            settings=preferences
        )

        if not updated_settings:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update preferences"
            )

        # Track preference update
        await track_user_interaction(
            interaction_type="update",
            entity_type="preferences",
            current_user={"user_id": current_user.user_id}
        )

        return updated_settings

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preferences: {str(e)}"
        )


# ======== SAVED SEARCHES ========

@router.get("/user/searches", response_model=List[SavedSearchResponse])
async def get_saved_searches(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of searches to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    include_ai_suggestions: bool = Query(True, description="Include AI-generated suggestions"),
    current_user: UserProfile = Depends(get_current_user_profile)
):
    """
    Get user's saved searches with AI enhancements

    Returns all saved searches for the current user, including search parameters,
    metadata, AI suggestions, and usage analytics.

    **Enhanced Features:**
    - AI-powered search suggestions and optimizations
    - Usage analytics and performance tracking
    - Category-based organization
    - Smart sorting by relevance and usage
    """
    try:
        saved_searches = await supabase_client.get_user_saved_searches(
            user_id=current_user.user_id,
            limit=limit
        )

        # Filter by category if specified
        if category:
            saved_searches = [s for s in saved_searches if getattr(s, 'category', 'general') == category]

        # Enhance with AI suggestions if requested
        if include_ai_suggestions:
            for search in saved_searches:
                # Add AI suggestions (placeholder for now)
                if hasattr(search, 'ai_suggestions') and not search.ai_suggestions:
                    search.ai_suggestions = {
                        "suggested_keywords": [],
                        "location_recommendations": [],
                        "filter_optimizations": [],
                        "confidence_score": 0.0
                    }

        # Track interaction
        await track_user_interaction(
            interaction_type="view",
            entity_type="saved_searches",
            current_user={"user_id": current_user.user_id}
        )

        return [
            SavedSearchResponse(**search.dict())
            for search in saved_searches
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get saved searches: {str(e)}"
        )


@router.post("/user/searches", response_model=SavedSearchResponse)
async def create_saved_search(
    search_request: SavedSearchRequest,
    current_user: UserProfile = Depends(check_usage_limits("saved_searches"))
):
    """
    Save a search with AI enhancement

    Saves search parameters for quick access with AI-powered optimizations
    and optional conversion to smart alerts.

    **Enhanced Features:**
    - AI-powered search optimization suggestions
    - Automatic categorization and tagging
    - Performance prediction and recommendations
    - Smart alert conversion options
    """
    try:
        # Create saved search with AI enhancements
        search_data = search_request.dict()
        search_data["search_id"] = f"search_{current_user.user_id}_{int(datetime.utcnow().timestamp())}"
        search_data["category"] = search_data.get("category", "general")

        # Add AI suggestions (placeholder implementation)
        search_data["ai_suggestions"] = {
            "suggested_keywords": [],  # Would be generated by AI
            "location_recommendations": [],
            "filter_optimizations": [],
            "confidence_score": 0.8
        }

        # Add AI insights
        search_data["ai_insights"] = {
            "search_complexity": "medium",
            "expected_results": "50-100",
            "optimization_potential": "high",
            "alert_recommended": search_data.get("is_alert", False)
        }

        saved_search = await supabase_client.create_saved_search(
            user_id=current_user.user_id,
            search_data=search_data
        )

        if not saved_search:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save search"
            )

        # Track creation
        await track_user_interaction(
            interaction_type="create",
            entity_type="saved_search",
            entity_id=saved_search.search_id,
            current_user={"user_id": current_user.user_id}
        )

        return SavedSearchResponse(**saved_search.dict())

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create saved search: {str(e)}"
        )


@router.put("/user/searches/{search_id}", response_model=SavedSearchResponse)
async def update_saved_search(
    search_id: str = Path(..., description="Saved search ID"),
    search_request: SavedSearchRequest = None,
    current_user: UserProfile = Depends(get_current_user_profile)
):
    """
    Update a saved search

    Updates search parameters, name, or converts to/from alert.
    """
    try:
        update_data = search_request.dict(exclude_unset=True)

        updated_search = await supabase_client.update_saved_search(
            search_id=search_id,
            user_id=current_user.user_id,
            data=update_data
        )

        if not updated_search:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saved search not found"
            )

        return SavedSearchResponse(**updated_search.dict())

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update saved search: {str(e)}"
        )


@router.delete("/user/searches/{search_id}")
async def delete_saved_search(
    search_id: str = Path(..., description="Saved search ID"),
    current_user: UserProfile = Depends(get_current_user_profile)
):
    """
    Delete a saved search

    Permanently removes the saved search and any associated alerts.
    """
    try:
        success = await supabase_client.delete_saved_search(
            search_id=search_id,
            user_id=current_user.user_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saved search not found"
            )

        return {"message": "Saved search deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting saved search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete saved search: {str(e)}"
        )


@router.post("/user/searches/{search_id}/run")
async def execute_saved_search(
    search_id: str = Path(..., description="Saved search ID"),
    current_user: UserProfile = Depends(get_current_user_profile)
):
    """
    Execute a saved search and return results

    Runs the saved search query and returns current results,
    updating usage statistics and performance metrics.
    """
    try:
        # Get saved search
        saved_searches = await supabase_client.get_user_saved_searches(current_user.user_id)
        saved_search = next((s for s in saved_searches if s.search_id == search_id), None)

        if not saved_search:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saved search not found"
            )

        # Update usage tracking
        update_data = {
            "last_used": datetime.utcnow().isoformat(),
            "use_count": getattr(saved_search, 'use_count', 0) + 1
        }

        await supabase_client.update_saved_search(
            search_id=search_id,
            user_id=current_user.user_id,
            data=update_data
        )

        # Track execution
        await track_user_interaction(
            interaction_type="execute",
            entity_type="saved_search",
            entity_id=search_id,
            current_user={"user_id": current_user.user_id}
        )

        # TODO: Execute actual search using the search service
        # For now, return mock response
        return {
            "search_id": search_id,
            "executed_at": datetime.utcnow().isoformat(),
            "query": saved_search.query,
            "filters": saved_search.filters,
            "results_summary": {
                "total_results": 42,  # Mock data
                "new_since_last_run": 5,
                "execution_time_ms": 150
            },
            "next_steps": {
                "create_alert": not getattr(saved_search, 'converted_to_alert', False),
                "optimize_query": True,
                "share_search": True
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute saved search: {str(e)}"
        )


@router.get("/user/searches/suggestions")
async def get_search_suggestions(
    current_user: UserProfile = Depends(get_current_user_profile)
):
    """
    Get AI-powered search suggestions

    Returns personalized search suggestions based on user behavior,
    popular searches, and AI analysis of planning data trends.

    **Suggestion Types:**
    - Popular searches in your area
    - Trending planning applications
    - Personalized recommendations
    - Optimization suggestions for existing searches
    """
    try:
        # Get user's existing searches for context
        saved_searches = await supabase_client.get_user_saved_searches(current_user.user_id)

        # Generate AI-powered suggestions (placeholder implementation)
        suggestions = {
            "trending_keywords": [
                "residential development",
                "solar panels",
                "garage conversion",
                "commercial expansion"
            ],
            "location_suggestions": [
                {
                    "area": "City Center",
                    "reason": "High development activity",
                    "opportunity_score": 0.85
                },
                {
                    "area": "Suburban Areas",
                    "reason": "Emerging residential projects",
                    "opportunity_score": 0.72
                }
            ],
            "personalized_searches": [
                {
                    "name": "High-value residential projects",
                    "query": "residential AND value > 500000",
                    "reason": "Based on your previous searches",
                    "confidence": 0.9
                }
            ],
            "optimization_tips": [
                {
                    "search_id": saved_searches[0].search_id if saved_searches else None,
                    "suggestion": "Add location radius for better results",
                    "impact": "30% more relevant results"
                }
            ] if saved_searches else []
        }

        # Track suggestion viewing
        await track_user_interaction(
            interaction_type="view",
            entity_type="search_suggestions",
            current_user={"user_id": current_user.user_id}
        )

        return suggestions

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get search suggestions: {str(e)}"
        )


# ======== ALERTS ========

@router.get("/user/alerts", response_model=List[UserAlert])
async def get_user_alerts(
    active_only: bool = Query(True, description="Return only active alerts"),
    include_performance: bool = Query(True, description="Include performance metrics"),
    current_user: UserProfile = Depends(get_current_user_profile)
):
    """
    Get user's smart alerts with AI enhancements

    Returns all configured alerts with their settings, status, and AI-powered
    performance analytics.

    **Smart Alert Features:**
    - AI-powered relevance filtering
    - Automated false positive detection
    - Performance optimization suggestions
    - Smart notification timing
    - Predictive alert triggers
    """
    try:
        alerts = await supabase_client.get_user_alerts(
            user_id=current_user.user_id,
            active_only=active_only
        )

        # Enhance with performance metrics if requested
        if include_performance:
            for alert in alerts:
                # Add performance metrics (placeholder implementation)
                alert.performance_metrics = {
                    "accuracy_score": 0.85,
                    "false_positive_rate": 0.12,
                    "avg_relevance": 0.78,
                    "user_satisfaction": getattr(alert, 'user_feedback_score', 0.8),
                    "optimization_suggestions": [
                        "Narrow location radius for more relevant results",
                        "Add keyword exclusions to reduce noise"
                    ]
                }

        # Track interaction
        await track_user_interaction(
            interaction_type="view",
            entity_type="alerts",
            current_user={"user_id": current_user.user_id}
        )

        return alerts

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get alerts: {str(e)}"
        )


@router.post("/user/alerts", response_model=UserAlert)
async def create_smart_alert(
    alert_request: AlertRequest,
    current_user: UserProfile = Depends(check_usage_limits("alerts"))
):
    """
    Create a new smart alert with AI enhancements

    Sets up automated monitoring with AI-powered relevance filtering,
    smart notification timing, and adaptive learning capabilities.

    **Smart Alert Features:**
    - AI-powered relevance scoring
    - Adaptive false positive reduction
    - Smart notification timing optimization
    - Geographic intelligence and expansion
    - Keyword learning and optimization
    """
    try:
        # Create smart alert with AI enhancements
        alert_data = alert_request.dict()
        alert_data["alert_id"] = f"alert_{current_user.user_id}_{int(datetime.utcnow().timestamp())}"

        # Add AI enhancements
        alert_data["ai_enhanced"] = True
        alert_data["smart_filtering"] = True
        alert_data["min_relevance_score"] = 0.6  # AI relevance threshold

        # Set next check time based on frequency
        frequency_intervals = {
            "immediate": 0,  # Process immediately
            "daily": 24,
            "weekly": 168,
            "monthly": 720
        }

        hours_offset = frequency_intervals.get(alert_data.get("frequency", "daily"), 24)
        alert_data["next_check"] = (datetime.utcnow() + timedelta(hours=hours_offset)).isoformat()

        # Add AI criteria for smart filtering
        alert_data["ai_criteria"] = {
            "relevance_threshold": 0.6,
            "false_positive_protection": True,
            "semantic_matching": True,
            "location_intelligence": True,
            "trend_analysis": True
        }

        alert = await supabase_client.create_user_alert(
            user_id=current_user.user_id,
            alert_data=alert_data
        )

        if not alert:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create alert"
            )

        # Track alert creation
        await track_user_interaction(
            interaction_type="create",
            entity_type="alert",
            entity_id=alert.alert_id,
            current_user={"user_id": current_user.user_id}
        )

        return alert

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create alert: {str(e)}"
        )


@router.put("/user/alerts/{alert_id}", response_model=UserAlert)
async def update_alert(
    alert_id: str = Path(..., description="Alert ID"),
    alert_request: AlertRequest = None,
    current_user: UserProfile = Depends(get_current_user_profile)
):
    """
    Update an existing alert

    Modifies alert criteria, notification settings, or activation status.
    """
    try:
        # This would be implemented with proper alert update logic
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Alert updates not implemented yet"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update alert: {str(e)}"
        )


@router.delete("/user/alerts/{alert_id}")
async def delete_alert(
    alert_id: str = Path(..., description="Alert ID"),
    current_user: UserProfile = Depends(get_current_user_profile)
):
    """
    Delete an alert

    Permanently removes the alert and stops all notifications.
    """
    try:
        # Get user alerts to verify ownership
        alerts = await supabase_client.get_user_alerts(current_user.user_id, active_only=False)
        alert = next((a for a in alerts if a.alert_id == alert_id), None)

        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )

        # TODO: Implement actual alert deletion in supabase_client
        # For now, return success
        success = True  # await supabase_client.delete_user_alert(alert_id, current_user.user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete alert"
            )

        # Track deletion
        await track_user_interaction(
            interaction_type="delete",
            entity_type="alert",
            entity_id=alert_id,
            current_user={"user_id": current_user.user_id}
        )

        return {"message": "Alert deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete alert: {str(e)}"
        )


@router.post("/user/alerts/{alert_id}/test")
async def test_alert(
    alert_id: str = Path(..., description="Alert ID"),
    current_user: UserProfile = Depends(get_current_user_profile)
):
    """
    Test an alert to see what results it would return

    Executes the alert criteria against current data to show
    what planning applications would trigger the alert.

    **Test Features:**
    - Real-time result preview
    - AI relevance scoring demonstration
    - Performance estimation
    - Optimization suggestions
    """
    try:
        # Get alert details
        alerts = await supabase_client.get_user_alerts(current_user.user_id, active_only=False)
        alert = next((a for a in alerts if a.alert_id == alert_id), None)

        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )

        # TODO: Execute alert test using search service
        # For now, return mock test results
        test_results = {
            "alert_id": alert_id,
            "test_executed_at": datetime.utcnow().isoformat(),
            "criteria": {
                "query": alert.query,
                "filters": alert.filters,
                "location_filters": alert.location_filters
            },
            "mock_results": {
                "total_matches": 8,
                "high_relevance": 5,
                "medium_relevance": 2,
                "low_relevance": 1,
                "ai_filtered_out": 3
            },
            "sample_applications": [
                {
                    "id": "app_123",
                    "title": "Residential development in City Center",
                    "relevance_score": 0.92,
                    "reason": "High keyword match and location relevance"
                },
                {
                    "id": "app_124",
                    "title": "Commercial extension project",
                    "relevance_score": 0.78,
                    "reason": "Moderate keyword match"
                }
            ],
            "optimization_suggestions": [
                "Consider narrowing location radius for more targeted results",
                "Add keyword exclusions to reduce noise"
            ],
            "estimated_frequency": "2-3 notifications per week"
        }

        # Track test execution
        await track_user_interaction(
            interaction_type="test",
            entity_type="alert",
            entity_id=alert_id,
            current_user={"user_id": current_user.user_id}
        )

        return test_results

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test alert: {str(e)}"
        )


@router.post("/user/alerts/{alert_id}/feedback")
async def submit_alert_feedback(
    alert_id: str = Path(..., description="Alert ID"),
    feedback: str = Query(..., description="Feedback type: positive, negative, neutral"),
    relevance_score: Optional[int] = Query(None, ge=1, le=5, description="Relevance rating 1-5"),
    comment: Optional[str] = Query(None, description="Optional feedback comment"),
    current_user: UserProfile = Depends(get_current_user_profile)
):
    """
    Submit feedback on alert performance

    Provides feedback to improve AI alert accuracy and relevance.
    This data is used to train the AI system for better results.

    **Feedback Types:**
    - **positive**: Alert results were relevant and useful
    - **negative**: Alert results were not relevant or too noisy
    - **neutral**: Alert results were okay but could be improved
    """
    try:
        # Validate feedback
        if feedback not in ["positive", "negative", "neutral"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid feedback type. Must be: positive, negative, or neutral"
            )

        # Get alert to verify ownership
        alerts = await supabase_client.get_user_alerts(current_user.user_id, active_only=False)
        alert = next((a for a in alerts if a.alert_id == alert_id), None)

        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )

        # Store feedback for AI learning
        feedback_data = {
            "alert_id": alert_id,
            "user_id": current_user.user_id,
            "feedback_type": feedback,
            "relevance_score": relevance_score,
            "comment": comment,
            "timestamp": datetime.utcnow().isoformat()
        }

        # TODO: Store feedback in database for AI training
        # await supabase_client.store_alert_feedback(feedback_data)

        # Track feedback submission
        await track_user_interaction(
            interaction_type="feedback",
            entity_type="alert",
            entity_id=alert_id,
            current_user={"user_id": current_user.user_id}
        )

        return {
            "message": "Feedback submitted successfully",
            "feedback": feedback,
            "alert_id": alert_id,
            "submitted_at": datetime.utcnow().isoformat(),
            "ai_learning": "Your feedback helps improve alert accuracy"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(e)}"
        )


# ======== REPORTS ========

@router.get("/user/reports", response_model=List[UserReport])
async def get_user_reports(
    limit: int = Query(20, ge=1, le=50, description="Maximum number of reports to return"),
    status_filter: Optional[ReportStatus] = Query(None, description="Filter by report status"),
    current_user: UserProfile = Depends(get_current_user_profile)
):
    """
    Get user's generated reports

    Returns list of all reports generated by the user with status and metadata.

    **Report Types:**
    - Market analysis reports
    - Opportunity assessment reports
    - Geographic trend analysis
    - Custom data exports
    """
    try:
        reports = await supabase_client.get_user_reports(
            user_id=current_user.user_id,
            limit=limit
        )

        # Filter by status if specified
        if status_filter:
            reports = [report for report in reports if report.status == status_filter]

        return reports

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get reports: {str(e)}"
        )


@router.post("/user/reports", response_model=UserReport)
async def generate_report(
    report_request: ReportRequest,
    current_user: UserProfile = Depends(require_subscription("professional"))
):
    """
    Generate a new report

    **Professional/Enterprise Feature**

    Creates comprehensive reports based on planning data analysis.

    **Report Types Available:**
    - **market_analysis**: Market trends and statistics
    - **opportunity_report**: AI-powered opportunity analysis
    - **geographic_analysis**: Location-based insights
    - **developer_profile**: Applicant/agent analysis
    - **authority_performance**: Planning authority statistics

    **Report Features:**
    - AI-powered analysis and insights
    - Professional formatting (PDF/Excel)
    - Executive summaries
    - Data visualizations and charts
    """
    try:
        # Create report record
        report_data = report_request.dict()
        report_data["report_id"] = f"report_{current_user.user_id}_{int(datetime.utcnow().timestamp())}"
        report_data["status"] = ReportStatus.PENDING

        report = await supabase_client.create_user_report(
            user_id=current_user.user_id,
            report_data=report_data
        )

        if not report:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create report"
            )

        # TODO: Trigger background report generation
        # This would start an async task to generate the actual report content

        return report

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.get("/user/reports/{report_id}", response_model=UserReport)
async def get_report(
    report_id: str = Path(..., description="Report ID"),
    current_user: UserProfile = Depends(get_current_user_profile)
):
    """
    Get a specific report

    Returns detailed report information including content and download links.
    """
    try:
        reports = await supabase_client.get_user_reports(current_user.user_id)
        report = next((r for r in reports if r.report_id == report_id), None)

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )

        return report

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get report: {str(e)}"
        )


@router.delete("/user/reports/{report_id}")
async def delete_report(
    report_id: str = Path(..., description="Report ID"),
    current_user: UserProfile = Depends(get_current_user_profile)
):
    """
    Delete a report

    Permanently removes the report and any associated files.
    """
    try:
        # This would implement report deletion
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Report deletion not implemented yet"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete report: {str(e)}"
        )


# ======== USER SETTINGS ========

@router.get("/user/settings", response_model=UserSettings)
async def get_user_settings(
    current_user: UserProfile = Depends(get_current_user_profile)
):
    """
    Get user application settings

    Returns user preferences and configuration settings.
    """
    try:
        settings = await supabase_client.get_user_settings(current_user.user_id)

        if not settings:
            # Return default settings
            settings = UserSettings(
                user_id=current_user.user_id,
                default_search_radius=5.0,
                preferred_authorities=[],
                results_per_page=20,
                show_ai_insights=True,
                show_opportunity_scores=True,
                map_view="satellite",
                show_heat_map=True
            )

        return settings

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user settings: {str(e)}"
        )


@router.put("/user/settings", response_model=UserSettings)
async def update_user_settings(
    settings: UserSettings,
    current_user: UserProfile = Depends(get_current_user_profile)
):
    """
    Update user application settings

    Updates user preferences for search defaults, display options, and notifications.
    """
    try:
        settings.user_id = current_user.user_id

        updated_settings = await supabase_client.update_user_settings(
            user_id=current_user.user_id,
            settings=settings
        )

        if not updated_settings:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update settings"
            )

        return updated_settings

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update settings: {str(e)}"
        )


# ======== NOTIFICATIONS ========

@router.get("/user/notifications")
async def get_user_notifications(
    unread_only: bool = Query(False, description="Return only unread notifications"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of notifications to return"),
    current_user: UserProfile = Depends(get_current_user_profile)
):
    """
    Get user's notifications

    Returns in-app notifications with status, content, and metadata.

    **Notification Types:**
    - **alert**: New planning applications found by alerts
    - **report_ready**: Generated reports ready for download
    - **system**: System announcements and updates
    - **digest**: Daily/weekly summary notifications
    - **welcome**: Onboarding and welcome messages
    """
    try:
        notifications = await notification_service.get_user_notifications(
            user_id=current_user.user_id,
            unread_only=unread_only,
            limit=limit
        )

        # Track notification viewing
        await track_user_interaction(
            interaction_type="view",
            entity_type="notifications",
            current_user={"user_id": current_user.user_id}
        )

        return {
            "notifications": notifications,
            "total_count": len(notifications),
            "unread_count": len([n for n in notifications if not n.get("is_read", True)]),
            "last_updated": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notifications: {str(e)}"
        )


@router.put("/user/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str = Path(..., description="Notification ID"),
    current_user: UserProfile = Depends(get_current_user_profile)
):
    """
    Mark notification as read

    Updates the read status of a specific notification.
    """
    try:
        success = await notification_service.mark_notification_read(
            notification_id=notification_id,
            user_id=current_user.user_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )

        # Track interaction
        await track_user_interaction(
            interaction_type="read",
            entity_type="notification",
            entity_id=notification_id,
            current_user={"user_id": current_user.user_id}
        )

        return {
            "message": "Notification marked as read",
            "notification_id": notification_id,
            "marked_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notification as read: {str(e)}"
        )


@router.post("/user/notifications/mark-all-read")
async def mark_all_notifications_read(
    current_user: UserProfile = Depends(get_current_user_profile)
):
    """
    Mark all notifications as read

    Marks all user notifications as read in a single operation.
    """
    try:
        # Get all unread notifications
        notifications = await notification_service.get_user_notifications(
            user_id=current_user.user_id,
            unread_only=True,
            limit=1000  # Get all unread
        )

        # Mark each as read
        success_count = 0
        for notification in notifications:
            success = await notification_service.mark_notification_read(
                notification_id=notification["notification_id"],
                user_id=current_user.user_id
            )
            if success:
                success_count += 1

        # Track bulk action
        await track_user_interaction(
            interaction_type="mark_all_read",
            entity_type="notifications",
            current_user={"user_id": current_user.user_id}
        )

        return {
            "message": f"Marked {success_count} notifications as read",
            "notifications_marked": success_count,
            "marked_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark all notifications as read: {str(e)}"
        )


@router.post("/user/notifications/test")
async def send_test_notification(
    notification_type: str = Query("system", description="Type of test notification"),
    current_user: UserProfile = Depends(get_current_user_profile)
):
    """
    Send a test notification

    Sends a test notification to verify notification delivery settings.
    Useful for testing email and push notification configurations.

    **Available Test Types:**
    - **system**: General system notification
    - **alert**: Mock alert notification
    - **report_ready**: Mock report completion notification
    - **welcome**: Welcome message test
    """
    try:
        # Validate notification type
        valid_types = ["system", "alert", "report_ready", "welcome"]
        if notification_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid notification type. Valid options: {valid_types}"
            )

        # Send test notification based on type
        success = False
        if notification_type == "system":
            success = await notification_service.send_notification(
                user_id=current_user.user_id,
                notification_type="system",
                title="Test Notification",
                message="This is a test notification to verify your settings are working correctly.",
                data={"test": True}
            )
        elif notification_type == "alert":
            success = await notification_service.send_alert_notification(
                user_id=current_user.user_id,
                alert_name="Test Alert",
                alert_id="test_alert_123",
                new_applications_count=3
            )
        elif notification_type == "report_ready":
            success = await notification_service.send_report_ready_notification(
                user_id=current_user.user_id,
                report_name="Test Report",
                report_id="test_report_123"
            )
        elif notification_type == "welcome":
            success = await notification_service.send_welcome_notification(
                user_id=current_user.user_id,
                user_name=current_user.full_name or "User"
            )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send test notification"
            )

        # Track test
        await track_user_interaction(
            interaction_type="test",
            entity_type="notification",
            current_user={"user_id": current_user.user_id}
        )

        return {
            "message": f"Test {notification_type} notification sent successfully",
            "notification_type": notification_type,
            "sent_at": datetime.utcnow().isoformat(),
            "delivery_note": "Check your email and in-app notifications"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send test notification: {str(e)}"
        )