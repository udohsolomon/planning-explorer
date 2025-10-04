"""
Planning applications endpoints for Planning Explorer API
"""
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from datetime import datetime
import logging

from app.services.search import search_service
from app.services.ai_processor import ProcessingMode
from app.models.planning import (
    PlanningApplication, PlanningApplicationResponse, SearchResponse, SearchFilters,
    ApplicationStatus, DevelopmentType, ApplicationType, DecisionType
)
from app.models.applications import (
    ApplicationListResponse, ApplicationListData, ApplicationPreview
)
from app.middleware.auth import get_optional_user, log_api_request
from app.db.elasticsearch import es_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/applications", response_model=SearchResponse)
async def get_applications(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of results per page"),
    authority: Optional[str] = Query(None, description="Filter by planning authority"),
    app_status: Optional[ApplicationStatus] = Query(None, description="Filter by application status", alias="status"),
    development_type: Optional[DevelopmentType] = Query(None, description="Filter by development type"),
    application_type: Optional[ApplicationType] = Query(None, description="Filter by application type"),
    decision: Optional[DecisionType] = Query(None, description="Filter by decision outcome"),
    postcode: Optional[str] = Query(None, description="Filter by postcode"),
    submission_date_from: Optional[datetime] = Query(None, description="Submission date from"),
    submission_date_to: Optional[datetime] = Query(None, description="Submission date to"),
    decision_date_from: Optional[datetime] = Query(None, description="Decision date from"),
    decision_date_to: Optional[datetime] = Query(None, description="Decision date to"),
    opportunity_score_min: Optional[int] = Query(None, ge=0, le=100, description="Minimum opportunity score"),
    opportunity_score_max: Optional[int] = Query(None, ge=0, le=100, description="Maximum opportunity score"),
    approval_probability_min: Optional[float] = Query(None, ge=0, le=1, description="Minimum approval probability"),
    approval_probability_max: Optional[float] = Query(None, ge=0, le=1, description="Maximum approval probability"),
    project_value_min: Optional[float] = Query(None, description="Minimum project value"),
    project_value_max: Optional[float] = Query(None, description="Maximum project value"),
    lat: Optional[float] = Query(None, description="Latitude for radius search"),
    lon: Optional[float] = Query(None, description="Longitude for radius search"),
    radius_km: Optional[float] = Query(None, description="Search radius in kilometers"),
    sort_by: str = Query("submission_date", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user),
    _: None = Depends(log_api_request)
):
    """
    Get list of planning applications with optional filters

    Returns paginated list of planning applications with comprehensive filtering options.

    **Available Filters:**
    - **authority**: Planning authority name
    - **status**: Application status (submitted, validated, approved, etc.)
    - **development_type**: Type of development (residential, commercial, etc.)
    - **application_type**: Application type (full, outline, householder, etc.)
    - **decision**: Decision outcome (approved, refused, withdrawn)
    - **postcode**: Postcode filter (supports partial matching)
    - **submission_date_from/to**: Date range for submission
    - **decision_date_from/to**: Date range for decision
    - **opportunity_score_min/max**: AI opportunity score range (0-100)
    - **approval_probability_min/max**: AI approval probability range (0-1)
    - **project_value_min/max**: Project value range in GBP
    - **lat/lon/radius_km**: Geographic radius search

    **Sorting:**
    - **sort_by**: submission_date, decision_date, opportunity_score, approval_probability, project_value
    - **sort_order**: asc or desc
    """
    try:
        # Build filters from query parameters
        filters = SearchFilters()

        if authority:
            filters.authorities = [authority]
        if app_status:
            filters.statuses = [app_status]
        if development_type:
            filters.development_types = [development_type]
        if application_type:
            filters.application_types = [application_type]
        if decision:
            filters.decisions = [decision]
        if postcode:
            filters.postcode = postcode
        if submission_date_from:
            filters.submission_date_from = submission_date_from
        if submission_date_to:
            filters.submission_date_to = submission_date_to
        if decision_date_from:
            filters.decision_date_from = decision_date_from
        if decision_date_to:
            filters.decision_date_to = decision_date_to
        if opportunity_score_min is not None:
            filters.opportunity_score_min = opportunity_score_min
        if opportunity_score_max is not None:
            filters.opportunity_score_max = opportunity_score_max
        if approval_probability_min is not None:
            filters.approval_probability_min = approval_probability_min
        if approval_probability_max is not None:
            filters.approval_probability_max = approval_probability_max
        if project_value_min is not None:
            filters.project_value_min = project_value_min
        if project_value_max is not None:
            filters.project_value_max = project_value_max
        if lat is not None and lon is not None and radius_km is not None:
            filters.lat = lat
            filters.lon = lon
            filters.radius_km = radius_km

        return await search_service.get_applications_list(
            filters=filters if any(vars(filters).values()) else None,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get applications: {str(e)}"
        )


