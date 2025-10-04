"""
Enhanced error handling middleware for Planning Explorer API
"""
import logging
import traceback
from typing import Union, Optional
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError

from app.core.exceptions import (
    PlanningExplorerException,
    error_handler,
    create_validation_error_response
)

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Custom API error class"""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR",
        details: dict = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


def create_error_response(
    status_code: int,
    message: str,
    error_code: str = "ERROR",
    details: dict = None,
    request_id: str = None
) -> JSONResponse:
    """
    Create standardized error response

    Args:
        status_code: HTTP status code
        message: Error message
        error_code: Internal error code
        details: Additional error details
        request_id: Request ID for tracking

    Returns:
        JSONResponse with error details
    """
    error_response = {
        "error": {
            "code": error_code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
        }
    }

    if details:
        error_response["error"]["details"] = details

    if request_id:
        error_response["error"]["request_id"] = request_id

    return JSONResponse(
        status_code=status_code,
        content=error_response
    )


def setup_error_handlers(app: FastAPI) -> None:
    """
    Set up enhanced error handlers for the FastAPI application

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(PlanningExplorerException)
    async def planning_explorer_exception_handler(request: Request, exc: PlanningExplorerException) -> JSONResponse:
        """Handle custom Planning Explorer exceptions"""
        request_id = getattr(request.state, "request_id", None)
        user_id = getattr(request.state, "user_id", None)

        # Log error with context
        error_handler.log_error(exc, request, user_id)

        return error_handler.create_error_response(exc, request)

    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
        """Handle legacy custom API errors"""
        request_id = getattr(request.state, "request_id", None)

        logger.error(
            f"API Error: {exc.message}",
            extra={
                "error_code": exc.error_code,
                "status_code": exc.status_code,
                "details": exc.details,
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method
            }
        )

        return create_error_response(
            status_code=exc.status_code,
            message=exc.message,
            error_code=exc.error_code,
            details=exc.details,
            request_id=request_id
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """Handle FastAPI HTTP exceptions"""
        request_id = getattr(request.state, "request_id", None)

        # Map HTTP status codes to error codes
        error_code_mapping = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            409: "CONFLICT",
            422: "VALIDATION_ERROR",
            429: "RATE_LIMIT_EXCEEDED",
            500: "INTERNAL_ERROR",
            502: "BAD_GATEWAY",
            503: "SERVICE_UNAVAILABLE"
        }

        error_code = error_code_mapping.get(exc.status_code, "HTTP_ERROR")

        logger.warning(
            f"HTTP Exception: {exc.detail}",
            extra={
                "status_code": exc.status_code,
                "error_code": error_code,
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method
            }
        )

        return create_error_response(
            status_code=exc.status_code,
            message=str(exc.detail),
            error_code=error_code,
            request_id=request_id
        )

    @app.exception_handler(StarletteHTTPException)
    async def starlette_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """Handle Starlette HTTP exceptions"""
        request_id = getattr(request.state, "request_id", None)

        logger.warning(
            f"Starlette Exception: {exc.detail}",
            extra={
                "status_code": exc.status_code,
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method
            }
        )

        return create_error_response(
            status_code=exc.status_code,
            message=str(exc.detail),
            error_code="HTTP_ERROR",
            request_id=request_id
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle Pydantic validation errors"""
        request_id = getattr(request.state, "request_id", None)
        user_id = getattr(request.state, "user_id", None)

        # Convert to our custom validation error
        validation_error = create_validation_error_response(exc.errors())

        # Log error with context
        error_handler.log_error(validation_error, request, user_id)

        return error_handler.create_error_response(validation_error, request)

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
        """Handle Pydantic validation errors from models"""
        request_id = getattr(request.state, "request_id", None)

        # Format validation errors
        validation_errors = []
        for error in exc.errors():
            validation_errors.append({
                "field": " -> ".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })

        logger.warning(
            f"Model Validation Error: {len(validation_errors)} validation errors",
            extra={
                "validation_errors": validation_errors,
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method
            }
        )

        return create_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Model validation failed",
            error_code="MODEL_VALIDATION_ERROR",
            details={"validation_errors": validation_errors},
            request_id=request_id
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle all other unhandled exceptions"""
        request_id = getattr(request.state, "request_id", None)

        # Log the full exception with traceback
        logger.error(
            f"Unhandled Exception: {str(exc)}",
            extra={
                "exception_type": type(exc).__name__,
                "traceback": traceback.format_exc(),
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method
            }
        )

        # Don't expose internal error details in production
        if logger.level <= logging.DEBUG:
            message = f"Internal server error: {str(exc)}"
            details = {"exception_type": type(exc).__name__}
        else:
            message = "An internal server error occurred"
            details = None

        return create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=message,
            error_code="INTERNAL_SERVER_ERROR",
            details=details,
            request_id=request_id
        )