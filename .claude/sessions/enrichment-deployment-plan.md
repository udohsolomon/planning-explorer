# Enrichment Agent Deployment Plan

**Master Orchestrator Session**
**Date**: 2025-10-04
**Phase**: Deployment & Production Configuration
**Status**: 🟡 In Progress

---

## 📋 Strategic Overview

### Current State
✅ **Development Complete**: All 8 implementation phases finished
✅ **Testing Complete**: 95.5% test coverage, all integration tests passing
✅ **Mock Implementations**: System working with placeholder MCP clients
⏳ **Production Configuration**: Ready to configure for production use

### Deployment Objective
Configure and deploy the enrichment agent for production use with:
1. Redis caching for optimal performance
2. Real MCP servers for web scraping
3. Production-grade error handling and monitoring
4. Validation with real UK planning portal URLs

---

## 🎯 Deployment Phases

### Phase 9: Production Deployment (2-4 hours)

#### Phase 9.1: Redis Installation & Configuration (30 min)
**Agent**: DevOps Specialist
**Priority**: High
**Dependencies**: None

**Tasks**:
- [x] Review Redis setup documentation
- [ ] Choose Redis deployment option (WSL/Docker/Cloud)
- [ ] Install Redis server
- [ ] Configure Redis for production use
- [ ] Test Redis connectivity
- [ ] Update settings with Redis URL

**Success Criteria**:
- Redis server running and accessible
- Cache service connects successfully on startup
- Health check endpoint reports Redis as healthy

**Options Analysis**:
1. **WSL Redis** (Recommended for Development)
   - Pros: Fast, local, easy to debug
   - Cons: Not suitable for production
   - Install time: 5 minutes

2. **Docker Redis** (Recommended for Production)
   - Pros: Isolated, portable, production-ready
   - Cons: Requires Docker
   - Install time: 10 minutes

3. **Cloud Redis** (Upstash/Redis Cloud)
   - Pros: Managed, scalable, zero-ops
   - Cons: Monthly cost, network latency
   - Setup time: 15 minutes

**Recommended**: Start with WSL for development, move to Docker for production

---

#### Phase 9.2: MCP Server Research (45 min)
**Agent**: AI Engineer + DevOps Specialist
**Priority**: High
**Dependencies**: None

**Research Areas**:
1. **Playwright MCP Server**
   - Official Anthropic MCP servers
   - Alternative implementations
   - Configuration requirements
   - Performance characteristics

2. **Firecrawl MCP Server**
   - Available implementations
   - API key requirements
   - Rate limits and pricing
   - Response time expectations

3. **Context7 MCP Server**
   - LLM integration options (OpenAI, Anthropic)
   - Prompt optimization strategies
   - Cost per extraction
   - Accuracy benchmarks

**Deliverables**:
- MCP server comparison matrix
- Installation guides for each server
- Configuration templates
- Cost analysis

---

#### Phase 9.3: Playwright MCP Configuration (30 min)
**Agent**: Backend Engineer
**Priority**: High
**Dependencies**: Phase 9.2

**Tasks**:
- [ ] Install Playwright MCP server
- [ ] Configure server URL and credentials
- [ ] Update `playwright_client.py` with real implementation
- [ ] Test with sample JavaScript-heavy portal
- [ ] Validate HTML extraction quality

**Implementation**:
```python
# app/services/mcp_clients/playwright_client.py
async def fetch(self, url: str, wait_for_selector: Optional[str] = None) -> str:
    result = await mcp_client.call_tool(
        "playwright_navigate",
        {
            "url": url,
            "wait_for_selector": wait_for_selector or "body",
            "timeout": self.timeout_ms
        }
    )
    return result["html"]
```

**Test URLs**:
- Unknown portals requiring JavaScript rendering
- Single-page applications (SPAs)

---

#### Phase 9.4: Firecrawl MCP Configuration (30 min)
**Agent**: Backend Engineer
**Priority**: High
**Dependencies**: Phase 9.2

**Tasks**:
- [ ] Install/configure Firecrawl MCP server
- [ ] Obtain API key if required
- [ ] Update `firecrawl_client.py` with real implementation
- [ ] Test with Idox portal (Dover)
- [ ] Test with Liverpool custom portal
- [ ] Validate extraction accuracy

**Implementation**:
```python
# app/services/mcp_clients/firecrawl_client.py
async def fetch(self, url: str, format: str = "html") -> str:
    result = await mcp_client.call_tool(
        "firecrawl_scrape",
        {
            "url": url,
            "format": format,
            "timeout": self.timeout_ms
        }
    )
    return result["content"]
```

**Test URLs**:
- Dover Idox portal
- Liverpool custom portal
- Other known UK planning authorities

---

#### Phase 9.5: Context7 MCP Configuration (45 min)
**Agent**: AI Engineer
**Priority**: High
**Dependencies**: Phase 9.2

