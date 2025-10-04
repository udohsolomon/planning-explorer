"""
Main AI Processing Service Orchestrator for Planning Explorer

This service coordinates all AI processing components including opportunity scoring,
document summarization, vector embeddings, natural language processing, and
market intelligence to provide comprehensive AI-powered planning insights.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json
import numpy as np

from app.core.ai_config import ai_config, AIModel, AIProvider
from app.ai.opportunity_scorer import OpportunityScorer, ScoringResult
from app.ai.summarizer import DocumentSummarizer, SummaryResult, SummaryType, SummaryLength
from app.ai.embeddings import EmbeddingService, EmbeddingResult, EmbeddingType, SemanticSearchResult
from app.ai.nlp_processor import NLPProcessor, ParsedQuery, QueryIntent
from app.ai.market_intelligence import MarketIntelligenceEngine, MarketIntelligenceReport, AnalysisPeriod
from app.models.planning import PlanningApplication

logger = logging.getLogger(__name__)


class ProcessingMode(str, Enum):
    """AI processing modes"""
    FAST = "fast"           # Quick processing with basic AI features
    STANDARD = "standard"   # Balanced processing with most features
    COMPREHENSIVE = "comprehensive"  # Full AI analysis with all features
    BATCH = "batch"         # Optimized for batch processing


class ProcessingPriority(str, Enum):
    """Processing priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class ProcessingRequest:
    """Request for AI processing"""
    request_id: str
    application_ids: List[str]
    processing_mode: ProcessingMode
    priority: ProcessingPriority
    features: List[str]  # Specific features to enable
    context: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    callback_url: Optional[str] = None


@dataclass
class ProcessingResult:
    """Result of AI processing"""
    request_id: str
    application_id: str
    processing_mode: ProcessingMode
    features_processed: List[str]
    results: Dict[str, Any]
    processing_time_ms: int
    success: bool
    errors: List[str]
    warnings: List[str]
    confidence_scores: Dict[str, float]
    generated_at: datetime


@dataclass
class BatchProcessingResult:
    """Result of batch AI processing"""
    request_id: str
    total_applications: int
    successful_count: int
    failed_count: int
    processing_time_ms: int
    results: List[ProcessingResult]
    summary_stats: Dict[str, Any]
    generated_at: datetime


