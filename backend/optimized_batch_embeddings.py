#!/usr/bin/env python3
"""
Optimized Batch Embedding Generator - 24-48 Hour Target
Uses OpenAI batch API (up to 2048 texts per call) + concurrent processing
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
from app.core.config import settings
import openai

# Setup logging
def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"optimized_embedding_{timestamp}.log"

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


class OptimizedBatchEmbeddings:
    """Optimized batch embeddings with concurrent processing"""

    def __init__(
        self,
        target_documents: int = 2_500_000,
        es_batch_size: int = 1000,
        api_batch_size: int = 500,  # OpenAI supports up to 2048
        concurrent_batches: int = 5,  # Process 5 API batches concurrently
        dry_run: bool = False
    ):
        self.target_documents = target_documents
        self.es_batch_size = es_batch_size
        self.api_batch_size = api_batch_size
        self.concurrent_batches = concurrent_batches
        self.dry_run = dry_run

        # Initialize OpenAI client directly
        self.openai_client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = "text-embedding-3-small"

        # State tracking
        self.processed_count = 0
        self.successful_count = 0
        self.failed_count = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.start_time = time.time()

        # Checkpoint
        self.checkpoint_file = f"optimized_checkpoint_{int(time.time())}.json"
        self.processed_ids = set()

    async def initialize(self) -> bool:
        """Initialize services"""
        logger.info("🚀 Initializing Optimized Batch Embedding Generator")
        logger.info(f"📊 Target: {self.target_documents:,} documents")
        logger.info(f"📦 ES Batch Size: {self.es_batch_size} docs/fetch")
        logger.info(f"🔥 API Batch Size: {self.api_batch_size} texts/API call")
        logger.info(f"⚡ Concurrent API Batches: {self.concurrent_batches}")

        try:
            await es_client.connect()
            if not await es_client.health_check():
                logger.error("❌ Elasticsearch health check failed")
                return False

            logger.info("✅ Elasticsearch connected")

            # Test OpenAI API with batch call
            test_result = await self.openai_client.embeddings.create(
                model=self.model,
                input=["Test 1", "Test 2", "Test 3"]  # Batch test
            )

            if not test_result or len(test_result.data) != 3:
                logger.error("❌ OpenAI batch API test failed")
                return False

            logger.info(f"✅ OpenAI batch API ready (dims: {len(test_result.data[0].embedding)})")
            return True

        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False

    async def get_documents_batch(
        self,
        sort_values: Optional[List[Any]] = None
    ) -> tuple[List[Dict], Optional[List[Any]]]:
        """Get batch of documents ordered by recent first"""
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
            "_source": ["uid", "description", "start_date"],
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
        """Generate embeddings for multiple texts in ONE API call"""
        if not texts:
            return []

        max_retries = 3
        for attempt in range(max_retries):
            try:
                api_start = time.time()

                # BATCH API CALL - multiple texts in one request
                response = await self.openai_client.embeddings.create(
                    model=self.model,
                    input=texts  # List of texts
                )

                api_time = time.time() - api_start

                # Extract embeddings in order
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
                if attempt < max_retries - 1:
                    delay = 2 ** attempt
                    logger.warning(f"⚠️ Batch attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"❌ Batch embedding failed after {max_retries} attempts: {e}")
                    return []

        return []

    async def process_api_batch(
        self,
        batch_items: List[Dict]
    ) -> Dict[str, int]:
        """Process one API batch (up to api_batch_size texts)"""
        if not batch_items:
            return {"succeeded": 0, "failed": 0}

        # Extract texts
        texts = [item["description"] for item in batch_items]

        # Batch generate embeddings
        embeddings = await self.batch_generate_embeddings(texts)

        if not embeddings or len(embeddings) != len(batch_items):
            logger.error(f"❌ Embedding count mismatch: {len(embeddings)} vs {len(batch_items)}")
            return {"succeeded": 0, "failed": len(batch_items)}

        # Bulk update ES
        bulk_operations = []
        for item, embedding in zip(batch_items, embeddings):
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
                    succeeded = len(batch_items) - errors
                    logger.warning(f"⚠️ Bulk update had {errors} errors")
                else:
                    succeeded = len(batch_items)

                # Track processed IDs
                for item in batch_items:
                    self.processed_ids.add(item["id"])

                return {"succeeded": succeeded, "failed": len(batch_items) - succeeded}

            except Exception as e:
                logger.error(f"❌ Bulk update failed: {e}")
                return {"succeeded": 0, "failed": len(batch_items)}
        else:
            # Dry run
            for item in batch_items:
                self.processed_ids.add(item["id"])
            return {"succeeded": len(batch_items), "failed": 0}

    async def process_es_batch_concurrent(
        self,
        documents: List[Dict]
    ) -> Dict[str, int]:
        """Process ES batch with concurrent API calls"""
        if not documents:
            return {"processed": 0, "succeeded": 0, "failed": 0}

        # Prepare batch items
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
            return {"processed": 0, "succeeded": 0, "failed": 0}

        # Split into API batches
        api_batches = [
            batch_items[i:i + self.api_batch_size]
            for i in range(0, len(batch_items), self.api_batch_size)
        ]

        # Process API batches CONCURRENTLY
        tasks = [self.process_api_batch(batch) for batch in api_batches]
        results = await asyncio.gather(*tasks)

        # Aggregate results
        total_succeeded = sum(r["succeeded"] for r in results)
        total_failed = sum(r["failed"] for r in results)

        return {
            "processed": len(batch_items),
            "succeeded": total_succeeded,
            "failed": total_failed
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
            "processed_ids_count": len(self.processed_ids)
        }

        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint, f)

        logger.debug(f"💾 Checkpoint saved: {self.processed_count:,} docs")

    async def run(self):
        """Main execution loop"""
        logger.info("🏁 Starting OPTIMIZED batch embedding generation")
        logger.info(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        sort_values = None
        batch_num = 0

        try:
            while self.processed_count < self.target_documents:
                batch_num += 1

                # Get batch from ES
                documents, next_sort = await self.get_documents_batch(
                    sort_values=sort_values
                )

                if not documents:
                    logger.info("✅ No more documents to process")
                    break

                # Process batch with concurrent API calls
                batch_start = time.time()
                result = await self.process_es_batch_concurrent(documents)
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
                eta_hours = eta_minutes / 60

                progress_pct = (self.processed_count / self.target_documents) * 100

                logger.info(
                    f"📊 Batch {batch_num}: {result['succeeded']}/{result['processed']} succeeded "
                    f"in {batch_time:.1f}s | "
                    f"Progress: {self.processed_count:,}/{self.target_documents:,} ({progress_pct:.1f}%) | "
                    f"Rate: {rate:.0f} docs/min | "
                    f"ETA: {eta_hours:.1f}h ({eta_minutes:.0f}min) | "
                    f"Cost: ${self.total_cost:.2f}"
                )

                # Update sort for next batch
                sort_values = next_sort

                # Checkpoint every 10 batches
                if batch_num % 10 == 0:
                    await self.save_checkpoint()

                # Brief pause
                await asyncio.sleep(0.05)

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
        logger.info("📊 OPTIMIZED BATCH EMBEDDING REPORT")
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
            "session_id": f"optimized_batch_{int(self.start_time)}",
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
            "throughput_docs_per_minute": self.processed_count/(total_time/60),
            "configuration": {
                "es_batch_size": self.es_batch_size,
                "api_batch_size": self.api_batch_size,
                "concurrent_batches": self.concurrent_batches
            }
        }

        report_file = f"optimized_embedding_report_{int(self.start_time)}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"📁 Detailed report saved: {report_file}")

        # Cleanup
        await es_client.disconnect()


async def main():
    parser = argparse.ArgumentParser(
        description="Optimized Batch Embedding Generator - 24-48 Hour Target"
    )

    parser.add_argument(
        '--target',
        type=int,
        default=2_500_000,
        help='Target number of documents to process'
    )
    parser.add_argument(
        '--es-batch-size',
        type=int,
        default=1000,
        help='Number of documents to fetch from ES per batch'
    )
    parser.add_argument(
        '--api-batch-size',
        type=int,
        default=500,
        help='Number of texts per OpenAI API call (max 2048)'
    )
    parser.add_argument(
        '--concurrent-batches',
        type=int,
        default=5,
        help='Number of concurrent API batches to process'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run mode (no ES updates)'
    )

    args = parser.parse_args()

    logger.info("🎯 Optimized Batch Embedding Generator")
    logger.info(f"📋 Configuration: {vars(args)}")

    generator = OptimizedBatchEmbeddings(
        target_documents=args.target,
        es_batch_size=args.es_batch_size,
        api_batch_size=args.api_batch_size,
        concurrent_batches=args.concurrent_batches,
        dry_run=args.dry_run
    )

    if not await generator.initialize():
        logger.error("❌ Initialization failed, exiting")
        sys.exit(1)

    await generator.run()


if __name__ == "__main__":
    asyncio.run(main())
