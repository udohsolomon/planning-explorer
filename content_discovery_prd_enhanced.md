# 📄 PRD – Content & Discovery Pages (Enhanced for Specialist Agents)

**Product Name:** Planning Explorer
**Feature Set:** Content & Discovery Pages
**Version:** v2.0 (Enhanced - Specialist-Ready)
**Owner:** Planning Explorer Product Team
**Date:** 2025-10-02
**Framework:** Custom Subagent Coordination

---

## 📋 Executive Summary

**What:** Discovery-oriented landing pages showcasing planning applications by authority, location, and sector, plus an interactive Insights Hub.

**Why:**
- **SEO Growth** → Drive 10k+ long-tail organic traffic
- **User Discovery** → Enable exploration without complex searches
- **Brand Authority** → Establish Planning Explorer as the UK planning intelligence leader
- **Monetization** → Convert SEO traffic to Pro/Enterprise subscriptions

**Success Criteria:**
- 10k+ indexed SEO pages within 6 months
- 40% increase in organic traffic
- 15% conversion from discovery pages to Pro signups
- Sub-2s page load time for all content pages

---

## 🎯 Strategic Overview

### Business Objectives
1. **Traffic Growth**: Capture long-tail search queries (e.g., "Planning Applications in Milton Keynes 2025")
2. **User Engagement**: Reduce bounce rate by 25% through valuable content
3. **Revenue Impact**: Generate 30% of new Pro subscriptions from content pages
4. **Market Position**: Become the #1 ranked source for UK planning data discovery

### User Personas
1. **Property Developers**: Researching opportunities in specific areas
2. **Planning Consultants**: Monitoring trends and competitor activity
3. **Suppliers**: Identifying upcoming projects in their sector
4. **Investors**: Analyzing market activity and approval rates
5. **General Public**: Checking local planning applications

---

## 🏗️ Feature Specifications

### 2.1 Authority Pages 🏛️
**Route Pattern:** `/authorities/[authority-slug]`
**Example:** `/authorities/milton-keynes-city-council`

#### Core Features
✅ **Hero Section**
- H1: "Planning Applications in [Authority Name]"
- Authority logo/coat of arms (if available)
- Last updated timestamp
- CTA: "Track applications in this area" → signup

✅ **Key Stats Dashboard** (shadcn/ui Cards)
- Total applications (last 12 months, all-time)
- Approval rate (% with trend indicator)
- Average decision time (days, with benchmark comparison)
- Current active applications
- Top 3 sectors by volume
- Busiest month (historical data)

✅ **Interactive Filters** (shadcn/ui Select, DatePicker)
- Date range selector (Last 30 days, 3 months, 12 months, All time)
- Application status (Approved, Pending, Rejected, Withdrawn)
- Use class/sector dropdown
- Sort by: Date, Opportunity Score, Decision Time

✅ **Visualizations** (Recharts)
- **Line Chart**: Monthly trend of applications (12-month rolling)
- **Pie Chart**: Approval vs Refusal breakdown
- **Bar Chart**: Top 10 sectors by volume
- **Heat Map**: Decision times across months (calendar view)

✅ **Application List** (shadcn/ui DataTable)
- Paginated results (20 per page, ISR cached)
- Columns: Address, Status, Date, Opportunity Score, Decision Time
- Click-through to full application detail
- Freemium limit: Show 5 results, "Sign up to see all"

✅ **Related Content Section**
- Link to authority's website
- Related location pages (towns within authority)
- Related sector pages
- "Authorities nearby" carousel

✅ **SEO Optimization**
- Dynamic meta title: "Planning Applications in [Authority] | Planning Explorer"
- Meta description: Stats summary with call-to-action
- Schema.org: GovernmentOrganization + Dataset
- Canonical URL with proper routing
- Open Graph tags for social sharing
- Breadcrumbs: Home → Authorities → [Authority]

---

### 2.2 Location Pages 📍
**Route Pattern:** `/locations/[location-slug]`
**Examples:**
- `/locations/manchester`
- `/locations/mk1-2ab` (postcode level)

#### Core Features
✅ **Hero Section**
- H1: "Planning Applications in [Location]"
- Location type badge (City, Town, Postcode District)
- Geographic context: "[Location], [County/Region]"
- CTA: "Get alerts for this location"

✅ **Interactive Map** (OpenStreetMap + CARTO Basemaps)
- **Tile Provider**: CARTO basemaps (Light, Dark, Voyager styles)
- **Map Library**: Leaflet.js (open-source, lightweight)
- **Clustered Markers**: MarkerCluster plugin for application grouping
- **Color-coded Markers**: By status (green=approved, orange=pending, red=rejected)
- **Interactions**: Click markers to preview application details
- **Drawing Tools**: Leaflet-Draw for custom boundary filtering
- **Zoom Levels**: Auto-fit to location boundary with appropriate zoom
- **Basemap Styles**: Toggle between CARTO Light, Dark, and Voyager themes
- **No API Keys Required**: OSM + CARTO free tier (self-hosted tiles optional)

✅ **Location Stats** (shadcn/ui Cards with icons)
- Total applications this year
- Most common sectors (Top 3 with percentages)
- Average decision time (if multi-authority, show breakdown)
- Authority coverage (if location spans multiple councils)
- Population context (if available from ONS data)
- Comparison to regional average

✅ **Visualizations**
- **Area Chart**: Monthly applications (stacked by status)
- **Donut Chart**: Sector distribution
- **Heat Map**: Geographic density within location
- **Timeline**: Notable/high-value applications

✅ **Application List** (Enhanced DataTable)
- Distance sorting (nearest first)
- Map sync: Click row → highlight marker
- "View on map" button per row
- Freemium: 3 results preview

✅ **Location Insights** (AI-Generated)
- One-paragraph summary: "In [Location], residential development dominates with 45% of applications..."
- Trend analysis: "Approvals have increased 12% compared to last year..."
- Notable projects: Highlight 2-3 significant applications

✅ **SEO Optimization**
- Dynamic meta: "Planning Applications in [Location] - [Year] Data"
- Schema.org: Place + Dataset
- Local business schema (if commercial-focused)
- Geo-coordinates in meta tags
- FAQ schema: "How many planning applications in [Location]?"

---

