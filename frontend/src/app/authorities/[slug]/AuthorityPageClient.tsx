'use client'

import { useEffect, useState } from 'react'
import { Calendar, TrendingUp, FileText, Clock, CheckCircle2, XCircle, AlertCircle } from 'lucide-react'
import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/Select'
import { StatsCard, StatsCardGrid } from '@/components/discovery/StatsCard'
import { TrendChart } from '@/components/discovery/TrendChart'
import { ApplicationsTable } from '@/components/discovery/ApplicationsTable'
import { FreemiumGate } from '@/components/discovery/FreemiumGate'
import { StructuredData } from '@/components/seo/StructuredData'
import { getAuthorityStats, getApplicationsList } from '@/lib/content-discovery-api'
import { AuthorityStats, Application } from '@/types/content-discovery'

// Planning Explorer original color palette
const COLORS = {
  primary: '#7CB342',
  secondary: '#388E3C',
  chartColors: ['#7CB342', '#388E3C', '#81C784', '#66BB6A', '#4CAF50', '#43A047', '#2E7D32', '#1B5E20'],
}

interface AuthorityPageClientProps {
  slug: string
}

export default function AuthorityPageClient({ slug }: AuthorityPageClientProps) {
  const [stats, setStats] = useState<AuthorityStats | null>(null)
  const [applications, setApplications] = useState<Application[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filter state
  const [dateRange, setDateRange] = useState('12m')
  const [statusFilter, setStatusFilter] = useState('all')
  const [sectorFilter, setSectorFilter] = useState('all')
  const [sortBy, setSortBy] = useState('date')

  useEffect(() => {
    async function fetchData() {
      if (!slug) return

      setLoading(true)
      setError(null)

      try {
        // Fetch authority stats
        const statsResponse = await getAuthorityStats(slug)
        if (statsResponse.success && statsResponse.data) {
          setStats(statsResponse.data)
        } else {
          setError(statsResponse.message || 'Failed to load authority statistics')
          setLoading(false)
          return
        }

        // Fetch applications list
        try {
          const appsResponse = await getApplicationsList(slug, {
            status: statusFilter !== 'all' ? statusFilter : undefined,
            sector: sectorFilter !== 'all' ? sectorFilter : undefined,
            sortBy: sortBy,
          })
          if (appsResponse.success && appsResponse.data) {
            setApplications(appsResponse.data.applications)
          }
        } catch (appError) {
          console.warn('Applications list not available:', appError)
          // Continue even if applications list fails
        }
      } catch (err) {
        console.error('Error fetching authority data:', err)
        setError(err instanceof Error ? err.message : 'An unexpected error occurred')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [slug, dateRange, statusFilter, sectorFilter, sortBy])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Container className="py-16">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-[#7CB342] mx-auto mb-4"></div>
              <p className="text-gray-600 text-lg">Loading authority statistics...</p>
            </div>
          </div>
        </Container>
      </div>
    )
  }

  if (error || !stats) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Container className="py-16">
          <div className="bg-white rounded-lg border border-red-200 p-8">
            <div className="text-center">
              <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Data</h2>
              <p className="text-gray-600 mb-6">
                {error || 'Unable to load authority statistics. Please check that the authority slug is correct.'}
              </p>
              <Button asChild>
                <a href="/authorities">Back to Authorities List</a>
              </Button>
            </div>
          </div>
        </Container>
      </div>
    )
  }

  // Prepare chart data
  const approvalBreakdown = [
    { name: 'Approved', value: Math.round(stats.total_applications_12m * stats.approval_rate), fill: COLORS.chartColors[0] },
    { name: 'Rejected', value: Math.round(stats.total_applications_12m * (1 - stats.approval_rate)), fill: COLORS.chartColors[1] },
  ]

  const topSectorsData = stats.top_sectors.slice(0, 10).map((sector, idx) => ({
    name: sector.sector,
    count: sector.count,
    fill: COLORS.chartColors[idx % COLORS.chartColors.length],
  }))

  const monthlyTrendData = stats.monthly_trend.map(month => ({
    month: month.month,
    Total: month.total,
    Permitted: month.permitted,
    Rejected: month.rejected,
    Pending: month.pending,
  }))

  const approvalRatePercent = (stats.approval_rate * 100).toFixed(1)
  const lastUpdated = new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })

  return (
    <>
      {/* SEO Structured Data */}
      <StructuredData
        type="GovernmentOrganization"
        data={{
          name: stats.authority_name,
          url: `https://planningexplorer.com/authorities/${slug}`,
          dataset: {
            '@type': 'Dataset',
            name: `Planning Applications in ${stats.authority_name}`,
            description: `Comprehensive dataset of ${stats.total_applications_all_time.toLocaleString()} planning applications submitted to ${stats.authority_name}. Includes approval rates, decision times, and sector analysis.`,
            temporalCoverage: '2020/..',
            spatialCoverage: {
              '@type': 'Place',
              name: stats.authority_name,
            },
          },
        }}
      />

      <div className="min-h-screen bg-gray-50">
        {/* Hero Section */}
        <div className="bg-white border-b border-gray-200">
          <Container className="py-12">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div className="flex-1">
                <nav className="flex items-center space-x-2 text-sm text-gray-600 mb-3">
                  <a href="/" className="hover:text-[#7CB342] transition-colors">Home</a>
                  <span>/</span>
                  <a href="/authorities" className="hover:text-[#7CB342] transition-colors">Authorities</a>
                  <span>/</span>
                  <span className="text-gray-900 font-medium">{stats.authority_name}</span>
                </nav>
                <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-3">
                  Planning Applications in {stats.authority_name}
                </h1>
                <p className="text-lg text-gray-600">
                  Comprehensive planning data and statistics for {stats.authority_name}
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  Last updated: {lastUpdated}
                </p>
              </div>
              <Button size="lg" className="bg-[#7CB342] hover:bg-[#388E3C] shrink-0">
                Track Applications in This Area
              </Button>
            </div>
          </Container>
        </div>

        {/* Stats Grid */}
        <Container className="py-8">
          <StatsCardGrid columns={6}>
            <StatsCard
              title="Last 12 Months"
              value={stats.total_applications_12m.toLocaleString()}
              description="Total Applications"
              icon={<FileText className="w-5 h-5" />}
              variant="default"
            />
            <StatsCard
              title="All Time"
              value={stats.total_applications_all_time.toLocaleString()}
              description="Total Applications"
              icon={<TrendingUp className="w-5 h-5" />}
              variant="default"
            />
            <StatsCard
              title="Approval Rate"
              value={`${approvalRatePercent}%`}
              description="Success Rate"
              icon={<CheckCircle2 className="w-5 h-5" />}
              variant="success"
            />
            <StatsCard
              title="Decision Time"
              value={stats.avg_decision_days.toFixed(0)}
              description="Avg Days to Decision"
              icon={<Clock className="w-5 h-5" />}
              variant="default"
            />
            <StatsCard
              title="Active"
              value={stats.active_applications.toLocaleString()}
              description="Current Applications"
              icon={<AlertCircle className="w-5 h-5" />}
              variant="warning"
            />
            <StatsCard
              title="Top Sector"
              value={stats.top_sectors[0]?.sector || 'N/A'}
              description={`${stats.top_sectors[0]?.percentage.toFixed(1)}% of applications`}
              icon={<Calendar className="w-5 h-5" />}
              variant="info"
            />
          </StatsCardGrid>
        </Container>

        {/* Charts Section */}
        <Container className="py-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <TrendChart
              title="Monthly Application Trends"
              description="Application submissions and decisions over the last 12 months"
              data={monthlyTrendData}
              chartType="line"
              height={350}
              xAxisKey="month"
              lines={[
                { dataKey: 'Total', stroke: COLORS.chartColors[0], name: 'Total' },
                { dataKey: 'Permitted', stroke: COLORS.chartColors[1], name: 'Permitted' },
              ]}
            />

            <TrendChart
              title="Approval Breakdown"
              description="Approval vs rejection rate for the last 12 months"
              data={approvalBreakdown}
              chartType="pie"
              height={350}
            />
          </div>

          <TrendChart
            title="Top 10 Sectors by Volume"
            description="Most common application types in the last 12 months"
            data={topSectorsData}
            chartType="bar"
            height={400}
            xAxisKey="name"
            bars={[{ dataKey: 'count', fill: COLORS.chartColors[0], name: 'Applications' }]}
          />
        </Container>

        {/* Applications Table */}
        <Container className="py-8">
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-2xl font-bold text-gray-900">Recent Applications</h2>
              <p className="text-sm text-gray-600 mt-1">
                Showing {applications.length > 0 ? '5 of ' : ''}{stats.total_applications_12m.toLocaleString()} applications from the last 12 months
              </p>
            </div>

            {applications.length > 0 ? (
              <>
                <ApplicationsTable applications={applications.slice(0, 5)} />
                <FreemiumGate
                  totalCount={stats.total_applications_12m}
                  visibleCount={5}
                  itemType="applications"
                  ctaText={`See all ${stats.total_applications_12m.toLocaleString()} applications`}
                />
              </>
            ) : (
              <div className="p-12 text-center">
                <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-600 mb-2">Applications list not available</p>
                <p className="text-sm text-gray-500">
                  This feature requires the backend applications endpoint to be implemented.
                </p>
              </div>
            )}
          </div>
        </Container>
      </div>
    </>
  )
}
