# Planning Stats Backend Implementation Guide

## Overview
The frontend now fetches real-time statistics from Elasticsearch. You need to implement the `/v1/stats/overview` endpoint in the FastAPI backend.

---

## Frontend Changes Completed ✅

### 1. API Client Method Added
**File:** `/frontend/src/lib/api.ts`

```typescript
async getPlanningStats(): Promise<APIResponse<{
  totalApplications: number
  totalDecisions: number
  totalGranted: number
  totalHousingUnits: number
  grantedPercentage: number
  applicationsYoY: number
  decisionsYoY: number
  housingUnitsYoY: number
}>> {
  return this.request('/v1/stats/overview')
}
```

### 2. Component Updated
**File:** `/frontend/src/components/sections/PlanningStatsBar.tsx`

- Fetches data on component mount
- Formats numbers (e.g., 336000 → "+336K")
- Formats YoY percentages with arrows (↑/↓)
- Shows loading state with pulse animation
- Gracefully falls back to default values on error

---

## Backend Implementation Required

### Endpoint to Create
**Route:** `GET /api/v1/stats/overview`
**Method:** `GET`
**No parameters required**

### Response Format
```json
{
  "success": true,
  "message": "Statistics retrieved successfully",
  "data": {
    "totalApplications": 336000,
    "totalDecisions": 321400,
    "totalGranted": 69200,
    "totalHousingUnits": 239000,
    "grantedPercentage": 87.0,
    "applicationsYoY": -9.0,
    "decisionsYoY": -9.0,
    "housingUnitsYoY": -6.0
  }
}
```

---

## Elasticsearch Aggregation Queries

### 1. Total Applications
Count all documents in the index.

```python
# Simple count
total_applications = es.count(index="planning_applications_*")['count']
```

### 2. Total Decisions
Count documents where `status` is not "Pending" or has a `decision_date`.

```python
total_decisions = es.count(
    index="planning_applications_*",
    body={
        "query": {
            "bool": {
                "should": [
                    {"exists": {"field": "decided_date"}},
                    {"exists": {"field": "decision_date"}},
                    {"bool": {
                        "must_not": {
                            "term": {"status.keyword": "Pending"}
                        }
                    }}
                ]
            }
        }
    }
)['count']
```

### 3. Total Granted
Count documents where `decision` = "Granted" or `status` = "Approved".

```python
total_granted = es.count(
    index="planning_applications_*",
    body={
        "query": {
            "bool": {
                "should": [
                    {"term": {"decision.keyword": "Granted"}},
                    {"term": {"status.keyword": "Approved"}},
                    {"term": {"decision.keyword": "Approved"}}
                ]
            }
        }
    }
)['count']
```

### 4. Total Housing Units
Sum the `housing_units` field (you may need to extract this from `description` or add it as a field).

```python
# If you have a housing_units field:
housing_agg = es.search(
    index="planning_applications_*",
    size=0,
    body={
        "aggs": {
            "total_units": {
                "sum": {"field": "housing_units"}
            }
        }
    }
)
total_housing_units = int(housing_agg['aggregations']['total_units']['value'])

# If not, you'll need to estimate or extract from descriptions
# For now, can use a fixed value or calculate from app_type
```

### 5. Granted Percentage
```python
granted_percentage = (total_granted / total_decisions * 100) if total_decisions > 0 else 0
```

### 6. YoY Calculations
Compare current year (Sept 2024) to previous year (Sept 2023).

```python
# Applications YoY
current_year_apps = es.count(
    index="planning_applications_*",
    body={
        "query": {
            "range": {
                "submission_date": {
                    "gte": "2023-10-01",
                    "lte": "2024-09-30"
                }
            }
        }
    }
)['count']

previous_year_apps = es.count(
    index="planning_applications_*",
    body={
        "query": {
            "range": {
                "submission_date": {
                    "gte": "2022-10-01",
                    "lte": "2023-09-30"
                }
            }
        }
    }
)['count']

applications_yoy = ((current_year_apps - previous_year_apps) / previous_year_apps * 100) if previous_year_apps > 0 else 0
```

Repeat similar logic for `decisions_yoy` and `housing_units_yoy`.

---

## FastAPI Implementation Example

