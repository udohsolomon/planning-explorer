"""
pSEO API Endpoints
FastAPI routes for pSEO page generation, retrieval, and management
"""

from typing import Optional, Dict, List
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

from app.services.pseo.orchestrator import pSEOOrchestrator
from app.services.pseo.batch_processor import BatchProcessor
from app.db.elasticsearch import es_client

# Setup logging
logger = logging.getLogger(__name__)

# Create router (no prefix - will be added by api_router inclusion)
router = APIRouter(tags=["pSEO"])


# === PAGE RETRIEVAL ENDPOINTS ===


@router.get("/")
async def list_pseo_pages(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    
):
    """
    List all generated pSEO pages with pagination.

    Args:
        limit: Number of pages to return (max 500)
        offset: Offset for pagination

    Returns:
        List of pSEO pages with metadata
    """

    try:
        result = await es_client.client.search(
            index="pseo_pages",
            body={
                "query": {"match_all": {}},
                "size": limit,
                "from": offset,
                "_source": [
                    "authority_id", "authority_name", "url_slug",
                    "generated_at", "metadata"
                ],
                "sort": [{"generated_at": {"order": "desc"}}]
            }
        )

        pages = [hit['_source'] for hit in result['hits']['hits']]
        total = result['hits']['total']['value']

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": pages,
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total
            }
        )

    except Exception as e:
        logger.error(f"Error listing pSEO pages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === GENERATION ENDPOINTS ===

@router.post("/generate/{authority_id}")
async def generate_pseo_page(
    authority_id: str,
    force_scraper: Optional[str] = Query(None, regex="^(playwright|firecrawl)$"),
    background_tasks: BackgroundTasks = None,
    
):
    """
    Generate pSEO page for a specific authority.

    Args:
        authority_id: Authority ID to generate page for
        force_scraper: Force specific scraper ('playwright' or 'firecrawl')

    Returns:
        Generated page data or background task ID
    """

    try:
        # Get authority data from ES
        authority_result = await es_client.client.get(
            index="local_authorities",
            id=authority_id
        )

        authority = authority_result['_source']
        authority['id'] = authority_id

    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Authority not found: {authority_id}"
        )

    try:
        # Create orchestrator and generate page
        orchestrator = pSEOOrchestrator(es_client.client)

        logger.info(f"Starting pSEO generation for {authority.get('name')}")

        page = await orchestrator.generate_page(authority, force_scraper)

        if page.get('status') == 'failed':
            raise HTTPException(
                status_code=500,
                detail=f"Page generation failed: {page.get('error')}"
            )

        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "data": page,
                "message": f"Successfully generated pSEO page for {authority.get('name')}",
                "cost": page.get('metadata', {}).get('generation_cost', 0),
                "word_count": page.get('metadata', {}).get('total_words', 0)
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating pSEO page: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-generate")
async def batch_generate_pseo_pages(
    max_cost: Optional[float] = Query(None, ge=0),
    start_from: int = Query(0, ge=0),
    limit: Optional[int] = Query(None, ge=1, le=425),
    background_tasks: BackgroundTasks = None,
    
):
    """
    Batch generate pSEO pages for all or subset of authorities.

    Args:
        max_cost: Maximum total cost to spend (stops when reached)
        start_from: Resume from specific authority index
        limit: Limit number of authorities to process

    Returns:
        Batch processing summary or background task ID
    """

    try:
        processor = BatchProcessor(es_client.client)

        logger.info(
            f"Starting batch pSEO generation "
            f"(max_cost: {max_cost}, start_from: {start_from}, limit: {limit})"
        )

        # Run batch processing
        summary = await processor.process_all_authorities(
            max_cost=max_cost,
            start_from=start_from,
            limit=limit
        )

        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "data": summary,
                "message": "Batch processing completed",
                "statistics": summary.get('statistics', {}),
                "costs": summary.get('costs', {})
            }
        )

    except Exception as e:
        logger.error(f"Error in batch generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-generate/resume")
async def resume_batch_generation(
    
):
    """
    Resume batch processing from last checkpoint.

    Returns:
        Batch processing summary
    """

    try:
        processor = BatchProcessor(es_client.client)

        logger.info("Resuming batch pSEO generation from checkpoint")

        summary = await processor.resume_from_checkpoint()

        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "data": summary,
                "message": "Batch processing resumed and completed",
                "statistics": summary.get('statistics', {}),
                "costs": summary.get('costs', {})
            }
        )

    except Exception as e:
        logger.error(f"Error resuming batch generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === STATISTICS ENDPOINTS ===

@router.get("/stats")
async def get_generation_stats(
    
):
    """
    Get overall pSEO generation statistics.

    Returns:
        Aggregated statistics across all generated pages
    """

    try:
        # Aggregate statistics from all pages
        result = await es_client.client.search(
            index="pseo_pages",
            body={
                "size": 0,
                "aggs": {
                    "total_pages": {"value_count": {"field": "_id"}},
                    "total_cost": {"sum": {"field": "metadata.generation_cost"}},
                    "avg_cost": {"avg": {"field": "metadata.generation_cost"}},
                    "total_words": {"sum": {"field": "metadata.total_words"}},
                    "avg_words": {"avg": {"field": "metadata.total_words"}},
                    "scraper_breakdown": {
                        "terms": {"field": "metadata.scraper_used.keyword"}
                    },
                    "latest_generation": {
                        "max": {"field": "generated_at"}
                    }
                }
            }
        )

        aggs = result['aggregations']

        stats = {
            "total_pages": aggs['total_pages']['value'],
            "total_cost": round(aggs['total_cost']['value'], 2) if aggs['total_cost']['value'] else 0,
            "avg_cost_per_page": round(aggs['avg_cost']['value'], 4) if aggs['avg_cost']['value'] else 0,
            "total_words": int(aggs['total_words']['value']) if aggs['total_words']['value'] else 0,
            "avg_words_per_page": int(aggs['avg_words']['value']) if aggs['avg_words']['value'] else 0,
            "scraper_usage": {
                bucket['key']: bucket['doc_count']
                for bucket in aggs['scraper_breakdown']['buckets']
            },
            "latest_generation": aggs['latest_generation']['value_as_string']
        }

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": stats
            }
        )

    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/{authority_id}")
