# Applicant/Agent Enrichment Agent - Frontend Integration Guide

## Overview

The Planning Explorer platform now includes **real-time data enrichment** for Applicant Name and Agent Name fields in planning application reports. This document describes the frontend implementation and backend integration requirements.

## Implementation Status

### ✅ Completed (Frontend)
- [x] Skeleton loading component (`src/components/ui/Skeleton.tsx`)
- [x] Loading state management in report page
- [x] Conditional rendering for applicant/agent fields
- [x] 3-second simulation for demo purposes
- [x] Comprehensive documentation in code comments
- [x] Sample report documentation

### ⏳ Pending (Backend)
- [ ] Enrichment agent implementation (Python/FastAPI)
- [ ] Redis caching layer (24h TTL)
- [ ] API endpoint modification to trigger agent
- [ ] Optional: Polling endpoint for enrichment status
- [ ] Optional: WebSocket support for real-time updates

## User Experience Flow

```
1. User searches for planning applications
2. User clicks "Generate Report" or "View Details"
3. Report page loads immediately with base data
4. Applicant/Agent fields show animated skeleton (pulsing gray bar)
5. After 2-5 seconds, skeleton replaced with actual names
6. If already cached, fields populate immediately (no skeleton)
```

## Frontend Implementation

### File: `src/components/ui/Skeleton.tsx`
```typescript
import { cn } from '@/lib/utils'

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {}

export function Skeleton({ className, ...props }: SkeletonProps) {
  return (
    <div
      className={cn('animate-pulse rounded-md bg-slate-200', className)}
      {...props}
    />
  )
}
```

### File: `src/app/report/[id]/page.tsx`

**State Management:**
```typescript
const [enrichmentLoading, setEnrichmentLoading] = useState(false)
```

**Data Fetching Logic:**
```typescript
// Set loading state initially
setEnrichmentLoading(true)

// Fetch report data
const reportResponse = await apiClient.getBankGradeReport(applicationId, {...})

// Check if data available
if (report.application_details?.applicant_name || report.application_details?.agent_name) {
  setEnrichmentLoading(false)  // Cache hit - data available
} else {
  // Cache miss - simulate agent enrichment (3s delay)
  setTimeout(() => {
    setEnrichmentLoading(false)
  }, 3000)
}
```

**Conditional Rendering:**
```typescript
<div className="flex items-start gap-3">
  <User className="w-5 h-5 text-slate-400 mt-0.5" />
  <div className="flex-1">
    <p className="text-xs text-slate-500">Applicant Name</p>
    {enrichmentLoading ? (
      <Skeleton className="h-5 w-48 mt-1" />
    ) : (
      <p className="text-sm text-slate-800 font-medium">
        {safeDisplay(report?.application_details?.applicant_name)}
      </p>
    )}
  </div>
</div>
```

## Backend API Requirements

### Endpoint: `GET /api/report/{application_id}`

#### Response Format

**Case 1: Cache Hit (Data Available Immediately)**
```json
{
  "success": true,
  "data": {
    "report": {
      "application_details": {
        "applicant_name": "Discovery Park (South) Limited",
        "agent_name": "KSR Architects",
        "reference": "DOV/24/01234",
        "address": "33 Floyd Avenue Manchester M21 7LU",
        ...
      },
      ...
    }
  },
  "metadata": {
    "enrichment_source": "cache",
    "cached_at": "2025-10-04T05:30:00Z"
  }
}
```

**Case 2: Cache Miss (Agent Triggered)**
```json
{
  "success": true,
  "data": {
    "report": {
      "application_details": {
        "applicant_name": null,
        "agent_name": null,
        "reference": "DOV/24/01234",
        ...
      },
      ...
    },
    "enrichment_status": "loading",
    "enrichment_job_id": "enrich_DOV_24_01234_1728022500"
  }
}
```

### Backend Implementation Steps

#### 1. Install Dependencies
```bash
pip install redis aioredis playwright firecrawl-py
```

#### 2. Redis Cache Setup
```python
import redis
from datetime import timedelta

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True
)

CACHE_TTL = 86400  # 24 hours
```

