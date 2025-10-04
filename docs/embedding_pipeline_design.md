# Continuous Embedding Pipeline Design
**Planning Explorer - Automated Embedding Generation System**

*Last Updated: October 2025*

---

## 🎯 Overview

The continuous embedding pipeline automatically generates vector embeddings for new and updated planning applications as they arrive in the Elasticsearch database, ensuring semantic search capabilities are always up-to-date.

## 📊 Current Status

### PoC Results (Completed)
- ✅ **10,000 documents** processed successfully
- ✅ **9,986 embeddings** generated (99.9% success rate)
- ✅ **$0.01 total cost** (extremely cost-effective)
- ✅ **52 docs/min throughput**
- ✅ **text-embedding-3-small** (1536 dimensions)
- ⚠️ **Pagination issue fixed** (search_after API implemented)

### Remaining Work
- 🔄 **40,000 documents** remaining for initial backfill
- 🔄 Continuous pipeline implementation
- 🔄 Event-driven processing integration

---

## 🏗️ Architecture Design

### Three Pipeline Approaches

#### **1. Scheduled Batch Processing** (Recommended for Initial Implementation)
**Description**: Periodic processing of new/updated documents on a fixed schedule.

**Pros:**
- ✅ Simple to implement and maintain
- ✅ Predictable resource usage
- ✅ Easy cost control and budgeting
- ✅ Batch optimization reduces API calls
- ✅ Less complex error handling

**Cons:**
- ❌ Latency: Embeddings delayed until next run
- ❌ May miss rapid updates between cycles

**Use Cases:**
- Initial backfill processing
- Low-urgency embedding updates
- Budget-constrained environments
- Predictable workload patterns

**Implementation:**
```python
# Run every hour
schedule_interval = 60 minutes
batch_size = 100
priority_processing = True  # Process recent docs first
```

---

#### **2. Event-Driven Processing**
**Description**: Generate embeddings immediately when documents are created/updated.

**Pros:**
- ✅ Real-time updates (< 1 second latency)
- ✅ Always up-to-date search index
- ✅ No missed updates
- ✅ Better user experience

**Cons:**
- ❌ Complex infrastructure (message queue, workers)
- ❌ Higher costs (no batching optimization)
- ❌ Requires ES change data capture
- ❌ More complex error handling and retry logic

**Use Cases:**
- Critical real-time applications
- High-value document updates
- User-facing search requiring instant results

**Implementation Options:**

**Option A: Elasticsearch Watcher + Webhook**
```json
{
  "trigger": {
    "schedule": {"interval": "5m"}
  },
  "input": {
    "search": {
      "request": {
        "indices": ["planning_applications"],
        "body": {
          "query": {
            "bool": {
              "must_not": [{"exists": {"field": "description_embedding"}}],
              "filter": [{"range": {"start_date": {"gte": "now-5m"}}}]
            }
          }
        }
      }
    }
  },
  "actions": {
    "webhook": {
      "webhook": {
        "url": "http://localhost:8000/api/internal/process-embeddings",
        "method": "POST"
      }
    }
  }
}
```

**Option B: Application-Level Hooks**
```python
# In data ingestion service
async def create_planning_application(data: dict):
    # 1. Create document in ES
    doc_id = await es_client.index_document(data)

    # 2. Trigger embedding generation (async)
    await message_queue.publish(
        "embedding.generate",
        {"doc_id": doc_id, "priority": "high"}
    )

    return doc_id
```

---

#### **3. Hybrid Approach** (⭐ **RECOMMENDED FOR PRODUCTION**)
**Description**: Combines scheduled batching with event-driven processing for critical updates.

**Strategy:**
- **Event-driven**: Recent documents (< 24h) for instant search availability
- **Scheduled batching**: Older documents (> 24h) for cost efficiency
- **Priority queue**: Process by importance and recency

**Pros:**
- ✅ Best of both worlds: low latency + cost efficiency
- ✅ Flexible resource allocation
- ✅ Optimized for different use cases
- ✅ Scalable architecture

**Cons:**
- ❌ More complex implementation
- ❌ Requires priority management logic