```python
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime, timedelta
from app.core.elasticsearch import get_es_client

router = APIRouter(prefix="/v1/stats", tags=["stats"])

@router.get("/overview")
async def get_stats_overview():
    """
    Get platform-wide planning statistics

    Returns:
        - Total applications, decisions, granted permissions
        - Housing units
        - Grant percentage
        - Year-over-year changes
    """
    try:
        es = get_es_client()
        index = "planning_applications_*"

        # 1. Total Applications
        total_applications = es.count(index=index)['count']

        # 2. Total Decisions (has decided_date or not pending)
        total_decisions = es.count(
            index=index,
            body={
                "query": {
                    "bool": {
                        "should": [
                            {"exists": {"field": "decided_date"}},
                            {"exists": {"field": "decision_date"}}
                        ]
                    }
                }
            }
        )['count']

        # 3. Total Granted
        total_granted = es.count(
            index=index,
            body={
                "query": {
                    "bool": {
                        "should": [
                            {"term": {"decision.keyword": "Granted"}},
                            {"term": {"status.keyword": "Approved"}},
                            {"term": {"decision.keyword": "Approved"}}
                        ]
                    }
                }
            }
        )['count']

        # 4. Granted Percentage
        granted_percentage = (total_granted / total_decisions * 100) if total_decisions > 0 else 0

        # 5. YoY Calculations
        # Current year (Oct 2023 - Sept 2024)
        current_year_start = "2023-10-01"
        current_year_end = "2024-09-30"

        # Previous year (Oct 2022 - Sept 2023)
        previous_year_start = "2022-10-01"
        previous_year_end = "2023-09-30"

        # Applications YoY
        current_apps = es.count(
            index=index,
            body={
                "query": {
                    "range": {
                        "submission_date": {
                            "gte": current_year_start,
                            "lte": current_year_end
                        }
                    }
                }
            }
        )['count']

        previous_apps = es.count(
            index=index,
            body={
                "query": {
                    "range": {
                        "submission_date": {
                            "gte": previous_year_start,
                            "lte": previous_year_end
                        }
                    }
                }
            }
        )['count']

        applications_yoy = ((current_apps - previous_apps) / previous_apps * 100) if previous_apps > 0 else 0

        # Decisions YoY
        current_decisions = es.count(
            index=index,
            body={
                "query": {
                    "range": {
                        "decided_date": {
                            "gte": current_year_start,
                            "lte": current_year_end
                        }
                    }
                }
            }
        )['count']

        previous_decisions = es.count(
            index=index,
            body={
                "query": {
                    "range": {
                        "decided_date": {
                            "gte": previous_year_start,
                            "lte": previous_year_end
                        }
                    }
                }
            }
        )['count']

        decisions_yoy = ((current_decisions - previous_decisions) / previous_decisions * 100) if previous_decisions > 0 else 0

        # Housing units (placeholder - needs proper implementation)
        total_housing_units = 239000  # TODO: Calculate from data
        housing_units_yoy = -6.0  # TODO: Calculate YoY

        return {
            "success": True,
            "message": "Statistics retrieved successfully",
            "data": {
                "totalApplications": total_applications,
                "totalDecisions": total_decisions,
                "totalGranted": total_granted,
                "totalHousingUnits": total_housing_units,
                "grantedPercentage": round(granted_percentage, 1),
                "applicationsYoY": round(applications_yoy, 1),
                "decisionsYoY": round(decisions_yoy, 1),
                "housingUnitsYoY": round(housing_units_yoy, 1)
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch statistics: {str(e)}"
        )
```

---

## Field Mapping Notes

Ensure your ES documents have these fields:
- `submission_date` or `start_date` - When application was submitted
- `decided_date` or `decision_date` - When decision was made
- `status` - Current status (Pending, Approved, Rejected, etc.)
- `decision` - Decision outcome (Granted, Refused, etc.)
- `housing_units` (optional) - Number of housing units

If field names are different in your index, adjust the queries accordingly.

---

## Testing

### 1. Test the Endpoint
```bash
curl http://localhost:8000/api/v1/stats/overview
```

### 2. Expected Response
```json
{
  "success": true,
  "message": "Statistics retrieved successfully",
  "data": {
    "totalApplications": 336000,
    "totalDecisions": 321400,
    "totalGranted": 69200,
    "totalHousingUnits": 239000,
    "grantedPercentage": 87.0,
    "applicationsYoY": -9.0,
    "decisionsYoY": -9.0,
    "housingUnitsYoY": -6.0
  }
}
```

### 3. Frontend Testing
Once the endpoint is live:
1. Refresh the homepage
2. Stats should load automatically
3. Check browser console for API call
4. Values should match screenshot numbers

---

## Performance Optimization

### Caching
Since stats don't change frequently, cache the response:

```python
from functools import lru_cache
from datetime import datetime, timedelta

# Cache for 1 hour
_cache = {"data": None, "timestamp": None}
CACHE_TTL = 3600  # 1 hour in seconds

@router.get("/overview")
async def get_stats_overview():
    # Check cache
    if _cache["data"] and _cache["timestamp"]:
        if (datetime.now() - _cache["timestamp"]).total_seconds() < CACHE_TTL:
            return _cache["data"]

    # Fetch fresh data...
    result = {
        "success": True,
        "message": "Statistics retrieved successfully",
        "data": {...}
    }

    # Update cache
    _cache["data"] = result
    _cache["timestamp"] = datetime.now()

    return result
```

### Use ES Aggregations
Instead of multiple `count` queries, combine into one aggregation request for better performance.

---

## Next Steps

1. ✅ Frontend implementation complete
2. ⏳ **Create the FastAPI endpoint** (use code above)
3. ⏳ **Add ES field for housing units** if not present
4. ⏳ **Test endpoint** with curl/Postman
5. ⏳ **Verify frontend displays real data**
6. ⏳ **Add caching** for performance
7. ⏳ **Monitor ES query performance**

---

## Questions?

- **Date field missing?** Check your ES mapping for `submission_date`, `decided_date`
- **Housing units calculation?** Extract from `description` field using regex or add as indexed field
- **Different field names?** Update the ES queries to match your schema
- **Performance issues?** Add caching and use ES aggregations

---

**Status:** Frontend ready ✅ | Backend TODO ⏳
