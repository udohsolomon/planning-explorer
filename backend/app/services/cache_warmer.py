"""
Cache warming service for Content Discovery statistics
Preloads popular authority stats on application startup
"""
import asyncio
from app.services.elasticsearch_stats import get_authority_stats_cached
from app.data.uk_authorities import LONDON_BOROUGHS, GREATER_MANCHESTER

# Top 20 UK authorities by planning application volume
# Using data from uk_authorities.py for consistency
POPULAR_AUTHORITIES = [
    # Top London Boroughs
    "Westminster",
    "Camden",
    "Hackney",
    "Islington",
    "Lambeth",
    "Southwark",
    "Tower Hamlets",
    "Wandsworth",
    # Major Cities
    "Manchester",
    "Birmingham",
    "Leeds",
    "Liverpool",
    "Bristol",
    "Sheffield",
    "Newcastle upon Tyne",
    "Nottingham",
    "Leicester",
    "Edinburgh",
    "Glasgow",
    "Cardiff"
]


async def warm_cache_on_startup():
    """
    Pre-populate cache with popular authority stats

    This runs on application startup to ensure the most frequently
    accessed pages are immediately available from cache.

    Expected cache hit rate after warming: 95%+ for top authorities
    """
    print("🔥 Warming cache for popular authorities...")

    success_count = 0
    fail_count = 0

    for authority in POPULAR_AUTHORITIES:
        try:
            await get_authority_stats_cached(authority)
            success_count += 1
            print(f"✅ Cached: {authority}")
        except Exception as e:
            fail_count += 1
            print(f"❌ Failed to cache {authority}: {str(e)}")

    print(f"\n✅ Cache warming complete: {success_count}/{len(POPULAR_AUTHORITIES)} authorities cached")

    if fail_count > 0:
        print(f"⚠️  {fail_count} authorities failed to cache")


async def invalidate_stats_cache():
    """
    Clear all cached statistics

    Call this after daily data ingestion to ensure fresh data
    """
    from app.services.elasticsearch_stats import stats_cache

    cache_size_before = len(stats_cache)
    stats_cache.clear()

    print(f"✅ Cache invalidated: {cache_size_before} entries cleared")


async def get_cache_stats():
    """
    Get current cache statistics for monitoring

    Returns:
        dict: Cache metrics
    """
    from app.services.elasticsearch_stats import stats_cache

    return {
        "current_size": len(stats_cache),
        "max_size": stats_cache.maxsize,
        "ttl_seconds": stats_cache.ttl,
        "utilization": round(len(stats_cache) / stats_cache.maxsize * 100, 1)
    }
