"""
User models for Planning Explorer with Supabase integration
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, EmailStr, validator


class UserRole(str, Enum):
    """User role types"""
    FREE = "free"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    ADMIN = "admin"


class AlertFrequency(str, Enum):
    """Alert notification frequency"""
    IMMEDIATE = "immediate"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class ReportStatus(str, Enum):
    """Report generation status"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


# ======== USER MODELS ========

class UserProfile(BaseModel):
    """User profile model"""

    user_id: str = Field(..., description="User unique identifier")
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, description="User full name")
    company: Optional[str] = Field(None, description="Company name")
    role: UserRole = Field(UserRole.FREE, description="User subscription role")
    avatar_url: Optional[str] = Field(None, description="Avatar image URL")
    phone: Optional[str] = Field(None, description="Phone number")

    # Preferences
    email_notifications: bool = Field(True, description="Email notifications enabled")
    push_notifications: bool = Field(True, description="Push notifications enabled")
    marketing_emails: bool = Field(False, description="Marketing emails enabled")

    # Usage tracking
    api_calls_this_month: int = Field(0, description="API calls this month")
    searches_this_month: int = Field(0, description="Searches this month")
    reports_generated: int = Field(0, description="Total reports generated")

    # Limits based on subscription
    max_saved_searches: int = Field(10, description="Maximum saved searches")
    max_alerts: int = Field(5, description="Maximum alerts")
    max_api_calls_per_month: int = Field(1000, description="Monthly API call limit")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

    class Config:
        use_enum_values = True


class UserSettings(BaseModel):
    """User application settings"""

    user_id: str = Field(..., description="User ID")

    # Search preferences
    default_search_radius: float = Field(5.0, description="Default search radius in km")
    preferred_authorities: List[str] = Field(default_factory=list, description="Preferred planning authorities")
    default_filters: Optional[Dict[str, Any]] = Field(None, description="Default search filters")

    # Display preferences
    results_per_page: int = Field(20, ge=5, le=100, description="Results per page")
    show_ai_insights: bool = Field(True, description="Show AI insights by default")
    show_opportunity_scores: bool = Field(True, description="Show opportunity scores")

    # Map preferences
    map_view: str = Field("satellite", description="Default map view")
    show_heat_map: bool = Field(True, description="Show application density heat map")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ======== SAVED SEARCHES ========

class SavedSearch(BaseModel):
    """User saved search model"""

    search_id: str = Field(..., description="Unique search identifier")
    user_id: str = Field(..., description="User ID")
    name: str = Field(..., min_length=1, max_length=100, description="Search name")
    description: Optional[str] = Field(None, max_length=500, description="Search description")

    # Search parameters
    query: Optional[str] = Field(None, description="Search query")
    filters: Optional[Dict[str, Any]] = Field(None, description="Search filters")
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_order: Optional[str] = Field(None, description="Sort order")

    # Metadata
    is_alert: bool = Field(False, description="Convert to alert")
    alert_frequency: Optional[AlertFrequency] = Field(None, description="Alert frequency")
    last_run: Optional[datetime] = Field(None, description="Last search execution")
    result_count: Optional[int] = Field(None, description="Last result count")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SavedSearchResponse(BaseModel):
    """API response for saved searches"""

    search_id: str
    name: str
    description: Optional[str]
    query: Optional[str]
    filters: Optional[Dict[str, Any]]
    is_alert: bool
    alert_frequency: Optional[AlertFrequency]
    last_run: Optional[datetime]
    result_count: Optional[int]
    created_at: datetime
    updated_at: datetime


# ======== ALERTS ========

