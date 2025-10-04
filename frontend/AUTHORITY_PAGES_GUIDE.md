# Authority Pages User Guide

## Navigation Structure

```
/authorities                    → Authority List Page (all authorities)
/authorities/poole              → Authority Detail Page (Poole)
/authorities/manchester         → Authority Detail Page (Manchester)
/authorities/birmingham         → Authority Detail Page (Birmingham)
... (425 total authorities)
```

## Authority List Page (`/authorities`)

### Layout Overview
```
┌─────────────────────────────────────────────────────────────┐
│ UK Planning Authorities                                     │
│ Explore planning statistics and insights for 56 local...   │
│                                                             │
│ [Search authorities by name or region...] 🔍               │
└─────────────────────────────────────────────────────────────┘

Filter by Region:
[All Regions (56)] [Greater London (33)] [Greater Manchester (10)]
[West Midlands (7)] [Scotland (2)] [Wales (1)] ...

Showing 56 authorities

┌─── Greater London ────────────────────────────────────────┐
│                                                            │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────┐│
│ │ Westminster │ │   Camden    │ │  Islington  │ │Hackney││
│ │ Greater L.  │ │ Greater L.  │ │ Greater L.  │ │ ...   ││
│ │ View stats→ │ │ View stats→ │ │ View stats→ │ │       ││
│ └─────────────┘ └─────────────┘ └─────────────┘ └───────┘│
│                                                            │
│ [16 more cards in grid...]                                │
└────────────────────────────────────────────────────────────┘

┌─── Greater Manchester ────────────────────────────────────┐
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│ │ Manchester  │ │   Salford   │ │   Bolton    │ ...      │
│ └─────────────┘ └─────────────┘ └─────────────┘          │
└────────────────────────────────────────────────────────────┘

[More regions...]
```

### Features
- **Search**: Real-time filtering by authority name or region
- **Region Filters**: Click pills to filter by specific region
- **Grouped Display**: Authorities organized by region
- **Card Grid**: Responsive (1-4 columns based on screen size)
- **Hover Effects**: Cards highlight on hover
- **Click Navigation**: Cards link to detail pages

## Authority Detail Page (`/authorities/[slug]`)

### Layout Overview
```
┌─────────────────────────────────────────────────────────────┐
│                      Poole                         [Active] │
│        Planning Authority Statistics & Insights             │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  KEY METRICS (4 Cards)                                       │
│                                                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────┐│
│  │ Last 12 Mo.  │ │ Success Rate │ │ Process Time │ │Work-││
│  │     258      │ │    80.0%     │ │   11 days    │ │load ││
│  │ Total Apps   │ │ Approval Rate│ │ Avg Decision │ │1108 ││
│  └──────────────┘ └──────────────┘ └──────────────┘ └─────┘│
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  ┌─── Top Sectors ──────────┐  ┌─── Status Breakdown ─────┐ │
│  │                           │  │                          │ │
│  │ Trees          133  51.6% │  │      ┌───────────┐      │ │
│  │ ████████████████████      │  │     ╱             ╲     │ │
│  │                           │  │    │   Undecided   │    │ │
│  │ Full           101  39.1% │  │    │      251      │    │ │
│  │ ███████████████           │  │    │               │    │ │
│  │                           │  │     ╲             ╱     │ │
│  │ Outline         11   4.3% │  │      └───────────┘      │ │
│  │ ██                        │  │                          │ │
│  │                           │  │  Legend:                 │ │
│  │ [More sectors...]         │  │  ● Undecided: 251        │ │
│  │                           │  │  ● Withdrawn: 4          │ │
│  └───────────────────────────┘  └──────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│              Monthly Application Trends                       │
│                                                              │
│  Total                                                       │
│  Applications  ┌─────────────────────────────────────────┐  │
│     250        │              ╱╲                          │  │
│     200        │         ╱────  ─────╲                    │  │
│     150        │    ╱───               ───╲               │  │
│     100        │   ╱                        ────────      │  │
│      50        │  ╱                                  ╲    │  │
│       0        └─────────────────────────────────────────┘  │
│              Oct '24  Nov '24  Dec '24  Jan '25  Feb '25   │
│                                                              │
│  Legend:                                                     │
│  ─── Total Applications  ─── Permitted                      │
│  ─── Rejected           ─── Pending                         │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│              About This Authority                            │
│                                                              │
│  Total Applications (All Time)     Data Updated             │
│            5,622                   Statistics are updated    │
│                                   daily from planning portals│
└──────────────────────────────────────────────────────────────┘
```