### 2.3 Sector / Use Class Pages 🏗️
**Route Pattern:** `/sectors/[sector-slug]`
**Examples:**
- `/sectors/residential`
- `/sectors/renewable-energy`
- `/sectors/student-housing`

#### Core Features
✅ **Hero Section**
- H1: "[Sector] Planning Applications"
- Sector icon/illustration
- Industry context: Brief description of sector
- CTA: "Track [Sector] opportunities"

✅ **Sector Intelligence Dashboard**
- UK-wide volume (last 12 months, trend %)
- Sector approval rate (vs national average)
- Average project value (if available)
- Top 5 most active authorities
- Top 5 most active agents/consultants
- Growth forecast (AI prediction based on trends)

✅ **Visualizations**
- **Multi-line Chart**: Sector trends over 24 months (compare regions)
- **Horizontal Bar**: Top 10 authorities by volume
- **Network Graph**: Agent/Consultant activity (Pro feature)
- **Funnel Chart**: Application → Approval conversion

✅ **Application List** (Sector-Filtered DataTable)
- Default sort: Opportunity Score (highest first)
- Sector-specific columns: Project Type, Agent, Estimated Value
- Freemium: 5 results, "Unlock full list"

✅ **Sector Insights** (AI-Generated Long-Form)
- **Overview**: "The [Sector] sector has seen [trend] over the past 12 months..."
- **Regulatory Context**: Key planning policies affecting this sector
- **Market Drivers**: What's fueling growth or decline
- **Geographic Hotspots**: Where activity is concentrated
- **Opportunities**: "Suppliers in [service] should focus on [regions]"
- Word count: 500-800 words (SEO-optimized)

✅ **Industry Resources** (Pro/Enterprise)
- Downloadable sector report (PDF)
- Agent league table (approval rates, volume)
- Case studies: Successful applications in sector
- Upcoming policy changes affecting sector

✅ **Related Sectors**
- "Explore similar sectors" carousel
- Cross-linking to complementary sectors

✅ **SEO Optimization**
- Meta title: "[Sector] Planning Applications UK - [Year] Data & Trends"
- Long meta description (155-160 chars)
- Schema.org: Dataset + Article (for insights content)
- FAQ schema: "What are [sector] planning applications?"
- Author markup (if insights are AI + human reviewed)

---

### 2.4 Trends & Insights Hub 📊
**Route:** `/insights`
**Purpose:** Interactive data-driven hub showcasing UK-wide planning intelligence

#### Core Features
✅ **Dashboard Navigation** (shadcn/ui Tabs)
- Tab 1: Authorities Overview
- Tab 2: Regional Trends
- Tab 3: Sector Performance
- Tab 4: Agent League Tables
- Tab 5: Predictive Insights (Enterprise)

✅ **Authorities Dashboard**
- **Top 10 by Approvals** (Monthly update)
  - Bar chart with % approved
  - Median decision time indicator
  - Click → Authority page
- **Fastest Decision Times** (Ranked list)
  - Days to decision (median, P50, P90)
  - Trend arrows
- **Most Active** (By application volume)
  - Applications per 1000 population (normalized)

✅ **Regional Trends Dashboard**
- **UK Map**: Choropleth showing application density
- **Regional Comparison**: Line charts (England, Scotland, Wales, NI)
- **Urban vs Rural**: Approval rate comparison
- **Filters**: Date range, sector filter

✅ **Sector Performance Dashboard**
- **Sector Growth Matrix**: Bubble chart (volume vs approval rate)
- **Emerging Sectors**: AI-identified growth sectors
- **Declining Sectors**: Trend analysis
- **Seasonal Patterns**: Heatmap of sector activity by month

✅ **Agent League Tables** (Pro Feature)
- **Most Active Agents**: Volume + success rate
- **Top Consultants by Sector**: Specialized rankings
- **Approval Rate Champions**: Agents with 80%+ approval
- **Rising Stars**: New agents with strong performance
- Filters: Sector, region, authority

✅ **Predictive Insights** (Enterprise Feature - AI-Powered)
- **Approval Forecasts**: ML model predictions for sectors/regions
- **Capacity Warnings**: Authorities approaching backlog thresholds
- **Trend Alerts**: Emerging opportunities or risks
- **Market Shifts**: AI-detected pattern changes

✅ **Interactive Features**
- **Export Options** (Pro/Enterprise):
  - PNG/SVG chart downloads
  - CSV data export
  - PDF dashboard reports
- **Shareable Links**: Save dashboard state in URL
- **Alerts**: "Notify me when [metric] changes"
- **Comparison Mode**: Select multiple authorities/sectors to compare

✅ **SEO Content**
- **Monthly Commentary**: "This Month's Planning Insights" (blog-style)
- **Quarterly Reports**: "Q1 2025 UK Planning Trends" (evergreen)
- **Data Stories**: "Why Manchester's Approval Rate Surged in March"
- Schema.org: Article + Dataset

---

## 🔧 Technical Architecture

### 3.1 Elasticsearch Schema Enhancements

#### New Aggregation Pipelines
**Authority Aggregations** (`/stats/authority/{id}`)
```json
{
  "aggregations": {
    "total_applications": { "value_count": { "field": "id" } },
    "approval_rate": { "avg": { "field": "is_approved" } },
    "avg_decision_days": { "avg": { "field": "decision_days" } },
    "by_status": { "terms": { "field": "status" } },
    "by_sector": { "terms": { "field": "use_class", "size": 10 } },
    "monthly_trend": {
      "date_histogram": {
        "field": "submitted_date",
        "calendar_interval": "month"
      },
      "aggs": { "approved": { "filter": { "term": { "status": "approved" } } } }
    }
  }
}
```

**Location Aggregations** (`/stats/location/{slug}`)
- Geo-bounding box queries for location boundaries
- Geohash grid aggregations for heatmaps
- Distance-based sorting from location centroid

**Sector Aggregations** (`/stats/sector/{slug}`)
- Multi-level aggregations: Sector → Authority → Month
- Top agents by sector (terms aggregation on `agent_name`)
- Opportunity score distribution (histogram aggregation)

**Trends Aggregations** (`/stats/trends`)
- Time-series aggregations with moving averages
- Percentile aggregations for decision times
- Composite aggregations for league tables

