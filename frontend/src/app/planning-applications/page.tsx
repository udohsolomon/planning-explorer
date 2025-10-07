'use client'

import { useState, useMemo, useEffect } from 'react'
import Link from 'next/link'
import { Container } from '@/components/ui/Container'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Footer } from '@/components/sections/Footer'
import { PlanningStatsBar } from '@/components/sections/PlanningStatsBar'
import { getAllAuthorities, searchAuthorities } from '@/lib/content-discovery-api'
import { AuthorityListItem } from '@/types/content-discovery'
import {
  Search, MapPin, ArrowRight, Filter,
  Sparkles, ChevronDown, BarChart3,
  FileText, CheckCircle, Clock, TrendingUp
} from 'lucide-react'
import { cn } from '@/lib/utils'

const ITEMS_PER_PAGE = 12

// Authority card with stats fetching
function AuthorityCard({ authority }: { authority: AuthorityListItem }) {
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchStats() {
      try {
        const response = await fetch(`http://localhost:8000/api/v1/stats/authority/${authority.slug}`)
        if (response.ok) {
          const result = await response.json()
          // API returns data directly (no wrapper)
          setStats(result)
        }
      } catch (error) {
        console.error(`Failed to fetch stats for ${authority.slug}:`, error)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [authority.slug])

  return (
    <Link href={`/planning-applications/${authority.slug}`}>
      <Card className="h-full group hover:shadow-2xl transition-all duration-300 cursor-pointer hover:border-planning-primary hover:-translate-y-1">
        <CardHeader className="pb-4">
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1">
              <CardTitle className="text-lg font-bold text-slate-800 group-hover:text-planning-primary transition-colors mb-2">
                {authority.name}
              </CardTitle>
              {authority.region && (
                <Badge variant="outline" size="sm" className="bg-planning-primary/5 text-planning-primary border-planning-primary/20">
                  <MapPin className="w-3 h-3 mr-1" />
                  {authority.region}
                </Badge>
              )}
            </div>
            <div className="w-10 h-10 bg-planning-primary/10 rounded-full flex items-center justify-center group-hover:bg-planning-primary group-hover:scale-110 transition-all">
              <ArrowRight className="w-5 h-5 text-planning-primary group-hover:text-white transition-colors" />
            </div>
          </div>
        </CardHeader>
        <CardContent className="pt-0">
          {/* Stats Grid */}
          {loading ? (
            <div className="grid grid-cols-2 gap-3 mb-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="bg-slate-50 rounded-lg p-3">
                  <div className="h-4 bg-slate-200 rounded animate-pulse mb-2"></div>
                  <div className="h-6 bg-slate-200 rounded animate-pulse"></div>
                </div>
              ))}
            </div>
          ) : stats ? (
            <div className="grid grid-cols-2 gap-3 mb-4">
              <div className="bg-slate-50 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-1">
                  <FileText className="w-4 h-4 text-planning-primary" />
                  <span className="text-xs text-slate-500">Applications</span>
                </div>
                <div className="text-lg font-bold text-slate-800">
                  {stats.total_applications_12m?.toLocaleString() || '0'}
                </div>
              </div>
              <div className="bg-slate-50 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-1">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  <span className="text-xs text-slate-500">Approval</span>
                </div>
                <div className="text-lg font-bold text-green-600">
                  {stats.approval_rate ? `${Math.round(stats.approval_rate)}%` : 'N/A'}
                </div>
              </div>
              <div className="bg-slate-50 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-1">
                  <Clock className="w-4 h-4 text-blue-600" />
                  <span className="text-xs text-slate-500">Avg Decision</span>
                </div>
                <div className="text-lg font-bold text-blue-600">
                  {stats.avg_decision_days ? `${Math.round(stats.avg_decision_days)}d` : 'N/A'}
                </div>
              </div>
              <div className="bg-slate-50 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-1">
                  <TrendingUp className="w-4 h-4 text-orange-600" />
                  <span className="text-xs text-slate-500">Active</span>
                </div>
                <div className="text-lg font-bold text-orange-600">
                  {stats.active_applications?.toLocaleString() || '0'}
                </div>
              </div>
            </div>
          ) : null}

          {/* CTA */}
          <div className="flex items-center justify-between pt-3 border-t border-slate-100">
            <span className="text-sm text-slate-600 group-hover:text-planning-primary transition-colors">
              View Detailed Insights
            </span>
            <Sparkles className="w-4 h-4 text-planning-primary opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}

