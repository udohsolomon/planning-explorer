'use client'

import { useEffect, useState } from 'react'
import {
  MapPin, TrendingUp, FileText, Clock, CheckCircle2, Building2,
  Users, Filter, ArrowUpRight, BarChart3, Calendar, Activity, XCircle, AlertCircle
} from 'lucide-react'
import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/Select'
import { StatsCard, StatsCardGrid } from '@/components/discovery/StatsCard'
import { ApplicationsTable } from '@/components/discovery/ApplicationsTable'
import { PlanningMap } from '@/components/maps/PlanningMap'
import { StructuredData } from '@/components/seo/StructuredData'
import { Footer } from '@/components/sections/Footer'
import { TrendChart } from '@/components/discovery/TrendChart'
import { FreemiumGate } from '@/components/discovery/FreemiumGate'
import { getAuthorityStats, getApplicationsList } from '@/lib/content-discovery-api'
import type { Application, AuthorityStats } from '@/types/content-discovery'

// Planning Explorer original brand color
const BRAND_COLOR = '#7CB342'
const COLORS = {
  primary: '#7CB342',
  secondary: '#388E3C',
  chartColors: ['#7CB342', '#388E3C', '#81C784', '#66BB6A', '#4CAF50', '#43A047', '#2E7D32', '#1B5E20'],
}

interface PlanningApplicationsClientProps {
  slug: string
}

