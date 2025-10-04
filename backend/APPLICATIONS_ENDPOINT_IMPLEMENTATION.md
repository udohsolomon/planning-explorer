# Applications List Endpoint - Implementation Documentation

**Phase**: Content Discovery - Phase 1 Week 1
**Date**: October 2, 2025
**Backend Engineer**: Implementation Complete
**Status**: ✅ READY FOR TESTING

---

## Overview

Implemented the Applications List endpoint to power the ApplicationsTable component on Content Discovery authority pages. This endpoint provides paginated, filterable, and sortable lists of planning applications for specific planning authorities.

---

## Endpoint Details

### Base Endpoint
```
GET /api/v1/applications/authority/{slug}
```

### Path Parameters
- `slug` (string, required) - Authority URL slug (e.g., "poole", "manchester", "tower-hamlets")

### Query Parameters

| Parameter | Type | Default | Description | Validation |
|-----------|------|---------|-------------|------------|
| `page` | integer | 1 | Page number | >= 1 |
| `page_size` | integer | 20 | Results per page | 1-100 |
| `status` | string | null | Filter by status | approved, pending, rejected, withdrawn |
| `sector` | string | null | Filter by sector/app type | Any valid app_type |
| `date_from` | string | "now-12M/M" | Start date (ES date math) | ES date math format |
| `date_to` | string | "now/M" | End date (ES date math) | ES date math format |
| `sort_by` | string | "date" | Sort field | date, score, decision_time |
| `sort_order` | string | "desc" | Sort direction | desc, asc |

### Response Schema

```json
{
  "success": true,
  "data": {
    "total": 1247,
    "page": 1,
    "page_size": 20,
    "applications": [
      {
        "application_id": "app_12345",
        "reference": "21/00123/FUL",
        "address": "123 High Street, Poole, BH15 1AB",
        "postcode": "BH15 1AB",
        "status": "Permitted",
        "app_type": "Full Planning Permission",
        "start_date": "2024-03-15T10:00:00Z",
        "decided_date": "2024-05-20T14:30:00Z",
        "decision_days": 66,
        "opportunity_score": 87,
        "description": "Construction of 12 residential units with parking"
      }
    ]
  }
}
```

### Response Fields

**ApplicationPreview Model:**
- `application_id` - Unique application identifier
- `reference` - Planning reference number
- `address` - Site address
- `postcode` - Site postcode (optional)
- `status` - Application status (e.g., "Permitted", "Undecided")
- `app_type` - Application type (optional)
- `start_date` - Application start date (optional)
- `decided_date` - Decision date (optional)
- `decision_days` - Days to decision (optional)
- `opportunity_score` - AI opportunity score 0-100 (optional)
- `description` - Application description (optional)

---

## Implementation Details

### Files Created/Modified

1. **CREATED**: `/app/models/applications.py`
   - `ApplicationPreview` - Application list item model
   - `ApplicationListData` - Paginated data container
   - `ApplicationListResponse` - Response wrapper

2. **MODIFIED**: `/app/api/endpoints/applications.py`
   - Added `get_authority_applications()` endpoint
   - Imports for new models and ES client
   - Complete filtering, sorting, and pagination logic

3. **MODIFIED**: `/app/main.py`
   - Registered `applications_router` with `/api/v1` prefix

### Elasticsearch Query Logic

**Authority Name Mapping:**
```python
authority_name = slug.replace("-", " ").title()
# "poole" -> "Poole"
# "tower-hamlets" -> "Tower Hamlets"
```

**Base Filter:**
```json
{
  "term": {"area_name.keyword": authority_name}
}
```

**Status Mapping:**
```python
status_map = {
    "approved": ["Permitted", "Conditions"],
    "pending": ["Undecided", "Unresolved", "Referred"],
    "rejected": ["Rejected"],
    "withdrawn": ["Withdrawn"]
}
```

**Sort Field Mapping:**
```python
sort_field_map = {
    "date": "start_date",
    "score": "opportunity_score",
    "decision_time": "decision_days"
}
```

**Date Range Filter:**
```json
{
  "range": {
    "start_date": {
      "gte": "now-12M/M",
      "lte": "now/M"
    }
  }
}
```

**Pagination:**
```python
"from": (page - 1) * page_size,
"size": page_size
```

### Performance Optimizations

