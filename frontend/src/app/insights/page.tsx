/**
 * Insights Hub Page
 * PRD Reference: content_discovery_prd_enhanced.md lines 262-340
 * Features: 4 Dashboard Tabs (Authorities, Regions, Sectors, Agents)
 * Layout: Hero → Tabs → Filters → Stats → Trend Chart → League Table → Related Insights
 */

'use client'

import { useState, useEffect } from 'react'
import { Container } from '@/components/ui/Container'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/Tabs'
import { StatsCard, StatsCardGrid } from '@/components/discovery/StatsCard'
import { TrendChart, CHART_COLORS } from '@/components/discovery/TrendChart'
import { LeagueTable, LeagueTableRow } from '@/components/discovery/LeagueTable'
import { StructuredData, DatasetSchema } from '@/components/seo/StructuredData'
import { Select } from '@/components/ui/Select'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import {
  Building2,
  MapPin,
  Briefcase,
  Users,
  TrendingUp,
  Clock,
  CheckCircle,
  Activity,
  Download,
} from 'lucide-react'

// Dashboard types
type DashboardType = 'authorities' | 'regions' | 'sectors' | 'agents'

// Filter types
interface Filters {
  dateRange: '30d' | '3m' | '12m' | 'all'
  status: 'all' | 'approved' | 'pending' | 'rejected'
  sortBy: 'volume' | 'success_rate' | 'avg_time'
}

// API Response types (to be implemented by backend)
interface TrendsData {
  overview: {
    total_applications: number
    approval_rate: number
    avg_decision_days: number
    active_applications: number
  }
  trend: Array<{
    month: string
    applications: number
    approved: number
    avg_days: number
  }>
  leagueTable: LeagueTableRow[]
  topPerformers: Array<{
    name: string
    slug: string
    metric: number
  }>
}

