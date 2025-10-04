'use client'

import { useState } from 'react'
import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import { SemanticSearchBar } from '@/components/ai/SemanticSearchBar'
import { SmartSuggestions } from '@/components/ai/SmartSuggestions'
import { AISearchAnimation } from '@/components/search/animation/AISearchAnimation'
import { Search, Filter, MapPin, Calendar, Building, ChevronDown, Brain, Sparkles } from 'lucide-react'
import { useSearchStore } from '@/lib/store'
import { apiClient } from '@/lib/api'

interface SearchFilters {
  query: string
  location: string
  applicationStatus: string
  applicationType: string
  dateFrom: string
  dateTo: string
  postcode: string
}

const applicationStatuses = [
  { value: '', label: 'All Statuses' },
  { value: 'pending', label: 'Pending' },
  { value: 'approved', label: 'Approved' },
  { value: 'refused', label: 'Refused' },
  { value: 'withdrawn', label: 'Withdrawn' }
]

const applicationTypes = [
  { value: '', label: 'All Types' },
  { value: 'full', label: 'Full Planning' },
  { value: 'outline', label: 'Outline Planning' },
  { value: 'reserved', label: 'Reserved Matters' },
  { value: 'minor', label: 'Minor Development' },
  { value: 'major', label: 'Major Development' },
  { value: 'householder', label: 'Householder' }
]

