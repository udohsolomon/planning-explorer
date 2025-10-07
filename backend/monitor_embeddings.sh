#!/bin/bash

# Monitor Embedding Progress Script

echo "=================================="
echo "EMBEDDING GENERATION MONITOR"
echo "=================================="
echo ""

# Check if optimized script is running
PROCESS_COUNT=$(ps aux | grep "optimized_batch_embeddings.py" | grep -v grep | wc -l)

if [ $PROCESS_COUNT -eq 0 ]; then
    echo "⚠️  WARNING: Optimized embedding script is NOT running!"
    echo ""
else
    echo "✅ Script Status: RUNNING"
    echo ""
fi

# Get total embedded count from Elasticsearch
echo "📊 EMBEDDING STATISTICS:"
echo "------------------------"

EMBEDDED_COUNT=$(curl -s -X GET "localhost:9200/planning_applications/_count" \
  -H 'Content-Type: application/json' \
  -d '{"query":{"exists":{"field":"description_embedding"}}}' | \
  jq -r '.count // 0')

TOTAL_DOCS=$(curl -s -X GET "localhost:9200/planning_applications/_count" | jq -r '.count // 0')

echo "✅ Documents Embedded: $(printf "%'d" $EMBEDDED_COUNT)"
echo "📄 Total Documents: $(printf "%'d" $TOTAL_DOCS)"

if [ $TOTAL_DOCS -gt 0 ]; then
    PERCENT=$(echo "scale=2; ($EMBEDDED_COUNT * 100) / $TOTAL_DOCS" | bc)
    echo "📈 Progress: ${PERCENT}%"
fi

echo ""

# Show latest log entries
echo "📋 RECENT LOG ENTRIES:"
echo "----------------------"
tail -n 5 logs/optimized_embedding_*.log 2>/dev/null || echo "No log file found"

echo ""

# Calculate estimated completion
if [ $EMBEDDED_COUNT -gt 0 ]; then
    REMAINING=$((2500000 - EMBEDDED_COUNT))

    # Extract rate from latest log
    RATE=$(tail -n 20 logs/optimized_embedding_*.log 2>/dev/null | grep "Rate:" | tail -1 | sed -n 's/.*Rate: \([0-9]*\) docs\/min.*/\1/p')

    if [ ! -z "$RATE" ] && [ $RATE -gt 0 ]; then
        ETA_MINUTES=$((REMAINING / RATE))
        ETA_HOURS=$((ETA_MINUTES / 60))
        ETA_DAYS=$((ETA_HOURS / 24))

        echo "⏱️  ESTIMATED COMPLETION:"
        echo "------------------------"
        echo "Rate: ${RATE} docs/min"
        echo "Remaining: $(printf "%'d" $REMAINING) documents"

        if [ $ETA_DAYS -gt 0 ]; then
            echo "ETA: ${ETA_DAYS}d ${ETA_HOURS}h ($(printf "%'d" $ETA_MINUTES) minutes)"
        else
            echo "ETA: ${ETA_HOURS}h ($(printf "%'d" $ETA_MINUTES) minutes)"
        fi
    fi
fi

echo ""
echo "=================================="
echo "Run: ./monitor_embeddings.sh to refresh"
echo "Or: watch -n 60 ./monitor_embeddings.sh (auto-refresh every 60s)"
echo "=================================="
