#!/usr/bin/env python3
"""
Bulk Import PSEO Pages to Elasticsearch
Imports all JSON files from outputs/pseo/ into ES pseo_pages index
"""

import json
import os
import glob
import asyncio
from datetime import datetime
from app.db.elasticsearch import es_client


async def bulk_import():
    """Import all PSEO JSON files to Elasticsearch"""

    print(f"\n{'='*80}")
    print(f"BULK IMPORT TO ELASTICSEARCH")
    print(f"{'='*80}\n")

    # Find all JSON files
    json_dir = "outputs/pseo"
    json_files = glob.glob(f"{json_dir}/*.json")
    json_files = [f for f in json_files if not f.endswith('checkpoint.json')]

    print(f"Found {len(json_files)} PSEO pages to import\n")

    imported = 0
    failed = 0

    for json_file in json_files:
        try:
            # Load JSON
            with open(json_file, 'r', encoding='utf-8') as f:
                page_data = json.load(f)

            authority_id = page_data.get('authority_id')
            slug = page_data.get('url_slug')

            # Import to ES
            await es_client.client.index(
                index="pseo_pages",
                id=authority_id,
                body=page_data
            )

            imported += 1
            print(f"✅ [{imported}/{len(json_files)}] Imported: {slug}")

        except Exception as e:
            failed += 1
            print(f"❌ Failed: {os.path.basename(json_file)} - {e}")

    print(f"\n{'='*80}")
    print(f"IMPORT COMPLETE")
    print(f"{'='*80}")
    print(f"Successfully imported: {imported}")
    print(f"Failed: {failed}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    asyncio.run(bulk_import())
