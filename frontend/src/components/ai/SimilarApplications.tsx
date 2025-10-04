'use client'

import { useState, useEffect } from 'react'
import {
  Search,
  ExternalLink,
  MapPin,
  Calendar,
  CheckCircle,
  AlertTriangle,
  Clock,
  Building,
  TrendingUp,
  Copy,
  Filter,
  RefreshCw,
  Brain
} from 'lucide-react'
import { PlanningApplication } from '@/lib/store'
import { apiClient } from '@/lib/api'

interface SimilarApplication extends PlanningApplication {
  similarityScore: number
  similarityFactors: string[]
  matchReason: string
}

interface SimilarApplicationsProps {
  applicationId?: string
  application?: PlanningApplication
  maxResults?: number
  minSimilarity?: number
  showFilters?: boolean
  autoLoad?: boolean
  className?: string
  onApplicationClick?: (application: SimilarApplication) => void
}

export function SimilarApplications({
  applicationId,
  application,
  maxResults = 5,
  minSimilarity = 0.7,
  showFilters = true,
  autoLoad = true,
  className = '',
  onApplicationClick
}: SimilarApplicationsProps) {
  const [similarApplications, setSimilarApplications] = useState<SimilarApplication[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState({
    status: 'all',
    dateRange: 'all',
    developmentType: 'all',
    distance: 10 // km
  })
  const [expandedApp, setExpandedApp] = useState<string | null>(null)

  useEffect(() => {
    if (autoLoad && (applicationId || application)) {
      fetchSimilarApplications()
    }
  }, [applicationId, application, autoLoad])

  const fetchSimilarApplications = async () => {
    setIsLoading(true)
    setError(null)

    try {
      // Mock data since we don't have the exact endpoint implemented yet
      // In a real implementation, this would call the vector similarity search endpoint
      const mockSimilarApplications: SimilarApplication[] = [
        {
          id: 'APP-2024-001',
          reference: '24/01234/FUL',
          description: 'Construction of 12 residential units with associated parking',
          address: '45-47 High Street, London SW1A 1AA',
          postcode: 'SW1A 1AA',
          applicationType: 'Full Planning',
          status: 'approved',
          submissionDate: '2024-01-15',
          decisionDate: '2024-03-20',
          localAuthority: 'Westminster City Council',
          ward: 'St James\'s',
          coordinates: { lat: 51.4994, lng: -0.1357 },
          aiScore: 85,
          riskLevel: 'low' as const,
          similarityScore: 0.92,
          similarityFactors: ['Development type', 'Location proximity', 'Scale'],
          matchReason: 'Similar residential development in the same area'
        },
        {
          id: 'APP-2024-002',
          reference: '24/02345/FUL',
          description: 'Residential development comprising 8 flats with basement parking',
          address: '123 Victoria Street, London SW1E 6DE',
          postcode: 'SW1E 6DE',
          applicationType: 'Full Planning',
          status: 'approved',
          submissionDate: '2024-02-01',
          decisionDate: '2024-04-15',
          localAuthority: 'Westminster City Council',
          ward: 'Victoria',
          coordinates: { lat: 51.4956, lng: -0.1353 },
          aiScore: 78,
          riskLevel: 'low' as const,
          similarityScore: 0.88,
          similarityFactors: ['Development type', 'Authority', 'Size'],
          matchReason: 'Comparable scale residential project with similar approval path'
        },
        {
          id: 'APP-2023-015',
          reference: '23/05678/FUL',
          description: 'Conversion and extension to provide 10 residential units',
          address: '78 Grosvenor Road, London SW1V 3LG',
          postcode: 'SW1V 3LG',
          applicationType: 'Full Planning',
          status: 'approved',
          submissionDate: '2023-11-20',
          decisionDate: '2024-01-30',
          localAuthority: 'Westminster City Council',
          ward: 'Pimlico South',
          coordinates: { lat: 51.4889, lng: -0.1406 },
          aiScore: 72,
          riskLevel: 'medium' as const,
          similarityScore: 0.84,
          similarityFactors: ['Location', 'Planning authority', 'Use class'],
          matchReason: 'Similar residential conversion project with comparable complexity'
        },
        {
          id: 'APP-2024-003',
          reference: '24/03456/FUL',
          description: 'New build residential development of 15 units',
          address: '234 Kings Road, London SW3 5XP',
          postcode: 'SW3 5XP',
          applicationType: 'Full Planning',
          status: 'pending',
          submissionDate: '2024-03-10',
          localAuthority: 'Royal Borough of Kensington and Chelsea',
          ward: 'Chelsea Riverside',
          coordinates: { lat: 51.4878, lng: -0.1679 },
          aiScore: 68,
          riskLevel: 'medium' as const,
          similarityScore: 0.81,
          similarityFactors: ['Development type', 'Scale', 'Area demographics'],
          matchReason: 'Similar new-build residential project in comparable market'
        },
        {
          id: 'APP-2023-020',
          reference: '23/07890/FUL',
          description: 'Mixed-use development with 6 residential units and retail',
          address: '567 Oxford Street, London W1C 1AX',
          postcode: 'W1C 1AX',
          applicationType: 'Full Planning',
          status: 'refused',
          submissionDate: '2023-09-15',
          decisionDate: '2023-12-20',
          localAuthority: 'Westminster City Council',
          ward: 'West End',
          coordinates: { lat: 51.5154, lng: -0.1410 },
          aiScore: 45,
          riskLevel: 'high' as const,
          similarityScore: 0.75,
          similarityFactors: ['Mixed use', 'Central location', 'Development pressure'],
          matchReason: 'Mixed-use project showing potential challenges in high-density areas'
        }
      ]

      // Apply filters
      let filtered = mockSimilarApplications.filter(app => app.similarityScore >= minSimilarity)

      if (filters.status !== 'all') {
        filtered = filtered.filter(app => app.status === filters.status)
      }

      if (filters.developmentType !== 'all') {
        filtered = filtered.filter(app =>
          app.description.toLowerCase().includes(filters.developmentType.toLowerCase())
        )
      }

      // Sort by similarity score
      filtered.sort((a, b) => b.similarityScore - a.similarityScore)

      // Limit results
      filtered = filtered.slice(0, maxResults)

      setSimilarApplications(filtered)
    } catch (err) {
      setError('Failed to fetch similar applications')
      console.error('Error fetching similar applications:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'text-planning-highlight bg-planning-highlight/10'
      case 'refused':
        return 'text-red-600 bg-red-50'
      case 'pending':
        return 'text-planning-accent bg-planning-accent/10'
      case 'withdrawn':
        return 'text-gray-600 bg-gray-50'
      default:
        return 'text-planning-text-light bg-planning-border'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="w-3 h-3" />
      case 'refused':
        return <AlertTriangle className="w-3 h-3" />
      case 'pending':
        return <Clock className="w-3 h-3" />
      default:
        return <Building className="w-3 h-3" />
    }
  }

  const getSimilarityColor = (score: number) => {
    if (score >= 0.9) return 'text-planning-highlight'
    if (score >= 0.8) return 'text-planning-bright'
    if (score >= 0.7) return 'text-planning-accent'
    return 'text-planning-text-light'
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  if (isLoading) {
    return (
      <div className={`bg-white rounded-xl border border-planning-border p-6 ${className}`}>
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-8 h-8 bg-planning-primary/10 rounded-full flex items-center justify-center">
            <Search className="w-4 h-4 text-planning-primary animate-pulse" />
          </div>
          <div>
            <h3 className="font-semibold text-planning-primary">Similar Applications</h3>
            <p className="text-sm text-planning-text-light">Finding comparable applications...</p>
          </div>
          <div className="ml-auto w-6 h-6 border-2 border-planning-primary border-t-transparent rounded-full animate-spin"></div>
        </div>

        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="p-4 border border-planning-border rounded-lg">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="h-4 bg-planning-border rounded animate-pulse mb-2"></div>
                  <div className="h-3 bg-planning-border rounded animate-pulse w-3/4"></div>
                </div>
                <div className="w-16 h-6 bg-planning-border rounded animate-pulse"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={`bg-white rounded-xl border border-red-200 p-6 ${className}`}>
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-8 h-8 bg-red-50 rounded-full flex items-center justify-center">
            <AlertTriangle className="w-4 h-4 text-red-500" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-red-700">Similar Applications Unavailable</h3>
            <p className="text-sm text-red-600">{error}</p>
          </div>
          <button
            onClick={fetchSimilarApplications}
            className="text-sm text-planning-primary hover:text-planning-accent transition-colors font-medium"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className={`bg-white rounded-xl border border-planning-border overflow-hidden ${className}`}>
      {/* Header */}
      <div className="p-6 pb-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-planning-primary/10 rounded-full flex items-center justify-center">
              <Search className="w-4 h-4 text-planning-primary" />
            </div>
            <div>
              <h3 className="font-semibold text-planning-primary">Similar Applications</h3>
              <p className="text-sm text-planning-text-light flex items-center space-x-1">
                <Brain className="w-3 h-3" />
                <span>AI-powered vector similarity matching</span>
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={fetchSimilarApplications}
              className="p-2 text-planning-text-light hover:text-planning-primary transition-colors"
              title="Refresh similar applications"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
            <select
              value={filters.status}
              onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
              className="px-3 py-2 border border-planning-border rounded-lg text-sm focus:ring-2 focus:ring-planning-primary focus:border-planning-primary"
            >
              <option value="all">All Statuses</option>
              <option value="approved">Approved</option>
              <option value="pending">Pending</option>
              <option value="refused">Refused</option>
            </select>

            <select
              value={filters.developmentType}
              onChange={(e) => setFilters(prev => ({ ...prev, developmentType: e.target.value }))}
              className="px-3 py-2 border border-planning-border rounded-lg text-sm focus:ring-2 focus:ring-planning-primary focus:border-planning-primary"
            >
              <option value="all">All Types</option>
              <option value="residential">Residential</option>
              <option value="commercial">Commercial</option>
              <option value="mixed">Mixed Use</option>
            </select>

            <select
              value={filters.dateRange}
              onChange={(e) => setFilters(prev => ({ ...prev, dateRange: e.target.value }))}
              className="px-3 py-2 border border-planning-border rounded-lg text-sm focus:ring-2 focus:ring-planning-primary focus:border-planning-primary"
            >
              <option value="all">All Dates</option>
              <option value="year">Past Year</option>
              <option value="6months">Past 6 Months</option>
              <option value="3months">Past 3 Months</option>
            </select>

            <button
              onClick={fetchSimilarApplications}
              className="px-3 py-2 bg-planning-button text-white rounded-lg hover:bg-planning-primary hover:text-white transition-colors text-sm font-medium"
            >
              <Filter className="w-4 h-4 inline mr-1" />
              Apply
            </button>
          </div>
        )}
      </div>

      {/* Similar Applications List */}
      <div className="px-6 pb-6">
        {similarApplications.length === 0 ? (
          <div className="text-center py-8">
            <Search className="w-8 h-8 text-planning-text-light mx-auto mb-2" />
            <h4 className="font-medium text-planning-primary mb-1">No Similar Applications Found</h4>
            <p className="text-sm text-planning-text-light">
              Try adjusting your filters or check back later
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {similarApplications.map((app) => (
              <div
                key={app.id}
                className="border border-planning-border rounded-lg hover:border-planning-primary transition-colors"
              >
                <div className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h4 className="font-medium text-planning-primary">{app.reference}</h4>
                        <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(app.status)}`}>
                          {getStatusIcon(app.status)}
                          <span>{app.status.charAt(0).toUpperCase() + app.status.slice(1)}</span>
                        </div>
                        {app.aiScore && (
                          <div className="flex items-center space-x-1 px-2 py-1 bg-planning-highlight/10 text-planning-highlight rounded-full text-xs font-medium">
                            <TrendingUp className="w-3 h-3" />
                            <span>{app.aiScore}</span>
                          </div>
                        )}
                      </div>
                      <p className="text-sm text-planning-text-light mb-2 line-clamp-2">
                        {app.description}
                      </p>
                      <div className="flex items-center space-x-4 text-xs text-planning-text-light">
                        <div className="flex items-center space-x-1">
                          <MapPin className="w-3 h-3" />
                          <span>{app.address}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Calendar className="w-3 h-3" />
                          <span>{new Date(app.submissionDate).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>

                    <div className="text-right ml-4">
                      <div className={`text-lg font-bold ${getSimilarityColor(app.similarityScore)}`}>
                        {Math.round(app.similarityScore * 100)}%
                      </div>
                      <p className="text-xs text-planning-text-light">similarity</p>
                    </div>
                  </div>

                  {/* Similarity Factors */}
                  <div className="flex flex-wrap gap-2 mb-3">
                    {app.similarityFactors.map((factor, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-planning-primary/5 text-planning-primary rounded text-xs"
                      >
                        {factor}
                      </span>
                    ))}
                  </div>

                  <p className="text-sm text-planning-text-light italic mb-3">
                    {app.matchReason}
                  </p>

                  {/* Actions */}
                  <div className="flex items-center justify-between">
                    <button
                      onClick={() => setExpandedApp(expandedApp === app.id ? null : app.id)}
                      className="text-sm text-planning-primary hover:text-planning-accent transition-colors font-medium"
                    >
                      {expandedApp === app.id ? 'Show Less' : 'View Details'}
                    </button>

                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => copyToClipboard(app.reference)}
                        className="p-2 text-planning-text-light hover:text-planning-primary transition-colors"
                        title="Copy reference"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => onApplicationClick?.(app)}
                        className="p-2 text-planning-text-light hover:text-planning-primary transition-colors"
                        title="View application"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Expanded Details */}
                  {expandedApp === app.id && (
                    <div className="mt-4 pt-4 border-t border-planning-border">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                          <h5 className="font-medium text-planning-primary mb-2">Application Details</h5>
                          <div className="space-y-1 text-planning-text-light">
                            <div>Authority: {app.localAuthority}</div>
                            <div>Ward: {app.ward}</div>
                            <div>Type: {app.applicationType}</div>
                            {app.decisionDate && <div>Decision: {new Date(app.decisionDate).toLocaleDateString()}</div>}
                          </div>
                        </div>
                        <div>
                          <h5 className="font-medium text-planning-primary mb-2">Location</h5>
                          <div className="space-y-1 text-planning-text-light">
                            <div>Postcode: {app.postcode}</div>
                            {app.coordinates && (
                              <div>
                                Coordinates: {app.coordinates.lat.toFixed(4)}, {app.coordinates.lng.toFixed(4)}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-6 py-3 bg-planning-primary/5 border-t border-planning-border">
        <div className="flex items-center justify-between text-xs text-planning-text-light">
          <span>Powered by AI vector similarity matching</span>
          <span>Showing {similarApplications.length} of {similarApplications.length} results</span>
        </div>
      </div>
    </div>
  )
}