"""
Monitor Elasticsearch backfill task progress
"""
import requests
import json
import time
import sys
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

TASK_ID = "2iqqEcptRFmrkMI7OWyjwA:887491140"
ES_HOST = "https://95.217.117.251:9200"
ES_USER = "elastic"
ES_PASS = "d41=*sDuOnhQqXonYz2U"

def check_task_progress():
    """Check task progress and display status"""
    url = f"{ES_HOST}/_tasks/{TASK_ID}"

    try:
        response = requests.get(url, auth=(ES_USER, ES_PASS), verify=False)
        data = response.json()

        completed = data.get('completed', False)

        if completed:
            # Task finished - get final results
            print("\n" + "=" * 70)
            print("✅ BACKFILL COMPLETED!")
            print("=" * 70)

            if 'response' in data:
                result = data['response']
                print(f"Total documents: {result.get('total', 0):,}")
                print(f"Updated: {result.get('updated', 0):,}")
                print(f"Deleted: {result.get('deleted', 0):,}")
                print(f"Version conflicts: {result.get('version_conflicts', 0):,}")
                print(f"Failures: {len(result.get('failures', []))}")

                if result.get('failures'):
                    print("\n⚠️  Some failures occurred:")
                    for failure in result.get('failures', [])[:5]:
                        print(f"  - {failure}")

            print("=" * 70)
            return True

        # Task still running
        task = data['task']
        status = task['status']

        total = status['total']
        updated = status['updated']
        progress_pct = (updated / total * 100) if total > 0 else 0

        runtime_sec = task['running_time_in_nanos'] / 1e9
        rate = updated / runtime_sec if runtime_sec > 0 else 0
        remaining_docs = total - updated
        remaining_time = remaining_docs / rate if rate > 0 else 0

        print(f"\r⏳ Progress: {updated:,} / {total:,} ({progress_pct:.1f}%) | "
              f"Rate: {rate:.0f} docs/sec | "
              f"ETA: {remaining_time/60:.1f} min", end='', flush=True)

        return False

    except Exception as e:
        print(f"\n❌ Error checking task: {str(e)}")
        return False

def monitor_continuous():
    """Monitor task progress continuously"""
    print("🔍 Monitoring backfill task progress...")
    print(f"Task ID: {TASK_ID}")
    print()

    while True:
        completed = check_task_progress()
        if completed:
            break
        time.sleep(5)  # Check every 5 seconds

    print("\n\n✅ Monitoring complete!")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'once':
        check_task_progress()
        print()
    else:
        monitor_continuous()