#### New ES Fields Required
```json
{
  "location_slug": { "type": "keyword" },
  "authority_slug": { "type": "keyword" },
  "sector_slug": { "type": "keyword" },
  "decision_days": { "type": "integer" },
  "is_approved": { "type": "boolean" },
  "project_value_estimate": { "type": "float" },
  "agent_name": { "type": "keyword" },
  "consultant_name": { "type": "keyword" },
  "geo_location": { "type": "geo_point" },
  "location_boundary": { "type": "geo_shape" }
}
```

---

### 3.2 Backend API Specifications (FastAPI)

#### New Endpoints

**Authority Stats**
```python
@router.get("/api/stats/authority/{authority_slug}")
async def get_authority_stats(
    authority_slug: str,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    sector: Optional[str] = None
) -> AuthorityStatsResponse
```

**Location Stats**
```python
@router.get("/api/stats/location/{location_slug}")
async def get_location_stats(
    location_slug: str,
    radius_km: Optional[float] = None,
    include_map_data: bool = False
) -> LocationStatsResponse
```

**Sector Stats**
```python
@router.get("/api/stats/sector/{sector_slug}")
async def get_sector_stats(
    sector_slug: str,
    region: Optional[str] = None,
    authority: Optional[str] = None
) -> SectorStatsResponse
```

**Trends Dashboard**
```python
@router.get("/api/stats/trends")
async def get_trends_dashboard(
    dashboard_type: Literal["authorities", "regions", "sectors", "agents"],
    date_range: str = "12m",
    limit: int = 10
) -> TrendsDashboardResponse
```

#### Response Models (Pydantic)
```python
class AuthorityStatsResponse(BaseModel):
    authority_name: str
    authority_slug: str
    total_applications: int
    approval_rate: float
    avg_decision_days: float
    monthly_trend: List[MonthlyDataPoint]
    top_sectors: List[SectorBreakdown]
    status_breakdown: Dict[str, int]
    applications_preview: List[ApplicationPreview]  # 5 results for freemium

class LocationStatsResponse(BaseModel):
    location_name: str
    location_type: str  # city, town, postcode
    boundary: Optional[GeoJSON]
    total_applications: int
    authorities: List[str]  # If multi-authority
    sector_breakdown: List[SectorBreakdown]
    map_markers: Optional[List[MapMarker]]
    ai_summary: str  # Generated insight

class SectorStatsResponse(BaseModel):
    sector_name: str
    uk_volume: int
    approval_rate: float
    top_authorities: List[AuthorityBreakdown]
    top_agents: List[AgentStats]
    trend_data: List[MonthlyDataPoint]
    ai_insights: str  # Long-form generated content
```

#### Caching Strategy
**ES Built-in Caching:**
- Use ES request cache for repeated aggregation queries
- Cache query results for 5 minutes (configurable TTL)
- Invalidate on data updates (webhook from scraper)

**Application-Level Caching:**
- Cache heavy aggregations in memory (in-process LRU cache)
- Cache size: 1000 entries, 1-hour TTL
- Cache warming: Pre-compute top 100 authorities/locations on deployment

**ISR (Next.js):**
- Revalidate static pages every 3600 seconds (1 hour)
- On-demand revalidation via webhook `/api/revalidate`

---

### 3.3 Frontend Architecture (Next.js 14)

#### File Structure
```
planning-explorer-frontend/
├── app/
│   ├── authorities/
│   │   └── [slug]/
│   │       ├── page.tsx          # Dynamic authority page
│   │       └── loading.tsx       # Skeleton loader
│   ├── locations/
│   │   └── [slug]/
│   │       ├── page.tsx          # Dynamic location page
│   │       ├── components/
│   │       │   ├── LocationMap.tsx
│   │       │   └── LocationStats.tsx
│   ├── sectors/
│   │   └── [slug]/
│   │       ├── page.tsx          # Dynamic sector page
│   │       └── components/
│   │           ├── SectorDashboard.tsx
│   │           └── SectorInsights.tsx
│   ├── insights/
│   │   ├── page.tsx              # Trends hub landing
│   │   └── components/
│   │       ├── AuthoritiesDashboard.tsx
│   │       ├── RegionalTrends.tsx
│   │       ├── SectorPerformance.tsx
│   │       └── AgentLeagues.tsx
│   └── api/
│       ├── stats/
│       │   └── [...path]/route.ts  # Proxy to FastAPI
│       └── revalidate/route.ts     # ISR webhook
├── components/
│   ├── discovery/
│   │   ├── StatsCard.tsx         # Reusable stat display
│   │   ├── TrendChart.tsx        # Chart wrapper
│   │   ├── ApplicationsTable.tsx # Enhanced table
│   │   └── FreemiumGate.tsx      # Paywall component
│   ├── maps/
│   │   ├── PlanningMap.tsx       # Leaflet map wrapper
│   │   ├── MapMarkers.tsx        # Custom marker components
│   │   ├── MapClusters.tsx       # MarkerCluster integration
│   │   └── MapControls.tsx       # Basemap switcher, draw tools
│   └── seo/
│       ├── StructuredData.tsx    # Schema.org JSON-LD
│       └── SEOHead.tsx           # Meta tags helper
├── lib/
│   ├── stats-api.ts              # Stats endpoint client
│   ├── seo-helpers.ts            # Dynamic meta generation
│   ├── geo-utils.ts              # Location/boundary helpers
│   └── map-config.ts             # Leaflet + CARTO configuration
```

#### Map Integration Configuration

**Dependencies (package.json):**
```json
{
  "dependencies": {
    "leaflet": "^1.9.4",
    "react-leaflet": "^4.2.1",
    "leaflet.markercluster": "^1.5.3",
    "react-leaflet-markercluster": "^4.0.0",
    "leaflet-draw": "^1.0.4",
    "@types/leaflet": "^1.9.8",
    "@types/leaflet.markercluster": "^1.5.4"
  }
}
```

