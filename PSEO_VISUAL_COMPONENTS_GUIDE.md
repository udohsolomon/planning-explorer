# pSEO Visual Components - Complete Guide

## Overview
Based on the Planning Report screenshot you provided, here are the 8 data visualization components that will be added to EACH of the 425 authority pSEO pages.

---

## Visual Component Reference (From Screenshot)

### **What You Showed Me:**

1. **Planning Recommendations Box** (Purple/Pink background)
   - Icon + text list
   - "Review all planning documents and consultation responses"
   - "Engage planning consultant for detailed assessment"
   - "Conduct site visit and local area analysis"

2. **Planning Application Volume Trends** (Bar Chart)
   - Green bars showing monthly applications
   - One RED/ORANGE bar highlighting peak month
   - X-axis: Months (Jan, Feb, Mar... Dec)
   - Y-axis: Number of Applications (0-100 scale)
   - Legend: "Approved" vs "Peak Month"

3. **Average Decision Timeline by Application Type** (Horizontal Bar Chart)
   - Teal/green horizontal bars
   - Shows: Householder (42 days), Full Planning (84 days), Reserved Matters (56 days), Prior Approval (28 days)
   - Different shades of green (darker = longer timeline)
   - Days shown at end of each bar

4. **Comparable Applications Analysis** (Data Table)
   - Columns: Reference | Description | Value | Status | Decision Date
   - Example rows:
     - APP/2024/2165 | 25 Bank Street - Commercial Tower | £324M | Approved ✅ | 12 Aug 2024
     - APP/2023/4789 | Wood Wharf Phase 2 | £567M | Approved ✅ | 21 Nov 2023
   - Status badges: Green for Approved, Yellow for Pending, Red for Refused

---

## Complete Visual Components for pSEO Pages

### **Component 1: Planning Recommendations**
**Type:** Icon + Text List
**Location:** Top of page, after hero section

```
┌─────────────────────────────────────────────────────┐
│  PLANNING RECOMMENDATIONS                           │
│                                                     │
│  📄 Review all planning documents and consultation  │
│     responses                                       │
│                                                     │
│  👥 Engage planning consultant for detailed        │
│     assessment                                      │
│                                                     │
│  🏗️  Conduct site visit and local area analysis    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Data Source:**
- Generated from approval patterns in Elasticsearch
- Policy analysis from scraped data
- AI-suggested based on refusal reasons

**Visual Style:**
- Light purple/pink background (#f3e8ff, #fae8ff)
- Purple checkmark icons
- Clean, scannable list format

---

### **Component 2: Application Volume Trends (Bar Chart)**
**Type:** Vertical Bar Chart
**Location:** Main data dashboard section

```
Planning Application Volume Trends (Last 12 Months)

  100 ┤
   75 ┤     ███         ███                    ███
   50 ┤ ███ ███     ███ ███     ███        ███ ███     ███
   25 ┤ ███ ███ ███ ███ ███ ███ ███    ███ ███ ███ ███ ███
    0 ┴─────────────────────────────────────────────────────
      Jan Feb Mar Apr May Jun  Jul  Aug Sep Oct Nov Dec

      ■ Approved    ■ Peak Month (highlighted in red/orange)
```

**Data Points Per Bar:**
- Total applications that month
- Number approved
- Number refused
- Approval rate %
- Peak month indicator

**Visual Style:**
- Green bars (#10b981) for normal months
- Red/orange bar (#ef4444, #f97316) for peak month
- Hover tooltips showing exact numbers
- Grid lines for easy reading

**Implementation:**
```typescript
<VolumeTrendsChart
  data={[
    { month: 'Jan', total: 78, approved: 65, peak: false },
    { month: 'Feb', total: 56, approved: 48, peak: false },
    { month: 'Jul', total: 95, approved: 82, peak: true },  // RED BAR
    // ...
  ]}
/>
```

---

### **Component 3: Decision Timeline by Application Type (Horizontal Bar Chart)**
**Type:** Horizontal Bar Chart
**Location:** Data dashboard section

```
Average Decision Timeline by Application Type

Householder          ████████████████████████████ 42 days

Full Planning        ████████████████████████████████████████████████████████ 84 days

Reserved Matters     ████████████████████████████████████ 56 days

Prior Approval       ██████████████ 28 days

                     0         25        50        75        100
                              Average Days