### Components Breakdown

#### 1. Header Section
- Authority name in large text
- Active badge indicator
- Breadcrumb navigation

#### 2. Key Metrics Cards (4 cards)
```
Card 1: Total Applications (12 months)
Card 2: Approval Rate (%)
Card 3: Average Decision Days
Card 4: Active Applications Count
```

#### 3. Top Sectors Section
- Horizontal progress bars
- Sector name, count, and percentage
- Color-coded by index (8 green shades)
- Shows top 8 sectors

#### 4. Status Breakdown Chart
- Interactive Pie Chart (Recharts)
- Displays status distribution
- Labels show status name and percentage
- Legend below chart
- Tooltips on hover

#### 5. Monthly Trend Chart
- Multi-line chart (Recharts)
- 4 lines: Total, Permitted, Rejected, Pending
- X-axis: Months (formatted as "MMM YY")
- Y-axis: Application count
- Grid background
- Interactive tooltips
- Legend

#### 6. Additional Information
- Total applications (all time)
- Last updated information
- Footer with data source notes

## Color Scheme

### Primary Colors
- **Planning Green**: `#7CB342` - Main brand color
- **Dark Green**: `#388E3C` - Secondary actions
- **Accent Orange**: `#FFA726` - Highlights

### Status Colors
- **Success/Approved**: `#7CB342` (Green)
- **Warning/Pending**: `#FFCA28` (Yellow)
- **Danger/Rejected**: `#EF5350` (Red)
- **Info**: `#42A5F5` (Blue)

### Chart Colors (8 shades of green)
```
1. #7CB342  (Primary)
2. #388E3C  (Secondary)
3. #81C784  (Light)
4. #66BB6A  (Medium light)
5. #4CAF50  (Medium)
6. #43A047  (Medium dark)
7. #2E7D32  (Dark)
8. #1B5E20  (Darkest)
```

## Responsive Breakpoints

### Authority List Grid
- **Mobile** (< 768px): 1 column
- **Tablet** (768px - 1024px): 2 columns
- **Desktop** (1024px - 1280px): 3 columns
- **Large Desktop** (> 1280px): 4 columns

### Metrics Cards
- **Mobile**: 1 column (stacked)
- **Tablet**: 2 columns (2x2 grid)
- **Desktop**: 4 columns (1x4 row)

## User Interactions

### Authority List Page
1. **Search**: Type in search bar → Results filter instantly
2. **Region Filter**: Click region pill → Show only that region's authorities
3. **Clear Filters**: Click "All Regions" or "Clear Filters" button
4. **Navigate**: Click any card → Go to detail page

### Authority Detail Page
1. **Chart Hover**: Hover over chart elements → See tooltips with exact values
2. **Legend Click**: Click legend items → Toggle line visibility (LineChart)
3. **Back Navigation**: Click "Back to Authorities List" → Return to list
4. **Reload**: Refresh page → Fetch latest data from API

## Error States

### Loading
```
┌─────────────────────────────────┐
│                                 │
│         ⌛ (Spinner)             │
│                                 │
│  Loading authority statistics...│
│                                 │
└─────────────────────────────────┘
```

### Error
```
┌─────────────────────────────────┐
│  ❌ Error Loading Data           │
│                                 │
│  Failed to fetch authority      │
│  statistics. Please try again.  │
│                                 │
│  [Back to Authorities List]     │
└─────────────────────────────────┘
```

