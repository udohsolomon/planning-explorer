# Enrichment Agent Backend Implementation Session
**Session ID**: enrichment-agent-2025-10-04
**Started**: 2025-10-04T11:30:00Z
**Status**: Planning Complete → Execution Ready

---

## 🎯 MASTER ORCHESTRATOR STRATEGIC PLAN

### Project Objective
Implement backend infrastructure for real-time Applicant/Agent name enrichment from UK planning portals, integrating with existing Planning Explorer platform.

### Context
- **Frontend**: ✅ Complete (skeleton loading, state management, documentation)
- **Backend**: ⏳ Implementation needed (agent, caching, API integration)
- **MCP Tools Available**: Playwright, Firecrawl, Context7, Perplexity
- **Architecture**: FastAPI monolith with Elasticsearch + Supabase
- **Performance Target**: <5s enrichment, 24h cache, >95% success rate

---

## 📋 PHASE BREAKDOWN & AGENT ASSIGNMENTS

### **PHASE 1: Environment Setup** (30 minutes)
**Agent**: `devops-specialist`
**Dependencies**: None
**Execution Mode**: Independent

**Tasks**:
1. Install Python dependencies (redis, beautifulsoup4, playwright)
2. Start Redis server (Docker or local)
3. Verify MCP servers running (Playwright, Firecrawl, Context7)
4. Create directory structure: `app/agents/enrichment/`

**Success Criteria**:
- ✅ Redis responding to PING
- ✅ All Python packages installed
- ✅ MCP servers accessible
- ✅ Directory structure created

**Deliverables**:
```bash
# Redis health check
redis-cli ping  # Returns: PONG

# Python environment
pip list | grep -E 'redis|beautifulsoup4|playwright'

# Directory structure
backend/app/agents/enrichment/
  ├── __init__.py
  ├── portal_detectors.py
  ├── applicant_agent.py
  └── utils/
      ├── __init__.py
      └── validators.py
```

---

### **PHASE 2: Core Agent Implementation** (2 hours)
**Agent**: `ai-engineer` (primary) + `backend-engineer` (support)
**Dependencies**: Phase 1 complete
**Execution Mode**: Sequential (ai-engineer → backend-engineer)

#### **Step 2.1: Portal Detection Logic**
**Agent**: `ai-engineer`
**File**: `backend/app/agents/enrichment/portal_detectors.py`

**Implementation**:
```python
"""Portal type detection for UK planning portals"""

class PortalDetector:
    # Idox pattern (~60% of UK authorities)
    IDOX_PATTERN = r"publicaccess\..*\.gov\.uk/online-applications"

    # Known custom portals (~20%)
    KNOWN_CUSTOM_PORTALS = {
        "lar.liverpool.gov.uk": "liverpool_custom",
        # Extensible for future additions
    }

    @classmethod
    def detect(cls, url: str) -> Literal["idox_public_access", "liverpool_custom", "unknown"]:
        # Implementation provided in ENRICHMENT_AGENT_IMPLEMENTATION.md
        pass
```

**Success Criteria**:
- ✅ Correctly identifies Idox portals
- ✅ Correctly identifies Liverpool portal
- ✅ Returns "unknown" for other portals
- ✅ Unit tests pass (3 test cases)

---

#### **Step 2.2: Data Validation & Cleaning**
**Agent**: `ai-engineer`
**File**: `backend/app/agents/enrichment/utils/validators.py`

**Implementation**:
```python
"""Data validation for applicant/agent extraction"""

class ApplicantDataValidator:
    NA_PATTERNS = [r"^n/?a$", r"^not\s+available$", r"^none$", r"^-+$"]
    ERROR_PATTERNS = [r"applicant\s+name", r"<.*>", r"javascript:"]

    @classmethod
    def clean(cls, value: Optional[str]) -> Optional[str]:
        # Strip whitespace, check NA patterns, validate length
        pass

    @classmethod
    def validate_result(cls, applicant_name, agent_name) -> dict:
        # Return {valid, applicant_name, agent_name, warnings}
        pass
```

**Success Criteria**:
- ✅ Cleans whitespace correctly
- ✅ Detects "N/A" variations (6 patterns)
- ✅ Identifies extraction errors (HTML, labels)
- ✅ Unit tests pass (5 test cases)

---

#### **Step 2.3: Main Enrichment Agent**
**Agent**: `ai-engineer` (primary)
**File**: `backend/app/agents/enrichment/applicant_agent.py`

