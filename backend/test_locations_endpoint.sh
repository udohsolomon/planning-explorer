#!/bin/bash

# Test script for Location Statistics Endpoint
# Planning Explorer - Geospatial Intelligence Testing

BASE_URL="http://localhost:8000/api/v1/stats/locations"

echo "========================================="
echo "Location Statistics Endpoint Test Suite"
echo "========================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to test endpoint
test_endpoint() {
    local test_name=$1
    local url=$2
    local expected_status=$3

    echo "Testing: $test_name"
    echo "URL: $url"

    response=$(curl -s -w "\n%{http_code}" "$url")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" -eq "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} - HTTP $http_code"
        ((TESTS_PASSED++))

        # Pretty print JSON if status is 200
        if [ "$http_code" -eq 200 ]; then
            echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
        fi
    else
        echo -e "${RED}✗ FAIL${NC} - Expected HTTP $expected_status, got HTTP $http_code"
        echo "Response: $body"
        ((TESTS_FAILED++))
    fi
    echo ""
    echo "---"
    echo ""
}

# Test 1: List all available locations
test_endpoint \
    "List all available locations" \
    "$BASE_URL/" \
    200

# Test 2: Get London stats with default radius (5km)
test_endpoint \
    "Get London stats (default 5km radius)" \
    "$BASE_URL/london" \
    200

# Test 3: Get Manchester stats with custom radius
test_endpoint \
    "Get Manchester stats (10km radius)" \
    "$BASE_URL/manchester?radius_km=10" \
    200

# Test 4: Get Birmingham stats with max radius
test_endpoint \
    "Get Birmingham stats (50km radius)" \
    "$BASE_URL/birmingham?radius_km=50" \
    200

# Test 5: Get Liverpool stats with min radius
test_endpoint \
    "Get Liverpool stats (1km radius)" \
    "$BASE_URL/liverpool?radius_km=1" \
    200

# Test 6: Get Bristol stats with force refresh
test_endpoint \
    "Get Bristol stats (force refresh)" \
    "$BASE_URL/bristol?radius_km=5&force_refresh=true" \
    200

# Test 7: Get Bournemouth stats with custom date range
test_endpoint \
    "Get Bournemouth stats (custom date range)" \
    "$BASE_URL/bournemouth?radius_km=8&date_from=now-6M/M&date_to=now/M" \
    200

# Test 8: Invalid location slug
test_endpoint \
    "Invalid location (should return 404)" \
    "$BASE_URL/invalid-location" \
    404

# Test 9: Invalid radius (too small)
test_endpoint \
    "Invalid radius - too small (should return 422)" \
    "$BASE_URL/london?radius_km=0" \
    422

# Test 10: Invalid radius (too large)
test_endpoint \
    "Invalid radius - too large (should return 422)" \
    "$BASE_URL/london?radius_km=51" \
    422

# Test 11: Health check
test_endpoint \
    "Location stats health check" \
    "$BASE_URL/health" \
    200

# Test 12: Multiple locations for comparison
echo "Testing multiple locations in sequence..."
for location in poole leeds edinburgh oxford; do
    test_endpoint \
        "Get $location stats (5km radius)" \
        "$BASE_URL/$location?radius_km=5" \
        200
done

# Performance test
echo "========================================="
echo "Performance Test"
echo "========================================="
echo ""
echo "Testing cached vs uncached response times..."

# First request (uncached)
echo "Request 1 (uncached):"
time curl -s "$BASE_URL/london?radius_km=5" > /dev/null
echo ""

# Second request (cached)
echo "Request 2 (cached - should be faster):"
time curl -s "$BASE_URL/london?radius_km=5" > /dev/null
echo ""

# Summary
echo "========================================="
echo "Test Summary"
echo "========================================="
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Please review the output above.${NC}"
    exit 1
fi