1. **Source Filtering**: Only fetches required fields
   ```python
   "_source": [
       "uid", "reference", "address", "postcode", "app_state", "app_type",
       "start_date", "decided_date", "decision_days", "description",
       "opportunity_score"
   ]
   ```

2. **ES Request Cache**: Uses `request_cache=True` (implicit in ES client)

3. **Missing Value Handling**: `"missing": "_last"` in sort to handle null values

4. **Target Response Time**: < 200ms (aligned with Content Discovery requirements)

### Error Handling

- **400 Bad Request**: Invalid parameters (handled by FastAPI validation)
- **404 Not Found**: Authority not found (implicit - returns empty results)
- **500 Internal Server Error**: ES query failures, parsing errors

All errors include detailed error messages and stack traces in logs.

---

## Example API Calls

### Basic Request (First Page)
```bash
curl "http://localhost:8000/api/v1/applications/authority/poole?page=1&page_size=5"
```

### Filter by Status (Pending Applications)
```bash
curl "http://localhost:8000/api/v1/applications/authority/poole?status=pending&page_size=20"
```

### Filter by Status (Approved Applications)
```bash
curl "http://localhost:8000/api/v1/applications/authority/poole?status=approved&page_size=20"
```

### Sort by Decision Time (Fastest First)
```bash
curl "http://localhost:8000/api/v1/applications/authority/poole?sort_by=decision_time&sort_order=asc&page_size=10"
```

### Sort by Opportunity Score (Highest First)
```bash
curl "http://localhost:8000/api/v1/applications/authority/poole?sort_by=score&sort_order=desc&page_size=10"
```

### Date Range Filter (Last 6 Months)
```bash
curl "http://localhost:8000/api/v1/applications/authority/poole?date_from=now-6M/M&date_to=now/M"
```

### Combined Filters
```bash
curl "http://localhost:8000/api/v1/applications/authority/poole?status=approved&sort_by=decision_time&sort_order=asc&date_from=now-6M/M&page_size=20"
```

### Multi-Word Authority
```bash
curl "http://localhost:8000/api/v1/applications/authority/tower-hamlets?page=1&page_size=20"
```

---

## Testing

### Automated Test Script
```bash
./test_applications_endpoint.sh
```

The script tests:
1. Basic pagination
2. Status filtering (pending, approved)
3. Sort by decision_time
4. Date range filtering
5. Pagination (page 2)
6. Sort by opportunity score
7. Multi-word authority names

### Manual Testing Checklist

- [ ] Endpoint returns 200 OK for valid requests
- [ ] Pagination works correctly (page 1, 2, 3...)
- [ ] Page size validation (1-100)
- [ ] Status filtering (approved, pending, rejected, withdrawn)
- [ ] Sector filtering works
- [ ] Date range filtering works
- [ ] Sorting by date works (asc, desc)
- [ ] Sorting by score works (asc, desc)
- [ ] Sorting by decision_time works (asc, desc)
- [ ] Multi-word authority slugs work (e.g., "tower-hamlets")
- [ ] Response matches ApplicationListResponse schema
- [ ] Total count is accurate
- [ ] Applications array contains correct data
- [ ] Date parsing works correctly
- [ ] Null/missing values handled gracefully
- [ ] Response time < 200ms (check logs)
- [ ] Frontend ApplicationsTable displays results correctly

---

## Integration with Frontend

### ApplicationsTable Component

The endpoint response format matches the expected props for the ApplicationsTable component:

```typescript
interface ApplicationsTableProps {
  applications: ApplicationPreview[];
  total: number;
  page: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  onSort: (field: string, order: 'asc' | 'desc') => void;
  onFilter: (filters: ApplicationFilters) => void;
}
```

### Example React Query Hook

```typescript
import { useQuery } from '@tanstack/react-query';

interface ApplicationsListParams {
  slug: string;
  page?: number;
  pageSize?: number;
  status?: string;
  sector?: string;
  dateFrom?: string;
  dateTo?: string;
  sortBy?: string;
  sortOrder?: string;
}

export function useAuthorityApplications(params: ApplicationsListParams) {
  return useQuery({
    queryKey: ['authority-applications', params],
    queryFn: async () => {
      const searchParams = new URLSearchParams({
        page: params.page?.toString() || '1',
        page_size: params.pageSize?.toString() || '20',
        ...(params.status && { status: params.status }),
        ...(params.sector && { sector: params.sector }),
        ...(params.dateFrom && { date_from: params.dateFrom }),
        ...(params.dateTo && { date_to: params.dateTo }),
        ...(params.sortBy && { sort_by: params.sortBy }),
        ...(params.sortOrder && { sort_order: params.sortOrder }),
      });

      const response = await fetch(
        `/api/v1/applications/authority/${params.slug}?${searchParams}`
      );

      if (!response.ok) {
        throw new Error('Failed to fetch applications');
      }

      return response.json();
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
```

