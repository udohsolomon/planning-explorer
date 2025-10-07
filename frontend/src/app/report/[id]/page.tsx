'use client'

/**
 * Planning Application Report Page
 *
 * APPLICANT/AGENT ENRICHMENT AGENT INTEGRATION
 * ============================================
 *
 * This page implements real-time data enrichment for Applicant Name and Agent Name fields.
 *
 * FLOW:
 * 1. User clicks "Generate Report" or "View Details" from search results
 * 2. Frontend makes API call: GET /api/report/{application_id}
 * 3. Backend checks Redis cache for applicant/agent data (key: applicant_agent:{application_id}, TTL: 24h)
 * 4. If CACHE HIT: Return complete data immediately, enrichmentLoading = false
 * 5. If CACHE MISS:
 *    - Trigger enrichment agent asynchronously (max 5s timeout)
 *    - Agent scrapes planning portal URL to extract applicant/agent names
 *    - Uses Firecrawl (fast) or Playwright (JS-rendered) or Context7 (adaptive)
 *    - Returns enriched data or partial data with enrichment_status: 'loading'
 * 6. Frontend shows loading skeleton for applicant/agent fields while enriching
 * 7. Backend caches successful extraction for 24 hours
 * 8. Report renders with complete information
 *
 * BACKEND API STRUCTURE:
 * Response when data available immediately (cache hit):
 * {
 *   success: true,
 *   data: {
 *     report: {
 *       application_details: {
 *         applicant_name: "Discovery Park (South) Limited",
 *         agent_name: "KSR Architects",
 *         ...
 *       }
 *     }
 *   }
 * }
 *
 * Response when enrichment in progress (cache miss, agent triggered):
 * {
 *   success: true,
 *   data: {
 *     report: {
 *       application_details: {
 *         applicant_name: null,  // Frontend shows skeleton
 *         agent_name: null,      // Frontend shows skeleton
 *         ...
 *       }
 *     },
 *     enrichment_status: 'loading',
 *     enrichment_job_id: 'enrich_12345_1234567890'
 *   }
 * }
 *
 * AGENT DETAILS:
 * - Portal Type 1: Idox Public Access (~60%) - Navigate to details tab, scrape table
 * - Portal Type 2: Custom portals like Liverpool (~20%) - Direct access, labeled fields
 * - Portal Type 3: Unknown/Adaptive (~20%) - Use Context7 for semantic extraction
 * - Tools: Playwright MCP, Firecrawl MCP, Context7 MCP, Perplexity MCP
 * - Speed: 2-5 seconds (cached patterns), 5-8 seconds (adaptive/new portals)
 * - Cache: Redis 24h TTL, no ES persistence
 *
 * IMPLEMENTATION STATUS:
 * ✅ Frontend skeleton loading state implemented
 * ✅ 3-second simulation for demo purposes
 * ⏳ Backend agent integration pending
 * ⏳ Redis caching pending
 * ⏳ Real-time polling/websocket pending
 *
 * TODO FOR BACKEND:
 * 1. Implement enrichment agent (see agent prompt document)
 * 2. Add Redis caching layer
 * 3. Modify /api/report/{id} endpoint to trigger agent on cache miss
 * 4. Optional: Add /api/report/{id}/enrichment-status polling endpoint
 * 5. Optional: Add WebSocket support for real-time updates
 */

import { useEffect, useState, useRef } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import { apiClient, PlanningApplicationResponse } from '@/lib/api'
import { downloadPlanningReportPDF } from '@/lib/pdf-utils'
import { cn } from '@/lib/utils'
import {
  ArrowLeft, Download, Share2, Printer, FileText, MapPin,
  Calendar, Building2, User, Phone, Mail, Globe, Clock,
  CheckCircle, AlertTriangle, TrendingUp, BarChart3, PieChart,
  Brain, Shield, Target, Zap, ChevronRight, Info, ExternalLink,
  Hash, Home, Briefcase, Map, FileCheck, AlertCircle
} from 'lucide-react'
import Link from 'next/link'
import { LocationMap } from '@/components/report/LocationMap'
import { VolumeChart } from '@/components/report/VolumeChart'
import { TimelineChart } from '@/components/report/TimelineChart'
import { Skeleton } from '@/components/ui/Skeleton'

interface ReportSection {
  title: string
  icon: any
  content: any
}

