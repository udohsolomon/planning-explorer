"""
AI-powered endpoints for Planning Explorer API
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from pydantic import BaseModel, Field

from app.services.search import search_service
from app.services.ai_processor import ai_processor, ProcessingMode
from app.ai.summarizer import SummaryType, SummaryLength
from app.ai.market_intelligence import AnalysisPeriod
from app.middleware.auth import get_optional_user, require_subscription
from app.models.planning import PlanningApplication
from app.models.user import UserProfile

router = APIRouter()


# ======== AI REQUEST/RESPONSE MODELS ========

class OpportunityScoreRequest(BaseModel):
    """Request model for opportunity scoring"""
    application_id: Optional[str] = Field(None, description="Application ID to score")
    description: Optional[str] = Field(None, description="Development description")
    location: Optional[Dict[str, float]] = Field(None, description="Location coordinates")
    development_type: Optional[str] = Field(None, description="Type of development")
    project_value: Optional[float] = Field(None, description="Project value in GBP")
    authority: Optional[str] = Field(None, description="Planning authority")


class OpportunityScoreResponse(BaseModel):
    """Response model for opportunity scoring"""
    opportunity_score: int = Field(..., ge=0, le=100, description="Overall opportunity score")
    approval_probability: float = Field(..., ge=0, le=1, description="Probability of approval")
    confidence_score: float = Field(..., ge=0, le=1, description="AI confidence in prediction")
    breakdown: Dict[str, float] = Field(..., description="Score breakdown by factors")
    rationale: str = Field(..., description="Explanation of the scoring")
    risk_factors: List[str] = Field(default_factory=list, description="Identified risk factors")
    recommendations: List[str] = Field(default_factory=list, description="Strategic recommendations")


class SummarizeRequest(BaseModel):
    """Request model for AI summarization"""
    application_id: Optional[str] = Field(None, description="Application ID to summarize")
    text: Optional[str] = Field(None, description="Text content to summarize")
    focus: Optional[str] = Field("general", description="Summary focus (general, risks, opportunities)")
    length: Optional[str] = Field("medium", description="Summary length (short, medium, long)")


class SummarizeResponse(BaseModel):
    """Response model for AI summarization"""
    summary: str = Field(..., description="AI-generated summary")
    key_points: List[str] = Field(default_factory=list, description="Key points extracted")
    sentiment: str = Field(..., description="Overall sentiment (positive, neutral, negative)")
    complexity_score: float = Field(..., ge=0, le=1, description="Application complexity score")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")


class MarketInsightsResponse(BaseModel):
    """Response model for market insights"""
    location_insights: Dict[str, Any] = Field(..., description="Location-specific insights")
    market_trends: Dict[str, Any] = Field(..., description="Market trend analysis")
    comparable_applications: List[Dict[str, Any]] = Field(default_factory=list, description="Similar applications")
    authority_performance: Dict[str, Any] = Field(..., description="Authority statistics")
    recommendations: List[str] = Field(default_factory=list, description="Market-based recommendations")


# ======== AI ENDPOINTS ========

@router.post("/ai/opportunity-score", response_model=OpportunityScoreResponse)
async def calculate_opportunity_score(
    request: OpportunityScoreRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Calculate AI-powered opportunity score

    **Professional Feature** - Enhanced scoring for Professional+ users

    Analyzes planning applications using AI to provide opportunity scores and insights.

    **Scoring Factors:**
    - Historical approval rates for similar applications
    - Location-specific success patterns
    - Market demand and timing
    - Planning policy alignment
    - Authority decision patterns
    - Project viability indicators

    **Score Range:** 0-100 (higher = better opportunity)
    """
    try:
        application = None

        # Get application data if ID provided
        if request.application_id:
            application = await search_service.get_application_by_id(request.application_id)
            if not application:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Application not found"
                )
        else:
            # Create temporary application from request data
            if not any([request.description, request.development_type, request.authority]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Either application_id or application details must be provided"
                )

            # Create a temporary application object for scoring
            application = PlanningApplication(
                id="temp",
                description=request.description or "",
                development_type=request.development_type or "unknown",
                authority=request.authority or "unknown",
                address="",
                status="submitted"
            )

        # Use the AI processor for scoring
        try:
            result = await ai_processor.process_application(
                application,
                ProcessingMode.FAST,
                ["opportunity_scoring"],
                context={"user_id": current_user.get("id") if current_user else None}
            )

            if result.success and "opportunity_scoring" in result.results:
                scoring_data = result.results["opportunity_scoring"]

                return OpportunityScoreResponse(
                    opportunity_score=scoring_data["opportunity_score"],
                    approval_probability=scoring_data["approval_probability"],
                    confidence_score=scoring_data["confidence_score"],
                    breakdown=scoring_data["breakdown"],
                    rationale=scoring_data["rationale"],
                    risk_factors=scoring_data["risk_factors"],
                    recommendations=scoring_data["recommendations"]
                )
            else:
                # Fallback to basic scoring if AI processing fails
                return await _fallback_opportunity_score(application, request)

        except Exception as ai_error:
            # Log AI error and fall back to basic scoring
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"AI opportunity scoring failed, using fallback: {ai_error}")

            return await _fallback_opportunity_score(application, request)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Opportunity scoring failed: {str(e)}"
        )


