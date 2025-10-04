"""
Rate limiting middleware for Planning Explorer API
"""
import time
import asyncio
from typing import Dict, Optional
from collections import defaultdict, deque

from fastapi import FastAPI, Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import settings


class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self):
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.lock = asyncio.Lock()

    async def is_allowed(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple[bool, int]:
        """
        Check if request is allowed within rate limits

        Args:
            key: Unique identifier for rate limiting (IP, user ID, etc.)
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds

        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        async with self.lock:
            now = time.time()
            window_start = now - window_seconds

            # Get request history for this key
            request_times = self.requests[key]

            # Remove old requests outside the window
            while request_times and request_times[0] < window_start:
                request_times.popleft()

            # Check if we're within limits
            current_requests = len(request_times)
            remaining = max(0, max_requests - current_requests)

            if current_requests >= max_requests:
                return False, 0

            # Add current request
            request_times.append(now)

            return True, remaining - 1

    async def get_reset_time(self, key: str, window_seconds: int) -> Optional[int]:
        """
        Get when the rate limit will reset

        Args:
            key: Rate limit key
            window_seconds: Window size in seconds

        Returns:
            Unix timestamp when limit resets, or None if no limits
        """
        request_times = self.requests.get(key)
        if not request_times:
            return None

        oldest_request = request_times[0]
        reset_time = oldest_request + window_seconds
        return int(reset_time)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""

    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.rate_limiter = RateLimiter()
        self.default_requests = settings.rate_limit_requests
        self.default_period = settings.rate_limit_period

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Apply rate limiting to requests

        Args:
            request: HTTP request
            call_next: Next middleware/endpoint

        Returns:
            HTTP response

        Raises:
            HTTPException: If rate limit exceeded
        """
        # Skip rate limiting for certain paths
        skip_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/favicon.ico"
        ]

        if any(request.url.path.startswith(path) for path in skip_paths):
            return await call_next(request)

        # Determine rate limit key and limits
        rate_limit_key, max_requests, window_seconds = self._get_rate_limit_params(request)

        # Check rate limit
        is_allowed, remaining = await self.rate_limiter.is_allowed(
            key=rate_limit_key,
            max_requests=max_requests,
            window_seconds=window_seconds
        )

        if not is_allowed:
            # Get reset time
            reset_time = await self.rate_limiter.get_reset_time(rate_limit_key, window_seconds)

            # Create rate limit exceeded response
            headers = {
                "X-Rate-Limit-Limit": str(max_requests),
                "X-Rate-Limit-Remaining": "0",
                "X-Rate-Limit-Reset": str(reset_time) if reset_time else "",
                "Retry-After": str(window_seconds)
            }

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers=headers
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        reset_time = await self.rate_limiter.get_reset_time(rate_limit_key, window_seconds)
        response.headers["X-Rate-Limit-Limit"] = str(max_requests)
        response.headers["X-Rate-Limit-Remaining"] = str(remaining)
        if reset_time:
            response.headers["X-Rate-Limit-Reset"] = str(reset_time)

        return response

    def _get_rate_limit_params(self, request: Request) -> tuple[str, int, int]:
        """
        Get rate limiting parameters for the request

        Args:
            request: HTTP request

        Returns:
            Tuple of (key, max_requests, window_seconds)
        """
        # Check if user is authenticated
        auth_header = request.headers.get("authorization")
        user_id = None

        if auth_header:
            # Extract user ID from token (simplified)
            # In production, this would properly decode the JWT
            try:
                # This is a placeholder - implement proper JWT parsing
                user_id = "user_from_token"
            except:
                user_id = None

        if user_id:
            # Authenticated user rate limits (more generous)
            # Different limits based on user tier would be implemented here
            rate_limit_key = f"user:{user_id}"
            max_requests = self.default_requests * 2  # 2x limit for authenticated users
            window_seconds = self.default_period
        else:
            # Anonymous user rate limits (based on IP)
            client_ip = self._get_client_ip(request)
            rate_limit_key = f"ip:{client_ip}"
            max_requests = self.default_requests
            window_seconds = self.default_period

        # Apply endpoint-specific limits
        if request.url.path.startswith("/api/search"):
            # Search endpoints might have different limits
            max_requests = min(max_requests, 50)  # Max 50 searches per minute
        elif request.url.path.startswith("/api/ai"):
            # AI endpoints are more expensive
            max_requests = min(max_requests, 20)  # Max 20 AI requests per minute

        return rate_limit_key, max_requests, window_seconds

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for IP in headers (proxy scenarios)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        if request.client:
            return request.client.host

        return "unknown"


def setup_rate_limiting(app: FastAPI) -> None:
    """
    Set up rate limiting middleware

    Args:
        app: FastAPI application instance
    """
    app.add_middleware(RateLimitMiddleware)