#### 3. Enrichment Agent Integration
```python
from app.agents.applicant_enrichment_agent import enrich_applicant_data
import asyncio

async def get_report(application_id: str):
    # Fetch base data from Elasticsearch
    es_data = await get_application_from_es(application_id)

    # Check cache for enriched data
    cache_key = f"applicant_agent:{application_id}"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        # Cache hit - merge and return immediately
        enriched_data = json.loads(cached_data)
        return merge_report_data(es_data, enriched_data)

    # Cache miss - trigger agent with timeout
    try:
        enrichment_result = await asyncio.wait_for(
            enrich_applicant_data(
                url=es_data['url'],
                application_id=application_id
            ),
            timeout=5.0  # 5 second max
        )

        if enrichment_result['success']:
            # Cache successful extraction
            redis_client.setex(
                cache_key,
                CACHE_TTL,
                json.dumps(enrichment_result['data'])
            )
            return merge_report_data(es_data, enrichment_result['data'])
        else:
            # Extraction failed - return partial
            return merge_report_data(es_data, {
                'applicant_name': None,
                'agent_name': None
            })

    except asyncio.TimeoutError:
        # Agent timeout - return partial with loading status
        return {
            **es_data,
            'applicant_name': None,
            'agent_name': None,
            'enrichment_status': 'loading'
        }
```

#### 4. Agent Implementation
See separate agent prompt document for full implementation details.

**Quick Summary:**
```python
# app/agents/applicant_enrichment_agent.py

class ApplicantEnrichmentAgent:
    async def enrich(self, url: str, application_id: str) -> Dict:
        # Detect portal type
        portal_type = self._detect_portal_type(url)

        # Extract using appropriate strategy
        if portal_type == "idox_public_access":
            result = await self._extract_idox(url)  # Firecrawl
        elif portal_type in self.portal_patterns:
            result = await self._extract_custom_cached(url, portal_type)
        else:
            result = await self._extract_adaptive(url)  # Context7

        return {
            "success": result is not None,
            "data": result or {"applicant_name": None, "agent_name": None}
        }
```

## Portal Types & Extraction Strategies

### Type 1: Idox Public Access (~60% of UK authorities)
- **URL Pattern**: `publicaccess.{authority}.gov.uk/online-applications/applicationDetails.do`
- **Navigation**: Change `activeTab=summary` to `activeTab=details`
- **Tool**: Firecrawl (fast, static HTML)
- **Speed**: ~2 seconds
- **Example**: Dover, Canterbury, Brighton

### Type 2: Custom Portals (~20% of UK authorities)
- **Example**: Liverpool - `lar.liverpool.gov.uk/planning/index.html?fa=getApplication&id={id}`
- **Navigation**: Direct access
- **Tool**: Firecrawl (fast)
- **Speed**: ~2 seconds

### Type 3: Unknown/Adaptive (~20% of UK authorities)
- **Detection**: Context7 MCP for structure analysis
- **Extraction**: Semantic extraction with pattern caching
- **Tool**: Playwright + Context7
- **Speed**: ~5-8 seconds
- **Learning**: Caches successful patterns for future use

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Cache Hit Response | <100ms | Redis lookup only |
| Type 1/2 Extraction | <3s | Firecrawl scraping |
| Type 3 Extraction | <8s | Playwright + Context7 |
| Cache TTL | 24h | Balances freshness vs. load |
| Success Rate (Type 1) | >98% | Known portal structure |
| Success Rate (Type 2) | >92% | Cached patterns |
| Success Rate (Type 3) | >85% | Adaptive, improves over time |
| Overall Coverage | 100% | All applications with URLs |

## Testing

### Frontend Testing
```bash
# Run dev server
npm run dev

# Navigate to sample report
http://localhost:3000/report/sample

# Observe:
# 1. Applicant/Agent fields show skeleton for 3 seconds
# 2. Fields populate with data after delay
# 3. Skeleton has smooth pulse animation
```

### Backend Testing (After Agent Implementation)
```python
# Test cache hit
response = client.get("/api/report/DOV/24/01234")
assert response.json()['data']['report']['application_details']['applicant_name'] is not None

# Test cache miss (first request)
redis_client.delete("applicant_agent:DOV/24/01234")
response = client.get("/api/report/DOV/24/01234")
assert response.json()['enrichment_status'] == 'loading'

# Test cache after enrichment
time.sleep(3)
response = client.get("/api/report/DOV/24/01234")
assert response.json()['data']['report']['application_details']['applicant_name'] is not None
```

