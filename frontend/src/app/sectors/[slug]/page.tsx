/**
 * Sector Intelligence Page
 *
 * Comprehensive sector-specific planning intelligence with:
 * - Sector statistics dashboard
 * - 4 sector analytics charts (monthly trend, regional, authorities, agents)
 * - Filtered applications list with FreemiumGate
 * - Top Agents & Consultants league table
 * - Related content and SEO optimization
 *
 * PRD Reference: content_discovery_prd_enhanced.md lines 160-218
 * Brand Color: #7CB342 (Planning Explorer green)
 */

'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import {
  Building2,
  TrendingUp,
  FileText,
  Clock,
  MapPin,
  Users,
  DollarSign,
  Award,
  ArrowUpRight,
  ChevronRight,
} from 'lucide-react'
import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/Select'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { StatsCard, StatsCardGrid } from '@/components/discovery/StatsCard'
import { TrendChart, CHART_COLORS } from '@/components/discovery/TrendChart'
import { ApplicationsTable, Application } from '@/components/discovery/ApplicationsTable'
import { StructuredData } from '@/components/seo/StructuredData'
import { getSectorStats } from '@/lib/content-discovery-api'
import { SectorStats } from '@/types/content-discovery'

// Planning Explorer original brand color
const BRAND_COLORS = {
  primary: '#7CB342',
  secondary: '#388E3C',
  chartColors: ['#7CB342', '#388E3C', '#81C784', '#66BB6A', '#4CAF50', '#43A047', '#2E7D32', '#1B5E20'],
}

// Sector metadata for SEO and display
const SECTOR_METADATA: Record<string, { name: string; description: string; icon: string }> = {
  residential: {
    name: 'Residential',
    description: 'Residential development including houses, apartments, and conversions',
    icon: '🏠',
  },
  commercial: {
    name: 'Commercial',
    description: 'Offices, retail, and business premises development',
    icon: '🏢',
  },
  'mixed-use': {
    name: 'Mixed-Use',
    description: 'Combined residential and commercial developments',
    icon: '🏗️',
  },
  industrial: {
    name: 'Industrial',
    description: 'Warehouses, manufacturing facilities, and logistics centers',
    icon: '🏭',
  },
  retail: {
    name: 'Retail',
    description: 'Shopping centers, high street retail, and hospitality venues',
    icon: '🏪',
  },
  hospitality: {
    name: 'Hospitality',
    description: 'Hotels, restaurants, pubs, and leisure facilities',
    icon: '🏨',
  },
  education: {
    name: 'Education',
    description: 'Schools, universities, and educational facilities',
    icon: '🏫',
  },
  healthcare: {
    name: 'Healthcare',
    description: 'Hospitals, clinics, care homes, and medical facilities',
    icon: '🏥',
  },
  infrastructure: {
    name: 'Infrastructure',
    description: 'Transport, utilities, and public infrastructure',
    icon: '🚧',
  },
  'renewable-energy': {
    name: 'Renewable Energy',
    description: 'Solar, wind, and other renewable energy installations',
    icon: '⚡',
  },
}

// UK regions for filter
const UK_REGIONS = [
  'All Regions',
  'Greater London',
  'South East',
  'South West',
  'East of England',
  'West Midlands',
  'East Midlands',
  'Yorkshire and The Humber',
  'North West',
  'North East',
  'Scotland',
  'Wales',
  'Northern Ireland',
]