class UserAlert(BaseModel):
    """User alert model"""

    alert_id: str = Field(..., description="Unique alert identifier")
    user_id: str = Field(..., description="User ID")
    saved_search_id: Optional[str] = Field(None, description="Associated saved search ID")

    name: str = Field(..., min_length=1, max_length=100, description="Alert name")
    description: Optional[str] = Field(None, max_length=500, description="Alert description")

    # Alert criteria
    query: Optional[str] = Field(None, description="Search query")
    filters: Optional[Dict[str, Any]] = Field(None, description="Search filters")
    location_filters: Optional[Dict[str, Any]] = Field(None, description="Location-based filters")

    # Notification settings
    frequency: AlertFrequency = Field(AlertFrequency.DAILY, description="Alert frequency")
    email_enabled: bool = Field(True, description="Email notifications enabled")
    push_enabled: bool = Field(True, description="Push notifications enabled")

    # Status
    is_active: bool = Field(True, description="Alert is active")
    last_triggered: Optional[datetime] = Field(None, description="Last trigger timestamp")
    last_notification_sent: Optional[datetime] = Field(None, description="Last notification sent")
    new_results_count: int = Field(0, description="New results since last notification")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AlertTrigger(BaseModel):
    """Alert trigger event"""

    trigger_id: str = Field(..., description="Trigger identifier")
    alert_id: str = Field(..., description="Alert ID")
    user_id: str = Field(..., description="User ID")

    new_applications: List[str] = Field(..., description="New application IDs")
    trigger_reason: str = Field(..., description="Reason for trigger")
    notification_sent: bool = Field(False, description="Notification was sent")

    created_at: datetime = Field(default_factory=datetime.utcnow)


# ======== REPORTS ========

class UserReport(BaseModel):
    """User generated report model"""

    report_id: str = Field(..., description="Unique report identifier")
    user_id: str = Field(..., description="User ID")

    name: str = Field(..., min_length=1, max_length=100, description="Report name")
    description: Optional[str] = Field(None, max_length=500, description="Report description")
    report_type: str = Field(..., description="Report type (market_analysis, opportunity_report, etc.)")

    # Report parameters
    query: Optional[str] = Field(None, description="Search query used")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filters applied")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="Date range for analysis")
    location: Optional[Dict[str, Any]] = Field(None, description="Geographic focus")

    # Report content
    status: ReportStatus = Field(ReportStatus.PENDING, description="Report generation status")
    content: Optional[Dict[str, Any]] = Field(None, description="Report content JSON")
    summary: Optional[str] = Field(None, description="Executive summary")
    file_url: Optional[str] = Field(None, description="Generated file URL")
    file_format: str = Field("pdf", description="Report file format")

    # Metadata
    applications_analyzed: int = Field(0, description="Number of applications analyzed")
    generation_time_seconds: Optional[float] = Field(None, description="Generation time")
    error_message: Optional[str] = Field(None, description="Error message if failed")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")


# ======== API USAGE TRACKING ========

class APIUsage(BaseModel):
    """API usage tracking model"""

    usage_id: str = Field(..., description="Usage record identifier")
    user_id: str = Field(..., description="User ID")

    endpoint: str = Field(..., description="API endpoint called")
    method: str = Field(..., description="HTTP method")
    query_parameters: Optional[Dict[str, Any]] = Field(None, description="Query parameters")

    # Performance metrics
    response_time_ms: int = Field(..., description="Response time in milliseconds")
    response_status: int = Field(..., description="HTTP response status")
    results_returned: Optional[int] = Field(None, description="Number of results returned")

    # Billing
    billable: bool = Field(True, description="Counts towards usage limits")
    cost_credits: float = Field(0.0, description="Credits consumed")

    created_at: datetime = Field(default_factory=datetime.utcnow)


# ======== USER EVENTS ========

class UserEvent(BaseModel):
    """User activity tracking"""

    event_id: str = Field(..., description="Event identifier")
    user_id: str = Field(..., description="User ID")

    event_type: str = Field(..., description="Event type (search, view, save, etc.)")
    event_data: Optional[Dict[str, Any]] = Field(None, description="Event-specific data")

    # Context
    application_id: Optional[str] = Field(None, description="Related application ID")
    search_id: Optional[str] = Field(None, description="Related search ID")
    session_id: Optional[str] = Field(None, description="User session ID")

    # Client info
    user_agent: Optional[str] = Field(None, description="User agent string")
    ip_address: Optional[str] = Field(None, description="Client IP address")

    created_at: datetime = Field(default_factory=datetime.utcnow)


# ======== REQUEST/RESPONSE MODELS ========

class UserRegistrationRequest(BaseModel):
    """User registration request"""

    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="User password")
    full_name: Optional[str] = Field(None, description="Full name")
    company: Optional[str] = Field(None, description="Company name")
    role: UserRole = Field(UserRole.FREE, description="Initial role")