@router.get("/application", response_model=PlanningApplicationResponse)
async def get_application_by_id(
    id: str = Query(..., description="Planning application ID"),
    include_ai_insights: bool = Query(True, description="Include AI-generated insights"),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user),
    _: None = Depends(log_api_request)
):
    """
    Get detailed planning application by ID with AI-enhanced insights

    Returns complete details for a specific planning application including:
    - All application data and metadata
    - AI-generated insights and scores (if available)
    - Documents and consultation responses
    - Similar applications with AI similarity scoring
    - Planning history and constraints
    - Real-time opportunity scoring and market analysis
    """
    try:
        logger.info(f"[DEBUG ENDPOINT] Received request for application_id: '{id}'")
        logger.info(f"[DEBUG ENDPOINT] application_id type: {type(id)}, len: {len(id)}")
        logger.info(f"[DEBUG ENDPOINT] application_id repr: {repr(id)}")

        application = await search_service.get_application_by_id(id)

        logger.info(f"[DEBUG ENDPOINT] search_service returned: {application is not None}")

        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application {id} not found"
            )

        # Enhance with real-time AI insights if requested and user has access
        if include_ai_insights:
            try:
                from app.services.ai_processor import ai_processor

                # Process application with AI (fast mode for real-time response)
                ai_result = await ai_processor.process_application(
                    application,
                    ProcessingMode.FAST,
                    ["opportunity_scoring", "summarization", "market_context"],
                    context={"user_id": current_user.get("id") if current_user else None}
                )

                if ai_result.success:
                    # Update application with fresh AI insights
                    if "opportunity_scoring" in ai_result.results:
                        scoring = ai_result.results["opportunity_scoring"]
                        application.opportunity_score = scoring["opportunity_score"]
                        application.approval_probability = scoring["approval_probability"]
                        application.ai_insights = {
                            "opportunity_analysis": {
                                "score": scoring["opportunity_score"],
                                "confidence": scoring["confidence_score"],
                                "breakdown": scoring["breakdown"],
                                "rationale": scoring["rationale"],
                                "risk_factors": scoring["risk_factors"],
                                "recommendations": scoring["recommendations"]
                            }
                        }

                    if "summarization" in ai_result.results:
                        summary = ai_result.results["summarization"]
                        if not hasattr(application, 'ai_insights'):
                            application.ai_insights = {}
                        application.ai_insights["summary_analysis"] = {
                            "summary": summary["summary"],
                            "key_points": summary["key_points"],
                            "sentiment": summary["sentiment"],
                            "complexity_score": summary["complexity_score"]
                        }

                    if "market_context" in ai_result.results:
                        market = ai_result.results["market_context"]
                        if not hasattr(application, 'ai_insights'):
                            application.ai_insights = {}
                        application.ai_insights["market_context"] = market

                else:
                    # Log AI processing failure but continue
                    logger.warning(f"AI processing failed for {id}: {ai_result.errors}")

            except Exception as ai_error:
                # Log AI error but don't fail the request
                logger.warning(f"AI enhancement failed for {id}: {ai_error}")

        # Convert to response model (excludes embeddings and sensitive data)
        response_data = application.dict(exclude={
            'description_embedding', 'full_content_embedding', 'summary_embedding',
            'location_embedding', 'document_embeddings'
        })

        return PlanningApplicationResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get application: {str(e)}"
        )


