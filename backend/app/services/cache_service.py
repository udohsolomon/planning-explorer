"""
Redis Cache Service for Enrichment Data

This module provides 24-hour TTL caching for applicant/agent enrichment data
to avoid redundant scraping of planning portals.
"""

import json
import logging
from typing import Optional, Dict
from datetime import timedelta

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("redis package not installed, caching disabled")

logger = logging.getLogger(__name__)


class CacheService:
    """
    Redis-based cache service for enrichment data with 24h TTL.

    Features:
    - 24-hour cache expiration (86400 seconds)
    - Automatic JSON serialization/deserialization
    - Graceful degradation if Redis unavailable
    - Application-scoped key namespacing
    """

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """
        Initialize cache service with Redis connection.

        Args:
            redis_url: Redis connection URL (default: localhost:6379/0)
        """
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.ttl_seconds = 86400  # 24 hours
        self.key_prefix = "planning_explorer:enrichment:"
        self.available = False

        logger.info(f"CacheService initialized (Redis URL: {redis_url})")

    async def connect(self):
        """
        Establish Redis connection.

        Should be called during application startup (in lifespan manager).
        """
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available, caching will be disabled")
            return

        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )

            # Test connection
            await self.redis_client.ping()
            self.available = True
            logger.info("✅ Redis connection established successfully")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            logger.warning("Continuing without cache - enrichment will be slower")
            self.available = False

    async def disconnect(self):
        """
        Close Redis connection.

        Should be called during application shutdown (in lifespan manager).
        """
        if self.redis_client:
            try:
                await self.redis_client.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {str(e)}")

    def _make_key(self, application_id: str) -> str:
        """
        Create namespaced cache key for application.

        Args:
            application_id: Planning application reference ID

        Returns:
            Full Redis key with namespace
        """
        return f"{self.key_prefix}{application_id}"

    async def get_enrichment(self, application_id: str) -> Optional[Dict]:
        """
        Retrieve cached enrichment data for application.

        Args:
            application_id: Planning application reference ID

        Returns:
            Dictionary with applicant_name and agent_name, or None if not cached
        """
        if not self.available or not self.redis_client:
            return None

        try:
            key = self._make_key(application_id)
            cached_data = await self.redis_client.get(key)

            if cached_data:
                logger.info(f"✅ Cache HIT for {application_id}")
                return json.loads(cached_data)
            else:
                logger.info(f"❌ Cache MISS for {application_id}")
                return None

        except Exception as e:
            logger.error(f"Cache retrieval error for {application_id}: {str(e)}")
            return None

    async def set_enrichment(
        self,
        application_id: str,
        enrichment_data: Dict,
        ttl_seconds: Optional[int] = None
    ) -> bool:
        """
        Cache enrichment data for application with TTL.

        Args:
            application_id: Planning application reference ID
            enrichment_data: Dictionary with applicant_name and agent_name
            ttl_seconds: Optional custom TTL (default: 24 hours)

        Returns:
            True if cached successfully, False otherwise
        """
        if not self.available or not self.redis_client:
            return False

        try:
            key = self._make_key(application_id)
            ttl = ttl_seconds or self.ttl_seconds

            # Serialize to JSON
            data_json = json.dumps(enrichment_data)

            # Store with TTL
            await self.redis_client.setex(
                key,
                ttl,
                data_json
            )

            logger.info(f"✅ Cached enrichment for {application_id} (TTL: {ttl}s)")
            return True

        except Exception as e:
            logger.error(f"Cache storage error for {application_id}: {str(e)}")
            return False

    async def invalidate_enrichment(self, application_id: str) -> bool:
        """
        Remove cached enrichment data for application.

        Args:
            application_id: Planning application reference ID

        Returns:
            True if deleted, False if not found or error
        """
        if not self.available or not self.redis_client:
            return False

        try:
            key = self._make_key(application_id)
            deleted = await self.redis_client.delete(key)

            if deleted:
                logger.info(f"✅ Invalidated cache for {application_id}")
                return True
            else:
                logger.info(f"❌ No cache to invalidate for {application_id}")
                return False

        except Exception as e:
            logger.error(f"Cache invalidation error for {application_id}: {str(e)}")
            return False

    async def get_ttl(self, application_id: str) -> Optional[int]:
        """
        Get remaining TTL for cached enrichment.

        Args:
            application_id: Planning application reference ID

        Returns:
            Remaining seconds until expiration, or None if not cached
        """
        if not self.available or not self.redis_client:
            return None

        try:
            key = self._make_key(application_id)
            ttl = await self.redis_client.ttl(key)

            if ttl > 0:
                return ttl
            else:
                return None

        except Exception as e:
            logger.error(f"TTL retrieval error for {application_id}: {str(e)}")
            return None

    async def health_check(self) -> Dict:
        """
        Check cache service health status.

        Returns:
            Dictionary with health information
        """
        if not REDIS_AVAILABLE:
            return {
                "status": "unavailable",
                "available": False,
                "message": "Redis package not installed"
            }

        if not self.available or not self.redis_client:
            return {
                "status": "disconnected",
                "available": False,
                "message": "Redis not connected"
            }

        try:
            # Ping Redis
            await self.redis_client.ping()

            # Get Redis info
            info = await self.redis_client.info("server")

            return {
                "status": "healthy",
                "available": True,
                "redis_version": info.get("redis_version", "unknown"),
                "uptime_seconds": info.get("uptime_in_seconds", 0)
            }

        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "error",
                "available": False,
                "message": str(e)
            }


# Global cache instance (initialized in main.py)
cache_service: Optional[CacheService] = None


def get_cache_service() -> Optional[CacheService]:
    """
    Get global cache service instance.

    Returns:
        CacheService instance or None if not initialized
    """
    return cache_service


async def init_cache_service(redis_url: str = "redis://localhost:6379/0"):
    """
    Initialize global cache service.

    Should be called during application startup.

    Args:
        redis_url: Redis connection URL
    """
    global cache_service
    cache_service = CacheService(redis_url)
    await cache_service.connect()


async def shutdown_cache_service():
    """
    Shutdown global cache service.

    Should be called during application shutdown.
    """
    global cache_service
    if cache_service:
        await cache_service.disconnect()