export default function SectorDetailPage() {
  const params = useParams()
  const slug = params?.slug as string

  const [stats, setStats] = useState<SectorStats | null>(null)
  const [applications, setApplications] = useState<Application[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filter state
  const [dateRange, setDateRange] = useState('12m')
  const [regionFilter, setRegionFilter] = useState('All Regions')
  const [authorityFilter, setAuthorityFilter] = useState('all')
  const [sortBy, setSortBy] = useState('score')

  // Get sector metadata
  const sectorMeta = SECTOR_METADATA[slug] || {
    name: slug,
    description: 'Planning applications in this sector',
    icon: '📋',
  }

  useEffect(() => {
    async function fetchData() {
      if (!slug) return

      setLoading(true)
      setError(null)

      try {
        // Fetch sector stats
        const response = await getSectorStats(slug)
        if (response.success && response.data) {
          setStats(response.data)

          // Generate mock applications for demonstration
          // In production, this would call a real API endpoint
          const mockApps = generateMockApplications(response.data)
          setApplications(mockApps)
        } else {
          setError(response.message || 'Failed to load sector statistics')
        }
      } catch (err) {
        console.error('Error fetching sector data:', err)
        setError(err instanceof Error ? err.message : 'Sector data endpoint not yet implemented')

        // For demo purposes, use mock data
        const mockStats = generateMockSectorStats(slug, sectorMeta.name)
        setStats(mockStats)
        setApplications(generateMockApplications(mockStats))
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [slug, sectorMeta.name])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Container className="py-16">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-[#7CB342] mx-auto mb-4"></div>
              <p className="text-gray-600 text-lg">Loading sector intelligence...</p>
            </div>
          </div>
        </Container>
      </div>
    )
  }

  if (error && !stats) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Container className="py-16">
          <div className="bg-white rounded-lg border border-yellow-200 p-8">
            <div className="text-center">
              <div className="text-6xl mb-4">{sectorMeta.icon}</div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Sector Data Loading</h2>
              <p className="text-gray-600 mb-6">
                The sector statistics endpoint is being implemented. Showing demonstration data below.
              </p>
              <Button asChild>
                <a href="/sectors">Back to Sectors Overview</a>
              </Button>
            </div>
          </div>
        </Container>
      </div>
    )
  }

  if (!stats) return null

  // Prepare chart data
  const monthlyTrendData = stats.monthly_trend.map((month) => ({
    month: month.month,
    Total: month.total,
    Permitted: month.permitted,
    Rejected: month.rejected,
  }))

  // Regional breakdown for chart
  const regionalChartData = stats.regional_breakdown
    .slice(0, 10)
    .map((region, idx) => ({
      name: region.region,
      count: region.count,
      'Approval Rate': Math.round(region.approval_rate * 100),
    }))

  // Top authorities chart data
  const authoritiesChartData = stats.top_authorities
    .slice(0, 10)
    .map((auth) => ({
      name: auth.authority_name.length > 20 ? auth.authority_name.substring(0, 20) + '...' : auth.authority_name,
      count: auth.count,
      'Approval Rate': Math.round(auth.approval_rate * 100),
    }))

  // Top agents chart data
  const agentsChartData = stats.top_agents
    .slice(0, 10)
    .map((agent) => ({
      name: agent.agent_name.length > 20 ? agent.agent_name.substring(0, 20) + '...' : agent.agent_name,
      Applications: agent.applications_count,
      'Success Rate': Math.round(agent.success_rate * 100),
    }))

  const approvalRatePercent = (stats.approval_rate * 100).toFixed(1)
  const growthRatePercent = (stats.growth_rate_12m * 100).toFixed(1)
  const lastUpdated = new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })

  return (
    <>
      {/* SEO Structured Data */}
      <StructuredData
        schema={{
          type: 'Dataset',
          name: `${sectorMeta.name} Planning Applications - UK Data`,
          description: `Comprehensive dataset of ${stats.total_applications_all_time.toLocaleString()} ${sectorMeta.name.toLowerCase()} planning applications across the UK. ${sectorMeta.description}. Includes approval rates, decision times, regional analysis, and market intelligence.`,
          url: `https://planningexplorer.com/sectors/${slug}`,
          creator: {
            name: 'Planning Explorer',
            url: 'https://planningexplorer.com',
          },
          datePublished: '2020-01-01',
          dateModified: new Date().toISOString().split('T')[0],
          keywords: [
            `${sectorMeta.name} planning applications`,
            'UK planning data',
            'sector intelligence',
            'approval rates',
            'planning analytics',
          ],
        }}
      />

      <div className="min-h-screen bg-gray-50">
        {/* ========================================
            HERO SECTION
            ======================================== */}
        <div className="bg-white border-b border-gray-200">
          <Container className="py-12">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div className="flex-1">
                {/* Breadcrumb */}
                <nav className="flex items-center space-x-2 text-sm text-gray-600 mb-3">
                  <a href="/" className="hover:text-[#7CB342] transition-colors">
                    Home
                  </a>
                  <ChevronRight className="w-4 h-4" />
                  <a href="/sectors" className="hover:text-[#7CB342] transition-colors">
                    Sectors
                  </a>
                  <ChevronRight className="w-4 h-4" />
                  <span className="text-gray-900 font-medium">{sectorMeta.name}</span>
                </nav>

                {/* Hero Title */}
                <div className="flex items-center gap-3 mb-3">
                  <div className="text-5xl">{sectorMeta.icon}</div>
                  <h1 className="text-4xl md:text-5xl font-bold text-gray-900">
                    {sectorMeta.name} Planning Applications
                  </h1>
                </div>

                <p className="text-lg text-gray-600 mb-2">{sectorMeta.description}</p>
                <p className="text-sm text-gray-500">Last updated: {lastUpdated}</p>
              </div>

              <Button size="lg" className="bg-[#7CB342] hover:bg-[#388E3C] shrink-0">
                Track {sectorMeta.name} Opportunities
                <ArrowUpRight className="ml-2 w-4 h-4" />
              </Button>
            </div>
          </Container>
        </div>

        {/* ========================================
            SECTOR INTELLIGENCE PANEL (6 Stats Cards)
            ======================================== */}
        <Container className="py-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
            <StatsCard
              title="Total Applications"
              value={stats.total_applications_12m.toLocaleString()}
              description="Last 12 months"
              icon={<FileText className="w-5 h-5" />}
              trend={
                stats.growth_rate_12m !== 0
                  ? {
                      value: Math.abs(Number(growthRatePercent)),
                      direction: stats.growth_rate_12m > 0 ? 'up' : 'down',
                      label: 'vs last year',
                    }
                  : undefined
              }
            />

            <StatsCard
              title="Success Rate"
              value={`${approvalRatePercent}%`}
              description="Approval rate"
              icon={<Award className="w-5 h-5" />}
              valueClassName={Number(approvalRatePercent) > 70 ? 'text-green-600' : 'text-orange-600'}
            />

            <StatsCard
              title="Avg Project Value"
              value={stats.avg_project_value ? `£${(stats.avg_project_value / 1000000).toFixed(1)}M` : 'N/A'}
              description="Average value"
              icon={<DollarSign className="w-5 h-5" />}
            />

            <StatsCard
              title="Avg Timeline"
              value={`${stats.avg_decision_days.toFixed(0)} days`}
              description="Decision time"
              icon={<Clock className="w-5 h-5" />}
            />

            <StatsCard
              title="Top Region"
              value={stats.top_region}
              description={`${stats.regional_breakdown[0]?.percentage.toFixed(1)}% of applications`}
              icon={<MapPin className="w-5 h-5" />}
            />

            <StatsCard
              title="Top Authority"
              value={stats.top_authority.length > 15 ? stats.top_authority.substring(0, 15) + '...' : stats.top_authority}
              description="Most active"
              icon={<Building2 className="w-5 h-5" />}
            />
          </div>
        </Container>

        {/* ========================================
            FILTERS & SORT (Sticky Bar)
            ======================================== */}
        <div className="sticky top-0 z-10 bg-white border-y border-gray-200 shadow-sm">
          <Container className="py-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div>
                <label className="text-xs font-medium text-gray-700 mb-1 block">Date Range</label>
                <Select value={dateRange} onValueChange={setDateRange}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="30d">Last 30 days</SelectItem>
                    <SelectItem value="3m">Last 3 months</SelectItem>
                    <SelectItem value="12m">Last 12 months</SelectItem>
                    <SelectItem value="all">All time</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-xs font-medium text-gray-700 mb-1 block">Region</label>
                <Select value={regionFilter} onValueChange={setRegionFilter}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {UK_REGIONS.map((region) => (
                      <SelectItem key={region} value={region}>
                        {region}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-xs font-medium text-gray-700 mb-1 block">Authority</label>
                <Select value={authorityFilter} onValueChange={setAuthorityFilter}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Authorities</SelectItem>
                    {stats.top_authorities.slice(0, 10).map((auth) => (
                      <SelectItem key={auth.authority_name} value={auth.authority_name.toLowerCase()}>
                        {auth.authority_name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-xs font-medium text-gray-700 mb-1 block">Sort By</label>
                <Select value={sortBy} onValueChange={setSortBy}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="score">Opportunity Score</SelectItem>
                    <SelectItem value="date">Date (Newest)</SelectItem>
                    <SelectItem value="value">Project Value</SelectItem>
                    <SelectItem value="decision_time">Decision Time</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </Container>
        </div>

        {/* ========================================
            SECTOR ANALYTICS CHARTS (4 Charts Grid)
            ======================================== */}
        <Container className="py-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Sector Analytics</h2>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 1. Monthly Trend (Line Chart) */}
            <TrendChart
              title="Monthly Trend"
              description="Application submissions over the last 12 months"
              data={monthlyTrendData}
              type="line"
              dataKeys={{
                xAxis: 'month',
                yAxis: ['Total', 'Permitted', 'Rejected'],
              }}
              height={350}
              colors={BRAND_COLORS.chartColors}
              showExport={true}
            />

            {/* 2. Regional Breakdown (Bar Chart) */}
            <TrendChart
              title="Regional Breakdown"
              description="Applications and approval rates by region"
              data={regionalChartData}
              type="bar"
              dataKeys={{
                xAxis: 'name',
                yAxis: ['count'],
              }}
              height={350}
              colors={[BRAND_COLORS.primary]}
              showExport={true}
            />

            {/* 3. Top 10 Authorities (Bar Chart) */}
            <TrendChart
              title="Top 10 Authorities"
              description="Most active planning authorities in this sector"
              data={authoritiesChartData}
              type="bar"
              dataKeys={{
                xAxis: 'name',
                yAxis: ['count'],
              }}
              height={350}
              colors={[BRAND_COLORS.secondary]}
              showExport={true}
            />

            {/* 4. Top 10 Agents/Consultants (Bar Chart) */}
            <TrendChart
              title="Top 10 Agents & Consultants"
              description="Leading planning agents and consultants by application volume"
              data={agentsChartData}
              type="bar"
              dataKeys={{
                xAxis: 'name',
                yAxis: ['Applications'],
              }}
              height={350}
              colors={[BRAND_COLORS.chartColors[2]]}
              showExport={true}
            />
          </div>
        </Container>

        {/* ========================================
            APPLICATION LIST (DataTable + FreemiumGate)
            ======================================== */}
        <Container className="py-8">
          <ApplicationsTable
            applications={applications}
            title={`${sectorMeta.name} Planning Applications`}
            description={`Showing 5 of ${stats.total_applications_12m.toLocaleString()} applications from the last 12 months`}
            showFreemiumGate={true}
            freeLimit={5}
            showMapLink={false}
          />
        </Container>

        {/* ========================================
            TOP AGENTS & CONSULTANTS SECTION
            ======================================== */}
        <Container className="py-8">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Users className="w-5 h-5 text-[#7CB342]" />
                    Top Agents & Consultants League Table
                  </CardTitle>
                  <CardDescription>
                    Leading planning professionals in the {sectorMeta.name.toLowerCase()} sector
                  </CardDescription>
                </div>
                <Badge variant="default" className="bg-[#7CB342]">
                  Professional Feature
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              {/* Desktop Table */}
              <div className="hidden md:block overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Rank
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Agent / Consultant
                      </th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Applications
                      </th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Success Rate
                      </th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Avg Decision Time
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {stats.top_agents.slice(0, 10).map((agent, index) => (
                      <tr key={agent.agent_name} className="hover:bg-gray-50 transition-colors">
                        <td className="px-4 py-4">
                          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-gray-100 text-sm font-bold text-gray-700">
                            {index + 1}
                          </div>
                        </td>
                        <td className="px-4 py-4">
                          <div className="text-sm font-medium text-gray-900">{agent.agent_name}</div>
                        </td>
                        <td className="px-4 py-4 text-right">
                          <span className="text-sm font-medium text-gray-900">
                            {agent.applications_count.toLocaleString()}
                          </span>
                        </td>
                        <td className="px-4 py-4 text-right">
                          <Badge
                            variant={agent.success_rate > 0.8 ? 'success' : agent.success_rate > 0.6 ? 'warning' : 'default'}
                            size="sm"
                          >
                            {(agent.success_rate * 100).toFixed(1)}%
                          </Badge>
                        </td>
                        <td className="px-4 py-4 text-right">
                          <span className="text-sm text-gray-600">{agent.avg_decision_days.toFixed(0)} days</span>
                        </td>
                        <td className="px-4 py-4">
                          <Button variant="outline" size="sm">
                            View Profile
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Mobile Cards */}
              <div className="md:hidden space-y-4">
                {stats.top_agents.slice(0, 10).map((agent, index) => (
                  <div key={agent.agent_name} className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className="flex items-center justify-center w-10 h-10 rounded-full bg-[#7CB342] text-white text-sm font-bold">
                          {index + 1}
                        </div>
                        <div>
                          <h4 className="text-sm font-medium text-gray-900">{agent.agent_name}</h4>
                          <p className="text-xs text-gray-500">{agent.applications_count} applications</p>
                        </div>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-3 mb-3">
                      <div>
                        <p className="text-xs text-gray-500 mb-1">Success Rate</p>
                        <Badge
                          variant={agent.success_rate > 0.8 ? 'success' : agent.success_rate > 0.6 ? 'warning' : 'default'}
                          size="sm"
                        >
                          {(agent.success_rate * 100).toFixed(1)}%
                        </Badge>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 mb-1">Avg Decision</p>
                        <span className="text-sm font-medium text-gray-900">{agent.avg_decision_days.toFixed(0)} days</span>
                      </div>
                    </div>
                    <Button variant="outline" size="sm" className="w-full">
                      View Profile
                    </Button>
                  </div>
                ))}
              </div>

              {/* CTA for more */}
              <div className="mt-6 text-center p-6 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-3">
                  Unlock full agent profiles, success metrics, and contact details
                </p>
                <Button size="sm" className="bg-[#7CB342] hover:bg-[#388E3C]">
                  Upgrade to Professional
                </Button>
              </div>
            </CardContent>
          </Card>
        </Container>

        {/* ========================================
            RELATED CONTENT SECTION
            ======================================== */}
        <Container className="py-8 pb-16">
          <Card>
            <CardHeader>
              <CardTitle>Related Content</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Related Sectors */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                    <Building2 className="w-4 h-4 text-[#7CB342]" />
                    Explore Similar Sectors
                  </h4>
                  <div className="space-y-2">
                    {getRelatedSectors(slug).map((relatedSlug) => {
                      const meta = SECTOR_METADATA[relatedSlug]
                      return (
                        <a
                          key={relatedSlug}
                          href={`/sectors/${relatedSlug}`}
                          className="flex items-center gap-2 p-2 rounded hover:bg-gray-50 transition-colors group"
                        >
                          <span className="text-2xl">{meta.icon}</span>
                          <div className="flex-1">
                            <p className="text-sm font-medium text-gray-900 group-hover:text-[#7CB342]">
                              {meta.name}
                            </p>
                            <p className="text-xs text-gray-500">{meta.description.substring(0, 50)}...</p>
                          </div>
                          <ChevronRight className="w-4 h-4 text-gray-400 group-hover:text-[#7CB342]" />
                        </a>
                      )
                    })}
                  </div>
                </div>

                {/* Top Authorities in This Sector */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-[#7CB342]" />
                    Top Authorities in {sectorMeta.name}
                  </h4>
                  <div className="space-y-2">
                    {stats.top_authorities.slice(0, 5).map((auth) => (
                      <a
                        key={auth.authority_name}
                        href={`/authorities/${auth.authority_name.toLowerCase().replace(/\s+/g, '-')}`}
                        className="flex items-center justify-between p-2 rounded hover:bg-gray-50 transition-colors group"
                      >
                        <div>
                          <p className="text-sm font-medium text-gray-900 group-hover:text-[#7CB342]">
                            {auth.authority_name}
                          </p>
                          <p className="text-xs text-gray-500">{auth.count} applications</p>
                        </div>
                        <Badge variant="default" size="sm">
                          {(auth.approval_rate * 100).toFixed(0)}% approved
                        </Badge>
                      </a>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </Container>
      </div>
    </>
  )
}

/**
 * Get related sectors based on current sector
 */
function getRelatedSectors(currentSlug: string): string[] {
  const relatedMap: Record<string, string[]> = {
    residential: ['mixed-use', 'commercial', 'infrastructure'],
    commercial: ['mixed-use', 'retail', 'industrial'],
    'mixed-use': ['residential', 'commercial', 'retail'],
    industrial: ['commercial', 'infrastructure', 'renewable-energy'],
    retail: ['commercial', 'hospitality', 'mixed-use'],
    hospitality: ['retail', 'commercial', 'mixed-use'],
    education: ['healthcare', 'infrastructure', 'residential'],
    healthcare: ['education', 'infrastructure', 'residential'],
    infrastructure: ['industrial', 'renewable-energy', 'commercial'],
    'renewable-energy': ['infrastructure', 'industrial', 'commercial'],
  }

  return relatedMap[currentSlug] || ['residential', 'commercial', 'mixed-use']
}

/**
 * Generate mock sector statistics (for demonstration when backend not ready)
 */
function generateMockSectorStats(slug: string, sectorName: string): SectorStats {
  const baseVolume = Math.floor(Math.random() * 5000) + 2000
  const approvalRate = 0.65 + Math.random() * 0.25

  return {
    sector_name: sectorName,
    sector_slug: slug,
    total_applications_12m: baseVolume,
    total_applications_all_time: baseVolume * 5,
    approval_rate: approvalRate,
    avg_project_value: Math.floor(Math.random() * 5000000) + 500000,
    avg_decision_days: Math.floor(Math.random() * 50) + 40,
    active_applications: Math.floor(baseVolume * 0.15),
    top_region: 'Greater London',
    top_authority: 'Westminster',
    regional_breakdown: [
      { region: 'Greater London', count: Math.floor(baseVolume * 0.3), percentage: 30, approval_rate: approvalRate },
      { region: 'South East', count: Math.floor(baseVolume * 0.2), percentage: 20, approval_rate: approvalRate + 0.05 },
      { region: 'North West', count: Math.floor(baseVolume * 0.15), percentage: 15, approval_rate: approvalRate - 0.03 },
      { region: 'West Midlands', count: Math.floor(baseVolume * 0.12), percentage: 12, approval_rate: approvalRate },
      { region: 'Yorkshire', count: Math.floor(baseVolume * 0.1), percentage: 10, approval_rate: approvalRate + 0.02 },
    ],
    top_authorities: [
      { authority_name: 'Westminster', count: 450, approval_rate: 0.72, avg_decision_days: 45 },
      { authority_name: 'Manchester', count: 380, approval_rate: 0.68, avg_decision_days: 52 },
      { authority_name: 'Birmingham', count: 350, approval_rate: 0.65, avg_decision_days: 48 },
      { authority_name: 'Leeds', count: 320, approval_rate: 0.70, avg_decision_days: 50 },
      { authority_name: 'Bristol', count: 290, approval_rate: 0.75, avg_decision_days: 42 },
    ],
    top_agents: [
      { agent_name: 'Smith Planning Consultants', applications_count: 156, success_rate: 0.85, avg_decision_days: 38 },
      { agent_name: 'Jones & Associates', applications_count: 142, success_rate: 0.82, avg_decision_days: 41 },
      { agent_name: 'Green Development Partners', applications_count: 128, success_rate: 0.88, avg_decision_days: 35 },
      { agent_name: 'Urban Planning Solutions', applications_count: 115, success_rate: 0.79, avg_decision_days: 43 },
      { agent_name: 'Heritage Consultancy Ltd', applications_count: 98, success_rate: 0.81, avg_decision_days: 40 },
      { agent_name: 'Modern Planning Group', applications_count: 87, success_rate: 0.76, avg_decision_days: 45 },
      { agent_name: 'Regional Planning Experts', applications_count: 76, success_rate: 0.84, avg_decision_days: 39 },
      { agent_name: 'Sustainable Design Co', applications_count: 65, success_rate: 0.86, avg_decision_days: 37 },
      { agent_name: 'Metropolitan Consultants', applications_count: 54, success_rate: 0.78, avg_decision_days: 44 },
      { agent_name: 'Civic Planning Services', applications_count: 48, success_rate: 0.80, avg_decision_days: 42 },
    ],
    monthly_trend: generateMockMonthlyTrend(baseVolume),
    growth_rate_12m: (Math.random() - 0.3) * 0.4, // -12% to +28%
  }
}

/**
 * Generate mock monthly trend data
 */
function generateMockMonthlyTrend(baseVolume: number): any[] {
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  return months.map((month) => {
    const total = Math.floor((baseVolume / 12) * (0.8 + Math.random() * 0.4))
    const permitted = Math.floor(total * (0.6 + Math.random() * 0.2))
    const rejected = Math.floor(total * (0.15 + Math.random() * 0.15))
    const pending = total - permitted - rejected

    return {
      month,
      total,
      permitted,
      rejected,
      pending,
    }
  })
}

/**
 * Generate mock applications
 */
function generateMockApplications(stats: SectorStats): Application[] {
  const addresses = [
    '123 High Street, London',
    '45 Park Avenue, Manchester',
    '78 Church Road, Birmingham',
    '12 Market Square, Leeds',
    '56 Station Road, Bristol',
    '34 Queen Street, Liverpool',
    '89 King Street, Newcastle',
    '23 Mill Lane, Sheffield',
    '67 Bridge Street, Nottingham',
    '90 Castle Road, Edinburgh',
  ]

  const statuses = ['Approved', 'Pending', 'Under Review', 'Approved', 'Approved']

  return addresses.slice(0, 10).map((address, idx) => ({
    id: `app-${idx + 1}`,
    address,
    status: statuses[idx % statuses.length],
    date: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString(),
    opportunityScore: Math.floor(Math.random() * 40) + 60,
    decisionDays: Math.floor(Math.random() * 50) + 30,
    description: `${stats.sector_name} development application`,
    agent: stats.top_agents[idx % stats.top_agents.length]?.agent_name,
    sector: stats.sector_name,
    authority: stats.top_authorities[idx % stats.top_authorities.length]?.authority_name,
  }))
}