@router.get("/applications/{application_id}/similar")
async def get_similar_applications(
    application_id: str = Path(..., description="Planning application ID"),
    limit: int = Query(5, ge=1, le=20, description="Number of similar applications to return"),
    use_ai_similarity: bool = Query(True, description="Use AI-powered similarity scoring"),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user),
    _: None = Depends(log_api_request)
):
    """
    Get applications similar to the specified application with AI-enhanced similarity

    Uses advanced AI to find applications with similar characteristics:
    - Semantic similarity using vector embeddings
    - Similar development type and scale
    - Geographic proximity analysis
    - Similar applicants or agents
    - Comparable project values and complexity
    - Historical outcome patterns
    """
    try:
        # Get the base application
        application = await search_service.get_application_by_id(application_id)

        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application {application_id} not found"
            )

        detailed_similar = []

        if use_ai_similarity:
            try:
                from app.services.ai_processor import ai_processor

                # Use AI-powered similarity search if available
                if ai_processor.embedding_service:
                    # Get candidate applications (filter by location/authority for performance)
                    candidates_response = await search_service.get_applications_list(
                        filters=SearchFilters(authorities=[application.authority]),
                        page_size=100  # Limit candidates for performance
                    )

                    # Convert summaries to full applications for similarity analysis
                    candidate_apps = []
                    for summary in candidates_response.results[:50]:  # Limit further
                        if summary.application_id != application_id:
                            full_app = await search_service.get_application_by_id(summary.application_id)
                            if full_app:
                                candidate_apps.append(full_app)

                    # Perform semantic similarity search
                    if candidate_apps:
                        similarity_results = await ai_processor.embedding_service.semantic_search(
                            application.description or "",
                            candidate_apps,
                            k=limit
                        )

                        # Process AI similarity results
                        for result in similarity_results.results[:limit]:
                            similar_app = await search_service.get_application_by_id(result.application_id)
                            if similar_app:
                                summary_data = similar_app.dict(include={
                                    'application_id', 'reference', 'authority', 'address', 'postcode',
                                    'location', 'status', 'decision', 'submission_date', 'development_type',
                                    'description', 'opportunity_score', 'approval_probability'
                                })
                                summary_data['similarity_score'] = result.similarity_score
                                summary_data['similarity_type'] = "ai_semantic"
                                summary_data['similarity_factors'] = {
                                    "semantic_similarity": result.similarity_score,
                                    "development_type_match": similar_app.development_type == application.development_type,
                                    "authority_match": similar_app.authority == application.authority,
                                    "status_match": similar_app.status == application.status
                                }
                                detailed_similar.append(summary_data)

                else:
                    # Fall back to stored similar applications
                    logger.info("AI similarity not available, using stored similarities")
                    use_ai_similarity = False

            except Exception as ai_error:
                logger.warning(f"AI similarity search failed for {application_id}: {ai_error}")
                use_ai_similarity = False

        # Fallback to stored similar applications if AI not available or failed
        if not use_ai_similarity or not detailed_similar:
            similar_apps = application.similar_applications[:limit] if application.similar_applications else []

            for similar in similar_apps:
                similar_app = await search_service.get_application_by_id(similar.application_id)
                if similar_app:
                    summary_data = similar_app.dict(include={
                        'application_id', 'reference', 'authority', 'address', 'postcode',
                        'location', 'status', 'decision', 'submission_date', 'development_type',
                        'description', 'opportunity_score', 'approval_probability'
                    })
                    summary_data['similarity_score'] = similar.similarity_score
                    summary_data['similarity_type'] = similar.similarity_type
                    detailed_similar.append(summary_data)

        return {
            "base_application_id": application_id,
            "similar_applications": detailed_similar,
            "total_found": len(detailed_similar),
            "similarity_method": "ai_semantic" if use_ai_similarity and detailed_similar else "stored",
            "base_application_summary": {
                "development_type": application.development_type,
                "authority": application.authority,
                "status": application.status,
                "address": application.address
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get similar applications: {str(e)}"
        )


@router.get("/applications/{application_id}/history")
async def get_application_history(
    application_id: str = Path(..., description="Planning application ID"),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user),
    _: None = Depends(log_api_request)
):
    """
    Get planning history for the application site

    Returns historical planning applications for the same address or nearby locations.
    """
    try:
        application = await search_service.get_application_by_id(application_id)

        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application {application_id} not found"
            )

        return {
            "application_id": application_id,
            "address": application.address,
            "planning_history": application.planning_history or [],
            "total_historical_applications": len(application.planning_history) if application.planning_history else 0
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get application history: {str(e)}"
        )