**Implementation** (800+ lines):
```python
"""Main enrichment agent for applicant/agent extraction"""

class ApplicantEnrichmentAgent:
    def __init__(self):
        self.firecrawl = FirecrawlClient()
        self.playwright = PlaywrightClient()
        self.context7 = Context7Client()
        self.portal_patterns = {}  # Pattern cache

    async def enrich(self, url: str, application_id: str) -> Dict:
        # 1. Detect portal type
        # 2. Select extraction strategy
        # 3. Execute extraction
        # 4. Validate data
        # 5. Return result with metadata
        pass

    async def _extract_idox(self, url: str) -> Optional[Dict]:
        # Idox Public Access extraction (Type 1)
        pass

    async def _extract_custom_direct(self, url: str, portal_type: str) -> Optional[Dict]:
        # Known custom portal extraction (Type 2)
        pass

    async def _extract_adaptive(self, url: str) -> Optional[Dict]:
        # Adaptive extraction with Context7 (Type 3)
        pass
```

**Success Criteria**:
- ✅ Enrichment completes in <5s (Idox)
- ✅ Enrichment completes in <8s (Unknown)
- ✅ Returns correct data structure
- ✅ Handles errors gracefully
- ✅ Logs all operations

**Metrics to Track**:
- Processing time per portal type
- Success rate per portal type
- Confidence scores
- Extraction method distribution

---

### **PHASE 3: MCP Client Wrappers** (1 hour)
**Agent**: `backend-engineer`
**Dependencies**: Phase 2.1-2.2 complete (can run in parallel with 2.3)
**Execution Mode**: Parallel with Phase 2.3

**Files to Create**:
1. `backend/app/services/mcp_clients/__init__.py`
2. `backend/app/services/mcp_clients/playwright_client.py`
3. `backend/app/services/mcp_clients/firecrawl_client.py`
4. `backend/app/services/mcp_clients/context7_client.py`

#### **File 1: Playwright Client**
```python
"""Playwright MCP client wrapper"""

class PlaywrightClient:
    """Wrapper for Playwright MCP server"""

    async def fetch(self, url: str) -> str:
        """
        Fetch page content using Playwright (handles JavaScript)

        Args:
            url: URL to fetch

        Returns:
            HTML content as string
        """
        # Call your Playwright MCP server
        # Return page.content() or similar
        pass
```

#### **File 2: Firecrawl Client**
```python
"""Firecrawl MCP client wrapper"""

class FirecrawlClient:
    """Wrapper for Firecrawl MCP server"""

    async def fetch(self, url: str) -> str:
        """
        Fast HTML scraping for static content

        Args:
            url: URL to fetch

        Returns:
            HTML content as string
        """
        # Call your Firecrawl MCP server
        # Return HTML content
        pass
```

#### **File 3: Context7 Client**
```python
"""Context7 MCP client wrapper"""

class Context7Client:
    """Wrapper for Context7 MCP server (LLM-powered extraction)"""

    async def extract(self, page_content: str, prompt: str) -> Optional[Dict]:
        """
        Semantic extraction using LLM

        Args:
            page_content: HTML or text content
            prompt: Extraction instructions

        Returns:
            Extracted data dictionary or None
        """
        # Call your Context7 MCP server
        # Parse JSON response
        # Return {applicant_name: str|None, agent_name: str|None}
        pass
```

**Success Criteria**:
- ✅ All clients successfully connect to MCP servers
- ✅ Firecrawl returns HTML for test URL
- ✅ Playwright handles JS-rendered page
- ✅ Context7 extracts structured data
- ✅ Error handling for timeouts/failures

---

### **PHASE 4: Redis Caching Service** (30 minutes)
**Agent**: `backend-engineer`
**Dependencies**: Phase 1 complete
**Execution Mode**: Can run in parallel with Phase 2-3

**File**: `backend/app/services/cache_service.py`

**Implementation**:
```python
"""Redis caching service for enriched data"""

class CacheService:
    def __init__(self):
        self.redis = None
        self.ttl_seconds = 86400  # 24 hours

    async def connect(self, host="localhost", port=6379):
        self.redis = await redis.from_url(f"redis://{host}:{port}")

    async def get_enrichment(self, application_id: str) -> Optional[dict]:
        key = f"applicant_agent:{application_id}"
        value = await self.redis.get(key)
        return json.loads(value) if value else None

    async def set_enrichment(self, application_id: str, data: dict) -> bool:
        key = f"applicant_agent:{application_id}"
        await self.redis.setex(key, self.ttl_seconds, json.dumps(data))
        return True

    async def invalidate(self, application_id: str) -> bool:
        key = f"applicant_agent:{application_id}"
        await self.redis.delete(key)
        return True

cache = CacheService()  # Global instance
```

