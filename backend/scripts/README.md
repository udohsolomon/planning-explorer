# Planning Explorer AI Pipeline Scripts

This directory contains integration scripts for the Planning Explorer AI Intelligence Layer. These scripts provide utilities for bulk processing, performance benchmarking, data migration, and system testing.

## Scripts Overview

### 1. bulk_ai_processor.py
**Purpose**: Bulk AI processing of planning applications
**Features**:
- Process all or specific planning applications through the AI pipeline
- Resumable processing with checkpoint support
- Configurable batch sizes and concurrency
- Progress tracking and performance monitoring
- Comprehensive error handling and reporting

**Usage**:
```bash
# Process all applications
python scripts/bulk_ai_processor.py

# Process specific applications
python scripts/bulk_ai_processor.py --application-ids APP001 APP002 APP003

# Resume from checkpoint
python scripts/bulk_ai_processor.py --resume

# Use custom configuration
python scripts/bulk_ai_processor.py --config config.json

# Generate processing report
python scripts/bulk_ai_processor.py --report processing_report.json
```

**Configuration File Example**:
```json
{
  "batch_size": 100,
  "max_concurrent": 10,
  "processing_mode": "standard",
  "features": ["opportunity_scoring", "summarization", "embeddings"],
  "checkpoint_interval": 50,
  "retry_attempts": 3
}
```

### 2. performance_benchmark.py
**Purpose**: Performance benchmarking and optimization analysis
**Features**:
- Individual component performance testing
- Integration workflow benchmarking
- Performance target compliance verification
- Scalability analysis
- Optimization recommendations
- Visual performance reports

**Usage**:
```bash
# Full benchmark suite
python scripts/performance_benchmark.py

# Quick benchmark
python scripts/performance_benchmark.py --quick

# Benchmark specific component
python scripts/performance_benchmark.py --component opportunity_scorer

# Save results
python scripts/performance_benchmark.py --output benchmark_results.json
```

**Performance Targets**:
- Opportunity scoring: < 2 seconds per application
- Document summarization: < 3 seconds per document
- Vector embedding: < 1 second per text chunk
- Batch processing: 100+ applications per minute

### 3. data_migration.py
**Purpose**: Data migration for AI enhancement fields
**Features**:
- Elasticsearch mapping updates for AI fields
- Bulk data migration with AI processing
- Dry run capability for testing
- Data validation and verification
- Comprehensive migration reporting

**Usage**:
```bash
# Dry run migration
python scripts/data_migration.py --dry-run

# Full migration
python scripts/data_migration.py

# Force update existing AI data
python scripts/data_migration.py --force-update

# Custom batch size
python scripts/data_migration.py --batch-size 50

# Generate migration report
python scripts/data_migration.py --report migration_report.json
```

**AI Fields Added**:
- `ai_processed`: Boolean flag for AI processing status
- `opportunity_score`: Calculated opportunity score (0-100)
- `approval_probability`: Predicted approval probability
- `ai_summary`: AI-generated summary
- `embedding_vector`: Vector embedding for semantic search
- `ai_recommendations`: Strategic recommendations

### 4. test_ai_integration.py
**Purpose**: Comprehensive AI pipeline integration testing
**Features**:
- Connectivity testing (Elasticsearch, AI services)
- Individual component testing
- End-to-end workflow validation
- Performance verification
- Data quality assessment
- Integration health monitoring

**Usage**:
```bash
# Full integration test
python scripts/test_ai_integration.py

# Quick test
python scripts/test_ai_integration.py --quick

# Test specific component
python scripts/test_ai_integration.py --component embeddings

# Save test report
python scripts/test_ai_integration.py --output integration_test.json
```

**Test Categories**:
- **Connectivity**: Elasticsearch cluster, AI services availability
- **Components**: Individual AI component functionality
- **Integration**: End-to-end workflow testing
- **Performance**: Response time and throughput validation
- **Data Quality**: Result format and content validation

## Prerequisites

### Environment Setup
1. **Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   ```bash
   export ELASTICSEARCH_NODE="95.217.117.251:9200"
   export ELASTICSEARCH_USERNAME="your_username"
   export ELASTICSEARCH_PASSWORD="your_password"
   export OPENAI_API_KEY="your_openai_key"
   export ANTHROPIC_API_KEY="your_anthropic_key"
   ```

