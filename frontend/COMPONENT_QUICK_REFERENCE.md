# Content Discovery Components - Quick Reference

## 📦 Import Paths

```tsx
// Discovery Components
import { StatsCard, StatsCardGrid } from '@/components/discovery/StatsCard'
import { FreemiumGate, InlineFreemiumGate } from '@/components/discovery/FreemiumGate'
import { TrendChart, CHART_COLORS } from '@/components/discovery/TrendChart'
import { ApplicationsTable } from '@/components/discovery/ApplicationsTable'

// Map Components
import { PlanningMap } from '@/components/maps/PlanningMap'

// SEO Components
import { StructuredData } from '@/components/seo/StructuredData'
import {
  generateMetadata,
  generateAuthorityMetadata,
  generateLocationMetadata,
  Breadcrumbs
} from '@/components/seo/SEOHead'

// Utilities
import { getMarkerIcon, CARTO_BASEMAPS, UK_CENTER } from '@/lib/map-config'
import { calculateDistance, geocodePostcode } from '@/lib/geo-utils'
import {
  getAuthorityStats,
  getApplicationsList,
  getLocationStats
} from '@/lib/content-discovery-api'
```

---

## 🎨 Color Palette

```css
/* Planning Insights Colors */
--planning-primary: #2DCC9E      /* Teal - Main brand */
--planning-secondary: #1FAD85    /* Darker teal */
--planning-accent: #027554       /* Forest green */
--planning-button: #2DCC9E       /* Same as primary */

/* Status Colors */
Approved:  #2DCC9E (green)
Pending:   #FFCA28 (yellow)
Rejected:  #EF5350 (red)
Withdrawn: #9E9E9E (grey)

/* Chart Palette */
['#2DCC9E', '#1FAD85', '#81E6D9', '#66BB6A', '#4CAF50', '#43A047', '#2E7D32', '#1B5E20']
```

---

## 🔧 Common Usage Patterns

### Stats Dashboard
```tsx
<StatsCardGrid>
  <StatsCard
    title="Total Applications"
    value={5622}
    description="Last 12 months"
    trend={{ value: 12, direction: 'up' }}
    icon={<FileText className="h-5 w-5" />}
  />
</StatsCardGrid>
```

### Line Chart
```tsx
<TrendChart
  title="Monthly Trends"
  data={monthlyData}
  type="line"
  dataKeys={{ xAxis: 'month', yAxis: ['total', 'approved'] }}
  showExport={true}
/>
```

### Applications Table with Freemium
```tsx
<ApplicationsTable
  applications={apps}
  showFreemiumGate={true}
  freeLimit={5}
  currentPage={1}
  totalPages={10}
  onPageChange={setPage}
/>
```

### Interactive Map
```tsx
<PlanningMap
  applications={apps}
  center={[51.5074, -0.1278]}
  zoom={12}
  height="600px"
  showBasemapSwitcher={true}
  showLegend={true}
/>
```

### SEO Metadata (Next.js App Router)
```tsx
// In page.tsx
export const metadata = generateAuthorityMetadata('Poole', {
  totalApplications: 5622,
  approvalRate: 0.8,
  avgDecisionDays: 11
})

// Or custom
export const metadata = generateMetadata({
  title: 'Planning Applications in Milton Keynes',
  description: 'View all planning applications...',
  canonical: '/authorities/milton-keynes'
})
```

### Schema.org Markup
```tsx
<StructuredData
  schema={[
    {
      type: 'GovernmentOrganization',
      name: 'Poole Borough Council',
      url: 'https://planningexplorer.com/authorities/poole'
    },
    {
      type: 'Dataset',
      name: 'Poole Planning Applications',
      description: '5,622 planning applications'
    }
  ]}
/>
```

---

## 📐 Layout Template (Authority Page)

