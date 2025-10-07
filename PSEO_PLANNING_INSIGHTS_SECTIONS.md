# pSEO Planning Insights - Visual Data Sections

## Overview
Based on the planning report screenshot, integrate comprehensive data visualizations, charts, tables, and maps into each authority pSEO page.

---

## Additional pSEO Page Sections (Data Visualizations)

### **Section 1: Planning Recommendations**
**Location:** After introduction, before data dashboard

```typescript
interface PlanningRecommendationsSection {
  h2: string; // "Planning Recommendations for {Authority}"
  recommendations: Recommendation[];
}

interface Recommendation {
  icon: 'document' | 'consultant' | 'analysis';
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
}
```

**Content Examples:**
- Review all planning documents and consultation responses
- Engage planning consultant for detailed assessment
- Conduct site visit and local area analysis
- Assess policy compliance and mitigation requirements
- Review similar application outcomes in the area

**Data Source:** Generated from approval patterns and policy analysis

---

### **Section 2: Planning Application Volume Trends**
**Location:** Main data dashboard section

```typescript
interface VolumeTrendsChart {
  type: 'bar-chart';
  title: string; // "Planning Application Volume Trends (Last 12 Months)"
  data: MonthlyVolume[];
  comparison: {
    approved: number;
    peak_month: string;
    average_monthly: number;
  };
}

interface MonthlyVolume {
  month: string; // "Jan", "Feb", etc.
  total_applications: number;
  approved: number;
  refused: number;
  peak: boolean; // Highlight peak month in red/orange
}
```

**Visual:**
- **Bar chart** (green bars for approved, red/orange for peak months)
- X-axis: Months (Jan, Feb, Mar, etc.)
- Y-axis: Number of applications (0-100 scale)
- Legend: Approved vs Peak Month
- Hover tooltips: Exact numbers + approval rate

**Data Source:** Elasticsearch monthly aggregations

**Implementation:**
```python
# backend/app/services/pseo/data_pipeline.py

async def extract_volume_trends_chart_data(self) -> Dict:
    """Extract data for volume trends bar chart"""

    query = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"local_authority_id": self.authority_id}},
                    {"range": {"date_received": {"gte": "now-12M/M"}}}
                ]
            }
        },
        "aggs": {
            "monthly_volumes": {
                "date_histogram": {
                    "field": "date_received",
                    "calendar_interval": "month",
                    "format": "MMM"
                },
                "aggs": {
                    "approved": {"filter": {"term": {"decision": "approved"}}},
                    "refused": {"filter": {"term": {"decision": "refused"}}}
                }
            }
        },
        "size": 0
    }

    result = await self.es.search(index="planning_applications", body=query)

    buckets = result['aggregations']['monthly_volumes']['buckets']

    # Find peak month
    peak_volume = max(b['doc_count'] for b in buckets)

    chart_data = {
        'type': 'bar-chart',
        'title': f"Planning Application Volume Trends (Last 12 Months)",
        'data': [
            {
                'month': bucket['key_as_string'],
                'total_applications': bucket['doc_count'],
                'approved': bucket['approved']['doc_count'],
                'refused': bucket['refused']['doc_count'],
                'peak': bucket['doc_count'] == peak_volume
            }
            for bucket in buckets
        ],
        'comparison': {
            'approved': sum(b['approved']['doc_count'] for b in buckets),
            'peak_month': next(b['key_as_string'] for b in buckets if b['doc_count'] == peak_volume),
            'average_monthly': sum(b['doc_count'] for b in buckets) / len(buckets)
        }
    }

    return chart_data
```

---

### **Section 3: Average Decision Timeline by Application Type**
**Location:** Data dashboard section

```typescript
interface DecisionTimelineChart {
  type: 'horizontal-bar-chart';
  title: string; // "Average Decision Timeline by Application Type"
  data: ApplicationTypeTimeline[];
  note: string; // "Average processing times based on historical data. Actual timelines may vary by authority."
}

interface ApplicationTypeTimeline {
  application_type: string; // "Householder", "Full Planning", etc.
  avg_decision_days: number;
  median_decision_days: number;
  color: string; // Different shades of teal/green
}
```

