#!/bin/bash

# Test script for /v1/stats/overview endpoint
# Tests the platform statistics endpoint for the homepage stats bar

echo "=========================================="
echo "Testing /v1/stats/overview endpoint"
echo "=========================================="
echo ""

BASE_URL="http://localhost:8000/api/v1"
ENDPOINT="${BASE_URL}/stats/overview"

echo "Testing endpoint: ${ENDPOINT}"
echo ""

# Test 1: Basic request
echo "Test 1: Basic GET request"
echo "----------------------------"
response=$(curl -s -w "\n%{http_code}" "${ENDPOINT}")
http_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | head -n -1)

echo "HTTP Status: ${http_code}"
echo ""
echo "Response Body:"
echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
echo ""

if [ "$http_code" = "200" ]; then
    echo "✅ Status 200 - Success!"

    # Validate response structure
    echo ""
    echo "Validating response structure..."

    # Check for required fields
    if echo "$body" | grep -q "totalApplications"; then
        echo "✅ totalApplications field present"
    else
        echo "❌ totalApplications field missing"
    fi

    if echo "$body" | grep -q "totalDecisions"; then
        echo "✅ totalDecisions field present"
    else
        echo "❌ totalDecisions field missing"
    fi

    if echo "$body" | grep -q "totalGranted"; then
        echo "✅ totalGranted field present"
    else
        echo "❌ totalGranted field missing"
    fi

    if echo "$body" | grep -q "grantedPercentage"; then
        echo "✅ grantedPercentage field present"
    else
        echo "❌ grantedPercentage field missing"
    fi

    if echo "$body" | grep -q "applicationsYoY"; then
        echo "✅ applicationsYoY field present"
    else
        echo "❌ applicationsYoY field missing"
    fi

    if echo "$body" | grep -q "decisionsYoY"; then
        echo "✅ decisionsYoY field present"
    else
        echo "❌ decisionsYoY field missing"
    fi
else
    echo "❌ Request failed with status ${http_code}"
fi

echo ""
echo "=========================================="
echo "Test Complete"
echo "=========================================="