**CARTO Basemap Configuration:**
```typescript
// lib/map-config.ts
export const CARTO_BASEMAPS = {
  light: {
    url: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    maxZoom: 19,
    subdomains: 'abcd'
  },
  dark: {
    url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    maxZoom: 19,
    subdomains: 'abcd'
  },
  voyager: {
    url: 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    maxZoom: 19,
    subdomains: 'abcd'
  }
}

export const DEFAULT_MAP_CONFIG = {
  center: [54.5, -2.0], // UK center
  zoom: 6,
  minZoom: 5,
  maxZoom: 18,
  scrollWheelZoom: true,
  zoomControl: true
}

export const MARKER_CLUSTER_CONFIG = {
  spiderfyOnMaxZoom: true,
  showCoverageOnHover: false,
  zoomToBoundsOnClick: true,
  maxClusterRadius: 80,
  iconCreateFunction: (cluster) => {
    const count = cluster.getChildCount()
    let size = 'small'
    if (count > 10) size = 'medium'
    if (count > 50) size = 'large'

    return L.divIcon({
      html: `<div class="marker-cluster-${size}">${count}</div>`,
      className: 'marker-cluster',
      iconSize: L.point(40, 40)
    })
  }
}
```

**Example PlanningMap Component:**
```typescript
// components/maps/PlanningMap.tsx
'use client'

import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import MarkerClusterGroup from 'react-leaflet-markercluster'
import { FeatureGroup } from 'react-leaflet'
import { EditControl } from 'react-leaflet-draw'
import L from 'leaflet'
import { useState, useMemo } from 'react'
import { CARTO_BASEMAPS, DEFAULT_MAP_CONFIG, MARKER_CLUSTER_CONFIG } from '@/lib/map-config'

// Custom marker icons
const getMarkerIcon = (status: string) => {
  const colors = {
    approved: '#10B981',
    pending: '#F59E0B',
    rejected: '#EF4444'
  }

  return L.divIcon({
    html: `<div style="background-color: ${colors[status]}; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white;"></div>`,
    className: 'custom-marker',
    iconSize: [16, 16]
  })
}

interface PlanningMapProps {
  applications: Application[]
  center?: [number, number]
  zoom?: number
  onBoundaryDraw?: (bounds: L.LatLngBounds) => void
}

export function PlanningMap({
  applications,
  center = DEFAULT_MAP_CONFIG.center,
  zoom = DEFAULT_MAP_CONFIG.zoom,
  onBoundaryDraw
}: PlanningMapProps) {
  const [basemap, setBasemap] = useState<'light' | 'dark' | 'voyager'>('light')

  const markers = useMemo(() => (
    applications
      .filter(app => app.latitude && app.longitude)
      .map(app => ({
        id: app.id,
        position: [app.latitude, app.longitude] as [number, number],
        status: app.status,
        data: app
      }))
  ), [applications])

  return (
    <div className="relative w-full h-[600px] rounded-lg overflow-hidden">
      {/* Basemap Switcher */}
      <div className="absolute top-4 right-4 z-[1000] flex gap-2">
        {(['light', 'dark', 'voyager'] as const).map((style) => (
          <button
            key={style}
            onClick={() => setBasemap(style)}
            className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
              basemap === style
                ? 'bg-primary text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            {style.charAt(0).toUpperCase() + style.slice(1)}
          </button>
        ))}
      </div>

      <MapContainer
        center={center}
        zoom={zoom}
        scrollWheelZoom={DEFAULT_MAP_CONFIG.scrollWheelZoom}
        className="h-full w-full"
      >
        {/* CARTO Basemap Tile Layer */}
        <TileLayer
          url={CARTO_BASEMAPS[basemap].url}
          attribution={CARTO_BASEMAPS[basemap].attribution}
          maxZoom={CARTO_BASEMAPS[basemap].maxZoom}
          subdomains={CARTO_BASEMAPS[basemap].subdomains}
        />

        {/* Drawing Tools (Optional) */}
        {onBoundaryDraw && (
          <FeatureGroup>
            <EditControl
              position="topleft"
              onCreated={(e) => {
                const layer = e.layer
                if (layer instanceof L.Rectangle || layer instanceof L.Polygon) {
                  onBoundaryDraw(layer.getBounds())
                }
              }}
              draw={{
                rectangle: true,
                polygon: true,
                circle: false,
                circlemarker: false,
                marker: false,
                polyline: false
              }}
            />
          </FeatureGroup>
        )}

        {/* Clustered Markers */}
        <MarkerClusterGroup {...MARKER_CLUSTER_CONFIG}>
          {markers.map((marker) => (
            <Marker
              key={marker.id}
              position={marker.position}
              icon={getMarkerIcon(marker.status)}
            >
              <Popup>
                <div className="p-2">
                  <h3 className="font-semibold text-sm mb-1">
                    {marker.data.address}
                  </h3>
                  <p className="text-xs text-gray-600 mb-2">
                    {marker.data.applicationId}
                  </p>
                  <span className={`text-xs px-2 py-1 rounded ${
                    marker.status === 'approved' ? 'bg-green-100 text-green-700' :
                    marker.status === 'pending' ? 'bg-orange-100 text-orange-700' :
                    'bg-red-100 text-red-700'
                  }`}>
                    {marker.status.toUpperCase()}
                  </span>
                  <button
                    className="mt-2 text-xs text-blue-600 hover:underline"
                    onClick={() => window.location.href = `/applications/${marker.id}`}
                  >
                    View Details →
                  </button>
                </div>
              </Popup>
            </Marker>
          ))}
        </MarkerClusterGroup>
      </MapContainer>

      {/* Map Legend */}
      <div className="absolute bottom-4 left-4 z-[1000] bg-white p-3 rounded-md shadow-md">
        <h4 className="text-xs font-semibold mb-2">Status</h4>
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span className="text-xs">Approved</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-orange-500"></div>
            <span className="text-xs">Pending</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <span className="text-xs">Rejected</span>
          </div>
        </div>
      </div>
    </div>
  )
}
```

**Styling (globals.css):**
```css
/* Leaflet marker cluster styling */
.marker-cluster {
  background: rgba(59, 130, 246, 0.6);
  border: 3px solid rgba(59, 130, 246, 0.8);
  border-radius: 50%;
  color: white;
  font-weight: bold;
  text-align: center;
  line-height: 40px;
}

.marker-cluster-small {
  width: 40px;
  height: 40px;
  font-size: 12px;
}

.marker-cluster-medium {
  width: 50px;
  height: 50px;
  font-size: 14px;
  background: rgba(245, 158, 11, 0.6);
  border-color: rgba(245, 158, 11, 0.8);
}

.marker-cluster-large {
  width: 60px;
  height: 60px;
  font-size: 16px;
  background: rgba(239, 68, 68, 0.6);
  border-color: rgba(239, 68, 68, 0.8);
}

/* Custom marker styling */
.custom-marker {
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
}

/* Leaflet popup customization */
.leaflet-popup-content-wrapper {
  border-radius: 8px;
  padding: 0;
}

.leaflet-popup-content {
  margin: 0;
}
```

