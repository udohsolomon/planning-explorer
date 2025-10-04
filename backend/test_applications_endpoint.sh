#!/bin/bash
# Test script for Applications List Endpoint
# Content Discovery - Phase 1 Week 1

BASE_URL="http://localhost:8000/api/v1"

echo "=========================================="
echo "Testing Applications List Endpoint"
echo "=========================================="
echo ""

# Test 1: Basic request for Poole authority
echo "Test 1: Basic request for Poole authority (page 1, 5 results)"
echo "GET ${BASE_URL}/applications/authority/poole?page=1&page_size=5"
curl -s "${BASE_URL}/applications/authority/poole?page=1&page_size=5" | jq '.'
echo ""
echo "---"
echo ""

# Test 2: Filter by status (pending)
echo "Test 2: Filter by status (pending)"
echo "GET ${BASE_URL}/applications/authority/poole?page=1&page_size=5&status=pending"
curl -s "${BASE_URL}/applications/authority/poole?page=1&page_size=5&status=pending" | jq '.'
echo ""
echo "---"
echo ""

# Test 3: Filter by status (approved)
echo "Test 3: Filter by status (approved)"
echo "GET ${BASE_URL}/applications/authority/poole?page=1&page_size=5&status=approved"
curl -s "${BASE_URL}/applications/authority/poole?page=1&page_size=5&status=approved" | jq '.'
echo ""
echo "---"
echo ""

# Test 4: Sort by decision_time
echo "Test 4: Sort by decision_time (fastest decisions)"
echo "GET ${BASE_URL}/applications/authority/poole?page=1&page_size=5&sort_by=decision_time&sort_order=asc"
curl -s "${BASE_URL}/applications/authority/poole?page=1&page_size=5&sort_by=decision_time&sort_order=asc" | jq '.'
echo ""
echo "---"
echo ""

# Test 5: Date range filter (last 6 months)
echo "Test 5: Date range filter (last 6 months)"
echo "GET ${BASE_URL}/applications/authority/poole?page=1&page_size=5&date_from=now-6M/M&date_to=now/M"
curl -s "${BASE_URL}/applications/authority/poole?page=1&page_size=5&date_from=now-6M/M&date_to=now/M" | jq '.'
echo ""
echo "---"
echo ""

# Test 6: Pagination (page 2)
echo "Test 6: Pagination (page 2)"
echo "GET ${BASE_URL}/applications/authority/poole?page=2&page_size=10"
curl -s "${BASE_URL}/applications/authority/poole?page=2&page_size=10" | jq '.'
echo ""
echo "---"
echo ""

# Test 7: Sort by opportunity score (if available)
echo "Test 7: Sort by opportunity score (highest first)"
echo "GET ${BASE_URL}/applications/authority/poole?page=1&page_size=5&sort_by=score&sort_order=desc"
curl -s "${BASE_URL}/applications/authority/poole?page=1&page_size=5&sort_by=score&sort_order=desc" | jq '.'
echo ""
echo "---"
echo ""

# Test 8: Multi-word authority (e.g., "tower-hamlets")
echo "Test 8: Multi-word authority (Tower Hamlets)"
echo "GET ${BASE_URL}/applications/authority/tower-hamlets?page=1&page_size=5"
curl -s "${BASE_URL}/applications/authority/tower-hamlets?page=1&page_size=5" | jq '.'
echo ""
echo "---"
echo ""

echo "=========================================="
echo "Tests completed!"
echo "=========================================="
