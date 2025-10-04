# Location Statistics Endpoint - Quick Start Guide

## Quick Reference

### Endpoint URL
```
GET /api/v1/stats/locations/{location_slug}
```

### Example Requests

**Get London stats (default 5km radius):**
```bash
curl http://localhost:8000/api/v1/stats/locations/london
```

**Get Manchester stats with 15km radius:**
```bash
curl "http://localhost:8000/api/v1/stats/locations/manchester?radius_km=15"
```

**Get Bristol stats with force refresh:**
```bash
curl "http://localhost:8000/api/v1/stats/locations/bristol?force_refresh=true"
```

**List all available locations:**
```bash
curl http://localhost:8000/api/v1/stats/locations/
```

**Health check:**
```bash
curl http://localhost:8000/api/v1/stats/locations/health
```

## Available Locations (20 cities)

- london, manchester, birmingham, liverpool, bristol
- bournemouth, poole, leeds, sheffield, edinburgh
- glasgow, cardiff, newcastle, nottingham, southampton
- brighton, oxford, cambridge, bath, york

## Query Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| radius_km | integer | 5 | 1-50 | Search radius in kilometers |
| force_refresh | boolean | false | - | Skip cache and fetch fresh data |
| date_from | string | now-12M/M | ES date math | Start date for filtering |
| date_to | string | now/M | ES date math | End date for filtering |

## Response Fields

```json
{
  "location_name": "London",              // Human-readable name
  "location_slug": "london",              // URL identifier
  "center_coords": {"lat": X, "lng": Y},  // Center point
  "radius_km": 10,                        // Search radius
  "total_applications": 2456,             // Last 12 months
  "total_applications_all_time": 15789,   // All time
  "active_applications": 342,             // Pending decisions
  "approval_rate": 68.5,                  // Percentage
  "avg_decision_days": 87,                // Average days
  "top_sector": {...},                    // Most common type
  "top_authority": {...},                 // Most common authority
  "monthly_trend": [...],                 // 12 months data
  "status_breakdown": {...},              // By status
  "recent_applications": [...]            // Last 10 UIDs
}
```

## Performance

- **Cached response:** < 5ms
- **Uncached response:** < 200ms
- **Cache TTL:** 1 hour
- **Cache size:** 500 entries

## Testing

**Run test suite:**
```bash
./backend/test_locations_endpoint.sh
```

**Quick test:**
```bash
# Test London stats
curl http://localhost:8000/api/v1/stats/locations/london | jq

# Test with different radius
curl "http://localhost:8000/api/v1/stats/locations/manchester?radius_km=20" | jq

# Test cache performance
time curl -s http://localhost:8000/api/v1/stats/locations/london > /dev/null
time curl -s http://localhost:8000/api/v1/stats/locations/london > /dev/null
```

## Common Use Cases

**1. Compare multiple cities:**
```bash
for city in london manchester birmingham; do
  echo "=== $city ==="
  curl "http://localhost:8000/api/v1/stats/locations/$city?radius_km=10" | jq '.data | {location_name, total_applications, approval_rate}'
done
```

**2. Get detailed monthly trends:**
```bash
curl "http://localhost:8000/api/v1/stats/locations/london?radius_km=5" | jq '.data.monthly_trend'
```

**3. Check recent activity:**
```bash
curl "http://localhost:8000/api/v1/stats/locations/bristol?radius_km=8" | jq '.data.recent_applications'
```

**4. Analyze approval rates:**
```bash
curl "http://localhost:8000/api/v1/stats/locations/manchester?radius_km=10" | jq '.data | {location_name, approval_rate, avg_decision_days}'
```

## Error Codes

- **200** - Success
- **404** - Location not found
- **422** - Validation error (invalid radius)
- **500** - Internal server error
- **503** - Elasticsearch unavailable

## Files

- **Model:** `/backend/app/models/locations.py`
- **Endpoint:** `/backend/app/api/endpoints/locations.py`
- **Router Registration:** `/backend/app/main.py` (lines 80-82)
- **Tests:** `/backend/test_locations_endpoint.sh`
- **Documentation:** `/backend/LOCATIONS_ENDPOINT_IMPLEMENTATION.md`
- **Sample Response:** `/backend/sample_location_response.json`

## Integration Example (Python)

```python
import requests

# Get London stats
response = requests.get(
    "http://localhost:8000/api/v1/stats/locations/london",
    params={"radius_km": 10}
)
data = response.json()

print(f"Location: {data['data']['location_name']}")
print(f"Total Applications: {data['data']['total_applications']}")
print(f"Approval Rate: {data['data']['approval_rate']}%")
print(f"Avg Decision Days: {data['data']['avg_decision_days']}")
```

## Integration Example (JavaScript)

```javascript
// Fetch London stats
const response = await fetch(
  'http://localhost:8000/api/v1/stats/locations/london?radius_km=10'
);
const { data } = await response.json();

console.log(`Location: ${data.location_name}`);
console.log(`Total Applications: ${data.total_applications}`);
console.log(`Approval Rate: ${data.approval_rate}%`);
console.log(`Avg Decision Days: ${data.avg_decision_days}`);
```

## Next Steps

1. **Start the API:**
   ```bash
   cd /mnt/c/Users/Solomon-PC/Documents/Planning\ Explorer/backend
   uvicorn app.main:app --reload
   ```

2. **Run tests:**
   ```bash
   ./test_locations_endpoint.sh
   ```

3. **Check health:**
   ```bash
   curl http://localhost:8000/api/v1/stats/locations/health
   ```

4. **Test with your location:**
   ```bash
   curl http://localhost:8000/api/v1/stats/locations/YOUR_CITY
   ```

## Support

For detailed implementation details, see:
- Full documentation: `LOCATIONS_ENDPOINT_IMPLEMENTATION.md`
- Sample response: `sample_location_response.json`
- Test script: `test_locations_endpoint.sh`

---

**Quick Reference Version 1.0**
**Last Updated:** October 2, 2025