export default function AuthoritiesListPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedRegion, setSelectedRegion] = useState<string>('all')
  const [displayCount, setDisplayCount] = useState(ITEMS_PER_PAGE)
  const [isLoaded, setIsLoaded] = useState(false)
  const [showFilters, setShowFilters] = useState(false)

  useEffect(() => {
    setIsLoaded(true)
  }, [])

  // Get all authorities (425 authorities)
  const allAuthorities = useMemo(() => getAllAuthorities(), [])

  // Get unique regions
  const regions = useMemo(() => {
    const regionSet = new Set<string>()
    allAuthorities.forEach((auth) => {
      if (auth.region) regionSet.add(auth.region)
    })
    return Array.from(regionSet).sort()
  }, [allAuthorities])

  // Filter authorities based on search and region
  const filteredAuthorities = useMemo(() => {
    let filtered = searchAuthorities(searchQuery, allAuthorities)

    if (selectedRegion !== 'all') {
      filtered = filtered.filter((auth) => auth.region === selectedRegion)
    }

    return filtered.sort((a, b) => a.name.localeCompare(b.name))
  }, [searchQuery, selectedRegion, allAuthorities])

  // Paginated authorities
  const displayedAuthorities = useMemo(() => {
    return filteredAuthorities.slice(0, displayCount)
  }, [filteredAuthorities, displayCount])

  const hasMore = displayCount < filteredAuthorities.length

  const loadMore = () => {
    setDisplayCount(prev => Math.min(prev + ITEMS_PER_PAGE, filteredAuthorities.length))
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Hero Section - Brand Styled */}
      <section className="relative z-20 bg-gradient-to-br from-planning-primary via-planning-primary to-planning-accent overflow-hidden">
        {/* Hero Background Image */}
        <div className="absolute inset-0 overflow-hidden">
          <div
            className="w-full h-full bg-cover bg-center bg-no-repeat opacity-20"
            style={{
              backgroundImage: `url('https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1920&h=1080&fit=crop&crop=center')`
            }}
          />
          <div className="absolute inset-0 bg-gradient-to-br from-planning-primary/90 via-planning-primary/85 to-planning-accent/90"></div>
        </div>

        {/* Animated Background Elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-10 w-64 h-64 bg-planning-bright/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-planning-button/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
        </div>

        {/* Main Content */}
        <div className="relative z-10 py-16 md:py-24">
          <Container>
            <div className="max-w-4xl mx-auto text-center">
              {/* Badge */}
              <div className={cn(
                'inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full border border-white/20 mb-6',
                'transform transition-all duration-700 delay-200',
                isLoaded ? 'translate-y-0 opacity-100' : 'translate-y-8 opacity-0'
              )}>
                <Sparkles className="w-4 h-4 text-planning-bright animate-pulse" />
                <span className="text-sm font-semibold text-white">✨ AI-Powered Planning Intelligence</span>
              </div>

              {/* Title */}
              <h1 className={cn(
                'text-4xl md:text-5xl lg:text-6xl font-bold mb-6 leading-tight',
                'transform transition-all duration-700 delay-400',
                isLoaded ? 'translate-y-0 opacity-100' : 'translate-y-8 opacity-0'
              )} style={{ color: '#FFFFFF' }}>
                UK Planning Applications by Local Authority
              </h1>

              {/* Description */}
              <p className={cn(
                'text-lg md:text-xl text-white/90 mb-10 leading-relaxed max-w-3xl mx-auto',
                'transform transition-all duration-700 delay-600',
                isLoaded ? 'translate-y-0 opacity-100' : 'translate-y-8 opacity-0'
              )}>
                Browse planning applications from 425+ UK local planning authorities.
                Access real-time statistics, approval rates, decision times, and AI-powered insights.
              </p>

              {/* Enhanced Search Bar */}
              <div className={cn(
                'relative max-w-3xl mx-auto',
                'transform transition-all duration-700 delay-800',
                isLoaded ? 'translate-y-0 opacity-100' : 'translate-y-8 opacity-0'
              )}>
                <div className="relative group">
                  <div className="absolute -inset-1 bg-gradient-to-r from-planning-bright to-planning-button rounded-2xl blur opacity-25 group-hover:opacity-40 transition duration-300"></div>
                  <div className="relative">
                    <Search className="absolute left-5 top-1/2 -translate-y-1/2 w-6 h-6 text-slate-400 group-hover:text-planning-primary transition-colors" />
                    <Input
                      type="text"
                      placeholder="Search by authority name or region..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-full pl-14 pr-14 py-5 text-base bg-white border-2 border-white/20 shadow-2xl rounded-xl focus:ring-4 focus:ring-planning-bright/50 focus:border-planning-bright transition-all font-medium placeholder:text-slate-400"
                    />
                    {searchQuery ? (
                      <button
                        onClick={() => setSearchQuery('')}
                        className="absolute right-5 top-1/2 -translate-y-1/2 p-1 rounded-full bg-slate-100 text-slate-600 hover:bg-slate-200 hover:text-slate-800 transition-all"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    ) : (
                      <div className="absolute right-5 top-1/2 -translate-y-1/2 flex items-center gap-1.5 px-2.5 py-1 bg-planning-primary/10 rounded-md">
                        <Sparkles className="w-3.5 h-3.5 text-planning-primary" />
                        <span className="text-xs font-semibold text-planning-primary">AI Search</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </Container>
        </div>
      </section>

      {/* Planning Stats Bar - Real Data from API */}
      <PlanningStatsBar />

      {/* Filters and Results */}
      <Container className="py-12">
        {/* Filter Toggle Button (Mobile) */}
        <div className="mb-6 md:hidden">
          <Button
            onClick={() => setShowFilters(!showFilters)}
            variant="outline"
            className="w-full justify-between"
          >
            <span className="flex items-center gap-2">
              <Filter className="w-4 h-4" />
              Filter by Region
            </span>
            {showFilters ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </Button>
        </div>

        {/* Enhanced Region Filter Pills */}
        <div className={cn(
          'mb-8 transition-all duration-300',
          showFilters || 'md:block hidden'
        )}>
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
            <div className="flex items-center gap-3 mb-5">
              <div className="p-2 bg-planning-primary/10 rounded-lg">
                <Filter className="w-5 h-5 text-planning-primary" />
              </div>
              <div>
                <p className="text-base font-bold text-slate-800">Filter by Region</p>
                <p className="text-xs text-slate-500">Narrow down authorities by UK region</p>
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setSelectedRegion('all')}
                className={cn(
                  'px-5 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200',
                  selectedRegion === 'all'
                    ? 'bg-planning-primary text-white shadow-lg shadow-planning-primary/30 scale-105'
                    : 'bg-slate-50 text-slate-700 border border-slate-200 hover:bg-slate-100 hover:border-planning-primary/30 hover:scale-102'
                )}
              >
                <span className="flex items-center gap-2">
                  All Regions
                  <span className="px-2 py-0.5 bg-white/20 rounded-full text-xs">{allAuthorities.length}</span>
                </span>
              </button>
              {regions.map((region) => {
                const count = allAuthorities.filter((a) => a.region === region).length
                return (
                  <button
                    key={region}
                    onClick={() => setSelectedRegion(region)}
                    className={cn(
                      'px-5 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200',
                      selectedRegion === region
                        ? 'bg-planning-primary text-white shadow-lg shadow-planning-primary/30 scale-105'
                        : 'bg-slate-50 text-slate-700 border border-slate-200 hover:bg-slate-100 hover:border-planning-primary/30 hover:scale-102'
                    )}
                  >
                    <span className="flex items-center gap-2">
                      {region}
                      <span className={cn(
                        'px-2 py-0.5 rounded-full text-xs',
                        selectedRegion === region ? 'bg-white/20' : 'bg-slate-200'
                      )}>{count}</span>
                    </span>
                  </button>
                )
              })}
            </div>
          </div>
        </div>

        {/* Results Count */}
        <div className="mb-6 flex items-center justify-between">
          <p className="text-sm text-slate-600">
            Showing <span className="font-bold text-planning-primary">{displayedAuthorities.length}</span> of{' '}
            <span className="font-bold">{filteredAuthorities.length}</span> authorities
            {searchQuery && ` matching "${searchQuery}"`}
            {selectedRegion !== 'all' && ` in ${selectedRegion}`}
          </p>
          {filteredAuthorities.length > 0 && (
            <div className="hidden md:flex items-center gap-2 text-sm text-slate-500">
              <BarChart3 className="w-4 h-4" />
              <span>Stats Updated Daily</span>
            </div>
          )}
        </div>

        {/* Authorities Grid */}
        {filteredAuthorities.length === 0 ? (
          <Card className="border-2 border-dashed">
            <CardContent className="py-16 text-center">
              <div className="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <Search className="w-10 h-10 text-slate-400" />
              </div>
              <h3 className="text-xl font-bold text-slate-700 mb-2">No Authorities Found</h3>
              <p className="text-slate-600 mb-6 max-w-md mx-auto">
                We couldn't find any authorities matching your search criteria. Try adjusting your filters or search terms.
              </p>
              <Button
                onClick={() => {
                  setSearchQuery('')
                  setSelectedRegion('all')
                }}
                variant="primary"
                className="mx-auto"
              >
                Clear All Filters
              </Button>
            </CardContent>
          </Card>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {displayedAuthorities.map((authority) => (
                <AuthorityCard key={authority.slug} authority={authority} />
              ))}
            </div>

            {/* Load More Button */}
            {hasMore && (
              <div className="mt-12 text-center">
                <Button
                  onClick={loadMore}
                  size="lg"
                  variant="outline"
                  className="group"
                >
                  Load More Authorities
                  <ChevronDown className="ml-2 w-4 h-4 group-hover:translate-y-1 transition-transform" />
                </Button>
                <p className="mt-4 text-sm text-slate-500">
                  Showing {displayedAuthorities.length} of {filteredAuthorities.length} results
                </p>
              </div>
            )}

            {/* All Loaded Message */}
            {!hasMore && filteredAuthorities.length > ITEMS_PER_PAGE && (
              <div className="mt-12 text-center">
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-50 text-green-700 rounded-full">
                  <CheckCircle className="w-4 h-4" />
                  <span className="text-sm font-medium">All authorities loaded</span>
                </div>
              </div>
            )}
          </>
        )}
      </Container>

      {/* Footer */}
      <Footer />
    </div>
  )
}
