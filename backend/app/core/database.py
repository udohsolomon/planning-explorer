"""
Database connection management and lifecycle for Planning Explorer
"""
import asyncio
import logging
from contextlib import asynccontextmanager

from app.db.elasticsearch import es_client
from app.db.supabase import supabase_client

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan_manager():
    """
    Application lifespan manager for database connections

    Handles startup and shutdown of database connections
    """
    # Startup
    logger.info("Starting application...")

    # Initialize Elasticsearch connection
    try:
        es_connected = await es_client.connect()
        if es_connected:
            logger.info("✅ Elasticsearch connection established")
        else:
            logger.error("❌ Failed to connect to Elasticsearch")
    except Exception as e:
        logger.error(f"❌ Elasticsearch connection error: {str(e)}")

    # Initialize Supabase connection
    try:
        supabase_connected = supabase_client.connect()
        if supabase_connected:
            logger.info("✅ Supabase connection established")
        else:
            logger.error("❌ Failed to connect to Supabase")
    except Exception as e:
        logger.error(f"❌ Supabase connection error: {str(e)}")

    logger.info("🚀 Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application...")

    # Close Elasticsearch connection
    try:
        await es_client.disconnect()
        logger.info("✅ Elasticsearch connection closed")
    except Exception as e:
        logger.error(f"❌ Error closing Elasticsearch connection: {str(e)}")

    # Close Supabase connection
    try:
        supabase_client.disconnect()
        logger.info("✅ Supabase connection closed")
    except Exception as e:
        logger.error(f"❌ Error closing Supabase connection: {str(e)}")

    logger.info("👋 Application shutdown complete")


async def health_check() -> dict:
    """
    Perform health check on all database connections

    Returns:
        Dict with health status of each service
    """
    health_status = {
        "status": "healthy",
        "services": {}
    }

    # Check Elasticsearch
    try:
        es_healthy = await es_client.health_check()
        health_status["services"]["elasticsearch"] = {
            "status": "healthy" if es_healthy else "unhealthy",
            "connected": es_healthy
        }
    except Exception as e:
        health_status["services"]["elasticsearch"] = {
            "status": "unhealthy",
            "error": str(e)
        }

    # Check Supabase
    try:
        # Simple connection test
        supabase_healthy = supabase_client.client is not None
        health_status["services"]["supabase"] = {
            "status": "healthy" if supabase_healthy else "unhealthy",
            "connected": supabase_healthy
        }
    except Exception as e:
        health_status["services"]["supabase"] = {
            "status": "unhealthy",
            "error": str(e)
        }

    # Determine overall health
    all_healthy = all(
        service.get("status") == "healthy"
        for service in health_status["services"].values()
    )

    if not all_healthy:
        health_status["status"] = "unhealthy"

    return health_status