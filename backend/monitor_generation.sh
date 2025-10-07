#!/bin/bash
# Monitor PSEO Generation Progress

while true; do
    clear
    echo "============================================================"
    echo "PSEO GENERATION MONITOR"
    echo "============================================================"
    echo ""

    # Count files
    TOTAL_FILES=$(ls -1 outputs/pseo/*.json 2>/dev/null | grep -v checkpoint | wc -l)

    # Get latest progress from log
    LATEST_PROGRESS=$(grep "Total Progress:" generation.log | tail -1)
    LATEST_COST=$(grep "Total Cost:" generation.log | tail -1)
    LATEST_SUCCESS=$(grep "SUCCESS:" generation.log | tail -3)

    echo "📊 CURRENT STATUS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "JSON Files Generated: $TOTAL_FILES / 424"
    echo ""
    echo "$LATEST_PROGRESS"
    echo "$LATEST_COST"
    echo ""
    echo "📝 RECENT COMPLETIONS:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "$LATEST_SUCCESS"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Last updated: $(date)"
    echo "Press Ctrl+C to stop monitoring"

    sleep 30
done
