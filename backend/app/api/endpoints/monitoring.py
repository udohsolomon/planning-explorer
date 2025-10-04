"""
Monitoring and health check endpoints for Planning Explorer API
"""
import asyncio
import logging
import psutil
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.config import settings
from app.core.dependencies import (
    get_supabase_client,
    get_elasticsearch_client,
    check_api_health,
    config_validator,
    rate_limit_tracker
)
from app.core.exceptions import error_handler
from app.middleware.auth import get_admin_user, get_optional_user
from app.db.supabase import supabase_client
from app.db.elasticsearch import es_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


class HealthCheckResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: str
    uptime_seconds: float
    services: Dict[str, Any]
    configuration: Dict[str, Any]


class SystemMetricsResponse(BaseModel):
    """System metrics response model"""
    cpu_usage_percent: float
    memory_usage_percent: float
    disk_usage_percent: float
    active_connections: int
    request_count: int
    error_rate: float
    average_response_time_ms: float


class ServiceStatusResponse(BaseModel):
    """Service status response model"""
    service_name: str
    status: str
    uptime_seconds: Optional[float] = None
    last_check: str
    details: Dict[str, Any]


# Store application start time for uptime calculation
app_start_time = time.time()

# Request metrics storage (in production, this would be in Redis or a proper metrics store)
request_metrics = {
    "total_requests": 0,
    "total_errors": 0,
    "response_times": [],
    "last_reset": time.time()
}