class UserLoginRequest(BaseModel):
    """User login request"""

    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")


class UserUpdateRequest(BaseModel):
    """User profile update request"""

    full_name: Optional[str] = Field(None, description="Full name")
    company: Optional[str] = Field(None, description="Company name")
    phone: Optional[str] = Field(None, description="Phone number")
    email_notifications: Optional[bool] = Field(None, description="Email notifications")
    push_notifications: Optional[bool] = Field(None, description="Push notifications")
    marketing_emails: Optional[bool] = Field(None, description="Marketing emails")


class SavedSearchRequest(BaseModel):
    """Create/update saved search request"""

    name: str = Field(..., min_length=1, max_length=100, description="Search name")
    description: Optional[str] = Field(None, max_length=500, description="Search description")
    query: Optional[str] = Field(None, description="Search query")
    filters: Optional[Dict[str, Any]] = Field(None, description="Search filters")
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_order: Optional[str] = Field(None, description="Sort order")
    is_alert: bool = Field(False, description="Convert to alert")
    alert_frequency: Optional[AlertFrequency] = Field(None, description="Alert frequency")


class AlertRequest(BaseModel):
    """Create/update alert request"""

    name: str = Field(..., min_length=1, max_length=100, description="Alert name")
    description: Optional[str] = Field(None, max_length=500, description="Alert description")
    query: Optional[str] = Field(None, description="Search query")
    filters: Optional[Dict[str, Any]] = Field(None, description="Search filters")
    location_filters: Optional[Dict[str, Any]] = Field(None, description="Location filters")
    frequency: AlertFrequency = Field(AlertFrequency.DAILY, description="Alert frequency")
    email_enabled: bool = Field(True, description="Email notifications")
    push_enabled: bool = Field(True, description="Push notifications")


class ReportRequest(BaseModel):
    """Generate report request"""

    name: str = Field(..., min_length=1, max_length=100, description="Report name")
    description: Optional[str] = Field(None, max_length=500, description="Report description")
    report_type: str = Field(..., description="Report type")
    query: Optional[str] = Field(None, description="Search query")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filters")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="Date range")
    location: Optional[Dict[str, Any]] = Field(None, description="Geographic focus")
    file_format: str = Field("pdf", description="Output format")


class UserStatsResponse(BaseModel):
    """User statistics response"""

    total_searches: int = Field(..., description="Total searches performed")
    saved_searches: int = Field(..., description="Number of saved searches")
    active_alerts: int = Field(..., description="Number of active alerts")
    reports_generated: int = Field(..., description="Total reports generated")
    api_calls_this_month: int = Field(..., description="API calls this month")
    plan_usage: Dict[str, Any] = Field(..., description="Subscription plan usage")
    created_at: datetime = Field(..., description="Account creation date")
    last_login: Optional[datetime] = Field(None, description="Last login")


class AuthResponse(BaseModel):
    """Authentication response"""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    user: UserProfile = Field(..., description="User profile")
    refresh_token: Optional[str] = Field(None, description="Refresh token")


# ======== AI PERSONALIZATION MODELS ========

class InteractionType(str, Enum):
    """Types of user interactions for AI learning"""
    SEARCH = "search"
    VIEW_APPLICATION = "view_application"
    SAVE_SEARCH = "save_search"
    CREATE_ALERT = "create_alert"
    GENERATE_REPORT = "generate_report"
    DOWNLOAD_DOCUMENT = "download_document"
    BOOKMARK_APPLICATION = "bookmark_application"
    SHARE_APPLICATION = "share_application"
    FILTER_RESULTS = "filter_results"
    SORT_RESULTS = "sort_results"
    VIEW_MAP = "view_map"
    EXPORT_DATA = "export_data"
    AI_SUMMARY_VIEW = "ai_summary_view"
    OPPORTUNITY_SCORE_VIEW = "opportunity_score_view"
    FEEDBACK_POSITIVE = "feedback_positive"
    FEEDBACK_NEGATIVE = "feedback_negative"


class UserSegment(str, Enum):
    """User behavior segments for personalization"""
    NEWCOMER = "newcomer"
    OCCASIONAL_USER = "occasional_user"
    REGULAR_USER = "regular_user"
    POWER_USER = "power_user"
    PROFESSIONAL = "professional"
    RESEARCHER = "researcher"
    DEVELOPER = "developer"
    INACTIVE = "inactive"


