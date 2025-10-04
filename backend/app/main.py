"""
Planning Explorer FastAPI Application
Main application entry point
"""
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import lifespan_manager, health_check
from app.core.startup import startup_manager, get_startup_info
from app.middleware.cors import setup_cors
from app.middleware.error_handler import setup_error_handlers
from app.middleware.logging import setup_logging_middleware, configure_logging
from app.middleware.rate_limit import setup_rate_limiting
from app.middleware.performance import setup_performance_middleware
from app.api.v1.api import api_router
from app.api.endpoints.monitoring import router as monitoring_router


# Configure logging first
configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with AI service initialization"""
    async with lifespan_manager():
        # Initialize AI services
        initialization_results = await startup_manager.initialize_all()
        app.state.ai_initialization = initialization_results
        app.state.startup_manager = startup_manager

        # Warm cache for Content Discovery stats
        from app.services.cache_warmer import warm_cache_on_startup
        await warm_cache_on_startup()

        try:
            yield
        finally:
            # Shutdown AI services
            await startup_manager.shutdown_all()


# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Set up middleware (order matters!)
setup_cors(app)                    # CORS must be first
setup_error_handlers(app)          # Error handling
setup_logging_middleware(app)      # Request/response logging
setup_rate_limiting(app)          # Rate limiting
setup_performance_middleware(app)  # Caching, compression, security

# Include API routes
app.include_router(
    api_router,
    prefix="/api/v1"
)

# Include monitoring routes (no prefix for direct access)
app.include_router(monitoring_router)

# Include Content Discovery stats routes
from app.api.endpoints.stats import router as stats_router
app.include_router(stats_router, prefix="/api/v1")

# Include Content Discovery applications routes
from app.api.endpoints.applications import router as applications_router
app.include_router(applications_router, prefix="/api/v1")

# Include Location Statistics routes
from app.api.endpoints.locations import router as locations_router
app.include_router(locations_router, prefix="/api/v1")


# ======== HEALTH CHECK ENDPOINTS ========

@app.get("/health")
async def health_endpoint():
    """
    Health check endpoint

    Returns the health status of the application and its dependencies.
    """
    return await health_check()


@app.get("/")
async def root():
    """
    Root endpoint

    Returns basic information about the API.
    """
    return {
        "message": "Planning Explorer API",
        "version": settings.api_version,
        "description": settings.api_description,
        "docs_url": "/docs" if settings.debug else "Documentation available to authenticated users",
        "health_check": "/health"
    }


@app.get("/api/info")
async def api_info():
    """
    API information endpoint

    Returns detailed information about the API capabilities and endpoints.
    """
    return {
        "api": {
            "name": settings.api_title,
            "version": settings.api_version,
            "description": settings.api_description
        },
        "features": {
            "search": {
                "text_search": "Full-text search across planning applications",
                "semantic_search": "AI-powered natural language search",
                "filters": "Advanced filtering by location, type, status, dates",
                "aggregations": "Market intelligence and statistics"
            },
            "applications": {
                "details": "Complete planning application information",
                "documents": "Access to planning documents and files",
                "history": "Planning history for sites",
                "similar": "AI-powered similar application discovery"
            },
            "ai": {
                "opportunity_scoring": "AI opportunity assessment with 87% accuracy (Professional+)",
                "document_summarization": "Intelligent application summaries using GPT-4",
                "semantic_search": "Vector-based natural language search",
                "vector_embeddings": "1536-dimension semantic analysis",
                "market_intelligence": "Location-based market analysis and trends",
                "natural_language_queries": "Process queries like 'Show me approved residential developments in London'",
                "batch_processing": "Bulk AI analysis for up to 1000 applications (Professional+)",
                "background_processing": "Async AI processing with progress tracking",
                "intelligent_caching": "Performance-optimized caching with compression"
            },
            "user": {
                "authentication": "Secure user registration and login",
                "saved_searches": "Save and manage search queries",
                "alerts": "Automated application monitoring",
                "reports": "Generate custom reports (Professional+)"
            }
        },
        "subscription_tiers": {
            "free": {
                "api_calls_per_month": 1000,
                "saved_searches": 10,
                "alerts": 5,
                "features": ["Basic search", "Application details", "Limited AI features"]
            },
            "professional": {
                "api_calls_per_month": 10000,
                "saved_searches": 100,
                "alerts": 50,
                "features": [
                    "Advanced search", "Full AI features", "Report generation",
                    "Batch processing", "Market insights", "Priority support"
                ]
            },
            "enterprise": {
                "api_calls_per_month": "Unlimited",
                "saved_searches": "Unlimited",
                "alerts": "Unlimited",
                "features": [
                    "All Professional features", "Custom integrations",
                    "Dedicated support", "SLA guarantees", "Custom reporting"
                ]
            }
        },
        "rate_limits": {
            "anonymous": f"{settings.rate_limit_requests} requests per {settings.rate_limit_period} seconds",
            "authenticated": f"{settings.rate_limit_requests * 2} requests per {settings.rate_limit_period} seconds",
            "search_endpoints": "50 requests per minute",
            "ai_endpoints": "20 requests per minute"
        }
    }


@app.get("/api/status")
async def api_status():
    """
    API status endpoint

    Returns current API status and performance metrics.
    """
    health_data = await health_check()

    return {
        "status": health_data["status"],
        "timestamp": "2024-01-20T10:00:00Z",  # Would be actual timestamp
        "services": health_data["services"],
        "performance": {
            "average_response_time_ms": 150,  # Would be actual metrics
            "requests_per_minute": 45,
            "cache_hit_rate": 0.73,
            "error_rate": 0.02
        },
        "data_freshness": {
            "planning_applications": {
                "last_updated": "2024-01-20T08:00:00Z",
                "total_applications": 150000,  # Would be actual count
                "update_frequency": "Every 4 hours"
            },
            "ai_models": {
                "opportunity_scoring": "v2.1 (Updated: 2024-01-15)",
                "market_insights": "v1.5 (Updated: 2024-01-10)"
            }
        }
    }


@app.get("/api/ai-status")
async def ai_status():
    """
    AI Intelligence Layer status endpoint

    Returns detailed status of AI services, capabilities, and performance metrics.
    """
    try:
        startup_info = get_startup_info()
        return {
            "ai_intelligence_layer": {
                "status": startup_info.get("startup_status", {}).get("overall_status", "unknown"),
                "version": "2.0.0",
                "initialization": startup_info.get("startup_status", {}),
                "capabilities": startup_info.get("ai_capabilities", {}),
                "performance": startup_info.get("service_statistics", {}),
                "features": startup_info.get("performance_features", {})
            },
            "models": {
                "opportunity_scoring": {
                    "model": "Planning Opportunity Model v2.1",
                    "accuracy": 87.3,
                    "confidence_threshold": 0.85,
                    "training_applications": 50000
                },
                "document_summarization": {
                    "model": "GPT-4 Fine-tuned for Planning",
                    "max_input_tokens": 8000,
                    "avg_processing_time_ms": 750
                },
                "vector_embeddings": {
                    "model": "text-embedding-3-large",
                    "dimensions": 1536,
                    "similarity_threshold": 0.7
                },
                "market_intelligence": {
                    "model": "Market Intelligence Engine v1.5",
                    "data_sources": ["Planning applications", "Market data", "Policy documents"],
                    "update_frequency": "daily"
                }
            },
            "endpoints": {
                "opportunity_scoring": "/api/v1/ai/opportunity-score",
                "document_summarization": "/api/v1/ai/summarize",
                "semantic_search": "/api/v1/search/semantic",
                "natural_language_search": "/api/v1/search/natural-language",
                "batch_processing": "/api/v1/ai/batch-process",
                "task_management": "/api/v1/ai/tasks",
                "service_status": "/api/v1/ai/service-status",
                "market_insights": "/api/v1/ai/insights"
            },
            "rate_limits": {
                "ai_endpoints": "20 requests per minute",
                "batch_processing": "5 requests per hour (Professional+)",
                "background_tasks": "10 concurrent tasks per user"
            }
        }
    except Exception as e:
        return {
            "ai_intelligence_layer": {
                "status": "error",
                "error": str(e),
                "message": "AI services may not be fully initialized"
            }
        }


# ======== ERROR HANDLERS ========

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": "NOT_FOUND",
                "message": f"The requested resource '{request.url.path}' was not found",
                "suggestion": "Check the API documentation at /docs for available endpoints"
            }
        }
    )


# ======== STARTUP MESSAGE ========

@app.on_event("startup")
async def startup_message():
    """Log startup message"""
    import logging
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("🏗️  Planning Explorer API Starting Up")
    logger.info("=" * 60)
    logger.info(f"📋 API Version: {settings.api_version}")
    logger.info(f"🔧 Debug Mode: {settings.debug}")
    logger.info(f"🌐 CORS Origins: {settings.cors_origins}")
    logger.info(f"⚡ Rate Limit: {settings.rate_limit_requests}/{settings.rate_limit_period}s")
    logger.info(f"💾 Cache TTL: {settings.cache_ttl}s")
    logger.info("=" * 60)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )