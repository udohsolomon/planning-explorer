"""
Batch Processor for All 425 Authorities
Processes all authorities with rate limiting, progress tracking, and cost monitoring
"""

from typing import Dict, List, Optional
from elasticsearch import AsyncElasticsearch
from datetime import datetime
import asyncio
import json
import os
from .orchestrator import pSEOOrchestrator


class BatchProcessor:
    """
    Batch process all 425 UK planning authorities.
    Features: Rate limiting, progress tracking, cost monitoring, resume capability.
    """

    def __init__(self, es_client: AsyncElasticsearch):
        self.es = es_client
        self.orchestrator = pSEOOrchestrator(es_client)

        # Configuration
        self.max_concurrent = int(os.getenv('PSEO_MAX_CONCURRENT', '3'))
        self.batch_size = int(os.getenv('PSEO_BATCH_SIZE', '10'))
        self.output_dir = os.getenv('PSEO_OUTPUT_DIR', './outputs/pseo')

        # Tracking
        self.results: List[Dict] = []
        self.total_cost = 0.0
        self.start_time = None
        self.processed_count = 0
        self.failed_count = 0

    async def get_all_authorities(self) -> List[Dict]:
        """Fetch all 425 authorities from database"""

        # Query authorities (adjust based on your schema)
        query = {
            "query": {"match_all": {}},
            "size": 425,
            "_source": ["id", "name", "type", "region", "website_url", "slug", "population"]
        }

        result = await self.es.search(index="local_authorities", body=query)

        authorities = [
            {
                "id": hit['_source'].get('id'),
                "name": hit['_source'].get('name'),
                "type": hit['_source'].get('type', 'Local Authority'),
                "region": hit['_source'].get('region', 'UK'),
                "website_url": hit['_source'].get('website_url', ''),
                "slug": hit['_source'].get('slug', ''),
                "population": hit['_source'].get('population', 0)
            }
            for hit in result['hits']['hits']
        ]

        return authorities

    async def process_all_authorities(
        self,
        max_cost: Optional[float] = None,
        start_from: int = 0,
        limit: Optional[int] = None
    ) -> Dict:
        """
        Process all authorities with rate limiting and cost control.

        Args:
            max_cost: Maximum total cost to spend (stops when reached)
            start_from: Resume from specific authority index
            limit: Limit number of authorities to process
        """

        self.start_time = datetime.now()

        print(f"\n{'='*80}")
        print(f"BATCH pSEO GENERATION - Planning Explorer")
        print(f"{'='*80}")
        print(f"Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Max concurrent: {self.max_concurrent}")
        print(f"Max cost: ${max_cost if max_cost else 'No limit'}")
        print(f"{'='*80}\n")

        # Get authorities
        authorities = await self.get_all_authorities()

        if start_from > 0:
            authorities = authorities[start_from:]
            print(f"Resuming from authority #{start_from + 1}")

        if limit:
            authorities = authorities[:limit]
            print(f"Limited to {limit} authorities")

        total_authorities = len(authorities)
        print(f"Total authorities to process: {total_authorities}\n")

        # Process in batches with concurrency limit
        semaphore = asyncio.Semaphore(self.max_concurrent)

        for i in range(0, total_authorities, self.batch_size):
            batch = authorities[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1

            print(f"\n{'='*80}")
            print(f"BATCH {batch_num}/{(total_authorities + self.batch_size - 1) // self.batch_size}")
            print(f"Processing authorities {i + 1} to {min(i + self.batch_size, total_authorities)}")
            print(f"{'='*80}\n")

            # Process batch
            tasks = [
                self.process_single_authority(auth, semaphore, i + idx + 1, total_authorities)
                for idx, auth in enumerate(batch)
            ]

            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            self.results.extend(batch_results)

            # Check cost limit
            if max_cost and self.total_cost >= max_cost:
                print(f"\n⚠️  Cost limit reached: ${self.total_cost:.2f} >= ${max_cost}")
                print(f"Stopping batch processing...")
                break

            # Progress update
            self._print_progress_update()

            # Save checkpoint
            await self._save_checkpoint()

        # Final summary
        summary = self._generate_summary(total_authorities)
        await self._save_summary(summary)

        return summary

    async def process_single_authority(
        self,
        authority: Dict,
        semaphore: asyncio.Semaphore,
        index: int,
        total: int
    ) -> Dict:
        """Process single authority with semaphore control"""

        async with semaphore:
            try:
                print(f"[{index}/{total}] Processing {authority['name']}...")

                # Generate page
                page = await self.orchestrator.generate_page(authority)

                # Track results
                page_cost = page.get('metadata', {}).get('generation_cost', 0)
                self.total_cost += page_cost
                self.processed_count += 1

                result = {
                    "authority_id": authority['id'],
                    "authority_name": authority['name'],
                    "status": "success",
                    "timestamp": datetime.now().isoformat(),
                    "cost": page_cost,
                    "word_count": page.get('metadata', {}).get('total_words', 0),
                    "scraper_used": page.get('metadata', {}).get('scraper_used', 'unknown')
                }

                print(f"  ✅ {authority['name']} completed (${page_cost:.4f}, {result['word_count']} words)")

                return result

            except Exception as e:
                self.failed_count += 1

                print(f"  ❌ {authority['name']} failed: {e}")

                return {
                    "authority_id": authority['id'],
                    "authority_name": authority['name'],
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }

    def _print_progress_update(self):
        """Print progress update"""

        elapsed = (datetime.now() - self.start_time).total_seconds()
        elapsed_mins = elapsed / 60

        print(f"\n{'='*80}")
        print(f"PROGRESS UPDATE")
        print(f"{'='*80}")
        print(f"Processed: {self.processed_count}")
        print(f"Failed: {self.failed_count}")
        print(f"Total cost: ${self.total_cost:.2f}")
        print(f"Elapsed time: {elapsed_mins:.1f} minutes")

        if self.processed_count > 0:
            avg_cost = self.total_cost / self.processed_count
            avg_time = elapsed / self.processed_count
            print(f"Average cost per page: ${avg_cost:.4f}")
            print(f"Average time per page: {avg_time:.1f} seconds")

        print(f"{'='*80}\n")

    def _generate_summary(self, total: int) -> Dict:
        """Generate final summary"""

        elapsed = (datetime.now() - self.start_time).total_seconds()
        successful = [r for r in self.results if r.get('status') == 'success']
        failed = [r for r in self.results if r.get('status') == 'error']

        summary = {
            "batch_info": {
                "start_time": self.start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "elapsed_seconds": elapsed,
                "elapsed_minutes": elapsed / 60,
                "elapsed_hours": elapsed / 3600
            },
            "statistics": {
                "total_authorities": total,
                "processed": len(self.results),
                "successful": len(successful),
                "failed": len(failed),
                "success_rate": (len(successful) / len(self.results) * 100) if self.results else 0
            },
            "costs": {
                "total_cost": self.total_cost,
                "avg_cost_per_page": self.total_cost / len(successful) if successful else 0,
                "scraping_cost": sum(1 for r in successful if r.get('scraper_used') == 'Firecrawl') * 0.003,
                "content_generation_cost": self.total_cost
            },
            "content_stats": {
                "total_words": sum(r.get('word_count', 0) for r in successful),
                "avg_words_per_page": sum(r.get('word_count', 0) for r in successful) / len(successful) if successful else 0
            },
            "scraper_usage": {
                "playwright": sum(1 for r in successful if r.get('scraper_used') == 'Playwright'),
                "firecrawl": sum(1 for r in successful if r.get('scraper_used') == 'Firecrawl')
            },
            "performance": {
                "avg_time_per_page": elapsed / len(self.results) if self.results else 0,
                "pages_per_hour": (len(self.results) / elapsed * 3600) if elapsed > 0 else 0
            },
            "results": self.results
        }

        return summary

    async def _save_checkpoint(self):
        """Save checkpoint for resume capability"""

        checkpoint = {
            "processed_count": self.processed_count,
            "failed_count": self.failed_count,
            "total_cost": self.total_cost,
            "results": self.results,
            "timestamp": datetime.now().isoformat()
        }

        checkpoint_file = f"{self.output_dir}/checkpoint.json"
        os.makedirs(self.output_dir, exist_ok=True)

        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)

    async def _save_summary(self, summary: Dict):
        """Save final summary"""

        summary_file = f"{self.output_dir}/batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs(self.output_dir, exist_ok=True)

        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\n{'='*80}")
        print(f"BATCH PROCESSING COMPLETE")
        print(f"{'='*80}")
        print(f"Total processed: {summary['statistics']['processed']}")
        print(f"Successful: {summary['statistics']['successful']}")
        print(f"Failed: {summary['statistics']['failed']}")
        print(f"Success rate: {summary['statistics']['success_rate']:.1f}%")
        print(f"Total cost: ${summary['costs']['total_cost']:.2f}")
        print(f"Avg cost/page: ${summary['costs']['avg_cost_per_page']:.4f}")
        print(f"Total time: {summary['batch_info']['elapsed_hours']:.2f} hours")
        print(f"Avg time/page: {summary['performance']['avg_time_per_page']:.1f} seconds")
        print(f"Summary saved to: {summary_file}")
        print(f"{'='*80}\n")

    async def resume_from_checkpoint(self) -> Dict:
        """Resume batch processing from last checkpoint"""

        checkpoint_file = f"{self.output_dir}/checkpoint.json"

        if not os.path.exists(checkpoint_file):
            print("No checkpoint found. Starting fresh.")
            return await self.process_all_authorities()

        with open(checkpoint_file, 'r') as f:
            checkpoint = json.load(f)

        print(f"\nResuming from checkpoint:")
        print(f"  Previous processed: {checkpoint['processed_count']}")
        print(f"  Previous cost: ${checkpoint['total_cost']:.2f}")

        # Restore state
        self.results = checkpoint['results']
        self.processed_count = checkpoint['processed_count']
        self.failed_count = checkpoint['failed_count']
        self.total_cost = checkpoint['total_cost']

        # Resume from where we left off
        return await self.process_all_authorities(start_from=self.processed_count)


# CLI for batch processing
async def main():
    """CLI for batch processing"""

    import argparse
    from elasticsearch import AsyncElasticsearch

    parser = argparse.ArgumentParser(description='Batch process pSEO pages for all authorities')
    parser.add_argument('--all', action='store_true', help='Process all 425 authorities')
    parser.add_argument('--limit', type=int, help='Limit number of authorities')
    parser.add_argument('--max-cost', type=float, help='Maximum total cost')
    parser.add_argument('--start-from', type=int, default=0, help='Start from authority index')
    parser.add_argument('--resume', action='store_true', help='Resume from checkpoint')
    parser.add_argument('--es-host', type=str, default='localhost:9200', help='Elasticsearch host')

    args = parser.parse_args()

    # Connect to Elasticsearch
    es = AsyncElasticsearch([f"http://{args.es_host}"])

    # Create processor
    processor = BatchProcessor(es)

    # Run batch
    if args.resume:
        summary = await processor.resume_from_checkpoint()
    else:
        summary = await processor.process_all_authorities(
            max_cost=args.max_cost,
            start_from=args.start_from,
            limit=args.limit
        )

    await es.close()

    # Exit with appropriate code
    exit(0 if summary['statistics']['success_rate'] == 100 else 1)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