**Visual:**
- **Horizontal bar chart** (like screenshot)
- Y-axis: Application types (Householder, Full Planning, Reserved Matters, Prior Approval)
- X-axis: Average days (0-100 scale)
- Bar labels: Show exact number of days at the end
- Color scheme: Darker green for longer timelines

**Data Source:** Elasticsearch aggregation by application type

**Implementation:**
```python
async def extract_decision_timeline_chart_data(self) -> Dict:
    """Extract data for decision timeline horizontal bar chart"""

    query = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"local_authority_id": self.authority_id}},
                    {"range": {"decision_date": {"gte": "now-12M"}}},
                    {"exists": {"field": "decision_days"}}
                ]
            }
        },
        "aggs": {
            "by_application_type": {
                "terms": {"field": "application_type.keyword", "size": 20},
                "aggs": {
                    "avg_days": {"avg": {"field": "decision_days"}},
                    "median_days": {
                        "percentiles": {"field": "decision_days", "percents": [50]}
                    }
                }
            }
        },
        "size": 0
    }

    result = await self.es.search(index="planning_applications", body=query)

    buckets = result['aggregations']['by_application_type']['buckets']

    # Define colors (darker for longer timelines)
    colors = {
        'Householder': '#10b981',           # Lighter green
        'Full Planning': '#059669',         # Medium green
        'Reserved Matters': '#047857',      # Darker green
        'Prior Approval': '#065f46',        # Darkest green
        'default': '#0d9488'                # Teal
    }

    chart_data = {
        'type': 'horizontal-bar-chart',
        'title': 'Average Decision Timeline by Application Type',
        'data': [
            {
                'application_type': bucket['key'],
                'avg_decision_days': round(bucket['avg_days']['value'], 0),
                'median_decision_days': round(bucket['median_days']['values']['50.0'], 0),
                'color': colors.get(bucket['key'], colors['default'])
            }
            for bucket in buckets[:10]  # Top 10 types
        ],
        'note': 'Average processing times based on historical data. Actual timelines may vary by authority.'
    }

    return chart_data
```

---

### **Section 4: Comparable Applications Analysis**
**Location:** After comparative section

```typescript
interface ComparableApplicationsSection {
  h2: string; // "Comparable Applications Analysis"
  description: string; // "Similar applications in {Authority}"
  applications: ComparableApplication[];
}

interface ComparableApplication {
  reference: string;
  description: string;
  value: string; // e.g., "£324M"
  status: 'Approved' | 'Refused' | 'Pending' | 'Withdrawn';
  decision_date: string;
  similarity_score: number; // 0-100
}
```

**Visual:**
- **Data table** with columns:
  - Reference (clickable link)
  - Description (with location if available)
  - Value (£)
  - Status (colored badge: green=approved, red=refused, yellow=pending)
  - Decision Date

**Status Colors:**
```typescript
const statusColors = {
  'Approved': 'bg-green-100 text-green-800',
  'Refused': 'bg-red-100 text-red-800',
  'Pending': 'bg-yellow-100 text-yellow-800',
  'Withdrawn': 'bg-gray-100 text-gray-800'
}
```

**Data Source:** Elasticsearch query for similar applications

**Implementation:**
```python
async def extract_comparable_applications(self, reference_app: Dict = None) -> List[Dict]:
    """Find similar applications for comparison table"""

    # If no reference app provided, use recent major applications
    if not reference_app:
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"local_authority_id": self.authority_id}},
                        {"range": {"decision_date": {"gte": "now-24M"}}}
                    ],
                    "should": [
                        {"term": {"application_type.keyword": "major"}},
                        {"range": {"num_dwellings": {"gte": 10}}},
                        {"range": {"floorspace_sqm": {"gte": 1000}}}
                    ],
                    "minimum_should_match": 1
                }
            },
            "sort": [{"decision_date": {"order": "desc"}}],
            "size": 10
        }
    else:
        # Vector similarity search for truly comparable apps
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"local_authority_id": self.authority_id}},
                        {"range": {"decision_date": {"gte": "now-24M"}}}
                    ],
                    "should": [
                        {"match": {"development_description": reference_app.get('description', '')}},
                        {"term": {"application_type.keyword": reference_app.get('type', '')}}
                    ]
                }
            },
            "size": 10
        }

    result = await self.es.search(index="planning_applications", body=query)

    comparable_apps = []
    for hit in result['hits']['hits']:
        source = hit['_source']

        # Calculate value (if available)
        value = ''
        if source.get('estimated_value'):
            value = f"£{source['estimated_value']:,}"
        elif source.get('num_dwellings'):
            value = f"{source['num_dwellings']} dwellings"
        elif source.get('floorspace_sqm'):
            value = f"{source['floorspace_sqm']:,} sqm"

        comparable_apps.append({
            'reference': source.get('application_reference', ''),
            'description': source.get('development_description', '')[:80] + '...',
            'value': value,
            'status': source.get('decision', 'Pending').title(),
            'decision_date': source.get('decision_date', ''),
            'similarity_score': hit.get('_score', 0) * 10  # Normalize to 0-100
        })

    return comparable_apps
```