async def update_request_metrics(response_time_ms: float, is_error: bool = False):
    """Update request metrics"""
    request_metrics["total_requests"] += 1
    if is_error:
        request_metrics["total_errors"] += 1

    request_metrics["response_times"].append(response_time_ms)

    # Keep only last 1000 response times
    if len(request_metrics["response_times"]) > 1000:
        request_metrics["response_times"] = request_metrics["response_times"][-1000:]


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Comprehensive health check endpoint

    Returns detailed health status of all system components.
    """
    try:
        health_data = await check_api_health()
        uptime = time.time() - app_start_time

        return HealthCheckResponse(
            status=health_data["status"],
            timestamp=datetime.utcnow().isoformat(),
            uptime_seconds=uptime,
            services=health_data["services"],
            configuration=health_data["configuration"]
        )

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        )


@router.get("/health/liveness")
async def liveness_probe():
    """
    Kubernetes liveness probe endpoint

    Simple check to verify the application is running.
    """
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}


@router.get("/health/readiness")
async def readiness_probe():
    """
    Kubernetes readiness probe endpoint

    Check if the application is ready to receive traffic.
    """
    try:
        # Check critical dependencies
        await supabase_client.ensure_connection()
        await es_client.ensure_connection()

        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "supabase": "healthy",
                "elasticsearch": "healthy"
            }
        }

    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        )


@router.get("/metrics", response_model=SystemMetricsResponse)
async def system_metrics(admin_user: Dict[str, Any] = Depends(get_admin_user)):
    """
    Get system performance metrics

    Requires admin access.
    """
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)

        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent

        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100

        # Connection counts
        connections = len(psutil.net_connections())

        # Calculate metrics
        total_requests = request_metrics["total_requests"]
        total_errors = request_metrics["total_errors"]
        error_rate = (total_errors / total_requests) if total_requests > 0 else 0.0

        avg_response_time = 0.0
        if request_metrics["response_times"]:
            avg_response_time = sum(request_metrics["response_times"]) / len(request_metrics["response_times"])

        return SystemMetricsResponse(
            cpu_usage_percent=cpu_percent,
            memory_usage_percent=memory_percent,
            disk_usage_percent=disk_percent,
            active_connections=connections,
            request_count=total_requests,
            error_rate=error_rate,
            average_response_time_ms=avg_response_time
        )

    except Exception as e:
        logger.error(f"Failed to get system metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system metrics"
        )


@router.get("/services")
async def service_status(admin_user: Dict[str, Any] = Depends(get_admin_user)):
    """
    Get detailed status of all services

    Requires admin access.
    """
    services = []

    # Supabase status
    try:
        await supabase_client.ensure_connection()
        supabase_status = {
            "status": "healthy",
            "details": {
                "connected": True,
                "pool_size": getattr(supabase_client.pool, 'pool_size', 1) if supabase_client.pool else 1,
                "connection_type": "pooled" if supabase_client.pool else "single"
            }
        }
    except Exception as e:
        supabase_status = {
            "status": "unhealthy",
            "details": {"error": str(e)}
        }

    services.append(ServiceStatusResponse(
        service_name="supabase",
        status=supabase_status["status"],
        last_check=datetime.utcnow().isoformat(),
        details=supabase_status["details"]
    ))

    # Elasticsearch status
    try:
        es_healthy = await es_client.health_check()
        es_status = {
            "status": "healthy" if es_healthy else "unhealthy",
            "details": {
                "connected": es_healthy,
                "cluster_health": "green" if es_healthy else "red"
            }
        }

        if es_healthy and es_client.client:
            # Get cluster info
            try:
                cluster_info = await es_client.client.cluster.health()
                es_status["details"]["cluster_health"] = cluster_info["status"]
                es_status["details"]["number_of_nodes"] = cluster_info["number_of_nodes"]
            except:
                pass

    except Exception as e:
        es_status = {
            "status": "unhealthy",
            "details": {"error": str(e)}
        }

    services.append(ServiceStatusResponse(
        service_name="elasticsearch",
        status=es_status["status"],
        last_check=datetime.utcnow().isoformat(),
        details=es_status["details"]
    ))

    return {"services": services}


@router.get("/configuration")
async def configuration_status(admin_user: Dict[str, Any] = Depends(get_admin_user)):
    """
    Get configuration validation status

    Requires admin access.
    """
    config_report = config_validator.get_validation_report()

    return {
        "configuration": config_report,
        "settings": {
            "api_version": settings.api_version,
            "debug_mode": settings.debug,
            "max_connections": settings.max_connections,
            "rate_limits": {
                "requests": settings.rate_limit_requests,
                "period_seconds": settings.rate_limit_period
            },
            "subscription_tiers": {
                "free_api_limit": settings.free_tier_api_limit,
                "professional_api_limit": settings.professional_tier_api_limit,
                "enterprise_api_limit": settings.enterprise_tier_api_limit
            }
        }
    }


@router.get("/errors")
async def error_statistics(admin_user: Dict[str, Any] = Depends(get_admin_user)):
    """
    Get error statistics and recent errors

    Requires admin access.
    """
    return error_handler.get_error_stats()


@router.post("/errors/clear")
async def clear_error_statistics(admin_user: Dict[str, Any] = Depends(get_admin_user)):
    """
    Clear error statistics

    Requires admin access.
    """
    error_handler.clear_error_stats()
    return {"message": "Error statistics cleared"}


@router.get("/rate-limits")
async def rate_limit_status(
    admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """
    Get rate limiting status and statistics

    Requires admin access.
    """
    return {
        "configuration": {
            "requests_per_period": settings.rate_limit_requests,
            "period_seconds": settings.rate_limit_period
        },
        "active_limits": {
            "tracked_identifiers": len(rate_limit_tracker.request_counts),
            "current_requests": dict(rate_limit_tracker.request_counts),
            "last_reset_times": dict(rate_limit_tracker.last_reset)
        }
    }


@router.get("/performance")
async def performance_metrics(
    admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """
    Get detailed performance metrics

    Requires admin access.
    """
    uptime = time.time() - app_start_time

    # Response time percentiles
    response_times = request_metrics["response_times"]
    percentiles = {}
    if response_times:
        sorted_times = sorted(response_times)
        percentiles = {
            "p50": sorted_times[int(len(sorted_times) * 0.5)],
            "p95": sorted_times[int(len(sorted_times) * 0.95)],
            "p99": sorted_times[int(len(sorted_times) * 0.99)]
        }

    return {
        "uptime_seconds": uptime,
        "requests": {
            "total": request_metrics["total_requests"],
            "errors": request_metrics["total_errors"],
            "error_rate": (request_metrics["total_errors"] / request_metrics["total_requests"]) if request_metrics["total_requests"] > 0 else 0,
            "requests_per_second": request_metrics["total_requests"] / uptime if uptime > 0 else 0
        },
        "response_times": {
            "average_ms": sum(response_times) / len(response_times) if response_times else 0,
            "percentiles": percentiles,
            "sample_count": len(response_times)
        },
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "active_processes": len(psutil.pids())
        }
    }


@router.get("/dependencies")
async def dependency_status():
    """
    Check status of external dependencies

    Public endpoint for service discovery.
    """
    try:
        dependencies = {
            "supabase": {
                "status": "unknown",
                "response_time_ms": None
            },
            "elasticsearch": {
                "status": "unknown",
                "response_time_ms": None
            }
        }

        # Test Supabase
        start_time = time.time()
        try:
            await supabase_client.ensure_connection()
            dependencies["supabase"]["status"] = "healthy"
            dependencies["supabase"]["response_time_ms"] = (time.time() - start_time) * 1000
        except Exception as e:
            dependencies["supabase"]["status"] = "unhealthy"
            dependencies["supabase"]["error"] = str(e)

        # Test Elasticsearch
        start_time = time.time()
        try:
            es_healthy = await es_client.health_check()
            dependencies["elasticsearch"]["status"] = "healthy" if es_healthy else "unhealthy"
            dependencies["elasticsearch"]["response_time_ms"] = (time.time() - start_time) * 1000
        except Exception as e:
            dependencies["elasticsearch"]["status"] = "unhealthy"
            dependencies["elasticsearch"]["error"] = str(e)

        return dependencies

    except Exception as e:
        logger.error(f"Dependency check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check dependencies"
        )


# Middleware should be added at the app level, not router level
# @router.middleware("http")
# async def track_request_metrics(request: Request, call_next):
#     """Middleware to track request metrics"""
#     start_time = time.time()
#
#     try:
#         response = await call_next(request)
#         response_time_ms = (time.time() - start_time) * 1000
#         is_error = response.status_code >= 400
#
#         await update_request_metrics(response_time_ms, is_error)
#
#         return response
#
#     except Exception as e:
#         response_time_ms = (time.time() - start_time) * 1000
#         await update_request_metrics(response_time_ms, True)
#         raise


# Startup event to initialize monitoring
async def initialize_monitoring():
    """Initialize monitoring system"""
    logger.info("Initializing monitoring system...")

    # Reset metrics
    global app_start_time
    app_start_time = time.time()

    request_metrics.update({
        "total_requests": 0,
        "total_errors": 0,
        "response_times": [],
        "last_reset": time.time()
    })

    logger.info("✅ Monitoring system initialized")


# Cleanup function
async def cleanup_monitoring():
    """Cleanup monitoring resources"""
    logger.info("Cleaning up monitoring system...")
    # Add any cleanup logic here
    logger.info("✅ Monitoring cleanup completed")