export default function InsightsHubPage() {
  const [activeTab, setActiveTab] = useState<DashboardType>('authorities')
  const [filters, setFilters] = useState<Filters>({
    dateRange: '12m',
    status: 'all',
    sortBy: 'volume',
  })
  const [isLoading, setIsLoading] = useState(false)
  const [data, setData] = useState<TrendsData | null>(null)

  // Fetch data when tab or filters change
  useEffect(() => {
    fetchTrendsData()
  }, [activeTab, filters])

  const fetchTrendsData = async () => {
    setIsLoading(true)
    try {
      // TODO: Replace with actual API call to backend
      // const response = await fetch(`/api/stats/trends?type=${activeTab}&dateRange=${filters.dateRange}&status=${filters.status}&sortBy=${filters.sortBy}`)
      // const result = await response.json()
      // setData(result)

      // Mock data for now (graceful fallback)
      setData(getMockData(activeTab))
    } catch (error) {
      console.error('Failed to fetch trends data:', error)
      setData(getMockData(activeTab))
    } finally {
      setIsLoading(false)
    }
  }

  const getTabIcon = (type: DashboardType) => {
    const icons = {
      authorities: <Building2 className="h-4 w-4 mr-2" />,
      regions: <MapPin className="h-4 w-4 mr-2" />,
      sectors: <Briefcase className="h-4 w-4 mr-2" />,
      agents: <Users className="h-4 w-4 mr-2" />,
    }
    return icons[type]
  }

  const getTabLabel = (type: DashboardType) => {
    const labels = {
      authorities: 'Authorities',
      regions: 'Regions',
      sectors: 'Sectors',
      agents: 'Agents',
    }
    return labels[type]
  }

  const handleFilterChange = (key: keyof Filters, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value }))
  }

  const handleExportData = () => {
    // TODO: Implement CSV export functionality
    console.log('Exporting data...')
  }

  // Schema.org Dataset markup
  const datasetSchema: DatasetSchema = {
    type: 'Dataset',
    name: 'UK Planning Applications Insights Hub',
    description: `Comprehensive planning data insights for ${getTabLabel(activeTab)} across the UK. Updated monthly with approval rates, decision times, and application volumes.`,
    url: 'https://planningexplorer.com/insights',
    creator: {
      name: 'Planning Explorer',
      url: 'https://planningexplorer.com',
    },
    datePublished: '2025-01-01',
    dateModified: new Date().toISOString().split('T')[0],
    keywords: ['uk planning', 'planning applications', 'planning data', 'approval rates', activeTab],
    license: 'https://planningexplorer.com/terms',
  }

  return (
    <>
      <StructuredData schema={datasetSchema} />

      <div className="min-h-screen bg-gray-50">
        {/* Hero Section */}
        <div className="bg-white border-b border-gray-200">
          <Container>
            <div className="py-12 md:py-16">
              <div className="max-w-3xl">
                <h1 className="text-4xl md:text-5xl font-bold text-planning-primary mb-4">
                  Planning Insights Hub
                </h1>
                <p className="text-xl text-gray-600 mb-2">
                  Comprehensive UK planning intelligence across authorities, regions, sectors, and agents
                </p>
                <p className="text-sm text-gray-500">
                  Last Updated: {new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })}
                </p>
              </div>
            </div>
          </Container>
        </div>

        <Container>
          <div className="py-8">
            {/* Dashboard Type Tabs */}
            <Tabs defaultValue="authorities" value={activeTab} onValueChange={(val) => setActiveTab(val as DashboardType)}>
              <div className="mb-8">
                <TabsList className="w-full md:w-auto">
                  <TabsTrigger value="authorities">
                    {getTabIcon('authorities')}
                    <span className="hidden sm:inline">{getTabLabel('authorities')}</span>
                    <span className="sm:hidden">Auth</span>
                  </TabsTrigger>
                  <TabsTrigger value="regions">
                    {getTabIcon('regions')}
                    <span className="hidden sm:inline">{getTabLabel('regions')}</span>
                    <span className="sm:hidden">Regions</span>
                  </TabsTrigger>
                  <TabsTrigger value="sectors">
                    {getTabIcon('sectors')}
                    <span className="hidden sm:inline">{getTabLabel('sectors')}</span>
                    <span className="sm:hidden">Sectors</span>
                  </TabsTrigger>
                  <TabsTrigger value="agents">
                    {getTabIcon('agents')}
                    <span className="hidden sm:inline">{getTabLabel('agents')}</span>
                    <span className="sm:hidden">Agents</span>
                  </TabsTrigger>
                </TabsList>
              </div>

              {/* Global Filters - Sticky on scroll */}
              <div className="sticky top-0 z-10 bg-gray-50 pb-6">
                <Card>
                  <CardContent className="p-4">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <Select
                        label="Date Range"
                        value={filters.dateRange}
                        onChange={(e) => handleFilterChange('dateRange', e.target.value)}
                      >
                        <option value="30d">Last 30 Days</option>
                        <option value="3m">Last 3 Months</option>
                        <option value="12m">Last 12 Months</option>
                        <option value="all">All Time</option>
                      </Select>

                      <Select
                        label="Status"
                        value={filters.status}
                        onChange={(e) => handleFilterChange('status', e.target.value)}
                      >
                        <option value="all">All Status</option>
                        <option value="approved">Approved Only</option>
                        <option value="pending">Pending Only</option>
                        <option value="rejected">Rejected Only</option>
                      </Select>

                      <Select
                        label="Sort By"
                        value={filters.sortBy}
                        onChange={(e) => handleFilterChange('sortBy', e.target.value)}
                      >
                        <option value="volume">Application Volume</option>
                        <option value="success_rate">Success Rate</option>
                        <option value="avg_time">Avg Decision Time</option>
                      </Select>

                      <div className="flex items-end">
                        <Button
                          variant="outline"
                          size="md"
                          onClick={handleExportData}
                          className="w-full"
                        >
                          <Download className="h-4 w-4 mr-2" />
                          Export
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Tab Content */}
              <TabsContent value={activeTab}>
                <div className="space-y-8">
                  {/* Overview Stats (4 cards) */}
                  <StatsCardGrid>
                    <StatsCard
                      title="Total Applications"
                      value={data?.overview.total_applications || 0}
                      icon={<Activity className="h-6 w-6" />}
                      trend={{ value: 12, direction: 'up', label: 'vs last period' }}
                    />
                    <StatsCard
                      title="Approval Rate"
                      value={`${data?.overview.approval_rate || 0}%`}
                      icon={<CheckCircle className="h-6 w-6" />}
                      trend={{ value: 5, direction: 'up' }}
                    />
                    <StatsCard
                      title="Avg Decision Time"
                      value={`${data?.overview.avg_decision_days || 0} days`}
                      icon={<Clock className="h-6 w-6" />}
                      trend={{ value: 3, direction: 'down', label: 'faster' }}
                    />
                    <StatsCard
                      title="Active Applications"
                      value={data?.overview.active_applications || 0}
                      icon={<TrendingUp className="h-6 w-6" />}
                    />
                  </StatsCardGrid>

                  {/* Trend Visualization - Large 12-month chart */}
                  <TrendChart
                    title={`12-Month ${getTabLabel(activeTab)} Trend`}
                    description={`Application volume and approval rates over the last 12 months`}
                    data={data?.trend || []}
                    type="line"
                    dataKeys={{
                      xAxis: 'month',
                      yAxis: ['applications', 'approved'],
                    }}
                    height={400}
                    colors={[CHART_COLORS.primary, CHART_COLORS.success]}
                    showExport
                  />

                  {/* League Table */}
                  <LeagueTable
                    data={data?.leagueTable || []}
                    type={activeTab}
                    title={`Top ${getTabLabel(activeTab)}`}
                    description={`Ranked by ${filters.sortBy === 'volume' ? 'application volume' : filters.sortBy === 'success_rate' ? 'success rate' : 'average decision time'}`}
                    isLoading={isLoading}
                  />

                  {/* Related Insights Section */}
                  <Card>
                    <CardContent className="p-6">
                      <h3 className="text-xl font-bold text-gray-900 mb-4">Top Performers</h3>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {data?.topPerformers.slice(0, 3).map((performer, index) => (
                          <div
                            key={index}
                            className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                          >
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-2xl font-bold text-planning-primary">#{index + 1}</span>
                              <TrendingUp className="h-5 w-5 text-green-600" />
                            </div>
                            <h4 className="font-semibold text-gray-900 mb-1">{performer.name}</h4>
                            <p className="text-sm text-gray-600">
                              {performer.metric.toLocaleString()} applications
                            </p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </Container>
      </div>
    </>
  )
}

// Mock data generator (fallback until backend is ready)
function getMockData(type: DashboardType): TrendsData {
  const mockOverview = {
    total_applications: 12543,
    approval_rate: 72.5,
    avg_decision_days: 56,
    active_applications: 3421,
  }

  const mockTrend = Array.from({ length: 12 }, (_, i) => ({
    month: new Date(2024, i, 1).toLocaleDateString('en-GB', { month: 'short' }),
    applications: Math.floor(Math.random() * 2000) + 500,
    approved: Math.floor(Math.random() * 1400) + 300,
    avg_days: Math.floor(Math.random() * 30) + 40,
  }))

  const names = {
    authorities: ['Westminster City Council', 'Birmingham City Council', 'Manchester City Council', 'Leeds City Council', 'Liverpool City Council'],
    regions: ['London', 'South East', 'North West', 'West Midlands', 'Yorkshire'],
    sectors: ['Residential', 'Commercial', 'Mixed-use', 'Industrial', 'Retail'],
    agents: ['Savills', 'Knight Frank', 'JLL', 'CBRE', 'Colliers'],
  }

  const mockLeagueTable: LeagueTableRow[] = names[type].map((name, i) => ({
    rank: i + 1,
    name,
    slug: name.toLowerCase().replace(/\s+/g, '-'),
    total_applications: Math.floor(Math.random() * 5000) + 1000,
    percentage: parseFloat((Math.random() * 20 + 5).toFixed(1)),
    success_rate: parseFloat((Math.random() * 30 + 60).toFixed(1)),
    avg_decision_days: Math.floor(Math.random() * 40) + 40,
    trend: ['up', 'down', 'stable'][Math.floor(Math.random() * 3)] as 'up' | 'down' | 'stable',
    trend_percentage: Math.floor(Math.random() * 20) + 1,
  }))

  const mockTopPerformers = names[type].slice(0, 3).map((name) => ({
    name,
    slug: name.toLowerCase().replace(/\s+/g, '-'),
    metric: Math.floor(Math.random() * 5000) + 2000,
  }))

  return {
    overview: mockOverview,
    trend: mockTrend,
    leagueTable: mockLeagueTable,
    topPerformers: mockTopPerformers,
  }
}