### No Results (Search)
```
┌─────────────────────────────────┐
│         😕                       │
│                                 │
│  No Authorities Found           │
│                                 │
│  Try adjusting your search or   │
│  filter criteria                │
│                                 │
│  [Clear Filters]                │
└─────────────────────────────────┘
```

## Data Requirements

### Authority List
- Authority name
- URL slug
- Region (optional)

### Authority Detail
- Authority name
- Total applications (12 months)
- Total applications (all time)
- Approval rate (0-1 decimal)
- Average decision days (float)
- Active applications count
- Top sectors array (sector, count, percentage)
- Status breakdown object (status: count)
- Monthly trend array (month, total, permitted, rejected, pending)

## Performance Considerations

### Optimization Strategies
1. **Client-Side Rendering**: Fast initial load
2. **Lazy Loading**: Charts only render when in viewport
3. **Memoization**: useMemo for expensive calculations
4. **Debounced Search**: Search waits 300ms before filtering
5. **Responsive Images**: Authority logos (if added) use Next/Image

### Future Optimizations (ISR)
- Pre-generate all 425 authority pages
- Revalidate every 3600 seconds (1 hour)
- Serve static HTML with fresh data
- Reduce API calls

## Accessibility

### Features Implemented
- Semantic HTML structure
- ARIA labels for interactive elements
- Keyboard navigation support
- Focus indicators
- Alt text for icons (when added)
- Color contrast ratios meet WCAG AA

### Future Improvements
- Skip to content link
- Screen reader announcements
- High contrast mode
- Keyboard shortcuts
- Focus trap for modals

## Browser Compatibility

### Supported Browsers
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile Safari (iOS 14+)
- ✅ Chrome Mobile (Android 10+)

### Fallbacks
- Flexbox/Grid with fallbacks
- CSS custom properties with defaults
- Progressive enhancement approach

## Testing Checklist

### Functional Testing
- ✅ Authority list loads all authorities
- ✅ Search filters authorities correctly
- ✅ Region filters work as expected
- ✅ Cards link to detail pages
- ✅ Detail page loads correct data
- ✅ Charts render without errors
- ✅ Error states display properly
- ✅ Loading states show correctly

### Visual Testing
- ✅ Layout matches design system
- ✅ Colors use Planning Explorer palette
- ✅ Typography is consistent
- ✅ Spacing follows grid system
- ✅ Responsive breakpoints work
- ✅ Hover states are visible

### Performance Testing
- ⏱️ List page loads < 1s
- ⏱️ Detail page loads < 2s
- ⏱️ Charts render < 500ms
- ⏱️ Search response < 100ms

## Future Enhancements

### Phase 2 Features
1. **Comparison Tool**: Compare 2-4 authorities side-by-side
2. **Export Data**: Download charts/data as CSV or PDF
3. **Bookmarks**: Save favorite authorities
4. **Notifications**: Alert when authority stats change significantly
5. **Map View**: Geographic visualization of authorities
6. **Advanced Filters**: Filter by approval rate ranges, application volume
7. **Authority Profiles**: Add logos, contact info, website links
8. **Historical Data**: View trends over 2-5 years
9. **Ranking System**: Rank authorities by various metrics
10. **API Documentation**: Embed API explorer for developers

### Phase 3 Features
1. **AI Insights**: ChatGPT-powered analysis of authority trends
2. **Predictive Analytics**: Forecast future approval rates
3. **Competitor Analysis**: Compare against similar authorities
4. **Custom Reports**: Build and share custom reports
5. **Real-time Updates**: WebSocket integration for live data
6. **Mobile App**: Native iOS/Android apps
7. **Team Collaboration**: Share insights with team members
8. **Email Digests**: Weekly/monthly summary emails

---

**Documentation Last Updated**: October 2, 2025
**Version**: 1.0
**Author**: Frontend Specialist - Planning Explorer Team
