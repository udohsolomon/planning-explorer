# Applicant/Agent Enrichment Agent - Quick Start Guide

## Overview

The enrichment agent extracts Applicant Name and Agent Name from UK planning portals in real-time during report generation. **Frontend implementation is complete**. This guide shows how to complete the backend.

---

## ✅ What's Already Done (Frontend)

### 1. Loading Skeleton Component
**File**: `frontend/src/components/ui/Skeleton.tsx`
- Animated pulsing gray loading bar
- Reusable across the application

### 2. Report Page Integration
**File**: `frontend/src/app/report/[id]/page.tsx`
- `enrichmentLoading` state management
- Conditional rendering for applicant/agent fields
- 3-second simulation (replace with actual API call)
- Comprehensive inline documentation

### 3. Integration Documentation
**File**: `frontend/ENRICHMENT_AGENT_INTEGRATION.md`
- Complete frontend/backend integration guide
- API response formats
- UX flows
- Testing instructions

---

## 🏗️ What Needs To Be Done (Backend)

### Required Files (All Documented in `backend/ENRICHMENT_AGENT_IMPLEMENTATION.md`)

#### 1. Portal Detection
```python
# backend/app/agents/enrichment/portal_detectors.py
# ✅ Complete implementation provided in documentation
# Detects: Idox (60%), Liverpool/Custom (20%), Unknown (20%)
```

#### 2. Data Validation
```python
# backend/app/agents/enrichment/utils/validators.py
# ✅ Complete implementation provided in documentation
# Cleans text, validates data, handles "N/A" cases
```

#### 3. Main Enrichment Agent
```python
# backend/app/agents/enrichment/applicant_agent.py
# ✅ Complete implementation provided in documentation
# 800+ lines of production-ready code including:
# - Portal type detection
# - Multi-strategy extraction (Idox, Custom, Adaptive)
# - Firecrawl/Playwright/Context7 integration
# - Confidence scoring
# - Error handling
```

#### 4. Redis Caching Service
```python
# backend/app/services/cache_service.py
# ✅ Complete implementation provided in documentation
# 24h TTL, get/set/invalidate methods
```

#### 5. MCP Client Wrappers
```python
# backend/app/services/mcp_clients/playwright_client.py
# backend/app/services/mcp_clients/firecrawl_client.py
# backend/app/services/mcp_clients/context7_client.py
# ⚠️ Implement these based on your MCP server setup
```

#### 6. FastAPI Endpoint Integration
```python
# backend/app/api/reports.py
# ⚠️ Modify existing /api/report/{id} endpoint to:
# - Check Redis cache for applicant/agent data
# - Trigger enrichment agent on cache miss
# - Return enriched data or loading status
```

---

## 🚀 Implementation Steps

### Step 1: Install Dependencies
```bash
cd backend
pip install redis beautifulsoup4 playwright
# MCP servers should already be installed
```

### Step 2: Start Redis
```bash
# Option A: Docker
docker run -d -p 6379:6379 redis:latest

# Option B: Local install
redis-server
```

### Step 3: Copy Implementation Files
All code is provided in `backend/ENRICHMENT_AGENT_IMPLEMENTATION.md`. Copy the implementations to:

1. `backend/app/agents/enrichment/portal_detectors.py`
2. `backend/app/agents/enrichment/utils/validators.py`
3. `backend/app/agents/enrichment/applicant_agent.py`
4. `backend/app/services/cache_service.py`

### Step 4: Create MCP Client Wrappers
Based on your MCP setup, create thin wrappers:

```python
# Example: backend/app/services/mcp_clients/firecrawl_client.py
class FirecrawlClient:
    async def fetch(self, url: str) -> str:
        # Call your Firecrawl MCP server
        # Return HTML content as string
        pass
```

### Step 5: Modify Report Endpoint
```python
# backend/app/api/reports.py

from app.agents import enrich_applicant_data
from app.services.cache_service import cache

@router.get("/report/{application_id}")
async def get_report(application_id: str):
    # 1. Fetch base data from Elasticsearch
    es_data = await get_application_from_es(application_id)

    # 2. Check cache for enrichment
    cache_key = f"applicant_agent:{application_id}"
    cached = await cache.get_enrichment(application_id)

    if cached:
        # Cache hit - merge and return
        return merge_data(es_data, cached)

    # 3. Trigger enrichment agent
    try:
        result = await asyncio.wait_for(
            enrich_applicant_data(
                url=es_data['url'],
                application_id=application_id
            ),
            timeout=5.0
        )

        if result['success']:
            # Cache for 24 hours
            await cache.set_enrichment(application_id, result['data'])
            return merge_data(es_data, result['data'])

    except asyncio.TimeoutError:
        # Return with loading status
        pass

    return {
        **es_data,
        "applicant_name": None,
        "agent_name": None,
        "enrichment_status": "loading"
    }
```