**Implementation Architecture:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Data Ingestion Layer                         │
│  (API endpoints, scrapers, batch imports)                       │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ├─────────────┬──────────────────────────┐
                 ▼             ▼                          ▼
         ┌──────────────┐  ┌────────────────┐  ┌──────────────────┐
         │ Elasticsearch│  │  Event Queue   │  │ Priority Tracker │
         │   (Primary)  │  │  (RabbitMQ/    │  │  (Redis/Memory)  │
         │              │  │   Redis)       │  │                  │
         └──────┬───────┘  └────┬───────────┘  └────────┬─────────┘
                │               │                        │
                │               │                        │
                ▼               ▼                        ▼
         ┌──────────────────────────────────────────────────────┐
         │        Embedding Generation Coordinator              │
         │  - Priority management                               │
         │  - Cost tracking & budgeting                         │
         │  - Worker pool management                            │
         └────────────────┬─────────────────────────────────────┘
                          │
                ┌─────────┴──────────┬────────────────┐
                ▼                    ▼                ▼
         ┌──────────────┐    ┌──────────────┐  ┌──────────────┐
         │   Critical   │    │   Normal     │  │   Backfill   │
         │   Workers    │    │   Workers    │  │   Workers    │
         │  (Real-time) │    │  (Batched)   │  │  (Low prio)  │
         └──────┬───────┘    └──────┬───────┘  └──────┬───────┘
                │                   │                  │
                └───────────────────┴──────────────────┘
                                    │
                                    ▼
                        ┌────────────────────────┐
                        │   OpenAI Embeddings    │
                        │   API (Rate Limited)   │
                        └────────────────────────┘
```

---

## 📋 Priority-Based Processing

### Priority Levels

| Priority   | Age/Condition                    | Processing Time | Batch Size | Use Case                           |
|-----------|-----------------------------------|-----------------|------------|------------------------------------|
| CRITICAL  | < 24 hours old                   | < 5 minutes     | 50         | Recent applications, user searches |
| HIGH      | < 7 days or recently updated     | < 1 hour        | 100        | Active applications                |
| NORMAL    | < 30 days                        | < 4 hours       | 200        | Standard processing                |
| LOW       | > 30 days                        | Daily batch     | 500        | Historical backfill                |

### Priority Queue Logic

```python
async def get_documents_by_priority():
    now = datetime.now()

    # CRITICAL: Last 24 hours
    critical = await search_documents({
        "range": {"start_date": {"gte": now - timedelta(hours=24)}}
    })

    # HIGH: Last 7 days OR recently updated
    high = await search_documents({
        "bool": {
            "should": [
                {"range": {"start_date": {"gte": now - timedelta(days=7)}}},
                {"range": {"last_changed": {"gte": now - timedelta(hours=24)}}}
            ]
        }
    })

    # NORMAL: Last 30 days
    normal = await search_documents({
        "range": {"start_date": {"gte": now - timedelta(days=30)}}
    })

    # LOW: Older documents
    low = await search_documents({
        "range": {"start_date": {"lt": now - timedelta(days=30)}}
    })

    return {critical, high, normal, low}
```

---

## 💰 Cost Management

### Current Costs (PoC Results)
- **Per document**: $0.0000007 (0.00007 cents)
- **Per 1K tokens**: $0.00002
- **10K documents**: $0.01
- **Projected 50K**: $0.035 - $0.05

### Daily Budget Estimates

| Scenario                          | Documents/Day | Monthly Cost | Annual Cost |
|----------------------------------|---------------|--------------|-------------|
| Low activity (100 new/day)       | 100           | $0.21        | $2.55       |
| Medium activity (500 new/day)    | 500           | $1.05        | $12.78      |
| High activity (2,000 new/day)    | 2,000         | $4.20        | $51.10      |
| Full UK coverage (10K+/day)      | 10,000        | $21.00       | $255.50     |

### Cost Control Strategies

1. **Daily Budget Limits**
   ```python
   config = PipelineConfig(
       daily_cost_limit_usd=5.0,  # Stop at $5/day
       pause_on_limit=True,
       alert_threshold=0.8  # Alert at 80%
   )
   ```

2. **Smart Batching**
   - Batch size optimization: 100-500 docs per batch
   - Reduces API overhead
   - Better rate limit compliance

3. **Priority-Based Processing**
   - Process critical docs first
   - Defer low-priority backfill to off-peak hours
   - Skip re-embedding unchanged documents

4. **Model Selection**
   - **text-embedding-3-small**: $0.00002/1K tokens (current)
   - **text-embedding-3-large**: $0.00013/1K tokens (6.5x more expensive)
   - Use small model for initial implementation

---

## 🔄 Pipeline Operation Modes

### Mode 1: Initial Backfill (One-Time)
**Purpose**: Process existing 40,000+ documents without embeddings

**Configuration:**
```python
config = PipelineConfig(
    mode=PipelineMode.BACKFILL,
    batch_size=500,
    max_concurrent_batches=5,
    daily_cost_limit_usd=10.0,
    schedule_interval_minutes=None  # Continuous
)
```

**Execution:**
```bash
python production_embedding_generator.py --target 50000 --batch-size 500
```

**Timeline**: ~15-20 hours for 40K documents at 52 docs/min

---

### Mode 2: Continuous Scheduled Processing (Recommended)
**Purpose**: Ongoing processing of new documents

**Configuration:**
```python
config = PipelineConfig(
    mode=PipelineMode.SCHEDULED,
    schedule_interval_minutes=60,  # Hourly
    batch_size=100,
    process_recent_hours=24,
    daily_cost_limit_usd=5.0
)
```

**Execution:**
```bash
# As systemd service or cron job
python continuous_embedding_pipeline.py --mode scheduled
```

**Cron Schedule:**
```cron
# Run every hour
0 * * * * /usr/bin/python3 /app/continuous_embedding_pipeline.py
```

---

### Mode 3: Event-Driven Processing (Future)
**Purpose**: Real-time embedding for critical documents

**Configuration:**
```python
config = PipelineConfig(
    mode=PipelineMode.EVENT_DRIVEN,
    critical_age_hours=24,
    rate_limit_delay=0.5
)
```

**Integration Points:**
1. **Data ingestion API**: Trigger on POST /applications
2. **Elasticsearch watcher**: Detect new documents
3. **Message queue consumer**: Process events from RabbitMQ/Redis

---

### Mode 4: Hybrid (Production-Ready)
**Purpose**: Optimal balance of latency and cost

**Configuration:**
```python
config = PipelineConfig(
    mode=PipelineMode.HYBRID,

    # Scheduled component
    schedule_interval_minutes=60,
    batch_size=200,

    # Event-driven component
    critical_age_hours=24,
    event_driven_enabled=True,

    # Cost management
    daily_cost_limit_usd=10.0,
    priority_based_budgeting=True
)
```

**Processing Flow:**
1. **Real-time**: Documents < 24h old → Immediate processing
2. **Scheduled**: Documents 24h-30d old → Hourly batches
3. **Backfill**: Documents > 30d old → Daily low-priority batch

---

## 🚀 Deployment Strategy

### Phase 1: Complete Initial Backfill (Week 1)
```bash
# Resume from existing state
python production_embedding_generator.py \
    --resume \
    --state-file embedding_state_1727648832.json \
    --target 50000 \
    --batch-size 500
```

**Expected Results:**
- Process remaining 40,000 documents
- Total time: ~15-20 hours
- Total cost: $0.02-$0.03

---

### Phase 2: Deploy Scheduled Pipeline (Week 2)
```bash
# Install as systemd service
sudo cp continuous_embedding_pipeline.service /etc/systemd/system/
sudo systemctl enable continuous_embedding_pipeline
sudo systemctl start continuous_embedding_pipeline
```

**Service Configuration:**
```ini
[Unit]
Description=Planning Explorer Continuous Embedding Pipeline
After=network.target elasticsearch.service

