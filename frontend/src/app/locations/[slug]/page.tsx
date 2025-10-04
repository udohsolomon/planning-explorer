'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { MapPin, TrendingUp, FileText, Clock, CheckCircle2, Building2, Users } from 'lucide-react'
import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/Select'
import { StatsCard, StatsCardGrid } from '@/components/discovery/StatsCard'
import { ApplicationsTable } from '@/components/discovery/ApplicationsTable'
import { FreemiumGate } from '@/components/discovery/FreemiumGate'
import { PlanningMap } from '@/components/maps/PlanningMap'
import { StructuredData } from '@/components/seo/StructuredData'
import { getLocationStats, getApplicationsNearby } from '@/lib/content-discovery-api'
import { getLocationCoordinates } from '@/lib/map-config'
import type { Application, LocationStats } from '@/types/content-discovery'

// Planning Explorer original brand color
const BRAND_COLOR = '#7CB342'

export default function LocationDetailPage() {
  const params = useParams()
  const slug = params?.slug as string

  const [stats, setStats] = useState<LocationStats | null>(null)
  const [applications, setApplications] = useState<Application[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filter state
  const [dateRange, setDateRange] = useState('12m')
  const [statusFilter, setStatusFilter] = useState('all')
  const [sectorFilter, setSectorFilter] = useState('all')
  const [sortBy, setSortBy] = useState('date')
  const [radius, setRadius] = useState('5')

  useEffect(() => {
    async function fetchData() {
      if (!slug) return

      setLoading(true)
      setError(null)

      try {
        // Try to fetch location stats from API
        try {
          const statsResponse = await getLocationStats(slug, Number(radius))
          if (statsResponse.success && statsResponse.data) {
            setStats(statsResponse.data)
          } else {
            throw new Error('Location not found')
          }
        } catch (apiError) {
          // Fallback: Use hardcoded coordinates for known cities
          console.warn('Location stats API not ready, using fallback coordinates:', apiError)
          const coordinates = getLocationCoordinates(slug)

          setStats({
            location_name: coordinates.name,
            location_type: 'City',
            total_applications: 0,
            authorities: [],
            sector_breakdown: [],
            avg_decision_days: 0,
            approval_rate: 0,
            active_applications: 0,
            most_common_sector: null,
            coordinates: { lat: coordinates.lat, lng: coordinates.lng },
          })
        }

        // Fetch applications nearby for map display
        const coordinates = stats?.coordinates || getLocationCoordinates(slug)
        try {
          const appsResponse = await getApplicationsNearby(
            coordinates.lat,
            coordinates.lng,
            Number(radius)
          )
          if (appsResponse.success && appsResponse.data) {
            setApplications(appsResponse.data.applications || [])
          }
        } catch (appError) {
          console.warn('Applications nearby API not ready:', appError)
          // Continue without applications
        }
      } catch (err) {
        console.error('Error fetching location data:', err)
        setError(err instanceof Error ? err.message : 'An unexpected error occurred')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [slug, radius, dateRange, statusFilter, sectorFilter, sortBy])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Container className="py-16">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-[#7CB342] mx-auto mb-4"></div>
              <p className="text-gray-600 text-lg">Loading location data...</p>
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
              <MapPin className="w-16 h-16 text-red-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Location Not Found</h2>
              <p className="text-gray-600 mb-6">
                {error || 'Unable to load location data. Please check that the location slug is correct.'}
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
  const approvalRatePercent = (stats.approval_rate * 100).toFixed(1)

  return (
    <>
      {/* SEO Structured Data */}
      <StructuredData
        schema={[
          {
            type: 'Place',
            name: stats.location_name,
            description: `Planning applications and statistics for ${stats.location_name}`,
            geo: {
              latitude: stats.coordinates.lat,
              longitude: stats.coordinates.lng,
            },
            url: `https://planningexplorer.com/locations/${slug}`,
          },
          {
            type: 'Dataset',
            name: `Planning Applications in ${stats.location_name}`,
            description: `Comprehensive dataset of planning applications in ${stats.location_name}. Includes approval rates, decision times, and sector analysis.`,
            url: `https://planningexplorer.com/locations/${slug}`,
            creator: {
              name: 'Planning Explorer',
              url: 'https://planningexplorer.com',
            },
            datePublished: new Date().toISOString().split('T')[0],
            keywords: [
              'planning applications',
              stats.location_name,
              'UK planning',
              'development',
              'planning permission',
            ],
          },
        ]}
      />

      <div className="min-h-screen bg-gray-50">
        {/* ========================================
            HERO SECTION
            ======================================== */}
        <div className="bg-white border-b border-gray-200">
          <Container className="py-12">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div className="flex-1">
                <nav className="flex items-center space-x-2 text-sm text-gray-600 mb-3">
                  <a href="/" className="hover:text-[#7CB342] transition-colors">Home</a>
                  <span>/</span>
                  <a href="/locations" className="hover:text-[#7CB342] transition-colors">Locations</a>
                  <span>/</span>
                  <span className="text-gray-900 font-medium">{stats.location_name}</span>
                </nav>
                <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-3">
                  Planning Applications in {stats.location_name}
                </h1>
                <div className="flex items-center gap-3 mb-3">
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-[#7CB342]/10 text-[#7CB342]">
                    {stats.location_type}
                  </span>
                  {stats.authorities.length > 0 && (
                    <span className="text-sm text-gray-600">
                      {stats.authorities.length} {stats.authorities.length === 1 ? 'Authority' : 'Authorities'}
                    </span>
                  )}
                </div>
                <p className="text-lg text-gray-600">
                  Explore planning applications and development trends in {stats.location_name}
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  Last updated: {lastUpdated}
                </p>
              </div>
              <Button size="lg" className="bg-[#7CB342] hover:bg-[#689F38] shrink-0">
                Get Alerts for This Location
              </Button>
            </div>
          </Container>
        </div>

        {/* ========================================
            KEY STATS PANEL
            ======================================== */}
        <Container className="py-8">
          <StatsCardGrid>
            <StatsCard
              title="Total Applications"
              value={stats.total_applications.toLocaleString()}
              description="Within search radius"
              icon={<FileText className="w-5 h-5" />}
            />
            <StatsCard
              title="Active"
              value={stats.active_applications.toLocaleString()}
              description="Current Applications"
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
              title="Top Sector"
              value={stats.most_common_sector?.sector || 'N/A'}
              description={stats.most_common_sector ? `${stats.most_common_sector.percentage.toFixed(1)}% of applications` : 'No data available'}
              icon={<Building2 className="w-5 h-5" />}
            />
            <StatsCard
              title="Authorities"
              value={stats.authorities.length || 1}
              description={stats.authorities[0] || 'Coverage area'}
              icon={<Users className="w-5 h-5" />}
            />
          </StatsCardGrid>
        </Container>

        {/* ========================================
            FILTERS & SORT (Sticky)
            ======================================== */}
        <div className="sticky top-0 z-10 bg-white border-y border-gray-200 shadow-sm">
          <Container className="py-4">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1 grid grid-cols-2 md:grid-cols-5 gap-3">
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
                      {stats.sector_breakdown.slice(0, 10).map((sector) => (
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
                      <SelectItem value="distance">Distance (Nearest)</SelectItem>
                      <SelectItem value="score">Opportunity Score</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-xs font-medium text-gray-700 mb-1 block">Radius</label>
                  <Select value={radius} onValueChange={setRadius}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">1 km</SelectItem>
                      <SelectItem value="3">3 km</SelectItem>
                      <SelectItem value="5">5 km</SelectItem>
                      <SelectItem value="10">10 km</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>
          </Container>
        </div>

        {/* ========================================
            INTERACTIVE MAP (Full-screen)
            ======================================== */}
        <Container className="py-8">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Interactive Map</h2>
            <p className="text-gray-600">
              Explore {applications.length.toLocaleString()} planning applications on the map
            </p>
          </div>

          {applications.length > 0 ? (
            <PlanningMap
              applications={applications}
              center={[stats.coordinates.lat, stats.coordinates.lng]}
              zoom={13}
              height="700px"
              showBasemapSwitcher={true}
              showLegend={true}
              className="mb-8"
            />
          ) : (
            <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
              <MapPin className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-600 mb-2">Map data not available</p>
              <p className="text-sm text-gray-500">
                The backend API endpoint for nearby applications is not yet implemented.
              </p>
            </div>
          )}
        </Container>

        {/* ========================================
            APPLICATION LIST (DataTable)
            ======================================== */}
        <Container className="py-8">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Planning Applications</h2>
            <p className="text-gray-600">
              Recent applications within {radius}km of {stats.location_name}
            </p>
          </div>

          {applications.length > 0 ? (
            <>
              <ApplicationsTable
                applications={applications}
                showFreemiumGate={true}
                freeLimit={5}
                showMapLink={true}
              />
            </>
          ) : (
            <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
              <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-600 mb-2">No applications found</p>
              <p className="text-sm text-gray-500">
                Try adjusting your filters or increasing the search radius.
              </p>
            </div>
          )}
        </Container>

        {/* ========================================
            RELATED CONTENT SECTION
            ======================================== */}
        <Container className="py-8 pb-16">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Related Content</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Nearby Locations</h4>
                <p className="text-sm text-gray-600 mb-3">
                  Explore planning applications in nearby areas
                </p>
                <ul className="space-y-1">
                  <li>
                    <a href="/locations/manchester" className="text-sm text-[#7CB342] hover:underline">
                      Manchester
                    </a>
                  </li>
                  <li>
                    <a href="/locations/birmingham" className="text-sm text-[#7CB342] hover:underline">
                      Birmingham
                    </a>
                  </li>
                  <li>
                    <a href="/locations/london" className="text-sm text-[#7CB342] hover:underline">
                      London
                    </a>
                  </li>
                </ul>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 mb-2">Related Sectors</h4>
                <p className="text-sm text-gray-600 mb-3">
                  View applications by sector type
                </p>
                <ul className="space-y-1">
                  {stats.sector_breakdown.slice(0, 3).map((sector) => (
                    <li key={sector.sector}>
                      <a
                        href={`/sectors/${sector.sector.toLowerCase().replace(/\s+/g, '-')}`}
                        className="text-sm text-[#7CB342] hover:underline"
                      >
                        {sector.sector} ({sector.count} applications)
                      </a>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 mb-2">Popular Authorities</h4>
                <p className="text-sm text-gray-600 mb-3">
                  Explore other local planning authorities
                </p>
                <ul className="space-y-1">
                  {stats.authorities.slice(0, 3).map((authority) => (
                    <li key={authority}>
                      <a
                        href={`/authorities/${authority.toLowerCase().replace(/\s+/g, '-')}`}
                        className="text-sm text-[#7CB342] hover:underline"
                      >
                        {authority}
                      </a>
                    </li>
                  ))}
                  {stats.authorities.length === 0 && (
                    <li className="text-sm text-gray-500">No authorities available</li>
                  )}
                </ul>
              </div>
            </div>
          </div>
        </Container>
      </div>
    </>
  )
}