#### SSR/ISR Strategy
**Static Pre-rendering (generateStaticParams):**
- Top 100 authorities
- Top 200 locations (major cities/towns)
- All sector pages (~20 sectors)

**ISR (Incremental Static Regeneration):**
- All other authority pages (400+ councils)
- Postcode-level pages (10k+ routes)
- Revalidate: 3600s (1 hour)

**Dynamic SSR:**
- Insights Hub (real-time data)
- User-specific dashboards (logged-in)

#### Component Library (shadcn/ui)
**Required Components:**
- Card, Badge, Button (already implemented)
- Tabs, Select, DatePicker (for filters)
- DataTable (enhanced with server-side pagination)
- Skeleton (loading states)
- Dialog (freemium modals)
- Tooltip (stat explanations)

**Custom Components:**
- `<StatsCard>`: Stat value + trend indicator + icon
- `<TrendChart>`: Recharts wrapper with responsive config
- `<FreemiumGate>`: "Sign up to see more" overlay
- `<PlanningMap>`: Leaflet map wrapper with CARTO basemaps
- `<MapMarkers>`: Custom status-based marker components
- `<MapClusters>`: MarkerClusterGroup integration
- `<MapControls>`: Basemap switcher and Leaflet-Draw tools

---

### 3.4 SEO Implementation

#### Dynamic Meta Tags (Next.js Metadata API)
```typescript
// app/authorities/[slug]/page.tsx
export async function generateMetadata({ params }): Promise<Metadata> {
  const stats = await getAuthorityStats(params.slug)

  return {
    title: `Planning Applications in ${stats.authority_name} | Planning Explorer`,
    description: `${stats.total_applications} planning applications in ${stats.authority_name}. ${stats.approval_rate}% approval rate. View detailed stats and trends.`,
    openGraph: {
      title: `${stats.authority_name} Planning Data`,
      description: `Discover planning applications and trends in ${stats.authority_name}`,
      images: [{ url: generateOGImage(stats) }],
    },
    alternates: {
      canonical: `/authorities/${params.slug}`,
    },
  }
}
```

#### Schema.org Structured Data
**Authority Pages:**
```json
{
  "@context": "https://schema.org",
  "@type": "GovernmentOrganization",
  "name": "Milton Keynes City Council",
  "url": "https://planningexplorer.com/authorities/milton-keynes-city-council",
  "dataset": {
    "@type": "Dataset",
    "name": "Planning Applications in Milton Keynes",
    "description": "Comprehensive dataset of planning applications...",
    "temporalCoverage": "2020/..",
    "spatialCoverage": {
      "@type": "Place",
      "name": "Milton Keynes"
    }
  }
}
```

**Location Pages:**
```json
{
  "@context": "https://schema.org",
  "@type": "Place",
  "name": "Manchester",
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": 53.4808,
    "longitude": -2.2426
  },
  "dataset": { ... }
}
```

**Sector Pages (Article + Dataset):**
```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Article",
      "headline": "Residential Planning Applications - 2025 Trends",
      "datePublished": "2025-01-01",
      "author": { "@type": "Organization", "name": "Planning Explorer" },
      "articleBody": "The residential sector has seen..."
    },
    {
      "@type": "Dataset",
      "name": "UK Residential Planning Applications"
    }
  ]
}
```

#### Sitemap Generation
```typescript
// app/sitemap.ts
export default async function sitemap(): MetadataRoute.Sitemap {
  const authorities = await getAllAuthorities()
  const locations = await getAllLocations()
  const sectors = await getAllSectors()

  return [
    ...authorities.map(a => ({
      url: `https://planningexplorer.com/authorities/${a.slug}`,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 0.8,
    })),
    ...locations.map(l => ({ ... })),
    ...sectors.map(s => ({ ... })),
  ]
}
```

#### Robots.txt
```
User-agent: *
Allow: /
Sitemap: https://planningexplorer.com/sitemap.xml

# Crawl-delay for polite bots
Crawl-delay: 1
```

---

## 🎨 UX/UI Design Specifications

### Design System Alignment
**Must match Planning Insights pixel-perfect design:**
- Primary color: `#2DCC9E` (Planning Insights green)
- Typography: SUSE (headings), DM Sans (body)
- Border radius: 8px
- Spacing: 8px grid system
- Shadows: Subtle, Planning Insights style

### Page Layout Template
```
┌─────────────────────────────────────────────┐
│          HEADER (Global Navigation)         │
├─────────────────────────────────────────────┤
│              HERO SECTION                   │
│  [Page Title] [CTA Button] [Last Updated]  │
├─────────────────────────────────────────────┤
│           KEY STATS PANEL (Cards)           │
│  [Stat 1]  [Stat 2]  [Stat 3]  [Stat 4]   │
├─────────────────────────────────────────────┤
│         FILTERS & SORT (Sticky)             │
│  [Date Range] [Status] [Sector] [Sort]     │
├─────────────────────────────────────────────┤
│        CHARTS / VISUALIZATIONS              │
│  [Chart 1]       [Chart 2]                  │
├─────────────────────────────────────────────┤
│        APPLICATION LIST (DataTable)         │
│  [Paginated results with freemium gate]    │
├─────────────────────────────────────────────┤
│         RELATED CONTENT SECTION             │
│  [Links to similar pages]                  │
├─────────────────────────────────────────────┤
│          FOOTER (Global)                    │
└─────────────────────────────────────────────┘
```

### Responsive Breakpoints
- **Mobile**: < 768px (single column, collapsed filters)
- **Tablet**: 768-1023px (two-column stats, simplified charts)
- **Desktop**: 1024px+ (full layout, side-by-side charts)

### Freemium UX Patterns
**Application Lists:**
- Show first 3-5 results
- Blur remaining results with overlay
- CTA: "Sign up free to see 50 more applications"
- Button: "Upgrade to Pro for full access"

**Charts:**
- Free: Show chart with watermark
- Pro: Remove watermark, add export button

**Downloads:**
- Free: Preview only
- Pro: CSV export
- Enterprise: PDF reports + API access

---

## 💰 Monetization Strategy

### Tier Feature Matrix

