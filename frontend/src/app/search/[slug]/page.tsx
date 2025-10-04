'use client'

import { useEffect, useState } from 'react'
import { useParams, useSearchParams, useRouter } from 'next/navigation'
import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import { ErrorState, SearchErrorState } from '@/components/ui/ErrorState'
import { AISearchAnimation } from '@/components/search/animation/AISearchAnimation'
import { apiClient, PlanningApplicationResponse } from '@/lib/api'
import { classifyError, generateSearchSuggestions, getRetryDelay, ErrorInfo } from '@/lib/errors'
import {
  Search, MapPin, Calendar, FileText, ArrowLeft, Filter,
  ChevronDown, Building2, Clock, TrendingUp, Brain, Sparkles,
  Download, Share2, Bookmark, Eye, ChevronRight, AlertCircle,
  CheckCircle, XCircle, Clock3, BarChart3, Target, Shield
} from 'lucide-react'
import Link from 'next/link'
import { useSearchStore } from '@/lib/store'

function createSlug(query: string): string {
  return query
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .substring(0, 60)
}

function parseSlug(slug: string): string {
  return slug.replace(/-/g, ' ')
}

export default function SearchResultsPage() {
  const params = useParams()
  const searchParams = useSearchParams()
  const router = useRouter()

  const slug = params.slug as string
  const queryFromUrl = searchParams.get('q') || parseSlug(slug || '')
  const searchType = searchParams.get('type') || 'semantic'

  const [results, setResults] = useState<PlanningApplicationResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<ErrorInfo | null>(null)
  const [retryCount, setRetryCount] = useState(0)
  const [totalResults, setTotalResults] = useState(0)
  const [showFilters, setShowFilters] = useState(false)
  const [selectedView, setSelectedView] = useState<'grid' | 'list'>('list')
  const [sortBy, setSortBy] = useState<'relevance' | 'date' | 'score'>('relevance')
  const [showAnimation, setShowAnimation] = useState(false)

  const { setQuery, setSearchType } = useSearchStore()

  useEffect(() => {
    setQuery(queryFromUrl)
    setSearchType(searchType as any)
  }, [queryFromUrl, searchType, setQuery, setSearchType])

  useEffect(() => {
    if (queryFromUrl) {
      // Show animation only for AI searches (semantic or natural_language)
      if (searchType === 'semantic' || searchType === 'natural_language') {
        setShowAnimation(true)
      }
      performSearch()
    }
  }, [queryFromUrl, searchType, sortBy])

  const performSearch = async (isRetry: boolean = false) => {
    setLoading(true)
    setError(null)

    if (isRetry) {
      setRetryCount(prev => prev + 1)
    } else {
      setRetryCount(0)
    }

    try {
      let response

      switch (searchType) {
        case 'semantic':
          response = await apiClient.semanticSearch(queryFromUrl)
          break
        case 'natural_language':
          response = await apiClient.naturalLanguageSearch(queryFromUrl)
          break
        default:
          response = await apiClient.searchPlanningApplications({
            query: queryFromUrl,
            limit: 50,
            offset: 0
          })
      }

      if (response.success) {
        let sortedResults = response.data || []

        // Debug logging to understand data structure
        console.log('Search API Response:', response)
        console.log('Results data structure:', sortedResults.slice(0, 2)) // Log first 2 results
        console.log('First result application_id:', sortedResults[0]?.application_id)
        console.log('First result keys:', Object.keys(sortedResults[0] || {}))

        // Apply sorting - handle both snake_case and camelCase
        if (sortBy === 'date') {
          sortedResults = sortedResults.sort((a, b) => {
            const dateA = a.submission_date || (a as any).submissionDate || '1970-01-01'
            const dateB = b.submission_date || (b as any).submissionDate || '1970-01-01'
            return new Date(dateB).getTime() - new Date(dateA).getTime()
          })
        } else if (sortBy === 'score') {
          sortedResults = sortedResults.sort((a, b) => {
            const scoreA = a.opportunityScore || (a.aiInsights as any)?.score || 0
            const scoreB = b.opportunityScore || (b.aiInsights as any)?.score || 0
            return scoreB - scoreA
          })
        }

        setResults(sortedResults)
        setTotalResults(response.meta?.total || sortedResults.length)
        setRetryCount(0) // Reset retry count on success
      } else {
        // Handle API response failure
        const errorInfo = classifyError(new Error('Search request failed'))
        errorInfo.suggestions = [...errorInfo.suggestions, ...generateSearchSuggestions(queryFromUrl)]
        setError(errorInfo)
      }
    } catch (err) {
      console.error('Search error:', err)
      const errorInfo = classifyError(err)
      errorInfo.suggestions = [...errorInfo.suggestions, ...generateSearchSuggestions(queryFromUrl)]
      setError(errorInfo)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string | undefined) => {
    if (!dateString) return 'N/A'
    try {
      return new Date(dateString).toLocaleDateString('en-GB', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
      })
    } catch {
      return 'N/A'
    }
  }

  const getStatusIcon = (status: string) => {
    if (!status) return <AlertCircle className="w-4 h-4" />
    switch (status.toLowerCase()) {
      case 'approved':
        return <CheckCircle className="w-4 h-4" />
      case 'rejected':
        return <XCircle className="w-4 h-4" />
      case 'pending':
        return <Clock3 className="w-4 h-4" />
      default:
        return <AlertCircle className="w-4 h-4" />
    }
  }

  const getStatusColor = (status: string) => {
    if (!status) return 'bg-gray-100 text-gray-800 border-gray-200'
    switch (status.toLowerCase()) {
      case 'approved':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'rejected':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-50 border-green-200'
    if (score >= 60) return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    if (score >= 40) return 'text-orange-600 bg-orange-50 border-orange-200'
    return 'text-red-600 bg-red-50 border-red-200'
  }

  const handleViewDetails = (result: PlanningApplicationResponse) => {
    // Use application_id as the primary identifier (mapped from ES uid/name/reference)
    const applicationId = result.application_id
    const reference = result.reference || 'N/A'
    const appSlug = createSlug(reference)

    if (!applicationId) {
      console.error('No valid application ID found in result:', result)
      alert('Unable to view details: Application ID is missing')
      return
    }

    // Encode the applicationId to handle slashes in IDs like "141478/FH/2024"
    router.push(`/application/${encodeURIComponent(applicationId)}/${appSlug}`)
  }

  const handleGenerateReport = (result: PlanningApplicationResponse) => {
    // Backend returns application_id as the primary identifier
    // This is mapped from ES uid -> name -> reference -> _id in priority order
    console.log('=== Generate Report Debug ===')
    console.log('Full result object:', result)
    console.log('result.application_id:', result.application_id)
    console.log('result.reference:', result.reference)
    console.log('result.id:', (result as any).id)
    console.log('result._id:', (result as any)._id)
    console.log('All result keys:', Object.keys(result))
    console.log('===========================')

    // Try multiple ID sources as fallback
    const applicationId = result.application_id || (result as any).id || (result as any)._id || result.reference

    if (!applicationId || applicationId === 'undefined' || applicationId === 'null') {
      console.error('No valid application ID found in result:', result)
      alert(`Unable to generate report: Application ID is missing.\n\nAvailable fields: ${Object.keys(result).join(', ')}\n\nPlease contact support if this issue persists.`)
      return
    }

    console.log('Generating report for application ID:', applicationId)
    console.log('Encoded ID:', encodeURIComponent(applicationId))

    // Encode the applicationId to handle slashes in IDs like "141478/FH/2024"
    router.push(`/report/${encodeURIComponent(applicationId)}`)
  }

  const handleRetrySearch = () => {
    if (error && error.retryDelay) {
      // Show user that retry is scheduled
      setLoading(true)
      const delay = getRetryDelay(retryCount, error.retryDelay)

      setTimeout(() => {
        performSearch(true)
      }, delay)
    } else {
      performSearch(true)
    }
  }

  const handleNewSearch = (newQuery: string) => {
    const newSlug = createSlug(newQuery)
    router.push(`/search/${newSlug}?q=${encodeURIComponent(newQuery)}&type=${searchType}`)
  }

  const handleGoHome = () => {
    router.push('/')
  }

  const handleContactSupport = () => {
    router.push('/contact')
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* AI Search Animation */}
      {showAnimation && (
        <AISearchAnimation
          query={queryFromUrl}
          searchType={searchType === 'semantic' ? 'semantic' : searchType === 'natural_language' ? 'hybrid' : 'semantic'}
          onComplete={() => {
            console.log('🎉 AI search animation completed')
            setShowAnimation(false)
          }}
          onCancel={() => {
            console.log('❌ AI search animation cancelled')
            setShowAnimation(false)
          }}
          onError={(error) => {
            console.error('⚠️ AI search animation error:', error)
            setShowAnimation(false)
          }}
        />
      )}

      {/* Enhanced Header */}
      <div className="bg-white border-b sticky top-0 z-10 shadow-sm">
        <Container>
          <div className="py-4">
            <div className="flex items-center justify-between mb-4">
              <Link href="/" className="flex items-center text-planning-primary hover:text-planning-accent transition-colors">
                <ArrowLeft className="w-5 h-5 mr-2" />
                Back to Home
              </Link>
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2 text-sm">
                  {searchType === 'semantic' && (
                    <>
                      <Brain className="w-4 h-4 text-planning-bright" />
                      <span className="text-planning-bright font-medium">AI-Powered Search</span>
                    </>
                  )}
                  {searchType === 'natural_language' && (
                    <>
                      <Sparkles className="w-4 h-4 text-planning-highlight" />
                      <span className="text-planning-highlight font-medium">Natural Language</span>
                    </>
                  )}
                </div>
                <button className="p-2 text-gray-600 hover:text-planning-primary transition-colors">
                  <Share2 className="w-5 h-5" />
                </button>
                <button className="p-2 text-gray-600 hover:text-planning-primary transition-colors">
                  <Download className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Search className="w-6 h-6 text-planning-primary mr-3" />
                <div>
                  <h1 className="text-2xl font-bold text-planning-primary">
                    Search Results
                  </h1>
                  <p className="text-gray-600">
                    "{queryFromUrl}"
                  </p>
                </div>
              </div>

              {!loading && (
                <div className="flex items-center space-x-4">
                  <div className="text-sm text-gray-500">
                    <span className="font-semibold text-planning-primary">{totalResults}</span> {totalResults === 1 ? 'result' : 'results'} found
                  </div>

                  {/* View Toggle */}
                  <div className="flex bg-gray-100 rounded-lg p-1">
                    <button
                      onClick={() => setSelectedView('list')}
                      className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                        selectedView === 'list'
                          ? 'bg-white text-planning-primary shadow-sm'
                          : 'text-gray-600 hover:text-planning-primary'
                      }`}
                    >
                      List
                    </button>
                    <button
                      onClick={() => setSelectedView('grid')}
                      className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                        selectedView === 'grid'
                          ? 'bg-white text-planning-primary shadow-sm'
                          : 'text-gray-600 hover:text-planning-primary'
                      }`}
                    >
                      Grid
                    </button>
                  </div>

                  {/* Sort Dropdown */}
                  <div className="relative">
                    <button
                      onClick={() => setShowFilters(!showFilters)}
                      className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-200 rounded-lg hover:border-planning-primary transition-colors"
                    >
                      <Filter className="w-4 h-4" />
                      <span className="text-sm">Sort by {sortBy}</span>
                      <ChevronDown className="w-4 h-4" />
                    </button>
                    {showFilters && (
                      <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-20">
                        <button
                          onClick={() => { setSortBy('relevance'); setShowFilters(false) }}
                          className="w-full text-left px-4 py-2 text-sm hover:bg-gray-50 transition-colors"
                        >
                          Relevance
                        </button>
                        <button
                          onClick={() => { setSortBy('date'); setShowFilters(false) }}
                          className="w-full text-left px-4 py-2 text-sm hover:bg-gray-50 transition-colors"
                        >
                          Date (Newest)
                        </button>
                        <button
                          onClick={() => { setSortBy('score'); setShowFilters(false) }}
                          className="w-full text-left px-4 py-2 text-sm hover:bg-gray-50 transition-colors"
                        >
                          AI Score
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </Container>
      </div>

      {/* Results Section */}
      <Container>
        <div className="py-8">
          {loading && (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-planning-primary mx-auto mb-4"></div>
              <p className="text-gray-600">Searching with AI intelligence...</p>
            </div>
          )}

          {error && (
            <SearchErrorState
              errorInfo={error}
              searchQuery={queryFromUrl}
              onRetry={handleRetrySearch}
              onNewSearch={handleNewSearch}
              onGoHome={handleGoHome}
              onContactSupport={handleContactSupport}
            />
          )}

          {!loading && !error && results.length === 0 && (
            <SearchErrorState
              errorInfo={{
                type: 'no_results' as any,
                title: 'No Planning Applications Found',
                message: `No planning applications match your search for "${queryFromUrl}". Try adjusting your search terms or exploring nearby areas.`,
                suggestions: [
                  'Try broader search terms (e.g., "housing" instead of "affordable housing units")',
                  'Search in nearby areas or use a larger radius',
                  'Check spelling of location names',
                  'Use postcode search for more precise results',
                  'Try different property types (residential, commercial, industrial)'
                ],
                actions: [],
                canRetry: false
              }}
              searchQuery={queryFromUrl}
              onNewSearch={handleNewSearch}
              onGoHome={handleGoHome}
              onContactSupport={handleContactSupport}
            />
          )}

          {!loading && !error && results.length > 0 && (
            <div className={selectedView === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 gap-6' : 'space-y-6'}>
              {results.map((result, index) => {
                // Use application_id as the primary key (guaranteed to exist from backend)
                const uniqueKey = `${result.application_id || 'unknown'}-${index}`
                return (
                <div
                  key={uniqueKey}
                  className="bg-white rounded-xl shadow-sm border hover:shadow-lg transition-all duration-200 overflow-hidden group"
                >
                  {/* Card Header */}
                  <div className="p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="text-lg font-semibold text-planning-primary group-hover:text-planning-accent transition-colors">
                            {result.reference}
                          </h3>
                          <div className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(result.status)} flex items-center space-x-1`}>
                            {getStatusIcon(result.status)}
                            <span>{result.status}</span>
                          </div>
                        </div>
                        <p className="text-gray-700 line-clamp-2">
                          {result.description || 'No description available'}
                        </p>
                      </div>
                    </div>

                    {/* Meta Information */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm text-gray-600 mb-4">
                      <div className="flex items-center">
                        <MapPin className="w-4 h-4 mr-2 text-planning-accent" />
                        <span className="truncate">{result.address || 'N/A'}</span>
                      </div>
                      <div className="flex items-center">
                        <Calendar className="w-4 h-4 mr-2 text-planning-accent" />
                        <span>{formatDate(result.submission_date || (result as any).submissionDate)}</span>
                      </div>
                      <div className="flex items-center">
                        <Building2 className="w-4 h-4 mr-2 text-planning-accent" />
                        <span className="truncate">{(result.authority || (result as any).localAuthority || 'N/A').replace(/\)+$/, '')}</span>
                      </div>
                    </div>

                    {/* AI Insights Section */}
                    {result.aiInsights && (
                      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 mb-4">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center space-x-2">
                            <Brain className="w-5 h-5 text-blue-600" />
                            <h4 className="font-semibold text-blue-900">AI Analysis</h4>
                          </div>
                          <div className="flex items-center space-x-3">
                            <div className={`px-3 py-1 rounded-lg border ${getScoreColor(result.aiInsights.score)} font-semibold text-sm flex items-center space-x-1`}>
                              <Target className="w-4 h-4" />
                              <span>Score: {result.aiInsights.score}/100</span>
                            </div>
                            <div className="flex items-center space-x-1 text-sm">
                              <Shield className="w-4 h-4 text-gray-500" />
                              <span className="text-gray-700">
                                {result.aiInsights.confidence}% confidence
                              </span>
                            </div>
                          </div>
                        </div>

                        <div className="space-y-2">
                          <p className="text-sm text-gray-700">
                            <span className="font-medium">Prediction:</span> {result.aiInsights.predictedOutcome}
                          </p>

                          {result.aiInsights.opportunities && result.aiInsights.opportunities.length > 0 && (
                            <div className="flex flex-wrap gap-2 mt-2">
                              {result.aiInsights.opportunities.slice(0, 3).map((opp, idx) => (
                                <span key={idx} className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs">
                                  {opp}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Action Buttons */}
                    <div className="flex items-center justify-between pt-4 border-t">
                      <div className="flex items-center space-x-2">
                        <button className="p-2 text-gray-400 hover:text-planning-primary transition-colors">
                          <Bookmark className="w-5 h-5" />
                        </button>
                        <button className="p-2 text-gray-400 hover:text-planning-primary transition-colors">
                          <Share2 className="w-5 h-5" />
                        </button>
                      </div>
                      <div className="flex items-center space-x-3">
                        <button
                          onClick={() => handleGenerateReport(result)}
                          disabled={!result.application_id}
                          className="px-4 py-2 text-sm font-medium text-planning-primary border border-planning-primary rounded-lg hover:bg-planning-primary hover:text-white transition-colors flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <BarChart3 className="w-4 h-4" />
                          <span>Generate Report</span>
                        </button>
                        <button
                          onClick={() => handleViewDetails(result)}
                          className="px-4 py-2 text-sm font-medium bg-planning-primary text-white rounded-lg hover:bg-planning-accent transition-colors flex items-center space-x-2"
                        >
                          <Eye className="w-4 h-4" />
                          <span>View Details</span>
                          <ChevronRight className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )})})
            </div>
          )}

          {/* Load More */}
          {!loading && !error && results.length > 0 && results.length < totalResults && (
            <div className="text-center mt-8">
              <Button
                onClick={() => {}}
                variant="outline"
                className="px-8"
              >
                Load More Results
              </Button>
            </div>
          )}
        </div>
      </Container>
    </div>
  )
}