# Planning Explorer - Elasticsearch Implementation Guide

## Overview

This guide provides complete implementation instructions for the enhanced Elasticsearch schema with vector embeddings and AI optimization for the Planning Explorer platform.

## Architecture Summary

- **Single-node Elasticsearch deployment** optimized for Planning Explorer
- **Vector embeddings** for semantic search using OpenAI text-embedding-3-large
- **AI enhancement fields** for opportunity scoring and insights
- **Performance-optimized** for < 100ms search response times
- **Native caching** without external dependencies

## File Structure

```
Planning Explorer/
├── elasticsearch_schema.json           # Complete ES mapping with AI fields
├── vector_search_config.json          # Vector search configurations
├── performance_config.json            # Single-node optimization settings
├── aggregation_config.json            # Analytics and filtering aggregations
├── sample_data_template.json          # Sample data structures
├── bulk_indexing_scripts.py           # Bulk indexing with AI processing
├── index_lifecycle_config.json        # Data retention and lifecycle
└── elasticsearch_implementation_guide.md  # This guide
```

## Quick Start

### 1. Install Elasticsearch (Single Node)

```bash
# Download and install Elasticsearch 8.x
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.11.0-linux-x86_64.tar.gz
tar -xzf elasticsearch-8.11.0-linux-x86_64.tar.gz
cd elasticsearch-8.11.0/

# Configure for single node (edit config/elasticsearch.yml)
echo "discovery.type: single-node" >> config/elasticsearch.yml
echo "xpack.security.enabled: false" >> config/elasticsearch.yml
echo "bootstrap.memory_lock: true" >> config/elasticsearch.yml

# Set heap size (adjust based on available RAM)
echo "-Xms2g" >> config/jvm.options.d/heap.options
echo "-Xmx2g" >> config/jvm.options.d/heap.options

# Start Elasticsearch
./bin/elasticsearch
```

### 2. Create the Index

```bash
# Create the planning applications index
curl -X PUT "localhost:9200/planning_applications" \
  -H "Content-Type: application/json" \
  -d @elasticsearch_schema.json
```

### 3. Set Up Bulk Indexing

```bash
# Install Python dependencies
pip install elasticsearch openai numpy

# Set up environment variables
export OPENAI_API_KEY="your-openai-api-key"

# Run the setup script
python bulk_indexing_scripts.py --setup

# Index sample data
python bulk_indexing_scripts.py --sample
```

## Schema Design Details

### Core Planning Fields

The schema includes all essential UK planning application fields:

- **Application Details**: ID, reference, authority, status, dates
- **Location Data**: Address, postcode, coordinates, ward information
- **Development Info**: Type, use class, description, project value
- **Stakeholders**: Applicant, agent, planning officer details
- **Process Data**: Documents, consultations, public comments

### AI Enhancement Fields

Enhanced with AI-powered fields for intelligent insights:

```json
{
  "ai_summary": "AI-generated application summary",
  "opportunity_score": 78,
  "opportunity_breakdown": {
    "approval_probability": 0.85,
    "market_potential": 0.72,
    "project_viability": 0.81
  },
  "risk_assessment": {
    "risk_level": "Low",
    "risk_factors": ["neighbour_objection"]
  },
  "predicted_timeline": {
    "decision_weeks": 8,
    "confidence": 0.78
  }
}
```

### Vector Embeddings

Multiple embedding types for comprehensive semantic search:

- **Description Embedding**: Core application description (1536 dims)
- **Full Content Embedding**: Complete application content (1536 dims)
- **Summary Embedding**: AI-generated summaries (1536 dims)
- **Location Embedding**: Geographic context (256 dims)
- **Document Embeddings**: Individual document vectors (nested)

## Search Capabilities

### Hybrid Search

Combines keyword and semantic search:

```python
{
  "query": {
    "bool": {
      "must": [
        {
          "multi_match": {
            "query": "residential extension",
            "fields": ["description^3", "proposal^2", "ai_summary^2"]
          }
        }
      ],
      "should": [
        {
          "script_score": {
            "query": {"match_all": {}},
            "script": {
              "source": "cosineSimilarity(params.query_vector, 'description_embedding') + 1.0",
              "params": {"query_vector": [0.1, 0.2, ...]}
            }
          }
        }
      ]
    }
  }
}
```

