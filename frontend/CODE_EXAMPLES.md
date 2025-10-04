# Content Discovery Code Examples

## Quick Reference for Common Patterns

### 1. Fetching Authority Statistics

```typescript
import { getAuthorityStats } from '@/lib/content-discovery-api'
import { AuthorityStats } from '@/types/content-discovery'

async function fetchData() {
  try {
    const response = await getAuthorityStats('poole')
    if (response.success && response.data) {
      const stats: AuthorityStats = response.data
      console.log('Approval Rate:', stats.approval_rate)
      console.log('Total Apps:', stats.total_applications_12m)
    }
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}
```

### 2. Using in a Component

```tsx
'use client'

import { useEffect, useState } from 'react'
import { getAuthorityStats } from '@/lib/content-discovery-api'
import { AuthorityStats } from '@/types/content-discovery'

export default function MyComponent() {
  const [stats, setStats] = useState<AuthorityStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadData() {
      const response = await getAuthorityStats('manchester')
      if (response.success) {
        setStats(response.data)
      }
      setLoading(false)
    }
    loadData()
  }, [])

  if (loading) return <div>Loading...</div>
  if (!stats) return <div>No data</div>

  return (
    <div>
      <h1>{stats.authority_name}</h1>
      <p>Approval Rate: {(stats.approval_rate * 100).toFixed(1)}%</p>
    </div>
  )
}
```

### 3. Creating a Metric Card

```tsx
import { Card, CardHeader, CardContent, CardDescription, CardTitle } from '@/components/ui/Card'

function MetricCard({ title, value, description }: {
  title: string
  value: string | number
  description: string
}) {
  return (
    <Card>
      <CardHeader>
        <CardDescription>{title}</CardDescription>
        <CardTitle className="text-3xl">{value}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-gray-600">{description}</p>
      </CardContent>
    </Card>
  )
}

// Usage
<MetricCard
  title="Last 12 Months"
  value={stats.total_applications_12m.toLocaleString()}
  description="Total Applications"
/>
```

### 4. Building a Pie Chart (Recharts)

```tsx
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'

const COLORS = ['#7CB342', '#388E3C', '#81C784', '#66BB6A']

function StatusPieChart({ statusBreakdown }: { statusBreakdown: Record<string, number> }) {
  const data = Object.entries(statusBreakdown).map(([status, count]) => ({
    name: status,
    value: count,
  }))

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, percent }: any) => `${name} (${(percent * 100).toFixed(0)}%)`}
          outerRadius={80}
          fill="#8884d8"
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  )
}
```

### 5. Building a Line Chart (Recharts)

```tsx
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

function MonthlyTrendChart({ monthlyTrend }: { monthlyTrend: MonthlyTrend[] }) {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={monthlyTrend}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis
          dataKey="month"
          stroke="#666"
          tick={{ fill: '#666', fontSize: 12 }}
          tickFormatter={(value) => {
            const [year, month] = value.split('-')
            const date = new Date(parseInt(year), parseInt(month) - 1)
            return date.toLocaleDateString('en-GB', { month: 'short', year: '2-digit' })
          }}
        />
        <YAxis stroke="#666" tick={{ fill: '#666', fontSize: 12 }} />
        <Tooltip
          contentStyle={{ backgroundColor: 'white', border: '1px solid #ddd', borderRadius: '8px' }}
        />
        <Legend />
        <Line type="monotone" dataKey="total" stroke="#7CB342" strokeWidth={2} name="Total" />
        <Line type="monotone" dataKey="permitted" stroke="#388E3C" strokeWidth={2} name="Permitted" />
        <Line type="monotone" dataKey="rejected" stroke="#EF5350" strokeWidth={2} name="Rejected" />
        <Line type="monotone" dataKey="pending" stroke="#FFCA28" strokeWidth={2} name="Pending" />
      </LineChart>
    </ResponsiveContainer>
  )
}
```

### 6. Progress Bars for Top Sectors

```tsx
function SectorProgressBars({ topSectors }: { topSectors: SectorBreakdown[] }) {
  const COLORS = ['#7CB342', '#388E3C', '#81C784', '#66BB6A', '#4CAF50']

  return (
    <div className="space-y-4">
      {topSectors.map((sector, index) => (
        <div key={sector.sector}>
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm font-medium text-gray-700">{sector.sector}</span>
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">{sector.count}</span>
              <Badge variant="outline" size="sm">
                {sector.percentage.toFixed(1)}%
              </Badge>
            </div>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="h-2 rounded-full transition-all"
              style={{
                width: `${sector.percentage}%`,
                backgroundColor: COLORS[index % COLORS.length],
              }}
            />
          </div>
        </div>
      ))}
    </div>
  )
}
```