async def get_authority_generation_stats(
    authority_id: str,
    
):
    """
    Get generation statistics for specific authority.

    Args:
        authority_id: Authority ID

    Returns:
        Generation statistics for the authority
    """

    try:
        result = await es_client.client.get(
            index="pseo_pages",
            id=authority_id
        )

        page = result['_source']

        stats = {
            "authority_id": authority_id,
            "authority_name": page.get('authority_name'),
            "generated_at": page.get('generated_at'),
            "metadata": page.get('metadata', {}),
            "generation_log": page.get('generation_log', [])
        }

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": stats
            }
        )

    except Exception as e:
        logger.error(f"Error getting authority stats: {e}")
        raise HTTPException(status_code=404, detail=f"Page not found: {authority_id}")


# === CACHE MANAGEMENT ENDPOINTS ===

@router.delete("/cache/{authority_id}")
async def clear_authority_cache(
    authority_id: str,
    
):
    """
    Clear cached pSEO page for an authority.
    Forces regeneration on next request.

    Args:
        authority_id: Authority ID to clear cache for

    Returns:
        Success message
    """

    try:
        await es_client.client.delete(
            index="pseo_pages",
            id=authority_id
        )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"Cache cleared for authority: {authority_id}"
            }
        )

    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=404, detail=f"Page not found: {authority_id}")


@router.delete("/cache")
async def clear_all_cache(
    confirm: bool = Query(False),
    
):
    """
    Clear all cached pSEO pages.
    Requires confirmation parameter.

    Args:
        confirm: Must be true to proceed

    Returns:
        Success message with count
    """

    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Must set confirm=true to clear all cache"
        )

    try:
        # Delete all documents in index
        result = await es_client.client.delete_by_query(
            index="pseo_pages",
            body={"query": {"match_all": {}}}
        )

        deleted_count = result['deleted']

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"Cleared all pSEO cache ({deleted_count} pages deleted)"
            }
        )

    except Exception as e:
        logger.error(f"Error clearing all cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === HEALTH CHECK ===

@router.get("/health")
async def health_check(
    
):
    """
    Health check for pSEO system.

    Returns:
        System health status
    """

    try:
        # Check ES connection
        es_health = await es_client.client.cluster.health()

        # Check if pseo_pages index exists
        index_exists = await es_client.client.indices.exists(index="pseo_pages")

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "elasticsearch": {
                    "status": es_health['status'],
                    "cluster_name": es_health['cluster_name']
                },
                "pseo_index_exists": index_exists,
                "timestamp": datetime.now().isoformat()
            }
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")

@router.get("/{authority_slug}")
async def get_pseo_page(authority_slug: str):
    """
    Get generated pSEO page for an authority by slug.

    Args:
        authority_slug: URL slug for authority (e.g., 'birmingham')

    Returns:
        Complete pSEO page data with all sections
    """

    try:
        # Try to get document by ID (assuming authority_id is used as doc ID)
        # If that fails, search by url_slug
        try:
            result = await es_client.client.get(
                index="pseo_pages",
                id=authority_slug
            )
            page_data = result['_source']
        except:
            # Fallback: search by url_slug
            search_result = await es_client.client.search(
                index="pseo_pages",
                body={
                    "query": {
                        "bool": {
                            "should": [
                                {"term": {"url_slug": authority_slug}},
                                {"term": {"authority_id": authority_slug}}
                            ],
                            "minimum_should_match": 1
                        }
                    },
                    "size": 1
                }
            )

            if not search_result['hits']['hits']:
                raise HTTPException(
                    status_code=404,
                    detail=f"pSEO page not found for authority: {authority_slug}"
                )

            page_data = search_result['hits']['hits'][0]['_source']

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": page_data,
                "generated_at": page_data.get('generated_at'),
                "metadata": page_data.get('metadata', {})
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving pSEO page: {e}")
        raise HTTPException(status_code=500, detail=str(e))

        raise HTTPException(status_code=503, detail="pSEO system unhealthy")