## Visual Design

### Skeleton Animation
- **Color**: `bg-slate-200` (light gray)
- **Animation**: `animate-pulse` (built-in Tailwind)
- **Dimensions**: `h-5 w-48` (height: 1.25rem, width: 12rem)
- **Border Radius**: `rounded-md`

### Loading State
```
┌─────────────────────────────────────┐
│ Timeline                             │
├─────────────────────────────────────┤
│ 👤 Applicant Name                   │
│    ▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░              │ ← Pulsing skeleton
│                                      │
│ 👤 Agent Name                       │
│    ▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░              │ ← Pulsing skeleton
└─────────────────────────────────────┘
```

### Loaded State
```
┌─────────────────────────────────────┐
│ Timeline                             │
├─────────────────────────────────────┤
│ 👤 Applicant Name                   │
│    Discovery Park (South) Limited    │
│                                      │
│ 👤 Agent Name                       │
│    KSR Architects                    │
└─────────────────────────────────────┘
```

## Optional Enhancements

### 1. Polling Endpoint (Progressive Loading)
```typescript
// Frontend polling logic
async function pollForEnrichment(id: string) {
  const interval = setInterval(async () => {
    const response = await fetch(`/api/report/${id}/enrichment-status`)
    const status = await response.json()

    if (status.status === 'completed') {
      setReport(prev => ({
        ...prev,
        applicant_name: status.data.applicant_name,
        agent_name: status.data.agent_name
      }))
      setEnrichmentLoading(false)
      clearInterval(interval)
    }
  }, 1000)  // Poll every 1 second

  // Stop after 10 seconds
  setTimeout(() => clearInterval(interval), 10000)
}
```

### 2. WebSocket Support (Real-time)
```typescript
// Frontend WebSocket connection
const ws = new WebSocket(`ws://localhost:8000/ws/report/${params.id}`)

ws.onmessage = (event) => {
  const message = JSON.parse(event.data)

  if (message.type === 'enrichment_complete') {
    setReport(prev => ({
      ...prev,
      applicant_name: message.data.applicant_name,
      agent_name: message.data.agent_name
    }))
    setEnrichmentLoading(false)
  }
}
```

## Error Handling

### Frontend
- If enrichment fails, show "N/A" instead of skeleton
- No error message to user (graceful degradation)
- Fields simply remain as "N/A" if data unavailable

### Backend
- Log extraction failures for monitoring
- Return null values instead of errors
- Retry logic for network failures (max 3 attempts)
- Cache extraction failures with shorter TTL (1 hour) to prevent repeated scraping

## Monitoring & Metrics

### Key Metrics to Track
- Cache hit rate (target: >70% after initial period)
- Average enrichment time by portal type
- Extraction success rate by portal type
- Number of unique portal patterns discovered
- Manual review queue size

### Logging
```python
logger.info(f"Enrichment cache hit for {application_id}")
logger.info(f"Enrichment cache miss for {application_id}, triggering agent")
logger.info(f"Enrichment success for {application_id} in {processing_time}ms")
logger.error(f"Enrichment failed for {application_id}: {error_message}")
```

## Security Considerations

- Rate limiting on enrichment agent (max 10 concurrent requests)
- Timeout protection (5 second max per extraction)
- URL validation before scraping (must be valid planning portal)
- No sensitive data in cache keys (use application_id, not personal info)
- Redis authentication in production

## Next Steps

1. **Backend Team**: Implement enrichment agent following agent prompt document
2. **DevOps Team**: Set up Redis instance with 24h TTL configuration
3. **Backend Team**: Modify `/api/report/{id}` endpoint to integrate agent
4. **Testing Team**: Create test suite for agent extraction accuracy
5. **Frontend Team**: Monitor skeleton loading behavior in production

## Documentation References

- **Agent Prompt Document**: Full specification for enrichment agent implementation
- **API Documentation**: Backend API endpoint specifications
- **Frontend Component Library**: shadcn/ui Skeleton component usage

---

**Last Updated**: 2025-10-04
**Implementation**: Frontend Complete, Backend Pending
**Contact**: Development Team
