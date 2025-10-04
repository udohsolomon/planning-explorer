#!/usr/bin/env python3
"""
Weekend Batch Embedding Generator - Optimized for 2.5M Documents
Processes from recent to old with batched API calls for maximum efficiency
"""

import asyncio
import argparse
import json
import logging
import sys
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from app.db.elasticsearch import es_client
from app.ai.embeddings import EmbeddingService

# Setup logging
def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"weekend_embedding_{timestamp}.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Quiet noisy loggers
    logging.getLogger("elasticsearch").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    return logging.getLogger(__name__)

logger = setup_logging()


class BatchEmbeddingGenerator:
    """Optimized batch embedding generator for 2.5M documents"""

    def __init__(
        self,
        target_documents: int = 2_500_000,
        batch_size: int = 100,  # Docs per API call
        es_batch_size: int = 500,  # Docs to fetch from ES
        max_retries: int = 3,
        dry_run: bool = False
    ):
        self.target_documents = target_documents
        self.batch_size = batch_size  # API batch size
        self.es_batch_size = es_batch_size
        self.max_retries = max_retries
        self.dry_run = dry_run

        self.embedding_service = EmbeddingService()

        # State tracking
        self.processed_count = 0
        self.successful_count = 0
        self.failed_count = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.start_time = time.time()

        # Checkpoint
        self.checkpoint_file = f"batch_checkpoint_{int(time.time())}.json"
        self.processed_ids = set()

    async def initialize(self) -> bool:
        """Initialize services"""
        logger.info("🚀 Initializing Weekend Batch Embedding Generator")
        logger.info(f"📊 Target: {self.target_documents:,} documents")
        logger.info(f"📦 API Batch Size: {self.batch_size} docs/call")
        logger.info(f"🔄 ES Batch Size: {self.es_batch_size} docs/fetch")

        try:
            await es_client.connect()
            if not await es_client.health_check():
                logger.error("❌ Elasticsearch health check failed")
                return False

            logger.info("✅ Elasticsearch connected")

            # Test embedding service
            test_result = await self.embedding_service.generate_text_embedding(
                "Test planning application"
            )
            if not test_result or not test_result.embedding:
                logger.error("❌ Embedding service test failed")
                return False

            logger.info(f"✅ Embedding service ready (dim: {len(test_result.embedding)})")
            return True

        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False

    async def get_documents_batch(
        self,
        offset: int = 0,
        sort_values: Optional[List[Any]] = None
    ) -> tuple[List[Dict], Optional[List[Any]]]:
        """
        Get batch of documents ordered by recent first
        Uses search_after for deep pagination
        """
        query = {
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

        # Exclude already processed (for resume)
        if self.processed_ids:
            chunks = [list(self.processed_ids)[i:i+1024]
                     for i in range(0, len(self.processed_ids), 1024)]
            for chunk in chunks:
                query["bool"]["must_not"].append({"terms": {"_id": chunk}})

        # Sort by most recent first
        sort = [
            {"start_date": {"order": "desc", "missing": "_last"}},
            {"last_changed": {"order": "desc", "missing": "_last"}},
            {"uid.keyword": {"order": "asc"}}
        ]

        search_params = {
            "query": query,
            "size": self.es_batch_size,
            "sort": sort,
            "source": ["uid", "description", "start_date"],
            "track_total_hits": True
        }

        if sort_values:
            search_params["search_after"] = sort_values

        try:
            response = await es_client.client.search(
                index=es_client.index_name,
                **search_params
            )

            documents = response.get("hits", {}).get("hits", [])
            total_hits = response.get("hits", {}).get("total", {}).get("value", 0)

            next_sort = documents[-1].get("sort") if documents else None

            logger.debug(f"📥 Retrieved {len(documents)} docs (total available: {total_hits:,})")
            return documents, next_sort

        except Exception as e:
            logger.error(f"❌ Failed to retrieve batch: {e}")
            raise

    async def batch_generate_embeddings(
        self,
        texts: List[str]
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in one API call
        OpenAI supports up to 2,048 inputs per request
        """
        if not texts:
            return []

        for attempt in range(self.max_retries):
            try:
                api_start = time.time()

                # Batch API call
                response = await self.embedding_service.client.embeddings.create(
                    model=self.embedding_service.model,
                    input=texts  # Multiple texts
                )

                api_time = time.time() - api_start

                # Extract embeddings
                embeddings = [item.embedding for item in response.data]
                tokens = response.usage.total_tokens

                # Update metrics
                self.total_tokens += tokens
                cost = (tokens / 1000) * 0.00002
                self.total_cost += cost

                logger.debug(
                    f"✅ Generated {len(embeddings)} embeddings in {api_time:.2f}s "
                    f"({tokens} tokens, ${cost:.4f})"
                )

                return embeddings

            except Exception as e:
                if attempt < self.max_retries - 1:
                    delay = 2 ** attempt
                    logger.warning(f"⚠️ Batch embedding attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"❌ Batch embedding failed after {self.max_retries} attempts: {e}")
                    return []

        return []

    async def process_es_batch(
        self,
        documents: List[Dict]
    ) -> Dict[str, int]:
        """Process a batch of documents from ES"""
        if not documents:
            return {"processed": 0, "succeeded": 0, "failed": 0}

        # Prepare texts and doc info
        batch_items = []
        for doc in documents:
            doc_id = doc["_id"]
            description = doc["_source"].get("description", "").strip()

            if description and len(description) >= 10:
                batch_items.append({
                    "id": doc_id,
                    "description": description
                })

        if not batch_items:
            logger.debug("⏭️  No valid documents in this batch")
            return {"processed": 0, "succeeded": 0, "failed": 0}

        # Split into API batches (100 docs per API call)
        api_batches = [
            batch_items[i:i + self.batch_size]
            for i in range(0, len(batch_items), self.batch_size)
        ]

        succeeded = 0
        failed = 0

        for api_batch in api_batches:
            # Extract texts
            texts = [item["description"] for item in api_batch]

            # Batch generate embeddings
            embeddings = await self.batch_generate_embeddings(texts)

            if not embeddings or len(embeddings) != len(api_batch):
                logger.error(f"❌ Embedding count mismatch: {len(embeddings)} vs {len(api_batch)}")
                failed += len(api_batch)
                continue

            # Bulk update ES
            bulk_operations = []
            for item, embedding in zip(api_batch, embeddings):
                bulk_operations.append({
                    "update": {
                        "_id": item["id"],
                        "_index": es_client.index_name
                    }
                })
                bulk_operations.append({
                    "doc": {
                        "description_embedding": embedding,
                        "embedding_dimensions": len(embedding),
                        "embedding_model": "text-embedding-3-small",
                        "embedding_generated_at": datetime.utcnow().isoformat()
                    }
                })

            # Execute bulk update
            if not self.dry_run and bulk_operations:
                try:
                    result = await es_client.client.bulk(
                        operations=bulk_operations,
                        refresh=False
                    )

                    if result.get("errors"):
                        errors = sum(1 for item in result["items"] if item.get("update", {}).get("error"))
                        succeeded += len(api_batch) - errors
                        failed += errors
                        logger.warning(f"⚠️ Bulk update had {errors} errors")
                    else:
                        succeeded += len(api_batch)

                    # Track processed IDs
                    for item in api_batch:
                        self.processed_ids.add(item["id"])

                except Exception as e:
                    logger.error(f"❌ Bulk update failed: {e}")
                    failed += len(api_batch)
            else:
                succeeded += len(api_batch)
                for item in api_batch:
                    self.processed_ids.add(item["id"])

        return {
            "processed": len(batch_items),
            "succeeded": succeeded,
            "failed": failed
        }

    async def save_checkpoint(self):
        """Save progress checkpoint"""
        checkpoint = {
            "timestamp": datetime.now().isoformat(),
            "processed_count": self.processed_count,
            "successful_count": self.successful_count,
            "failed_count": self.failed_count,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "processed_ids": list(self.processed_ids)
        }

        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint, f)

        logger.debug(f"💾 Checkpoint saved: {self.processed_count:,} docs")

    async def run(self):
        """Main execution loop"""
        logger.info("🏁 Starting batch embedding generation")
        logger.info(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        sort_values = None
        batch_num = 0

        try:
            while self.processed_count < self.target_documents:
                batch_num += 1

                # Get batch from ES
                documents, next_sort = await self.get_documents_batch(
                    offset=self.processed_count,
                    sort_values=sort_values
                )

                if not documents:
                    logger.info("✅ No more documents to process")
                    break

                # Process batch
                batch_start = time.time()
                result = await self.process_es_batch(documents)
                batch_time = time.time() - batch_start

                # Update counters
                self.processed_count += result["processed"]
                self.successful_count += result["succeeded"]
                self.failed_count += result["failed"]

                # Progress report
                elapsed = time.time() - self.start_time
                rate = self.processed_count / (elapsed / 60) if elapsed > 0 else 0
                remaining = self.target_documents - self.processed_count
                eta_minutes = (remaining / rate) if rate > 0 else 0

                progress_pct = (self.processed_count / self.target_documents) * 100

                logger.info(
                    f"📊 Batch {batch_num}: {result['succeeded']}/{result['processed']} succeeded "
                    f"in {batch_time:.1f}s | "
                    f"Progress: {self.processed_count:,}/{self.target_documents:,} ({progress_pct:.1f}%) | "
                    f"Rate: {rate:.0f} docs/min | "
                    f"ETA: {eta_minutes:.0f} min | "
                    f"Cost: ${self.total_cost:.2f}"
                )

                # Update sort for next batch
                sort_values = next_sort

                # Checkpoint every 10 batches
                if batch_num % 10 == 0:
                    await self.save_checkpoint()

                # Brief pause to avoid overwhelming ES
                await asyncio.sleep(0.1)

        except KeyboardInterrupt:
            logger.info("🛑 Interrupted by user")
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")
            import traceback
            logger.error(traceback.format_exc())
        finally:
            await self.finalize()

    async def finalize(self):
        """Finalize and generate report"""
        logger.info("🏁 Finalizing embedding generation...")

        # Save final checkpoint
        await self.save_checkpoint()

        # Refresh ES index
        if not self.dry_run and self.successful_count > 0:
            try:
                logger.info("🔄 Refreshing Elasticsearch index...")
                await es_client.client.indices.refresh(index=es_client.index_name)
                logger.info("✅ Index refreshed")
            except Exception as e:
                logger.error(f"❌ Index refresh failed: {e}")

        # Generate report
        total_time = time.time() - self.start_time

        logger.info("=" * 80)
        logger.info("📊 WEEKEND BATCH EMBEDDING REPORT")
        logger.info("=" * 80)
        logger.info(f"⏱️  Total Duration: {total_time/3600:.1f} hours ({total_time/60:.1f} minutes)")
        logger.info(f"📄 Documents Processed: {self.processed_count:,}")
        logger.info(f"✅ Successful Embeddings: {self.successful_count:,}")
        logger.info(f"❌ Failed Embeddings: {self.failed_count:,}")
        logger.info(f"📈 Success Rate: {(self.successful_count/max(self.processed_count,1))*100:.1f}%")
        logger.info(f"🎟️  Total Tokens: {self.total_tokens:,}")
        logger.info(f"💰 Total Cost: ${self.total_cost:.2f}")
        logger.info(f"📊 Cost per Document: ${self.total_cost/max(self.successful_count,1):.6f}")
        logger.info(f"🚀 Throughput: {self.processed_count/(total_time/60):.0f} docs/minute")
        logger.info("=" * 80)

        # Save detailed report
        report = {
            "session_id": f"weekend_batch_{int(self.start_time)}",
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_hours": total_time / 3600,
            "documents_processed": self.processed_count,
            "successful_embeddings": self.successful_count,
            "failed_embeddings": self.failed_count,
            "success_rate": (self.successful_count/max(self.processed_count,1))*100,
            "total_tokens": self.total_tokens,
            "total_cost_usd": self.total_cost,
            "cost_per_document": self.total_cost/max(self.successful_count,1),
            "throughput_docs_per_minute": self.processed_count/(total_time/60)
        }

        report_file = f"weekend_embedding_report_{int(self.start_time)}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"📁 Detailed report saved: {report_file}")

        # Cleanup
        await es_client.disconnect()


async def main():
    parser = argparse.ArgumentParser(
        description="Weekend Batch Embedding Generator - Optimized for 2.5M docs"
    )

    parser.add_argument(
        '--target',
        type=int,
        default=2_500_000,
        help='Target number of documents to process'
    )
    parser.add_argument(
        '--api-batch-size',
        type=int,
        default=100,
        help='Number of documents per API call (max 2048)'
    )
    parser.add_argument(
        '--es-batch-size',
        type=int,
        default=500,
        help='Number of documents to fetch from ES per batch'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run mode (no ES updates)'
    )

    args = parser.parse_args()

    logger.info("🎯 Weekend Batch Embedding Generator")
    logger.info(f"📋 Configuration: {vars(args)}")

    generator = BatchEmbeddingGenerator(
        target_documents=args.target,
        batch_size=args.api_batch_size,
        es_batch_size=args.es_batch_size,
        dry_run=args.dry_run
    )

    if not await generator.initialize():
        logger.error("❌ Initialization failed, exiting")
        sys.exit(1)

    await generator.run()


if __name__ == "__main__":
    asyncio.run(main())