@router.get("/applications/{application_id}/documents")
async def get_application_documents(
    application_id: str = Path(..., description="Planning application ID"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user),
    _: None = Depends(log_api_request)
):
    """
    Get documents for a planning application

    Returns list of all documents associated with the application.
    """
    try:
        application = await search_service.get_application_by_id(application_id)

        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application {application_id} not found"
            )

        documents = application.documents or []

        # Filter by document type if specified
        if document_type:
            documents = [doc for doc in documents if doc.type.lower() == document_type.lower()]

        return {
            "application_id": application_id,
            "documents": [doc.dict() for doc in documents],
            "total_documents": len(documents)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get application documents: {str(e)}"
        )


@router.get("/applications/{application_id}/consultations")
async def get_application_consultations(
    application_id: str = Path(..., description="Planning application ID"),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user),
    _: None = Depends(log_api_request)
):
    """
    Get consultation responses for a planning application

    Returns all consultation responses from statutory consultees and public comments.
    """
    try:
        application = await search_service.get_application_by_id(application_id)

        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application {application_id} not found"
            )

        return {
            "application_id": application_id,
            "consultations": [consultation.dict() for consultation in application.consultations] if application.consultations else [],
            "public_comments": application.public_comments.dict() if application.public_comments else None,
            "total_consultations": len(application.consultations) if application.consultations else 0
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get consultation responses: {str(e)}"
        )


# ============================================================================
# Content Discovery - Applications List Endpoint
# ============================================================================