```

**Data Points Per Bar:**
- Application type name
- Average decision days
- Median decision days
- Number of applications (in tooltip)
- Color intensity based on timeline length

**Visual Style:**
- Teal/green color scheme
- Darker green = longer timelines
- Lighter green = faster decisions
- Days shown at end of each bar
- Clean, professional look

**Color Mapping:**
```typescript
const colors = {
  'Householder': '#10b981',      // Light green (fastest)
  'Prior Approval': '#059669',   // Medium green
  'Reserved Matters': '#047857', // Darker green
  'Full Planning': '#065f46',    // Darkest green (slowest)
}
```

---

### **Component 4: Comparable Applications Table**
**Type:** Data Table with Status Badges
**Location:** Comparative analysis section

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ COMPARABLE APPLICATIONS ANALYSIS                                                    │
├─────────────┬───────────────────────────┬──────────┬────────────┬──────────────────┤
│ REFERENCE   │ DESCRIPTION              │ VALUE    │ STATUS     │ DECISION DATE    │
├─────────────┼───────────────────────────┼──────────┼────────────┼──────────────────┤
│ APP/24/2165 │ 25 Bank St - Comm Tower  │ £324M    │ Approved ✅ │ 12 Aug 2024     │
│ APP/23/4789 │ Wood Wharf Phase 2       │ £567M    │ Approved ✅ │ 21 Nov 2023     │
│ APP/24/1033 │ Landmark Penside Ext     │ £189M    │ Pending ⏳  │ -               │
│ APP/23/8901 │ South Quay Plaza        │ £425M    │ Approved ✅ │ 07 Mar 2024     │
└─────────────┴───────────────────────────┴──────────┴────────────┴──────────────────┘
```

**Columns:**
1. **Reference** (Clickable link) - Blue text, monospace font
2. **Description** - Location + brief description (truncated to 80 chars)
3. **Value** - £ amount or number of dwellings
4. **Status** - Color-coded badge
5. **Decision Date** - Formatted DD Mon YYYY

