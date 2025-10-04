"""
Elasticsearch Backfill Script
Populate new Content Discovery fields on existing 2.3M documents

This script applies the content_discovery_enrichment pipeline to all
existing documents in the planning_applications index.

Estimated time: 30-60 minutes for 2.3M documents
"""
import asyncio
import time
from elasticsearch import Elasticsearch
from datetime import datetime

# ES Connection
ES_HOST = 'https://95.217.117.251:9200/'
ES_USER = 'elastic'
ES_PASS = 'd41=*sDuOnhQqXonYz2U'

def run_backfill():
    """
    Run backfill using _update_by_query with the ingest pipeline

    This will:
    1. Process all documents in batches
    2. Apply content_discovery_enrichment pipeline
    3. Populate: authority_slug, location_slug, decision_days, is_approved
    """

    print("=" * 70)
    print("ES BACKFILL - Content Discovery Field Population")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Connect to ES
    es = Elasticsearch(
        ES_HOST,
        basic_auth=(ES_USER, ES_PASS),
        verify_certs=False,
        ssl_show_warn=False,
        request_timeout=300  # 5 minute timeout for large operations
    )

    # Check connection
    if not es.ping():
        print("❌ Failed to connect to Elasticsearch")
        return False

    print("✅ Connected to Elasticsearch")

    # Get total document count
    count_response = es.count(index='planning_applications')
    total_docs = count_response['count']
    print(f"📊 Total documents to process: {total_docs:,}")
    print()

    # Check if pipeline exists
    try:
        pipeline_exists = es.ingest.get_pipeline(id='content_discovery_enrichment')
        print("✅ Ingest pipeline 'content_discovery_enrichment' exists")
        print()
    except:
        print("❌ Ingest pipeline 'content_discovery_enrichment' not found")
        print("   Run create_ingest_pipeline.py first")
        return False

    # Run update_by_query with pipeline
    print("🚀 Starting backfill with _update_by_query...")
    print("   This will run in the background and may take 30-60 minutes")
    print("   Processing in batches of 1000 documents")
    print()

    start_time = time.time()

    try:
        # Run update_by_query with pipeline
        # Using wait_for_completion=False for async execution on large dataset
        response = es.update_by_query(
            index='planning_applications',
            body={
                "query": {
                    "match_all": {}
                }
            },
            pipeline='content_discovery_enrichment',
            wait_for_completion=False,  # Run async and return task ID
            slices='auto',  # Parallel processing across shards
            scroll='5m',
            conflicts='proceed',  # Continue on version conflicts
            refresh=True
        )

        elapsed_time = time.time() - start_time

        # Check if async task was created
        if 'task' in response:
            task_id = response['task']
            print("✅ Backfill task started!")
            print()
            print("=" * 70)
            print("ASYNC BACKFILL TASK")
            print("=" * 70)
            print(f"Task ID: {task_id}")
            print(f"Processing 2.3M documents in the background...")
            print()
            print("To check progress, run:")
            print(f"  curl -k -u elastic:d41=*sDuOnhQqXonYz2U 'https://95.217.117.251:9200/_tasks/{task_id}'")
            print()
            print("Or use the status check:")
            print(f"  python3 run_es_backfill.py status")
            print("=" * 70)
            print()
        else:
            # Synchronous completion (shouldn't happen with wait_for_completion=False)
            print("✅ Backfill completed!")
            print()
            print("=" * 70)
            print("BACKFILL RESULTS")
            print("=" * 70)
            print(f"Total documents: {response.get('total', 0):,}")
            print(f"Updated: {response.get('updated', 0):,}")
            print(f"Failures: {response.get('failures', [])}")
            print(f"Version conflicts: {response.get('version_conflicts', 0):,}")
            print(f"Time taken: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
            print(f"Rate: {response.get('total', 0) / elapsed_time:.0f} docs/second")
            print("=" * 70)
            print()

        # Verify results by checking a sample document
        print("🔍 Verifying backfill results...")
        sample = es.search(
            index='planning_applications',
            body={
                "query": {"match_all": {}},
                "size": 1
            }
        )

        if sample['hits']['hits']:
            doc = sample['hits']['hits'][0]['_source']
            print("\nSample document fields:")
            print(f"  authority_slug: {doc.get('authority_slug', 'NOT SET')}")
            print(f"  location_slug: {doc.get('location_slug', 'NOT SET')}")
            print(f"  decision_days: {doc.get('decision_days', 'NOT SET')}")
            print(f"  is_approved: {doc.get('is_approved', 'NOT SET')}")
            print()

        # Check how many documents have decision_days populated
        decision_days_count = es.count(
            index='planning_applications',
            body={
                "query": {
                    "exists": {"field": "decision_days"}
                }
            }
        )

        print(f"✅ Documents with decision_days: {decision_days_count['count']:,} / {total_docs:,}")
        print(f"   ({decision_days_count['count'] / total_docs * 100:.1f}%)")
        print()

        print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"\n❌ Backfill failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def check_backfill_status():
    """
    Check the status of fields population
    Useful for monitoring progress
    """
    es = Elasticsearch(
        ES_HOST,
        basic_auth=(ES_USER, ES_PASS),
        verify_certs=False,
        ssl_show_warn=False
    )

    if not es.ping():
        print("❌ Failed to connect to Elasticsearch")
        return

    print("=" * 70)
    print("BACKFILL STATUS CHECK")
    print("=" * 70)

    total = es.count(index='planning_applications')['count']

    # Check each new field
    fields_to_check = [
        'authority_slug',
        'location_slug',
        'decision_days',
        'is_approved'
    ]

    for field in fields_to_check:
        count = es.count(
            index='planning_applications',
            body={
                "query": {
                    "exists": {"field": field}
                }
            }
        )['count']

        percentage = (count / total * 100) if total > 0 else 0
        status = "✅" if percentage > 90 else "⚠️" if percentage > 50 else "❌"
        print(f"{status} {field:20s}: {count:>10,} / {total:,} ({percentage:>5.1f}%)")

    print("=" * 70)


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'status':
        # Check status only
        check_backfill_status()
    else:
        # Run backfill
        print("\n⚠️  WARNING: This will update 2.3M documents")
        print("   Estimated time: 30-60 minutes")
        print("   This is a one-time operation")
        print()

        confirm = input("Continue? (yes/no): ").strip().lower()

        if confirm == 'yes':
            success = run_backfill()
            sys.exit(0 if success else 1)
        else:
            print("❌ Backfill cancelled")
            sys.exit(1)