---

### **Section 5: Geographic Heat Map**
**Location:** Geographic insights section

```typescript
interface GeographicHeatMap {
  type: 'heat-map' | 'choropleth';
  title: string; // "{Authority} Planning Application Heat Map"
  data: WardHeatData[];
  legend: {
    min: number;
    max: number;
    colors: string[]; // Gradient from light to dark
  };
}

interface WardHeatData {
  ward_name: string;
  lat: number;
  lng: number;
  application_count: number;
  approval_rate: number;
  intensity: number; // 0-100 for heat intensity
}
```

**Visual:**
- **Interactive map** with color-coded wards
- Hover: Ward name, application count, approval rate
- Color gradient: Light blue (low activity) → Dark blue/red (high activity)
- Clustering for dense areas

**Data Source:** Elasticsearch geo aggregation

**Implementation:**
```python
async def extract_geographic_heat_map_data(self) -> Dict:
    """Extract data for geographic heat map"""

    query = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"local_authority_id": self.authority_id}},
                    {"range": {"date_received": {"gte": "now-12M"}}},
                    {"exists": {"field": "location"}}  # Has geo coordinates
                ]
            }
        },
        "aggs": {
            "by_ward": {
                "terms": {"field": "ward.keyword", "size": 100},
                "aggs": {
                    "approved": {"filter": {"term": {"decision": "approved"}}},
                    "centroid": {
                        "geo_centroid": {"field": "location"}
                    }
                }
            }
        },
        "size": 0
    }

    result = await self.es.search(index="planning_applications", body=query)

    buckets = result['aggregations']['by_ward']['buckets']

    # Find max application count for normalization
    max_count = max(b['doc_count'] for b in buckets) if buckets else 1

    heat_map_data = {
        'type': 'heat-map',
        'title': f"{self.authority['name']} Planning Application Heat Map",
        'data': [
            {
                'ward_name': bucket['key'],
                'lat': bucket['centroid']['location']['lat'],
                'lng': bucket['centroid']['location']['lon'],
                'application_count': bucket['doc_count'],
                'approval_rate': round((bucket['approved']['doc_count'] / bucket['doc_count'] * 100), 1),
                'intensity': int((bucket['doc_count'] / max_count) * 100)
            }
            for bucket in buckets
            if bucket.get('centroid', {}).get('location')
        ],
        'legend': {
            'min': 0,
            'max': max_count,
            'colors': ['#dbeafe', '#93c5fd', '#3b82f6', '#1e40af', '#1e3a8a']  # Blue gradient
        }
    }

    return heat_map_data
```

---

### **Section 6: Application Type Distribution (Pie/Donut Chart)**
**Location:** Application types section

```typescript
interface ApplicationDistributionChart {
  type: 'donut-chart' | 'pie-chart';
  title: string; // "Application Type Distribution"
  data: TypeDistribution[];
  total_applications: number;
}

interface TypeDistribution {
  type: string;
  count: number;
  percentage: number;
  color: string;
  approval_rate: number;
}
```

**Visual:**
- **Donut chart** with segments for each application type
- Center: Total application count
- Segments colored differently
- Hover: Type name, count, percentage, approval rate