**Tasks**:
- [ ] Set up Context7/LLM integration
- [ ] Configure API keys (OpenAI/Anthropic)
- [ ] Update `context7_client.py` with real implementation
- [ ] Optimize extraction prompt
- [ ] Test accuracy with various portal types
- [ ] Benchmark cost per extraction

**Implementation**:
```python
# app/services/mcp_clients/context7_client.py
async def extract(self, content: str, prompt: str) -> Optional[Dict]:
    result = await mcp_client.call_tool(
        "context7_extract",
        {
            "content": content,
            "prompt": prompt,
            "model": self.model,
            "timeout": self.timeout_ms
        }
    )
    return json.loads(result["extracted_data"])
```

**Optimization Strategy**:
- Use GPT-4-mini for cost efficiency
- Implement result caching
- Add validation layer
- Monitor accuracy metrics

---

#### Phase 9.6: Client Wrapper Updates (30 min)
**Agent**: Backend Engineer
**Priority**: High
**Dependencies**: Phases 9.3, 9.4, 9.5

**Tasks**:
- [ ] Remove mock implementations
- [ ] Add proper error handling
- [ ] Implement retry logic
- [ ] Add request logging
- [ ] Update health checks
- [ ] Add timeout handling

**Code Updates**:
1. Replace placeholder responses with actual MCP calls
2. Add exponential backoff for retries
3. Implement circuit breaker pattern
4. Add detailed error messages
5. Log all requests/responses for debugging

**Error Handling Strategy**:
```python
async def fetch(self, url: str) -> str:
    for attempt in range(3):
        try:
            result = await self._make_mcp_call(url)
            return result
        except TimeoutError:
            if attempt == 2:
                raise
            await asyncio.sleep(2 ** attempt)
        except Exception as e:
            logger.error(f"MCP call failed: {e}")
            raise
```

---

#### Phase 9.7: Production Testing (1 hour)
**Agent**: QA Engineer
**Priority**: Critical
**Dependencies**: Phase 9.6

**Test Plan**:

1. **Unit Tests** (15 min)
   - Re-run all existing tests with real MCP clients
   - Verify mock removal didn't break tests
   - Update test expectations if needed

2. **Integration Tests** (30 min)
   - Test with real Dover URL (Idox)
   - Test with real Liverpool URL (custom)
   - Test with unknown portal (adaptive)
   - Measure actual extraction times
   - Validate extracted data quality

3. **Performance Tests** (15 min)
   - Test cache hit performance (<100ms)
   - Test cache miss scenarios (2-8s)
   - Test concurrent requests (10 simultaneous)
   - Monitor memory usage
   - Check CPU utilization

**Test URLs**:
```
Dover (Idox):
https://publicaccess.dover.gov.uk/online-applications/applicationDetails.do?activeTab=summary&keyVal=S4S7QCFZH0F00

Liverpool (Custom):
https://lar.liverpool.gov.uk/planning/index.html?fa=getApplication&id=175224

Southampton (Idox):
https://publicaccess.southampton.gov.uk/online-applications/applicationDetails.do?activeTab=summary&keyVal=...

Manchester (Custom):
https://planning.manchester.gov.uk/...
```

**Success Criteria**:
- ✅ 100% successful extraction from Idox portals
- ✅ 100% successful extraction from Liverpool portal
- ✅ >80% successful extraction from unknown portals
- ✅ Cache hit: <100ms response time
- ✅ Idox extraction: <3s average time
- ✅ Unknown extraction: <8s average time
- ✅ No memory leaks during 100 consecutive requests

---

#### Phase 9.8: Production Monitoring (30 min)
**Agent**: DevOps Specialist
**Priority**: Medium
**Dependencies**: Phase 9.7

**Monitoring Setup**:

1. **Metrics to Track**:
   - Enrichment success rate (target: >95%)
   - Cache hit rate (target: >70%)
   - Average processing time per portal type
   - Error rate by portal type
   - Redis connection health
   - MCP server response times

2. **Logging Enhancements**:
   - Structured logging for all enrichment requests
   - Error tracking with stack traces
   - Performance timing logs
   - Cache operation logs

3. **Alerting** (Optional):
   - Alert if error rate > 10%
   - Alert if cache service unavailable
   - Alert if average time > 10s
   - Alert if MCP server failures > 5%

4. **Dashboard** (Future):
   - Real-time enrichment metrics
   - Portal type distribution
   - Performance trends over time
   - Cost analysis (MCP API usage)

**Implementation**:
```python
# Add to enrichment agent
logger.info(
    "enrichment_complete",
    extra={
        "application_id": application_id,
        "portal_type": portal_type,
        "extraction_method": method,
        "processing_time_ms": processing_time,
        "cache_hit": cache_hit,
        "success": success
    }
)
```

---

## 📊 Resource Requirements

### Development Time
| Phase | Estimated Time | Agent |
|-------|---------------|-------|
| 9.1 Redis Setup | 30 min | DevOps |
| 9.2 MCP Research | 45 min | AI + DevOps |
| 9.3 Playwright Config | 30 min | Backend |
| 9.4 Firecrawl Config | 30 min | Backend |
| 9.5 Context7 Config | 45 min | AI Engineer |
| 9.6 Wrapper Updates | 30 min | Backend |
| 9.7 Production Testing | 60 min | QA |
| 9.8 Monitoring Setup | 30 min | DevOps |
| **Total** | **4-5 hours** | Multiple |