| Feature | Free (Starter) | Pro (£199.99/mo) | Enterprise (£499.99/mo) |
|---------|----------------|------------------|-------------------------|
| Authority Pages | 5 results preview | Full results | Full + API access |
| Location Pages | 3 results preview | Full results + map clusters | Full + custom boundaries |
| Sector Pages | Basic stats only | Full stats + AI insights | Full + agent league tables |
| Insights Hub | View only | Interactive + exports | Predictive analytics |
| Chart Exports | Watermarked PNG | Clean PNG/SVG/CSV | PDF reports + scheduled |
| AI Summaries | 100-word preview | Full summaries | Custom summaries |
| Alerts | None | Email alerts | Real-time webhooks |
| Historical Data | Last 12 months | 5 years | All-time |

### Conversion Funnels
**SEO → Free Signup:**
- Freemium gate on application list (CTA: "Sign up free")
- Email capture for alerts
- Lead magnet: "Download monthly planning report"

**Free → Pro:**
- Paywall on full results ("Upgrade to Pro")
- Feature discovery: Show locked features with upgrade prompt
- Trial offer: "7-day Pro trial"

**Pro → Enterprise:**
- Usage limits: "You've exported 50 charts this month. Upgrade for unlimited."
- API access: "Need programmatic access? Contact sales."
- Team features: "Add team members with Enterprise"

---

## 📊 Success Metrics & KPIs

### SEO Performance
**Primary Metrics:**
- **Indexed Pages**: Target 10,000+ in 6 months
- **Organic Impressions**: 500k/month by month 6
- **Click-Through Rate**: 3.5% average (above industry 2.5%)
- **Average Position**: Top 10 for 60% of target keywords

**Keyword Targets:**
- Authority queries: "planning applications in [council]" (400+ keywords)
- Location queries: "planning applications [city/town]" (1000+ keywords)
- Sector queries: "[sector] planning applications UK" (50+ keywords)

**Tracking:**
- Google Search Console API integration
- Weekly SEO reports in Insights Hub
- Rank tracking for top 100 keywords

### Engagement Metrics
**Time on Page:**
- Authority pages: > 2 minutes (benchmark: 1:30)
- Sector pages: > 3 minutes (content-heavy)
- Insights Hub: > 5 minutes (interactive)

**Interaction Rate:**
- Chart interactions: 40% of visitors
- Filter usage: 60% of visitors
- CTA clicks: 15% (signup or upgrade)

**Bounce Rate:**
- Target: < 50% (current benchmark: 65%)
- Sector pages: < 40% (high-value content)

### Conversion Metrics
**Free Signups:**
- SEO traffic → signup: 5% conversion
- Target: 500 signups/month from discovery pages

**Pro Upgrades:**
- Free → Pro from discovery pages: 10%
- Target: 50 Pro upgrades/month attributed to content

**Revenue Attribution:**
- 30% of new MRR from content pages
- LTV of SEO-acquired users: £500+

### Technical Performance
**Page Speed:**
- Lighthouse Score: > 95
- First Contentful Paint: < 1.2s
- Time to Interactive: < 2.0s
- Largest Contentful Paint: < 2.5s

**Availability:**
- Uptime: 99.9%
- API response time: < 200ms (p95)
- Cache hit rate: > 80%

---

## 🚀 Implementation Roadmap

### Phase 1: MVP Foundation (Weeks 1-6)
**Goal:** Launch authority and basic location pages with core SEO

**Elasticsearch Architect Tasks:**
- [ ] Design aggregation pipelines for authority stats
- [ ] Add new fields: `authority_slug`, `location_slug`, `decision_days`
- [ ] Create geospatial mappings for location queries
- [ ] Implement caching strategy for aggregations
- [ ] Performance test aggregations (< 100ms target)

**Backend Engineer Tasks:**
- [ ] Implement `/api/stats/authority/{slug}` endpoint
- [ ] Implement `/api/stats/location/{slug}` endpoint
- [ ] Create Pydantic response models
- [ ] Add request caching layer
- [ ] Generate slug data for all authorities and major locations
- [ ] Create data seeding script for testing

**Frontend Specialist Tasks:**
- [ ] Create authority page template (`app/authorities/[slug]/page.tsx`)
- [ ] Build location page template (`app/locations/[slug]/page.tsx`)
- [ ] Implement StatsCard component (shadcn/ui)
- [ ] Integrate Recharts for basic charts (line, pie, bar)
- [ ] Build ApplicationsTable with freemium gate
- [ ] Implement PlanningMap component with Leaflet + CARTO
- [ ] Add map marker clustering (react-leaflet-markercluster)
- [ ] Create map controls (basemap switcher, legend)
- [ ] Implement SEO metadata generation
- [ ] Add Schema.org structured data components
- [ ] Create skeleton loading states

**AI Engineer Tasks:**
- [ ] Generate AI summaries for top 100 authorities (batch process)
- [ ] Create location insights generation pipeline
- [ ] Implement opportunity score display on discovery pages

**QA Engineer Tasks:**
- [ ] Create E2E tests for authority pages (Playwright)
- [ ] Test SEO metadata generation
- [ ] Validate Schema.org markup
- [ ] Performance testing (Lighthouse CI)
- [ ] Accessibility audit (WCAG 2.1 AA)

**Deliverables:**
- 100 authority pages live
- 50 major location pages live
- All pages indexed by Google
- Core SEO optimizations complete

---

### Phase 2: Sector Pages & Insights Hub (Weeks 7-12)
**Goal:** Add sector intelligence and launch interactive Insights Hub

**Elasticsearch Architect Tasks:**
- [ ] Design sector aggregation pipelines
- [ ] Add `sector_slug`, `agent_name`, `consultant_name` fields
- [ ] Create multi-level aggregations (sector → authority → month)
- [ ] Implement agent/consultant analytics queries
- [ ] Optimize for Insights Hub dashboard queries

**Backend Engineer Tasks:**
- [ ] Implement `/api/stats/sector/{slug}` endpoint
- [ ] Implement `/api/stats/trends` endpoint with dashboard types
- [ ] Create agent league table queries
- [ ] Add export functionality (CSV, PDF generation)
- [ ] Implement alert subscription endpoints
- [ ] Add freemium/Pro/Enterprise access control