**Success Criteria**:
- ✅ Redis connection established
- ✅ Get/set operations work
- ✅ TTL set correctly (24h)
- ✅ Health check passes
- ✅ Integration test passes

---

### **PHASE 5: API Endpoint Integration** (45 minutes)
**Agent**: `backend-engineer`
**Dependencies**: Phase 2, 3, 4 complete
**Execution Mode**: Sequential after all previous phases

**File**: `backend/app/api/reports.py` (modify existing)

**Implementation**:
```python
"""Report generation endpoint with enrichment"""

from app.agents import enrich_applicant_data
from app.services.cache_service import cache

@router.get("/report/{application_id}")
async def get_bank_grade_report(application_id: str):
    """
    Generate bank-grade report with real-time applicant/agent enrichment
    """
    # 1. Fetch base data from Elasticsearch
    es_data = await get_application_from_es(application_id)

    # 2. Check Redis cache for enrichment
    cached_enrichment = await cache.get_enrichment(application_id)

    if cached_enrichment:
        # Cache hit - merge and return immediately
        logger.info(f"Cache hit for enrichment: {application_id}")
        return merge_enrichment_data(es_data, cached_enrichment)

    # 3. Cache miss - trigger enrichment agent
    logger.info(f"Cache miss - triggering enrichment agent: {application_id}")

    try:
        enrichment_result = await asyncio.wait_for(
            enrich_applicant_data(
                url=es_data.get('url'),
                application_id=application_id
            ),
            timeout=5.0  # 5 second max
        )

        if enrichment_result['success']:
            # Cache successful extraction
            await cache.set_enrichment(
                application_id,
                enrichment_result['data']
            )

            logger.info(f"Enrichment successful: {application_id} "
                       f"in {enrichment_result['metadata']['processing_time_ms']}ms")

            return merge_enrichment_data(es_data, enrichment_result['data'])
        else:
            # Extraction failed - return partial data
            logger.warning(f"Enrichment failed: {application_id}")
            return merge_enrichment_data(es_data, {
                'applicant_name': None,
                'agent_name': None
            })

    except asyncio.TimeoutError:
        # Agent timeout - return partial with loading status
        logger.warning(f"Enrichment timeout: {application_id}")
        return {
            **es_data,
            'applicant_name': None,
            'agent_name': None,
            'enrichment_status': 'loading'
        }

def merge_enrichment_data(es_data: dict, enrichment: dict) -> dict:
    """Merge enrichment data into report"""
    if 'application_details' not in es_data:
        es_data['application_details'] = {}

    es_data['application_details']['applicant_name'] = enrichment.get('applicant_name')
    es_data['application_details']['agent_name'] = enrichment.get('agent_name')

    return es_data
```

**Success Criteria**:
- ✅ Endpoint responds in <5s with enrichment
- ✅ Endpoint responds in <100ms with cache hit
- ✅ Timeout handling works correctly
- ✅ Error handling doesn't break report generation
- ✅ Integration test passes with real URL

---

### **PHASE 6: Application Lifecycle Integration** (15 minutes)
**Agent**: `backend-engineer`
**Dependencies**: Phase 4 complete
**Execution Mode**: Sequential

**File**: `backend/app/main.py` (modify existing)

**Implementation**:
```python
"""FastAPI application with enrichment support"""

from app.services.cache_service import cache

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Planning Explorer API...")

    # Connect to Redis
    await cache.connect()
    logger.info("Redis cache connected")

    # Existing connections...
    # await elasticsearch.connect()
    # await supabase.connect()

    yield

    # Shutdown
    logger.info("Shutting down Planning Explorer API...")
    await cache.close()
    logger.info("Redis cache closed")

app = FastAPI(lifespan=lifespan)
```

**Success Criteria**:
- ✅ Redis connects on startup
- ✅ Redis disconnects on shutdown
- ✅ Application starts without errors
- ✅ Health check includes cache status

---

### **PHASE 7: Testing & Validation** (1 hour)
**Agent**: `qa-engineer`
**Dependencies**: All previous phases complete
**Execution Mode**: Sequential

#### **Test Suite 1: Unit Tests**
**File**: `backend/tests/agents/test_portal_detectors.py`

```python
"""Unit tests for portal detection"""

def test_detect_idox_portal():
    url = "https://publicaccess.dover.gov.uk/online-applications/..."
    assert PortalDetector.detect(url) == "idox_public_access"

def test_detect_liverpool_portal():
    url = "https://lar.liverpool.gov.uk/planning/..."
    assert PortalDetector.detect(url) == "liverpool_custom"

def test_detect_unknown_portal():
    url = "https://example.com/planning/12345"
    assert PortalDetector.detect(url) == "unknown"
```

