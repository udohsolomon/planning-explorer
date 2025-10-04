#!/usr/bin/env python3
"""
Continuous Embedding Pipeline for Planning Explorer

This module provides automated, incremental embedding generation for new and
updated planning applications as they are added to Elasticsearch.

Design Approaches:
1. **Scheduled Batch Processing**: Periodic processing of new/updated documents
2. **Event-Driven Processing**: Real-time embedding on document creation/update
3. **Hybrid Approach**: Scheduled for bulk + event-driven for critical updates

Recommended: Hybrid approach for optimal balance of cost, latency, and completeness
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
import json

from app.db.elasticsearch import es_client
from app.ai.embeddings import EmbeddingService


logger = logging.getLogger(__name__)


class PipelineMode(str, Enum):
    """Pipeline execution modes"""
    SCHEDULED = "scheduled"          # Run on schedule (e.g., hourly, daily)
    EVENT_DRIVEN = "event_driven"    # Process on document events
    HYBRID = "hybrid"                # Combination of both
    BACKFILL = "backfill"           # One-time backfill for missing embeddings


class ProcessingPriority(str, Enum):
    """Document processing priority levels"""
    CRITICAL = "critical"    # Recent, high-value applications (< 24h old)
    HIGH = "high"           # Recent applications (< 7 days)
    NORMAL = "normal"       # Standard processing (< 30 days)
    LOW = "low"            # Older applications (> 30 days)


@dataclass
class PipelineConfig:
    """Configuration for continuous embedding pipeline"""

    # Scheduling configuration
    schedule_interval_minutes: int = 60  # Run every hour
    batch_size: int = 100
    max_concurrent_batches: int = 3

    # Processing windows
    process_recent_hours: int = 24  # Process docs from last 24 hours
    process_updated_hours: int = 24  # Process updated docs from last 24 hours

    # Rate limiting
    rate_limit_delay: float = 0.5  # 500 RPM OpenAI compliance
    max_retries: int = 3

    # Priority thresholds
    critical_age_hours: int = 24
    high_priority_age_days: int = 7
    normal_priority_age_days: int = 30

    # Cost management
    daily_cost_limit_usd: float = 10.0  # Max $10/day
    pause_on_limit: bool = True

    # Monitoring
    enable_metrics: bool = True
    alert_on_failures: bool = True
    failure_threshold: int = 10  # Alert after 10 consecutive failures


class ContinuousEmbeddingPipeline:
    """
    Continuous embedding pipeline that automatically processes new and updated
    planning applications as they arrive in Elasticsearch.

    Features:
    - Incremental processing of new documents
    - Detection and reprocessing of updated documents
    - Priority-based processing queue
    - Cost tracking and budget management
    - Failure handling and retry logic
    - Performance metrics and monitoring
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self.embedding_service = EmbeddingService()
        self.logger = logging.getLogger(__name__)

        # State tracking
        self.is_running = False
        self.last_run_time: Optional[datetime] = None
        self.daily_cost_usd: float = 0.0
        self.daily_cost_reset_date: str = datetime.now().date().isoformat()
        self.consecutive_failures: int = 0

        # Metrics
        self.metrics = {
            "documents_processed": 0,
            "embeddings_generated": 0,
            "total_cost_usd": 0.0,
            "average_processing_time_ms": 0.0,
            "failure_count": 0,
            "last_run_timestamp": None
        }

    async def start_scheduled_pipeline(self):
        """
        Start the continuous embedding pipeline in scheduled mode.
        Runs periodically based on configuration.
        """
        self.logger.info(f"🚀 Starting continuous embedding pipeline (scheduled mode)")
        self.logger.info(f"📋 Schedule: Every {self.config.schedule_interval_minutes} minutes")
        self.logger.info(f"📦 Batch size: {self.config.batch_size}")
        self.logger.info(f"💰 Daily cost limit: ${self.config.daily_cost_limit_usd}")

        self.is_running = True

        while self.is_running:
            try:
                # Check daily cost limit
                await self._check_daily_cost_limit()

                # Run embedding generation cycle
                await self._run_generation_cycle()

                # Wait for next scheduled run
                self.logger.info(f"⏳ Waiting {self.config.schedule_interval_minutes} minutes until next run")
                await asyncio.sleep(self.config.schedule_interval_minutes * 60)

            except Exception as e:
                self.logger.error(f"❌ Error in pipeline cycle: {str(e)}")
                self.consecutive_failures += 1

                if self.consecutive_failures >= self.config.failure_threshold:
                    self.logger.error(f"🚨 Pipeline stopped: {self.consecutive_failures} consecutive failures")
                    break

                # Exponential backoff on failures
                backoff_time = min(300, 30 * (2 ** self.consecutive_failures))
                self.logger.info(f"⏳ Backing off for {backoff_time} seconds")
                await asyncio.sleep(backoff_time)

    async def _run_generation_cycle(self):
        """Execute one cycle of embedding generation"""
        self.logger.info("🔄 Starting embedding generation cycle")
        start_time = time.time()

        try:
            # 0. Ensure ES client is connected
            if not es_client.client:
                await es_client.connect()
                self.logger.info("✅ Connected to Elasticsearch")

            # 1. Get documents needing embeddings (prioritized)
            documents_by_priority = await self._get_documents_by_priority()

            total_processed = 0
            total_generated = 0

            # 2. Process by priority (critical first, then high, normal, low)
            for priority in [ProcessingPriority.CRITICAL, ProcessingPriority.HIGH,
                           ProcessingPriority.NORMAL, ProcessingPriority.LOW]:

                docs = documents_by_priority.get(priority, [])
                if not docs:
                    continue

                self.logger.info(f"📊 Processing {len(docs)} {priority.value} priority documents")

                # Process in batches
                for i in range(0, len(docs), self.config.batch_size):
                    batch = docs[i:i + self.config.batch_size]

                    processed, generated = await self._process_batch(batch, priority)
                    total_processed += processed
                    total_generated += generated

                    # Check cost limit between batches
                    if await self._check_daily_cost_limit():
                        self.logger.warning("💰 Daily cost limit reached, stopping cycle")
                        return

            # 3. Update metrics
            cycle_time = time.time() - start_time
            self.metrics["documents_processed"] += total_processed
            self.metrics["embeddings_generated"] += total_generated
            self.metrics["last_run_timestamp"] = datetime.now().isoformat()

            self.consecutive_failures = 0  # Reset on success
            self.last_run_time = datetime.now()

            self.logger.info(f"✅ Cycle complete: {total_processed} docs, {total_generated} embeddings in {cycle_time:.1f}s")

        except Exception as e:
            self.logger.error(f"❌ Error in generation cycle: {str(e)}")
            raise

    async def _get_documents_by_priority(self) -> Dict[ProcessingPriority, List[Dict[str, Any]]]:
        """
        Get documents needing embeddings, organized by priority.

        Priority logic:
        - CRITICAL: Created in last 24 hours, no embedding
        - HIGH: Created in last 7 days or recently updated, no embedding
        - NORMAL: Created in last 30 days, no embedding
        - LOW: Older documents, no embedding
        """
        documents_by_priority = {
            ProcessingPriority.CRITICAL: [],
            ProcessingPriority.HIGH: [],
            ProcessingPriority.NORMAL: [],
            ProcessingPriority.LOW: []
        }

        now = datetime.now()

        # Base query: documents without embeddings
        base_query = {
            "bool": {
                "must_not": [
                    {"exists": {"field": "description_embedding"}}
                ],
                "must": [
                    {"exists": {"field": "description"}},
                    {"range": {"description": {"gte": 10}}}
                ]
            }
        }

        # Critical: Last 24 hours
        critical_cutoff = now - timedelta(hours=self.config.critical_age_hours)
        critical_query = {
            "bool": {
                **base_query["bool"],
                "filter": [
                    {"range": {"start_date": {"gte": critical_cutoff.isoformat()}}}
                ]
            }
        }

        critical_docs = await self._search_documents(critical_query, limit=self.config.batch_size * 2)
        documents_by_priority[ProcessingPriority.CRITICAL] = critical_docs

        # High: Last 7 days or recently updated
        high_cutoff = now - timedelta(days=self.config.high_priority_age_days)
        high_query = {
            "bool": {
                **base_query["bool"],
                "should": [
                    {"range": {"start_date": {"gte": high_cutoff.isoformat()}}},
                    {"range": {"last_changed": {"gte": critical_cutoff.isoformat()}}}
                ],
                "minimum_should_match": 1
            }
        }

        high_docs = await self._search_documents(high_query, limit=self.config.batch_size * 3)
        documents_by_priority[ProcessingPriority.HIGH] = high_docs

        # Normal: Last 30 days
        normal_cutoff = now - timedelta(days=self.config.normal_priority_age_days)
        normal_query = {
            "bool": {
                **base_query["bool"],
                "filter": [
                    {"range": {"start_date": {"gte": normal_cutoff.isoformat(), "lt": high_cutoff.isoformat()}}}
                ]
            }
        }

        normal_docs = await self._search_documents(normal_query, limit=self.config.batch_size * 5)
        documents_by_priority[ProcessingPriority.NORMAL] = normal_docs

        # Low: Older documents (limited to avoid overwhelming the system)
        low_query = {
            "bool": {
                **base_query["bool"],
                "filter": [
                    {"range": {"start_date": {"lt": normal_cutoff.isoformat()}}}
                ]
            }
        }

        low_docs = await self._search_documents(low_query, limit=self.config.batch_size)
        documents_by_priority[ProcessingPriority.LOW] = low_docs

        return documents_by_priority

    async def _search_documents(self, query: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """Search for documents matching query"""
        try:
            response = await es_client.client.search(
                index=es_client.index_name,
                query=query,
                size=limit,
                sort=[
                    {"start_date": {"order": "desc", "missing": "_last"}},
                    {"uid.keyword": {"order": "asc"}}  # Use uid instead of _id
                ],
                _source=["uid", "description", "start_date", "last_changed", "address", "authority"]
            )

            return response.get("hits", {}).get("hits", [])

        except Exception as e:
            self.logger.error(f"❌ Search error: {str(e)}")
            return []

    async def _process_batch(self, documents: List[Dict[str, Any]],
                            priority: ProcessingPriority) -> tuple[int, int]:
        """
        Process a batch of documents to generate embeddings.

        Returns:
            Tuple of (processed_count, generated_count)
        """
        processed = 0
        generated = 0

        for doc in documents:
            try:
                doc_id = doc["_id"]
                source = doc["_source"]
                description = source.get("description", "").strip()

                if not description or len(description) < 10:
                    continue

                # Generate embedding
                embedding_result = await self.embedding_service.generate_text_embedding(description)

                if embedding_result and embedding_result.embedding:
                    # Update document in ES
                    update_doc = {
                        "description_embedding": embedding_result.embedding,
                        "embedding_dimensions": len(embedding_result.embedding),
                        "embedding_model": embedding_result.model_used,
                        "embedding_generated_at": datetime.utcnow().isoformat(),
                        "embedding_text_hash": embedding_result.text_hash,
                        "embedding_confidence": embedding_result.confidence_score,
                        "embedding_priority": priority.value
                    }

                    success = await es_client.update_document(
                        doc_id=doc_id,
                        document=update_doc,
                        refresh=False
                    )

                    if success:
                        generated += 1

                        # Update cost tracking
                        cost = (embedding_result.token_count / 1000) * 0.00002
                        self.daily_cost_usd += cost
                        self.metrics["total_cost_usd"] += cost

                    processed += 1

                    # Rate limiting
                    await asyncio.sleep(self.config.rate_limit_delay)

            except Exception as e:
                self.logger.error(f"❌ Error processing document {doc.get('_id')}: {str(e)}")
                self.metrics["failure_count"] += 1

        return processed, generated

    async def _check_daily_cost_limit(self) -> bool:
        """
        Check if daily cost limit has been reached.

        Returns:
            True if limit reached, False otherwise
        """
        # Reset daily cost if new day
        today = datetime.now().date().isoformat()
        if today != self.daily_cost_reset_date:
            self.logger.info(f"📅 New day: Resetting daily cost (previous: ${self.daily_cost_usd:.4f})")
            self.daily_cost_usd = 0.0
            self.daily_cost_reset_date = today
            return False

        # Check limit
        if self.daily_cost_usd >= self.config.daily_cost_limit_usd:
            self.logger.warning(f"💰 Daily cost limit reached: ${self.daily_cost_usd:.4f} / ${self.config.daily_cost_limit_usd}")
            return True

        return False

    async def process_document_event(self, doc_id: str, event_type: str):
        """
        Process a single document event (for event-driven mode).

        Args:
            doc_id: Document ID
            event_type: Event type (created, updated, etc.)
        """
        self.logger.info(f"📨 Processing event: {event_type} for document {doc_id}")

        try:
            # Retrieve document from ES
            doc = await es_client.get_document(doc_id)

            if not doc:
                self.logger.warning(f"⚠️  Document {doc_id} not found")
                return

            # Generate embedding
            description = doc.get("description", "").strip()

            if description and len(description) >= 10:
                embedding_result = await self.embedding_service.generate_text_embedding(description)

                if embedding_result and embedding_result.embedding:
                    update_doc = {
                        "description_embedding": embedding_result.embedding,
                        "embedding_dimensions": len(embedding_result.embedding),
                        "embedding_model": embedding_result.model_used,
                        "embedding_generated_at": datetime.utcnow().isoformat(),
                        "embedding_text_hash": embedding_result.text_hash,
                        "embedding_confidence": embedding_result.confidence_score,
                        "embedding_event_type": event_type
                    }

                    await es_client.update_document(doc_id=doc_id, document=update_doc)
                    self.logger.info(f"✅ Generated embedding for {doc_id}")

        except Exception as e:
            self.logger.error(f"❌ Error processing event for {doc_id}: {str(e)}")

    def get_metrics(self) -> Dict[str, Any]:
        """Get pipeline metrics"""
        return {
            **self.metrics,
            "is_running": self.is_running,
            "last_run_time": self.last_run_time.isoformat() if self.last_run_time else None,
            "daily_cost_usd": self.daily_cost_usd,
            "consecutive_failures": self.consecutive_failures,
            "config": {
                "schedule_interval_minutes": self.config.schedule_interval_minutes,
                "batch_size": self.config.batch_size,
                "daily_cost_limit_usd": self.config.daily_cost_limit_usd
            }
        }

    def stop(self):
        """Stop the pipeline"""
        self.logger.info("🛑 Stopping continuous embedding pipeline")
        self.is_running = False


async def main():
    """Example usage of continuous embedding pipeline"""

    # Configure pipeline
    config = PipelineConfig(
        schedule_interval_minutes=60,  # Run every hour
        batch_size=100,
        daily_cost_limit_usd=5.0,
        critical_age_hours=24,
        high_priority_age_days=7
    )

    # Initialize pipeline
    pipeline = ContinuousEmbeddingPipeline(config)

    # Start scheduled processing
    await pipeline.start_scheduled_pipeline()


if __name__ == "__main__":
    asyncio.run(main())