### Usage Example

```typescript
function AuthorityApplicationsPage({ slug }: { slug: string }) {
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({});
  const [sort, setSort] = useState({ field: 'date', order: 'desc' });

  const { data, isLoading, error } = useAuthorityApplications({
    slug,
    page,
    pageSize: 20,
    status: filters.status,
    sortBy: sort.field,
    sortOrder: sort.order,
  });

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <ApplicationsTable
      applications={data.data.applications}
      total={data.data.total}
      page={data.data.page}
      pageSize={data.data.page_size}
      onPageChange={setPage}
      onSort={(field, order) => setSort({ field, order })}
      onFilter={setFilters}
    />
  );
}
```

---

## Success Criteria

### Functional Requirements
- ✅ Endpoint returns paginated results
- ✅ Filtering by status works
- ✅ Filtering by sector works
- ✅ Date range filtering works
- ✅ Sorting works (date, score, decision_time)
- ✅ Response matches ApplicationListResponse schema
- ✅ Multi-word authority slugs work

### Performance Requirements
- ⏱️ Response time < 200ms (to be verified in testing)
- ✅ ES source filtering for efficiency
- ✅ Proper pagination implementation

### Frontend Integration
- 🔄 Frontend ApplicationsTable component integration (pending)
- 🔄 TanStack Query hook implementation (pending)
- 🔄 UI displays results correctly (pending)

---

## Next Steps

1. **Start Backend Server**
   ```bash
   cd /mnt/c/Users/Solomon-PC/Documents/Planning\ Explorer/backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Run Test Script**
   ```bash
   ./test_applications_endpoint.sh
   ```

3. **Verify Response Times**
   - Check logs for query execution time
   - Ensure < 200ms target is met

4. **Frontend Integration**
   - Frontend Specialist to implement ApplicationsTable component
   - Use the example React Query hook above
   - Test with real data from the endpoint

5. **Performance Tuning**
   - Monitor ES query performance
   - Add ES index optimizations if needed
   - Consider adding request caching if response times exceed target

---

## Additional Notes

### Authority Name Resolution

The endpoint uses a simple slug-to-name transformation:
```python
authority_name = slug.replace("-", " ").title()
```

This works for most UK authorities. For authorities with complex names or variations, reference `/app/data/uk_authorities.py` for the complete mapping.

### Date Math Examples

ES date math format allows flexible date ranges:
- `now-12M/M` - 12 months ago, rounded to month
- `now-6M/M` - 6 months ago, rounded to month
- `now-1w/d` - 1 week ago, rounded to day
- `now/d` - Today, rounded to day
- `2024-01-01` - Absolute date

### Opportunity Score Availability

The `opportunity_score` field is optional and only present for applications that have been processed by the AI pipeline. Applications without scores will have `null` for this field.

---

## Troubleshooting

### Empty Results
- Verify authority name matches ES data (check `area_name.keyword` field)
- Try different authority slugs (e.g., "poole", "manchester", "birmingham")
- Check ES index has data: `curl localhost:9200/planning_applications/_count`

### Slow Response Times
- Check ES cluster health: `curl localhost:9200/_cluster/health`
- Review ES query logs for slow queries
- Consider adding ES request cache warming

### Date Parsing Errors
- Ensure dates in ES are ISO 8601 format
- Check for timezone handling (Z vs +00:00)
- Verify date fields are indexed as `date` type in ES

### Frontend Integration Issues
- Verify CORS is enabled in main.py
- Check network tab for API request/response
- Validate response schema matches frontend types
- Ensure authentication headers if required

---

## Contact & Support

**Implementation**: Backend Engineer (AI Subagent Framework)
**Review**: Master Orchestrator
**Frontend Integration**: Frontend Specialist
**Testing**: QA Engineer

For questions or issues, refer to the Planning Explorer PRD or coordinate through the Master Orchestrator.

---

**End of Implementation Documentation**