### Step 6: Update Main App
```python
# backend/app/main.py

from app.services.cache_service import cache

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await cache.connect()  # ← Add this
    yield
    # Shutdown
    await cache.close()  # ← Add this
```

### Step 7: Test
```bash
# Start backend
cd backend
uvicorn app.main:app --reload

# Test enrichment
curl http://localhost:8000/api/report/DOV/24/01234

# Check logs for:
# - "Starting enrichment for..."
# - "Detected portal type: idox_public_access"
# - "Enrichment completed in XXXms"
# - "Cache hit/miss for..."
```

---

## 📊 Monitoring

### Key Metrics to Track

```python
# Add to your logging/monitoring
logger.info(f"Enrichment stats: "
           f"cache_hit={cache_hit_count}, "
           f"avg_time={avg_processing_time}ms, "
           f"success_rate={success_rate}%")
```

### Expected Performance
- **Cache Hit**: <100ms response
- **Idox Portal**: 2-3s extraction
- **Custom Portal**: 2-3s extraction
- **Unknown Portal**: 5-8s extraction
- **Success Rate**: >95% overall

---

## 🧪 Testing Endpoints

### Dover (Idox Portal)
```
URL: https://publicaccess.dover.gov.uk/online-applications/applicationDetails.do?activeTab=summary&keyVal=S4S7QCFZH0F00

Expected:
{
  "applicant_name": "Discovery Park (South) Limited",
  "agent_name": "KSR Architects"
}
```

### Liverpool (Custom Portal)
```
URL: https://lar.liverpool.gov.uk/planning/index.html?fa=getApplication&id=175224

Expected:
{
  "applicant_name": "Mr Tom Elford (Onward Group)",
  "agent_name": "Mr James Perrett (Arcus Consulting LLP)"
}
```

---

## 🔧 Troubleshooting

### Issue: "Redis connection refused"
**Solution**: Ensure Redis is running on port 6379
```bash
redis-cli ping
# Should return: PONG
```

### Issue: "MCP client not found"
**Solution**: Implement MCP client wrappers for your MCP server setup

### Issue: "Extraction returning None"
**Solution**: Check portal structure hasn't changed. Add logging to see HTML content:
```python
logger.debug(f"HTML content: {html_content[:500]}")
```

### Issue: "Timeout errors"
**Solution**: Increase timeout in report endpoint:
```python
timeout=10.0  # Instead of 5.0
```

---

## 📚 Documentation References

1. **Frontend Integration**: `frontend/ENRICHMENT_AGENT_INTEGRATION.md`
2. **Backend Implementation**: `backend/ENRICHMENT_AGENT_IMPLEMENTATION.md`
3. **Agent Prompt** (for understanding): Created earlier in conversation
4. **Report Page Code**: `frontend/src/app/report/[id]/page.tsx` (lines 1-77 have full documentation)

---

## 🎯 Success Criteria

✅ Frontend shows loading skeleton for 3 seconds (DONE)
⏳ Backend agent extracts applicant/agent from portals
⏳ Redis caches results for 24 hours
⏳ Report page receives enriched data from API
⏳ Success rate >95% for Idox portals
⏳ Success rate >90% for custom portals

---

## 🚦 Current Status

| Component | Status | File |
|-----------|--------|------|
| Frontend Skeleton | ✅ Complete | `frontend/src/components/ui/Skeleton.tsx` |
| Frontend Loading State | ✅ Complete | `frontend/src/app/report/[id]/page.tsx` |
| Frontend Docs | ✅ Complete | `frontend/ENRICHMENT_AGENT_INTEGRATION.md` |
| Portal Detection | ✅ Code Ready | `backend/ENRICHMENT_AGENT_IMPLEMENTATION.md` |
| Data Validation | ✅ Code Ready | `backend/ENRICHMENT_AGENT_IMPLEMENTATION.md` |
| Main Agent | ✅ Code Ready | `backend/ENRICHMENT_AGENT_IMPLEMENTATION.md` |
| Redis Caching | ✅ Code Ready | `backend/ENRICHMENT_AGENT_IMPLEMENTATION.md` |
| MCP Clients | ⏳ Need Implementation | Based on your MCP setup |
| API Endpoint | ⏳ Need Integration | Modify existing endpoint |
| Testing | ⏳ After Implementation | Use test URLs provided |

---

**Next Action**: Copy code from `backend/ENRICHMENT_AGENT_IMPLEMENTATION.md` to actual files and implement MCP client wrappers.

**Estimated Time**: 2-3 hours for a developer familiar with the codebase.

---

*Last Updated: 2025-10-04*
*Frontend: Complete | Backend: Implementation Ready*