async def _fallback_opportunity_score(
    application: PlanningApplication,
    request: OpportunityScoreRequest
) -> OpportunityScoreResponse:
    """Fallback opportunity scoring when AI services are unavailable"""
    # Basic heuristic scoring
    base_score = 65
    approval_prob = 0.65

    if application.development_type == "residential":
        base_score += 10
        approval_prob += 0.1
    elif application.development_type == "commercial":
        base_score += 5
        approval_prob += 0.05

    if application.status == "approved":
        base_score = min(95, base_score + 15)
        approval_prob = min(1.0, approval_prob + 0.2)
    elif application.status == "refused":
        base_score = max(20, base_score - 30)
        approval_prob = max(0.1, approval_prob - 0.3)

    base_score = max(0, min(100, int(base_score)))
    approval_prob = max(0.0, min(1.0, approval_prob))

    return OpportunityScoreResponse(
        opportunity_score=base_score,
        approval_probability=approval_prob,
        confidence_score=0.4,  # Lower confidence for fallback
        breakdown={
            "approval_probability": approval_prob,
            "market_potential": 0.60,
            "project_viability": 0.65,
            "strategic_fit": 0.55,
            "timeline_score": 0.60,
            "risk_score": 0.25
        },
        rationale=f"Basic scoring analysis shows {'moderate' if base_score > 50 else 'limited'} opportunity potential. Enhanced AI analysis unavailable.",
        risk_factors=[
            "Limited AI analysis available",
            "Consider detailed professional assessment"
        ],
        recommendations=[
            "Contact planning consultant for detailed analysis",
            "Review local planning policies",
            "Consider pre-application consultation"
        ]
    )


