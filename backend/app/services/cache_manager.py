"""
Intelligent Caching Manager for Planning Explorer AI Services

Provides sophisticated caching strategies for AI processing results,
search results, and frequently accessed data with cache invalidation,
performance monitoring, and adaptive cache sizing.
"""

import asyncio
import logging
import time
import json
import hashlib
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import pickle
import gzip
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class CacheLevel(str, Enum):
    """Cache priority levels"""
    CRITICAL = "critical"      # Never evict unless expired
    HIGH = "high"             # Evict only under memory pressure
    NORMAL = "normal"         # Standard eviction policy
    LOW = "low"              # Evict first under memory pressure


class CacheType(str, Enum):
    """Types of cached data"""
    AI_PROCESSING = "ai_processing"
    SEARCH_RESULTS = "search_results"
    APPLICATION_DATA = "application_data"
    EMBEDDINGS = "embeddings"
    MARKET_INSIGHTS = "market_insights"
    USER_SESSIONS = "user_sessions"


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    cache_type: CacheType
    level: CacheLevel
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    size_bytes: int = 0
    compression_enabled: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CacheStats:
    """Cache performance statistics"""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    evictions: int = 0
    total_size_bytes: int = 0
    average_access_time_ms: float = 0.0
    compression_ratio: float = 0.0


