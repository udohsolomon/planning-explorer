"""
Logging middleware for Planning Explorer API
"""
import time
import uuid
import logging
from typing import Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

from app.core.config import settings

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging and performance tracking"""

    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.app = app

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and response with logging

        Args:
            request: HTTP request
            call_next: Next middleware/endpoint

        Returns:
            HTTP response
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Start timing
        start_time = time.time()

        # Get client information
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")

        # Log request
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client_ip": client_ip,
                "user_agent": user_agent,
                "headers": dict(request.headers) if settings.log_level == "DEBUG" else {}
            }
        )

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log error and re-raise
            processing_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "processing_time_ms": round(processing_time * 1000, 2),
                    "error": str(e),
                    "client_ip": client_ip
                }
            )
            raise

        # Calculate processing time
        processing_time = time.time() - start_time
        processing_time_ms = round(processing_time * 1000, 2)

        # Add response headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = str(processing_time_ms)

        # Get response size
        response_size = 0
        if hasattr(response, "body"):
            response_size = len(response.body)
        elif isinstance(response, StreamingResponse):
            # For streaming responses, we can't easily get the size
            response_size = -1

        # Log response
        log_level = logging.INFO
        if response.status_code >= 400:
            log_level = logging.WARNING
        if response.status_code >= 500:
            log_level = logging.ERROR

        logger.log(
            log_level,
            f"Request completed: {request.method} {request.url.path} - {response.status_code}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "processing_time_ms": processing_time_ms,
                "response_size_bytes": response_size,
                "client_ip": client_ip
            }
        )

        # Log slow requests
        if processing_time_ms > 1000:  # Log requests slower than 1 second
            logger.warning(
                f"Slow request detected: {processing_time_ms}ms",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "processing_time_ms": processing_time_ms
                }
            )

        return response

    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address from request

        Args:
            request: HTTP request

        Returns:
            Client IP address
        """
        # Check for IP in headers (proxy/load balancer scenarios)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fallback to client host
        if request.client:
            return request.client.host

        return "unknown"


class RequestSizeMiddleware(BaseHTTPMiddleware):
    """Middleware to limit request body size"""

    def __init__(self, app: FastAPI, max_size: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Check request size limits

        Args:
            request: HTTP request
            call_next: Next middleware/endpoint

        Returns:
            HTTP response

        Raises:
            HTTPException: If request body is too large
        """
        content_length = request.headers.get("content-length")

        if content_length:
            content_length = int(content_length)
            if content_length > self.max_size:
                from fastapi import HTTPException, status
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Request body too large. Maximum size: {self.max_size} bytes"
                )

        return await call_next(request)


def setup_logging_middleware(app: FastAPI) -> None:
    """
    Set up logging middleware for the FastAPI application

    Args:
        app: FastAPI application instance
    """
    # Add request size limits
    app.add_middleware(RequestSizeMiddleware, max_size=10 * 1024 * 1024)  # 10MB

    # Add logging middleware
    app.add_middleware(LoggingMiddleware)


def configure_logging():
    """Configure application logging"""

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Configure specific loggers
    loggers = {
        "app": logging.getLogger("app"),
        "uvicorn": logging.getLogger("uvicorn"),
        "uvicorn.access": logging.getLogger("uvicorn.access"),
        "fastapi": logging.getLogger("fastapi"),
        "elasticsearch": logging.getLogger("elasticsearch"),
        "supabase": logging.getLogger("supabase")
    }

    # Set log levels
    for logger_name, logger_instance in loggers.items():
        if logger_name == "uvicorn.access":
            # Reduce access log verbosity
            logger_instance.setLevel(logging.WARNING)
        else:
            logger_instance.setLevel(getattr(logging, settings.log_level.upper()))

    # Disable some noisy loggers in production
    if settings.log_level.upper() != "DEBUG":
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)

    logger.info("Logging configured successfully")
    logger.info(f"Log level: {settings.log_level.upper()}")
    logger.info(f"Debug mode: {settings.debug}")