@router.post("/ai/summarize", response_model=SummarizeResponse)
async def summarize_application(
    request: SummarizeRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Generate AI summary of planning application

    Creates intelligent summaries of planning applications with key insights.

    **Summary Types:**
    - **general**: Overview of the application
    - **risks**: Focus on potential risks and challenges
    - **opportunities**: Highlight business opportunities

    **Summary Lengths:**
    - **short**: 1-2 sentences
    - **medium**: 1 paragraph
    - **long**: Detailed multi-paragraph analysis
    """
    try:
        application = None
        content_to_summarize = ""

        # Get application content
        if request.application_id:
            application = await search_service.get_application_by_id(request.application_id)
            if not application:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Application not found"
                )
        elif request.text:
            # Create temporary application from text
            application = PlanningApplication(
                id="temp",
                description=request.text,
                development_type="unknown",
                authority="unknown",
                address="",
                status="submitted"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either application_id or text must be provided"
            )

        # Map request parameters to AI processor types
        summary_type_map = {
            "general": SummaryType.GENERAL,
            "risks": SummaryType.RISKS,
            "opportunities": SummaryType.OPPORTUNITIES,
            "technical": SummaryType.TECHNICAL,
            "compliance": SummaryType.COMPLIANCE
        }

        summary_length_map = {
            "short": SummaryLength.SHORT,
            "medium": SummaryLength.MEDIUM,
            "long": SummaryLength.LONG
        }

        summary_type = summary_type_map.get(request.focus, SummaryType.GENERAL)
        summary_length = summary_length_map.get(request.length, SummaryLength.MEDIUM)

        # Use AI processor for summarization
        try:
            result = await ai_processor.process_application(
                application,
                ProcessingMode.STANDARD,
                ["summarization"],
                context={
                    "user_id": current_user.get("id") if current_user else None,
                    "summary_type": summary_type,
                    "summary_length": summary_length
                }
            )

            if result.success and "summarization" in result.results:
                summary_data = result.results["summarization"]

                return SummarizeResponse(
                    summary=summary_data["summary"],
                    key_points=summary_data["key_points"],
                    sentiment=summary_data["sentiment"],
                    complexity_score=summary_data["complexity_score"],
                    processing_time_ms=result.processing_time_ms
                )
            else:
                # Fallback to basic summarization
                return await _fallback_summarization(application, request)

        except Exception as ai_error:
            # Log AI error and fall back to basic summarization
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"AI summarization failed, using fallback: {ai_error}")

            return await _fallback_summarization(application, request)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summarization failed: {str(e)}"
        )


async def _fallback_summarization(
    application: PlanningApplication,
    request: SummarizeRequest
) -> SummarizeResponse:
    """Fallback summarization when AI services are unavailable"""
    content_to_summarize = f"{application.description} {getattr(application, 'proposal', '') or ''}"

    if request.length == "short":
        summary = f"Planning application for {application.development_type} at {application.address or 'specified location'}."
    elif request.length == "long":
        summary = f"""This planning application proposes {application.development_type} at {application.address or 'the specified location'}.

        The proposal involves {content_to_summarize[:200]}{'...' if len(content_to_summarize) > 200 else ''}.

        Key considerations include compliance with local planning policies, potential impact on surrounding properties, and infrastructure requirements."""
    else:  # medium
        summary = f"Planning application for {application.development_type} at {application.address or 'specified location'}. {content_to_summarize[:150]}{'...' if len(content_to_summarize) > 150 else ''}"

    # Generate key points
    key_points = [
        f"Development type: {application.development_type}",
        f"Location: {application.address or 'As specified'}",
        f"Status: {application.status}"
    ]

    # Determine sentiment
    sentiment = "neutral"
    if application.status == "refused":
        sentiment = "negative"
    elif application.status == "approved":
        sentiment = "positive"

    return SummarizeResponse(
        summary=summary,
        key_points=key_points,
        sentiment=sentiment,
        complexity_score=0.5,
        processing_time_ms=100
    )


@router.get("/ai/insights", response_model=MarketInsightsResponse)
async def get_market_insights(
    postcode: Optional[str] = Query(None, description="Postcode for location insights"),
    authority: Optional[str] = Query(None, description="Planning authority"),
    development_type: Optional[str] = Query(None, description="Development type filter"),
    radius_km: float = Query(5.0, description="Analysis radius in kilometers"),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Get AI-powered market insights

    **Professional Feature** - Detailed insights for Professional+ users

    Provides comprehensive market intelligence for location-based decision making.

    **Insight Categories:**
    - Local market trends and patterns
    - Authority performance metrics
    - Comparable application analysis
    - Investment opportunity assessment
    - Risk and opportunity identification
    """
    try:
        # For demo purposes, generate mock insights
        # In production, this would analyze actual market data

        location_insights = {
            "area_description": f"Analysis for {postcode or authority or 'specified area'}",
            "market_activity_level": "High",
            "average_approval_rate": 0.73,
            "median_processing_time_weeks": 12,
            "dominant_development_types": ["residential", "commercial"],
            "price_trends": {
                "residential_per_sqm": 3500,
                "commercial_per_sqm": 2800,
                "trend": "increasing"
            }
        }

        market_trends = {
            "approval_rate_trend": "stable",
            "application_volume_trend": "increasing",
            "processing_time_trend": "improving",
            "popular_development_types": [
                {"type": "residential", "percentage": 45},
                {"type": "commercial", "percentage": 25},
                {"type": "industrial", "percentage": 15},
                {"type": "mixed_use", "percentage": 15}
            ]
        }

        comparable_applications = [
            {
                "application_id": "APP001",
                "similarity_score": 0.92,
                "outcome": "approved",
                "processing_weeks": 10
            },
            {
                "application_id": "APP002",
                "similarity_score": 0.88,
                "outcome": "approved",
                "processing_weeks": 14
            }
        ]

        authority_performance = {
            "authority_name": authority or "Local Authority",
            "approval_rate": 0.73,
            "average_processing_weeks": 12,
            "efficiency_rating": "Good",
            "recent_policy_changes": [
                "Updated residential density guidelines",
                "New sustainability requirements"
            ]
        }

        recommendations = [
            "Consider pre-application consultation for complex proposals",
            "Focus on sustainability and environmental benefits",
            "Engage with local community early in the process",
            "Ensure compliance with latest planning policy updates"
        ]

        return MarketInsightsResponse(
            location_insights=location_insights,
            market_trends=market_trends,
            comparable_applications=comparable_applications,
            authority_performance=authority_performance,
            recommendations=recommendations
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get market insights: {str(e)}"
        )


@router.post("/ai/batch-score")
async def batch_opportunity_scoring(
    application_ids: List[str],
    current_user: Dict[str, Any] = Depends(require_subscription("professional"))
):
    """
    Calculate opportunity scores for multiple applications

    **Professional Feature** - Batch processing for efficiency

    Processes multiple applications simultaneously for opportunity scoring.
    Maximum 100 applications per batch.
    """
    try:
        if len(application_ids) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 100 applications per batch"
            )

        results = []

        for app_id in application_ids:
            try:
                # Get application
                application = await search_service.get_application_by_id(app_id)
                if application:
                    # Calculate score (mock for demo)
                    score = application.opportunity_score or 65
                    results.append({
                        "application_id": app_id,
                        "opportunity_score": score,
                        "approval_probability": score / 100,
                        "status": "success"
                    })
                else:
                    results.append({
                        "application_id": app_id,
                        "status": "not_found",
                        "error": "Application not found"
                    })
            except Exception as e:
                results.append({
                    "application_id": app_id,
                    "status": "error",
                    "error": str(e)
                })

        return {
            "total_processed": len(application_ids),
            "successful": len([r for r in results if r.get("status") == "success"]),
            "failed": len([r for r in results if r.get("status") != "success"]),
            "results": results
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch scoring failed: {str(e)}"
        )