[Service]
Type=simple
User=planning-explorer
WorkingDirectory=/app/backend
ExecStart=/usr/bin/python3 continuous_embedding_pipeline.py --mode scheduled
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
```

---

### Phase 3: Add Event-Driven Processing (Week 3-4)
1. Implement application-level hooks
2. Setup message queue (Redis Streams or RabbitMQ)
3. Deploy worker processes
4. Configure priority routing

---

## 📊 Monitoring & Alerting

### Key Metrics to Track

1. **Processing Metrics**
   - Documents processed per hour/day
   - Embedding generation success rate
   - Average processing time
   - Queue depth by priority

2. **Cost Metrics**
   - Daily cost USD
   - Cost per document
   - Monthly projection
   - Budget utilization %

3. **Performance Metrics**
   - API response time
   - Throughput (docs/min)
   - Error rate
   - Retry count

4. **System Health**
   - Pipeline uptime
   - Consecutive failures
   - Last successful run
   - ES index health

### Monitoring Dashboard (Example)

```python
# GET /api/internal/embedding-pipeline/metrics
{
    "status": "running",
    "last_run": "2025-10-01T14:00:00Z",
    "documents_processed_today": 1247,
    "embeddings_generated_today": 1245,
    "success_rate": 99.84,
    "daily_cost_usd": 0.87,
    "daily_budget_used_percent": 17.4,
    "average_processing_time_ms": 847,
    "queue_depth": {
        "critical": 5,
        "high": 23,
        "normal": 156,
        "low": 4829
    }
}
```

### Alert Conditions

```python
# Alert if:
- consecutive_failures >= 10
- daily_cost_usd >= daily_cost_limit * 0.9
- success_rate < 95%
- processing_time_ms > 2000
- queue_depth["critical"] > 100
```

---

## 🔧 Operational Procedures

### Starting the Pipeline

```bash
# Check ES health
curl -X GET "http://localhost:9200/_cluster/health"

# Start continuous pipeline
python continuous_embedding_pipeline.py --mode scheduled

# Monitor logs
tail -f logs/embedding_pipeline.log
```

### Resuming After Interruption

```bash
# Pipeline automatically resumes from last saved state
python continuous_embedding_pipeline.py --resume --state-file state.json
```

### Emergency Stop

```bash
# Graceful shutdown (saves state)
kill -SIGTERM <pipeline_pid>

# Or use systemd
sudo systemctl stop continuous_embedding_pipeline
```

### Manual Backfill for Specific Documents

```python
# Python script
from continuous_embedding_pipeline import ContinuousEmbeddingPipeline

pipeline = ContinuousEmbeddingPipeline()

# Process specific document
await pipeline.process_document_event(
    doc_id="abc123",
    event_type="manual_backfill"
)
```

---

## 🎯 Recommendations

### Immediate Actions (Week 1)
1. ✅ **Resume backfill**: Complete remaining 40K documents
2. ✅ **Validate search**: Test semantic search with generated embeddings
3. ✅ **Measure quality**: Evaluate embedding relevance scores

### Short-term (Weeks 2-4)
1. 🔄 **Deploy scheduled pipeline**: Hourly processing of new docs
2. 🔄 **Implement monitoring**: Metrics dashboard and alerts
3. 🔄 **Optimize costs**: Fine-tune batch sizes and schedules

### Long-term (Months 2-3)
1. 🔄 **Add event-driven**: Real-time processing for critical docs
2. 🔄 **Scale workers**: Multiple concurrent processing workers
3. 🔄 **Advanced features**: Multi-field embeddings, location vectors

---

## 📚 Additional Resources

- **OpenAI Embeddings Docs**: https://platform.openai.com/docs/guides/embeddings
- **Elasticsearch search_after**: https://www.elastic.co/guide/en/elasticsearch/reference/current/paginate-search-results.html#search-after
- **Vector Search Best Practices**: https://www.elastic.co/blog/vector-search-elasticsearch-rationale

---

## 🔐 Security Considerations

1. **API Key Management**
   - Store OpenAI keys in environment variables or secrets manager
   - Rotate keys quarterly
   - Monitor usage for anomalies

2. **Access Control**
   - Restrict pipeline API endpoints to internal network
   - Require authentication for manual triggers
   - Audit log all embedding operations

3. **Data Privacy**
   - Don't log full document content
   - Hash sensitive fields before logging
   - Comply with GDPR for planning application data

---

**Document Version**: 1.0
**Last Review**: October 2025
**Next Review**: December 2025