@router.get("/applications/authority/{slug}", response_model=ApplicationListResponse)
async def get_authority_applications(
    slug: str = Path(..., description="Authority URL slug (e.g., 'poole')"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    status: Optional[str] = Query(None, description="Filter by status (approved, pending, rejected, withdrawn)"),
    sector: Optional[str] = Query(None, description="Filter by sector/use class"),
    date_from: Optional[str] = Query("now-12M/M", description="Start date (ES date math)"),
    date_to: Optional[str] = Query("now/M", description="End date (ES date math)"),
    sort_by: Optional[str] = Query("date", description="Sort field (date, score, decision_time)"),
    sort_order: Optional[str] = Query("desc", description="Sort direction (desc, asc)"),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user),
    _: None = Depends(log_api_request)
):
    """
    Get paginated list of applications for a specific planning authority

    **Performance target:** < 200ms

    **Example:** `/applications/authority/poole?page=1&page_size=20&status=pending`

    **Query Parameters:**
    - **slug**: Authority URL slug (e.g., "poole", "manchester")
    - **page**: Page number (1-indexed)
    - **page_size**: Results per page (max 100)
    - **status**: Filter by status (approved, pending, rejected, withdrawn)
    - **sector**: Filter by sector/application type
    - **date_from**: Start date using ES date math (default: "now-12M/M")
    - **date_to**: End date using ES date math (default: "now/M")
    - **sort_by**: Sort field - "date", "score", or "decision_time"
    - **sort_order**: Sort direction - "desc" or "asc"

    **Response:**
    Returns paginated applications list with:
    - Application reference and ID
    - Address and postcode
    - Status and type
    - Start and decision dates
    - Decision days
    - AI opportunity score (if available)
    - Description
    """
    try:
        # Convert slug to authority name (e.g., "poole" -> "Poole")
        authority_name = slug.replace("-", " ").title()

        logger.info(f"Fetching applications for authority: {authority_name} (slug: {slug})")

        # Build ES query filters
        filters = [
            {"term": {"area_name.keyword": authority_name}}
        ]

        # Add date range filter
        if date_from or date_to:
            date_filter = {"range": {"start_date": {}}}
            if date_from:
                date_filter["range"]["start_date"]["gte"] = date_from
            if date_to:
                date_filter["range"]["start_date"]["lte"] = date_to
            filters.append(date_filter)

        # Add status filter
        if status:
            status_map = {
                "approved": ["Permitted", "Conditions"],
                "pending": ["Undecided", "Unresolved", "Referred"],
                "rejected": ["Rejected"],
                "withdrawn": ["Withdrawn"]
            }
            status_values = status_map.get(status.lower(), [status])
            filters.append({"terms": {"app_state.keyword": status_values}})

        # Add sector filter (using app_type as sector proxy)
        if sector:
            filters.append({"term": {"app_type.keyword": sector}})

        # Map sort_by to ES field
        sort_field_map = {
            "date": "start_date",
            "score": "opportunity_score",
            "decision_time": "decision_days"
        }
        sort_field = sort_field_map.get(sort_by, "start_date")

        # Build ES query
        query = {
            "query": {
                "bool": {
                    "filter": filters
                }
            },
            "sort": [
                {sort_field: {"order": sort_order, "missing": "_last"}}
            ],
            "from": (page - 1) * page_size,
            "size": page_size,
            "_source": [
                "uid", "reference", "address", "postcode", "app_state", "app_type",
                "start_date", "decided_date", "decision_days", "description",
                "opportunity_score"
            ]
        }

        # Execute ES query
        logger.info(f"Executing ES query with {len(filters)} filters, sort: {sort_field} {sort_order}")
        es_response = await es_client.search(
            index="planning_applications",
            query=query["query"],
            size=page_size,
            from_=(page - 1) * page_size,
            sort=query["sort"],
            source=query["_source"]
        )

        # Parse ES response
        total = es_response.get("hits", {}).get("total", {}).get("value", 0)
        hits = es_response.get("hits", {}).get("hits", [])

        logger.info(f"ES returned {total} total results, {len(hits)} in this page")

        # Convert hits to ApplicationPreview models
        applications = []
        for hit in hits:
            source = hit.get("_source", {})

            # Parse dates
            start_date = None
            decided_date = None
            if source.get("start_date"):
                try:
                    start_date = datetime.fromisoformat(source["start_date"].replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    pass

            if source.get("decided_date"):
                try:
                    decided_date = datetime.fromisoformat(source["decided_date"].replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    pass

            app_preview = ApplicationPreview(
                application_id=source.get("uid", hit.get("_id")),
                reference=source.get("reference", ""),
                address=source.get("address", ""),
                postcode=source.get("postcode"),
                status=source.get("app_state", "Unknown"),
                app_type=source.get("app_type"),
                start_date=start_date,
                decided_date=decided_date,
                decision_days=source.get("decision_days"),
                opportunity_score=source.get("opportunity_score"),
                description=source.get("description")
            )
            applications.append(app_preview)

        # Build response
        response = ApplicationListResponse(
            success=True,
            data=ApplicationListData(
                total=total,
                page=page,
                page_size=page_size,
                applications=applications
            )
        )

        logger.info(f"Returning {len(applications)} applications for {authority_name}")
        return response

    except Exception as e:
        logger.error(f"Failed to fetch applications for authority {slug}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch applications: {str(e)}"
        )