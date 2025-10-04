# Weekend Batch Embedding Execution Guide

## 🎯 Objective
Embed all 2.5M planning applications over the weekend using optimized batch processing.

## ⚡ Key Optimizations
- **Batch API calls:** 100 documents per OpenAI request (100x faster)
- **Recent first:** Process newest applications first (highest value)
- **Resume capability:** Automatic checkpoint/resume on interruption
- **Bulk ES updates:** Batch updates for efficiency

## 📊 Expected Results
- **Time:** 8-12 hours (vs 17 days without batching)
- **Cost:** ~$2.50 total
- **Throughput:** ~3,500-5,000 docs/minute
- **Coverage:** 2.5M applications

## 🚀 Execution Steps

### Step 1: Pre-flight Check (5 minutes)

```bash
# 1. Check Elasticsearch health
curl localhost:9200/_cluster/health

# 2. Verify disk space (need 50+ GB free)
df -h

# 3. Check ES heap settings
curl localhost:9200/_nodes/stats/jvm | jq '.nodes[].jvm.mem'

# 4. Test OpenAI API
python3 -c "
import asyncio
from app.ai.embeddings import EmbeddingService
async def test():
    svc = EmbeddingService()
    result = await svc.generate_text_embedding('test')
    print(f'✅ API working, dims: {len(result.embedding)}')
asyncio.run(test())
"

# 5. Count documents without embeddings
curl -X GET "localhost:9200/planning_applications/_count" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "must_not": {"exists": {"field": "description_embedding"}},
      "must": {"exists": {"field": "description"}}
    }
  }
}'
```

### Step 2: Start Embedding Generation

```bash
# Navigate to backend directory
cd /mnt/c/Users/Solomon-PC/Documents/Planning\ Explorer/backend

# Run with default settings (recommended)
python3 weekend_batch_embeddings.py --target 2500000

# Or with custom batch sizes
python3 weekend_batch_embeddings.py \
  --target 2500000 \
  --api-batch-size 100 \
  --es-batch-size 500
```

### Step 3: Monitor Progress

**In another terminal:**
```bash
# Watch live logs
tail -f logs/weekend_embedding_*.log

# Check progress every 5 minutes
watch -n 300 'curl -s localhost:9200/planning_applications/_count -H "Content-Type: application/json" -d '"'"'{"query":{"exists":{"field":"description_embedding"}}}'"'"' | jq ".count"'

# Monitor ES performance
watch -n 60 'curl -s localhost:9200/_nodes/stats | jq ".nodes[].jvm.mem.heap_used_percent"'
```

### Step 4: Estimated Timeline

**Phase 1: First 500k docs (Recent)**
- Time: ~2 hours
- Cost: $0.50
- Progress: 20%

**Phase 2: Next 1M docs**
- Time: ~4 hours
- Cost: $1.00
- Progress: 60%

**Phase 3: Remaining 1M docs (Oldest)**
- Time: ~4 hours
- Cost: $1.00
- Progress: 100%

**Total: 8-12 hours** (depending on API latency)

### Step 5: Validation (After Completion)

```bash
# 1. Check total embedded documents
curl -X GET "localhost:9200/planning_applications/_count" -H 'Content-Type: application/json' -d'
{
  "query": {
    "exists": {"field": "description_embedding"}
  }
}'

# Expected: ~2,500,000

# 2. Test semantic search
curl -X POST "localhost:8000/api/search/semantic" \
  -H 'Content-Type: application/json' \
  -d '{"query": "housing development in London", "k": 10}'

# 3. Check final report
cat weekend_embedding_report_*.json

# 4. Benchmark search performance
ab -n 100 -c 10 http://localhost:8000/api/search/semantic?query=housing
```

## 🔧 Configuration Options

### API Batch Size
```bash
# Conservative (safer, slower)
--api-batch-size 50

# Recommended (balanced)
--api-batch-size 100

# Aggressive (faster, might hit limits)
--api-batch-size 200
```

### ES Batch Size
```bash
# Small (lower memory)
--es-batch-size 250

# Recommended (balanced)
--es-batch-size 500

# Large (higher memory, faster)
--es-batch-size 1000
```

## 📈 Performance Expectations

### Throughput Rates
```
API Batch Size 50:  ~2,500 docs/min  → 16 hours
API Batch Size 100: ~5,000 docs/min  → 8 hours
API Batch Size 200: ~8,000 docs/min  → 5 hours
```

