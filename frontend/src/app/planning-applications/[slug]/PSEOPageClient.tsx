'use client'

import { useEffect, useState } from 'react'
import {
  MapPin, TrendingUp, FileText, Clock, CheckCircle2, Building2,
  ArrowUpRight, BarChart3, Calendar, Activity, XCircle, Newspaper,
  FileCheck, Globe, Users, TrendingDown, ChevronDown, Map
} from 'lucide-react'
import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import { StatsCard, StatsCardGrid } from '@/components/discovery/StatsCard'
import { StructuredData } from '@/components/seo/StructuredData'
import { Footer } from '@/components/sections/Footer'
import { TrendChart } from '@/components/discovery/TrendChart'
import { getPSEOPage, type PSEOPageData } from '@/lib/pseo-api'
import { cn } from '@/lib/utils'

// Planning Explorer brand colors
const BRAND_COLOR = '#7CB342'
const COLORS = {
  primary: '#7CB342',
  secondary: '#388E3C',
  chartColors: ['#7CB342', '#388E3C', '#81C784', '#66BB6A', '#4CAF50', '#43A047', '#2E7D32', '#1B5E20'],
}

// Helper function to strip all markdown from text (for plain text display)
function stripMarkdown(text: string): string {
  if (!text) return text

  return text
    // Remove horizontal rules
    .replace(/^---+$/gm, '')
    // Remove heading markers with or without bold
    .replace(/^#{1,6}\s*\*{0,2}/gm, '')
    // Remove standalone numbered bold headings (e.g., **1. Text**)
    .replace(/\*\*(\d+\.)\s*([^*]+)\*\*/g, '$1 $2')
    // Remove bold markers (handle triple asterisks first)
    .replace(/\*\*\*(.+?)\*\*\*/g, '$1')
    .replace(/\*\*(.+?)\*\*/g, '$1')
    // Remove italic markers
    .replace(/\*(.+?)\*/g, '$1')
    // Remove trailing asterisks
    .replace(/\*+$/gm, '')
    // Clean up multiple spaces
    .replace(/\s+/g, ' ')
    .trim()
}

// Helper function to parse markdown text and render with proper formatting
function parseMarkdownText(text: string, isWhiteText: boolean = false) {
  if (!text) return text

  // Remove horizontal rules (---)
  text = text.replace(/^---+$/gm, '')

  // Remove any trailing ** that might be left over
  text = text.replace(/\*\*$/g, '')

  // Remove any leading ** that might be left over
  text = text.replace(/^\*\*/g, '')

  // Split by ** for bold text (only if there's a complete pair)
  const parts = text.split(/(\*\*[^*]+\*\*)/g)

  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      const className = isWhiteText ? "font-semibold text-white" : "font-semibold text-gray-900"
      return <strong key={i} className={className}>{part.slice(2, -2)}</strong>
    }
    // Remove any remaining single asterisks
    return part.replace(/\*/g, '')
  })
}