#### **Test Suite 2: Integration Tests**
**File**: `backend/tests/agents/test_enrichment_integration.py`

```python
"""Integration tests for enrichment agent"""

@pytest.mark.asyncio
async def test_enrich_dover_application():
    """Test with real Dover (Idox) URL"""
    url = "https://publicaccess.dover.gov.uk/online-applications/..."
    result = await enrich_applicant_data(url, "TEST/001")

    assert result['success'] == True
    assert result['data']['applicant_name'] is not None
    assert result['metadata']['portal_type'] == "idox_public_access"
    assert result['metadata']['processing_time_ms'] < 5000

@pytest.mark.asyncio
async def test_enrich_liverpool_application():
    """Test with real Liverpool URL"""
    url = "https://lar.liverpool.gov.uk/planning/index.html?..."
    result = await enrich_applicant_data(url, "TEST/002")

    assert result['success'] == True
    assert result['data']['applicant_name'] is not None

@pytest.mark.asyncio
async def test_cache_hit():
    """Test Redis caching"""
    app_id = "TEST/003"

    # First call - cache miss
    result1 = await get_report(app_id)

    # Second call - cache hit
    start = time.time()
    result2 = await get_report(app_id)
    duration = (time.time() - start) * 1000

    assert duration < 100  # Cache hit should be <100ms
    assert result1 == result2
```

**Success Criteria**:
- ✅ All unit tests pass (10+ tests)
- ✅ Integration tests pass with real URLs
- ✅ Cache hit test confirms <100ms response
- ✅ Error handling tests pass
- ✅ Performance tests meet targets

---

### **PHASE 8: Monitoring & Logging** (30 minutes)
**Agent**: `backend-engineer`
**Dependencies**: Phase 5 complete
**Execution Mode**: Can run in parallel with Phase 7

**Implementation Areas**:

1. **Structured Logging**
```python
logger.info(f"Enrichment started: {application_id}", extra={
    "application_id": application_id,
    "url": url,
    "portal_type": portal_type
})

logger.info(f"Enrichment completed: {application_id}", extra={
    "application_id": application_id,
    "processing_time_ms": processing_time,
    "success": True,
    "method": extraction_method,
    "confidence": confidence
})
```

2. **Metrics Collection**
```python
# Track in-memory or push to monitoring system
metrics = {
    "total_enrichments": 0,
    "cache_hits": 0,
    "cache_misses": 0,
    "success_by_portal_type": {
        "idox": {"total": 0, "success": 0},
        "custom": {"total": 0, "success": 0},
        "unknown": {"total": 0, "success": 0}
    },
    "avg_processing_time_ms": 0
}
```

3. **Health Endpoint**
```python
@app.get("/health/enrichment")
async def enrichment_health():
    return {
        "status": "healthy",
        "cache": await cache.health_check(),
        "metrics": {
            "cache_hit_rate": calculate_hit_rate(),
            "avg_processing_time": get_avg_time(),
            "success_rate": calculate_success_rate()
        }
    }
```

**Success Criteria**:
- ✅ All enrichment operations logged
- ✅ Metrics tracked and accessible
- ✅ Health endpoint returns status
- ✅ Errors logged with full context

---

## 📊 EXECUTION TIMELINE

| Phase | Agent | Duration | Dependencies | Start | End |
|-------|-------|----------|--------------|-------|-----|
| 1. Setup | devops-specialist | 30 min | None | T+0 | T+30m |
| 2. Core Agent | ai-engineer + backend | 2 hours | Phase 1 | T+30m | T+2h30m |
| 3. MCP Clients | backend-engineer | 1 hour | Phase 1 | T+30m | T+1h30m |
| 4. Caching | backend-engineer | 30 min | Phase 1 | T+30m | T+1h |
| 5. API Integration | backend-engineer | 45 min | 2,3,4 | T+2h30m | T+3h15m |
| 6. Lifecycle | backend-engineer | 15 min | Phase 4 | T+1h | T+1h15m |
| 7. Testing | qa-engineer | 1 hour | All | T+3h15m | T+4h15m |
| 8. Monitoring | backend-engineer | 30 min | Phase 5 | T+3h15m | T+3h45m |

**Total Duration**: ~4.5 hours
**Critical Path**: Phase 1 → 2 → 5 → 7
**Parallel Opportunities**: Phases 3, 4, 8 can run concurrently

---

## 🎯 SUCCESS METRICS

