"""
Custom exceptions and error handling for Planning Explorer API
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.requests import Request


logger = logging.getLogger(__name__)


class PlanningExplorerException(Exception):
    """Base exception for Planning Explorer application"""

    def __init__(
        self,
        message: str,
        error_code: str = "GENERAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()
        super().__init__(message)


class ValidationError(PlanningExplorerException):
    """Input validation error"""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details or {}
        )
        if field:
            self.details["field"] = field
        if value is not None:
            self.details["provided_value"] = str(value)


class AuthenticationError(PlanningExplorerException):
    """Authentication failed"""

    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )


class AuthorizationError(PlanningExplorerException):
    """Authorization/permission denied"""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        required_role: Optional[str] = None,
        required_tier: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=status.HTTP_403_FORBIDDEN,
            details=details or {}
        )
        if required_role:
            self.details["required_role"] = required_role
        if required_tier:
            self.details["required_tier"] = required_tier


class SubscriptionRequiredError(PlanningExplorerException):
    """Subscription upgrade required"""

    def __init__(
        self,
        message: str = "Subscription upgrade required",
        current_tier: Optional[str] = None,
        required_tier: Optional[str] = None,
        feature: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="SUBSCRIPTION_REQUIRED",
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            details=details or {}
        )
        if current_tier:
            self.details["current_tier"] = current_tier
        if required_tier:
            self.details["required_tier"] = required_tier
        if feature:
            self.details["feature"] = feature


class RateLimitExceededError(PlanningExplorerException):
    """Rate limit exceeded"""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        limit: Optional[int] = None,
        window: Optional[int] = None,
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details or {}
        )
        if limit:
            self.details["limit"] = limit
        if window:
            self.details["window_seconds"] = window
        if retry_after:
            self.details["retry_after_seconds"] = retry_after


class UsageLimitExceededError(PlanningExplorerException):
    """Usage limit exceeded for subscription tier"""

    def __init__(
        self,
        message: str = "Usage limit exceeded",
        resource_type: Optional[str] = None,
        current_usage: Optional[int] = None,
        limit: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="USAGE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details or {}
        )
        if resource_type:
            self.details["resource_type"] = resource_type
        if current_usage is not None:
            self.details["current_usage"] = current_usage
        if limit is not None:
            self.details["limit"] = limit


class DatabaseConnectionError(PlanningExplorerException):
    """Database connection failed"""

    def __init__(
        self,
        message: str = "Database connection failed",
        service: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="DATABASE_CONNECTION_ERROR",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details or {}
        )
        if service:
            self.details["service"] = service


class SearchServiceError(PlanningExplorerException):
    """Search service error"""

    def __init__(
        self,
        message: str = "Search service error",
        query: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="SEARCH_SERVICE_ERROR",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details or {}
        )
        if query:
            self.details["query"] = query


class AIServiceError(PlanningExplorerException):
    """AI service error"""

    def __init__(
        self,
        message: str = "AI service error",
        service: Optional[str] = None,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="AI_SERVICE_ERROR",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details or {}
        )
        if service:
            self.details["service"] = service
        if operation:
            self.details["operation"] = operation


class DataNotFoundError(PlanningExplorerException):
    """Requested data not found"""

    def __init__(
        self,
        message: str = "Data not found",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="DATA_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details or {}
        )
        if resource_type:
            self.details["resource_type"] = resource_type
        if resource_id:
            self.details["resource_id"] = resource_id


class ConfigurationError(PlanningExplorerException):
    """Configuration error"""

    def __init__(
        self,
        message: str = "Configuration error",
        config_key: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details or {}
        )
        if config_key:
            self.details["config_key"] = config_key


class ExternalServiceError(PlanningExplorerException):
    """External service error"""

    def __init__(
        self,
        message: str = "External service error",
        service_name: Optional[str] = None,
        service_response: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details or {}
        )
        if service_name:
            self.details["service_name"] = service_name
        if service_response:
            self.details["service_response"] = service_response


class ErrorHandler:
    """Central error handler for the application"""

    def __init__(self):
        self.error_counts = {}
        self.last_errors = []
        self.max_recent_errors = 100

    def log_error(self, error: Exception, request: Optional[Request] = None, user_id: Optional[str] = None):
        """Log error with context information"""
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id
        }

        if request:
            error_info.update({
                "path": request.url.path,
                "method": request.method,
                "query_params": dict(request.query_params),
                "headers": dict(request.headers),
                "client_ip": request.client.host if request.client else None
            })

        if isinstance(error, PlanningExplorerException):
            error_info.update({
                "error_code": error.error_code,
                "status_code": error.status_code,
                "details": error.details
            })

        # Count error occurrences
        error_key = f"{type(error).__name__}:{str(error)[:100]}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1

        # Store recent errors
        self.last_errors.append(error_info)
        if len(self.last_errors) > self.max_recent_errors:
            self.last_errors.pop(0)

        # Log to application logger
        if isinstance(error, PlanningExplorerException):
            if error.status_code >= 500:
                logger.error(f"Internal error: {error.message}", extra=error_info)
            elif error.status_code >= 400:
                logger.warning(f"Client error: {error.message}", extra=error_info)
            else:
                logger.info(f"Error handled: {error.message}", extra=error_info)
        else:
            logger.error(f"Unexpected error: {str(error)}", extra=error_info, exc_info=True)

    def create_error_response(self, error: Exception, request: Optional[Request] = None) -> JSONResponse:
        """Create standardized error response"""
        if isinstance(error, PlanningExplorerException):
            response_content = {
                "error": {
                    "code": error.error_code,
                    "message": error.message,
                    "timestamp": error.timestamp,
                    "details": error.details
                }
            }

            # Add request context for debugging (only in debug mode)
            if request and hasattr(request.app, 'debug') and request.app.debug:
                response_content["debug"] = {
                    "path": request.url.path,
                    "method": request.method
                }

            return JSONResponse(
                status_code=error.status_code,
                content=response_content
            )
        else:
            # Generic error response for unexpected errors
            response_content = {
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

            # Include error details in debug mode
            if request and hasattr(request.app, 'debug') and request.app.debug:
                response_content["debug"] = {
                    "error_type": type(error).__name__,
                    "error_message": str(error),
                    "path": request.url.path,
                    "method": request.method
                }

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=response_content
            )

    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        return {
            "total_errors": sum(self.error_counts.values()),
            "unique_errors": len(self.error_counts),
            "most_common_errors": sorted(
                self.error_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
            "recent_errors_count": len(self.last_errors),
            "last_error": self.last_errors[-1] if self.last_errors else None
        }

    def clear_error_stats(self):
        """Clear error statistics"""
        self.error_counts.clear()
        self.last_errors.clear()


# Global error handler instance
error_handler = ErrorHandler()


def create_validation_error_response(validation_errors: List[Dict[str, Any]]) -> ValidationError:
    """Create validation error from pydantic validation errors"""
    if len(validation_errors) == 1:
        error = validation_errors[0]
        field = ".".join(str(loc) for loc in error.get("loc", []))
        return ValidationError(
            message=error.get("msg", "Validation failed"),
            field=field,
            value=error.get("input"),
            details={"validation_errors": validation_errors}
        )
    else:
        return ValidationError(
            message=f"Multiple validation errors ({len(validation_errors)} fields)",
            details={"validation_errors": validation_errors}
        )


# Common error responses for reuse
def authentication_required():
    """Standard authentication required error"""
    return AuthenticationError("Authentication required to access this resource")


def subscription_required(required_tier: str, current_tier: str = "free"):
    """Standard subscription required error"""
    return SubscriptionRequiredError(
        message=f"This feature requires {required_tier} subscription",
        current_tier=current_tier,
        required_tier=required_tier
    )


def rate_limit_exceeded(limit: int, window: int, retry_after: int = None):
    """Standard rate limit exceeded error"""
    return RateLimitExceededError(
        message=f"Rate limit exceeded: {limit} requests per {window} seconds",
        limit=limit,
        window=window,
        retry_after=retry_after
    )


def usage_limit_exceeded(resource_type: str, current: int, limit: int):
    """Standard usage limit exceeded error"""
    return UsageLimitExceededError(
        message=f"{resource_type.title()} limit exceeded: {current}/{limit}",
        resource_type=resource_type,
        current_usage=current,
        limit=limit
    )


def service_unavailable(service_name: str):
    """Standard service unavailable error"""
    return DatabaseConnectionError(
        message=f"{service_name} service is currently unavailable",
        service=service_name
    )


def data_not_found(resource_type: str, resource_id: str = None):
    """Standard data not found error"""
    return DataNotFoundError(
        message=f"{resource_type.title()} not found" + (f": {resource_id}" if resource_id else ""),
        resource_type=resource_type,
        resource_id=resource_id
    )


# Export all exceptions and utilities
__all__ = [
    "PlanningExplorerException",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "SubscriptionRequiredError",
    "RateLimitExceededError",
    "UsageLimitExceededError",
    "DatabaseConnectionError",
    "SearchServiceError",
    "AIServiceError",
    "DataNotFoundError",
    "ConfigurationError",
    "ExternalServiceError",
    "ErrorHandler",
    "error_handler",
    "create_validation_error_response",
    "authentication_required",
    "subscription_required",
    "rate_limit_exceeded",
    "usage_limit_exceeded",
    "service_unavailable",
    "data_not_found"
]