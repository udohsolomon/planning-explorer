"""
Statistics API endpoints for Content Discovery pages
Phase 1 Week 2-3 - Backend Implementation with Pydantic Models

Master Orchestrator: content-discovery-implementation-plan.md
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
import logging

from app.services.elasticsearch_stats import (
    get_authority_stats_cached,
    get_location_stats_cached,
    get_platform_overview_stats_cached
)
from app.models.stats_responses import (
    AuthorityStatsResponse,
    LocationStatsResponse,
    StatsHealthResponse
)
from app.utils.slug_lookup import (
    authority_slug_to_name,
    location_slug_to_name,
    validate_authority_slug
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stats", tags=["statistics"])


@router.get("/overview")
async def get_platform_overview_stats():
    """
    Get platform-wide planning statistics overview for homepage stats bar

    **Performance target:** < 200ms (cached)

    **Cache TTL:** 1 hour

    **Returns:**
    - Total applications count
    - Total decisions count
    - Total granted permissions
    - Total housing units (estimated)
    - Granted percentage
    - Year-over-year comparisons (Oct 2023 - Sept 2024 vs Oct 2022 - Sept 2023)

    **Example:** `/stats/overview`
    """
    try:
        logger.info("Fetching platform overview statistics")

        # Get cached stats
        stats = await get_platform_overview_stats_cached()

        return {
            "success": True,
            "message": "Statistics retrieved successfully",
            "data": stats
        }

    except Exception as e:
        logger.error(f"Failed to fetch overview statistics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch statistics: {str(e)}"
        )


@router.get("/authority/{slug}", response_model=AuthorityStatsResponse)
async def get_authority_stats_endpoint(
    slug: str,
    force_refresh: bool = Query(False, description="Skip cache and fetch fresh data"),
    date_from: str = Query("now-12M/M", description="Start date (ES date math)"),
    date_to: str = Query("now/M", description="End date (ES date math)")
):
    """
    Get authority statistics for Content Discovery pages

    **Performance target:** < 100ms (cached), < 150ms (ES query)

    **Cache TTL:** 1 hour

    **Example:** `/stats/authority/poole`

    **Response includes:**
    - Total applications (12 months, all-time)
    - Approval rate
    - Average decision days
    - Active applications
    - Top 3 sectors
    - Status breakdown
    - Monthly trend (12 months)

    **Phase 1 Week 2-3 Deliverable**
    """
    try:
        # Validate slug
        is_valid, error_msg = validate_authority_slug(slug)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        # Convert slug to authority name using registry
        authority_name = authority_slug_to_name(slug)
        if not authority_name:
            raise HTTPException(
                status_code=404,
                detail=f"Authority not found: {slug}"
            )

        # Fetch stats from ES
        stats = await get_authority_stats_cached(
            authority_name=authority_name,
            date_from=date_from,
            date_to=date_to,
            force_refresh=force_refresh
        )

        # Add slug and timestamp
        stats["authority_slug"] = slug
        stats["last_updated"] = datetime.utcnow()

        return stats

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch authority statistics: {str(e)}"
        )


@router.get("/location/{slug}")
async def get_location_stats_endpoint(
    slug: str,
    force_refresh: bool = Query(False, description="Skip cache and fetch fresh data"),
    date_from: str = Query("now-12M/M", description="Start date (ES date math)"),
    date_to: str = Query("now/M", description="End date (ES date math)")
):
    """
    Get location statistics for Content Discovery pages

    **Performance target:** < 200ms (cached), < 180ms (ES query)

    **Cache TTL:** 1 hour

    **Example:** `/stats/location/manchester`

    **Note:** Requires location boundary data (GeoJSON polygons)

    **Response includes:**
    - Total applications (this year, all-time)
    - Approval rate
    - Average decision days
    - Top 3 sectors
    - Authority coverage (if multi-authority)
    - Monthly trend
    - Sector distribution
    - Heatmap data (geohash grid)
    """
    try:
        # TODO: Lookup location boundary from location registry
        # For MVP, return error until boundary data is available
        raise HTTPException(
            status_code=501,
            detail="Location statistics require boundary data. Location registry not yet implemented. "
                   "See backend/app/services/elasticsearch_stats.py for implementation guidance."
        )

        # Future implementation:
        # from app.services.location_registry import get_location_by_slug
        # location = await get_location_by_slug(slug)
        #
        # stats = await get_location_stats_cached(
        #     location_slug=slug,
        #     boundary_geojson=location['boundary'],
        #     centroid=location['centroid'],
        #     date_from=date_from,
        #     date_to=date_to,
        #     force_refresh=force_refresh
        # )
        #
        # return {
        #     "success": True,
        #     "data": stats,
        #     "cached": not force_refresh
        # }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch location statistics: {str(e)}"
        )


@router.get("/health", response_model=StatsHealthResponse)
async def stats_health_check():
    """
    Health check endpoint for statistics service
    """
    from app.services.elasticsearch_stats import stats_cache

    return {
        "status": "healthy",
        "cache_size": len(stats_cache),
        "cache_maxsize": stats_cache.maxsize,
        "cache_ttl": stats_cache.ttl
    }