### Performance Targets
| Metric | Target | How to Measure |
|--------|--------|----------------|
| Cache Hit Response | <100ms | Time from API call to response |
| Idox Extraction | <3s | Agent processing time |
| Custom Extraction | <3s | Agent processing time |
| Adaptive Extraction | <8s | Agent processing time |
| Cache Hit Rate | >70% | cache_hits / total_requests |
| Success Rate (Idox) | >98% | successful_extractions / total_idox |
| Success Rate (Custom) | >92% | successful_extractions / total_custom |
| Success Rate (Unknown) | >85% | successful_extractions / total_unknown |

### Quality Targets
- ✅ 100% unit test coverage for validators
- ✅ 100% integration test coverage for portal types
- ✅ 0 blocking errors during extraction
- ✅ Graceful degradation on failures

---

## 🚨 RISK ASSESSMENT & MITIGATION

### Risk 1: MCP Server Integration Complexity
**Probability**: Medium
**Impact**: High
**Mitigation**:
- Create thin wrapper layer
- Mock MCP responses for testing
- Have fallback extraction strategies

### Risk 2: Portal Structure Changes
**Probability**: Low (for established portals)
**Impact**: Medium
**Mitigation**:
- Log all extraction failures with HTML samples
- Alert on success rate drops
- Maintain pattern cache for quick updates

### Risk 3: Performance Degradation
**Probability**: Low
**Impact**: Medium
**Mitigation**:
- Implement timeout protection (5s max)
- Cache aggressively (24h TTL)
- Monitor processing times

### Risk 4: Redis Unavailability
**Probability**: Low
**Impact**: High
**Mitigation**:
- Gracefully degrade to no caching
- Agent still runs, just slower
- Alert on cache failures

---

## 📦 DELIVERABLES CHECKLIST

### Code Files
- [x] `backend/app/agents/__init__.py`
- [ ] `backend/app/agents/enrichment/__init__.py`
- [ ] `backend/app/agents/enrichment/portal_detectors.py`
- [ ] `backend/app/agents/enrichment/applicant_agent.py`
- [ ] `backend/app/agents/enrichment/utils/__init__.py`
- [ ] `backend/app/agents/enrichment/utils/validators.py`
- [ ] `backend/app/services/mcp_clients/__init__.py`
- [ ] `backend/app/services/mcp_clients/playwright_client.py`
- [ ] `backend/app/services/mcp_clients/firecrawl_client.py`
- [ ] `backend/app/services/mcp_clients/context7_client.py`
- [ ] `backend/app/services/cache_service.py`
- [ ] `backend/app/api/reports.py` (modified)
- [ ] `backend/app/main.py` (modified)

### Test Files
- [ ] `backend/tests/agents/__init__.py`
- [ ] `backend/tests/agents/test_portal_detectors.py`
- [ ] `backend/tests/agents/test_validators.py`
- [ ] `backend/tests/agents/test_applicant_agent.py`
- [ ] `backend/tests/agents/test_enrichment_integration.py`

### Documentation
- [x] `backend/ENRICHMENT_AGENT_IMPLEMENTATION.md`
- [x] `frontend/ENRICHMENT_AGENT_INTEGRATION.md`
- [x] `ENRICHMENT_AGENT_QUICKSTART.md`
- [x] `.claude/sessions/enrichment-agent-implementation.md` (this file)

---

## 🔄 NEXT ACTIONS

### Immediate (Start Now)
1. **DevOps Specialist**: Execute Phase 1 (Setup)
   - Install dependencies
   - Start Redis
   - Create directory structure

### After Phase 1
2. **AI Engineer**: Execute Phase 2.1-2.2 (Portal Detection + Validation)
3. **Backend Engineer**: Execute Phase 3 & 4 in parallel (MCP Clients + Caching)

### After Phases 2, 3, 4
4. **Backend Engineer**: Execute Phase 5 (API Integration)
5. **QA Engineer**: Execute Phase 7 (Testing)

### Final Steps
6. **Backend Engineer**: Execute Phase 8 (Monitoring)
7. **Master Orchestrator**: Integration review and validation

---

## 📞 COORDINATION PROTOCOL

### Status Updates
- Update TodoWrite after each phase completion
- Log all blockers immediately
- Report success metrics after testing

### Escalation Criteria
- Phase takes >2x estimated time
- MCP integration fails
- Success rate <80% in testing
- Critical bugs discovered

---

**Session Status**: ✅ Planning Complete
**Ready for Execution**: Yes
**Estimated Completion**: T+4.5 hours
**Next Agent**: `devops-specialist` (Phase 1)

---

*Master Orchestrator: Strategic plan approved. All agents have clear assignments. Execute Phase 1 immediately.*