class CacheManager:
    """
    Intelligent cache manager with adaptive strategies for AI services
    """

    def __init__(
        self,
        max_memory_mb: int = 1024,
        default_ttl_hours: int = 24,
        compression_threshold_kb: int = 100,
        cleanup_interval_minutes: int = 30
    ):
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.default_ttl = timedelta(hours=default_ttl_hours)
        self.compression_threshold_bytes = compression_threshold_kb * 1024
        self.cleanup_interval = timedelta(minutes=cleanup_interval_minutes)

        # Cache storage
        self.cache: Dict[str, CacheEntry] = {}
        self.cache_by_type: Dict[CacheType, List[str]] = {
            cache_type: [] for cache_type in CacheType
        }

        # Statistics
        self.stats = CacheStats()

        # Performance monitoring
        self.executor = ThreadPoolExecutor(max_workers=2)
        self._cleanup_task: Optional[asyncio.Task] = None
        self._last_cleanup = datetime.utcnow()

        # Cache configuration by type
        self.type_config = {
            CacheType.AI_PROCESSING: {
                "default_ttl_hours": 24,
                "max_size_mb": 400,
                "compression": True,
                "level": CacheLevel.HIGH
            },
            CacheType.SEARCH_RESULTS: {
                "default_ttl_hours": 6,
                "max_size_mb": 200,
                "compression": False,
                "level": CacheLevel.NORMAL
            },
            CacheType.APPLICATION_DATA: {
                "default_ttl_hours": 12,
                "max_size_mb": 300,
                "compression": True,
                "level": CacheLevel.HIGH
            },
            CacheType.EMBEDDINGS: {
                "default_ttl_hours": 72,
                "max_size_mb": 200,
                "compression": True,
                "level": CacheLevel.CRITICAL
            },
            CacheType.MARKET_INSIGHTS: {
                "default_ttl_hours": 48,
                "max_size_mb": 100,
                "compression": True,
                "level": CacheLevel.NORMAL
            },
            CacheType.USER_SESSIONS: {
                "default_ttl_hours": 1,
                "max_size_mb": 50,
                "compression": False,
                "level": CacheLevel.LOW
            }
        }

    async def start(self):
        """Start cache manager and background tasks"""
        if not self._cleanup_task:
            self._cleanup_task = asyncio.create_task(self._background_cleanup())
            logger.info("Cache manager started")

    async def stop(self):
        """Stop cache manager and cleanup"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None

        self.executor.shutdown(wait=False)
        logger.info("Cache manager stopped")

    async def get(
        self,
        key: str,
        cache_type: CacheType = CacheType.APPLICATION_DATA
    ) -> Optional[Any]:
        """
        Get cached value by key

        Args:
            key: Cache key
            cache_type: Type of cached data

        Returns:
            Cached value or None if not found/expired
        """
        start_time = time.time()

        try:
            self.stats.total_requests += 1

            cache_key = self._build_cache_key(key, cache_type)
            entry = self.cache.get(cache_key)

            if not entry:
                self.stats.cache_misses += 1
                return None

            # Check expiration
            if entry.expires_at and datetime.utcnow() > entry.expires_at:
                await self._remove_entry(cache_key)
                self.stats.cache_misses += 1
                return None

            # Update access statistics
            entry.access_count += 1
            entry.last_accessed = datetime.utcnow()
            self.stats.cache_hits += 1

            # Decompress if needed
            value = entry.value
            if entry.compression_enabled:
                value = await self._decompress_value(value)

            return value

        finally:
            # Update access time statistics
            access_time = (time.time() - start_time) * 1000
            self._update_access_time(access_time)

    async def set(
        self,
        key: str,
        value: Any,
        cache_type: CacheType = CacheType.APPLICATION_DATA,
        ttl_hours: Optional[int] = None,
        level: Optional[CacheLevel] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Set cached value

        Args:
            key: Cache key
            value: Value to cache
            cache_type: Type of cached data
            ttl_hours: Time to live in hours (use default if None)
            level: Cache priority level
            metadata: Additional metadata

        Returns:
            True if cached successfully
        """
        try:
            cache_key = self._build_cache_key(key, cache_type)
            config = self.type_config.get(cache_type, {})

            # Determine TTL and level
            if ttl_hours is None:
                ttl_hours = config.get("default_ttl_hours", 24)
            if level is None:
                level = config.get("level", CacheLevel.NORMAL)

            expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)

            # Serialize and optionally compress value
            serialized_value = value
            compression_enabled = False
            size_bytes = 0

            if config.get("compression", False):
                serialized_size = len(pickle.dumps(value))
                if serialized_size > self.compression_threshold_bytes:
                    serialized_value = await self._compress_value(value)
                    compression_enabled = True
                    size_bytes = len(serialized_value)
                else:
                    size_bytes = serialized_size

            # Create cache entry
            entry = CacheEntry(
                key=cache_key,
                value=serialized_value,
                cache_type=cache_type,
                level=level,
                created_at=datetime.utcnow(),
                expires_at=expires_at,
                size_bytes=size_bytes,
                compression_enabled=compression_enabled,
                metadata=metadata or {}
            )

            # Check memory limits
            if not await self._ensure_memory_available(entry.size_bytes):
                logger.warning(f"Failed to cache {cache_key}: insufficient memory")
                return False

            # Remove existing entry if present
            if cache_key in self.cache:
                await self._remove_entry(cache_key)

            # Add new entry
            self.cache[cache_key] = entry
            self.cache_by_type[cache_type].append(cache_key)
            self.stats.total_size_bytes += entry.size_bytes

            logger.debug(f"Cached {cache_key} ({size_bytes} bytes, TTL: {ttl_hours}h)")
            return True

        except Exception as e:
            logger.error(f"Failed to cache {key}: {str(e)}")
            return False

    async def delete(self, key: str, cache_type: CacheType = CacheType.APPLICATION_DATA) -> bool:
        """Delete cached value"""
        try:
            cache_key = self._build_cache_key(key, cache_type)
            if cache_key in self.cache:
                await self._remove_entry(cache_key)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete cache key {key}: {str(e)}")
            return False

    async def invalidate_by_type(self, cache_type: CacheType) -> int:
        """Invalidate all entries of a specific type"""
        try:
            keys_to_remove = self.cache_by_type[cache_type].copy()
            removed_count = 0

            for cache_key in keys_to_remove:
                if cache_key in self.cache:
                    await self._remove_entry(cache_key)
                    removed_count += 1

            logger.info(f"Invalidated {removed_count} entries of type {cache_type.value}")
            return removed_count

        except Exception as e:
            logger.error(f"Failed to invalidate cache type {cache_type.value}: {str(e)}")
            return 0

    async def invalidate_by_pattern(self, pattern: str, cache_type: Optional[CacheType] = None) -> int:
        """Invalidate entries matching a pattern"""
        try:
            keys_to_check = []
            if cache_type:
                keys_to_check = self.cache_by_type[cache_type].copy()
            else:
                keys_to_check = list(self.cache.keys())

            removed_count = 0
            for cache_key in keys_to_check:
                if pattern in cache_key:
                    await self._remove_entry(cache_key)
                    removed_count += 1

            logger.info(f"Invalidated {removed_count} entries matching pattern '{pattern}'")
            return removed_count

        except Exception as e:
            logger.error(f"Failed to invalidate pattern {pattern}: {str(e)}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        hit_rate = 0.0
        if self.stats.total_requests > 0:
            hit_rate = self.stats.cache_hits / self.stats.total_requests

        memory_usage_mb = self.stats.total_size_bytes / (1024 * 1024)
        memory_usage_percent = (self.stats.total_size_bytes / self.max_memory_bytes) * 100

        type_stats = {}
        for cache_type in CacheType:
            type_entries = len(self.cache_by_type[cache_type])
            type_size = sum(
                self.cache[key].size_bytes
                for key in self.cache_by_type[cache_type]
                if key in self.cache
            )
            type_stats[cache_type.value] = {
                "entries": type_entries,
                "size_mb": type_size / (1024 * 1024),
                "size_percent": (type_size / max(1, self.stats.total_size_bytes)) * 100
            }

        return {
            "performance": {
                "total_requests": self.stats.total_requests,
                "cache_hits": self.stats.cache_hits,
                "cache_misses": self.stats.cache_misses,
                "hit_rate": hit_rate,
                "average_access_time_ms": self.stats.average_access_time_ms
            },
            "memory": {
                "total_entries": len(self.cache),
                "total_size_mb": memory_usage_mb,
                "max_size_mb": self.max_memory_bytes / (1024 * 1024),
                "usage_percent": memory_usage_percent,
                "evictions": self.stats.evictions
            },
            "by_type": type_stats,
            "compression": {
                "compression_ratio": self.stats.compression_ratio,
                "threshold_kb": self.compression_threshold_bytes / 1024
            }
        }

    async def clear_all(self) -> int:
        """Clear all cache entries"""
        try:
            count = len(self.cache)
            self.cache.clear()
            for cache_type in CacheType:
                self.cache_by_type[cache_type].clear()

            self.stats.total_size_bytes = 0
            logger.info(f"Cleared all cache entries ({count} items)")
            return count

        except Exception as e:
            logger.error(f"Failed to clear cache: {str(e)}")
            return 0

    # Private methods

    def _build_cache_key(self, key: str, cache_type: CacheType) -> str:
        """Build cache key with type prefix"""
        return f"{cache_type.value}:{key}"

    async def _remove_entry(self, cache_key: str) -> None:
        """Remove entry from cache"""
        entry = self.cache.get(cache_key)
        if entry:
            self.stats.total_size_bytes -= entry.size_bytes
            self.cache_by_type[entry.cache_type].remove(cache_key)
            del self.cache[cache_key]

    async def _ensure_memory_available(self, required_bytes: int) -> bool:
        """Ensure sufficient memory is available"""
        if self.stats.total_size_bytes + required_bytes <= self.max_memory_bytes:
            return True

        # Need to evict entries
        bytes_to_free = (self.stats.total_size_bytes + required_bytes) - self.max_memory_bytes
        return await self._evict_entries(bytes_to_free)

    async def _evict_entries(self, bytes_to_free: int) -> bool:
        """Evict cache entries to free memory"""
        try:
            # Get candidates for eviction (exclude CRITICAL level)
            candidates = [
                (key, entry) for key, entry in self.cache.items()
                if entry.level != CacheLevel.CRITICAL
            ]

            # Sort by priority: LOW first, then by access patterns
            candidates.sort(key=lambda x: (
                x[1].level.value,  # Level priority
                x[1].access_count,  # Access frequency
                x[1].last_accessed  # Recency
            ))

            bytes_freed = 0
            entries_evicted = 0

            for cache_key, entry in candidates:
                if bytes_freed >= bytes_to_free:
                    break

                bytes_freed += entry.size_bytes
                await self._remove_entry(cache_key)
                entries_evicted += 1

            self.stats.evictions += entries_evicted

            if bytes_freed >= bytes_to_free:
                logger.info(f"Evicted {entries_evicted} entries, freed {bytes_freed} bytes")
                return True
            else:
                logger.warning(f"Could not free enough memory: freed {bytes_freed}, needed {bytes_to_free}")
                return False

        except Exception as e:
            logger.error(f"Error during cache eviction: {str(e)}")
            return False

    async def _compress_value(self, value: Any) -> bytes:
        """Compress value for storage"""
        def compress():
            serialized = pickle.dumps(value)
            return gzip.compress(serialized)

        return await asyncio.get_event_loop().run_in_executor(self.executor, compress)

    async def _decompress_value(self, compressed_value: bytes) -> Any:
        """Decompress value from storage"""
        def decompress():
            decompressed = gzip.decompress(compressed_value)
            return pickle.loads(decompressed)

        return await asyncio.get_event_loop().run_in_executor(self.executor, decompress)

    async def _background_cleanup(self):
        """Background task for cache cleanup"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval.total_seconds())

                # Remove expired entries
                expired_keys = []
                now = datetime.utcnow()

                for cache_key, entry in self.cache.items():
                    if entry.expires_at and now > entry.expires_at:
                        expired_keys.append(cache_key)

                for cache_key in expired_keys:
                    await self._remove_entry(cache_key)

                if expired_keys:
                    logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

                self._last_cleanup = now

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cache cleanup error: {str(e)}")

    def _update_access_time(self, access_time_ms: float):
        """Update average access time statistics"""
        if self.stats.total_requests == 1:
            self.stats.average_access_time_ms = access_time_ms
        else:
            # Rolling average
            alpha = 0.1  # Smoothing factor
            self.stats.average_access_time_ms = (
                alpha * access_time_ms + (1 - alpha) * self.stats.average_access_time_ms
            )


# Global cache manager instance
cache_manager = CacheManager()