export default function PlanningApplicationReport() {
  const params = useParams()
  const router = useRouter()
  const reportRef = useRef<HTMLDivElement>(null)

  // Decode the applicationId to handle encoded slashes from IDs like "141478/FH/2024"
  const applicationId = params.id ? decodeURIComponent(params.id as string) : ''
  const [application, setApplication] = useState<PlanningApplicationResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [report, setReport] = useState<any>(null)
  const [aiInsights, setAiInsights] = useState<any>(null)
  const [planningInsights, setPlanningInsights] = useState<any>(null)
  const [downloadingPDF, setDownloadingPDF] = useState(false)
  const [pdfError, setPdfError] = useState<string | null>(null)
  const [enrichmentLoading, setEnrichmentLoading] = useState(false)

  useEffect(() => {
    console.log('=== Report Page Debug ===')
    console.log('Raw params:', params)
    console.log('Raw params.id:', params.id)
    console.log('Decoded Application ID:', applicationId)
    console.log('Is undefined?', applicationId === 'undefined')
    console.log('Is null?', applicationId === 'null')
    console.log('Is empty?', applicationId === '')
    console.log('========================')

    if (applicationId && applicationId !== 'undefined' && applicationId !== 'null' && applicationId !== '') {
      fetchApplicationDetails()
    } else {
      setError(`Invalid application ID provided: "${applicationId}"\n\nPlease return to search and try again.`)
      setLoading(false)
    }
  }, [applicationId])

  // Auto-dismiss PDF error after 10 seconds
  useEffect(() => {
    if (pdfError) {
      const timeout = setTimeout(() => {
        setPdfError(null)
      }, 10000)
      return () => clearTimeout(timeout)
    }
  }, [pdfError])

  const fetchApplicationDetails = async () => {
    setLoading(true)
    setError(null)

    try {
      console.log('Fetching bank-grade report for ID:', applicationId)

      // Set enrichment loading if applicant/agent data not immediately available
      // Backend should return enrichment_status: 'loading' if data is being scraped
      setEnrichmentLoading(true)

      // Use the new unified bank-grade report endpoint
      const reportResponse = await apiClient.getBankGradeReport(applicationId, {
        include_market_analysis: true,
        include_risk_assessment: true,
        include_comparable_analysis: true
      })

      console.log('Bank-grade report API response:', reportResponse)

      if (reportResponse.success && reportResponse.data && reportResponse.data.report) {
        // Extract data from bank-grade report
        const report = reportResponse.data.report

        // Store report in state for later use in JSX
        setReport(report)

        // Map report data to application format
        const mappedApplication = {
          ...report.application_details,
          reference: report.application_details.reference,
          address: report.application_details.address,
          postcode: report.application_details.postcode,
          localAuthority: report.application_details.authority,
          status: report.application_details.status,
          decision: report.application_details.decision,
          applicationType: report.application_details.application_type,
          description: report.application_details.description,
          submissionDate: report.application_details.submission_date,
          decisionDate: report.application_details.decision_date,
          ward: report.application_details.ward,
          documents: [], // Documents will come from separate endpoint if needed
          aiInsights: {
            score: report.opportunity_assessment?.overall_score || 0,
            confidence: (report.opportunity_assessment?.approval_probability || 0) * 100,
            riskLevel: report.risk_assessment?.overall_risk_level?.split(' ')[0]?.toLowerCase() || 'medium',
            predictedOutcome: report.ai_intelligence?.predicted_outcome?.predicted_decision || 'Unknown',
            opportunities: report.recommendations?.immediate_actions || [],
            concerns: report.risk_assessment?.risk_factors || []
          }
        }

        setApplication(mappedApplication as any)

        // Set AI insights from report
        setAiInsights({
          score: report.opportunity_assessment?.overall_score || 0,
          confidence: (report.opportunity_assessment?.approval_probability || 0) * 100,
          riskLevel: report.risk_assessment?.overall_risk_level?.split(' ')[0]?.toLowerCase() || 'medium',
          predictedOutcome: report.ai_intelligence?.predicted_outcome?.predicted_decision || 'Unknown',
          opportunities: report.recommendations?.immediate_actions || [],
          concerns: report.risk_assessment?.risk_factors || []
        })

        // Set planning insights from report
        setPlanningInsights({
          location_insights: report.market_intelligence?.location_analysis || {},
          authority_performance: report.market_intelligence?.authority_performance || {},
          recommendations: report.recommendations?.immediate_actions || []
        })

        // Check if applicant/agent data is available
        // If available immediately (from cache), stop loading skeleton
        if (report.application_details?.applicant_name || report.application_details?.agent_name) {
          setEnrichmentLoading(false)
        } else {
          // Simulate agent enrichment with 3-second delay
          // In production, backend will handle this via:
          // 1. Check Redis cache for applicant/agent data
          // 2. If cache miss, trigger enrichment agent
          // 3. Return enrichment_status: 'loading' in API response
          // 4. Frontend polls /api/report/{id}/enrichment-status every 1s
          setTimeout(() => {
            // TODO: Replace with actual polling logic when backend agent is ready
            // For now, just stop showing skeleton after 3 seconds
            setEnrichmentLoading(false)
          }, 3000)
        }
      } else {
        console.error('API returned unsuccessful response:', reportResponse)
        setError(reportResponse.message || 'Failed to fetch bank-grade report')
      }
    } catch (err) {
      console.error('Error fetching application:', err)
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred'

      if (errorMessage.includes('404') || errorMessage.includes('Not found')) {
        setError(`Application with ID '${applicationId}' was not found. Please check the application ID and try again.`)
      } else if (errorMessage.includes('Network') || errorMessage.includes('fetch')) {
        setError('Network error: Unable to connect to the server. Please check your connection and try again.')
      } else {
        setError(`An error occurred while fetching application details: ${errorMessage}`)
      }
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string | undefined | null) => {
    if (!dateString) return 'N/A'
    try {
      return new Date(dateString).toLocaleDateString('en-GB', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      })
    } catch {
      return 'N/A'
    }
  }

  const safeDisplay = (value: any, defaultValue: string = 'N/A') => {
    if (value === null || value === undefined || value === '') {
      return defaultValue
    }
    return String(value)
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'approved':
        return 'text-[#043F2E] bg-green-50 border-green-200'
      case 'rejected':
        return 'text-red-600 bg-red-50 border-red-200'
      case 'pending':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'low':
        return 'text-[#043F2E] bg-green-50'
      case 'medium':
        return 'text-yellow-600 bg-yellow-50'
      case 'high':
        return 'text-red-600 bg-red-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  const handlePrint = () => {
    window.print()
  }

  const handleDownloadPDF = async () => {
    if (!application) {
      setPdfError('No application data available for PDF generation')
      return
    }

    setDownloadingPDF(true)
    setPdfError(null)

    try {
      console.log('Generating PDF from web page...')

      // Import the web-to-PDF utility
      const { downloadWebPageAsPDF, downloadViaPrint } = await import('@/lib/web-to-pdf')

      // Get the report container element
      const reportElement = reportRef.current
      if (!reportElement) {
        throw new Error('Report element not found')
      }

      // Generate filename
      const filename = `planning-report-${application.reference?.replace(/\//g, '_')}-${new Date().toISOString().split('T')[0]}.pdf`

      try {
        // Try html2canvas + jsPDF first
        await downloadWebPageAsPDF({
          element: reportElement,
          filename,
          scale: 2,
          quality: 0.95
        })

        console.log('✅ PDF downloaded successfully!')
      } catch (html2canvasError) {
        // Fallback to browser print dialog if html2canvas fails
        console.warn('⚠️  html2canvas failed, falling back to print dialog:', html2canvasError)
        downloadViaPrint(filename)
        console.log('ℹ️  Please use your browser\'s print dialog to save as PDF')
      }
    } catch (error) {
      console.error('❌ PDF download error:', error)
      setPdfError(error instanceof Error ? error.message : 'Failed to download PDF')
    } finally {
      setDownloadingPDF(false)
    }
  }

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: `Planning Application Report - ${application?.reference}`,
        text: `View the detailed report for planning application ${application?.reference}`,
        url: window.location.href
      })
    } else {
      // Fallback: Copy URL to clipboard
      navigator.clipboard.writeText(window.location.href)
      alert('Report link copied to clipboard!')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-planning-primary mx-auto mb-4"></div>
          <p className="text-gray-600">Generating comprehensive report...</p>
        </div>
      </div>
    )
  }

  if (error || !application) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-2xl mx-auto p-8">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Error Loading Report</h2>
          <p className="text-gray-600 mb-4 whitespace-pre-line">{error || 'Application not found'}</p>

          <div className="bg-gray-100 rounded-lg p-4 mb-6 text-left">
            <h3 className="font-semibold text-gray-800 mb-2">Debug Information:</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li><strong>Application ID:</strong> {applicationId || 'Not provided'}</li>
              <li><strong>Raw Params:</strong> {JSON.stringify(params)}</li>
              <li><strong>URL:</strong> {typeof window !== 'undefined' ? window.location.href : 'N/A'}</li>
            </ul>
          </div>

          <div className="flex gap-3 justify-center">
            <Button onClick={() => router.back()} variant="outline">Go Back</Button>
            <Button onClick={() => router.push('/')}>Return to Home</Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header Actions */}
      <div className="bg-white border-b sticky top-0 z-50 shadow-md print:hidden">
        <Container>
          <div className="py-4 flex items-center justify-between">
            <Link href="/" className="flex items-center text-planning-primary hover:text-planning-accent transition-colors">
              <ArrowLeft className="w-5 h-5 mr-2" />
              Back to Search
            </Link>
            <div className="flex items-center space-x-3">
              <Button
                onClick={handleShare}
                variant="outline"
                className="flex items-center space-x-2"
              >
                <Share2 className="w-4 h-4" />
                <span>Share</span>
              </Button>
              <Button
                onClick={handlePrint}
                variant="outline"
                className="flex items-center space-x-2"
              >
                <Printer className="w-4 h-4" />
                <span>Print</span>
              </Button>
              <Button
                onClick={handleDownloadPDF}
                disabled={downloadingPDF || !application}
                className="flex items-center space-x-2"
              >
                {downloadingPDF ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                    <span>Generating PDF...</span>
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4" />
                    <span>Download PDF</span>
                  </>
                )}
              </Button>
            </div>
          </div>
        </Container>
      </div>

      {/* PDF Error Toast */}
      {pdfError && (
        <div className="fixed top-4 right-4 z-50 max-w-md">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 shadow-lg">
            <div className="flex">
              <div className="flex-shrink-0">
                <AlertCircle className="h-5 w-5 text-red-400" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">
                  PDF Generation Failed
                </h3>
                <div className="mt-2 text-sm text-red-700">
                  <p>{pdfError}</p>
                </div>
                <div className="mt-4">
                  <div className="flex space-x-2">
                    <Button
                      onClick={() => setPdfError(null)}
                      variant="outline"
                      className="text-xs"
                    >
                      Dismiss
                    </Button>
                    <Button
                      onClick={handleDownloadPDF}
                      disabled={downloadingPDF}
                      className="text-xs"
                    >
                      Try Again
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Report Content - Professional Bank-Grade Design */}
      <Container>
        <div ref={reportRef} className="py-8 max-w-6xl mx-auto">
          {/* Professional Cover Section */}
          <div className="bg-gradient-to-br from-slate-800 via-slate-900 to-slate-800 rounded-2xl shadow-2xl p-12 mb-8 relative overflow-hidden">
            {/* Decorative Background Pattern */}
            <div className="absolute inset-0 opacity-5">
              <div className="absolute top-0 left-0 w-full h-full" style={{
                backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
                backgroundSize: '40px 40px'
              }}></div>
            </div>

            <div className="relative z-10">
              <div className="flex items-start justify-between mb-8">
                <div className="flex-1">
                  <h1 className="text-5xl font-black mb-3 tracking-tight" style={{ color: '#FFFFFF' }}>
                    PLANNING APPLICATION REPORT
                  </h1>
                  <p className="text-lg font-light" style={{ color: '#FFFFFF' }}>
                    Created on {formatDate(new Date().toISOString())}
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-white mb-2">Planning Explorer</div>
                  <p className="text-sm text-white/60">Report ID: {applicationId ? applicationId.slice(0, 8).toUpperCase() : 'N/A'}</p>
                </div>
              </div>

              <div className="mt-8 space-y-3">
                <p className="text-xl text-white/90 font-medium">
                  {application.address}
                </p>
                <p className="text-lg text-white/70">
                  {application.postcode}
                </p>
              </div>

              {/* Key Metrics Bar */}
              <div className="grid grid-cols-3 gap-6 mt-10 pt-8 border-t border-white/20">
                <div>
                  <p className="text-xs text-white/50 uppercase tracking-wider mb-2">Reference</p>
                  <p className="text-lg font-bold text-white">{safeDisplay(application.reference)}</p>
                </div>
                <div>
                  <p className="text-xs text-white/50 uppercase tracking-wider mb-2">Authority</p>
                  <p className="text-lg font-black uppercase text-white">{safeDisplay(application.localAuthority)}</p>
                </div>
                <div>
                  <p className="text-xs text-white/50 uppercase tracking-wider mb-2">Status</p>
                  <p className="text-lg font-black uppercase text-white">{safeDisplay(application.status)}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Table of Contents */}
          <div className="bg-slate-50 rounded-2xl shadow-lg p-10 mb-8">
            <h2 className="text-4xl font-thin text-slate-800 mb-8 tracking-[0.2em] uppercase opacity-30">
              CONTENTS
            </h2>
            <div className="space-y-5">
              {[
                { title: 'KEY PLANNING INFORMATION', page: '1' },
                { title: 'APPLICATION DETAILS', page: '2' },
                { title: 'AI INTELLIGENCE ANALYSIS', page: '3' },
                { title: 'PLANNING INSIGHTS', page: '4' },
                { title: 'OPPORTUNITY ASSESSMENT', page: '5' },
                { title: 'DOCUMENTS & APPENDIX', page: '6' }
              ].map((item, idx) => (
                <div key={idx} className="flex justify-between items-center pb-4 border-b border-dotted border-slate-300">
                  <span className="text-sm font-medium text-slate-700">{item.title}</span>
                  <span className="text-sm text-slate-500">{item.page}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Executive Summary Section */}
          <div className="bg-white rounded-2xl shadow-lg p-10 mb-8">
            <div className="flex items-center justify-between mb-8 pb-6 border-b-2 border-[#043F2E]">
              <h2 className="text-3xl font-bold text-slate-800">EXECUTIVE SUMMARY</h2>
              <div className="text-xl font-bold text-[#043F2E]">Planning Explorer</div>
            </div>

            <div className="mb-8">
              <div className="bg-slate-50 rounded-lg p-6">
                <p className="text-sm text-slate-700 leading-relaxed">
                  {report.executive_summary?.overview || 'This planning application analysis is based on comprehensive AI intelligence and market data.'}
                </p>

                {report.executive_summary?.key_highlights && report.executive_summary.key_highlights.length > 0 && (
                  <div className="mt-6">
                    <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">Key Highlights</h4>
                    <ul className="space-y-2">
                      {report.executive_summary.key_highlights.map((highlight: string, index: number) => (
                        <li key={index} className="flex items-start gap-2 text-sm text-slate-700">
                          <span className="w-1.5 h-1.5 bg-[#043F2E] rounded-full mt-2 flex-shrink-0"></span>
                          {highlight}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>

            <div className="mb-8">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white border border-slate-200 rounded-lg p-4">
                  <p className="text-xs text-slate-500 uppercase tracking-wide mb-2">Investment Rating</p>
                  <p className="text-xl font-bold text-[#043F2E]">
                    {report.executive_summary?.opportunity_rating || 'Pending Analysis'}
                  </p>
                </div>
                <div className="bg-white border border-slate-200 rounded-lg p-4">
                  <p className="text-xs text-slate-500 uppercase tracking-wide mb-2">Recommendation</p>
                  <p className={cn(
                    "text-xl font-bold",
                    report.executive_summary?.recommendation === 'RECOMMEND' ? 'text-green-600' :
                    report.executive_summary?.recommendation === 'REVIEW' ? 'text-yellow-600' :
                    'text-red-600'
                  )}>
                    {report.executive_summary?.recommendation || 'REVIEW'}
                  </p>
                </div>
              </div>
            </div>

            {report.executive_summary?.critical_factors && report.executive_summary.critical_factors.length > 0 && (
              <div className="mb-8">
                <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Critical Factors</h3>
                <div className="space-y-2">
                  {report.executive_summary.critical_factors.map((factor: string, index: number) => (
                    <div key={index} className="flex items-start gap-2 text-sm text-slate-700 bg-amber-50 rounded p-3">
                      <span className="text-amber-600">⚠️</span>
                      {factor}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Key Planning Information Section */}
          <div className="bg-white rounded-2xl shadow-lg p-10 mb-8">
            <div className="flex items-center justify-between mb-8 pb-6 border-b-2 border-[#043F2E]">
              <h2 className="text-3xl font-bold text-slate-800">KEY PLANNING INFORMATION</h2>
              <div className="text-xl font-bold text-[#043F2E]">Planning Explorer</div>
            </div>

            {/* Property Overview */}
            <div className="mb-8">
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Property Overview</h3>
              <div className="bg-white border border-slate-200 rounded-xl p-6">
                <p className="text-lg font-semibold text-slate-800 mb-6">{application.address}</p>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                    <p className="text-xs text-slate-500 uppercase tracking-wide mb-2">Reference Number</p>
                    <p className="text-base font-bold text-slate-800">{application.reference}</p>
                  </div>
                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                    <p className="text-xs text-slate-500 uppercase tracking-wide mb-2">Application Type</p>
                    <p className="text-base font-bold text-slate-800">{application.applicationType}</p>
                  </div>
                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                    <p className="text-xs text-slate-500 uppercase tracking-wide mb-2">Submission Date</p>
                    <p className="text-base font-bold text-slate-800">{formatDate(application.submissionDate)}</p>
                  </div>
                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                    <p className="text-xs text-slate-500 uppercase tracking-wide mb-2">Current Status</p>
                    <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold uppercase ${getStatusColor(safeDisplay(application.status))}`}>
                      {safeDisplay(application.status)}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* AI Intelligence Metrics - Professional Score Cards */}
            {application.aiInsights && (
              <div className="mb-8">
                <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Intelligence Metrics</h3>
                <div className="flex justify-around gap-6">
                  <div className="text-center">
                    <div className="w-24 h-24 mx-auto bg-blue-500 rounded-full flex items-center justify-center mb-3 shadow-lg">
                      <span className="text-3xl font-bold text-white">{safeDisplay(application.aiInsights.score)}</span>
                    </div>
                    <p className="text-xs text-slate-600">Opportunity<br/>Score</p>
                  </div>
                  <div className="text-center">
                    <div className="w-24 h-24 mx-auto bg-[#043F2E] rounded-full flex items-center justify-center mb-3 shadow-lg">
                      <span className="text-3xl font-bold text-white">{safeDisplay(application.aiInsights.confidence)}%</span>
                    </div>
                    <p className="text-xs text-slate-600">Approval<br/>Probability</p>
                  </div>
                  <div className="text-center">
                    <div className="w-24 h-24 mx-auto bg-amber-500 rounded-full flex items-center justify-center mb-3 shadow-lg">
                      <span className="text-xl font-bold text-white capitalize">{safeDisplay(application.aiInsights.riskLevel)}</span>
                    </div>
                    <p className="text-xs text-slate-600">Risk<br/>Level</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Application Details Section */}
          <div className="bg-white rounded-2xl shadow-lg p-10 mb-8">
            <div className="flex items-center justify-between mb-8 pb-6 border-b-2 border-[#043F2E]">
              <h2 className="text-3xl font-bold text-slate-800">APPLICATION DETAILS</h2>
            </div>

            <div className="mb-8">
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Development Description</h3>
              <div className="bg-slate-50 rounded-lg p-6">
                <p className="text-sm text-slate-700 leading-relaxed">{safeDisplay(application.description)}</p>
              </div>
            </div>

            <div className="mb-8">
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Planning Information</h3>
              <div className="grid grid-cols-3 gap-8">
                <div className="space-y-3">
                  <div className="flex items-start gap-3">
                    <Home className="w-5 h-5 text-slate-400 mt-0.5" />
                    <div>
                      <p className="text-xs text-slate-500">Address</p>
                      <p className="text-sm text-slate-800 font-medium">{safeDisplay(application.address)}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <MapPin className="w-5 h-5 text-slate-400 mt-0.5" />
                    <div>
                      <p className="text-xs text-slate-500">Postcode</p>
                      <p className="text-sm text-slate-800 font-medium">{safeDisplay(application.postcode)}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Map className="w-5 h-5 text-slate-400 mt-0.5" />
                    <div>
                      <p className="text-xs text-slate-500">Ward</p>
                      <p className="text-sm text-slate-800 font-medium">{safeDisplay(report?.application_details?.ward_name || application.ward)}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Globe className="w-5 h-5 text-slate-400 mt-0.5" />
                    <div>
                      <p className="text-xs text-slate-500">Website</p>
                      {report?.application_details?.url ? (
                        <a
                          href={report.application_details.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-blue-600 hover:text-blue-800 font-medium flex items-center gap-1"
                          title={report.application_details.url}
                        >
                          View Application <ExternalLink className="w-3 h-3" />
                        </a>
                      ) : (
                        <p className="text-sm text-slate-800 font-medium">N/A</p>
                      )}
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-start gap-3">
                    <Briefcase className="w-5 h-5 text-slate-400 mt-0.5" />
                    <div>
                      <p className="text-xs text-slate-500">Application Type</p>
                      <p className="text-sm text-slate-800 font-medium">{safeDisplay(application.applicationType)}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Calendar className="w-5 h-5 text-slate-400 mt-0.5" />
                    <div>
                      <p className="text-xs text-slate-500">Decision Date</p>
                      <p className="text-sm text-slate-800 font-medium">{formatDate(report?.application_details?.decided_date || application.decisionDate)}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <User className="w-5 h-5 text-slate-400 mt-0.5" />
                    <div className="flex-1">
                      <p className="text-xs text-slate-500">Applicant Name</p>
                      {enrichmentLoading ? (
                        <Skeleton className="h-5 w-48 mt-1" />
                      ) : (
                        <p className="text-sm text-slate-800 font-medium">{safeDisplay(report?.application_details?.applicant_name)}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <User className="w-5 h-5 text-slate-400 mt-0.5" />
                    <div className="flex-1">
                      <p className="text-xs text-slate-500">Agent Name</p>
                      {enrichmentLoading ? (
                        <Skeleton className="h-5 w-48 mt-1" />
                      ) : (
                        <p className="text-sm text-slate-800 font-medium">{safeDisplay(report?.application_details?.agent_name)}</p>
                      )}
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-start gap-3">
                    <FileText className="w-5 h-5 text-slate-400 mt-0.5" />
                    <div>
                      <p className="text-xs text-slate-500">Number of Documents</p>
                      <p className="text-sm text-slate-800 font-medium">{safeDisplay(report?.application_details?.n_documents)}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Clock className="w-5 h-5 text-slate-400 mt-0.5" />
                    <div>
                      <p className="text-xs text-slate-500">Statutory Days</p>
                      <p className="text-sm text-slate-800 font-medium">{safeDisplay(report?.application_details?.n_statutory_days)}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <ExternalLink className="w-5 h-5 text-slate-400 mt-0.5" />
                    <div>
                      <p className="text-xs text-slate-500">Documents URL</p>
                      {report?.application_details?.docs_url ? (
                        <a
                          href={report.application_details.docs_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-blue-600 hover:text-blue-800 font-medium flex items-center gap-1"
                          title={report.application_details.docs_url}
                        >
                          View Docs <ExternalLink className="w-3 h-3" />
                        </a>
                      ) : (
                        <p className="text-sm text-slate-800 font-medium">N/A</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <MapPin className="w-5 h-5 text-slate-400 mt-0.5" />
                    <div>
                      <p className="text-xs text-slate-500">Area Name</p>
                      <p className="text-sm text-slate-800 font-medium">{report?.application_details?.area_name || safeDisplay(application.localAuthority)}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Location Map */}
            {application.location && application.location.lat && application.location.lon && (
              <div className="mb-8">
                <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Property Location</h3>
                <LocationMap
                  latitude={application.location.lat}
                  longitude={application.location.lon}
                  address={application.address || ''}
                  postcode={application.postcode}
                  className="w-full"
                />
              </div>
            )}
          </div>

          {/* AI Intelligence Analysis Section */}
          {application.aiInsights && (
            <div className="bg-white rounded-2xl shadow-lg p-10 mb-8">
              <div className="flex items-center justify-between mb-8 pb-6 border-b-2 border-[#043F2E]">
                <h2 className="text-3xl font-bold text-slate-800">AI INTELLIGENCE ANALYSIS</h2>
              </div>

              <div className="mb-8">
                <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Predictive Analysis</h3>
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6">
                  <h4 className="text-sm font-semibold text-slate-800 mb-3">AI Prediction</h4>
                  <p className="text-sm text-slate-700 leading-relaxed">
                    {safeDisplay(application.aiInsights.predictedOutcome)}
                  </p>
                </div>
              </div>

              {/* Opportunities */}
              {application.aiInsights.opportunities && application.aiInsights.opportunities.length > 0 && (
                <div className="mb-8">
                  <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Identified Opportunities</h3>
                  <div className="bg-white border border-slate-200 rounded-xl p-6 space-y-3">
                    {application.aiInsights.opportunities.map((opp: string, index: number) => (
                      <div key={index} className="flex items-start gap-3">
                        <div className="w-2 h-2 bg-[#043F2E] rounded-full mt-2 flex-shrink-0"></div>
                        <p className="text-sm text-slate-700">{opp}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Concerns */}
              {application.aiInsights.concerns && application.aiInsights.concerns.length > 0 && (
                <div className="mb-8">
                  <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Areas of Attention</h3>
                  <div className="bg-white rounded-xl p-6 space-y-3">
                    {application.aiInsights.concerns.map((concern: string, index: number) => (
                      <div key={index} className="flex items-start gap-3">
                        <div className="w-2 h-2 bg-amber-500 rounded-full mt-2 flex-shrink-0"></div>
                        <p className="text-sm text-slate-700">{concern}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Planning Insights Section */}
          {planningInsights && (
            <div className="bg-white rounded-2xl shadow-lg p-10 mb-8">
              <div className="flex items-center justify-between mb-8 pb-6 border-b-2 border-[#043F2E]">
                <h2 className="text-3xl font-bold text-slate-800">PLANNING INSIGHTS</h2>
              </div>

              <div className="mb-8">
                <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Planning Performance Analysis</h3>
                <div className="bg-slate-50 rounded-xl p-6">
                  <p className="text-sm font-semibold text-slate-800 mb-4">Key Planning Statistics</p>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-white border border-slate-200 rounded-lg p-4">
                      <p className="text-xs text-slate-500 uppercase tracking-wide mb-2">Average Approval Rate</p>
                      <p className="text-2xl font-bold text-[#043F2E]">78%</p>
                      <p className="text-xs text-slate-500 mt-1">↑ 5% from last year</p>
                    </div>
                    <div className="bg-white border border-slate-200 rounded-lg p-4">
                      <p className="text-xs text-slate-500 uppercase tracking-wide mb-2">Average Decision Time</p>
                      <p className="text-2xl font-bold text-amber-600">56 days</p>
                      <p className="text-xs text-slate-500 mt-1">↓ 8 days improvement</p>
                    </div>
                    <div className="bg-white border border-slate-200 rounded-lg p-4">
                      <p className="text-xs text-slate-500 uppercase tracking-wide mb-2">Total Applications (YTD)</p>
                      <p className="text-2xl font-bold text-blue-600">2,847</p>
                      <p className="text-xs text-slate-500 mt-1">+12% vs last year</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-6 mb-8">
                {planningInsights.location_insights && (
                  <div>
                    <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Location Insights</h3>
                    <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 space-y-2">
                      {Object.entries(planningInsights.location_insights).slice(0, 5).map(([key, value]: [string, any]) => (
                        <div key={key} className="flex justify-between items-center">
                          <span className="text-xs text-slate-600 capitalize">{key.replace(/_/g, ' ')}</span>
                          <span className="text-sm font-semibold text-slate-800">{value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {planningInsights.authority_performance && (
                  <div>
                    <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Authority Performance</h3>
                    <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 space-y-2">
                      {Object.entries(planningInsights.authority_performance).slice(0, 5).map(([key, value]: [string, any]) => (
                        <div key={key} className="flex justify-between items-center">
                          <span className="text-xs text-slate-600 capitalize">{key.replace(/_/g, ' ')}</span>
                          <span className="text-sm font-semibold text-slate-800">{value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {planningInsights.recommendations && planningInsights.recommendations.length > 0 && (
                <div className="mb-8">
                  <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Planning Recommendations</h3>
                  <div className="bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-xl p-6">
                    <div className="space-y-3">
                      {planningInsights.recommendations.slice(0, 5).map((rec: string, index: number) => (
                        <div key={index} className="flex items-start gap-3">
                          <Info className="w-4 h-4 text-purple-600 mt-0.5 flex-shrink-0" />
                          <span className="text-sm text-slate-700">{rec}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Planning Application Volume Trends Chart */}
              <div className="mb-8">
                <VolumeChart />
              </div>

              {/* Average Decision Timeline Chart */}
              <div className="mb-8">
                <TimelineChart />
              </div>
            </div>
          )}

          {/* Documents Section */}
          {application.documents && application.documents.length > 0 && (
            <div className="bg-white rounded-2xl shadow-lg p-10 mb-8">
              <div className="flex items-center justify-between mb-8 pb-6 border-b-2 border-[#043F2E]">
                <h2 className="text-3xl font-bold text-slate-800">DOCUMENTS & APPENDIX</h2>
              </div>

              <div className="mb-8">
                <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Associated Documents</h3>
                <div className="space-y-3">
                  {application.documents.map((doc, index) => (
                    <div key={doc.id || index} className="flex items-center justify-between p-4 bg-slate-50 border border-slate-200 rounded-lg hover:bg-slate-100 transition-colors">
                      <div className="flex items-center gap-3">
                        <FileText className="w-5 h-5 text-slate-400" />
                        <div>
                          <p className="font-semibold text-slate-800 text-sm">{doc.name}</p>
                          <p className="text-xs text-slate-500">Type: {doc.type}</p>
                        </div>
                      </div>
                      <a
                        href={doc.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 text-[#043F2E] hover:text-[#065940] transition-colors text-sm font-medium"
                      >
                        <span>View</span>
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Comparable Applications Analysis Section */}
          <div className="bg-white rounded-2xl shadow-lg p-10 mb-8">
            <div className="flex items-center justify-between mb-8 pb-6 border-b-2 border-[#043F2E]">
              <h2 className="text-3xl font-bold text-slate-800">COMPARABLE APPLICATIONS ANALYSIS</h2>
            </div>

            <div className="mb-8">
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Similar Applications</h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b-2 border-slate-200">
                      <th className="text-left py-3 px-4 text-xs font-semibold text-slate-600 uppercase">Reference</th>
                      <th className="text-left py-3 px-4 text-xs font-semibold text-slate-600 uppercase">Description</th>
                      <th className="text-left py-3 px-4 text-xs font-semibold text-slate-600 uppercase">Value</th>
                      <th className="text-left py-3 px-4 text-xs font-semibold text-slate-600 uppercase">Status</th>
                      <th className="text-left py-3 px-4 text-xs font-semibold text-slate-600 uppercase">Decision Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b border-slate-100">
                      <td className="py-3 px-4 text-sm text-slate-700 font-medium">APP/2024/2156</td>
                      <td className="py-3 px-4 text-sm text-slate-700">25 Bank Street - Commercial Tower</td>
                      <td className="py-3 px-4 text-sm text-slate-700 font-semibold">£324M</td>
                      <td className="py-3 px-4"><span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-semibold">Approved</span></td>
                      <td className="py-3 px-4 text-sm text-slate-700">12-Aug-2024</td>
                    </tr>
                    <tr className="border-b border-slate-100">
                      <td className="py-3 px-4 text-sm text-slate-700 font-medium">APP/2023/4789</td>
                      <td className="py-3 px-4 text-sm text-slate-700">Wood Wharf Phase 2</td>
                      <td className="py-3 px-4 text-sm text-slate-700 font-semibold">£567M</td>
                      <td className="py-3 px-4"><span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-semibold">Approved</span></td>
                      <td className="py-3 px-4 text-sm text-slate-700">23-Nov-2023</td>
                    </tr>
                    <tr className="border-b border-slate-100">
                      <td className="py-3 px-4 text-sm text-slate-700 font-medium">APP/2024/1033</td>
                      <td className="py-3 px-4 text-sm text-slate-700">Landmark Pinnacle Extension</td>
                      <td className="py-3 px-4 text-sm text-slate-700 font-semibold">£189M</td>
                      <td className="py-3 px-4"><span className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded text-xs font-semibold">Pending</span></td>
                      <td className="py-3 px-4 text-sm text-slate-700">-</td>
                    </tr>
                    <tr className="border-b border-slate-100">
                      <td className="py-3 px-4 text-sm text-slate-700 font-medium">APP/2023/8901</td>
                      <td className="py-3 px-4 text-sm text-slate-700">South Quay Plaza</td>
                      <td className="py-3 px-4 text-sm text-slate-700 font-semibold">£425M</td>
                      <td className="py-3 px-4"><span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-semibold">Approved</span></td>
                      <td className="py-3 px-4 text-sm text-slate-700">07-Mar-2024</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Planning Recommendations Section */}
          <div className="bg-white rounded-2xl shadow-lg p-10 mb-8">
            <div className="flex items-center justify-between mb-8 pb-6 border-b-2 border-[#043F2E]">
              <h2 className="text-3xl font-bold text-slate-800">PLANNING RECOMMENDATIONS</h2>
            </div>

            <div className="space-y-6">
              <div className="bg-slate-50 rounded-lg p-6">
                <h3 className="text-sm font-bold text-slate-800 mb-3">Strategic Timing</h3>
                <p className="text-sm text-slate-700 leading-relaxed">
                  Submit before Q2 2025 to benefit from current favorable policy environment and avoid potential regulatory changes.
                </p>
              </div>

              <div className="bg-slate-50 rounded-lg p-6">
                <h3 className="text-sm font-bold text-slate-800 mb-3">Community Engagement</h3>
                <p className="text-sm text-slate-700 leading-relaxed">
                  Proactive consultation with local groups has shown 73% higher approval rates for similar scale developments.
                </p>
              </div>

              <div className="bg-slate-50 rounded-lg p-6">
                <h3 className="text-sm font-bold text-slate-800 mb-3">Risk Mitigation</h3>
                <p className="text-sm text-slate-700 leading-relaxed">
                  Consider pre-application advice and environmental impact assessment to address potential concerns early.
                </p>
              </div>
            </div>
          </div>

          {/* Project Timeline & Milestones Section */}
          <div className="bg-white rounded-2xl shadow-lg p-10 mb-8">
            <div className="flex items-center justify-between mb-8 pb-6 border-b-2 border-[#043F2E]">
              <h2 className="text-3xl font-bold text-slate-800">PROJECT TIMELINE & MILESTONES</h2>
            </div>

            <div className="space-y-6">
              {/* Completed Milestone */}
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-12 h-12 bg-green-500 rounded-full flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-bold text-slate-800 mb-2">Application Submitted</h3>
                  <p className="text-sm text-slate-600 mb-1">15-Mar-2024 • Documentation and initial submission completed</p>
                  <span className="inline-block px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-semibold">✓ Completed</span>
                </div>
              </div>

              {/* Completed Milestone */}
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-12 h-12 bg-green-500 rounded-full flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-bold text-slate-800 mb-2">Validation & Initial Review</h3>
                  <p className="text-sm text-slate-600 mb-1">22-Mar-2024 • Technical validation and compliance check (7 days)</p>
                  <span className="inline-block px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-semibold">✓ Completed</span>
                </div>
              </div>

              {/* Completed Milestone */}
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-12 h-12 bg-green-500 rounded-full flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-bold text-slate-800 mb-2">Public Consultation Period</h3>
                  <p className="text-sm text-slate-600 mb-1">05-Apr-2024 • Community engagement and feedback collection (21 days)</p>
                  <span className="inline-block px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-semibold">✓ Completed</span>
                </div>
              </div>

              {/* Completed Milestone */}
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-12 h-12 bg-green-500 rounded-full flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-bold text-slate-800 mb-2">Committee Review & Decision</h3>
                  <p className="text-sm text-slate-600 mb-1">18-Jun-2024 • Final assessment and approval decision (89 days total)</p>
                  <span className="inline-block px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-semibold">✓ Approved</span>
                </div>
              </div>

              {/* In Progress Milestone */}
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center">
                  <svg className="w-6 h-6 text-white animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-bold text-slate-800 mb-2">S106 Agreement Completion</h3>
                  <p className="text-sm text-slate-600 mb-1">Expected: 15-Oct-2024 • Legal agreements and community obligations</p>
                  <span className="inline-block px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-semibold">⏳ In Progress</span>
                </div>
              </div>

              {/* Pending Milestone */}
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-12 h-12 bg-slate-300 rounded-full flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-bold text-slate-800 mb-2">Planning Permission Issued</h3>
                  <p className="text-sm text-slate-600 mb-1">Expected: 30-Oct-2024 • Final permission documentation and commencement</p>
                  <span className="inline-block px-2 py-1 bg-slate-100 text-slate-700 rounded text-xs font-semibold">◦ Pending</span>
                </div>
              </div>
            </div>
          </div>

          {/* Report Information and Footer */}
          <div className="bg-white rounded-2xl shadow-lg p-10 mb-8">
            <div className="flex items-center justify-between mb-8 pb-6 border-b-2 border-[#043F2E]">
              <h2 className="text-3xl font-bold text-slate-800">REPORT INFORMATION</h2>
            </div>

            <div className="mb-8">
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-6">
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <div className="mb-4">
                      <p className="text-xs text-slate-500 mb-1">Report Generated</p>
                      <p className="text-sm font-semibold text-slate-800">{formatDate(new Date().toISOString())}</p>
                    </div>
                    <div className="mb-4">
                      <p className="text-xs text-slate-500 mb-1">Report ID</p>
                      <p className="text-sm font-semibold text-slate-800">{application.reference || 'N/A'}</p>
                    </div>
                    <div className="mb-4">
                      <p className="text-xs text-slate-500 mb-1">Data Sources</p>
                      <p className="text-sm text-slate-700">UK Planning Portal, AI Analysis Engine</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 mb-1">Validity</p>
                      <p className="text-sm text-slate-700">30 days from generation date</p>
                    </div>
                  </div>
                  <div className="flex items-center justify-center">
                    <div className="bg-white border-2 border-slate-300 rounded-lg p-4">
                      <div className="w-24 h-24 bg-slate-100 rounded flex items-center justify-center">
                        <Hash className="w-12 h-12 text-slate-400" />
                      </div>
                      <p className="text-xs text-slate-500 text-center mt-2">Scan for digital version</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="mb-8">
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Contact Information</h3>
              <div className="bg-white border border-slate-200 rounded-lg p-6">
                <p className="text-sm font-semibold text-slate-800 mb-4">Planning Explorer</p>
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <p className="text-xs text-slate-500 uppercase tracking-wide mb-2">Address</p>
                    <p className="text-sm text-slate-700">Planning Intelligence Centre<br/>Manchester, United Kingdom</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 uppercase tracking-wide mb-2">Email</p>
                    <p className="text-sm text-slate-700">hello@planningexplorer.co.uk</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 uppercase tracking-wide mb-2">Website</p>
                    <p className="text-sm text-slate-700">www.planningexplorer.co.uk</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 uppercase tracking-wide mb-2">Follow Us</p>
                    <p className="text-sm text-slate-700">Follow us for planning insights</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="mb-8">
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Important Disclaimers</h3>
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-6 space-y-4">
                <div>
                  <p className="text-sm font-semibold text-slate-800 mb-2">Accuracy and Completeness</p>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    All reasonable efforts have been made by Planning Explorer to ensure the accuracy, validity and completeness of the enclosed
                    planning information, with accuracy, validity and completeness neither warranted nor guaranteed. Planning Explorer accepts zero
                    liability for any and all losses or damages resulting from the data and information contained within this document.
                  </p>
                </div>

                <div>
                  <p className="text-sm font-semibold text-slate-800 mb-2">Data Sources and Currency</p>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    Data and information displayed in the above Planning Application Report has been aggregated from a number of data points by the
                    Planning Explorer AI Intelligence Service and the Planning Explorer Automated Analysis Model. The data and information contained
                    is up-to-date as of the date of publication.
                  </p>
                </div>

                <div>
                  <p className="text-sm font-semibold text-slate-800 mb-2">Professional Advice</p>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    Data and information displayed within the Planning Application Report does not constitute professional planning or legal advice.
                    Thoroughly discuss your options with a trained planning expert or solicitor before taking action. For more information and planning
                    intelligence services, please contact Planning Explorer at hello@planningexplorer.co.uk or visit https://www.planningexplorer.co.uk.
                    To opt out of future communication, contact Planning Explorer directly.
                  </p>
                </div>

                <div>
                  <p className="text-sm font-semibold text-slate-800 mb-2">Copyright and Database Rights</p>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    Planning application information produced by Local Planning Authorities. © Crown copyright and database rights 2025.<br/><br/>
                    The polygons (including the associated geometry, namely x, y co-ordinates) and UPRNs are subject to Crown and GeoPlace LLP copyright
                    and database rights 2025 Ordnance Survey 100026316.<br/><br/>
                    AI analysis and predictive modelling © 2025 Planning Explorer. All rights reserved.
                  </p>
                </div>
              </div>
            </div>

            <div className="mb-8">
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">About Planning Explorer</h3>
              <div className="bg-gradient-to-r from-[#f0f9e8] to-emerald-50 rounded-lg p-6">
                <p className="text-sm font-semibold text-slate-800 mb-3">Your AI-Powered Planning Intelligence Partner</p>
                <p className="text-xs text-slate-700 leading-relaxed mb-4">
                  Planning Explorer revolutionises property intelligence by transforming weeks of manual research into minutes of AI-powered insights.
                  We provide comprehensive UK planning data that's accessible, actionable, and intelligent for every property professional.
                </p>
                <div className="grid grid-cols-4 gap-4 mt-4">
                  <div>
                    <p className="text-lg font-bold text-[#043F2E]">336K+</p>
                    <p className="text-xs text-slate-600">Applications Tracked</p>
                  </div>
                  <div>
                    <p className="text-lg font-bold text-[#043F2E]">321K+</p>
                    <p className="text-xs text-slate-600">Councils Covered</p>
                  </div>
                  <div>
                    <p className="text-lg font-bold text-[#043F2E]">85%+</p>
                    <p className="text-xs text-slate-600">Prediction Accuracy</p>
                  </div>
                  <div>
                    <p className="text-lg font-bold text-[#043F2E]">98%</p>
                    <p className="text-xs text-slate-600">Customer Satisfaction</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Professional Footer */}
          <div className="bg-slate-800 rounded-2xl shadow-2xl p-8 text-center">
            <div className="border-t-4 border-[#043F2E] pt-6">
              <div className="flex justify-between items-center text-white/80 text-xs">
                <p>© 2024 Planning Explorer. All rights reserved.</p>
                <p>AI-Generated Report | Confidence Level: {application.aiInsights?.confidence || 95}%</p>
                <p>Page 1 of 8</p>
              </div>
            </div>
          </div>
        </div>
      </Container>

    </div>
  )
}