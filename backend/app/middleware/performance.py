"""
Performance optimization middleware for Planning Explorer API
"""
import gzip
import asyncio
from typing import Callable, Dict, Any, Optional
from datetime import datetime, timedelta

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
from starlette.types import Message

from app.core.config import settings


class CompressionMiddleware(BaseHTTPMiddleware):
    """Middleware for response compression"""

    def __init__(self, app: FastAPI, minimum_size: int = 1024):
        super().__init__(app)
        self.minimum_size = minimum_size

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Apply compression to responses if appropriate

        Args:
            request: HTTP request
            call_next: Next middleware/endpoint

        Returns:
            Potentially compressed HTTP response
        """
        response = await call_next(request)

        # Check if client accepts gzip compression
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" not in accept_encoding.lower():
            return response

        # Skip compression for certain content types
        content_type = response.headers.get("content-type", "")
        skip_types = [
            "image/",
            "video/",
            "audio/",
            "application/zip",
            "application/gzip",
            "application/pdf"
        ]

        if any(content_type.startswith(skip_type) for skip_type in skip_types):
            return response

        # Skip compression for small responses
        if hasattr(response, "body") and len(response.body) < self.minimum_size:
            return response

        # Compress response body
        if hasattr(response, "body"):
            compressed_body = gzip.compress(response.body)

            # Only use compression if it actually reduces size
            if len(compressed_body) < len(response.body):
                response.headers["content-encoding"] = "gzip"
                response.headers["content-length"] = str(len(compressed_body))
                response.body = compressed_body

        return response


class CacheMiddleware(BaseHTTPMiddleware):
    """Simple in-memory cache middleware"""

    def __init__(self, app: FastAPI, default_ttl: int = 300):
        super().__init__(app)
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        self.lock = asyncio.Lock()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Cache GET requests when appropriate

        Args:
            request: HTTP request
            call_next: Next middleware/endpoint

        Returns:
            Cached or fresh HTTP response
        """
        # Only cache GET requests
        if request.method != "GET":
            return await call_next(request)

        # Skip caching for certain paths
        skip_paths = [
            "/api/auth",
            "/api/user",
            "/docs",
            "/redoc"
        ]

        if any(request.url.path.startswith(path) for path in skip_paths):
            return await call_next(request)

        # Generate cache key
        cache_key = self._generate_cache_key(request)

        # Check cache
        async with self.lock:
            cached_response = await self._get_cached_response(cache_key)

        if cached_response:
            # Return cached response
            response = Response(
                content=cached_response["body"],
                status_code=cached_response["status_code"],
                headers=cached_response["headers"]
            )
            response.headers["X-Cache"] = "HIT"
            return response

        # Get fresh response
        response = await call_next(request)

        # Cache successful responses
        if response.status_code == 200 and hasattr(response, "body"):
            async with self.lock:
                await self._cache_response(cache_key, response)

        response.headers["X-Cache"] = "MISS"
        return response

    def _generate_cache_key(self, request: Request) -> str:
        """Generate cache key from request"""
        # Include path and query parameters
        key_parts = [
            request.url.path,
            str(sorted(request.query_params.items()))
        ]

        # Include user ID if authenticated (for user-specific caching)
        auth_header = request.headers.get("authorization")
        if auth_header:
            # This would extract user ID from JWT in production
            key_parts.append("authenticated")

        return "|".join(key_parts)

    async def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get response from cache if not expired"""
        if cache_key not in self.cache:
            return None

        cached_item = self.cache[cache_key]

        # Check if expired
        if datetime.utcnow() > cached_item["expires_at"]:
            del self.cache[cache_key]
            return None

        return cached_item

    async def _cache_response(self, cache_key: str, response: Response):
        """Cache response with TTL"""
        if not hasattr(response, "body"):
            return

        # Determine TTL based on endpoint
        ttl = self.default_ttl

        # Different TTLs for different endpoints
        if "/api/search" in cache_key:
            ttl = 60  # Search results change frequently
        elif "/api/applications" in cache_key:
            ttl = 300  # Application data is more stable
        elif "/api/aggregations" in cache_key:
            ttl = 600  # Aggregations can be cached longer

        expires_at = datetime.utcnow() + timedelta(seconds=ttl)

        self.cache[cache_key] = {
            "body": response.body,
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "expires_at": expires_at
        }

        # Simple cache size management
        if len(self.cache) > 1000:
            # Remove oldest 20% of entries
            sorted_items = sorted(
                self.cache.items(),
                key=lambda x: x[1]["expires_at"]
            )
            for key, _ in sorted_items[:200]:
                del self.cache[key]


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Add security headers to responses

        Args:
            request: HTTP request
            call_next: Next middleware/endpoint

        Returns:
            Response with security headers
        """
        response = await call_next(request)

        # Add security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https:; "
                "font-src 'self' https:;"
            )
        }

        for header, value in security_headers.items():
            response.headers[header] = value

        return response


class ResponseTimeMiddleware(BaseHTTPMiddleware):
    """Middleware to add response time headers and optimize slow responses"""

    def __init__(self, app: FastAPI, slow_threshold_ms: int = 1000):
        super().__init__(app)
        self.slow_threshold_ms = slow_threshold_ms

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Track response times and optimize slow responses

        Args:
            request: HTTP request
            call_next: Next middleware/endpoint

        Returns:
            Response with timing headers
        """
        import time

        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        process_time_ms = round(process_time * 1000, 2)

        # Add timing headers
        response.headers["X-Process-Time"] = str(process_time_ms)

        # Log slow responses
        if process_time_ms > self.slow_threshold_ms:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"Slow response: {request.method} {request.url.path} took {process_time_ms}ms"
            )

        return response


def setup_performance_middleware(app: FastAPI) -> None:
    """
    Set up performance optimization middleware

    Args:
        app: FastAPI application instance
    """
    # Add security headers
    app.add_middleware(SecurityHeadersMiddleware)

    # Add response time tracking
    app.add_middleware(ResponseTimeMiddleware, slow_threshold_ms=1000)

    # Add caching (with conservative TTL for data freshness)
    app.add_middleware(CacheMiddleware, default_ttl=settings.cache_ttl)

    # Add compression (should be last to compress final response)
    app.add_middleware(CompressionMiddleware, minimum_size=1024)