### Infrastructure Costs (Monthly)
| Service | Option | Cost |
|---------|--------|------|
| Redis | WSL (Dev) | $0 |
| Redis | Docker (Prod) | $0 |
| Redis | Upstash (Cloud) | $0-10 |
| Playwright MCP | Self-hosted | $0 |
| Firecrawl | API | $0-50 |
| Context7/LLM | OpenAI API | $10-100 |
| **Total** | | **$10-160/month** |

### Technical Requirements
- ✅ Python 3.11+ with asyncio
- ✅ Redis 6.0+ (optional but recommended)
- ⏳ MCP server infrastructure
- ⏳ OpenAI/Anthropic API keys
- ✅ Docker (for production Redis)

---

## 🎯 Success Metrics

### Deployment Success Criteria
- [ ] Redis installed and connected
- [ ] All 3 MCP servers configured and tested
- [ ] Client wrappers updated with real implementations
- [ ] All tests passing with real MCP clients
- [ ] Production validation complete with real URLs
- [ ] Monitoring and logging configured

### Performance Targets
- Cache hit response: <100ms (✅ Target)
- Idox extraction: <3s (✅ Target)
- Custom extraction: <3s (✅ Target)
- Unknown extraction: <8s (✅ Target)
- Success rate: >95% (✅ Target)
- Cache hit rate: >70% (After 1 week)

### Quality Targets
- Applicant name accuracy: >90%
- Agent name accuracy: >90%
- False positive rate: <5%
- System uptime: >99.5%

---

## 🚨 Risk Assessment

### High-Risk Items
1. **MCP Server Availability**
   - Risk: Servers may not be production-ready
   - Mitigation: Research alternatives, keep mock fallback

2. **Extraction Accuracy**
   - Risk: Real portals may differ from test cases
   - Mitigation: Extensive testing, validation layer

3. **Cost Overruns**
   - Risk: LLM API costs higher than expected
   - Mitigation: Monitor usage, implement caching, optimize prompts

### Medium-Risk Items
1. **Redis Dependency**
   - Risk: Redis failure impacts performance
   - Mitigation: Graceful degradation already implemented

2. **Portal Changes**
   - Risk: Planning portals may change structure
   - Mitigation: Regular monitoring, adaptive extraction

### Low-Risk Items
1. **Performance**
   - Risk: Slower than expected
   - Mitigation: Async processing, caching strategy

---

## 📝 Decision Log

### Decisions Made
1. **Caching Strategy**: Redis with 24h TTL (no ES persistence)
2. **Mock Pattern**: Placeholder MCP clients for development
3. **Graceful Degradation**: System works without Redis
4. **Multi-Strategy**: Different approaches per portal type

### Pending Decisions
1. **MCP Server Choice**: Which specific implementations to use
2. **LLM Provider**: OpenAI vs Anthropic for Context7
3. **Redis Deployment**: WSL vs Docker vs Cloud
4. **Monitoring Tool**: CloudWatch, Datadog, or self-hosted

---

## 🔄 Next Actions

### Immediate (Today)
1. ✅ Create deployment plan (this document)
2. ⏳ Research available MCP server options
3. ⏳ Choose Redis deployment strategy
4. ⏳ Begin Redis installation

### Short-term (This Week)
1. ⏳ Configure all 3 MCP servers
2. ⏳ Update client wrappers
3. ⏳ Test with real portal URLs
4. ⏳ Set up basic monitoring

### Medium-term (Next Week)
1. ⏳ Production deployment
2. ⏳ Monitor performance metrics
3. ⏳ Optimize based on real data
4. ⏳ Document operational procedures

---

## 📚 Documentation

### Required Documentation
- [ ] MCP server setup guide
- [ ] Redis configuration guide
- [ ] Production deployment checklist
- [ ] Operational runbook
- [ ] Troubleshooting guide
- [ ] Cost optimization guide

### Existing Documentation
- ✅ Implementation guide (`ENRICHMENT_AGENT_IMPLEMENTATION.md`)
- ✅ Quick start guide (`ENRICHMENT_AGENT_QUICKSTART.md`)
- ✅ Redis setup guide (`REDIS_SETUP.md`)
- ✅ Completion summary (`ENRICHMENT_IMPLEMENTATION_COMPLETE.md`)

---

## 🎓 Lessons Learned (To Be Updated)

### What Works Well
- Mock client pattern allows independent development
- Graceful degradation ensures system resilience
- Comprehensive testing catches issues early

### Areas for Improvement
- TBD after production deployment

---

**Master Orchestrator Status**: Planning Complete ✅
**Next Phase**: Execution (Phase 9.1 - Redis Installation)
**Recommended Start**: Proceed with Redis setup while researching MCP servers in parallel