**Status Badge Colors:**
- ✅ **Approved**: Green background (#dcfce7), Green text (#166534)
- ❌ **Refused**: Red background (#fee2e2), Red text (#991b1b)
- ⏳ **Pending**: Yellow background (#fef9c3), Yellow text (#854d0e)
- ⚪ **Withdrawn**: Gray background (#f3f4f6), Gray text (#374151)

**Visual Style:**
- Clean table with borders
- Hover effect on rows (light gray background)
- Alternating row colors for readability
- Mobile responsive (stack on small screens)

---

### **Component 5: Geographic Heat Map**
**Type:** Interactive Map (Choropleth/Heat Map)
**Location:** Geographic insights section

```
         {Authority Name} Planning Application Heat Map

    ┌─────────────────────────────────────────────────┐
    │                                                 │
    │     🔴 🔴                High Activity          │
    │   🔴 🟠 🟡              (Ward A: 145 apps)      │
    │     🟡 🟢 🟢                                     │
    │   🟢 🔵 🔵 🔵          Medium Activity          │
    │     🔵   🔵            (Ward B: 67 apps)        │
    │                                                 │
    │                        Low Activity            │
    │                        (Ward C: 12 apps)       │
    └─────────────────────────────────────────────────┘

    Legend:  🔵 Low (0-20)  🟢 Medium (21-50)  🟡 High (51-100)
            🟠 Very High (101-150)  🔴 Extreme (150+)
```

**Features:**
- Interactive hover tooltips
- Click to filter/focus on ward
- Color gradient based on application density
- Approval rate overlay (optional toggle)

**Data Points Per Ward:**
- Ward name
- Total applications (12 months)
- Approval rate
- Geographic coordinates (lat/lng)
- Heat intensity (0-100)

**Visual Style:**
- Blue-to-red gradient (#dbeafe → #ef4444)
- Smooth color transitions
- Interactive zoom/pan
- Legend with ranges

**Implementation:**
```typescript
<GeographicHeatMap
  data={[
    { ward: 'Central', lat: 52.48, lng: -1.89, apps: 145, intensity: 95 },
    { ward: 'North', lat: 52.52, lng: -1.91, apps: 67, intensity: 45 },
    // ...
  ]}
  legend={{ min: 0, max: 150, colors: ['#dbeafe', '#3b82f6', '#ef4444'] }}
/>
```

---

### **Component 6: Application Type Distribution (Donut Chart)**
**Type:** Donut/Pie Chart
**Location:** Application types section

```
        Application Type Distribution

              ╱───────╲
          ╱───────────────╲
        ╱─────────────────────╲
       │    Householder 35%    │───┐
       │                       │   │
       │  Full Planning 28%    │   │ Total: 1,247
       │                       │   │ Applications
       │  Other Types 37%      │   │
        ╲─────────────────────╱    │
          ╲───────────────╱         │
              ╲───────╱─────────────┘

    🟢 Householder (35%)      🔵 Full Planning (28%)
    🟣 Outline (12%)          🟡 Change of Use (15%)
    ⚫ Other (10%)
```

**Data Points Per Segment:**
- Application type name
- Count
- Percentage of total
- Approval rate (in tooltip)
- Color assignment

**Visual Style:**
- Vibrant, distinct colors for each type
- Center shows total count
- Hover shows detailed breakdown
- Clean legend below

**Segment Colors:**
```typescript
const typeColors = {
  'Householder': '#10b981',      // Green
  'Full Planning': '#3b82f6',    // Blue
  'Outline': '#8b5cf6',          // Purple
  'Change of Use': '#f59e0b',    // Yellow/Orange
  'Reserved Matters': '#ef4444', // Red
  'Listed Building': '#ec4899',  // Pink
  'Other': '#6b7280'             // Gray
}
```

---

### **Component 7: Approval Rate Trends (Line Chart)**
**Type:** Line Chart with Trend Lines
**Location:** Data dashboard section

```
          Approval Rate Trends Over Time (24 Months)

  100% ┤
       │                                        ┌─ Regional Avg (87%)
   90% ┤─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┘
       │                 ╱─╲
   80% ┤            ╱───╱   ╲─╲          ╱─╲
       │       ╱───╱             ╲    ╱──╱   ╲──╲
   70% ┤  ╱───╱                   ╲──╱             ╲  ← This Authority
       │ ╱
   60% ┤╱
       │
   50% ┴────────────────────────────────────────────────────
      Jan'24  Apr'24  Jul'24  Oct'24  Jan'25  Apr'25

      ─── This Authority    ─ ─ Regional Average    ─ · National Average
```

**Features:**
- Main line: This authority's approval rate
- Reference line 1: Regional average (dashed)
- Reference line 2: National average (dotted)
- Shaded area for variance
- Data points on hover

**Visual Style:**
- Bold line for authority (#3b82f6)
- Dashed line for regional (#10b981)
- Dotted line for national (#6b7280)
- Hover shows exact percentage + application count
- Smooth curves (not jagged)

---

### **Component 8: Agent/Developer Performance Matrix**
**Type:** Scatter Plot / Bubble Chart
**Location:** Developer insights section

```
        Agent Performance: Success Rate vs Volume

  100% ┤                    🔵 High Vol, High Success
       │                  🔵     🔵
   90% ┤               🔵    🟢
       │            🔵         🟢  🔵
   80% ┤         🟢              🟢    ← Bubble size = Avg decision time
       │      🔵      🟢    🟢
   70% ┤   🔵    🔵      🟢
       │                  🔴
   60% ┤  🔴                🔴  Low Vol, Low Success
       │
   50% ┴────────────────────────────────────────────────
       0    10    20    30    40    50    60    70
                  Application Volume (12 months)

    🟢 Residential Specialist    🔵 Commercial Specialist    🔴 Mixed Practice
```

**Quadrants:**
1. **Top Right**: High volume + High success (⭐ Star performers)
2. **Top Left**: Low volume + High success (Boutique specialists)
3. **Bottom Right**: High volume + Low success (Volume players)
4. **Bottom Left**: Low volume + Low success (New/struggling)

**Data Points Per Agent:**
- X-axis: Application count (volume)
- Y-axis: Approval rate (success)
- Bubble size: Average decision time
- Color: Specialty type
- Name (on hover)

**Visual Style:**
- Different colors for specialties
- Larger bubbles = longer decision times
- Quadrant grid lines
- Interactive tooltips
- Click to see agent detail

---

## Implementation Tech Stack

### **Chart Library Options:**

1. **Recharts** (Recommended ✅)
   - React-native
   - Good documentation
   - Responsive
   - Already used in Planning Explorer

```bash
npm install recharts
```

2. **Chart.js** (Alternative)
   - Very popular
   - More configuration options
   - Good for complex charts

3. **D3.js** (Advanced)
   - Maximum flexibility
   - Steep learning curve
   - Best for custom visualizations

### **Map Library:**

1. **Mapbox GL JS** (Recommended ✅)
   - Professional maps
   - Great heat map support
   - Free tier available

```bash
npm install mapbox-gl
```

2. **Leaflet** (Free Alternative)
   - Open source
   - Good plugin ecosystem
   - No API key needed

---

## Data Flow for Visual Components

```
┌─────────────────────────┐
│   Elasticsearch DB      │
│  (Planning Applications)│
└───────────┬─────────────┘
            │
            ↓
┌─────────────────────────┐
│  Data Pipeline Service  │
│  - Extract metrics      │
│  - Calculate trends     │
│  - Aggregate by type    │
└───────────┬─────────────┘
            │
            ↓
┌─────────────────────────┐
│  Chart Data Formatter   │
│  - Format for Recharts  │
│  - Add colors           │
│  - Calculate percentages│
└───────────┬─────────────┘
            │
            ↓
┌─────────────────────────┐
│  React Components       │
│  - VolumeTrendsChart    │
│  - TimelineChart        │
│  - ComparableTable      │
│  - HeatMap              │
│  - DonutChart           │
│  - LineChart            │
│  - ScatterPlot          │
└─────────────────────────┘
```

---

## Example: Complete Component in Page

```typescript
// frontend/src/app/planning-applications/[slug]/page.tsx

export default function AuthorityPage({ params }) {
  const { data } = useAuthorityPageData(params.slug);

  return (
    <>
      {/* Hero Section */}
      <HeroSection data={data.hero} />

      {/* Planning Recommendations */}
      <PlanningRecommendations items={data.recommendations} />

      {/* Data Visualizations Dashboard */}
      <section className="py-12 bg-gray-50">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold mb-8">Live Planning Data & Insights</h2>

          {/* Volume Trends Bar Chart */}
          <VolumeTrendsChart
            data={data.charts.volumeTrends}
            className="mb-8"
          />

          {/* Decision Timeline Horizontal Bars */}
          <DecisionTimelineChart
            data={data.charts.decisionTimeline}
            className="mb-8"
          />

          {/* Application Distribution Donut */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            <ApplicationDistributionChart data={data.charts.distribution} />
            <ApprovalRateLineChart data={data.charts.approvalTrends} />
          </div>

          {/* Geographic Heat Map */}
          <GeographicHeatMap
            data={data.charts.geographic}
            className="mb-8"
          />

          {/* Agent Performance Scatter */}
          <AgentPerformanceScatter
            data={data.charts.agentPerformance}
            className="mb-8"
          />

          {/* Comparable Applications Table */}
          <ComparableApplicationsTable
            applications={data.comparableApps}
          />
        </div>
      </section>

      {/* Rest of page... */}
    </>
  );
}
```

---

## Summary: 8 Visual Components Per Page

| # | Component | Type | Location | Data Source |
|---|-----------|------|----------|-------------|
| 1 | Planning Recommendations | Icon List | Top | AI-Generated |
| 2 | Volume Trends | Bar Chart | Dashboard | ES Monthly Agg |
| 3 | Decision Timeline | Horizontal Bars | Dashboard | ES Type Agg |
| 4 | Comparable Apps | Data Table | Comparative | ES Similar Query |
| 5 | Geographic Heat Map | Map | Geographic | ES Geo Agg |
| 6 | Type Distribution | Donut Chart | Types | ES Type Agg |
| 7 | Approval Rate Trends | Line Chart | Dashboard | ES Time Series |
| 8 | Agent Performance | Scatter Plot | Insights | ES Agent Agg |

**Total per page:** 8 interactive visualizations
**Total for 425 pages:** 3,400 visualizations
**Tech stack:** Recharts + Mapbox GL
**Mobile responsive:** Yes, all components

---

These are professional, data-rich visualizations that transform each pSEO page into an interactive planning intelligence dashboard, matching the quality shown in your screenshot!

Would you like me to:
1. **Implement the React components** for these visualizations?
2. **Complete the Elasticsearch queries** for all chart data?
3. **Continue with the content generator** and other pending components?
