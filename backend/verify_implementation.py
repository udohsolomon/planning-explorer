#!/usr/bin/env python3
"""
Verification script for stats overview endpoint implementation
Checks that all code is properly integrated without starting the server
"""

import sys
import importlib.util

def check_file_exists(filepath, description):
    """Check if a file exists"""
    try:
        with open(filepath, 'r') as f:
            print(f"✅ {description}: {filepath}")
            return True
    except FileNotFoundError:
        print(f"❌ {description}: {filepath} NOT FOUND")
        return False

def check_function_exists(module_path, function_name, description):
    """Check if a function exists in a module"""
    try:
        spec = importlib.util.spec_from_file_location("module", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, function_name):
            print(f"✅ {description}: {function_name}() found in {module_path}")
            return True
        else:
            print(f"❌ {description}: {function_name}() NOT FOUND in {module_path}")
            return False
    except Exception as e:
        print(f"❌ {description}: Error loading {module_path} - {str(e)}")
        return False

def check_string_in_file(filepath, search_string, description):
    """Check if a string exists in a file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            if search_string in content:
                print(f"✅ {description}: '{search_string}' found")
                return True
            else:
                print(f"❌ {description}: '{search_string}' NOT FOUND")
                return False
    except Exception as e:
        print(f"❌ {description}: Error reading {filepath} - {str(e)}")
        return False

def main():
    print("=" * 70)
    print("Platform Overview Statistics Endpoint - Implementation Verification")
    print("=" * 70)
    print()

    all_checks_passed = True

    # Check 1: API endpoint file exists and has the overview route
    print("1. Checking API Endpoint File...")
    print("-" * 70)
    endpoint_file = "app/api/endpoints/stats.py"
    all_checks_passed &= check_file_exists(endpoint_file, "Stats endpoint file")
    all_checks_passed &= check_string_in_file(
        endpoint_file,
        '@router.get("/overview")',
        "Overview route decorator"
    )
    all_checks_passed &= check_string_in_file(
        endpoint_file,
        "get_platform_overview_stats_cached",
        "Service function import"
    )
    print()

    # Check 2: Elasticsearch stats service file
    print("2. Checking Elasticsearch Stats Service...")
    print("-" * 70)
    service_file = "app/services/elasticsearch_stats.py"
    all_checks_passed &= check_file_exists(service_file, "ES stats service file")
    all_checks_passed &= check_string_in_file(
        service_file,
        "async def get_platform_overview_stats_cached",
        "Platform overview stats function"
    )
    all_checks_passed &= check_string_in_file(
        service_file,
        "totalApplications",
        "Response field: totalApplications"
    )
    all_checks_passed &= check_string_in_file(
        service_file,
        "totalDecisions",
        "Response field: totalDecisions"
    )
    all_checks_passed &= check_string_in_file(
        service_file,
        "totalGranted",
        "Response field: totalGranted"
    )
    all_checks_passed &= check_string_in_file(
        service_file,
        "grantedPercentage",
        "Response field: grantedPercentage"
    )
    all_checks_passed &= check_string_in_file(
        service_file,
        "applicationsYoY",
        "Response field: applicationsYoY"
    )
    print()

    # Check 3: Caching implementation
    print("3. Checking Caching Implementation...")
    print("-" * 70)
    all_checks_passed &= check_string_in_file(
        service_file,
        "stats_cache",
        "Cache instance"
    )
    all_checks_passed &= check_string_in_file(
        service_file,
        'cache_key = get_cache_key("platform_overview")',
        "Cache key generation"
    )
    all_checks_passed &= check_string_in_file(
        service_file,
        "stats_cache[cache_key] = stats",
        "Cache storage"
    )
    print()

    # Check 4: Elasticsearch queries
    print("4. Checking Elasticsearch Queries...")
    print("-" * 70)
    all_checks_passed &= check_string_in_file(
        service_file,
        "es_client.count",
        "ES count query usage"
    )
    all_checks_passed &= check_string_in_file(
        service_file,
        "planning_applications",
        "Index name"
    )
    all_checks_passed &= check_string_in_file(
        service_file,
        "decided_date",
        "Decision date field"
    )
    all_checks_passed &= check_string_in_file(
        service_file,
        "app_state.keyword",
        "Application state field"
    )
    print()

    # Check 5: YoY calculations
    print("5. Checking YoY Calculations...")
    print("-" * 70)
    all_checks_passed &= check_string_in_file(
        service_file,
        "2023-10-01",
        "Current year start date"
    )
    all_checks_passed &= check_string_in_file(
        service_file,
        "2024-09-30",
        "Current year end date"
    )
    all_checks_passed &= check_string_in_file(
        service_file,
        "2022-10-01",
        "Previous year start date"
    )
    all_checks_passed &= check_string_in_file(
        service_file,
        "2023-09-30",
        "Previous year end date"
    )
    print()

    # Check 6: Error handling and logging
    print("6. Checking Error Handling and Logging...")
    print("-" * 70)
    all_checks_passed &= check_string_in_file(
        service_file,
        "logger.info",
        "Info logging"
    )
    all_checks_passed &= check_string_in_file(
        service_file,
        "logger.error",
        "Error logging"
    )
    all_checks_passed &= check_string_in_file(
        service_file,
        "except Exception",
        "Exception handling"
    )
    print()

    # Check 7: Test script exists
    print("7. Checking Test Script...")
    print("-" * 70)
    all_checks_passed &= check_file_exists(
        "test_stats_overview.sh",
        "Test script"
    )
    print()

    # Check 8: Documentation exists
    print("8. Checking Documentation...")
    print("-" * 70)
    all_checks_passed &= check_file_exists(
        "STATS_OVERVIEW_IMPLEMENTATION.md",
        "Implementation documentation"
    )
    print()

    # Final summary
    print("=" * 70)
    if all_checks_passed:
        print("✅ ALL CHECKS PASSED - Implementation verified successfully!")
        print()
        print("Next steps:")
        print("1. Start the backend server:")
        print("   python -m uvicorn app.main:app --reload")
        print()
        print("2. Test the endpoint:")
        print("   ./test_stats_overview.sh")
        print()
        print("3. Check the API documentation:")
        print("   http://localhost:8000/docs")
        print("=" * 70)
        return 0
    else:
        print("❌ SOME CHECKS FAILED - Please review the errors above")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(main())