class FeedbackType(str, Enum):
    """Types of user feedback for learning"""
    EXPLICIT_RATING = "explicit_rating"
    IMPLICIT_CLICK = "implicit_click"
    IMPLICIT_TIME_SPENT = "implicit_time_spent"
    IMPLICIT_SAVE = "implicit_save"
    IMPLICIT_SHARE = "implicit_share"
    IMPLICIT_IGNORE = "implicit_ignore"
    RECOMMENDATION_FEEDBACK = "recommendation_feedback"
    SEARCH_FEEDBACK = "search_feedback"
    SUMMARY_FEEDBACK = "summary_feedback"
    FEATURE_FEEDBACK = "feature_feedback"


class RecommendationType(str, Enum):
    """Types of AI recommendations"""
    OPPORTUNITIES = "opportunities"
    SEARCHES = "searches"
    APPLICATIONS = "applications"
    MARKET_INTELLIGENCE = "market_intelligence"
    TRAINING_CONTENT = "training_content"
    FEATURES = "features"
    TIMING = "timing"
    GEOGRAPHIC = "geographic"


class UserInteraction(BaseModel):
    """User interaction tracking for AI learning"""

    interaction_id: str = Field(..., description="Unique interaction identifier")
    user_id: str = Field(..., description="User ID")
    interaction_type: InteractionType = Field(..., description="Type of interaction")
    session_id: Optional[str] = Field(None, description="Session identifier")

    # Context data
    application_id: Optional[str] = Field(None, description="Related application ID")
    search_query: Optional[str] = Field(None, description="Search query if applicable")
    filters_used: Optional[Dict[str, Any]] = Field(None, description="Filters applied")
    location: Optional[Dict[str, float]] = Field(None, description="Geographic context")

    # Metadata
    device_type: Optional[str] = Field(None, description="Device type")
    duration_seconds: Optional[float] = Field(None, description="Time spent")
    result_count: Optional[int] = Field(None, description="Number of results")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")

    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserBehaviorProfile(BaseModel):
    """Comprehensive user behavior profile for personalization"""

    user_id: str = Field(..., description="User ID")
    segment: UserSegment = Field(..., description="User behavior segment")

    # Interaction statistics
    total_interactions: int = Field(0, description="Total interactions count")
    interaction_frequency: float = Field(0.0, description="Interactions per day")
    preferred_interaction_types: List[str] = Field(default_factory=list)

    # Behavioral patterns
    geographic_focus: List[Dict[str, Any]] = Field(default_factory=list)
    search_patterns: Dict[str, Any] = Field(default_factory=dict)
    time_patterns: Dict[str, Any] = Field(default_factory=dict)

    # AI metrics
    expertise_level: float = Field(0.0, description="User expertise level (0-1)")
    engagement_score: float = Field(0.0, description="Engagement score (0-1)")
    risk_tolerance: float = Field(0.5, description="Risk tolerance (0-1)")

    # Preferences
    interests: List[str] = Field(default_factory=list)
    preferred_authorities: List[str] = Field(default_factory=list)
    session_duration_avg: float = Field(0.0, description="Average session duration")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class UserPreferences(BaseModel):
    """Detailed user preferences for AI personalization"""

    user_id: str = Field(..., description="User ID")

    # Content preferences (0-1 scale)
    content_preferences: Dict[str, float] = Field(default_factory=dict)
    feature_preferences: Dict[str, float] = Field(default_factory=dict)
    interaction_preferences: Dict[str, float] = Field(default_factory=dict)

    # Geographic and temporal preferences
    geographic_preferences: List[Dict[str, Any]] = Field(default_factory=list)
    temporal_preferences: Dict[str, Any] = Field(default_factory=dict)

    # AI behavior preferences
    risk_preferences: Dict[str, float] = Field(default_factory=dict)
    complexity_preference: float = Field(0.5, description="Complexity preference (0-1)")

    # System preferences
    notification_preferences: Dict[str, Any] = Field(default_factory=dict)
    privacy_preferences: Dict[str, bool] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class UserRecommendation(BaseModel):
    """AI-generated user recommendations"""

    recommendation_id: str = Field(..., description="Unique recommendation ID")
    user_id: str = Field(..., description="User ID")
    recommendation_type: RecommendationType = Field(..., description="Type of recommendation")

    # Recommendation content
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Recommendation description")
    action_url: Optional[str] = Field(None, description="Action URL")

    # AI metrics
    confidence: float = Field(..., description="AI confidence score (0-1)")
    relevance_score: float = Field(..., description="Relevance score (0-1)")
    reasoning: List[str] = Field(default_factory=list, description="AI reasoning")

    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    expires_at: Optional[datetime] = Field(None, description="Expiration time")

    # Tracking
    viewed: bool = Field(False, description="User viewed recommendation")
    clicked: bool = Field(False, description="User clicked recommendation")
    feedback_value: Optional[float] = Field(None, description="User feedback (-1 to 1)")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserFeedback(BaseModel):
    """User feedback for AI learning"""

    feedback_id: str = Field(..., description="Unique feedback ID")
    user_id: str = Field(..., description="User ID")
    feedback_type: FeedbackType = Field(..., description="Type of feedback")

    # Target information
    target_type: str = Field(..., description="Type of target (recommendation, search_result, etc.)")
    target_id: str = Field(..., description="Target identifier")

    # Feedback data
    feedback_value: float = Field(..., description="Feedback value (-1 to 1)")
    context: Dict[str, Any] = Field(default_factory=dict, description="Feedback context")

    # Metadata
    session_id: Optional[str] = Field(None, description="Session ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    created_at: datetime = Field(default_factory=datetime.utcnow)


class AIParameters(BaseModel):
    """User-specific AI parameters"""

    user_id: str = Field(..., description="User ID")
    parameters: Dict[str, Any] = Field(..., description="AI parameters")

    # Metadata
    model_version: str = Field("1.0", description="AI model version")
    last_training: Optional[datetime] = Field(None, description="Last training timestamp")
    performance_metrics: Dict[str, float] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PersonalizationInsight(BaseModel):
    """AI-generated insights about user behavior"""

    insight_id: str = Field(..., description="Unique insight ID")
    user_id: str = Field(..., description="User ID")
    insight_type: str = Field(..., description="Type of insight")

    # Insight content
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Insight description")
    confidence: float = Field(..., description="Confidence score (0-1)")

    # Actionable recommendations
    actionable_recommendations: List[str] = Field(default_factory=list)
    data_points: Dict[str, Any] = Field(default_factory=dict)

    # Metadata
    expires_at: Optional[datetime] = Field(None, description="Expiration time")
    acknowledged: bool = Field(False, description="User acknowledged insight")

    created_at: datetime = Field(default_factory=datetime.utcnow)


# ======== REQUEST/RESPONSE MODELS FOR AI FEATURES ========

class RecommendationRequest(BaseModel):
    """Request for AI recommendations"""

    recommendation_type: RecommendationType = Field(..., description="Type of recommendations")
    limit: int = Field(10, ge=1, le=50, description="Maximum recommendations")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class FeedbackRequest(BaseModel):
    """Request to submit feedback"""

    target_type: str = Field(..., description="Type of target")
    target_id: str = Field(..., description="Target identifier")
    feedback_value: float = Field(..., ge=-1.0, le=1.0, description="Feedback value")
    feedback_type: FeedbackType = Field(..., description="Type of feedback")
    context: Optional[Dict[str, Any]] = Field(None, description="Feedback context")


class PersonalizationResponse(BaseModel):
    """Response with personalized content"""

    personalized: bool = Field(..., description="Content was personalized")
    personalization_factors: List[str] = Field(default_factory=list)
    confidence: float = Field(..., description="Personalization confidence")
    content: Dict[str, Any] = Field(..., description="Personalized content")


class UserInsightsResponse(BaseModel):
    """Response with user behavior insights"""

    user_segment: UserSegment = Field(..., description="User behavior segment")
    expertise_level: float = Field(..., description="Expertise level (0-1)")
    engagement_score: float = Field(..., description="Engagement score (0-1)")
    top_interests: List[str] = Field(default_factory=list)
    recommendations_count: int = Field(0, description="Available recommendations")
    insights: List[PersonalizationInsight] = Field(default_factory=list)