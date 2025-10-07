#!/usr/bin/env python3
"""
Regenerate the 11 Original PSEO Pages
Quick recovery script to restore the working pages
"""

import json
import os
import asyncio
from datetime import datetime
from typing import Dict
import sys
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.pseo.orchestrator import pSEOOrchestrator


# The 11 original authorities that need to be restored
ORIGINAL_11 = [
    'york',
    'cornwall',
    'birmingham',
    'brighton-and-hove',
    'bristol',
    'cambridge',
    'hillingdon',
    'leeds',
    'manchester',
    'oxford',
    'westminster'
]


async def regenerate_original_11():
    """Regenerate the 11 original PSEO pages"""

    print(f"\n{'='*80}")
    print(f"REGENERATING 11 ORIGINAL PSEO PAGES")
    print(f"{'='*80}\n")

    # Load all authorities
    with open('authorities.json', 'r') as f:
        data = json.load(f)
    all_authorities = data.get('authorities', [])

    # Filter to just the 11 we need
    authorities_to_generate = [
        auth for auth in all_authorities
        if auth.get('slug') in ORIGINAL_11
    ]

    print(f"Found {len(authorities_to_generate)} authorities to regenerate\n")

    # Create orchestrator
    orchestrator = pSEOOrchestrator(es_client=None)
    output_dir = "outputs/pseo"
    os.makedirs(output_dir, exist_ok=True)

    # Stats
    successful = 0
    failed = 0
    total_cost = 0.0

    # Generate each page
    for i, authority in enumerate(authorities_to_generate, 1):
        slug = authority.get('slug', '')
        name = authority.get('name', 'Unknown')

        try:
            print(f"[{i}/11] Generating: {name} ({slug})")
            print(f"{'='*80}")

            # Generate page
            start = datetime.now()
            page_data = await orchestrator.generate_page(authority)
            elapsed = (datetime.now() - start).total_seconds()

            # Save to file
            output_file = f"{output_dir}/{slug}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(page_data, f, indent=2, ensure_ascii=False)

            # Get stats
            cost = page_data.get('metadata', {}).get('generation_cost', 0.0)
            words = page_data.get('metadata', {}).get('total_words', 0)

            successful += 1
            total_cost += cost

            print(f"✅ SUCCESS: {name}")
            print(f"   Cost: ${cost:.4f} | Words: {words:,} | Time: {elapsed:.1f}s")
            print(f"   Progress: {successful}/{11} completed\n")

        except Exception as e:
            failed += 1
            print(f"❌ FAILED: {name}")
            print(f"   Error: {str(e)}\n")
            continue

    # Final summary
    print(f"\n{'='*80}")
    print(f"REGENERATION COMPLETE")
    print(f"{'='*80}")
    print(f"Successfully generated: {successful}/11")
    print(f"Failed: {failed}/11")
    print(f"Total cost: ${total_cost:.2f}")
    print(f"Average cost per page: ${total_cost/successful:.4f}" if successful > 0 else "N/A")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    asyncio.run(regenerate_original_11())
