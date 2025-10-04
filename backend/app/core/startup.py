"""
Application startup and initialization for Planning Explorer AI-enhanced backend

Handles initialization of AI services, background processors, cache management,
and other components required for the full AI intelligence layer.
"""

import asyncio
import logging
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI

logger = logging.getLogger(__name__)


class StartupManager:
    """Manages application startup and shutdown sequences"""

    def __init__(self):
        self.ai_processor_initialized = False
        self.background_processor_started = False
        self.cache_manager_started = False

    async def initialize_ai_services(self) -> bool:
        """Initialize AI processing services"""
        try:
            from app.services.ai_processor import ai_processor

            # AI processor initializes components in its constructor
            # Just verify it's working
            health_status = await ai_processor.health_check()
            if health_status["overall_health"] in ["healthy", "degraded"]:
                self.ai_processor_initialized = True
                logger.info("AI processing services initialized successfully")

                # Log available components
                components = health_status["components"]
                available_count = sum(1 for status in components.values() if status == "healthy")
                logger.info(f"AI components available: {available_count}/5")

                return True
            else:
                logger.warning("AI processing services initialized with issues")
                return False

        except Exception as e:
            logger.error(f"Failed to initialize AI services: {str(e)}")
            return False

    async def start_background_processing(self) -> bool:
        """Start background processing services"""
        try:
            from app.services.background_processor import background_processor

            await background_processor.start_workers()
            self.background_processor_started = True
            logger.info("Background processing services started")
            return True

        except Exception as e:
            logger.error(f"Failed to start background processing: {str(e)}")
            return False

    async def start_cache_manager(self) -> bool:
        """Start intelligent cache management"""
        try:
            from app.services.cache_manager import cache_manager

            await cache_manager.start()
            self.cache_manager_started = True
            logger.info("Cache management services started")
            return True

        except Exception as e:
            logger.error(f"Failed to start cache manager: {str(e)}")
            return False

    async def initialize_all(self) -> dict:
        """Initialize all AI and supporting services"""
        logger.info("Starting Planning Explorer AI Intelligence Layer initialization...")

        results = {
            "ai_services": await self.initialize_ai_services(),
            "background_processing": await self.start_background_processing(),
            "cache_management": await self.start_cache_manager()
        }

        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)

        if success_count == total_count:
            logger.info("🚀 AI Intelligence Layer fully operational - all services started successfully")
        elif success_count > 0:
            logger.warning(f"⚠️ AI Intelligence Layer partially operational - {success_count}/{total_count} services started")
        else:
            logger.error("❌ AI Intelligence Layer failed to start - no services available")

        return results

    async def shutdown_all(self) -> None:
        """Shutdown all services gracefully"""
        logger.info("Shutting down AI Intelligence Layer services...")

        # Shutdown in reverse order
        if self.cache_manager_started:
            try:
                from app.services.cache_manager import cache_manager
                await cache_manager.stop()
                logger.info("Cache manager stopped")
            except Exception as e:
                logger.error(f"Error stopping cache manager: {str(e)}")

        if self.background_processor_started:
            try:
                from app.services.background_processor import background_processor
                await background_processor.stop_workers()
                logger.info("Background processor stopped")
            except Exception as e:
                logger.error(f"Error stopping background processor: {str(e)}")

        logger.info("AI Intelligence Layer shutdown complete")

    def get_initialization_status(self) -> dict:
        """Get current initialization status"""
        return {
            "ai_processor": self.ai_processor_initialized,
            "background_processor": self.background_processor_started,
            "cache_manager": self.cache_manager_started,
            "overall_status": "operational" if all([
                self.ai_processor_initialized,
                self.background_processor_started,
                self.cache_manager_started
            ]) else "partial" if any([
                self.ai_processor_initialized,
                self.background_processor_started,
                self.cache_manager_started
            ]) else "failed"
        }


# Global startup manager instance
startup_manager = StartupManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager for startup/shutdown"""
    # Startup
    try:
        initialization_results = await startup_manager.initialize_all()
        app.state.ai_initialization = initialization_results
        app.state.startup_manager = startup_manager
        logger.info("Application startup complete")
        yield
    finally:
        # Shutdown
        await startup_manager.shutdown_all()
        logger.info("Application shutdown complete")


def get_startup_info() -> dict:
    """Get information about the startup process and AI capabilities"""
    try:
        from app.services.ai_processor import ai_processor
        from app.services.background_processor import background_processor
        from app.services.cache_manager import cache_manager

        return {
            "startup_status": startup_manager.get_initialization_status(),
            "ai_capabilities": {
                "opportunity_scoring": bool(ai_processor.opportunity_scorer),
                "document_summarization": bool(ai_processor.document_summarizer),
                "vector_embeddings": bool(ai_processor.embedding_service),
                "natural_language_processing": bool(ai_processor.nlp_processor),
                "market_intelligence": bool(ai_processor.market_intelligence)
            },
            "service_statistics": {
                "ai_processor": ai_processor.get_service_status()["statistics"],
                "background_processor": background_processor.get_service_stats(),
                "cache_manager": cache_manager.get_stats()
            },
            "performance_features": {
                "intelligent_caching": startup_manager.cache_manager_started,
                "background_processing": startup_manager.background_processor_started,
                "batch_operations": startup_manager.background_processor_started,
                "semantic_search": bool(ai_processor.embedding_service),
                "natural_language_queries": bool(ai_processor.nlp_processor)
            }
        }

    except Exception as e:
        logger.error(f"Error getting startup info: {str(e)}")
        return {
            "startup_status": startup_manager.get_initialization_status(),
            "error": str(e)
        }