### Semantic Search

Pure vector similarity search:

```python
{
  "query": {
    "script_score": {
      "query": {"bool": {"filter": filters}},
      "script": {
        "source": "cosineSimilarity(params.query_vector, 'full_content_embedding') + 1.0",
        "params": {"query_vector": embedding}
      }
    }
  },
  "min_score": 1.7
}
```

### Similar Applications

Find applications similar to a given one:

```python
{
  "query": {
    "script_score": {
      "script": {
        "source": """
          double desc_sim = cosineSimilarity(params.desc_vector, 'description_embedding');
          double content_sim = cosineSimilarity(params.content_vector, 'full_content_embedding');
          double location_sim = cosineSimilarity(params.location_vector, 'location_embedding');
          return (desc_sim * 0.5) + (content_sim * 0.3) + (location_sim * 0.2) + 1.0;
        """
      }
    }
  }
}
```

## Performance Optimization

### Single-Node Configuration

Optimized settings for single-node deployment:

```json
{
  "number_of_shards": 1,
  "number_of_replicas": 0,
  "refresh_interval": "5s",
  "queries.cache.enabled": true,
  "requests.cache.enable": true,
  "codec": "best_compression"
}
```

### Caching Strategy

Three-tier caching approach:

1. **Query Cache**: Frequent filter queries (512MB)
2. **Request Cache**: Search request results (256MB)
3. **Field Data Cache**: Aggregation fields (256MB)

### Vector Search Optimization

- **Approximate kNN**: Use num_candidates=1000, k=100
- **Pre-filtering**: Apply cheap filters before vector search
- **Cache warming**: Preload frequently accessed vectors

## Analytics and Aggregations

### Market Analysis

```json
{
  "aggs": {
    "by_authority": {
      "terms": {"field": "authority", "size": 50},
      "aggs": {
        "avg_opportunity": {"avg": {"field": "opportunity_score"}},
        "approval_rate": {
          "filter": {"terms": {"decision": ["approved", "granted"]}},
          "aggs": {"count": {"value_count": {"field": "application_id"}}}
        }
      }
    }
  }
}
```

### Geographic Hotspots

```json
{
  "aggs": {
    "hotspot_grid": {
      "geohash_grid": {"field": "location", "precision": 6},
      "aggs": {
        "avg_opportunity": {"avg": {"field": "opportunity_score"}},
        "total_value": {"sum": {"field": "project_value"}}
      }
    }
  }
}
```

### Opportunity Analysis

```json
{
  "aggs": {
    "high_opportunity_sectors": {
      "filter": {"range": {"opportunity_score": {"gte": 75}}},
      "aggs": {
        "by_development_type": {
          "terms": {"field": "development_type", "size": 10}
        }
      }
    }
  }
}
```

## AI Processing Pipeline

### Embedding Generation

```python
async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
    response = await self.openai_client.embeddings.create(
        model="text-embedding-3-large",
        input=texts,
        encoding_format="float"
    )
    return [embedding.embedding for embedding in response.data]
```

### Bulk Processing

```python
# Process applications in batches of 1000
for batch in batches(applications, 1000):
    processed_batch = await self.process_applications_batch(batch)
    actions = self.prepare_bulk_actions(processed_batch)
    await helpers.async_bulk(self.es_client, actions)
```

## Data Lifecycle Management

### Retention Strategy

- **Active Applications**: Current + 6 months (indefinite retention)
- **Historical Applications**: 6 months to 2 years
- **Archived Applications**: 2+ years (7-year retention)

### Lifecycle Phases

1. **Hot Phase**: Active indexing and frequent searches
2. **Warm Phase**: Read-only with force merge optimization
3. **Cold Phase**: Compressed storage for occasional access
4. **Delete Phase**: Automatic deletion after retention period