3. **Elasticsearch Access**:
   - Ensure connectivity to Planning Explorer ES cluster (95.217.117.251:9200)
   - Verify `planning_applications` index exists and is accessible
   - Confirm appropriate read/write permissions

### AI Service Configuration
- **OpenAI**: Required for embeddings and optional for summarization
- **Anthropic**: Required for advanced analysis and summarization
- **Sentence Transformers**: Fallback for local embeddings

## Performance Optimization

### Recommended Settings
- **Batch Size**: 100 applications (adjust based on available memory)
- **Concurrency**: 10 concurrent processes (adjust based on API rate limits)
- **Processing Mode**:
  - `fast`: Basic opportunity scoring only
  - `standard`: Scoring + summarization + market context
  - `comprehensive`: All AI features enabled
  - `batch`: Optimized for bulk processing

### Memory Requirements
- **Minimum**: 4GB RAM for basic processing
- **Recommended**: 8GB RAM for standard batch processing
- **Optimal**: 16GB+ RAM for comprehensive analysis

### API Rate Limits
- **OpenAI**: 50 requests/minute (configurable)
- **Anthropic**: 30 requests/minute (configurable)
- Built-in rate limiting and retry logic

## Monitoring and Logging

### Log Files
- `bulk_processing.log`: Bulk processing activities
- `ai_integration_test.log`: Integration test results
- `data_migration.log`: Migration process logs

### Key Metrics
- **Processing Rate**: Applications processed per minute
- **Success Rate**: Percentage of successful AI processing
- **Error Rate**: Failed processing attempts
- **Performance**: Average processing time per component

### Health Checks
```bash
# Check AI service status
curl http://localhost:8000/api/v1/ai/models

# Test individual endpoints
curl http://localhost:8000/api/v1/ai/opportunity-score -X POST -H "Content-Type: application/json" -d '{"application_id": "TEST001"}'
```

## Troubleshooting

### Common Issues

1. **Elasticsearch Connection Failed**:
   - Verify network connectivity to 95.217.117.251:9200
   - Check authentication credentials
   - Confirm index exists and permissions are correct

2. **AI API Rate Limits**:
   - Reduce `max_concurrent` setting
   - Increase delays between requests
   - Verify API key quotas and limits

3. **Memory Issues**:
   - Reduce batch size
   - Enable garbage collection optimizations
   - Monitor memory usage during processing

4. **Performance Issues**:
   - Check AI service response times
   - Verify Elasticsearch query performance
   - Review network latency

### Error Codes
- **Exit Code 0**: Success
- **Exit Code 1**: General error
- **Exit Code 130**: Interrupted by user (Ctrl+C)

### Getting Help
- Review log files for detailed error messages
- Run integration tests to identify specific issues
- Use `--dry-run` mode for testing configurations
- Check AI service status endpoints

## Best Practices

### Production Deployment
1. **Test First**: Always run integration tests before production deployment
2. **Gradual Rollout**: Process applications in small batches initially
3. **Monitor Performance**: Track processing rates and success rates
4. **Backup Data**: Ensure Elasticsearch snapshots before bulk operations
5. **API Key Management**: Use secure credential management
6. **Resource Monitoring**: Monitor CPU, memory, and network usage

### Maintenance
- Run performance benchmarks monthly
- Update AI models and configurations as needed
- Monitor API usage and costs
- Review and archive log files regularly
- Test disaster recovery procedures

## Architecture Integration

### Component Interaction
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Elasticsearch  │◄──►│  AI Processor    │◄──►│  OpenAI/Claude  │
│  Cluster        │    │  Orchestrator    │    │  APIs           │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         ▲                        ▲                       ▲
         │                        │                       │
         ▼                        ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Planning       │    │  Vector          │    │  Market         │
│  Applications   │    │  Embeddings      │    │  Intelligence   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Data Flow
1. **Input**: Planning applications from Elasticsearch
2. **Processing**: AI analysis and enhancement
3. **Storage**: Enhanced data back to Elasticsearch
4. **Output**: AI-powered insights and recommendations

## Version Information
- **AI Pipeline Version**: 2.0.0
- **Elasticsearch Schema**: Enhanced with AI fields
- **API Compatibility**: FastAPI backend v1.0.0
- **Frontend Integration**: Ready for Planning Insights reproduction

For technical support or questions, refer to the main project documentation or contact the development team.