**Frontend Specialist Tasks:**
- [ ] Build sector page template with long-form content
- [ ] Create Insights Hub navigation (shadcn/ui Tabs)
- [ ] Implement AuthoritiesDashboard component
- [ ] Implement RegionalTrends component
- [ ] Implement SectorPerformance component
- [ ] Build agent league tables (DataTable)
- [ ] Add chart export functionality
- [ ] Integrate PDF report generation
- [ ] Build alert subscription UI

**AI Engineer Tasks:**
- [ ] Generate long-form sector insights (1500-3000 words per sector)
- [ ] Create trend analysis summaries
- [ ] Implement "This Month's Insights" auto-generation
- [ ] Build agent performance scoring algorithm

**Docs Writer Tasks:**
- [ ] Create user guides for discovery pages
- [ ] Write sector explainer content
- [ ] Document API endpoints for Enterprise customers

**QA Engineer Tasks:**
- [ ] E2E tests for sector pages and Insights Hub
- [ ] Test export functionality (CSV, PDF)
- [ ] Validate freemium gates and upgrade flows
- [ ] Load testing for dashboard queries

**Deliverables:**
- 20 sector pages live with AI insights
- Insights Hub launched with 4 dashboard types
- Export functionality for Pro users
- Alert subscription system live

---

### Phase 3: Advanced Features & Scale (Weeks 13-24)
**Goal:** Scale to 10k+ pages, add predictive analytics, enable full API access

**Elasticsearch Architect Tasks:**
- [ ] Optimize for 10k+ location pages (postcode level)
- [ ] Implement time-series forecasting data structures
- [ ] Create ML feature extraction pipelines
- [ ] Scale aggregation caching for high traffic

**Backend Engineer Tasks:**
- [ ] Generate slugs for all UK postcodes
- [ ] Implement ISR revalidation webhooks
- [ ] Create Enterprise API endpoints with authentication
- [ ] Add rate limiting and usage tracking
- [ ] Implement advanced filtering (custom date ranges, multiple sectors)
- [ ] Build data export scheduler for Enterprise

**Frontend Specialist Tasks:**
- [ ] Scale to 10k+ location pages via ISR
- [ ] Implement advanced Leaflet features (custom boundaries, Leaflet-Draw tools)
- [ ] Build predictive insights dashboard (Enterprise)
- [ ] Add comparison mode (multi-authority, multi-sector)
- [ ] Optimize bundle size and performance
- [ ] Implement social sharing features

**AI Engineer Tasks:**
- [ ] Train ML model for approval forecasting
- [ ] Implement capacity warning system (backlog detection)
- [ ] Create trend alert generation
- [ ] Build personalized recommendation engine

**DevOps Specialist Tasks:**
- [ ] Set up CDN for static assets
- [ ] Implement monitoring and alerting
- [ ] Scale infrastructure for high traffic
- [ ] Create backup and disaster recovery plan

**Security Auditor Tasks:**
- [ ] Audit API authentication and authorization
- [ ] Review freemium enforcement logic
- [ ] Validate GDPR compliance for alert subscriptions
- [ ] Penetration testing

**QA Engineer Tasks:**
- [ ] Load testing for 10k concurrent users
- [ ] Validate ISR revalidation logic
- [ ] Test ML predictions accuracy
- [ ] Enterprise API integration testing

**Deliverables:**
- 10,000+ SEO pages indexed
- Predictive analytics live for Enterprise
- Full API access with documentation
- Infrastructure scaled for growth

---

## 🧑‍💻 Specialist Agent Assignments

### Master Orchestrator Role
**Responsibilities:**
- Coordinate all phases and specialist handoffs
- Review integration between authority/location/sector pages
- Ensure consistency across all discovery pages
- Monitor progress against roadmap milestones
- Make architectural decisions (e.g., ISR vs SSR strategy)

**Key Decisions:**
- Prioritization of page types (authority → location → sector)
- Freemium gate thresholds (how many results to show)
- ISR revalidation intervals (balance freshness vs cost)
- When to parallelize specialists vs sequential execution

---

### Elasticsearch Architect 🔵
**Phase 1 Focus:**
- Authority and location aggregation pipelines
- Geospatial mapping and boundary queries
- Caching strategy for heavy aggregations

**Phase 2 Focus:**
- Sector aggregations and agent analytics
- Multi-level aggregations for Insights Hub
- Query optimization for dashboard performance

**Phase 3 Focus:**
- Scaling to 10k+ pages
- ML feature extraction for predictions
- Advanced geospatial queries

**Deliverables:**
- ES mapping configurations (JSON)
- Aggregation query templates
- Performance benchmarks
- Caching configuration

---

### Backend Engineer 🟠
**Phase 1 Focus:**
- Stats API endpoints for authority and location
- Response models and validation
- Slug generation for routes

**Phase 2 Focus:**
- Sector and trends endpoints
- Export functionality (CSV, PDF)
- Alert subscription system
- Access control (freemium/Pro/Enterprise)

**Phase 3 Focus:**
- Enterprise API with authentication
- Rate limiting and usage tracking
- ISR revalidation webhooks
- Scheduled data exports

**Deliverables:**
- FastAPI routers and endpoints
- Pydantic models
- API documentation (OpenAPI spec)
- Unit and integration tests

---

### Frontend Specialist 🟢
**Phase 1 Focus:**
- Authority and location page templates
- shadcn/ui components (StatsCard, charts, tables)
- Leaflet map integration with CARTO basemaps
- Map marker clustering and popups
- SEO metadata and Schema.org
- Skeleton loading states

**Phase 2 Focus:**
- Sector pages with long-form content
- Insights Hub with interactive dashboards
- Chart exports and PDF generation
- Alert subscription UI

**Phase 3 Focus:**
- Scaling to 10k+ ISR pages
- Advanced Leaflet features (draw tools, custom boundaries)
- Predictive insights dashboard
- Performance optimization

**Deliverables:**
- Next.js page components
- Reusable UI components (shadcn/ui)
- Leaflet map components with CARTO integration
- Map clustering and interactive features
- SEO implementation (metadata, Schema.org)
- Responsive design (mobile, tablet, desktop)

---

### AI Engineer 🔵
**Phase 1 Focus:**
- Authority and location AI summaries
- Opportunity score integration on discovery pages

**Phase 2 Focus:**
- Long-form sector insights (500-800 words)
- Trend analysis summaries
- Agent performance scoring

