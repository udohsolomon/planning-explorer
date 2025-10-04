"""
Search endpoints for Planning Explorer API
"""
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
import logging
import traceback
import time

from app.services.search import search_service
from app.models.planning import (
    SearchRequest, SearchResponse, SearchFilters, PlanningApplication,
    PlanningApplicationResponse, PlanningApplicationSummary, ApplicationStatus,
    DevelopmentType, ApplicationType, DecisionType
)
from app.middleware.auth import get_optional_user, log_api_request

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/search", response_model=SearchResponse)
async def search_applications(
    search_request: SearchRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user),
    _: None = Depends(log_api_request)
):
    """
    Search planning applications with advanced filters

    - **query**: Text search across description, address, applicant, etc.
    - **filters**: Advanced filtering options
    - **sort_by**: Sort field (relevance, submission_date, opportunity_score, etc.)
    - **sort_order**: Sort order (asc/desc)
    - **page**: Page number for pagination
    - **page_size**: Number of results per page (max 100)
    - **include_ai_fields**: Include AI-generated insights
    """
    try:
        return await search_service.search_applications(search_request)
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Standard search failed: {str(e)}\nTraceback: {error_trace}")

        # Provide detailed error information
        error_detail = {
            "error": "SEARCH_ERROR",
            "message": "An error occurred while searching. Please try again.",
            "suggestion": "Try adjusting your search terms or filters."
        }

        # Add debug info in development
        try:
            from app.core.config import settings
            if settings.debug:
                error_detail["debug_info"] = {
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
        except:
            pass

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )


@router.post("/search/semantic")
async def semantic_search(
    query: str,
    k: int = Query(50, ge=1, le=100, description="Number of results to return"),
    filters: Optional[SearchFilters] = None,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user),
    _: None = Depends(log_api_request)
):
    """
    AI-powered semantic search using natural language

    Uses vector embeddings to find applications similar in meaning to your query.

    - **query**: Natural language search query
    - **k**: Number of results to return
    - **filters**: Optional filters to apply

    Returns APIResponse format compatible with frontend
    """
    start_time = time.time()
    request_id = f"semantic_search_{int(start_time * 1000)}"

    logger.info(f"[{request_id}] Starting semantic search - query: '{query}', k: {k}, user: {current_user.get('id') if current_user else 'anonymous'}")

    try:
        # Check AI processor availability
        try:
            from app.services.ai_processor import ai_processor
            if not ai_processor.embedding_service:
                logger.warning(f"[{request_id}] Embedding service not available, falling back to text search")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail={
                        "error": "SEMANTIC_SEARCH_UNAVAILABLE",
                        "message": "AI embedding service is not initialized. Semantic search is temporarily unavailable.",
                        "suggestion": "Try using regular text search instead."
                    }
                )
        except ImportError as import_error:
            logger.error(f"[{request_id}] AI processor import failed: {import_error}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "error": "AI_SERVICE_UNAVAILABLE",
                    "message": "AI processing services are not available.",
                    "suggestion": "Contact support if this issue persists."
                }
            )

        # Check Elasticsearch connectivity
        try:
            from app.db.elasticsearch import es_client
            if not await es_client.health_check():
                logger.error(f"[{request_id}] Elasticsearch health check failed")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail={
                        "error": "DATABASE_UNAVAILABLE",
                        "message": "Search database is currently unavailable.",
                        "suggestion": "Please try again in a few moments."
                    }
                )
        except Exception as es_error:
            logger.error(f"[{request_id}] Elasticsearch connection error: {es_error}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "error": "DATABASE_CONNECTION_ERROR",
                    "message": "Unable to connect to search database.",
                    "details": str(es_error)
                }
            )

        # Execute semantic search
        result = await search_service.semantic_search(
            query_text=query,
            filters=filters,
            k=k
        )

        processing_time = int((time.time() - start_time) * 1000)
        logger.info(f"[{request_id}] Semantic search completed successfully - {result.total} results in {processing_time}ms")

        # Return in APIResponse format expected by frontend
        return {
            "data": result.results,
            "message": f"Found {result.total} results for semantic search",
            "success": True,
            "meta": {
                "total": result.total,
                "page": result.page,
                "limit": result.page_size,
                "totalPages": result.total_pages
            }
        }

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        processing_time = int((time.time() - start_time) * 1000)
        error_trace = traceback.format_exc()
        logger.error(f"[{request_id}] Semantic search failed after {processing_time}ms: {str(e)}\nTraceback: {error_trace}")

        # Provide detailed error information
        error_detail = {
            "error": "SEMANTIC_SEARCH_ERROR",
            "message": "An error occurred while processing your semantic search request.",
            "request_id": request_id,
            "processing_time_ms": processing_time,
            "suggestion": "Try simplifying your search query or use regular text search."
        }

        # Add specific error details for debugging (in development)
        try:
            from app.core.config import settings
            if settings.debug:
                error_detail["debug_info"] = {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "query": query,
                    "k": k,
                    "filters": filters.dict() if filters else None
                }
        except:
            pass

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )


@router.post("/search/natural-language", response_model=SearchResponse)
async def natural_language_search(
    query: str,
    k: int = Query(50, ge=1, le=100, description="Number of results to return"),
    filters: Optional[SearchFilters] = None,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user),
    _: None = Depends(log_api_request)
):
    """
    AI-powered natural language search

    Process natural language queries and return relevant planning applications.

    Examples:
    - "Show me approved residential developments in London"
    - "Find commercial applications submitted this year"
    - "What extensions were approved near SW1A 1AA?"
    """
    try:
        from app.services.ai_processor import ai_processor

        # Get applications for processing (limit for performance)
        all_apps_response = await search_service.get_applications_list(
            filters=filters,
            page_size=min(k * 5, 200)  # Get more to process with NLP
        )

        # Process with AI
        nlp_result = await ai_processor.process_natural_language_query(
            query,
            [app for app in all_apps_response.results],  # Convert summaries to applications
            context={"user_id": current_user.get("id") if current_user else None}
        )

        # If semantic results available, use them
        if nlp_result.get("semantic_results") and nlp_result["semantic_results"]["total_results"] > 0:
            semantic_results = nlp_result["semantic_results"]["results"][:k]

            # Convert to PlanningApplicationSummary
            results = []
            for result in semantic_results:
                if hasattr(result, 'application_id'):
                    app = await search_service.get_application_by_id(result.application_id)
                    if app:
                        summary_data = app.dict(exclude={
                            'description_embedding', 'full_content_embedding',
                            'summary_embedding', 'location_embedding', 'document_embeddings'
                        })
                        summary_data['similarity_score'] = result.similarity_score
                        results.append(PlanningApplicationSummary(**summary_data))

            return SearchResponse(
                results=results,
                total=len(results),
                page=1,
                page_size=k,
                total_pages=1,
                took_ms=nlp_result.get("processing_time_ms", 100),
                query_metadata={
                    "original_query": query,
                    "processed_with_ai": True,
                    "query_intent": nlp_result.get("parsed_query", {}).get("intent"),
                    "suggestions": nlp_result.get("parsed_query", {}).get("suggestions", [])
                }
            )
        else:
            # Use Elasticsearch query from NLP processor
            es_query = nlp_result.get("elasticsearch_query")
            if es_query:
                search_request = SearchRequest(
                    query="",  # Query already processed
                    filters=filters,
                    page_size=k,
                    sort_by="relevance"
                )

                # Override the query building with AI-generated query
                response = await es_client.search(
                    query=es_query,
                    size=k,
                    source=search_service._get_source_fields(True)
                )

                # Process results
                results = []
                for hit in response.get("hits", {}).get("hits", []):
                    source = hit["_source"]
                    summary = PlanningApplicationSummary(**source)
                    results.append(summary)

                total = response.get("hits", {}).get("total", {})
                if isinstance(total, dict):
                    total_count = total.get("value", 0)
                else:
                    total_count = total

                return SearchResponse(
                    results=results,
                    total=total_count,
                    page=1,
                    page_size=k,
                    total_pages=(total_count + k - 1) // k if total_count > 0 else 0,
                    took_ms=nlp_result.get("processing_time_ms", 100),
                    query_metadata={
                        "original_query": query,
                        "processed_with_ai": True,
                        "query_intent": nlp_result.get("parsed_query", {}).get("intent"),
                        "suggestions": nlp_result.get("parsed_query", {}).get("suggestions", [])
                    }
                )
            else:
                # Fallback to regular search
                search_request = SearchRequest(
                    query=query,
                    filters=filters,
                    page_size=k
                )
                return await search_service.search_applications(search_request)

    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Natural language search failed: {str(e)}\nTraceback: {error_trace}")

        # Provide detailed error information
        error_detail = {
            "error": "NATURAL_LANGUAGE_SEARCH_ERROR",
            "message": "An error occurred while processing your natural language search.",
            "suggestion": "Try using simpler language or standard text search."
        }

        # Add debug info in development
        try:
            from app.core.config import settings
            if settings.debug:
                error_detail["debug_info"] = {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "query": query
                }
        except:
            pass

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )


@router.get("/search/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=2, description="Search query for suggestions"),
    limit: int = Query(10, ge=1, le=20, description="Maximum number of suggestions"),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Get AI-enhanced search suggestions and auto-complete

    Returns intelligent suggestions using AI to understand context and intent.
    """
    try:
        from app.services.ai_processor import ai_processor

        # Try to get AI-enhanced suggestions
        suggestions = {
            "queries": [],
            "addresses": [],
            "authorities": [],
            "development_types": [],
            "smart_suggestions": []
        }

        # Basic suggestions (always available)
        basic_queries = [
            f"{q} extension",
            f"{q} new build",
            f"{q} residential",
            f"{q} commercial",
            f"{q} approved",
            f"{q} planning permission"
        ]

        # If NLP processor available, get enhanced suggestions
        if ai_processor.nlp_processor:
            try:
                # Process query for intent and generate contextual suggestions
                parsed = await ai_processor.nlp_processor.process_query(
                    q, context={"suggestion_mode": True}
                )

                suggestions["smart_suggestions"] = parsed.suggestions[:limit//2]
                suggestions["queries"] = basic_queries[:limit - len(suggestions["smart_suggestions"])]
            except Exception as e:
                logger.warning(f"AI suggestions failed, using basic: {e}")
                suggestions["queries"] = basic_queries[:limit]
        else:
            suggestions["queries"] = basic_queries[:limit]

        # Get authority suggestions from Elasticsearch
        try:
            agg_response = await es_client.aggregations({
                "authority_suggestions": {
                    "terms": {
                        "field": "authority",
                        "include": f".*{q.lower()}.*",
                        "size": 5
                    }
                }
            })

            if agg_response and "authority_suggestions" in agg_response:
                suggestions["authorities"] = [
                    bucket["key"] for bucket in
                    agg_response["authority_suggestions"].get("buckets", [])
                ]

            # Get development type suggestions
            dev_type_agg = await es_client.aggregations({
                "dev_type_suggestions": {
                    "terms": {
                        "field": "development_type",
                        "include": f".*{q.lower()}.*",
                        "size": 5
                    }
                }
            })

            if dev_type_agg and "dev_type_suggestions" in dev_type_agg:
                suggestions["development_types"] = [
                    bucket["key"] for bucket in
                    dev_type_agg["dev_type_suggestions"].get("buckets", [])
                ]

        except Exception as e:
            logger.warning(f"Elasticsearch suggestions failed: {e}")

        return suggestions

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get suggestions: {str(e)}"
        )


@router.get("/aggregations")
async def get_aggregations(
    authorities: Optional[str] = Query(None, description="Comma-separated list of authorities"),
    statuses: Optional[str] = Query(None, description="Comma-separated list of statuses"),
    development_types: Optional[str] = Query(None, description="Comma-separated list of development types"),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user),
    _: None = Depends(log_api_request)
):
    """
    Get market intelligence aggregations

    Returns statistical breakdowns and trends across planning data.

    - **authorities**: Filter by specific authorities
    - **statuses**: Filter by application statuses
    - **development_types**: Filter by development types
    """
    try:
        # Build filters from query parameters
        filters = SearchFilters()

        if authorities:
            filters.authorities = [auth.strip() for auth in authorities.split(",")]

        if statuses:
            try:
                filters.statuses = [ApplicationStatus(status.strip()) for status in statuses.split(",")]
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status value: {str(e)}"
                )

        if development_types:
            try:
                filters.development_types = [DevelopmentType(dt.strip()) for dt in development_types.split(",")]
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid development type: {str(e)}"
                )

        return await search_service.get_aggregations(filters)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get aggregations: {str(e)}"
        )