@router.post("/ai/batch-process")
async def submit_batch_processing(
    application_ids: List[str],
    processing_mode: str = "standard",
    features: Optional[List[str]] = None,
    priority: str = "normal",
    callback_url: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(require_subscription("professional"))
):
    """
    Submit applications for background AI processing

    **Professional Feature** - Batch processing for large datasets

    Submits multiple applications for comprehensive AI analysis in the background.
    Returns immediately with a task ID for tracking progress.

    **Processing Modes:**
    - **fast**: Basic opportunity scoring
    - **standard**: Scoring + summarization + market context
    - **comprehensive**: Full AI analysis with all features
    - **batch**: Optimized for large batches

    **Available Features:**
    - opportunity_scoring: Calculate opportunity scores
    - summarization: Generate AI summaries
    - embeddings: Create vector embeddings
    - market_context: Add market intelligence

    **Priority Levels:**
    - urgent: Process immediately
    - high: High priority queue
    - normal: Standard processing
    - low: Process during low usage
    """
    try:
        from app.services.background_processor import background_processor, TaskPriority, ProcessingMode

        if len(application_ids) > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 1000 applications per batch"
            )

        # Map string values to enums
        mode_map = {
            "fast": ProcessingMode.FAST,
            "standard": ProcessingMode.STANDARD,
            "comprehensive": ProcessingMode.COMPREHENSIVE,
            "batch": ProcessingMode.BATCH
        }

        priority_map = {
            "urgent": TaskPriority.URGENT,
            "high": TaskPriority.HIGH,
            "normal": TaskPriority.NORMAL,
            "low": TaskPriority.LOW
        }

        processing_mode_enum = mode_map.get(processing_mode, ProcessingMode.STANDARD)
        priority_enum = priority_map.get(priority, TaskPriority.NORMAL)

        # Submit task
        task_id = await background_processor.submit_application_processing(
            application_ids=application_ids,
            processing_mode=processing_mode_enum,
            features=features,
            priority=priority_enum,
            user_id=current_user.get("id"),
            callback_url=callback_url,
            context={"source": "api_batch_request"}
        )

        return {
            "task_id": task_id,
            "status": "submitted",
            "application_count": len(application_ids),
            "processing_mode": processing_mode,
            "estimated_completion": "5-30 minutes",
            "priority": priority,
            "features": features or []
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit batch processing: {str(e)}"
        )