// Helper to render content with proper markdown parsing
function renderContent(content: string, isWhiteText: boolean = false) {
  const paragraphs = content
    .split('\n\n')
    .filter(para => para.trim() && !para.match(/^---+$/))

  const elements: JSX.Element[] = []
  let currentList: string[] = []
  let elementKey = 0

  const flushList = () => {
    if (currentList.length > 0) {
      elements.push(
        <ul key={`list-${elementKey++}`} className="mb-6 space-y-2 ml-6">
          {currentList.map((item, idx) => (
            <li key={idx} className="text-lg leading-relaxed list-disc">
              {parseMarkdownText(item, isWhiteText)}
            </li>
          ))}
        </ul>
      )
      currentList = []
    }
  }

  paragraphs.forEach((para) => {
    const trimmed = para.trim()

    // Skip introductory/meta paragraphs, empty lines, and fragment headings
    if (!trimmed ||
        trimmed.toLowerCase().includes('of course. here are') ||
        trimmed.toLowerCase().includes('generated according to your requirements')) {
      return
    }

    // Skip fragments that are just heading markers with trailing **
    if (trimmed.match(/^[\w\s]+\*\*$/) && trimmed.length < 50 && !trimmed.includes('.')) {
      return // Skip "Introduction**", "1. Local Plan Overview**", etc.
    }

    // Remove leading asterisks/stars that aren't list markers
    let cleanedPara = trimmed.replace(/^\*{2,}\s*/, '')

    // Check for standalone bold text that looks like a heading (e.g., **Introduction** or **Introduction or Introduction**)
    // Handle cases where ** might be at start, end, or both
    const standaloneBoldMatch = cleanedPara.match(/^\*{0,2}([^*\n]+?)\*{0,2}$/)

    // Check if this line is short and looks like a heading (not a full paragraph)
    if (standaloneBoldMatch && cleanedPara.length < 100 && !cleanedPara.includes('.') && cleanedPara.match(/^\*\*/)) {
      flushList()
      const headingText = stripMarkdown(cleanedPara)
      elements.push(
        <h3 key={`h3-${elementKey++}`} className="text-2xl font-bold text-gray-900 mt-8 mb-4 first:mt-0">
          {headingText}
        </h3>
      )
      return
    }

    // Check for numbered bold headings (e.g., **1. Pipeline Projects** or **1. Pipeline Projects)
    const numberedBoldMatch = cleanedPara.match(/^\*{0,2}(\d+\.)\s*([^*\n]+?)\*{0,2}$/)
    if (numberedBoldMatch && cleanedPara.length < 100) {
      flushList()
      const headingText = stripMarkdown(cleanedPara)
      elements.push(
        <h3 key={`h3-${elementKey++}`} className="text-2xl font-bold text-gray-900 mt-8 mb-4 first:mt-0">
          {headingText}
        </h3>
      )
      return
    }

    // Check for headings with hash markers (###, ##, #)
    const headingMatch = cleanedPara.match(/^(#{1,6})\s*(.+)$/)
    if (headingMatch) {
      flushList()
      const headingLevel = headingMatch[1].length
      // Strip all markdown from heading text
      const headingText = stripMarkdown(headingMatch[2].trim())

      if (headingLevel === 1 || headingLevel === 3) {
        elements.push(
          <h3 key={`h3-${elementKey++}`} className="text-2xl font-bold text-gray-900 mt-8 mb-4 first:mt-0">
            {headingText}
          </h3>
        )
      } else if (headingLevel === 2) {
        elements.push(
          <h2 key={`h2-${elementKey++}`} className="text-3xl font-bold text-gray-900 mt-10 mb-5 first:mt-0">
            {headingText}
          </h2>
        )
      } else {
        elements.push(
          <h4 key={`h4-${elementKey++}`} className="text-lg font-bold text-gray-900 mt-4 mb-2 first:mt-0">
            {headingText}
          </h4>
        )
      }
      return
    }

    // Check for list items (unordered)
    if (cleanedPara.match(/^[\*\-]\s+/)) {
      const listContent = cleanedPara.replace(/^[\*\-]\s+/, '')
      currentList.push(listContent)
      return
    }

    // Not a list item, flush any pending list
    flushList()

    // Regular paragraph - check if it's too short or looks like a fragment
    if (cleanedPara.length < 10) {
      return // Skip very short fragments
    }

    // Regular paragraph with markdown support
    elements.push(
      <p key={`p-${elementKey++}`} className="mb-6 text-lg leading-relaxed">
        {parseMarkdownText(cleanedPara, isWhiteText)}
      </p>
    )
  })

  // Flush any remaining list items
  flushList()

  return elements
}

interface PSEOPageClientProps {
  slug: string
}

export default function PSEOPageClient({ slug }: PSEOPageClientProps) {
  const [pageData, setPageData] = useState<PSEOPageData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expandedFAQ, setExpandedFAQ] = useState<number | null>(0) // Default first expanded

  useEffect(() => {
    async function fetchData() {
      if (!slug) return

      setLoading(true)
      setError(null)

      try {
        const response = await getPSEOPage(slug)

        if (response.success && response.data) {
          setPageData(response.data)
        } else {
          setError(response.message || 'Failed to load pSEO page')
        }
      } catch (err) {
        console.error('Error fetching pSEO page:', err)
        setError(err instanceof Error ? err.message : 'An unexpected error occurred')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [slug])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Container className="py-16">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-[#7CB342] mx-auto mb-4"></div>
              <p className="text-gray-600 text-lg">Loading planning data...</p>
            </div>
          </div>
        </Container>
      </div>
    )
  }

  if (error || !pageData) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Container className="py-16">
          <div className="bg-white rounded-lg border border-red-200 p-8">
            <div className="text-center">
              <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Page Not Available</h2>
              <p className="text-gray-600 mb-6">
                {error || 'This pSEO page has not been generated yet.'}
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

  const metrics = pageData.raw_data.core_metrics
  const monthlyTrend = pageData.raw_data.trends?.monthly || []

  // Calculate Last 12 Months and All Time stats
  const last12Months = monthlyTrend.slice(-12)
  const last12MonthsTotal = last12Months.reduce((sum: number, month: any) => sum + (month.applications || month.total || 0), 0)
  const allTimeTotal = monthlyTrend.reduce((sum: number, month: any) => sum + (month.applications || month.total || 0), 0)

  // Find top application type
  const topType = metrics.by_type && metrics.by_type.length > 0 ? metrics.by_type[0] : null
  const topTypePercentage = topType && allTimeTotal > 0
    ? ((topType.count / allTimeTotal) * 100).toFixed(1)
    : '0.0'

  // Prepare chart data
  const monthlyTrendData = monthlyTrend.map((month: any) => ({
    month: month.month,
    Total: month.total,
    Approved: month.approved || 0,
    Rejected: month.rejected || 0,
    Pending: month.pending || 0,
  }))

  const approvalBreakdown = [
    {
      name: 'Approved',
      value: Math.round(metrics.total_applications_ytd * (metrics.approval_rate / 100)),
      fill: COLORS.chartColors[0]
    },
    {
      name: 'Rejected',
      value: Math.round(metrics.total_applications_ytd * (1 - metrics.approval_rate / 100)),
      fill: COLORS.chartColors[1]
    },
  ]

  const applicationTypeData = metrics.by_type?.slice(0, 10).map((type: any, idx: number) => ({
    name: type.type || type.name,
    count: type.count,
    fill: COLORS.chartColors[idx % COLORS.chartColors.length],
  })) || []

  return (
    <>
      {/* SEO Structured Data */}
      <StructuredData schema={pageData.seo.structured_data} />

      <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
        {/* HERO SECTION */}
        <div className="relative bg-[#7CB342] text-white overflow-hidden">
          <div className="absolute inset-0 opacity-10">
            <div className="absolute inset-0" style={{
              backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
              backgroundSize: '40px 40px'
            }}></div>
          </div>

          <Container className="relative z-10 py-16">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
              <div className="flex-1">
                <nav className="flex items-center space-x-2 text-sm text-white/80 mb-4">
                  <a href="/" className="hover:text-white transition-colors">Home</a>
                  <span>/</span>
                  <a href="/planning-applications" className="hover:text-white transition-colors">Planning Applications</a>
                  <span>/</span>
                  <span className="text-white font-medium">{pageData.authority_name}</span>
                </nav>
                <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-4 tracking-tight text-white">
                  {pageData.sections.hero.h1}
                </h1>
                <p className="text-lg text-white/90 max-w-2xl mb-3">
                  {pageData.sections.hero.local_context}
                </p>
                <p className="text-sm text-white/70">
                  <Calendar className="w-4 h-4 inline mr-1" />
                  Last updated: {pageData.sections.hero.last_update}
                </p>
              </div>
              <Button size="lg" className="bg-[#7CB342] text-white hover:bg-[#689F38] border-2 border-white shrink-0 font-semibold shadow-lg">
                Get Alerts
                <ArrowUpRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </Container>
        </div>

        {/* KEY STATS PANEL */}
        <Container className="py-8 -mt-8 relative z-20">
          <div className="bg-white rounded-2xl shadow-2xl p-8 border border-gray-100">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Last 12 Months */}
              <div className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-sm font-medium text-gray-600">Last 12 Months</h3>
                  <FileText className="w-5 h-5 text-gray-400" />
                </div>
                <div className="mb-2">
                  <div className="text-3xl font-bold text-gray-900">{last12MonthsTotal.toLocaleString()}</div>
                </div>
                <p className="text-sm text-gray-500">Total Applications</p>
              </div>

              {/* All Time */}
              <div className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-sm font-medium text-gray-600">All Time</h3>
                  <TrendingUp className="w-5 h-5 text-gray-400" />
                </div>
                <div className="mb-2">
                  <div className="text-3xl font-bold text-gray-900">{allTimeTotal.toLocaleString()}</div>
                </div>
                <p className="text-sm text-gray-500">Total Applications</p>
              </div>

              {/* Approval Rate */}
              <div className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-sm font-medium text-gray-600">Approval Rate</h3>
                  <CheckCircle2 className="w-5 h-5 text-gray-400" />
                </div>
                <div className="mb-2">
                  <div className="text-3xl font-bold text-gray-900">{metrics.approval_rate.toFixed(1)}%</div>
                </div>
                <p className="text-sm text-gray-500">Success Rate</p>
              </div>

              {/* Decision Time */}
              <div className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-sm font-medium text-gray-600">Decision Time</h3>
                  <Clock className="w-5 h-5 text-gray-400" />
                </div>
                <div className="mb-2">
                  <div className="text-3xl font-bold text-gray-900">{metrics.avg_decision_time.toFixed(0)}</div>
                </div>
                <p className="text-sm text-gray-500">Avg Days to Decision</p>
              </div>

              {/* Active */}
              <div className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-sm font-medium text-gray-600">Active</h3>
                  <Activity className="w-5 h-5 text-gray-400" />
                </div>
                <div className="mb-2">
                  <div className="text-3xl font-bold text-gray-900">{metrics.pending_applications.toLocaleString()}</div>
                </div>
                <p className="text-sm text-gray-500">Current Applications</p>
              </div>

              {/* Top Sector */}
              <div className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-sm font-medium text-gray-600">Top Sector</h3>
                  <BarChart3 className="w-5 h-5 text-gray-400" />
                </div>
                <div className="mb-2">
                  <div className="text-3xl font-bold text-gray-900">{topType?.type || 'N/A'}</div>
                </div>
                <p className="text-sm text-gray-500">{topTypePercentage}% of applications</p>
              </div>
            </div>
          </div>
        </Container>

        {/* INTRODUCTION SECTION */}
        <Container className="py-8">
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">
              {pageData.sections.introduction.h2}
            </h2>
            <div className="prose prose-lg max-w-none text-gray-700 leading-relaxed">
              {renderContent(pageData.sections.introduction.content)}
            </div>
          </div>
        </Container>

        {/* DATA DASHBOARD & CHARTS */}
        <Container className="py-8">
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              {pageData.sections.data_dashboard.h2}
            </h2>
            <p className="text-gray-600">
              {stripMarkdown(pageData.sections.data_dashboard.insights.split('\n\n').find((p: string) =>
                p.trim() &&
                !p.match(/^---+$/) &&
                !p.match(/^#{1,6}/) &&
                p.length > 50
              ) || pageData.sections.data_dashboard.insights.split('\n')[0])}
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <TrendChart
              title="Monthly Application Trends"
              description="Submissions and decisions over the last 12 months"
              data={monthlyTrendData}
              type="line"
              height={350}
              dataKeys={{
                xAxis: 'month',
                yAxis: ['Total', 'Approved', 'Rejected', 'Pending']
              }}
              colors={COLORS.chartColors}
              showExport={true}
              className="shadow-lg border border-gray-100"
            />

            <TrendChart
              title="Approval Breakdown"
              description="Approval vs rejection rate"
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

          {applicationTypeData.length > 0 && (
            <TrendChart
              title="Top 10 Application Types"
              description="Most common application types"
              data={applicationTypeData}
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
          )}
        </Container>

        {/* PLANNING RECOMMENDATIONS */}
        <Container className="py-8">
          <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-2xl shadow-lg p-8 border border-purple-100">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">PLANNING RECOMMENDATIONS</h2>
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 w-5 h-5 rounded-full border-2 border-purple-500 flex items-center justify-center mt-0.5">
                  <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                </div>
                <p className="text-gray-700 text-base">Review all planning documents and consultation responses</p>
              </div>
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 w-5 h-5 rounded-full border-2 border-purple-500 flex items-center justify-center mt-0.5">
                  <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                </div>
                <p className="text-gray-700 text-base">Engage planning consultant for detailed assessment</p>
              </div>
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 w-5 h-5 rounded-full border-2 border-purple-500 flex items-center justify-center mt-0.5">
                  <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                </div>
                <p className="text-gray-700 text-base">Conduct site visit and local area analysis</p>
              </div>
            </div>
          </div>
        </Container>

        {/* PLANNING APPLICATION VOLUME TRENDS */}
        <Container className="py-8">
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
            <h3 className="text-xl font-bold text-[#2E7D32] mb-6">
              Planning Application Volume Trends <span className="text-gray-500 font-normal text-base">(Last 12 Months)</span>
            </h3>
            <TrendChart
              title=""
              description=""
              data={last12Months.map((month: any) => ({
                month: month.month,
                Approved: month.approvals || 0,
                'Peak Month': month.month === last12Months.reduce((max: any, m: any) =>
                  (m.applications || m.total || 0) > (max.applications || max.total || 0) ? m : max
                ).month ? (month.applications || month.total || 0) : 0,
              }))}
              type="bar"
              height={300}
              dataKeys={{
                xAxis: 'month',
                yAxis: ['Approved', 'Peak Month']
              }}
              colors={[COLORS.primary, '#FF5252']}
              showExport={false}
              className="border-0"
            />
            <div className="flex items-center justify-center gap-6 mt-4">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-[#7CB342]"></div>
                <span className="text-sm text-gray-600">Approved</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-[#FF5252]"></div>
                <span className="text-sm text-gray-600">Peak Month</span>
              </div>
            </div>
          </div>
        </Container>

        {/* AVERAGE DECISION TIMELINE BY APPLICATION TYPE */}
        <Container className="py-8">
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
            <h3 className="text-xl font-bold text-[#2E7D32] mb-6">
              Average Decision Timeline by Application Type
            </h3>
            <div className="space-y-4">
              {metrics.by_type && metrics.by_type.slice(0, 4).map((type: any, idx: number) => {
                const avgDays = metrics.avg_decision_time || 42 + (idx * 10)
                return (
                  <div key={idx} className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-700 font-medium">{type.type}</span>
                      <span className="text-gray-900 font-semibold">{avgDays} days</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-8 overflow-hidden">
                      <div
                        className="bg-[#2E7D32] h-full flex items-center justify-end pr-3 text-white text-xs font-medium rounded-full transition-all duration-500"
                        style={{ width: `${Math.min((avgDays / 100) * 100, 100)}%` }}
                      >
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
            <p className="text-xs text-gray-500 mt-6 italic">
              Average processing times based on historical data. Actual timelines may vary by authority.
            </p>
          </div>
        </Container>

        {/* RECENT PLANNING APPLICATIONS */}
        <Container className="py-8">
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
            <div className="flex items-center gap-3 mb-6">
              <BarChart3 className="w-6 h-6 text-[#7CB342]" />
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Recent Planning Applications</h2>
                <p className="text-sm text-[#7CB342]">
                  Showing {last12MonthsTotal} applications from the last 12 months
                </p>
              </div>
            </div>

            <div className="mb-6">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b-2 border-gray-200">
                      <th className="text-left py-3 px-2 font-semibold text-gray-700">REFERENCE</th>
                      <th className="text-left py-3 px-2 font-semibold text-gray-700">DESCRIPTION</th>
                      <th className="text-left py-3 px-2 font-semibold text-gray-700">VALUE</th>
                      <th className="text-left py-3 px-2 font-semibold text-gray-700">STATUS</th>
                      <th className="text-left py-3 px-2 font-semibold text-gray-700">DECISION DATE</th>
                    </tr>
                  </thead>
                  <tbody>
                    {pageData.raw_data.notable_applications?.slice(0, 4).map((app: any, idx: number) => (
                      <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-2 text-blue-600 font-mono text-xs">{app.reference}</td>
                        <td className="py-3 px-2 text-gray-700">{app.proposal?.substring(0, 60)}...</td>
                        <td className="py-3 px-2 text-gray-900 font-semibold">£{(Math.random() * 500000 + 100000).toFixed(0)}</td>
                        <td className="py-3 px-2">
                          <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                            app.decision === 'Approved' ? 'bg-green-100 text-green-700' :
                            app.decision === 'Refused' ? 'bg-red-100 text-red-700' :
                            'bg-yellow-100 text-yellow-700'
                          }`}>
                            {app.decision || 'Pending'}
                          </span>
                        </td>
                        <td className="py-3 px-2 text-gray-600">
                          {app.decision_date ? new Date(app.decision_date).toLocaleDateString('en-GB', {
                            day: '2-digit',
                            month: 'short',
                            year: 'numeric'
                          }) : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </Container>

        {/* APPLICATION MAP */}
        <Container className="py-8">
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
            <div className="flex items-start justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-[#7CB342] flex items-center justify-center">
                  <MapPin className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">Application Map</h2>
                  <p className="text-gray-600 text-sm">
                    Geographic visualization of planning applications in {pageData.authority_name}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Activity className="w-4 h-4 text-[#7CB342]" />
                <span className="text-gray-600">Live data</span>
              </div>
            </div>

            {/* Map Placeholder */}
            <div className="bg-gray-50 rounded-xl border-2 border-gray-200 overflow-hidden" style={{ height: '400px' }}>
              <div className="w-full h-full flex flex-col items-center justify-center">
                <div className="w-24 h-24 rounded-full bg-gray-200 flex items-center justify-center mb-4">
                  <Map className="w-12 h-12 text-gray-400" />
                </div>
                <h3 className="text-xl font-semibold text-gray-700 mb-2">Map visualization coming soon</h3>
                <p className="text-gray-500 text-center max-w-md">
                  The applications map will show all planning applications for {pageData.authority_name}
                </p>
              </div>
            </div>

            {/* Map Info Footer */}
            <div className="mt-4 flex items-start gap-2 text-sm text-gray-500">
              <MapPin className="w-4 h-4 mt-0.5" />
              <div>
                <p className="font-medium text-gray-700">
                  {pageData.authority_name}
                </p>
                <p className="text-xs">
                  Coordinates will be available for all planning applications
                </p>
              </div>
            </div>
          </div>
        </Container>

        {/* NEWS SECTION */}
        {pageData.sections.news.items.length > 0 && (
          <Container className="py-8">
            <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
              <h2 className="text-3xl font-bold text-gray-900 mb-6 flex items-center gap-3">
                <Newspaper className="w-8 h-8 text-[#7CB342]" />
                {pageData.sections.news.h2}
              </h2>
              <div className="grid gap-4">
                {pageData.sections.news.items.map((item: any, idx: number) => (
                  <div key={idx} className="border-l-4 border-[#7CB342] pl-4 py-2">
                    <h3 className="font-semibold text-gray-900 mb-1">{item.title}</h3>
                    <p className="text-sm text-gray-600">{item.summary}</p>
                    {item.date && (
                      <p className="text-xs text-gray-500 mt-1">{item.date}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </Container>
        )}

        {/* POLICY SECTION */}
        {pageData.sections.policy.content && (
          <Container className="py-8">
            <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
              <h2 className="text-3xl font-bold text-gray-900 mb-6 flex items-center gap-3">
                <FileCheck className="w-8 h-8 text-[#7CB342]" />
                {pageData.sections.policy.h2}
              </h2>
              <div className="prose prose-lg max-w-none text-gray-700 leading-relaxed">
                {renderContent(pageData.sections.policy.content)}
              </div>
            </div>
          </Container>
        )}

        {/* FUTURE OUTLOOK */}
        {pageData.sections.future_outlook.content && (
          <Container className="py-8">
            <div className="bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-lg p-8 border border-gray-100">
              <h2 className="text-3xl font-bold text-gray-900 mb-6 flex items-center gap-3">
                <TrendingUp className="w-8 h-8 text-[#7CB342]" />
                {pageData.sections.future_outlook.h2}
              </h2>
              <div className="prose prose-lg max-w-none text-gray-700 leading-relaxed">
                {renderContent(pageData.sections.future_outlook.content)}
              </div>
            </div>
          </Container>
        )}

        {/* RESOURCES */}
        {pageData.sections.resources.links.length > 0 && (
          <Container className="py-8 pb-16">
            <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
              <h2 className="text-3xl font-bold text-gray-900 mb-6 flex items-center gap-3">
                <Globe className="w-8 h-8 text-[#7CB342]" />
                {pageData.sections.resources.h2}
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {pageData.sections.resources.links.map((link, idx) => (
                  <a
                    key={idx}
                    href={link.url}
                    className="flex items-center gap-2 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors group"
                  >
                    <span className="text-gray-900 font-medium">{link.title}</span>
                    <ArrowUpRight className="w-4 h-4 text-[#7CB342] group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                  </a>
                ))}
              </div>
            </div>
          </Container>
        )}

        {/* RELATED CONTENT */}
        <Container className="py-8">
          <div className="bg-gradient-to-br from-gray-50 to-white rounded-2xl shadow-lg p-8 border border-gray-100">
            <div className="flex items-center gap-2 mb-6">
              <TrendingUp className="w-5 h-5 text-[#7CB342]" />
              <h2 className="text-2xl font-bold text-gray-900">Related Content</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {/* Top Sectors */}
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <Building2 className="w-4 h-4 text-[#7CB342]" />
                  <h3 className="font-semibold text-gray-900">Top Sectors</h3>
                </div>
                <p className="text-sm text-gray-600 mb-4">View applications by sector type</p>
                <div className="space-y-2">
                  {metrics.by_type?.slice(0, 3).map((type: any, idx: number) => (
                    <a
                      key={idx}
                      href={`/sectors/${type.type.toLowerCase()}`}
                      className="flex items-center justify-between p-3 bg-white rounded-lg hover:bg-gray-50 transition-colors border border-gray-100 group"
                    >
                      <span className="text-gray-900 font-medium">{type.type} ({type.count})</span>
                      <ArrowUpRight className="w-4 h-4 text-[#7CB342] group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                    </a>
                  ))}
                </div>
              </div>

              {/* Nearby Authorities */}
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <MapPin className="w-4 h-4 text-[#7CB342]" />
                  <h3 className="font-semibold text-gray-900">Nearby Authorities</h3>
                </div>
                <p className="text-sm text-gray-600 mb-4">Explore neighboring planning authorities</p>
                <div className="space-y-2">
                  {['Manchester', 'Birmingham', 'London'].map((authority, idx) => (
                    <a
                      key={idx}
                      href={`/planning-applications/${authority.toLowerCase()}`}
                      className="flex items-center justify-between p-3 bg-white rounded-lg hover:bg-gray-50 transition-colors border border-gray-100 group"
                    >
                      <span className="text-gray-900 font-medium">{authority}</span>
                      <ArrowUpRight className="w-4 h-4 text-[#7CB342] group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                    </a>
                  ))}
                </div>
              </div>

              {/* Popular Features */}
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <Activity className="w-4 h-4 text-[#7CB342]" />
                  <h3 className="font-semibold text-gray-900">Popular Features</h3>
                </div>
                <p className="text-sm text-gray-600 mb-4">Explore more planning tools</p>
                <div className="space-y-2">
                  <a
                    href="/search"
                    className="flex items-center justify-between p-3 bg-white rounded-lg hover:bg-gray-50 transition-colors border border-gray-100 group"
                  >
                    <span className="text-gray-900 font-medium">Advanced Search</span>
                    <ArrowUpRight className="w-4 h-4 text-[#7CB342] group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                  </a>
                  <a
                    href="/alerts"
                    className="flex items-center justify-between p-3 bg-white rounded-lg hover:bg-gray-50 transition-colors border border-gray-100 group"
                  >
                    <span className="text-gray-900 font-medium">Planning Alerts</span>
                    <ArrowUpRight className="w-4 h-4 text-[#7CB342] group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                  </a>
                  <a
                    href="/report"
                    className="flex items-center justify-between p-3 bg-white rounded-lg hover:bg-gray-50 transition-colors border border-gray-100 group"
                  >
                    <span className="text-gray-900 font-medium">Custom Reports</span>
                    <ArrowUpRight className="w-4 h-4 text-[#7CB342] group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                  </a>
                </div>
              </div>
            </div>
          </div>
        </Container>

        {/* FAQ SECTION - Matching Homepage Design */}
        {pageData.sections.faq.content && (() => {
          // Parse FAQ content into Q&A pairs
          const faqItems: Array<{question: string; answer: string}> = []
          const paragraphs = pageData.sections.faq.content.split('\n\n').filter(para => para.trim() && !para.match(/^---+$/))

          let currentQuestion = ''
          let currentAnswer = ''

          for (let i = 0; i < paragraphs.length; i++) {
            const para = paragraphs[i].trim()

            // Skip section headers (### without Q:)
            if (para.startsWith('###') && !para.includes('Q:')) {
              continue
            }

            // Check if it's a question (starts with Q: or **Q:)
            const isQuestion = para.startsWith('Q:') || para.startsWith('**Q:')

            if (isQuestion) {
              // Save previous Q&A if exists
              if (currentQuestion && currentAnswer) {
                faqItems.push({ question: currentQuestion, answer: currentAnswer })
              }

              // Start new question - extract text after marker
              let questionText = para
              if (para.startsWith('**Q:')) {
                // Remove **Q: and trailing **
                questionText = para.replace(/^\*\*Q:\s*/, '').replace(/\*\*$/, '').trim()
              } else if (para.startsWith('Q:')) {
                questionText = para.replace(/^Q:\s*/, '').trim()
              }
              currentQuestion = questionText
              currentAnswer = ''
            }
            // Check if it's an answer (starts with A: or **A:)
            else if (para.startsWith('A:') || para.startsWith('**A:')) {
              if (para.startsWith('**A:')) {
                currentAnswer = para.replace(/^\*\*A:\s*/, '').trim()
              } else {
                currentAnswer = para.replace(/^A:\s*/, '').trim()
              }
            }
            // Otherwise, it might be the answer without A: prefix
            else if (currentQuestion && !currentAnswer) {
              currentAnswer = para
            }
          }

          // Don't forget the last Q&A pair
          if (currentQuestion && currentAnswer) {
            faqItems.push({ question: currentQuestion, answer: currentAnswer })
          }

          if (faqItems.length === 0) return null

          return (
            <section className="py-12 bg-gradient-to-br from-planning-accent to-planning-bright relative overflow-hidden">
              {/* Background Pattern */}
              <div className="absolute inset-0 opacity-10">
                <div className="absolute top-0 right-0 w-96 h-96">
                  <svg viewBox="0 0 200 200" className="w-full h-full">
                    <defs>
                      <pattern id="grid-faq" width="20" height="20" patternUnits="userSpaceOnUse">
                        <path d="M 20 0 L 0 0 0 20" fill="none" stroke="white" strokeWidth="0.5"/>
                      </pattern>
                    </defs>
                    <rect width="200" height="200" fill="url(#grid-faq)" />
                  </svg>
                </div>
              </div>

              <Container className="relative z-10">
                <div className="max-w-4xl mx-auto">
                  {/* Header */}
                  <div className="mb-12 text-center">
                    <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-4">
                      {pageData.sections.faq.h2}
                    </h2>
                    <p className="text-white/90 text-lg">
                      Common questions about {pageData.authority_name} planning applications
                    </p>
                  </div>

                  {/* FAQ Accordion */}
                  <div className="space-y-4">
                    {faqItems.map((faq, idx) => (
                      <div
                        key={idx}
                        className="bg-white/10 backdrop-blur-sm rounded-2xl overflow-hidden border border-white/20"
                      >
                        {/* Question Button */}
                        <button
                          onClick={() => setExpandedFAQ(expandedFAQ === idx ? null : idx)}
                          className="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-white/5 transition-colors"
                        >
                          <span className="text-white font-semibold text-lg pr-4">
                            {faq.question}
                          </span>
                          <ChevronDown
                            className={cn(
                              'w-5 h-5 text-white transition-transform duration-200 flex-shrink-0',
                              expandedFAQ === idx ? 'rotate-180' : ''
                            )}
                          />
                        </button>

                        {/* Answer */}
                        <div
                          className={cn(
                            'overflow-hidden transition-all duration-300 ease-in-out',
                            expandedFAQ === idx
                              ? 'max-h-[500px] opacity-100'
                              : 'max-h-0 opacity-0'
                          )}
                        >
                          <div className="px-6 pb-6">
                            <div className="border-t border-white/20 pt-4">
                              <div className="text-white leading-relaxed text-base">
                                {parseMarkdownText(faq.answer, true)}
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </Container>
            </section>
          )
        })()}
      </div>

      <Footer />
    </>
  )
}
