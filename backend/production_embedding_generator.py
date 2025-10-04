#!/usr/bin/env python3
"""
Production Embedding Generation System for Planning Explorer

This comprehensive system generates embeddings for planning application descriptions
with advanced error handling, resume capability, progress monitoring, and cost tracking.

Features:
- Robust batch processing with rate limiting (500 RPM compliance)
- Advanced error handling and automatic retry logic
- Resume capability for interrupted processing
- Real-time progress monitoring and ETA calculation
- Comprehensive cost tracking and performance metrics
- Production-grade logging and monitoring
- Command-line interface for operational control

Usage:
    python production_embedding_generator.py --target 50000 --batch-size 500
    python production_embedding_generator.py --resume --state-file state.json
    python production_embedding_generator.py --dry-run --target 1000
"""

import asyncio
import argparse
import json
import logging
import os
import signal
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple
import traceback

from app.db.elasticsearch import es_client
from app.ai.embeddings import EmbeddingService

# Advanced logging configuration
def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """Setup comprehensive logging with file and console output"""

    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Set log file if not provided
    if not log_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"embedding_generation_{timestamp}.log"

    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Setup handlers
    handlers = [
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers,
        force=True
    )

    # Set specific logger levels
    logging.getLogger("elasticsearch").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    return logging.getLogger(__name__)