**Phase 3 Focus:**
- ML approval forecasting model
- Capacity warning system
- Personalized recommendations
- Trend alert generation

**Deliverables:**
- AI-generated content (summaries, insights)
- ML models (Python, trained and deployed)
- Prompt templates
- Accuracy evaluation reports

---

### QA Engineer 🟣
**Responsibilities Across All Phases:**
- E2E testing with Playwright (page navigation, interactions)
- SEO validation (meta tags, Schema.org, sitemap)
- Performance testing (Lighthouse, load tests)
- Accessibility audits (WCAG 2.1 AA)
- Freemium gate testing (paywall enforcement)
- Cross-browser compatibility

**Deliverables:**
- Playwright test suites
- Performance reports
- Accessibility audit results
- Bug reports and regression tests

---

### DevOps Specialist ⚫
**Phase 1 Focus:**
- CI/CD for Next.js deployment
- ISR configuration and monitoring

**Phase 2 Focus:**
- Scaling for increased traffic
- Monitoring and alerting setup

**Phase 3 Focus:**
- CDN setup for static assets
- Infrastructure scaling (auto-scaling, load balancing)
- Backup and disaster recovery

**Deliverables:**
- Docker configurations
- Deployment scripts
- Monitoring dashboards
- Infrastructure documentation

---

### Security Auditor 🔴
**Phase 2 Focus:**
- API authentication and authorization review
- Freemium enforcement security audit
- GDPR compliance for alerts

**Phase 3 Focus:**
- Enterprise API security review
- Rate limiting validation
- Penetration testing

**Deliverables:**
- Security audit reports
- Compliance checklists
- Remediation recommendations

---

### Docs Writer ⚪
**Phase 2 Focus:**
- User guides for discovery pages
- Sector explainer content
- API documentation for Enterprise

**Phase 3 Focus:**
- Enterprise API reference
- Data dictionary
- Developer onboarding guides

**Deliverables:**
- Markdown documentation
- OpenAPI specifications
- User guides and tutorials

---

## 🎯 Acceptance Criteria

### Authority Pages
- [ ] 400+ authority pages deployed
- [ ] All pages load in < 2s
- [ ] SEO metadata dynamically generated
- [ ] Schema.org markup validated
- [ ] Freemium gate enforced (5 results max)
- [ ] Charts render correctly on mobile
- [ ] Lighthouse score > 95

### Location Pages
- [ ] 1000+ location pages deployed (cities, towns, postcodes)
- [ ] Leaflet + OSM + CARTO integration functional
- [ ] Geospatial clustering accurate
- [ ] AI summaries generated for top 100 locations
- [ ] Responsive design tested on mobile/tablet/desktop

### Sector Pages
- [ ] 20 sector pages with 1500+ word AI insights
- [ ] Agent league tables functional (Pro feature)
- [ ] Sector trends charts accurate
- [ ] Internal linking to authority/location pages
- [ ] SEO content ranking in top 20 for target keywords

### Insights Hub
- [ ] 4 dashboard types functional (authorities, regions, sectors, agents)
- [ ] Chart exports working (PNG, CSV)
- [ ] PDF reports generated correctly
- [ ] Real-time data updates via ISR
- [ ] Predictive analytics functional (Enterprise)

### Technical
- [ ] All API endpoints documented
- [ ] Response times < 200ms (p95)
- [ ] Cache hit rate > 80%
- [ ] ISR revalidation working
- [ ] 10k+ pages in sitemap
- [ ] Google indexing confirmed

### Business
- [ ] 500+ free signups/month from discovery pages
- [ ] 10% conversion to Pro from freemium gates
- [ ] 30% of new MRR attributed to content pages
- [ ] SEO traffic up 40% within 6 months

---

## 📚 Appendix

### A. URL Structure Reference
```
/authorities/[authority-slug]
  Examples:
  - /authorities/milton-keynes-city-council
  - /authorities/manchester-city-council
  - /authorities/westminster-city-council

/locations/[location-slug]
  Examples:
  - /locations/manchester
  - /locations/milton-keynes
  - /locations/mk1-2ab (postcode)
  - /locations/greater-manchester (region)

/sectors/[sector-slug]
  Examples:
  - /sectors/residential
  - /sectors/renewable-energy
  - /sectors/commercial-retail
  - /sectors/student-housing

/insights
  - /insights?tab=authorities
  - /insights?tab=regions
  - /insights?tab=sectors
  - /insights?tab=agents
```

### B. Priority Keyword Targets (Top 50)
1. "planning applications in [council name]" (400+ variations)
2. "planning applications [city/town name]" (1000+ variations)
3. "[sector] planning applications UK"
4. "planning permission statistics [area]"
5. "planning approval rates [council]"
6. "fastest planning decisions UK"
7. "planning trends [year]"
8. "[sector] planning trends UK"
9. "planning consultants [area]"
10. "planning data [location]"

### C. Schema.org Templates
See technical specifications in Section 3.4.

### D. Freemium Conversion Optimizations
**Best Practices:**
- Show value before gating (5 results preview, not 0)
- Use gentle CTAs ("See all 147 applications →" vs "UPGRADE NOW")
- Offer free signup first, then upsell to Pro
- Display locked features prominently to encourage upgrades
- A/B test gate thresholds (3 vs 5 vs 10 results)

### E. Performance Budget
**Page Load:**
- HTML: < 50kb
- JavaScript: < 200kb (initial bundle)
- CSS: < 50kb
- Images: Lazy-loaded, WebP format
- Fonts: Preloaded, subset for performance

**API Response:**
- Authority stats: < 150ms
- Location stats: < 200ms (with geo queries)
- Sector stats: < 100ms (cached)
- Trends dashboard: < 300ms

---

## ✅ PRD Sign-Off

**Prepared for:** Planning Explorer Specialist Agent Framework
**Framework Version:** Custom Subagent Coordination v2.0
**Status:** Ready for Master Orchestrator

**Next Steps:**
1. Load Master Orchestrator: `@.claude/orchestrator/master-orchestrator.md`
2. Command: "Analyze content_discovery_prd_enhanced.md and create Phase 1 implementation plan"
3. Master Orchestrator will coordinate specialists for MVP delivery

---

*This enhanced PRD is optimized for specialist agent coordination with clear technical specifications, implementation phases, and acceptance criteria. Each specialist has defined tasks, deliverables, and integration points.*
