"""
API endpoints for AI personalization and learning features
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.security import HTTPBearer
from datetime import datetime, timedelta
import logging

from app.middleware.auth import get_current_user, get_current_user_profile as get_current_active_user
from app.db.supabase import supabase_client
from app.models.user import (
    UserProfile,
    RecommendationType,
    FeedbackType,
    UserSegment,
    RecommendationRequest,
    FeedbackRequest,
    PersonalizationResponse,
    UserInsightsResponse,
    UserInteraction,
    UserRecommendation,
    PersonalizationInsight
)
from app.ai.user_analytics import UserBehaviorAnalyzer, InteractionType
from app.ai.personalization_engine import PersonalizationEngine
from app.ai.learning_system import LearningSystem
from app.ai.privacy_manager import PrivacyManager, ConsentType, DataCategory

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()


# Dependency injection for AI services
async def get_ai_services():
    """Get AI personalization services"""
    supabase = get_supabase_client()
    behavior_analyzer = UserBehaviorAnalyzer(supabase)
    personalization_engine = PersonalizationEngine(supabase, behavior_analyzer)
    learning_system = LearningSystem(supabase, behavior_analyzer, personalization_engine)
    privacy_manager = PrivacyManager(supabase)

    return {
        'behavior_analyzer': behavior_analyzer,
        'personalization_engine': personalization_engine,
        'learning_system': learning_system,
        'privacy_manager': privacy_manager,
        'supabase': supabase
    }


@router.post(
    "/recommendations/{user_id}",
    response_model=List[UserRecommendation],
    summary="Generate personalized recommendations",
    description="Generate AI-powered personalized recommendations for a user"
)
async def generate_recommendations(
    user_id: str,
    request: RecommendationRequest,
    current_user: UserProfile = Depends(get_current_active_user),
    services: Dict = Depends(get_ai_services)
):
    """
    Generate personalized recommendations for a user

    - **user_id**: User identifier
    - **recommendation_type**: Type of recommendations to generate
    - **limit**: Maximum number of recommendations (1-50)
    - **context**: Additional context for recommendations
    """
    try:
        # Verify user authorization (users can only get their own recommendations unless admin)
        if current_user.user_id != user_id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to access this user's recommendations")

        # Check privacy consent
        privacy_manager = services['privacy_manager']
        has_consent = await privacy_manager.check_consent(
            user_id, ConsentType.PERSONALIZATION, "recommendation_generation"
        )

        if not has_consent:
            raise HTTPException(
                status_code=403,
                detail="User consent required for personalized recommendations. Please review privacy settings."
            )

        personalization_engine = services['personalization_engine']

        # Generate recommendations
        recommendations = await personalization_engine.generate_recommendations(
            user_id=user_id,
            recommendation_type=request.recommendation_type,
            limit=request.limit,
            context=request.context
        )

        # Convert to response format
        response_recommendations = []
        for rec in recommendations:
            response_recommendations.append(UserRecommendation(
                recommendation_id=rec.recommendation_id,
                user_id=rec.user_id,
                recommendation_type=rec.type,
                title=rec.title,
                description=rec.description,
                action_url=rec.action_url,
                confidence=rec.confidence,
                relevance_score=rec.relevance_score,
                reasoning=rec.reasoning,
                metadata=rec.metadata,
                expires_at=rec.expires_at,
                viewed=False,
                clicked=False,
                feedback_value=None,
                created_at=rec.created_at
            ))

        # Track recommendation generation
        behavior_analyzer = services['behavior_analyzer']
        await behavior_analyzer.track_interaction(
            user_id=user_id,
            interaction_type=InteractionType.AI_SUMMARY_VIEW,
            context={
                'feature': 'recommendations',
                'recommendation_type': request.recommendation_type.value,
                'count': len(response_recommendations)
            }
        )

        logger.info(f"Generated {len(response_recommendations)} recommendations for user {user_id}")
        return response_recommendations

    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")


@router.get(
    "/recommendations/{user_id}",
    response_model=List[UserRecommendation],
    summary="Get existing recommendations",
    description="Retrieve existing personalized recommendations for a user"
)
async def get_user_recommendations(
    user_id: str,
    recommendation_type: Optional[RecommendationType] = Query(None, description="Filter by recommendation type"),
    limit: int = Query(20, ge=1, le=100, description="Maximum recommendations to return"),
    include_expired: bool = Query(False, description="Include expired recommendations"),
    current_user: UserProfile = Depends(get_current_active_user),
    services: Dict = Depends(get_ai_services)
):
    """
    Get existing recommendations for a user

    - **user_id**: User identifier
    - **recommendation_type**: Optional filter by recommendation type
    - **limit**: Maximum recommendations to return
    - **include_expired**: Whether to include expired recommendations
    """
    try:
        # Verify user authorization
        if current_user.user_id != user_id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to access this user's recommendations")

        supabase = services['supabase']

        # Build query
        query = supabase.table('user_recommendations')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .limit(limit)

        if recommendation_type:
            query = query.eq('recommendation_type', recommendation_type.value)

        if not include_expired:
            current_time = datetime.utcnow().isoformat()
            query = query.or_(f'expires_at.is.null,expires_at.gte.{current_time}')

        result = query.execute()
        recommendations = result.data

        # Convert to response format
        response_recommendations = []
        for rec_data in recommendations:
            response_recommendations.append(UserRecommendation(**rec_data))

        return response_recommendations

    except Exception as e:
        logger.error(f"Error getting user recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve recommendations")


@router.post(
    "/feedback",
    summary="Submit user feedback",
    description="Submit feedback for AI learning and improvement"
)
async def submit_feedback(
    request: FeedbackRequest,
    background_tasks: BackgroundTasks,
    current_user: UserProfile = Depends(get_current_active_user),
    services: Dict = Depends(get_ai_services)
):
    """
    Submit user feedback for AI learning

    - **target_type**: Type of target being rated (recommendation, search_result, summary, etc.)
    - **target_id**: Identifier of the target
    - **feedback_value**: Feedback value from -1 (negative) to 1 (positive)
    - **feedback_type**: Type of feedback (explicit_rating, implicit_click, etc.)
    - **context**: Additional feedback context
    """
    try:
        learning_system = services['learning_system']

        # Process feedback
        success = await learning_system.process_user_feedback(
            user_id=current_user.user_id,
            feedback_type=request.feedback_type,
            target_type=request.target_type,
            target_id=request.target_id,
            feedback_value=request.feedback_value,
            context=request.context or {}
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to process feedback")

        # Schedule background learning update
        background_tasks.add_task(
            _update_user_learning,
            current_user.user_id,
            request,
            services
        )

        return {"message": "Feedback submitted successfully", "processed": True}

    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")


@router.get(
    "/insights/{user_id}",
    response_model=UserInsightsResponse,
    summary="Get user behavior insights",
    description="Get AI-generated insights about user behavior and preferences"
)
async def get_user_insights(
    user_id: str,
    current_user: UserProfile = Depends(get_current_active_user),
    services: Dict = Depends(get_ai_services)
):
    """
    Get comprehensive user behavior insights

    - **user_id**: User identifier
    """
    try:
        # Verify user authorization
        if current_user.user_id != user_id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to access this user's insights")

        behavior_analyzer = services['behavior_analyzer']

        # Get user behavior profile
        user_profile = await behavior_analyzer.analyze_user_patterns(user_id)

        # Get user insights
        insights = await behavior_analyzer.generate_user_insights(user_id)

        # Count available recommendations
        supabase = services['supabase']
        rec_count_result = supabase.table('user_recommendations')\
            .select('id', count='exact')\
            .eq('user_id', user_id)\
            .or_(f'expires_at.is.null,expires_at.gte.{datetime.utcnow().isoformat()}')\
            .execute()

        rec_count = rec_count_result.count or 0

        # Convert insights to response format
        insight_objects = []
        for insight in insights:
            insight_objects.append(PersonalizationInsight(
                insight_id=f"insight_{user_id}_{len(insight_objects)}",
                user_id=insight.user_id,
                insight_type=insight.insight_type,
                title=insight.title,
                description=insight.description,
                confidence=insight.confidence,
                actionable_recommendations=insight.actionable_recommendations,
                data_points=insight.data_points,
                created_at=insight.created_at
            ))

        response = UserInsightsResponse(
            user_segment=user_profile.segment,
            expertise_level=user_profile.expertise_level,
            engagement_score=user_profile.engagement_score,
            top_interests=user_profile.interests[:5],  # Top 5 interests
            recommendations_count=rec_count,
            insights=insight_objects
        )

        return response

    except Exception as e:
        logger.error(f"Error getting user insights: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user insights")


@router.post(
    "/personalize/search",
    response_model=PersonalizationResponse,
    summary="Personalize search results",
    description="Apply AI personalization to search results"
)
async def personalize_search_results(
    search_results: List[Dict[str, Any]],
    search_context: Dict[str, Any],
    current_user: UserProfile = Depends(get_current_active_user),
    services: Dict = Depends(get_ai_services)
):
    """
    Personalize search results based on user preferences and behavior

    - **search_results**: Original search results to personalize
    - **search_context**: Search context (query, filters, etc.)
    """
    try:
        personalization_engine = services['personalization_engine']

        # Personalize search results
        personalized_results = await personalization_engine.personalize_search_results(
            user_id=current_user.user_id,
            search_results=search_results,
            search_context=search_context
        )

        # Calculate personalization factors
        personalization_factors = []
        if personalized_results != search_results:
            personalization_factors.append("Results reranked based on your preferences")
            personalization_factors.append("Content adapted to your expertise level")

            # Check if geographic preferences were applied
            behavior_analyzer = services['behavior_analyzer']
            user_profile = await behavior_analyzer.analyze_user_patterns(current_user.user_id)
            if user_profile.geographic_focus:
                personalization_factors.append("Prioritized based on your geographic interests")

        # Calculate confidence
        confidence = 0.8 if len(personalization_factors) > 0 else 0.3

        response = PersonalizationResponse(
            personalized=len(personalization_factors) > 0,
            personalization_factors=personalization_factors,
            confidence=confidence,
            content={'results': personalized_results}
        )

        # Track personalization usage
        await services['behavior_analyzer'].track_interaction(
            user_id=current_user.user_id,
            interaction_type=InteractionType.SEARCH,
            context={
                'personalized': True,
                'results_count': len(personalized_results),
                'factors_applied': len(personalization_factors)
            }
        )

        return response

    except Exception as e:
        logger.error(f"Error personalizing search results: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to personalize search results")


@router.post(
    "/personalize/summary",
    response_model=PersonalizationResponse,
    summary="Generate personalized AI summary",
    description="Generate AI summary personalized for user's expertise and interests"
)
async def personalize_ai_summary(
    application_data: Dict[str, Any],
    summary_context: Optional[Dict[str, Any]] = None,
    current_user: UserProfile = Depends(get_current_active_user),
    services: Dict = Depends(get_ai_services)
):
    """
    Generate personalized AI summary for planning application

    - **application_data**: Planning application data to summarize
    - **summary_context**: Additional context for summary generation
    """
    try:
        personalization_engine = services['personalization_engine']

        # Generate personalized summary
        personalized_summary = await personalization_engine.customize_ai_summaries(
            user_id=current_user.user_id,
            application_data=application_data,
            summary_context=summary_context
        )

        # Extract personalization factors
        personalization_factors = personalized_summary.get('adaptation_factors', [])

        response = PersonalizationResponse(
            personalized=True,
            personalization_factors=personalization_factors,
            confidence=personalized_summary.get('confidence', 0.7),
            content=personalized_summary
        )

        # Track AI summary usage
        await services['behavior_analyzer'].track_interaction(
            user_id=current_user.user_id,
            interaction_type=InteractionType.AI_SUMMARY_VIEW,
            context={
                'application_id': application_data.get('id'),
                'personalization_level': personalized_summary.get('personalization_level'),
                'confidence': personalized_summary.get('confidence')
            }
        )

        return response

    except Exception as e:
        logger.error(f"Error generating personalized summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate personalized summary")


@router.post(
    "/track/interaction",
    summary="Track user interaction",
    description="Track user interaction for AI learning"
)
async def track_user_interaction(
    interaction_type: InteractionType,
    context: Dict[str, Any],
    session_id: Optional[str] = None,
    application_id: Optional[str] = None,
    current_user: UserProfile = Depends(get_current_active_user),
    services: Dict = Depends(get_ai_services)
):
    """
    Track user interaction for behavioral analysis and AI learning

    - **interaction_type**: Type of interaction
    - **context**: Interaction context and metadata
    - **session_id**: Optional session identifier
    - **application_id**: Optional related application ID
    """
    try:
        behavior_analyzer = services['behavior_analyzer']

        # Track interaction
        success = await behavior_analyzer.track_interaction(
            user_id=current_user.user_id,
            interaction_type=interaction_type,
            context=context,
            session_id=session_id,
            application_id=application_id
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to track interaction")

        return {"message": "Interaction tracked successfully", "tracked": True}

    except Exception as e:
        logger.error(f"Error tracking interaction: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to track interaction")


@router.get(
    "/behavior/profile/{user_id}",
    summary="Get user behavior profile",
    description="Get comprehensive user behavior profile for analysis"
)
async def get_user_behavior_profile(
    user_id: str,
    current_user: UserProfile = Depends(get_current_active_user),
    services: Dict = Depends(get_ai_services)
):
    """
    Get detailed user behavior profile

    - **user_id**: User identifier
    """
    try:
        # Verify user authorization (admin or own profile)
        if current_user.user_id != user_id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to access this user's profile")

        behavior_analyzer = services['behavior_analyzer']

        # Get behavior profile
        profile = await behavior_analyzer.analyze_user_patterns(user_id)

        # Convert to response format (excluding sensitive data for non-admin users)
        profile_data = {
            'user_id': profile.user_id,
            'segment': profile.segment,
            'total_interactions': profile.total_interactions,
            'interaction_frequency': profile.interaction_frequency,
            'expertise_level': profile.expertise_level,
            'engagement_score': profile.engagement_score,
            'interests': profile.interests,
            'geographic_focus': profile.geographic_focus[:3],  # Top 3 areas only
            'last_updated': profile.last_updated
        }

        # Include detailed data for admin users
        if current_user.role == "admin":
            profile_data.update({
                'preferred_interaction_types': profile.preferred_interaction_types,
                'search_patterns': profile.search_patterns,
                'time_patterns': profile.time_patterns,
                'risk_tolerance': profile.risk_tolerance,
                'preferred_authorities': profile.preferred_authorities,
                'session_duration_avg': profile.session_duration_avg
            })

        return profile_data

    except Exception as e:
        logger.error(f"Error getting behavior profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve behavior profile")


@router.post(
    "/admin/retrain",
    summary="Retrain AI models (Admin only)",
    description="Trigger retraining of personalization AI models"
)
async def retrain_ai_models(
    background_tasks: BackgroundTasks,
    model_type: Optional[str] = Query(None, description="Specific model to retrain"),
    user_scope: Optional[List[str]] = Query(None, description="Specific users to train on"),
    current_user: UserProfile = Depends(get_current_active_user),
    services: Dict = Depends(get_ai_services)
):
    """
    Trigger AI model retraining (Admin only)

    - **model_type**: Optional specific model to retrain
    - **user_scope**: Optional specific users to train on
    """
    try:
        # Verify admin authorization
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")

        learning_system = services['learning_system']

        # Schedule background retraining
        background_tasks.add_task(
            _retrain_models,
            learning_system,
            model_type,
            user_scope
        )

        return {
            "message": "Model retraining scheduled",
            "model_type": model_type or "all",
            "user_scope": user_scope or "all_users"
        }

    except Exception as e:
        logger.error(f"Error scheduling model retraining: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to schedule model retraining")


@router.get(
    "/admin/learning/insights",
    summary="Get learning system insights (Admin only)",
    description="Get insights about AI learning performance and trends"
)
async def get_learning_insights(
    time_period_days: int = Query(30, ge=1, le=365, description="Time period to analyze"),
    current_user: UserProfile = Depends(get_current_active_user),
    services: Dict = Depends(get_ai_services)
):
    """
    Get AI learning system insights (Admin only)

    - **time_period_days**: Time period to analyze (1-365 days)
    """
    try:
        # Verify admin authorization
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")

        learning_system = services['learning_system']

        # Get learning insights
        insights = await learning_system.generate_learning_insights(time_period_days)

        return {
            "time_period_days": time_period_days,
            "insights": insights,
            "generated_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting learning insights: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve learning insights")


# Background task functions
async def _update_user_learning(user_id: str, feedback_request: FeedbackRequest, services: Dict):
    """Background task to update user learning based on feedback"""
    try:
        learning_system = services['learning_system']
        behavior_analyzer = services['behavior_analyzer']

        # Get recent user interactions
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        interactions_result = services['supabase'].table('user_interactions')\
            .select('*')\
            .eq('user_id', user_id)\
            .gte('timestamp', cutoff_date.isoformat())\
            .execute()

        interactions = interactions_result.data

        # Update user preferences based on implicit signals
        implicit_signals = []
        for interaction in interactions:
            implicit_signals.append({
                'type': 'interaction',
                'interaction_type': interaction['interaction_type'],
                'context': interaction.get('context', {}),
                'strength': 1.0
            })

        await learning_system.update_user_preferences(user_id, implicit_signals)

        logger.info(f"Updated learning for user {user_id} based on feedback")

    except Exception as e:
        logger.error(f"Error in background learning update: {str(e)}")


async def _retrain_models(learning_system: LearningSystem, model_type: Optional[str], user_scope: Optional[List[str]]):
    """Background task to retrain AI models"""
    try:
        training_results = await learning_system.train_personalization_models(
            user_data=user_scope,
            model_type=model_type
        )

        logger.info(f"Completed model retraining: {training_results}")

    except Exception as e:
        logger.error(f"Error in background model retraining: {str(e)}")


# ======== PRIVACY AND CONSENT MANAGEMENT ENDPOINTS ========

@router.post(
    "/privacy/consent/request",
    summary="Request user consent",
    description="Request user consent for specific data processing activities"
)
async def request_consent(
    consent_type: ConsentType,
    purpose: str,
    data_categories: List[DataCategory],
    processing_details: Dict[str, Any],
    legal_basis: str = "consent",
    current_user: UserProfile = Depends(get_current_active_user),
    services: Dict = Depends(get_ai_services)
):
    """
    Request user consent for data processing

    - **consent_type**: Type of consent being requested
    - **purpose**: Purpose of data processing
    - **data_categories**: Categories of data to be processed
    - **processing_details**: Details about processing activities
    - **legal_basis**: Legal basis for processing
    """
    try:
        privacy_manager = services['privacy_manager']

        consent_id = await privacy_manager.request_consent(
            user_id=current_user.user_id,
            consent_type=consent_type,
            purpose=purpose,
            data_categories=data_categories,
            processing_details=processing_details,
            legal_basis=legal_basis
        )

        return {
            "consent_id": consent_id,
            "message": "Consent request created successfully",
            "status": "pending"
        }

    except Exception as e:
        logger.error(f"Error requesting consent: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to request consent")


@router.post(
    "/privacy/consent/{consent_id}/grant",
    summary="Grant consent",
    description="Grant consent for data processing"
)
async def grant_consent(
    consent_id: str,
    current_user: UserProfile = Depends(get_current_active_user),
    services: Dict = Depends(get_ai_services)
):
    """
    Grant user consent for data processing

    - **consent_id**: Consent record identifier
    """
    try:
        privacy_manager = services['privacy_manager']

        success = await privacy_manager.grant_consent(
            consent_id=consent_id,
            user_id=current_user.user_id
        )

        if not success:
            raise HTTPException(status_code=400, detail="Failed to grant consent")

        return {
            "message": "Consent granted successfully",
            "status": "granted"
        }

    except Exception as e:
        logger.error(f"Error granting consent: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to grant consent")


@router.post(
    "/privacy/consent/{consent_type}/withdraw",
    summary="Withdraw consent",
    description="Withdraw consent and stop related data processing"
)
async def withdraw_consent(
    consent_type: ConsentType,
    withdrawal_reason: Optional[str] = None,
    current_user: UserProfile = Depends(get_current_active_user),
    services: Dict = Depends(get_ai_services)
):
    """
    Withdraw user consent for data processing

    - **consent_type**: Type of consent to withdraw
    - **withdrawal_reason**: Optional reason for withdrawal
    """
    try:
        privacy_manager = services['privacy_manager']

        success = await privacy_manager.withdraw_consent(
            user_id=current_user.user_id,
            consent_type=consent_type,
            withdrawal_reason=withdrawal_reason
        )

        if not success:
            raise HTTPException(status_code=400, detail="Failed to withdraw consent")

        return {
            "message": "Consent withdrawn successfully",
            "status": "withdrawn"
        }

    except Exception as e:
        logger.error(f"Error withdrawing consent: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to withdraw consent")


@router.get(
    "/privacy/settings",
    summary="Get privacy settings",
    description="Get user's privacy settings and preferences"
)
async def get_privacy_settings(
    current_user: UserProfile = Depends(get_current_active_user),
    services: Dict = Depends(get_ai_services)
):
    """
    Get user's privacy settings and preferences
    """
    try:
        privacy_manager = services['privacy_manager']

        settings = await privacy_manager.get_user_privacy_settings(current_user.user_id)

        return {
            "user_id": settings.user_id,
            "personalization_enabled": settings.personalization_enabled,
            "behavioral_tracking_enabled": settings.behavioral_tracking_enabled,
            "ai_learning_enabled": settings.ai_learning_enabled,
            "analytics_enabled": settings.analytics_enabled,
            "data_retention_period_days": settings.data_retention_period_days,
            "anonymization_level": settings.anonymization_level,
            "export_format_preference": settings.export_format_preference,
            "notification_preferences": settings.notification_preferences,
            "third_party_sharing_allowed": settings.third_party_sharing_allowed,
            "profile_visibility": settings.profile_visibility,
            "data_portability_enabled": settings.data_portability_enabled,
            "automated_decision_making_consent": settings.automated_decision_making_consent,
            "last_updated": settings.updated_at.isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting privacy settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve privacy settings")


@router.put(
    "/privacy/settings",
    summary="Update privacy settings",
    description="Update user's privacy settings and preferences"
)
async def update_privacy_settings(
    settings_updates: Dict[str, Any],
    current_user: UserProfile = Depends(get_current_active_user),
    services: Dict = Depends(get_ai_services)
):
    """
    Update user's privacy settings

    - **settings_updates**: Privacy settings to update
    """
    try:
        privacy_manager = services['privacy_manager']

        updated_settings = await privacy_manager.update_privacy_settings(
            user_id=current_user.user_id,
            settings_updates=settings_updates
        )

        return {
            "message": "Privacy settings updated successfully",
            "updated_settings": {
                "personalization_enabled": updated_settings.personalization_enabled,
                "behavioral_tracking_enabled": updated_settings.behavioral_tracking_enabled,
                "ai_learning_enabled": updated_settings.ai_learning_enabled,
                "data_retention_period_days": updated_settings.data_retention_period_days,
                "anonymization_level": updated_settings.anonymization_level
            }
        }

    except Exception as e:
        logger.error(f"Error updating privacy settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update privacy settings")


@router.post(
    "/privacy/export",
    summary="Export user data",
    description="Export user's personal data (GDPR Article 20)"
)
async def export_user_data(
    data_categories: Optional[List[DataCategory]] = None,
    format_type: str = "json",
    current_user: UserProfile = Depends(get_current_active_user),
    services: Dict = Depends(get_ai_services)
):
    """
    Export user's personal data

    - **data_categories**: Specific data categories to export (optional, defaults to all)
    - **format_type**: Export format (json, csv, xml)
    """
    try:
        privacy_manager = services['privacy_manager']

        export_data = await privacy_manager.export_user_data(
            user_id=current_user.user_id,
            data_categories=data_categories,
            format_type=format_type
        )

        return {
            "message": "Data export completed successfully",
            "export_data": export_data,
            "download_url": f"/api/v1/ai/personalization/privacy/download/{export_data.get('export_id', 'unknown')}"
        }

    except Exception as e:
        logger.error(f"Error exporting user data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to export user data")


@router.delete(
    "/privacy/data",
    summary="Delete user data",
    description="Delete or anonymize user's personal data (GDPR Article 17)"
)
async def delete_user_data(
    data_categories: Optional[List[DataCategory]] = None,
    anonymize_instead: bool = False,
    confirmation: str = Query(..., description="Type 'DELETE' to confirm"),
    current_user: UserProfile = Depends(get_current_active_user),
    services: Dict = Depends(get_ai_services)
):
    """
    Delete or anonymize user's personal data

    - **data_categories**: Specific data categories to delete (optional, defaults to all)
    - **anonymize_instead**: Anonymize data instead of deleting
    - **confirmation**: Must type 'DELETE' to confirm
    """
    try:
        # Require explicit confirmation
        if confirmation != "DELETE":
            raise HTTPException(
                status_code=400,
                detail="Confirmation required. Please provide 'DELETE' as confirmation parameter."
            )

        privacy_manager = services['privacy_manager']

        success = await privacy_manager.delete_user_data(
            user_id=current_user.user_id,
            data_categories=data_categories,
            anonymize_instead=anonymize_instead
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to process data deletion request")

        action = "anonymized" if anonymize_instead else "deleted"
        return {
            "message": f"User data {action} successfully",
            "action": action,
            "categories": [cat.value for cat in data_categories] if data_categories else "all"
        }

    except Exception as e:
        logger.error(f"Error deleting user data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete user data")


@router.get(
    "/privacy/audit",
    summary="Audit data processing",
    description="Get audit trail of data processing activities"
)
async def audit_data_processing(
    start_date: Optional[datetime] = Query(None, description="Start date for audit period"),
    end_date: Optional[datetime] = Query(None, description="End date for audit period"),
    current_user: UserProfile = Depends(get_current_active_user),
    services: Dict = Depends(get_ai_services)
):
    """
    Get audit trail of data processing activities

    - **start_date**: Start date for audit period (optional)
    - **end_date**: End date for audit period (optional)
    """
    try:
        privacy_manager = services['privacy_manager']

        # Regular users can only audit their own data
        user_id = current_user.user_id if current_user.role != "admin" else None

        processing_logs = await privacy_manager.audit_data_processing(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )

        return {
            "audit_period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            },
            "total_logs": len(processing_logs),
            "processing_logs": [
                {
                    "log_id": log.log_id,
                    "processing_purpose": log.processing_purpose.value,
                    "data_categories": [cat.value for cat in log.data_categories],
                    "legal_basis": log.legal_basis,
                    "processor_id": log.processor_id,
                    "processing_location": log.processing_location,
                    "automated": log.automated,
                    "timestamp": log.timestamp.isoformat()
                }
                for log in processing_logs
            ]
        }

    except Exception as e:
        logger.error(f"Error auditing data processing: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to audit data processing")


@router.get(
    "/privacy/consent/status",
    summary="Check consent status",
    description="Check status of user's consent for different processing activities"
)
async def check_consent_status(
    current_user: UserProfile = Depends(get_current_active_user),
    services: Dict = Depends(get_ai_services)
):
    """
    Check status of user's consent for different processing activities
    """
    try:
        privacy_manager = services['privacy_manager']

        consent_status = {}

        # Check all consent types
        for consent_type in ConsentType:
            consent_status[consent_type.value] = await privacy_manager.check_consent(
                user_id=current_user.user_id,
                consent_type=consent_type
            )

        return {
            "user_id": current_user.user_id,
            "consent_status": consent_status,
            "last_checked": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error checking consent status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check consent status")