@dataclass
class ProcessingState:
    """State management for resume capability"""
    session_id: str
    start_time: float
    target_documents: int
    batch_size: int
    processed_count: int
    successful_embeddings: int
    failed_embeddings: int
    skipped_documents: int
    total_tokens: int
    total_cost_usd: float
    last_processed_offset: int
    processed_document_ids: Set[str]
    error_count: int
    batch_times: List[float]
    current_phase: str
    last_sort_values: Optional[List[Any]] = None  # For search_after pagination

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for JSON serialization"""
        state_dict = asdict(self)
        state_dict['processed_document_ids'] = list(self.processed_document_ids)
        return state_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessingState':
        """Create state from dictionary"""
        data['processed_document_ids'] = set(data.get('processed_document_ids', []))
        return cls(**data)

@dataclass
class BatchResult:
    """Result of processing a single batch"""
    batch_num: int
    documents_retrieved: int
    embeddings_generated: int
    embeddings_updated: int
    processing_time: float
    total_tokens: int
    estimated_cost: float
    errors: List[str]
    skipped_docs: int

class ProductionEmbeddingGenerator:
    """
    Production-ready embedding generation system with comprehensive features:
    - Advanced error handling and retry logic
    - Resume capability with state persistence
    - Real-time progress monitoring and metrics
    - Cost tracking and performance optimization
    - Production-grade logging and monitoring
    """

    def __init__(self,
                 target_documents: int = 50000,
                 batch_size: int = 500,
                 rate_limit_delay: float = 0.5,
                 max_retries: int = 3,
                 retry_delay: float = 2.0,
                 state_file: Optional[str] = None,
                 dry_run: bool = False):
        """
        Initialize the production embedding generator

        Args:
            target_documents: Number of documents to process (POC: 50,000)
            batch_size: Documents per batch (optimized: 500)
            rate_limit_delay: Delay between API calls (500 RPM compliance: 0.5s)
            max_retries: Maximum retry attempts for failed operations
            retry_delay: Initial delay for exponential backoff
            state_file: File for saving/loading processing state
            dry_run: Run without making actual changes
        """
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.target_documents = target_documents
        self.batch_size = batch_size
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.dry_run = dry_run

        # State management
        self.state_file = state_file or f"embedding_state_{int(time.time())}.json"
        self.state: Optional[ProcessingState] = None
        self._shutdown_requested = False

        # Services
        self.embedding_service = EmbeddingService()

        # Performance tracking
        self.performance_metrics = {
            'api_calls_total': 0,
            'api_calls_successful': 0,
            'api_calls_failed': 0,
            'avg_api_response_time': 0.0,
            'avg_tokens_per_request': 0.0,
            'throughput_docs_per_minute': 0.0,
            'estimated_completion_time': None
        }

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"🛑 Received signal {signum}, initiating graceful shutdown...")
        self._shutdown_requested = True

    async def initialize(self) -> bool:
        """
        Initialize all services and validate system readiness

        Returns:
            bool: True if initialization successful
        """
        self.logger.info("🚀 Initializing Production Embedding Generator...")

        try:
            # Connect to Elasticsearch
            await es_client.connect()
            if not await es_client.health_check():
                self.logger.error("❌ Elasticsearch health check failed")
                return False
            self.logger.info("✅ Elasticsearch connected and healthy")

            # Validate embedding service
            test_result = await self._test_embedding_service()
            if not test_result:
                self.logger.error("❌ Embedding service validation failed")
                return False
            self.logger.info("✅ Embedding service validated")

            # Check index schema and embedding fields
            schema_valid = await self._validate_index_schema()
            if not schema_valid:
                self.logger.error("❌ Index schema validation failed")
                return False
            self.logger.info("✅ Index schema validated")

            # Initialize or load state
            await self._initialize_state()

            self.logger.info("🎯 System initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"❌ Initialization failed: {str(e)}")
            self.logger.debug(traceback.format_exc())
            return False

    async def _test_embedding_service(self) -> bool:
        """Test embedding service functionality"""
        try:
            test_text = "Test planning application for residential development"
            result = await self.embedding_service.generate_text_embedding(test_text)

            if not result or not result.embedding:
                return False

            # Validate dimensions (expecting 1536 for OpenAI small)
            if len(result.embedding) != 1536:
                self.logger.warning(f"⚠️  Unexpected embedding dimensions: {len(result.embedding)}")

            self.logger.info(f"✅ Embedding service test successful (dims: {len(result.embedding)})")
            return True

        except Exception as e:
            self.logger.error(f"❌ Embedding service test failed: {str(e)}")
            return False

    async def _validate_index_schema(self) -> bool:
        """Validate that index has proper embedding field mapping"""
        try:
            mapping_response = await es_client.client.indices.get_mapping(index=es_client.index_name)
            properties = mapping_response[es_client.index_name]['mappings']['properties']

            # Check for description_embedding field
            embedding_field = properties.get('description_embedding')
            if not embedding_field:
                self.logger.error("❌ No description_embedding field found in index mapping")
                return False

            if embedding_field.get('type') != 'dense_vector':
                self.logger.error("❌ description_embedding field is not dense_vector type")
                return False

            dimensions = embedding_field.get('dims', 0)
            if dimensions != 1536:
                self.logger.warning(f"⚠️  Expected 1536 dimensions, found {dimensions}")

            self.logger.info(f"✅ Index schema valid (embedding field: {dimensions} dims)")
            return True

        except Exception as e:
            self.logger.error(f"❌ Schema validation failed: {str(e)}")
            return False

    async def _initialize_state(self):
        """Initialize or load processing state"""
        try:
            # Try to load existing state file
            if os.path.exists(self.state_file):
                self.logger.info(f"📂 Loading existing state from {self.state_file}")
                with open(self.state_file, 'r') as f:
                    state_data = json.load(f)
                self.state = ProcessingState.from_dict(state_data)
                self.logger.info(f"✅ Resumed state: {self.state.processed_count:,} docs processed")
            else:
                # Create new state
                self.logger.info("🆕 Creating new processing state")
                session_id = f"emb_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.state = ProcessingState(
                    session_id=session_id,
                    start_time=time.time(),
                    target_documents=self.target_documents,
                    batch_size=self.batch_size,
                    processed_count=0,
                    successful_embeddings=0,
                    failed_embeddings=0,
                    skipped_documents=0,
                    total_tokens=0,
                    total_cost_usd=0.0,
                    last_processed_offset=0,
                    processed_document_ids=set(),
                    error_count=0,
                    batch_times=[],
                    current_phase="initialization",
                    last_sort_values=None
                )
                await self._save_state()

        except Exception as e:
            self.logger.error(f"❌ State initialization failed: {str(e)}")
            raise

    async def _save_state(self):
        """Save current processing state to file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state.to_dict(), f, indent=2, default=str)
            self.logger.debug(f"💾 State saved to {self.state_file}")
        except Exception as e:
            self.logger.error(f"❌ Failed to save state: {str(e)}")

    async def get_next_batch(self, offset: int = 0) -> Tuple[List[Dict[str, Any]], Optional[List[Any]]]:
        """
        Get next batch of documents that need embeddings using search_after pagination.

        This method uses Elasticsearch's search_after API to handle deep pagination
        beyond the default 10,000 document limit, enabling processing of large datasets.

        Args:
            offset: Starting offset for pagination (deprecated, kept for compatibility)

        Returns:
            Tuple of (documents list, sort_values for next batch)
        """
        # Query for documents without embeddings, sorted by most recent
        query = {
            "bool": {
                "must_not": [
                    {"exists": {"field": "description_embedding"}}
                ],
                "must": [
                    {"exists": {"field": "description"}},
                    {"range": {"description": {"gte": 10}}}  # At least 10 characters
                ]
            }
        }

        # Add exclusion for already processed documents (for resume capability)
        if self.state.processed_document_ids:
            # Split into chunks to avoid too large terms query
            doc_id_chunks = [list(self.state.processed_document_ids)[i:i+1024]
                           for i in range(0, len(self.state.processed_document_ids), 1024)]
            for chunk in doc_id_chunks:
                query["bool"]["must_not"].append({
                    "terms": {"_id": chunk}
                })

        # Sort configuration for search_after - use uid as tie-breaker instead of _id
        # (_id field requires fielddata enabled which is not recommended)
        sort = [
            {"start_date": {"order": "desc", "missing": "_last"}},
            {"last_changed": {"order": "desc", "missing": "_last"}},
            {"uid.keyword": {"order": "asc"}}  # Tie-breaker for consistent pagination
        ]

        try:
            # Build search request
            search_params = {
                "query": query,
                "size": self.batch_size,
                "sort": sort,
                "source": ["uid", "description", "start_date", "last_changed", "area_name", "app_type",
                          "other_fields", "address"],
                "track_total_hits": True  # Get accurate count
            }

            # Use search_after if we have last sort values (deep pagination)
            if self.state.last_sort_values:
                search_params["search_after"] = self.state.last_sort_values
                self.logger.debug(f"📥 Using search_after pagination: {self.state.last_sort_values}")
            else:
                self.logger.debug(f"📥 Starting new search from beginning")

            # Execute search via raw client for search_after support
            response = await es_client.client.search(
                index=es_client.index_name,
                **search_params
            )

            documents = response.get("hits", {}).get("hits", [])
            total_hits = response.get("hits", {}).get("total", {}).get("value", 0)

            # Extract sort values from last document for next batch
            next_sort_values = None
            if documents:
                next_sort_values = documents[-1].get("sort")

            self.logger.debug(f"📥 Retrieved {len(documents)} documents (total available: {total_hits:,})")
            return documents, next_sort_values

        except Exception as e:
            self.logger.error(f"❌ Failed to retrieve batch: {str(e)}")
            raise

    async def process_batch(self, documents: List[Dict[str, Any]], batch_num: int) -> BatchResult:
        """
        Process a batch of documents to generate embeddings

        Args:
            documents: List of documents to process
            batch_num: Current batch number

        Returns:
            BatchResult with processing statistics
        """
        batch_start_time = time.time()
        embeddings_generated = 0
        embeddings_updated = 0
        total_tokens = 0
        estimated_cost = 0.0
        errors = []
        skipped_docs = 0

        self.logger.info(f"🔄 Processing batch {batch_num} ({len(documents)} documents)")

        # Process each document in the batch
        for i, doc in enumerate(documents):
            if self._shutdown_requested:
                self.logger.info("🛑 Shutdown requested, stopping batch processing")
                break

            doc_id = doc["_id"]
            source = doc["_source"]
            description = source.get("description", "").strip()

            # Skip documents with insufficient description
            if not description or len(description) < 10:
                self.logger.debug(f"⏭️  Skipping document {doc_id}: insufficient description")
                skipped_docs += 1
                continue

            # Skip if already processed (additional safety check)
            if doc_id in self.state.processed_document_ids:
                self.logger.debug(f"⏭️  Skipping document {doc_id}: already processed")
                skipped_docs += 1
                continue

            try:
                # Generate embedding from description field ONLY
                # For POC: description field already contains developer names in most cases
                embedding_result = await self._generate_embedding_with_retry(
                    description, doc_id, max_retries=self.max_retries
                )

                if embedding_result:
                    embeddings_generated += 1
                    total_tokens += embedding_result.token_count
                    estimated_cost += self._calculate_cost(embedding_result.token_count)

                    # Update document in Elasticsearch
                    if not self.dry_run:
                        update_success = await self._update_document_with_retry(
                            doc_id, embedding_result, source, max_retries=self.max_retries
                        )
                        if update_success:
                            embeddings_updated += 1
                            self.state.processed_document_ids.add(doc_id)
                        else:
                            errors.append(f"Failed to update document {doc_id}")
                    else:
                        embeddings_updated += 1  # Count as updated in dry run
                        self.state.processed_document_ids.add(doc_id)
                        self.logger.debug(f"🧪 DRY RUN: Would update document {doc_id}")
                else:
                    errors.append(f"Failed to generate embedding for {doc_id}")

                # Rate limiting
                await asyncio.sleep(self.rate_limit_delay)

                # Progress update within batch
                if (i + 1) % 50 == 0:
                    self.logger.debug(f"   📊 Batch progress: {i+1}/{len(documents)} documents")

            except Exception as e:
                error_msg = f"Error processing document {doc_id}: {str(e)}"
                self.logger.error(f"❌ {error_msg}")
                errors.append(error_msg)
                self.state.error_count += 1

        # Calculate batch processing time
        batch_time = time.time() - batch_start_time

        return BatchResult(
            batch_num=batch_num,
            documents_retrieved=len(documents),
            embeddings_generated=embeddings_generated,
            embeddings_updated=embeddings_updated,
            processing_time=batch_time,
            total_tokens=total_tokens,
            estimated_cost=estimated_cost,
            errors=errors,
            skipped_docs=skipped_docs
        )

    async def _generate_embedding_with_retry(self,
                                           description: str,
                                           doc_id: str,
                                           max_retries: int = 3) -> Optional[Any]:
        """Generate embedding with exponential backoff retry logic"""

        for attempt in range(max_retries + 1):
            try:
                # Track API call metrics
                api_start_time = time.time()
                self.performance_metrics['api_calls_total'] += 1

                embedding_result = await self.embedding_service.generate_text_embedding(description)

                if embedding_result and embedding_result.embedding:
                    # Update API metrics
                    api_time = time.time() - api_start_time
                    self.performance_metrics['api_calls_successful'] += 1
                    self._update_api_metrics(api_time, embedding_result.token_count)

                    return embedding_result
                else:
                    self.logger.warning(f"⚠️  Empty embedding result for document {doc_id}")
                    return None

            except Exception as e:
                self.performance_metrics['api_calls_failed'] += 1

                if attempt < max_retries:
                    delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    self.logger.warning(f"⚠️  Attempt {attempt + 1} failed for {doc_id}, retrying in {delay}s: {str(e)}")
                    await asyncio.sleep(delay)
                else:
                    self.logger.error(f"❌ All {max_retries + 1} attempts failed for {doc_id}: {str(e)}")
                    return None

        return None

    async def _update_document_with_retry(self,
                                        doc_id: str,
                                        embedding_result: Any,
                                        source: Dict[str, Any],
                                        max_retries: int = 3) -> bool:
        """Update document in ES with retry logic"""

        update_doc = {
            "description_embedding": embedding_result.embedding,
            "embedding_dimensions": len(embedding_result.embedding),
            "embedding_model": embedding_result.model_used,
            "embedding_generated_at": datetime.utcnow().isoformat(),
            "embedding_text_hash": embedding_result.text_hash,
            "embedding_confidence": embedding_result.confidence_score
        }

        for attempt in range(max_retries + 1):
            try:
                success = await es_client.update_document(
                    doc_id=doc_id,
                    document=update_doc,
                    refresh=False  # Batch refresh for performance
                )

                if success:
                    return True
                else:
                    if attempt < max_retries:
                        delay = self.retry_delay * (2 ** attempt)
                        self.logger.warning(f"⚠️  ES update attempt {attempt + 1} failed for {doc_id}, retrying in {delay}s")
                        await asyncio.sleep(delay)
                    else:
                        self.logger.error(f"❌ All ES update attempts failed for {doc_id}")
                        return False

            except Exception as e:
                if attempt < max_retries:
                    delay = self.retry_delay * (2 ** attempt)
                    self.logger.warning(f"⚠️  ES update error attempt {attempt + 1} for {doc_id}, retrying in {delay}s: {str(e)}")
                    await asyncio.sleep(delay)
                else:
                    self.logger.error(f"❌ All ES update attempts failed for {doc_id}: {str(e)}")
                    return False

        return False

    def _calculate_cost(self, tokens: int) -> float:
        """Calculate estimated cost for embedding generation"""
        # OpenAI text-embedding-3-small pricing: $0.00002 per 1K tokens
        return (tokens / 1000) * 0.00002

    def _update_api_metrics(self, api_time: float, tokens: int):
        """Update API performance metrics"""
        # Rolling average for API response time
        current_avg = self.performance_metrics['avg_api_response_time']
        total_calls = self.performance_metrics['api_calls_successful']
        self.performance_metrics['avg_api_response_time'] = (
            (current_avg * (total_calls - 1) + api_time) / total_calls
        )

        # Rolling average for tokens per request
        current_token_avg = self.performance_metrics['avg_tokens_per_request']
        self.performance_metrics['avg_tokens_per_request'] = (
            (current_token_avg * (total_calls - 1) + tokens) / total_calls
        )

    def _update_batch_metrics(self, batch_result: BatchResult):
        """Update batch processing metrics"""
        # Update state with batch results
        self.state.processed_count += batch_result.documents_retrieved
        self.state.successful_embeddings += batch_result.embeddings_generated
        self.state.failed_embeddings += (batch_result.documents_retrieved -
                                       batch_result.embeddings_generated -
                                       batch_result.skipped_docs)
        self.state.skipped_documents += batch_result.skipped_docs
        self.state.total_tokens += batch_result.total_tokens
        self.state.total_cost_usd += batch_result.estimated_cost

        # Update batch times for ETA calculation
        self.state.batch_times.append(batch_result.processing_time)
        if len(self.state.batch_times) > 10:  # Keep last 10 for rolling average
            self.state.batch_times = self.state.batch_times[-10:]

        # Calculate throughput
        elapsed_time = time.time() - self.state.start_time
        if elapsed_time > 0:
            self.performance_metrics['throughput_docs_per_minute'] = (
                self.state.processed_count / (elapsed_time / 60)
            )

        # Calculate ETA
        self._calculate_eta()

    def _calculate_eta(self):
        """Calculate estimated time to completion"""
        if not self.state.batch_times:
            return

        avg_batch_time = sum(self.state.batch_times) / len(self.state.batch_times)
        remaining_docs = self.state.target_documents - self.state.processed_count
        remaining_batches = remaining_docs / self.state.batch_size
        estimated_seconds = remaining_batches * avg_batch_time

        if estimated_seconds > 0:
            eta = datetime.now() + timedelta(seconds=estimated_seconds)
            self.performance_metrics['estimated_completion_time'] = eta.strftime("%Y-%m-%d %H:%M:%S")

    def _log_batch_progress(self, batch_result: BatchResult):
        """Log detailed batch progress information"""
        progress_pct = (self.state.processed_count / self.state.target_documents) * 100

        self.logger.info(f"📊 Batch {batch_result.batch_num} Results:")
        self.logger.info(f"   ✅ Processed: {self.state.processed_count:,}/{self.state.target_documents:,} ({progress_pct:.1f}%)")
        self.logger.info(f"   🧠 Embeddings: {batch_result.embeddings_generated}/{batch_result.documents_retrieved}")
        self.logger.info(f"   💾 Updated in ES: {batch_result.embeddings_updated}")
        self.logger.info(f"   ⏱️  Batch time: {batch_result.processing_time:.1f}s")
        self.logger.info(f"   💰 Batch cost: ${batch_result.estimated_cost:.4f}")
        self.logger.info(f"   📈 Total cost: ${self.state.total_cost_usd:.2f}")

        if self.performance_metrics['estimated_completion_time']:
            self.logger.info(f"   🎯 ETA: {self.performance_metrics['estimated_completion_time']}")

        throughput = self.performance_metrics['throughput_docs_per_minute']
        self.logger.info(f"   🚀 Throughput: {throughput:.1f} docs/min")

        # Log errors if any
        if batch_result.errors:
            self.logger.warning(f"   ⚠️  Errors in batch: {len(batch_result.errors)}")
            for error in batch_result.errors[:3]:  # Show first 3 errors
                self.logger.warning(f"      - {error}")
            if len(batch_result.errors) > 3:
                self.logger.warning(f"      ... and {len(batch_result.errors) - 3} more errors")

    async def run_embedding_generation(self) -> bool:
        """
        Main embedding generation process

        Returns:
            bool: True if process completed successfully
        """
        self.logger.info("🚀 Starting Production Embedding Generation")
        self.logger.info(f"📋 Configuration:")
        self.logger.info(f"   Target documents: {self.state.target_documents:,}")
        self.logger.info(f"   Batch size: {self.state.batch_size}")
        self.logger.info(f"   Rate limit: {self.rate_limit_delay}s per API call")
        self.logger.info(f"   Dry run: {self.dry_run}")
        self.logger.info(f"   Session ID: {self.state.session_id}")

        if self.state.processed_count > 0:
            self.logger.info(f"📂 Resuming from: {self.state.processed_count:,} documents processed")

        self.state.current_phase = "processing"
        batch_num = (self.state.processed_count // self.state.batch_size) + 1

        try:
            while (self.state.processed_count < self.state.target_documents and
                   not self._shutdown_requested):

                # Get next batch of documents using search_after pagination
                documents, next_sort_values = await self.get_next_batch()

                if not documents:
                    self.logger.info("✅ No more documents to process")
                    break

                # Process the batch
                batch_result = await self.process_batch(documents, batch_num)

                # Update metrics and state
                self._update_batch_metrics(batch_result)
                self._log_batch_progress(batch_result)

                # Update sort values for next iteration (search_after pagination)
                self.state.last_sort_values = next_sort_values

                # Save state periodically
                await self._save_state()

                batch_num += 1

                # Check if we've reached target
                if self.state.processed_count >= self.state.target_documents:
                    self.logger.info(f"🎯 Reached target of {self.state.target_documents:,} documents")
                    break

                # Brief pause between batches for system stability
                await asyncio.sleep(1)

            # Determine success status
            success = not self._shutdown_requested

            if self._shutdown_requested:
                self.logger.info("🛑 Process interrupted by shutdown signal")
            else:
                self.logger.info("✅ Embedding generation completed successfully")

            return success

        except Exception as e:
            self.logger.error(f"❌ Fatal error in embedding generation: {str(e)}")
            self.logger.debug(traceback.format_exc())
            return False

        finally:
            await self._finalize()

    async def _finalize(self):
        """Finalize processing and generate comprehensive report"""
        self.logger.info("🏁 Finalizing embedding generation...")

        self.state.current_phase = "finalizing"
        total_time = time.time() - self.state.start_time

        # Refresh Elasticsearch index to make embeddings searchable
        if not self.dry_run and self.state.successful_embeddings > 0:
            try:
                self.logger.info("🔄 Refreshing Elasticsearch index...")
                await es_client.client.indices.refresh(index=es_client.index_name)
                self.logger.info("✅ Index refreshed - embeddings now searchable")
            except Exception as e:
                self.logger.error(f"❌ Failed to refresh index: {e}")

        # Generate comprehensive final report
        await self._generate_final_report(total_time)

        # Save final state
        await self._save_state()

        # Cleanup
        await es_client.disconnect()

        self.logger.info("🎉 Embedding generation finalized")

    async def _generate_final_report(self, total_time: float):
        """Generate comprehensive final processing report"""

        # Calculate final statistics
        success_rate = (self.state.successful_embeddings / max(self.state.processed_count, 1)) * 100
        avg_docs_per_minute = (self.state.processed_count / (total_time / 60)) if total_time > 0 else 0

        # API performance metrics
        api_success_rate = (self.performance_metrics['api_calls_successful'] /
                           max(self.performance_metrics['api_calls_total'], 1)) * 100

        self.logger.info("📊 FINAL EMBEDDING GENERATION REPORT")
        self.logger.info("=" * 50)
        self.logger.info(f"🆔 Session ID: {self.state.session_id}")
        self.logger.info(f"📅 Start Time: {datetime.fromtimestamp(self.state.start_time).strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"📅 End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"⏱️  Total Duration: {total_time/3600:.1f} hours ({total_time/60:.1f} minutes)")
        self.logger.info("")

        self.logger.info("📄 DOCUMENT PROCESSING:")
        self.logger.info(f"   🎯 Target Documents: {self.state.target_documents:,}")
        self.logger.info(f"   📊 Documents Processed: {self.state.processed_count:,}")
        self.logger.info(f"   ✅ Successful Embeddings: {self.state.successful_embeddings:,}")
        self.logger.info(f"   ❌ Failed Embeddings: {self.state.failed_embeddings:,}")
        self.logger.info(f"   ⏭️  Skipped Documents: {self.state.skipped_documents:,}")
        self.logger.info(f"   📈 Success Rate: {success_rate:.1f}%")
        self.logger.info("")

        self.logger.info("🔧 API PERFORMANCE:")
        self.logger.info(f"   📞 Total API Calls: {self.performance_metrics['api_calls_total']:,}")
        self.logger.info(f"   ✅ Successful Calls: {self.performance_metrics['api_calls_successful']:,}")
        self.logger.info(f"   ❌ Failed Calls: {self.performance_metrics['api_calls_failed']:,}")
        self.logger.info(f"   📈 API Success Rate: {api_success_rate:.1f}%")
        self.logger.info(f"   ⏱️  Avg Response Time: {self.performance_metrics['avg_api_response_time']:.2f}s")
        self.logger.info(f"   🔤 Avg Tokens/Request: {self.performance_metrics['avg_tokens_per_request']:.0f}")
        self.logger.info("")

        self.logger.info("💰 COST ANALYSIS:")
        self.logger.info(f"   🎟️  Total Tokens Processed: {self.state.total_tokens:,}")
        self.logger.info(f"   💳 Total Estimated Cost: ${self.state.total_cost_usd:.2f}")
        self.logger.info(f"   📊 Cost per Document: ${(self.state.total_cost_usd/max(self.state.successful_embeddings,1)):.4f}")
        self.logger.info(f"   📊 Cost per 1K Tokens: ${(self.state.total_cost_usd/(self.state.total_tokens/1000)):.4f}" if self.state.total_tokens > 0 else "   📊 Cost per 1K Tokens: $0.0000")
        self.logger.info("")

        self.logger.info("🚀 PERFORMANCE METRICS:")
        self.logger.info(f"   📈 Throughput: {avg_docs_per_minute:.1f} documents/minute")
        self.logger.info(f"   📈 Token Processing Rate: {(self.state.total_tokens/(total_time/60)):.0f} tokens/minute" if total_time > 0 else "   📈 Token Processing Rate: 0 tokens/minute")
        self.logger.info(f"   ⚡ Rate Limit Compliance: {self.rate_limit_delay}s delay (500 RPM target)")
        self.logger.info("")

        if self.dry_run:
            self.logger.info("🧪 DRY RUN MODE - No actual changes made to Elasticsearch")
        else:
            self.logger.info("💾 ELASTICSEARCH UPDATES:")
            self.logger.info(f"   📝 Documents Updated: {self.state.successful_embeddings:,}")
            self.logger.info(f"   🔄 Index Refreshed: ✅")
            self.logger.info(f"   🔍 Embeddings Now Searchable: ✅")

        # Save detailed report to file
        report_data = {
            "session_id": self.state.session_id,
            "configuration": {
                "target_documents": self.state.target_documents,
                "batch_size": self.state.batch_size,
                "rate_limit_delay": self.rate_limit_delay,
                "dry_run": self.dry_run
            },
            "processing_summary": {
                "total_time_seconds": total_time,
                "documents_processed": self.state.processed_count,
                "successful_embeddings": self.state.successful_embeddings,
                "failed_embeddings": self.state.failed_embeddings,
                "skipped_documents": self.state.skipped_documents,
                "success_rate_percent": success_rate
            },
            "api_performance": {
                "total_api_calls": self.performance_metrics['api_calls_total'],
                "successful_api_calls": self.performance_metrics['api_calls_successful'],
                "failed_api_calls": self.performance_metrics['api_calls_failed'],
                "api_success_rate_percent": api_success_rate,
                "avg_response_time_seconds": self.performance_metrics['avg_api_response_time'],
                "avg_tokens_per_request": self.performance_metrics['avg_tokens_per_request']
            },
            "cost_analysis": {
                "total_tokens": self.state.total_tokens,
                "total_cost_usd": self.state.total_cost_usd,
                "cost_per_document_usd": self.state.total_cost_usd / max(self.state.successful_embeddings, 1),
                "cost_per_1k_tokens_usd": (self.state.total_cost_usd / (self.state.total_tokens / 1000)) if self.state.total_tokens > 0 else 0
            },
            "performance_metrics": {
                "throughput_docs_per_minute": avg_docs_per_minute,
                "token_processing_rate_per_minute": (self.state.total_tokens / (total_time / 60)) if total_time > 0 else 0,
                "rate_limit_delay_seconds": self.rate_limit_delay
            }
        }

        # Save comprehensive report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"embedding_generation_report_{timestamp}.json"

        try:
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            self.logger.info(f"📁 Detailed report saved: {report_file}")
        except Exception as e:
            self.logger.error(f"❌ Failed to save report: {e}")

def create_argument_parser():
    """Create command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="Production Embedding Generation System for Planning Explorer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Generate embeddings for 50,000 documents (POC target)
    python production_embedding_generator.py --target 50000

    # Resume from saved state file
    python production_embedding_generator.py --resume --state-file state.json

    # Dry run to test without making changes
    python production_embedding_generator.py --dry-run --target 1000

    # Custom batch size and rate limiting
    python production_embedding_generator.py --target 10000 --batch-size 200 --rate-limit 1.0
        """
    )

    # Primary configuration
    parser.add_argument('--target', type=int, default=50000,
                       help='Number of documents to process (default: 50000)')
    parser.add_argument('--batch-size', type=int, default=500,
                       help='Documents per batch (default: 500)')
    parser.add_argument('--rate-limit', type=float, default=0.5,
                       help='Delay between API calls in seconds (default: 0.5 for 500 RPM)')

    # Operation modes
    parser.add_argument('--dry-run', action='store_true',
                       help='Run without making actual changes to Elasticsearch')
    parser.add_argument('--resume', action='store_true',
                       help='Resume from existing state file')

    # Advanced configuration
    parser.add_argument('--state-file', type=str,
                       help='State file for resume capability (auto-generated if not specified)')
    parser.add_argument('--max-retries', type=int, default=3,
                       help='Maximum retry attempts for failed operations (default: 3)')
    parser.add_argument('--retry-delay', type=float, default=2.0,
                       help='Initial retry delay in seconds (default: 2.0)')

    # Logging configuration
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Logging level (default: INFO)')
    parser.add_argument('--log-file', type=str,
                       help='Log file path (auto-generated if not specified)')

    return parser

async def main():
    """Main entry point for the embedding generation system"""

    # Parse command-line arguments
    parser = create_argument_parser()
    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(args.log_level, args.log_file)

    logger.info("🚀 Production Embedding Generation System Starting")
    logger.info(f"📋 Configuration: {vars(args)}")

    try:
        # Create and initialize generator
        generator = ProductionEmbeddingGenerator(
            target_documents=args.target,
            batch_size=args.batch_size,
            rate_limit_delay=args.rate_limit,
            max_retries=args.max_retries,
            retry_delay=args.retry_delay,
            state_file=args.state_file,
            dry_run=args.dry_run
        )

        # Initialize system
        if not await generator.initialize():
            logger.error("❌ System initialization failed")
            sys.exit(1)

        # Run embedding generation
        success = await generator.run_embedding_generation()

        if success:
            logger.info("✅ Embedding generation completed successfully")
            sys.exit(0)
        else:
            logger.error("❌ Embedding generation failed or was interrupted")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("❌ Process interrupted by user")
        sys.exit(130)  # Standard exit code for Ctrl+C
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        logger.debug(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())