#!/usr/bin/env python3
"""
Complete PSEO Page Generation Script
Generates all 414 remaining authority pages with checkpointing and validation
"""

import json
import os
import asyncio
from datetime import datetime
from typing import Dict, List
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.pseo.orchestrator import pSEOOrchestrator


class CompletePSEOGenerator:
    """Generate all PSEO pages with checkpointing and monitoring"""

    def __init__(self):
        self.output_dir = "outputs/pseo"
        self.checkpoint_file = f"{self.output_dir}/generation_checkpoint.json"
        self.orchestrator = pSEOOrchestrator(es_client=None)  # No ES needed

        # Stats
        self.total_generated = 0
        self.total_failed = 0
        self.total_cost = 0.0
        self.start_time = None
        self.results = []

    def load_authorities(self) -> List[Dict]:
        """Load authorities from authorities.json"""
        with open('authorities.json', 'r') as f:
            data = json.load(f)
        return data.get('authorities', [])

    def load_checkpoint(self) -> Dict:
        """Load checkpoint if exists"""
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        return {
            'completed': [],
            'failed': [],
            'last_index': 0,
            'total_cost': 0.0
        }

    def save_checkpoint(self, checkpoint: Dict):
        """Save checkpoint"""
        os.makedirs(self.output_dir, exist_ok=True)
        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)

    def get_already_generated(self) -> List[str]:
        """Get list of already generated slugs"""
        if not os.path.exists(self.output_dir):
            return []

        return [
            f.replace('.json', '')
            for f in os.listdir(self.output_dir)
            if f.endswith('.json') and f != 'generation_checkpoint.json'
        ]

    async def generate_single_page(self, authority: Dict, index: int, total: int) -> Dict:
        """Generate a single PSEO page"""
        slug = authority.get('slug', '')
        name = authority.get('name', 'Unknown')

        try:
            print(f"\n[{index + 1}/{total}] Generating: {name} ({slug})")
            print(f"{'='*80}")

            # Generate page
            start = datetime.now()
            page_data = await self.orchestrator.generate_page(authority)
            elapsed = (datetime.now() - start).total_seconds()

            # Save to file
            output_file = f"{self.output_dir}/{slug}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(page_data, f, indent=2, ensure_ascii=False)

            # Get stats
            cost = page_data.get('metadata', {}).get('generation_cost', 0.0)
            words = page_data.get('metadata', {}).get('total_words', 0)

            self.total_generated += 1
            self.total_cost += cost

            result = {
                'slug': slug,
                'name': name,
                'status': 'success',
                'cost': cost,
                'words': words,
                'elapsed': elapsed,
                'timestamp': datetime.now().isoformat()
            }

            print(f"✅ SUCCESS: {name}")
            print(f"   Cost: ${cost:.4f} | Words: {words} | Time: {elapsed:.1f}s")
            print(f"   Total Progress: {self.total_generated} completed, {self.total_failed} failed")
            print(f"   Total Cost: ${self.total_cost:.2f}")

            return result

        except Exception as e:
            self.total_failed += 1

            print(f"❌ FAILED: {name}")
            print(f"   Error: {str(e)}")

            return {
                'slug': slug,
                'name': name,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def generate_all(self, batch_size: int = 5, max_concurrent: int = 3):
        """Generate all pages with batching"""
        self.start_time = datetime.now()

        print(f"\n{'='*80}")
        print(f"PLANNING EXPLORER - COMPLETE PSEO GENERATION")
        print(f"{'='*80}")
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Batch Size: {batch_size}")
        print(f"Max Concurrent: {max_concurrent}")
        print(f"{'='*80}\n")

        # Load authorities and checkpoint
        all_authorities = self.load_authorities()
        already_generated = self.get_already_generated()
        checkpoint = self.load_checkpoint()

        # Filter out already generated
        remaining = [
            auth for auth in all_authorities
            if auth.get('slug') not in already_generated
        ]

        total_remaining = len(remaining)
        print(f"📊 Status:")
        print(f"   Total authorities: {len(all_authorities)}")
        print(f"   Already generated: {len(already_generated)}")
        print(f"   Remaining to generate: {total_remaining}")
        print(f"\n{'='*80}\n")

        if total_remaining == 0:
            print("✅ All pages already generated!")
            return

        # Process in batches
        semaphore = asyncio.Semaphore(max_concurrent)

        for batch_start in range(0, total_remaining, batch_size):
            batch_end = min(batch_start + batch_size, total_remaining)
            batch = remaining[batch_start:batch_end]
            batch_num = (batch_start // batch_size) + 1
            total_batches = (total_remaining + batch_size - 1) // batch_size

            print(f"\n{'='*80}")
            print(f"BATCH {batch_num}/{total_batches}")
            print(f"Processing {batch_start + 1} to {batch_end} of {total_remaining}")
            print(f"{'='*80}")

            # Process batch with concurrency control
            async def process_with_sem(auth, idx):
                async with semaphore:
                    return await self.generate_single_page(
                        auth,
                        batch_start + idx + len(already_generated),
                        len(all_authorities)
                    )

            tasks = [
                process_with_sem(auth, idx)
                for idx, auth in enumerate(batch)
            ]

            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Save results
            for result in batch_results:
                if isinstance(result, Exception):
                    print(f"❌ Exception: {result}")
                    self.results.append({
                        'status': 'exception',
                        'error': str(result)
                    })
                else:
                    self.results.append(result)

            # Update checkpoint
            checkpoint = {
                'completed': [r['slug'] for r in self.results if r.get('status') == 'success'],
                'failed': [r['slug'] for r in self.results if r.get('status') == 'failed'],
                'last_index': batch_end,
                'total_cost': self.total_cost,
                'results': self.results
            }
            self.save_checkpoint(checkpoint)

            # Progress summary
            print(f"\n{'='*80}")
            print(f"BATCH {batch_num} COMPLETE")
            print(f"{'='*80}")
            print(f"Generated so far: {self.total_generated}")
            print(f"Failed so far: {self.total_failed}")
            print(f"Total cost so far: ${self.total_cost:.2f}")
            elapsed_mins = (datetime.now() - self.start_time).total_seconds() / 60
            print(f"Elapsed time: {elapsed_mins:.1f} minutes")
            if self.total_generated > 0:
                print(f"Avg cost/page: ${self.total_cost / self.total_generated:.4f}")
                print(f"Avg time/page: {elapsed_mins * 60 / self.total_generated:.1f} seconds")
            print(f"{'='*80}\n")

            # Small delay between batches
            if batch_end < total_remaining:
                await asyncio.sleep(2)

        # Final summary
        self.print_final_summary(len(all_authorities))

    def print_final_summary(self, total_authorities: int):
        """Print final generation summary"""
        elapsed = (datetime.now() - self.start_time).total_seconds()

        print(f"\n\n{'='*80}")
        print(f"🎉 PSEO GENERATION COMPLETE!")
        print(f"{'='*80}")
        print(f"\n📊 FINAL STATISTICS:")
        print(f"   Total Authorities: {total_authorities}")
        print(f"   Successfully Generated: {self.total_generated}")
        print(f"   Failed: {self.total_failed}")
        print(f"   Success Rate: {(self.total_generated / (self.total_generated + self.total_failed) * 100):.1f}%")

        print(f"\n💰 COST BREAKDOWN:")
        print(f"   Total Cost: ${self.total_cost:.2f}")
        print(f"   Avg Cost/Page: ${self.total_cost / self.total_generated:.4f}" if self.total_generated > 0 else "   N/A")

        print(f"\n⏱️  TIME BREAKDOWN:")
        print(f"   Total Time: {elapsed / 3600:.2f} hours")
        print(f"   Avg Time/Page: {elapsed / self.total_generated:.1f} seconds" if self.total_generated > 0 else "   N/A")
        print(f"   Pages/Hour: {self.total_generated / (elapsed / 3600):.1f}" if elapsed > 0 else "   N/A")

        print(f"\n📁 OUTPUT:")
        print(f"   Location: {self.output_dir}/")
        print(f"   Total Files: {len(os.listdir(self.output_dir))}")

        print(f"\n{'='*80}\n")

        # Save final report
        report = {
            'generation_complete': True,
            'timestamp': datetime.now().isoformat(),
            'statistics': {
                'total_authorities': total_authorities,
                'generated': self.total_generated,
                'failed': self.total_failed,
                'success_rate': (self.total_generated / (self.total_generated + self.total_failed) * 100) if (self.total_generated + self.total_failed) > 0 else 0
            },
            'costs': {
                'total': self.total_cost,
                'average_per_page': self.total_cost / self.total_generated if self.total_generated > 0 else 0
            },
            'time': {
                'elapsed_seconds': elapsed,
                'elapsed_hours': elapsed / 3600,
                'avg_seconds_per_page': elapsed / self.total_generated if self.total_generated > 0 else 0
            },
            'results': self.results
        }

        report_file = f"{self.output_dir}/generation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"📄 Full report saved to: {report_file}\n")


async def main():
    """Main execution"""
    generator = CompletePSEOGenerator()
    await generator.generate_all(batch_size=10, max_concurrent=5)


if __name__ == "__main__":
    asyncio.run(main())