### 7. Search and Filter Authorities

```tsx
'use client'

import { useState, useMemo } from 'react'
import { getAllAuthorities, searchAuthorities } from '@/lib/content-discovery-api'
import { Input } from '@/components/ui/Input'

export default function AuthoritySearch() {
  const [searchQuery, setSearchQuery] = useState('')
  const allAuthorities = useMemo(() => getAllAuthorities(), [])

  const filteredAuthorities = useMemo(() => {
    return searchAuthorities(searchQuery, allAuthorities)
  }, [searchQuery, allAuthorities])

  return (
    <div>
      <Input
        type="text"
        placeholder="Search authorities..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
      />
      <div className="mt-4">
        <p>{filteredAuthorities.length} results</p>
        {filteredAuthorities.map((auth) => (
          <div key={auth.slug}>{auth.name}</div>
        ))}
      </div>
    </div>
  )
}
```

### 8. Loading State Component

```tsx
function LoadingState() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-16 px-4">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-planning-primary mx-auto mb-4"></div>
            <p className="text-gray-600 text-lg">Loading authority statistics...</p>
          </div>
        </div>
      </div>
    </div>
  )
}
```

### 9. Error State Component

```tsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card'

function ErrorState({ error, onRetry }: { error: string; onRetry?: () => void }) {
  return (
    <Card className="border-red-200 bg-red-50">
      <CardHeader>
        <CardTitle className="text-red-600">Error Loading Data</CardTitle>
        <CardDescription className="text-red-500">{error}</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-gray-600 mb-4">
          Please try again or contact support if the issue persists.
        </p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="inline-flex items-center justify-center rounded-md bg-planning-primary px-4 py-2 text-sm font-medium text-white hover:bg-planning-secondary transition-colors"
          >
            Try Again
          </button>
        )}
      </CardContent>
    </Card>
  )
}
```

### 10. Region Filter Pills

```tsx
function RegionFilterPills({
  regions,
  selectedRegion,
  onSelect,
  authorities,
}: {
  regions: string[]
  selectedRegion: string
  onSelect: (region: string) => void
  authorities: AuthorityListItem[]
}) {
  return (
    <div className="flex flex-wrap gap-2">
      <button
        onClick={() => onSelect('all')}
        className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
          selectedRegion === 'all'
            ? 'bg-planning-primary text-white'
            : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
        }`}
      >
        All Regions ({authorities.length})
      </button>
      {regions.map((region) => {
        const count = authorities.filter((a) => a.region === region).length
        return (
          <button
            key={region}
            onClick={() => onSelect(region)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
              selectedRegion === region
                ? 'bg-planning-primary text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            {region} ({count})
          </button>
        )
      })}
    </div>
  )
}
```

### 11. Authority Card Component

```tsx
import Link from 'next/link'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'

function AuthorityCard({ authority }: { authority: AuthorityListItem }) {
  return (
    <Link href={`/authorities/${authority.slug}`}>
      <Card className="h-full hover:shadow-lg transition-shadow cursor-pointer hover:border-planning-primary">
        <CardHeader>
          <div className="flex items-start justify-between gap-2">
            <CardTitle className="text-base leading-tight">{authority.name}</CardTitle>
            <svg
              className="w-5 h-5 text-planning-primary flex-shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5l7 7-7 7"
              />
            </svg>
          </div>
        </CardHeader>
        <CardContent>
          {authority.region && (
            <Badge variant="outline" size="sm">
              {authority.region}
            </Badge>
          )}
          <p className="text-xs text-gray-500 mt-2">Click to view detailed statistics</p>
        </CardContent>
      </Card>
    </Link>
  )
}
```

### 12. Custom Hook for Authority Data

```tsx
import { useState, useEffect } from 'react'
import { getAuthorityStats } from '@/lib/content-discovery-api'
import { AuthorityStats } from '@/types/content-discovery'