class AIProcessor:
    """
    Main AI processing service that orchestrates all AI components.

    Provides a unified interface for AI processing with intelligent
    resource management, caching, and performance optimization.
    """

    def __init__(self):
        self.config = ai_config
        self._initialize_components()
        self._processing_queue = asyncio.Queue()
        self._active_requests = {}
        self._stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_processing_time": 0,
            "cache_hits": 0
        }

    def _initialize_components(self) -> None:
        """Initialize AI processing components"""
        try:
            self.opportunity_scorer = OpportunityScorer()
            logger.info("Opportunity scorer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize opportunity scorer: {e}")
            self.opportunity_scorer = None

        try:
            self.document_summarizer = DocumentSummarizer()
            logger.info("Document summarizer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize document summarizer: {e}")
            self.document_summarizer = None

        try:
            self.embedding_service = EmbeddingService()
            logger.info("Embedding service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize embedding service: {e}")
            self.embedding_service = None

        try:
            self.nlp_processor = NLPProcessor()
            logger.info("NLP processor initialized")
        except Exception as e:
            logger.error(f"Failed to initialize NLP processor: {e}")
            self.nlp_processor = None

        try:
            self.market_intelligence = MarketIntelligenceEngine()
            logger.info("Market intelligence engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize market intelligence: {e}")
            self.market_intelligence = None

        # Check if any components are available
        available_components = sum([
            bool(self.opportunity_scorer),
            bool(self.document_summarizer),
            bool(self.embedding_service),
            bool(self.nlp_processor),
            bool(self.market_intelligence)
        ])

        if available_components == 0:
            logger.error("No AI components available - all processing will use fallbacks")
        else:
            logger.info(f"AI Processor initialized with {available_components}/5 components available")

    async def process_application(
        self,
        application: PlanningApplication,
        processing_mode: ProcessingMode = ProcessingMode.STANDARD,
        features: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ProcessingResult:
        """
        Process a single planning application with AI features.

        Args:
            application: Planning application to process
            processing_mode: Processing mode (fast, standard, comprehensive)
            features: Specific features to enable
            context: Additional context for processing

        Returns:
            ProcessingResult with AI analysis results
        """
        request_id = f"single_{application.application_id}_{int(time.time())}"
        start_time = time.time()

        try:
            # Determine features to process
            enabled_features = self._determine_features(processing_mode, features)

            # Check intelligent cache
            cache_key = self._generate_cache_key(application.application_id, enabled_features)

            try:
                from app.services.cache_manager import cache_manager, CacheType, CacheLevel

                cached_result = await cache_manager.get(cache_key, CacheType.AI_PROCESSING)
                if cached_result:
                    self._stats["cache_hits"] += 1
                    logger.debug(f"Cache hit for application {application.application_id}")
                    return cached_result
            except ImportError:
                logger.warning("Cache manager not available, using fallback caching")
                # Fallback to simple in-memory cache
                if hasattr(self, '_simple_cache') and cache_key in self._simple_cache:
                    cached_result = self._simple_cache[cache_key]
                    self._stats["cache_hits"] += 1
                    logger.debug(f"Simple cache hit for application {application.application_id}")
                    return cached_result

            # Process features
            results = {}
            errors = []
            warnings = []
            confidence_scores = {}

            # Opportunity Scoring
            if "opportunity_scoring" in enabled_features and self.opportunity_scorer:
                try:
                    scoring_result = await self.opportunity_scorer.score_application(application, context)
                    results["opportunity_scoring"] = {
                        "opportunity_score": scoring_result.opportunity_score,
                        "approval_probability": scoring_result.approval_probability,
                        "confidence_score": scoring_result.confidence_score,
                        "breakdown": scoring_result.breakdown,
                        "rationale": scoring_result.rationale,
                        "risk_factors": scoring_result.risk_factors,
                        "recommendations": scoring_result.recommendations
                    }
                    confidence_scores["opportunity_scoring"] = scoring_result.confidence_score
                except Exception as e:
                    errors.append(f"Opportunity scoring failed: {str(e)}")
                    logger.error(f"Opportunity scoring error for {application.application_id}: {e}")

            # Document Summarization
            if "summarization" in enabled_features and self.document_summarizer:
                try:
                    summary_type = SummaryType.GENERAL
                    summary_length = SummaryLength.MEDIUM

                    if processing_mode == ProcessingMode.FAST:
                        summary_length = SummaryLength.SHORT
                    elif processing_mode == ProcessingMode.COMPREHENSIVE:
                        summary_length = SummaryLength.LONG

                    summary_result = await self.document_summarizer.summarize_application(
                        application, summary_type, summary_length
                    )
                    results["summarization"] = {
                        "summary": summary_result.summary,
                        "key_points": summary_result.key_points,
                        "sentiment": summary_result.sentiment,
                        "complexity_score": summary_result.complexity_score,
                        "recommendations": summary_result.recommendations
                    }
                    confidence_scores["summarization"] = summary_result.confidence_score
                except Exception as e:
                    errors.append(f"Summarization failed: {str(e)}")
                    logger.error(f"Summarization error for {application.application_id}: {e}")

            # Vector Embeddings
            if "embeddings" in enabled_features and self.embedding_service:
                try:
                    embedding_result = await self.embedding_service.generate_application_embedding(
                        application, EmbeddingType.COMBINED
                    )
                    results["embeddings"] = {
                        "dimensions": embedding_result.dimensions,
                        "model_used": embedding_result.model_used,
                        "confidence_score": embedding_result.confidence_score,
                        "metadata": embedding_result.metadata
                    }
                    # Store full embedding for similarity searches (not in API response)
                    results["embeddings"]["_vector"] = embedding_result.embedding
                    confidence_scores["embeddings"] = embedding_result.confidence_score
                except Exception as e:
                    errors.append(f"Embedding generation failed: {str(e)}")
                    logger.error(f"Embedding error for {application.application_id}: {e}")

            # Market Context (lightweight)
            if "market_context" in enabled_features:
                try:
                    market_context = await self._generate_market_context(application)
                    results["market_context"] = market_context
                    confidence_scores["market_context"] = 0.7  # Default confidence
                except Exception as e:
                    warnings.append(f"Market context generation had issues: {str(e)}")

            # Calculate overall confidence
            overall_confidence = np.mean(list(confidence_scores.values())) if confidence_scores else 0.5

            processing_time_ms = int((time.time() - start_time) * 1000)

            result = ProcessingResult(
                request_id=request_id,
                application_id=application.application_id,
                processing_mode=processing_mode,
                features_processed=list(results.keys()),
                results=results,
                processing_time_ms=processing_time_ms,
                success=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                confidence_scores=confidence_scores,
                generated_at=datetime.utcnow()
            )

            # Cache successful results intelligently
            if result.success:
                try:
                    from app.services.cache_manager import cache_manager, CacheType, CacheLevel

                    # Determine cache TTL based on processing mode and features
                    ttl_hours = 24  # Default
                    cache_level = CacheLevel.NORMAL

                    if processing_mode == ProcessingMode.COMPREHENSIVE:
                        ttl_hours = 48  # Cache comprehensive results longer
                        cache_level = CacheLevel.HIGH
                    elif "embeddings" in enabled_features:
                        ttl_hours = 72  # Cache embeddings longer
                        cache_level = CacheLevel.HIGH

                    await cache_manager.set(
                        cache_key,
                        result,
                        CacheType.AI_PROCESSING,
                        ttl_hours=ttl_hours,
                        level=cache_level,
                        metadata={
                            "application_id": application.application_id,
                            "features": enabled_features,
                            "processing_mode": processing_mode.value
                        }
                    )
                except ImportError:
                    # Fallback to simple caching
                    if not hasattr(self, '_simple_cache'):
                        self._simple_cache = {}
                    self._simple_cache[cache_key] = result

            # Update statistics
            self._stats["total_requests"] += 1
            if result.success:
                self._stats["successful_requests"] += 1
            else:
                self._stats["failed_requests"] += 1

            self._update_average_processing_time(processing_time_ms)

            logger.info(f"Processed application {application.application_id} in {processing_time_ms}ms with {len(enabled_features)} features")
            return result

        except Exception as e:
            logger.error(f"Critical error processing application {application.application_id}: {str(e)}")
            return self._generate_error_result(request_id, application.application_id, processing_mode, str(e))

    async def process_batch(
        self,
        applications: List[PlanningApplication],
        processing_mode: ProcessingMode = ProcessingMode.BATCH,
        features: Optional[List[str]] = None,
        max_concurrent: int = 10,
        context: Optional[Dict[str, Any]] = None
    ) -> BatchProcessingResult:
        """
        Process multiple applications in batch with optimized performance.

        Args:
            applications: List of applications to process
            processing_mode: Processing mode
            features: Features to enable
            max_concurrent: Maximum concurrent processing tasks
            context: Additional context

        Returns:
            BatchProcessingResult with all results
        """
        request_id = f"batch_{len(applications)}_{int(time.time())}"
        start_time = time.time()

        try:
            # Determine features for batch mode
            enabled_features = self._determine_features(processing_mode, features)

            # Process applications concurrently
            semaphore = asyncio.Semaphore(max_concurrent)

            async def process_with_semaphore(app):
                async with semaphore:
                    return await self.process_application(app, processing_mode, enabled_features, context)

            tasks = [process_with_semaphore(app) for app in applications]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            processed_results = []
            successful_count = 0
            failed_count = 0

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Batch processing error for application {applications[i].application_id}: {result}")
                    error_result = self._generate_error_result(
                        f"{request_id}_{i}",
                        applications[i].application_id,
                        processing_mode,
                        str(result)
                    )
                    processed_results.append(error_result)
                    failed_count += 1
                else:
                    processed_results.append(result)
                    if result.success:
                        successful_count += 1
                    else:
                        failed_count += 1

            processing_time_ms = int((time.time() - start_time) * 1000)

            # Generate summary statistics
            summary_stats = self._generate_batch_summary_stats(processed_results)

            batch_result = BatchProcessingResult(
                request_id=request_id,
                total_applications=len(applications),
                successful_count=successful_count,
                failed_count=failed_count,
                processing_time_ms=processing_time_ms,
                results=processed_results,
                summary_stats=summary_stats,
                generated_at=datetime.utcnow()
            )

            logger.info(f"Batch processed {len(applications)} applications in {processing_time_ms}ms "
                       f"({successful_count} successful, {failed_count} failed)")

            return batch_result

        except Exception as e:
            logger.error(f"Critical error in batch processing: {str(e)}")
            return BatchProcessingResult(
                request_id=request_id,
                total_applications=len(applications),
                successful_count=0,
                failed_count=len(applications),
                processing_time_ms=int((time.time() - start_time) * 1000),
                results=[],
                summary_stats={"error": str(e)},
                generated_at=datetime.utcnow()
            )

    async def process_natural_language_query(
        self,
        query: str,
        applications: List[PlanningApplication],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process natural language query against planning applications.

        Args:
            query: Natural language query
            applications: Applications to search
            context: Additional context

        Returns:
            Query results with AI-enhanced search
        """
        start_time = time.time()

        try:
            if not self.nlp_processor:
                # Fallback to simple text search
                return await self._fallback_text_search(query, applications)

            # Process query with NLP
            parsed_query = await self.nlp_processor.process_query(query, context)

            # Perform semantic search if embeddings available
            semantic_results = None
            if self.embedding_service and len(applications) > 0:
                try:
                    semantic_results = await self.embedding_service.semantic_search(
                        query, applications[:100]  # Limit for performance
                    )
                except Exception as e:
                    logger.warning(f"Semantic search failed, using parsed query: {e}")

            processing_time_ms = int((time.time() - start_time) * 1000)

            return {
                "original_query": query,
                "parsed_query": {
                    "intent": parsed_query.intent.value,
                    "query_type": parsed_query.query_type.value,
                    "confidence": parsed_query.confidence_score,
                    "suggestions": parsed_query.suggestions
                },
                "elasticsearch_query": parsed_query.elasticsearch_query,
                "semantic_results": {
                    "total_results": len(semantic_results.results) if semantic_results else 0,
                    "results": semantic_results.results[:10] if semantic_results else [],
                    "model_used": semantic_results.model_used if semantic_results else None
                } if semantic_results else None,
                "processing_time_ms": processing_time_ms,
                "enhanced_features_available": bool(self.embedding_service)
            }

        except Exception as e:
            logger.error(f"Error processing natural language query: {str(e)}")
            return await self._fallback_text_search(query, applications)

    async def generate_market_intelligence(
        self,
        applications: List[PlanningApplication],
        analysis_period: AnalysisPeriod = AnalysisPeriod.LAST_YEAR,
        geographical_scope: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive market intelligence report.

        Args:
            applications: Applications for analysis
            analysis_period: Time period for analysis
            geographical_scope: Geographic area to focus on

        Returns:
            Market intelligence report
        """
        start_time = time.time()

        try:
            if not self.market_intelligence:
                return self._generate_basic_market_stats(applications)

            report = await self.market_intelligence.generate_market_intelligence(
                applications, analysis_period, geographical_scope=geographical_scope
            )

            processing_time_ms = int((time.time() - start_time) * 1000)

            return {
                "analysis_period": report.analysis_period.value,
                "market_overview": report.market_overview,
                "trends": [
                    {
                        "metric": trend.metric,
                        "direction": trend.trend_direction.value,
                        "change_percentage": trend.change_percentage,
                        "confidence": trend.confidence_score,
                        "insights": trend.insights
                    }
                    for trend in report.trend_analyses
                ],
                "market_metrics": {
                    segment.value: {
                        "total_applications": metrics.total_applications,
                        "approval_rate": metrics.approval_rate,
                        "processing_time": metrics.average_processing_time,
                        "volume_trend": metrics.application_volume_trend.value,
                        "approval_trend": metrics.approval_rate_trend.value
                    }
                    for segment, metrics in report.market_metrics.items()
                },
                "opportunities": [
                    {
                        "title": opp.title,
                        "description": opp.description,
                        "growth_potential": opp.growth_potential,
                        "success_probability": opp.success_probability,
                        "recommendations": opp.recommendations
                    }
                    for opp in report.opportunities
                ],
                "risks": report.risks,
                "recommendations": report.recommendations,
                "data_quality_score": report.data_quality_score,
                "processing_time_ms": processing_time_ms,
                "generated_at": report.generated_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Error generating market intelligence: {str(e)}")
            return self._generate_basic_market_stats(applications)

    def _determine_features(self, processing_mode: ProcessingMode, custom_features: Optional[List[str]]) -> List[str]:
        """Determine which features to enable based on mode and availability"""
        if custom_features:
            return custom_features

        feature_sets = {
            ProcessingMode.FAST: ["opportunity_scoring"],
            ProcessingMode.STANDARD: ["opportunity_scoring", "summarization", "market_context"],
            ProcessingMode.COMPREHENSIVE: ["opportunity_scoring", "summarization", "embeddings", "market_context"],
            ProcessingMode.BATCH: ["opportunity_scoring", "embeddings"]  # Optimized for batch
        }

        base_features = feature_sets.get(processing_mode, ["opportunity_scoring"])

        # Filter by component availability
        available_features = []
        for feature in base_features:
            if feature == "opportunity_scoring" and self.opportunity_scorer:
                available_features.append(feature)
            elif feature == "summarization" and self.document_summarizer:
                available_features.append(feature)
            elif feature == "embeddings" and self.embedding_service:
                available_features.append(feature)
            elif feature == "market_context":  # Always available (basic version)
                available_features.append(feature)

        return available_features or ["basic_analysis"]  # Fallback

    def _generate_cache_key(self, application_id: str, features: List[str]) -> str:
        """Generate cache key for application and features"""
        features_str = "_".join(sorted(features))
        return f"{application_id}_{features_str}"

    async def _generate_market_context(self, application: PlanningApplication) -> Dict[str, Any]:
        """Generate basic market context for an application"""
        return {
            "development_type": application.development_type,
            "authority": application.authority,
            "location": application.address,
            "status": application.status,
            "context_type": "basic",
            "insights": [
                f"This is a {application.development_type} development",
                f"Being processed by {application.authority}",
                f"Current status: {application.status}"
            ]
        }

    def _generate_batch_summary_stats(self, results: List[ProcessingResult]) -> Dict[str, Any]:
        """Generate summary statistics for batch processing"""
        if not results:
            return {}

        # Processing time statistics
        processing_times = [r.processing_time_ms for r in results]

        # Feature usage statistics
        feature_usage = {}
        for result in results:
            for feature in result.features_processed:
                feature_usage[feature] = feature_usage.get(feature, 0) + 1

        # Confidence score statistics
        all_confidence_scores = []
        for result in results:
            all_confidence_scores.extend(result.confidence_scores.values())

        return {
            "processing_time_stats": {
                "min_ms": min(processing_times) if processing_times else 0,
                "max_ms": max(processing_times) if processing_times else 0,
                "avg_ms": np.mean(processing_times) if processing_times else 0,
                "total_ms": sum(processing_times)
            },
            "feature_usage": feature_usage,
            "confidence_stats": {
                "avg_confidence": np.mean(all_confidence_scores) if all_confidence_scores else 0,
                "min_confidence": min(all_confidence_scores) if all_confidence_scores else 0,
                "max_confidence": max(all_confidence_scores) if all_confidence_scores else 0
            },
            "success_rate": len([r for r in results if r.success]) / len(results) if results else 0
        }

    def _generate_error_result(
        self,
        request_id: str,
        application_id: str,
        processing_mode: ProcessingMode,
        error_message: str
    ) -> ProcessingResult:
        """Generate error result for failed processing"""
        return ProcessingResult(
            request_id=request_id,
            application_id=application_id,
            processing_mode=processing_mode,
            features_processed=[],
            results={},
            processing_time_ms=0,
            success=False,
            errors=[error_message],
            warnings=[],
            confidence_scores={},
            generated_at=datetime.utcnow()
        )

    async def _fallback_text_search(self, query: str, applications: List[PlanningApplication]) -> Dict[str, Any]:
        """Fallback text search when NLP processing is unavailable"""
        query_lower = query.lower()
        matches = []

        for app in applications:
            description = (app.description or "").lower()
            address = (app.address or "").lower()
            dev_type = (app.development_type or "").lower()

            if (query_lower in description or
                query_lower in address or
                query_lower in dev_type):
                matches.append({
                    "application_id": app.application_id,
                    "relevance_score": 0.5,  # Basic relevance
                    "match_type": "text_search"
                })

        return {
            "original_query": query,
            "search_type": "fallback_text_search",
            "total_results": len(matches),
            "results": matches[:20],  # Limit results
            "elasticsearch_query": {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["description", "address", "development_type"]
                    }
                }
            },
            "processing_time_ms": 10,
            "enhanced_features_available": False
        }

    def _generate_basic_market_stats(self, applications: List[PlanningApplication]) -> Dict[str, Any]:
        """Generate basic market statistics when full intelligence is unavailable"""
        if not applications:
            return {"total_applications": 0, "status": "no_data"}

        # Basic statistics
        total_apps = len(applications)
        approved = len([app for app in applications if app.status == "approved"])
        refused = len([app for app in applications if app.status == "refused"])

        # Development types
        dev_types = {}
        for app in applications:
            if app.development_type:
                dev_types[app.development_type] = dev_types.get(app.development_type, 0) + 1

        return {
            "total_applications": total_apps,
            "approval_rate": approved / max(1, approved + refused),
            "development_type_distribution": dev_types,
            "analysis_type": "basic_statistics",
            "recommendations": ["Enable full market intelligence for comprehensive analysis"],
            "processing_time_ms": 50
        }

    def _update_average_processing_time(self, new_time: int) -> None:
        """Update running average of processing times"""
        current_avg = self._stats["average_processing_time"]
        total_requests = self._stats["total_requests"]

        self._stats["average_processing_time"] = (
            (current_avg * (total_requests - 1) + new_time) / total_requests
        )

    def get_service_status(self) -> Dict[str, Any]:
        """Get status of AI processing service"""
        return {
            "service_name": "AI Processor",
            "status": "operational",
            "components": {
                "opportunity_scorer": bool(self.opportunity_scorer),
                "document_summarizer": bool(self.document_summarizer),
                "embedding_service": bool(self.embedding_service),
                "nlp_processor": bool(self.nlp_processor),
                "market_intelligence": bool(self.market_intelligence)
            },
            "statistics": self._stats,
            "configuration": self.config.to_dict(),
            "cache_size": len(self._cache),
            "queue_size": self._processing_queue.qsize()
        }

    def clear_cache(self) -> None:
        """Clear processing cache"""
        self._cache.clear()
        logger.info("AI processor cache cleared")

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all AI components"""
        health_status = {
            "overall_health": "healthy",
            "components": {},
            "timestamp": datetime.utcnow().isoformat()
        }

        # Test each component
        try:
            if self.opportunity_scorer:
                health_status["components"]["opportunity_scorer"] = "healthy"
            else:
                health_status["components"]["opportunity_scorer"] = "unavailable"

            if self.document_summarizer:
                health_status["components"]["document_summarizer"] = "healthy"
            else:
                health_status["components"]["document_summarizer"] = "unavailable"

            if self.embedding_service:
                health_status["components"]["embedding_service"] = "healthy"
            else:
                health_status["components"]["embedding_service"] = "unavailable"

            if self.nlp_processor:
                health_status["components"]["nlp_processor"] = "healthy"
            else:
                health_status["components"]["nlp_processor"] = "unavailable"

            if self.market_intelligence:
                health_status["components"]["market_intelligence"] = "healthy"
            else:
                health_status["components"]["market_intelligence"] = "unavailable"

        except Exception as e:
            health_status["overall_health"] = "degraded"
            health_status["error"] = str(e)

        # Check if any critical components are missing
        available_components = sum(1 for status in health_status["components"].values()
                                 if status == "healthy")

        if available_components == 0:
            health_status["overall_health"] = "critical"
        elif available_components < 3:
            health_status["overall_health"] = "degraded"

        return health_status


# Global AI processor instance
ai_processor = AIProcessor()