## Monitoring and Maintenance

### Key Metrics

- **Search Performance**: < 100ms for standard, < 200ms for vector
- **Indexing Rate**: > 1000 docs/second
- **Cache Hit Ratio**: > 85% query cache, > 70% request cache
- **Resource Usage**: < 80% heap, < 70% CPU

### Daily Maintenance

```bash
# Force merge segments (02:00)
curl -X POST "localhost:9200/planning_applications/_forcemerge?max_num_segments=5"

# Clear field data cache (03:00)
curl -X POST "localhost:9200/_cache/clear?fielddata=true"

# Warm cache with common queries (04:00)
python warm_cache.py
```

## Backup and Recovery

### Snapshot Configuration

```bash
# Create snapshot repository
curl -X PUT "localhost:9200/_snapshot/planning_backup" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "fs",
    "settings": {
      "location": "/backup/elasticsearch",
      "compress": true
    }
  }'

# Create daily snapshots
curl -X PUT "localhost:9200/_snapshot/planning_backup/snapshot_%7Bnow%2Fd%7D" \
  -H "Content-Type: application/json" \
  -d '{
    "indices": "planning_applications*",
    "ignore_unavailable": true,
    "include_global_state": false
  }'
```

## Integration with FastAPI

### Search Endpoint Example

```python
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI

app = FastAPI()
es = AsyncElasticsearch([os.getenv("ELASTICSEARCH_URL")])

@app.get("/search")
async def search_applications(
    query: str,
    search_type: str = "hybrid",
    filters: dict = None,
    size: int = 20
):
    if search_type == "semantic":
        # Generate query embedding
        embedding = await generate_embedding(query)
        search_body = build_semantic_query(embedding, filters, size)
    else:
        search_body = build_hybrid_query(query, embedding, filters, size)

    response = await es.search(
        index="planning_applications",
        body=search_body
    )

    return format_search_results(response)
```

## Security Considerations

### Access Control

- **Network Security**: Bind to localhost for single-node
- **API Security**: No authentication in development, JWT in production
- **Data Privacy**: Anonymize personal data after retention period

### GDPR Compliance

- **Data Retention**: Follow retention policies
- **Right to Deletion**: Implement deletion on request
- **Data Minimization**: Store only necessary fields

## Scaling Considerations

### Vertical Scaling

- **100k applications**: 4GB heap
- **500k applications**: 8GB heap
- **1M applications**: 16GB heap
- **5M applications**: 31GB heap (max recommended)

### Horizontal Scaling Migration

When ready to scale beyond single node:

1. **Increase shard count** to 3-5 shards
2. **Add replica nodes** for read scaling
3. **Configure cluster discovery** settings
4. **Rebalance shards** across nodes

## Troubleshooting

### Common Issues

**Slow Vector Search**
- Reduce num_candidates in kNN queries
- Implement query filters before vector search
- Warm vector caches on startup

**High Memory Usage**
- Increase heap size
- Reduce field data cache size
- Clear unused indexes

**Indexing Slowness**
- Increase refresh interval during bulk operations
- Reduce number of replicas during indexing
- Use async AI processing

### Performance Monitoring

```bash
# Check cluster health
curl "localhost:9200/_cluster/health?pretty"

# Monitor search performance
curl "localhost:9200/_stats/search?pretty"

# Check cache usage
curl "localhost:9200/_stats/indices?level=indices&pretty"
```

## Future Enhancements

### Phase 2 Improvements

- **Geographic embeddings**: Specialized location vectors
- **Multi-modal search**: Combine text, location, and metadata
- **Real-time AI processing**: Stream processing for live updates
- **Advanced analytics**: ML-powered trend prediction

### Scalability Roadmap

- **Multi-node cluster**: When data exceeds single-node capacity
- **Dedicated vector store**: Consider specialized vector databases
- **Edge caching**: CDN for static geographic data
- **Read replicas**: Geographic distribution for global access

---

This implementation provides a robust, AI-enhanced Elasticsearch foundation for Planning Explorer with excellent performance characteristics and room for future growth.