export default function PlanningApplicationsClient({ slug }: PlanningApplicationsClientProps) {
  const [stats, setStats] = useState<AuthorityStats | null>(null)
  const [applications, setApplications] = useState<Application[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [mounted, setMounted] = useState(false)

  // Filter state
  const [dateRange, setDateRange] = useState('12m')
  const [statusFilter, setStatusFilter] = useState('all')
  const [sectorFilter, setSectorFilter] = useState('all')
  const [sortBy, setSortBy] = useState('date')

  useEffect(() => {
    setMounted(true)
  }, [])

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
              <p className="text-gray-600 text-lg">Loading planning application data...</p>
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
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Unable to Load Data</h2>
              <p className="text-gray-600 mb-6">
                {error || 'Unable to load planning application data. Please check that the authority exists.'}
              </p>
              <Button asChild>
                <a href="/">Back to Home</a>
              </Button>
            </div>
          </div>
        </Container>
      </div>
    )
  }

  const lastUpdated = new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })
  const approvalRatePercent = stats.approval_rate.toFixed(1)

  // Prepare chart data
  const approvalRateDecimal = stats.approval_rate / 100
  const approvalBreakdown = [
    { name: 'Approved', value: Math.round(stats.total_applications_12m * approvalRateDecimal), fill: COLORS.chartColors[0] },
    { name: 'Rejected', value: Math.round(stats.total_applications_12m * (1 - approvalRateDecimal)), fill: COLORS.chartColors[1] },
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

  return (
    <>
      {/* SEO Structured Data */}
      <StructuredData
        schema={[
          {
            type: 'GovernmentOrganization',
            name: stats.authority_name,
            url: `https://planningexplorer.com/planning-applications/${slug}`,
            description: `Planning authority statistics and application data for ${stats.authority_name}`,
          },
          {
            type: 'Dataset',
            name: `Planning Applications in ${stats.authority_name}`,
            description: `Comprehensive dataset of ${stats.total_applications_all_time.toLocaleString()} planning applications submitted to ${stats.authority_name}. Includes approval rates, decision times, and sector analysis.`,
            url: `https://planningexplorer.com/planning-applications/${slug}`,
            creator: {
              name: 'Planning Explorer',
              url: 'https://planningexplorer.com',
            },
            datePublished: new Date().toISOString().split('T')[0],
            keywords: [
              'planning applications',
              stats.authority_name,
              'UK planning',
              'approval rates',
              'planning statistics',
            ],
          },
        ]}
      />

      <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
        {/* ========================================
            HERO SECTION - Enhanced with gradient
            ======================================== */}
        <div className="relative bg-gradient-to-br from-[#7CB342] via-[#689F38] to-[#558B2F] text-white overflow-hidden">
          {/* Animated background pattern */}
          <div className="absolute inset-0 opacity-10">
            <div className="absolute inset-0" style={{
              backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
              backgroundSize: '40px 40px'
            }}></div>
          </div>

          <Container className="relative z-10 py-16">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
              <div className="flex-1 animate-fadeIn">
                <nav className="flex items-center space-x-2 text-sm text-white/80 mb-4">
                  <a href="/" className="hover:text-white transition-colors">Home</a>
                  <span>/</span>
                  <a href="/planning-applications" className="hover:text-white transition-colors">Planning Applications</a>
                  <span>/</span>
                  <span className="text-white font-medium">{stats.authority_name}</span>
                </nav>
                <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-4 tracking-tight">
                  Planning Applications in {stats.authority_name}
                </h1>
                <div className="flex items-center gap-3 mb-4">
                  <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold bg-white/20 backdrop-blur-sm border border-white/30">
                    <Building2 className="w-4 h-4 mr-2" />
                    Planning Authority
                  </span>
                  <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold bg-white/20 backdrop-blur-sm border border-white/30">
                    <FileText className="w-4 h-4 mr-2" />
                    {stats.total_applications_all_time.toLocaleString()} Total Applications
                  </span>
                </div>
                <p className="text-lg text-white/90 max-w-2xl mb-3">
                  Comprehensive planning intelligence, approval rates, decision times, and AI-powered insights
                </p>
                <p className="text-sm text-white/70">
                  <Calendar className="w-4 h-4 inline mr-1" />
                  Last updated: {lastUpdated}
                </p>
              </div>
              <Button size="lg" className="bg-white text-[#7CB342] hover:bg-gray-100 shrink-0 font-semibold shadow-lg hover:shadow-xl transition-all duration-300 group">
                Get Alerts for This Area
                <ArrowUpRight className="w-4 h-4 ml-2 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
              </Button>
            </div>
          </Container>
        </div>

        {/* ========================================
            KEY STATS PANEL - Enhanced cards
            ======================================== */}
        <Container className="py-8 -mt-8 relative z-20">
          <div className="bg-white rounded-2xl shadow-2xl p-8 border border-gray-100">
            <StatsCardGrid>
              <StatsCard
                title="Last 12 Months"
                value={stats.total_applications_12m.toLocaleString()}
                description="Total Applications"
                icon={<FileText className="w-5 h-5" />}
              />
              <StatsCard
                title="All Time"
                value={stats.total_applications_all_time.toLocaleString()}
                description="Total Applications"
                icon={<TrendingUp className="w-5 h-5" />}
              />
              <StatsCard
                title="Approval Rate"
                value={`${approvalRatePercent}%`}
                description="Success Rate"
                icon={<CheckCircle2 className="w-5 h-5" />}
                trend={Number(approvalRatePercent) > 70 ? { value: 5, direction: 'up' } : undefined}
              />
              <StatsCard
                title="Decision Time"
                value={stats.avg_decision_days.toFixed(0)}
                description="Avg Days to Decision"
                icon={<Clock className="w-5 h-5" />}
              />
              <StatsCard
                title="Active"
                value={stats.active_applications.toLocaleString()}
                description="Current Applications"
                icon={<AlertCircle className="w-5 h-5" />}
              />
              <StatsCard
                title="Top Sector"
                value={stats.top_sectors[0]?.sector || 'N/A'}
                description={stats.top_sectors[0] ? `${stats.top_sectors[0].percentage.toFixed(1)}% of applications` : 'No data available'}
                icon={<Building2 className="w-5 h-5" />}
              />
            </StatsCardGrid>
          </div>
        </Container>

        {/* ========================================
            CHARTS & ANALYTICS SECTION
            ======================================== */}
        <Container className="py-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <TrendChart
              title="Monthly Application Trends"
              description="Application submissions and decisions over the last 12 months"
              data={monthlyTrendData}
              type="line"
              height={350}
              dataKeys={{
                xAxis: 'month',
                yAxis: ['Total', 'Permitted', 'Rejected', 'Pending']
              }}
              colors={COLORS.chartColors}
              showExport={true}
              className="shadow-lg border border-gray-100"
            />

            <TrendChart
              title="Approval Breakdown"
              description="Approval vs rejection rate for the last 12 months"
              data={approvalBreakdown}
              type="pie"
              height={350}
              dataKeys={{
                nameKey: 'name',
                valueKey: 'value'
              }}
              colors={COLORS.chartColors}
              showExport={true}
              className="shadow-lg border border-gray-100"
            />
          </div>

          <TrendChart
            title="Top 10 Sectors by Volume"
            description="Most common application types in the last 12 months"
            data={topSectorsData}
            type="bar"
            height={400}
            dataKeys={{
              xAxis: 'name',
              yAxis: ['count']
            }}
            colors={COLORS.chartColors}
            showExport={true}
            className="shadow-lg border border-gray-100"
          />
        </Container>

        {/* ========================================
            INTERACTIVE MAP SECTION (Placeholder for now)
            ======================================== */}
        <Container className="py-8">
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
                  <MapPin className="w-8 h-8 text-[#7CB342]" />
                  Application Map
                </h2>
                <p className="text-gray-600">
                  Geographic visualization of planning applications in {stats.authority_name}
                </p>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Activity className="w-4 h-4" />
                <span>Live data</span>
              </div>
            </div>

            {applications.length > 0 ? (
              <div className="rounded-xl overflow-hidden border border-gray-200 shadow-sm">
                <PlanningMap
                  applications={applications}
                  center={applications[0]?.location?.coordinates ? [applications[0].location.coordinates[1], applications[0].location.coordinates[0]] : [51.5074, -0.1278]}
                  zoom={12}
                  height="600px"
                  showBasemapSwitcher={true}
                  showLegend={true}
                  className="w-full"
                />
              </div>
            ) : (
              <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl border border-gray-200 p-16 text-center">
                <MapPin className="w-16 h-16 text-gray-300 mx-auto mb-4 animate-pulse" />
                <p className="text-gray-600 mb-2 font-medium">Map visualization coming soon</p>
                <p className="text-sm text-gray-500">
                  The applications map will show all planning applications for {stats.authority_name}
                </p>
              </div>
            )}
          </div>
        </Container>

        {/* ========================================
            FILTERS & SORT (Sticky)
            ======================================== */}
        <div className="sticky top-0 z-30 bg-white/95 backdrop-blur-sm border-y border-gray-200 shadow-md">
          <Container className="py-4">
            <div className="flex items-center gap-3 mb-3">
              <Filter className="w-5 h-5 text-[#7CB342]" />
              <h3 className="text-sm font-semibold text-gray-900">Filter & Sort Applications</h3>
            </div>
            <div className="flex flex-col md:flex-row gap-3">
              <div className="flex-1 grid grid-cols-2 md:grid-cols-4 gap-3">
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
                  <label className="text-xs font-medium text-gray-700 mb-1 block">Status</label>
                  <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Statuses</SelectItem>
                      <SelectItem value="approved">Approved</SelectItem>
                      <SelectItem value="pending">Pending</SelectItem>
                      <SelectItem value="rejected">Rejected</SelectItem>
                      <SelectItem value="withdrawn">Withdrawn</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-xs font-medium text-gray-700 mb-1 block">Sector</label>
                  <Select value={sectorFilter} onValueChange={setSectorFilter}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Sectors</SelectItem>
                      {stats.top_sectors.slice(0, 10).map((sector) => (
                        <SelectItem key={sector.sector} value={sector.sector.toLowerCase()}>
                          {sector.sector}
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
                      <SelectItem value="date">Date (Newest)</SelectItem>
                      <SelectItem value="score">Opportunity Score</SelectItem>
                      <SelectItem value="type">Application Type</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>
          </Container>
        </div>

        {/* ========================================
            APPLICATION LIST (DataTable)
            ======================================== */}
        <Container className="py-8">
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
                    <BarChart3 className="w-8 h-8 text-[#7CB342]" />
                    Recent Planning Applications
                  </h2>
                  <p className="text-gray-600">
                    Showing {applications.length > 0 ? '5 of ' : ''}{stats.total_applications_12m.toLocaleString()} applications from the last 12 months
                  </p>
                </div>
              </div>
            </div>

            {applications.length > 0 ? (
              <>
                <ApplicationsTable
                  applications={applications.slice(0, 5)}
                />
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

        {/* ========================================
            RELATED CONTENT SECTION
            ======================================== */}
        <Container className="py-8 pb-16">
          <div className="bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-lg border border-gray-100 p-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-[#7CB342]" />
              Related Content
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="group">
                <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <Building2 className="w-4 h-4 text-[#7CB342]" />
                  Top Sectors
                </h4>
                <p className="text-sm text-gray-600 mb-4">
                  View applications by sector type
                </p>
                <ul className="space-y-2">
                  {stats.top_sectors.slice(0, 3).map((sector) => (
                    <li key={sector.sector}>
                      <a
                        href={`/sectors/${sector.sector.toLowerCase().replace(/\s+/g, '-')}`}
                        className="text-sm text-[#7CB342] hover:text-[#689F38] hover:underline flex items-center gap-1 group-hover:gap-2 transition-all"
                      >
                        {sector.sector} ({sector.count})
                        <ArrowUpRight className="w-3 h-3" />
                      </a>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="group">
                <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-[#7CB342]" />
                  Nearby Authorities
                </h4>
                <p className="text-sm text-gray-600 mb-4">
                  Explore neighboring planning authorities
                </p>
                <ul className="space-y-2">
                  <li>
                    <a href="/planning-applications/manchester" className="text-sm text-[#7CB342] hover:text-[#689F38] hover:underline flex items-center gap-1 group-hover:gap-2 transition-all">
                      Manchester
                      <ArrowUpRight className="w-3 h-3" />
                    </a>
                  </li>
                  <li>
                    <a href="/planning-applications/birmingham" className="text-sm text-[#7CB342] hover:text-[#689F38] hover:underline flex items-center gap-1 group-hover:gap-2 transition-all">
                      Birmingham
                      <ArrowUpRight className="w-3 h-3" />
                    </a>
                  </li>
                  <li>
                    <a href="/planning-applications/london" className="text-sm text-[#7CB342] hover:text-[#689F38] hover:underline flex items-center gap-1 group-hover:gap-2 transition-all">
                      London
                      <ArrowUpRight className="w-3 h-3" />
                    </a>
                  </li>
                </ul>
              </div>

              <div className="group">
                <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <Users className="w-4 h-4 text-[#7CB342]" />
                  Popular Features
                </h4>
                <p className="text-sm text-gray-600 mb-4">
                  Explore more planning tools
                </p>
                <ul className="space-y-2">
                  <li>
                    <a href="/search" className="text-sm text-[#7CB342] hover:text-[#689F38] hover:underline flex items-center gap-1 group-hover:gap-2 transition-all">
                      Advanced Search
                      <ArrowUpRight className="w-3 h-3" />
                    </a>
                  </li>
                  <li>
                    <a href="/alerts" className="text-sm text-[#7CB342] hover:text-[#689F38] hover:underline flex items-center gap-1 group-hover:gap-2 transition-all">
                      Planning Alerts
                      <ArrowUpRight className="w-3 h-3" />
                    </a>
                  </li>
                  <li>
                    <a href="/reports" className="text-sm text-[#7CB342] hover:text-[#689F38] hover:underline flex items-center gap-1 group-hover:gap-2 transition-all">
                      Custom Reports
                      <ArrowUpRight className="w-3 h-3" />
                    </a>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </Container>
      </div>

      {/* Global Footer */}
      <Footer />

      {/* Add CSS animations */}
      {mounted && (
        <style jsx global>{`
          @keyframes fadeIn {
            from {
              opacity: 0;
              transform: translateY(20px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }

          .animate-fadeIn {
            animation: fadeIn 0.6s ease-out forwards;
          }

          @keyframes pulse {
            0%, 100% {
              opacity: 1;
            }
            50% {
              opacity: 0.5;
            }
          }

          .animate-pulse {
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
          }
        `}</style>
      )}
    </>
  )
}