function useAuthorityStats(slug: string) {
  const [stats, setStats] = useState<AuthorityStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchStats() {
      if (!slug) return

      setLoading(true)
      setError(null)

      try {
        const response = await getAuthorityStats(slug)
        if (response.success && response.data) {
          setStats(response.data)
        } else {
          setError(response.message || 'Failed to load authority statistics')
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An unexpected error occurred')
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [slug])

  return { stats, loading, error }
}

// Usage
function MyComponent({ slug }: { slug: string }) {
  const { stats, loading, error } = useAuthorityStats(slug)

  if (loading) return <LoadingState />
  if (error) return <ErrorState error={error} />
  if (!stats) return null

  return <div>{stats.authority_name}</div>
}
```

### 13. Formatting Utilities

```typescript
// Format percentage
function formatPercentage(value: number): string {
  return `${(value * 100).toFixed(1)}%`
}

// Format number with commas
function formatNumber(value: number): string {
  return value.toLocaleString()
}

// Format date from YYYY-MM to readable format
function formatMonth(monthString: string): string {
  const [year, month] = monthString.split('-')
  const date = new Date(parseInt(year), parseInt(month) - 1)
  return date.toLocaleDateString('en-GB', { month: 'long', year: 'numeric' })
}

// Create URL slug from name
function createSlug(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

// Usage
const approvalRate = formatPercentage(stats.approval_rate) // "80.0%"
const totalApps = formatNumber(stats.total_applications_12m) // "1,234"
const monthName = formatMonth('2024-10') // "October 2024"
const slug = createSlug('Bournemouth, Christchurch and Poole') // "bournemouth-christchurch-and-poole"
```

### 14. Responsive Grid Layout

```tsx
function AuthorityGrid({ authorities }: { authorities: AuthorityListItem[] }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {authorities.map((authority) => (
        <AuthorityCard key={authority.slug} authority={authority} />
      ))}
    </div>
  )
}
```

### 15. Empty State

```tsx
function EmptyState({ onClearFilters }: { onClearFilters: () => void }) {
  return (
    <Card>
      <CardContent className="py-12 text-center">
        <svg
          className="w-16 h-16 text-gray-300 mx-auto mb-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <h3 className="text-lg font-semibold text-gray-700 mb-2">No Authorities Found</h3>
        <p className="text-gray-600 mb-4">Try adjusting your search or filter criteria</p>
        <button
          onClick={onClearFilters}
          className="inline-flex items-center justify-center rounded-md bg-planning-primary px-4 py-2 text-sm font-medium text-white hover:bg-planning-secondary transition-colors"
        >
          Clear Filters
        </button>
      </CardContent>
    </Card>
  )
}
```

## Color Palette Reference

```typescript
const COLORS = {
  primary: '#7CB342',        // Planning Green
  secondary: '#388E3C',      // Dark Green
  accent: '#FFA726',         // Orange
  danger: '#EF5350',         // Red
  info: '#42A5F5',           // Blue
  warning: '#FFCA28',        // Yellow
  chartColors: [
    '#7CB342',  // Primary
    '#388E3C',  // Secondary
    '#81C784',  // Light
    '#66BB6A',  // Medium Light
    '#4CAF50',  // Medium
    '#43A047',  // Medium Dark
    '#2E7D32',  // Dark
    '#1B5E20',  // Darkest
  ],
}
```

## TypeScript Type Definitions

```typescript
// Full type definitions from content-discovery.ts

export interface SectorBreakdown {
  sector: string
  count: number
  percentage: number
}

export interface StatusBreakdown {
  [status: string]: number
}

export interface MonthlyTrend {
  month: string       // Format: "YYYY-MM"
  total: number
  permitted: number
  rejected: number
  pending: number
}

export interface AuthorityStats {
  authority_name: string
  total_applications_12m: number
  total_applications_all_time: number
  approval_rate: number              // 0-1 decimal (0.8 = 80%)
  avg_decision_days: number
  active_applications: number
  top_sectors: SectorBreakdown[]
  status_breakdown: StatusBreakdown
  monthly_trend: MonthlyTrend[]
}

export interface AuthorityStatsResponse {
  success: boolean
  data: AuthorityStats
  message?: string
}

export interface AuthorityListItem {
  name: string
  slug: string
  region?: string
  total_applications?: number
  approval_rate?: number
}
```

## API Endpoints

```typescript
// Authority stats endpoint
GET /api/v1/stats/authority/{slug}

// Example: Get Poole statistics
GET /api/v1/stats/authority/poole

// Response:
{
  "success": true,
  "data": {
    "authority_name": "Poole",
    "total_applications_12m": 258,
    "total_applications_all_time": 5622,
    "approval_rate": 0.8,
    "avg_decision_days": 11.0,
    "active_applications": 1108,
    "top_sectors": [...],
    "status_breakdown": {...},
    "monthly_trend": [...]
  }
}
```

## Testing Examples

```typescript
// Test fetching authority stats
import { getAuthorityStats } from '@/lib/content-discovery-api'

describe('Authority Stats API', () => {
  test('should fetch Poole statistics', async () => {
    const response = await getAuthorityStats('poole')
    expect(response.success).toBe(true)
    expect(response.data.authority_name).toBe('Poole')
    expect(response.data.approval_rate).toBeGreaterThan(0)
  })

  test('should handle invalid slug', async () => {
    const response = await getAuthorityStats('invalid-slug')
    expect(response.success).toBe(false)
  })
})
```

---

**Last Updated**: October 2, 2025
**Version**: 1.0