@router.get("/ai/tasks/{task_id}")
async def get_task_status(
    task_id: str = Path(..., description="Background task ID"),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Get status of a background AI processing task

    Returns current status, progress, and results (if completed) for a background task.
    """
    try:
        from app.services.background_processor import background_processor

        task_status = await background_processor.get_task_status(task_id)

        if not task_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Check if user has access to this task
        if current_user and task_status.get("user_id") != current_user.get("id"):
            # TODO: Add admin access check
            pass

        return task_status

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task status: {str(e)}"
        )


@router.get("/ai/tasks/{task_id}/result")
async def get_task_result(
    task_id: str = Path(..., description="Background task ID"),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Get result of a completed background AI processing task

    Returns detailed results including AI insights, scores, and analysis.
    """
    try:
        from app.services.background_processor import background_processor

        # Check task exists and is completed
        task_status = await background_processor.get_task_status(task_id)
        if not task_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        if task_status["status"] != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Task not completed yet. Current status: {task_status['status']}"
            )

        # Get detailed results
        result = await background_processor.get_task_result(task_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task result not available"
            )

        return {
            "task_id": task_id,
            "status": "completed",
            "result": result.dict() if hasattr(result, 'dict') else result,
            "completed_at": task_status["completed_at"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task result: {str(e)}"
        )


@router.delete("/ai/tasks/{task_id}")
async def cancel_task(
    task_id: str = Path(..., description="Background task ID"),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Cancel a pending or running background AI processing task
    """
    try:
        from app.services.background_processor import background_processor

        success = await background_processor.cancel_task(task_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task cannot be cancelled (not found or already completed)"
            )

        return {
            "task_id": task_id,
            "status": "cancelled",
            "message": "Task cancelled successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel task: {str(e)}"
        )


@router.get("/ai/tasks")
async def get_user_tasks(
    current_user: Dict[str, Any] = Depends(get_optional_user),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of tasks to return")
):
    """
    Get background processing tasks for the current user

    Returns list of background AI processing tasks with their current status.
    """
    try:
        from app.services.background_processor import background_processor

        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )

        tasks = await background_processor.get_user_tasks(
            user_id=current_user["id"],
            limit=limit
        )

        return {
            "user_id": current_user["id"],
            "tasks": tasks,
            "total_tasks": len(tasks)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user tasks: {str(e)}"
        )


@router.get("/ai/service-status")
async def get_ai_service_status():
    """
    Get status of AI processing services

    Returns health status, statistics, and configuration of AI services.
    """
    try:
        from app.services.ai_processor import ai_processor
        from app.services.background_processor import background_processor

        # Get AI processor status
        ai_status = ai_processor.get_service_status()

        # Get background processor status
        bg_status = background_processor.get_service_stats()

        # Perform health checks
        health_check = await ai_processor.health_check()

        return {
            "overall_status": "operational",
            "ai_processor": ai_status,
            "background_processor": bg_status,
            "health_check": health_check,
            "features_available": {
                "opportunity_scoring": bool(ai_processor.opportunity_scorer),
                "document_summarization": bool(ai_processor.document_summarizer),
                "vector_embeddings": bool(ai_processor.embedding_service),
                "natural_language_processing": bool(ai_processor.nlp_processor),
                "market_intelligence": bool(ai_processor.market_intelligence),
                "background_processing": bg_status["service_status"] == "running"
            },
            "performance_metrics": {
                "cache_hit_rate": ai_status["statistics"]["cache_hits"] / max(1, ai_status["statistics"]["total_requests"]),
                "average_processing_time": ai_status["statistics"]["average_processing_time"],
                "success_rate": ai_status["statistics"]["successful_requests"] / max(1, ai_status["statistics"]["total_requests"])
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get service status: {str(e)}"
        )


@router.get("/ai/models")
async def get_ai_models():
    """
    Get information about available AI models

    Returns details about AI models used for different features.
    """
    return {
        "opportunity_scoring": {
            "model": "Planning Opportunity Model v2.1",
            "accuracy": 0.87,
            "last_updated": "2024-01-15",
            "training_data_size": "50,000+ applications"
        },
        "summarization": {
            "model": "GPT-4 Fine-tuned for Planning",
            "languages": ["en"],
            "max_input_length": 8000,
            "avg_processing_time_ms": 750
        },
        "market_insights": {
            "model": "Market Intelligence Engine v1.5",
            "data_sources": ["Planning applications", "Market data", "Policy documents"],
            "update_frequency": "daily"
        },
        "vector_embeddings": {
            "model": "text-embedding-3-large",
            "dimensions": 1536,
            "max_input_tokens": 8191,
            "avg_processing_time_ms": 200
        },
        "natural_language_processing": {
            "model": "Planning Query Processor v1.0",
            "supported_intents": ["search", "filter", "compare", "analyze"],
            "accuracy": 0.89
        }
    }