**Implementation:**
```python
async def extract_application_distribution_chart(self) -> Dict:
    """Extract data for application type distribution donut chart"""

    query = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"local_authority_id": self.authority_id}},
                    {"range": {"date_received": {"gte": "now-12M"}}}
                ]
            }
        },
        "aggs": {
            "by_type": {
                "terms": {"field": "application_type.keyword", "size": 15},
                "aggs": {
                    "approved": {"filter": {"term": {"decision": "approved"}}}
                }
            }
        },
        "size": 0
    }

    result = await self.es.search(index="planning_applications", body=query)

    buckets = result['aggregations']['by_type']['buckets']
    total = sum(b['doc_count'] for b in buckets)

    # Define colors for different types
    type_colors = {
        'Householder': '#10b981',
        'Full Planning': '#3b82f6',
        'Outline': '#8b5cf6',
        'Reserved Matters': '#f59e0b',
        'Change of Use': '#ef4444',
        'Listed Building': '#ec4899',
        'Advertisement': '#6366f1',
        'Prior Approval': '#14b8a6',
        'default': '#6b7280'
    }

    chart_data = {
        'type': 'donut-chart',
        'title': 'Application Type Distribution',
        'total_applications': total,
        'data': [
            {
                'type': bucket['key'],
                'count': bucket['doc_count'],
                'percentage': round((bucket['doc_count'] / total * 100), 1),
                'color': type_colors.get(bucket['key'], type_colors['default']),
                'approval_rate': round((bucket['approved']['doc_count'] / bucket['doc_count'] * 100), 1)
            }
            for bucket in buckets
        ]
    }

    return chart_data
```

---

### **Section 7: Approval Rate Trends (Line Chart)**
**Location:** Data dashboard

```typescript
interface ApprovalRateTrends {
  type: 'line-chart';
  title: string; // "Approval Rate Trends Over Time"
  data: MonthlyApprovalRate[];
  benchmark: {
    regional_avg: number;
    national_avg: number;
  };
}

interface MonthlyApprovalRate {
  month: string;
  approval_rate: number;
  application_count: number;
}
```

**Visual:**
- **Line chart** showing approval rate over 24 months
- X-axis: Months
- Y-axis: Approval rate (%)
- Reference lines: Regional average, National average
- Hover: Month, exact rate, application count

---

### **Section 8: Top Developers/Agents Performance Matrix**
**Location:** Developer insights section

```typescript
interface PerformanceMatrix {
  type: 'scatter-plot' | 'bubble-chart';
  title: string; // "Agent Performance: Success Rate vs Volume"
  data: AgentPerformance[];
  quadrants: {
    high_volume_high_success: Agent[];
    high_volume_low_success: Agent[];
    low_volume_high_success: Agent[];
    low_volume_low_success: Agent[];
  };
}

interface AgentPerformance {
  name: string;
  application_count: number; // X-axis
  approval_rate: number;     // Y-axis
  avg_decision_days: number; // Bubble size
  specialty: string[];
}
```

**Visual:**
- **Scatter plot** with agents plotted by volume vs success rate
- Quadrants showing different performance categories
- Bubble size: Average decision time
- Color: Specialty (residential, commercial, etc.)

---

## Frontend Component Implementation

### **React Component Example (TrendChart Enhancement)**

```typescript
// frontend/src/components/pseo/VolumeTrendsChart.tsx

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface VolumeTrendsChartProps {
  data: MonthlyVolume[];
  comparison: {
    approved: number;
    peak_month: string;
    average_monthly: number;
  };
}

export const VolumeTrendsChart: React.FC<VolumeTrendsChartProps> = ({ data, comparison }) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm">
      <h3 className="text-xl font-semibold mb-4">
        Planning Application Volume Trends (Last 12 Months)
      </h3>

      <ResponsiveContainer width="100%" height={350}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis label={{ value: 'Number of Applications', angle: -90, position: 'insideLeft' }} />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload;
                return (
                  <div className="bg-white p-3 border rounded shadow-lg">
                    <p className="font-semibold">{data.month}</p>
                    <p className="text-sm">Total: {data.total_applications}</p>
                    <p className="text-sm text-green-600">Approved: {data.approved}</p>
                    <p className="text-sm text-red-600">Refused: {data.refused}</p>
                    <p className="text-sm">
                      Approval Rate: {((data.approved / data.total_applications) * 100).toFixed(1)}%
                    </p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Legend />
          <Bar
            dataKey="approved"
            fill={(entry) => entry.peak ? '#ef4444' : '#10b981'}
            name="Approved Applications"
          />
        </BarChart>
      </ResponsiveContainer>

      <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
        <div className="bg-green-50 p-3 rounded">
          <p className="text-gray-600">Total Approved</p>
          <p className="text-xl font-semibold text-green-700">{comparison.approved}</p>
        </div>
        <div className="bg-orange-50 p-3 rounded">
          <p className="text-gray-600">Peak Month</p>
          <p className="text-xl font-semibold text-orange-700">{comparison.peak_month}</p>
        </div>
        <div className="bg-blue-50 p-3 rounded">
          <p className="text-gray-600">Monthly Average</p>
          <p className="text-xl font-semibold text-blue-700">{comparison.average_monthly.toFixed(0)}</p>
        </div>
      </div>
    </div>
  );
};
```