export function SearchInterface() {
  const [filters, setFilters] = useState<SearchFilters>({
    query: '',
    location: '',
    applicationStatus: '',
    applicationType: '',
    dateFrom: '',
    dateTo: '',
    postcode: ''
  })
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false)
  const [isSearching, setIsSearching] = useState(false)
  const [showAISearch, setShowAISearch] = useState(true)
  const [showSmartSuggestions, setShowSmartSuggestions] = useState(false)
  const [showAnimation, setShowAnimation] = useState(false)
  const [currentQuery, setCurrentQuery] = useState('')
  const [currentSearchType, setCurrentSearchType] = useState<'semantic' | 'keyword' | 'hybrid'>('semantic')

  const {
    searchType,
    setQuery,
    setResults,
    setLoading,
    setError,
    setLastSearchResult
  } = useSearchStore()

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFilters(prev => ({ ...prev, [name]: value }))
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    await performSearch(filters.query, searchType)
  }

  const handleAISearch = async (query: string, searchType: 'traditional' | 'semantic' | 'natural_language') => {
    console.log('🎯 handleAISearch called:', { query, searchType })
    // Prevent default navigation for AI searches - handle it ourselves
    await performSearch(query, searchType)
    console.log('✅ performSearch completed')
  }

  const performSearch = async (query: string, type: 'traditional' | 'semantic' | 'natural_language') => {
    console.log('🚀 performSearch called:', { query, type })

    setIsSearching(true)
    setLoading(true)
    setError(null)

    // Show animation for semantic/AI searches
    if (type === 'semantic' || type === 'natural_language') {
      console.log('✨ Showing animation for AI search')
      setShowAnimation(true)
      setCurrentQuery(query)
      setCurrentSearchType(type === 'semantic' ? 'semantic' : 'hybrid')
    }

    try {
      setQuery(query)

      let response
      const searchFilters = {
        location: filters.location,
        applicationType: filters.applicationType,
        status: filters.applicationStatus,
        dateFrom: filters.dateFrom,
        dateTo: filters.dateTo,
        postcode: filters.postcode,
      }

      const startTime = Date.now()

      switch (type) {
        case 'semantic':
          response = await apiClient.semanticSearch(query, searchFilters, 50)
          break
        case 'natural_language':
          response = await apiClient.naturalLanguageSearch(query, searchFilters, 50)
          break
        default:
          response = await apiClient.searchPlanningApplications({
            query,
            ...searchFilters,
            limit: 50,
            offset: 0
          })
      }

      const processingTime = Date.now() - startTime

      if (response.success) {
        setResults(response.data as any)

        // Store AI search result
        setLastSearchResult({
          query,
          searchType: type,
          results: response.data as any,
          suggestions: (response.meta as any)?.suggestions || [],
          processingTimeMs: processingTime,
          totalResults: response.meta?.total || response.data.length,
          timestamp: new Date().toISOString()
        })

        console.log(`${type} search completed:`, response.data)
      } else {
        throw new Error(response.message || 'Search failed')
      }
    } catch (error) {
      console.error('Search error:', error)
      setError(`Search failed: ${error}`)
    } finally {
      setIsSearching(false)
      setLoading(false)
      // Animation will close itself after completion
    }
  }

  const resetFilters = () => {
    setFilters({
      query: '',
      location: '',
      applicationStatus: '',
      applicationType: '',
      dateFrom: '',
      dateTo: '',
      postcode: ''
    })
  }

  return (
    <section className="py-24 bg-gradient-to-br from-gray-50 to-white">
      <Container>
        {/* Section Header */}
        <div className="text-center mb-12">
          <div className="inline-block px-4 py-2 bg-planning-button/10 rounded-full mb-6">
            <span className="text-planning-primary font-medium text-sm uppercase tracking-wider">
              AI-Powered Planning Search
            </span>
          </div>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-heading font-bold text-planning-primary mb-6">
            Find Planning Opportunities
          </h2>
          <p className="text-lg text-planning-text-light max-w-3xl mx-auto leading-relaxed">
            Search through millions of UK planning applications with our advanced AI-powered semantic search and natural language processing.
          </p>
        </div>

        {/* AI Search Toggle */}
        <div className="max-w-5xl mx-auto mb-6">
          <div className="flex items-center justify-center space-x-4">
            <button
              onClick={() => setShowAISearch(!showAISearch)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-full transition-colors ${
                showAISearch
                  ? 'bg-planning-primary text-white'
                  : 'bg-planning-border text-planning-text-light hover:bg-planning-primary/10'
              }`}
            >
              <Brain className="w-4 h-4" />
              <span>AI Search</span>
              {showAISearch && <Sparkles className="w-3 h-3" />}
            </button>
            <button
              onClick={() => setShowSmartSuggestions(!showSmartSuggestions)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-full transition-colors ${
                showSmartSuggestions
                  ? 'bg-planning-accent text-white'
                  : 'bg-planning-border text-planning-text-light hover:bg-planning-accent/10'
              }`}
            >
              <Sparkles className="w-4 h-4" />
              <span>Smart Suggestions</span>
            </button>
          </div>
        </div>

        {/* Search Interface */}
        <div className="max-w-5xl mx-auto">
          {/* AI Search Interface */}
          {showAISearch ? (
            <div className="space-y-6">
              <SemanticSearchBar
                placeholder="Try: 'Show me approved residential developments in London from 2024' or use traditional search"
                showSuggestions={true}
                showSearchType={true}
                onSearch={handleAISearch}
                className="shadow-lg"
              />

              {/* Traditional Search Fallback */}
              <div className="text-center">
                <button
                  onClick={() => setShowAISearch(false)}
                  className="text-sm text-planning-text-light hover:text-planning-primary transition-colors"
                >
                  Switch to traditional search interface
                </button>
              </div>
            </div>
          ) : (
            /* Traditional Search Interface */
            <form onSubmit={handleSearch} className="space-y-6">
              {/* Main Search Bar */}
              <div className="bg-white rounded-2xl p-6 shadow-lg border border-planning-border">
                <div className="flex flex-col lg:flex-row gap-4">
                  {/* Search Query */}
                  <div className="flex-1">
                    <div className="relative">
                      <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-planning-text-light w-5 h-5" />
                      <input
                        type="text"
                        name="query"
                        value={filters.query}
                        onChange={handleInputChange}
                        placeholder="Search by keyword, address, or reference number..."
                        className="w-full pl-12 pr-4 py-4 border border-planning-border rounded-xl focus:ring-2 focus:ring-planning-primary focus:border-planning-primary transition-colors text-lg"
                      />
                    </div>
                  </div>

                  {/* Location */}
                  <div className="lg:w-64">
                    <div className="relative">
                      <MapPin className="absolute left-4 top-1/2 transform -translate-y-1/2 text-planning-text-light w-5 h-5" />
                      <input
                        type="text"
                        name="location"
                        value={filters.location}
                        onChange={handleInputChange}
                        placeholder="Location or postcode"
                        className="w-full pl-12 pr-4 py-4 border border-planning-border rounded-xl focus:ring-2 focus:ring-planning-primary focus:border-planning-primary transition-colors"
                      />
                    </div>
                  </div>

                  {/* Search Button */}
                  <Button
                    type="submit"
                    disabled={isSearching}
                    className="px-8 py-4 text-lg"
                    size="lg"
                  >
                    {isSearching ? (
                      <>
                        <div className="w-5 h-5 border-2 border-planning-primary border-t-transparent rounded-full animate-spin mr-2" />
                        Searching...
                      </>
                    ) : (
                      'Search'
                    )}
                  </Button>
                </div>

                {/* AI Enhancement Suggestion */}
                <div className="mt-4 pt-4 border-t border-planning-border">
                  <div className="flex items-center justify-between">
                    <button
                      type="button"
                      onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                      className="flex items-center space-x-2 text-planning-primary hover:text-planning-accent transition-colors"
                    >
                      <Filter className="w-4 h-4" />
                      <span className="font-medium">Advanced Filters</span>
                      <ChevronDown className={`w-4 h-4 transition-transform ${showAdvancedFilters ? 'rotate-180' : ''}`} />
                    </button>

                    <div className="flex items-center space-x-4">
                      <button
                        type="button"
                        onClick={() => setShowAISearch(true)}
                        className="flex items-center space-x-2 text-planning-bright hover:text-planning-highlight transition-colors text-sm font-medium"
                      >
                        <Brain className="w-4 h-4" />
                        <span>Try AI Search</span>
                      </button>
                      <button
                        type="button"
                        onClick={resetFilters}
                        className="text-planning-text-light hover:text-planning-primary transition-colors text-sm"
                      >
                        Reset All
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </form>
          )}

          {/* Smart Suggestions */}
          {showSmartSuggestions && (
            <div className="mt-6">
              <SmartSuggestions
                context="search"
                location={filters.location}
                maxSuggestions={6}
                className="shadow-lg"
                onSuggestionClick={(suggestion) => {
                  // Handle suggestion click - could trigger a search or action
                  console.log('Suggestion clicked:', suggestion)
                }}
              />
            </div>
          )}

            {/* Advanced Filters */}
            {showAdvancedFilters && (
              <div className="bg-white rounded-2xl p-6 shadow-lg border border-planning-border">
                <h3 className="font-heading font-semibold text-planning-primary mb-4">
                  Advanced Search Options
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {/* Application Status */}
                  <div>
                    <label className="block text-sm font-medium text-planning-primary mb-2">
                      Application Status
                    </label>
                    <select
                      name="applicationStatus"
                      value={filters.applicationStatus}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 border border-planning-border rounded-lg focus:ring-2 focus:ring-planning-primary focus:border-planning-primary transition-colors"
                    >
                      {applicationStatuses.map((status) => (
                        <option key={status.value} value={status.value}>
                          {status.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Application Type */}
                  <div>
                    <label className="block text-sm font-medium text-planning-primary mb-2">
                      Application Type
                    </label>
                    <select
                      name="applicationType"
                      value={filters.applicationType}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 border border-planning-border rounded-lg focus:ring-2 focus:ring-planning-primary focus:border-planning-primary transition-colors"
                    >
                      {applicationTypes.map((type) => (
                        <option key={type.value} value={type.value}>
                          {type.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Postcode */}
                  <div>
                    <label className="block text-sm font-medium text-planning-primary mb-2">
                      Postcode
                    </label>
                    <input
                      type="text"
                      name="postcode"
                      value={filters.postcode}
                      onChange={handleInputChange}
                      placeholder="SW1A 1AA"
                      className="w-full px-4 py-3 border border-planning-border rounded-lg focus:ring-2 focus:ring-planning-primary focus:border-planning-primary transition-colors"
                    />
                  </div>

                  {/* Date From */}
                  <div>
                    <label className="block text-sm font-medium text-planning-primary mb-2">
                      <Calendar className="inline w-4 h-4 mr-1" />
                      Date From
                    </label>
                    <input
                      type="date"
                      name="dateFrom"
                      value={filters.dateFrom}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 border border-planning-border rounded-lg focus:ring-2 focus:ring-planning-primary focus:border-planning-primary transition-colors"
                    />
                  </div>

                  {/* Date To */}
                  <div>
                    <label className="block text-sm font-medium text-planning-primary mb-2">
                      <Calendar className="inline w-4 h-4 mr-1" />
                      Date To
                    </label>
                    <input
                      type="date"
                      name="dateTo"
                      value={filters.dateTo}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 border border-planning-border rounded-lg focus:ring-2 focus:ring-planning-primary focus:border-planning-primary transition-colors"
                    />
                  </div>

                  {/* Additional space for alignment */}
                  <div></div>
                </div>
              </div>
            )}

          {/* Quick Search Examples */}
          <div className="mt-8">
            <p className="text-sm text-planning-text-light mb-4">
              {showAISearch ? 'Try these AI-powered searches:' : 'Popular searches:'}
            </p>
            <div className="flex flex-wrap gap-2">
              {(showAISearch ? [
                'Show me high scoring residential developments approved in the last 6 months',
                'Find commercial applications with low risk factors near SW1A',
                'What planning trends are emerging in Manchester this year?',
                'Compare approval rates for housing developments across London boroughs'
              ] : [
                'Residential developments in London',
                'Approved applications 2024',
                'Commercial properties Manchester',
                'Planning appeals Birmingham'
              ]).map((example: string, index: number) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => {
                    if (showAISearch) {
                      handleAISearch(example, 'natural_language')
                    } else {
                      setFilters(prev => ({ ...prev, query: example }))
                    }
                  }}
                  className={`px-4 py-2 rounded-full text-sm transition-colors ${
                    showAISearch
                      ? 'bg-planning-bright/10 text-planning-bright hover:bg-planning-bright/20'
                      : 'bg-planning-primary/5 text-planning-primary hover:bg-planning-primary/10'
                  }`}
                >
                  {showAISearch && <Brain className="w-3 h-3 inline mr-1" />}
                  {example}
                </button>
              ))}
            </div>
          </div>

          {/* Search Tips */}
          <div className="mt-8 bg-planning-button/5 rounded-xl p-6">
            <h4 className="font-semibold text-planning-primary mb-3 flex items-center space-x-2">
              {showAISearch && <Brain className="w-4 h-4" />}
              <span>{showAISearch ? 'AI Search Tips:' : 'Search Tips:'}</span>
            </h4>
            <ul className="text-sm text-planning-text-light space-y-1">
              {showAISearch ? (
                <>
                  <li>• Ask questions naturally: "What residential projects were approved in Westminster last month?"</li>
                  <li>• Use semantic search to find similar meanings: "housing" will also find "residential", "apartments", "dwellings"</li>
                  <li>• Describe what you're looking for: "sustainable development with good approval chances"</li>
                  <li>• Compare and analyze: "Compare approval rates between different London boroughs"</li>
                  <li>• Search by concepts: "low-risk opportunities" or "high-opportunity projects"</li>
                </>
              ) : (
                <>
                  <li>• Use quotation marks for exact phrases: "residential development"</li>
                  <li>• Combine keywords with AND/OR: housing AND affordable</li>
                  <li>• Use wildcards for partial matches: develop*</li>
                  <li>• Search by planning reference: 2024/01234/FUL</li>
                </>
              )}
            </ul>
            {showAISearch && (
              <div className="mt-3 pt-3 border-t border-planning-primary/20">
                <p className="text-xs text-planning-bright">
                  💡 AI search understands context and meaning, not just keywords. Try asking questions like you would to a planning expert!
                </p>
              </div>
            )}
          </div>
        </div>

        {/* AI Search Animation */}
        {showAnimation && (
          <AISearchAnimation
            query={currentQuery}
            searchType={currentSearchType}
            onComplete={() => {
              setShowAnimation(false)
              console.log('AI search animation completed')
            }}
            onCancel={() => {
              setShowAnimation(false)
              setIsSearching(false)
              setLoading(false)
              console.log('AI search animation cancelled')
            }}
            onError={(error) => {
              console.error('Animation error:', error)
              setShowAnimation(false)
            }}
          />
        )}
      </Container>
    </section>
  )
}