### Cost Breakdown
```
Total documents: 2,500,000
Avg tokens/doc: 50
Total tokens: 125,000,000

Cost = (125,000,000 ÷ 1,000) × $0.00002
     = $2.50

Query costs: $0.0002 per search
Daily new apps: $0.0023 per day
```

## ⚠️ Troubleshooting

### Issue: Rate Limit Errors
```
Error: Rate limit exceeded (429)

Solution:
- Reduce --api-batch-size to 50
- Script has automatic retry with backoff
- OpenAI Tier 2: 3,500 RPM (should be fine)
```

### Issue: Out of Memory
```
Error: ES heap OutOfMemory

Solution:
# Increase ES heap (already have 128 GB RAM)
sudo vi /etc/elasticsearch/jvm.options
# Set: -Xms32g -Xmx32g

sudo systemctl restart elasticsearch
```

### Issue: Process Interrupted
```
Error: Connection lost, Ctrl+C, server restart

Solution:
# Script auto-saves checkpoints every 10 batches
# Just restart with same command - it will resume

python3 weekend_batch_embeddings.py --target 2500000
# ✅ Will skip already processed documents
```

### Issue: Slow Progress
```
Observed: <1,000 docs/min (expected: 3,500-5,000)

Checks:
1. API latency: Check OpenAI status
2. ES performance: Check disk I/O
3. Network: Check bandwidth

Quick fix:
# Increase parallelization
python3 weekend_batch_embeddings.py \
  --api-batch-size 150 \
  --es-batch-size 750
```

## 📊 Monitoring Dashboard

**Track these metrics:**

```bash
# Create monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash
while true; do
  clear
  echo "=== WEEKEND EMBEDDING PROGRESS ==="
  echo ""

  # Total embedded
  EMBEDDED=$(curl -s localhost:9200/planning_applications/_count -H 'Content-Type: application/json' -d '{"query":{"exists":{"field":"description_embedding"}}}' | jq -r '.count')
  echo "📊 Embedded: $EMBEDDED / 2,500,000"

  # Progress percentage
  PERCENT=$(echo "scale=2; ($EMBEDDED / 2500000) * 100" | bc)
  echo "📈 Progress: $PERCENT%"

  # Latest log entries
  echo ""
  echo "📋 Recent logs:"
  tail -n 3 logs/weekend_embedding_*.log

  echo ""
  echo "Next update in 60s..."
  sleep 60
done
EOF

chmod +x monitor.sh
./monitor.sh
```

## 🎯 Success Criteria

**Completion checklist:**

- [ ] 2.5M documents embedded (check count)
- [ ] Final cost ~$2.50 (check report)
- [ ] Search latency <500ms (benchmark)
- [ ] No errors in final report
- [ ] Semantic search returns relevant results
- [ ] ES heap stable (check _nodes/stats)

## 📝 Post-Execution

### 1. Verify Search Quality
```bash
# Test various queries
curl -X POST localhost:8000/api/search/semantic \
  -H 'Content-Type: application/json' \
  -d '{"query": "affordable housing", "k": 5}'

curl -X POST localhost:8000/api/search/semantic \
  -H 'Content-Type: application/json' \
  -d '{"query": "commercial development Manchester", "k": 5}'
```

### 2. Update Frontend
```bash
# Remove search type selector (semantic only for MVP)
# Update SemanticSearchBar to always use semantic
```

### 3. Archive Logs
```bash
# Save execution logs
mkdir -p embedding_execution_logs
cp logs/weekend_embedding_*.log embedding_execution_logs/
cp weekend_embedding_report_*.json embedding_execution_logs/
cp batch_checkpoint_*.json embedding_execution_logs/
```

### 4. Setup Continuous Updates
```bash
# Add to application indexing pipeline
# New apps automatically get embeddings
# See: backend/app/services/background_processor.py
```

## 🚨 Emergency Stop

**If you need to stop:**
```bash
# Ctrl+C in terminal (graceful)
# Or find process and kill
ps aux | grep weekend_batch
kill -SIGTERM <PID>

# State is saved in checkpoint file
# Resume later with same command
```

## 📞 Support

**Issues during execution:**
- Check logs: `tail -f logs/weekend_embedding_*.log`
- Check ES: `curl localhost:9200/_cluster/health`
- Check disk: `df -h`
- Check memory: `free -h`

**Expected execution window:**
- Start: Friday evening / Saturday morning
- Complete: Saturday evening / Sunday morning
- Buffer: Sunday for validation

---

**Ready to execute? Run the pre-flight checks and start the process!** 🚀