```tsx
export default function AuthorityPage({ params }) {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* 1. HERO SECTION */}
      <div className="bg-white border-b">
        <Container>
          <Breadcrumbs items={[...]} />
          <h1>Planning Applications in {authorityName}</h1>
          <Button>Track applications</Button>
        </Container>
      </div>

      {/* 2. KEY STATS */}
      <Container>
        <StatsCardGrid>
          {/* 6 stats cards */}
        </StatsCardGrid>
      </Container>

      {/* 3. FILTERS */}
      <Container>
        <div className="flex gap-4">
          {/* Date range, Status, Sector, Sort */}
        </div>
      </Container>

      {/* 4. CHARTS */}
      <Container>
        <div className="grid lg:grid-cols-2 gap-6">
          <TrendChart type="line" />
          <TrendChart type="pie" />
        </div>
      </Container>

      {/* 5. APPLICATIONS TABLE */}
      <Container>
        <ApplicationsTable showFreemiumGate={true} />
      </Container>

      {/* 6. RELATED CONTENT */}
      <Container>
        {/* Links to nearby authorities, sectors */}
      </Container>

      {/* 7. SEO */}
      <StructuredData schema={[...]} />
    </div>
  )
}
```

---

## 🌍 Map Basemaps (CARTO)

```tsx
import { CARTO_BASEMAPS } from '@/lib/map-config'

// Available basemaps (all free, no API key):
CARTO_BASEMAPS.light    // Clean minimal style
CARTO_BASEMAPS.dark     // Dark theme
CARTO_BASEMAPS.voyager  // Balanced with labels (default)

// Tile URL pattern:
https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png
```

---

## 📱 Responsive Breakpoints

```tsx
// Mobile
<768px   - Single column, card views
// Tablet
768-1023px - 2 columns, compact layout
// Desktop
1024px+  - 4 columns, full features

// StatsCardGrid automatically adapts:
grid-cols-1 md:grid-cols-2 lg:grid-cols-4
```

---

## 🔐 Freemium Logic

```tsx
const FREE_LIMIT = 5

// Show first 5 results
const visibleApps = applications.slice(0, FREE_LIMIT)

// Show gate if more results
{applications.length > FREE_LIMIT && (
  <FreemiumGate
    totalResults={applications.length}
    visibleResults={FREE_LIMIT}
  />
)}
```

---

## 🎯 ISR Configuration

```tsx
// In page.tsx (Next.js App Router)
export const revalidate = 3600 // 1 hour

// Or dynamic based on page type:
export const revalidate = params.type === 'authority' ? 3600 : 7200
```

---

## 🧪 Testing Data

```tsx
// Mock application for testing
const mockApp = {
  id: 'app-123',
  address: '123 High Street, London',
  status: 'Approved',
  date: '2024-10-01',
  opportunityScore: 85,
  decisionDays: 42,
  description: 'Residential extension',
  location: { lat: 51.5074, lng: -0.1278 }
}

// Mock stats
const mockStats = {
  authority_name: 'Poole',
  total_applications_12m: 258,
  total_applications_all_time: 5622,
  approval_rate: 0.8,
  avg_decision_days: 11,
  active_applications: 1108,
  top_sectors: [{ sector: 'Residential', count: 133, percentage: 51.6 }],
  status_breakdown: { Approved: 206, Pending: 48, Rejected: 4 },
  monthly_trend: [
    { month: '2024-10', total: 196, permitted: 150, rejected: 10, pending: 36 }
  ]
}
```

---

## ⚡ Performance Tips

1. **Map Components:** Always use dynamic import to prevent SSR errors
2. **Charts:** Limit data points to 24 months max
3. **Tables:** Implement virtual scrolling for 1000+ rows
4. **Images:** Use Next.js Image component with proper sizing
5. **API Calls:** Use ISR caching, avoid client-side fetching when possible

---

## 🐛 Common Issues & Solutions

### Issue: Map not rendering
**Solution:** Check dynamic import and SSR: false flag

### Issue: React 19 peer dependency warnings
**Solution:** Use --legacy-peer-deps flag with npm install

### Issue: Marker icons not showing
**Solution:** Verify Leaflet CSS imported in globals.css

### Issue: Charts too small on mobile
**Solution:** Set minHeight and use ResponsiveContainer

### Issue: Freemium gate not showing
**Solution:** Ensure applications.length > freeLimit

---

## 📞 API Endpoints Used

```
GET /api/v1/stats/authority/{slug}
GET /api/v1/applications/authority/{slug}?page=1&page_size=20
GET /api/v1/stats/location/{slug}?radius=5
GET /api/v1/applications/nearby?lat=51.5&lng=-0.1&radius=5
GET /api/v1/stats/sector/{slug}
```

---

**Last Updated:** October 2, 2025
**Version:** 1.0.0
**Status:** Production Ready