### **Decision Timeline Component**

```typescript
// frontend/src/components/pseo/DecisionTimelineChart.tsx

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export const DecisionTimelineChart: React.FC<{ data: ApplicationTypeTimeline[] }> = ({ data }) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm">
      <h3 className="text-xl font-semibold mb-4">
        Average Decision Timeline by Application Type
      </h3>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} layout="horizontal" margin={{ left: 120 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" label={{ value: 'Average Days', position: 'bottom' }} />
          <YAxis type="category" dataKey="application_type" width={110} />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload;
                return (
                  <div className="bg-white p-3 border rounded shadow-lg">
                    <p className="font-semibold">{data.application_type}</p>
                    <p className="text-sm">Average: {data.avg_decision_days} days</p>
                    <p className="text-sm">Median: {data.median_decision_days} days</p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Bar
            dataKey="avg_decision_days"
            fill={(entry) => entry.color}
            label={{ position: 'right', formatter: (value) => `${value} days` }}
          />
        </BarChart>
      </ResponsiveContainer>

      <p className="text-sm text-gray-500 mt-4">
        Average processing times based on historical data. Actual timelines may vary by authority.
      </p>
    </div>
  );
};
```

### **Comparable Applications Table**

```typescript
// frontend/src/components/pseo/ComparableApplicationsTable.tsx

export const ComparableApplicationsTable: React.FC<{ applications: ComparableApplication[] }> = ({ applications }) => {
  const getStatusColor = (status: string) => {
    const colors = {
      'Approved': 'bg-green-100 text-green-800',
      'Refused': 'bg-red-100 text-red-800',
      'Pending': 'bg-yellow-100 text-yellow-800',
      'Withdrawn': 'bg-gray-100 text-gray-800'
    };
    return colors[status] || colors['Pending'];
  };

  return (
    <div className="bg-white rounded-lg shadow-sm overflow-hidden">
      <div className="p-6 border-b">
        <h3 className="text-xl font-semibold">Comparable Applications Analysis</h3>
        <p className="text-gray-600 text-sm mt-1">Similar applications in this authority</p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Reference
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Description
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Value
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Decision Date
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {applications.map((app, index) => (
              <tr key={index} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <a href={`/application/${app.reference}`} className="text-blue-600 hover:underline font-mono text-sm">
                    {app.reference}
                  </a>
                </td>
                <td className="px-6 py-4">
                  <p className="text-sm text-gray-900">{app.description}</p>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <p className="text-sm font-semibold text-gray-900">{app.value}</p>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(app.status)}`}>
                    {app.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(app.decision_date).toLocaleDateString('en-GB', {
                    day: '2-digit',
                    month: 'short',
                    year: 'numeric'
                  })}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
```

---

## Summary of New Visual Sections

1. ✅ **Planning Recommendations** (Icon list)
2. ✅ **Volume Trends Bar Chart** (Monthly applications)
3. ✅ **Decision Timeline Horizontal Bars** (By application type)
4. ✅ **Comparable Applications Table** (Similar cases)
5. ✅ **Geographic Heat Map** (Ward-level activity)
6. ✅ **Application Distribution Donut Chart** (Type breakdown)
7. ✅ **Approval Rate Line Chart** (24-month trends)
8. ✅ **Agent Performance Scatter Plot** (Success vs volume)

**Total:** 8 new data visualization sections per pSEO page, matching the professional planning report style shown in the screenshot.

These visualizations transform the pSEO pages from text-heavy content into interactive, data-rich planning intelligence hubs.
