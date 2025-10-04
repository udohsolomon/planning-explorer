/**
 * ApplicationsTable Component
 * Paginated DataTable with freemium gate (5 results preview)
 * PRD Requirement: Paginated DataTable with columns:
 * - Address, Status, Date, Opportunity Score, Decision Time
 * - Click-through to /applications/[id]
 */

'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { FreemiumGate } from './FreemiumGate'
import { ChevronLeft, ChevronRight, ExternalLink, MapPin } from 'lucide-react'
import Link from 'next/link'

export interface Application {
  id: string
  address: string
  status: string
  date: string
  opportunityScore?: number
  decisionDays?: number
  description?: string
  location?: {
    lat: number
    lng: number
  }
}

export interface ApplicationsTableProps {
  applications: Application[]
  title?: string
  description?: string
  showFreemiumGate?: boolean
  freeLimit?: number
  currentPage?: number
  totalPages?: number
  onPageChange?: (page: number) => void
  isLoading?: boolean
  showMapLink?: boolean
  className?: string
}

export function ApplicationsTable({
  applications,
  title = 'Planning Applications',
  description,
  showFreemiumGate = true,
  freeLimit = 5,
  currentPage = 1,
  totalPages = 1,
  onPageChange,
  isLoading = false,
  showMapLink = false,
  className = '',
}: ApplicationsTableProps) {
  const [expandedRow, setExpandedRow] = useState<string | null>(null)

  // Limit visible applications for freemium users
  const visibleApplications = showFreemiumGate
    ? applications.slice(0, freeLimit)
    : applications

  const getStatusColor = (status: string): string => {
    const statusLower = status.toLowerCase()
    if (statusLower.includes('approved') || statusLower.includes('permitted')) {
      return 'success'
    }
    if (statusLower.includes('pending') || statusLower.includes('undecided')) {
      return 'warning'
    }
    if (statusLower.includes('rejected') || statusLower.includes('refused')) {
      return 'danger'
    }
    return 'default'
  }

  const getScoreColor = (score: number): string => {
    if (score >= 80) return 'text-green-600 bg-green-50'
    if (score >= 60) return 'text-yellow-600 bg-yellow-50'
    if (score >= 40) return 'text-orange-600 bg-orange-50'
    return 'text-red-600 bg-red-50'
  }

  const formatDate = (dateString: string): string => {
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-GB', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
      })
    } catch {
      return dateString
    }
  }

  if (isLoading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
          {description && <CardDescription>{description}</CardDescription>}
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-100 rounded animate-pulse" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className={className}>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>{title}</CardTitle>
              {description && <CardDescription>{description}</CardDescription>}
            </div>
            <div className="text-sm text-gray-600">
              Showing {visibleApplications.length} of {applications.length} applications
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {/* Desktop Table View */}
          <div className="hidden md:block overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Address
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  {visibleApplications.some((app) => app.opportunityScore !== undefined) && (
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Score
                    </th>
                  )}
                  {visibleApplications.some((app) => app.decisionDays !== undefined) && (
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Decision
                    </th>
                  )}
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {visibleApplications.map((app) => (
                  <tr
                    key={app.id}
                    className="hover:bg-gray-50 transition-colors cursor-pointer"
                    onClick={() => setExpandedRow(expandedRow === app.id ? null : app.id)}
                  >
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">{app.address}</div>
                      {app.description && expandedRow === app.id && (
                        <div className="text-sm text-gray-600 mt-1">{app.description}</div>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant={getStatusColor(app.status)} size="sm">
                        {app.status}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">{formatDate(app.date)}</td>
                    {app.opportunityScore !== undefined && (
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium ${getScoreColor(app.opportunityScore)}`}>
                          {app.opportunityScore}/100
                        </span>
                      </td>
                    )}
                    {app.decisionDays !== undefined && (
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {app.decisionDays} days
                      </td>
                    )}
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <Link href={`/applications/${app.id}`}>
                          <Button variant="outline" size="sm">
                            View
                            <ExternalLink className="ml-2 h-3 w-3" />
                          </Button>
                        </Link>
                        {showMapLink && app.location && (
                          <Button variant="ghost" size="sm" title="View on map">
                            <MapPin className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Mobile Card View */}
          <div className="md:hidden divide-y divide-gray-200">
            {visibleApplications.map((app) => (
              <div key={app.id} className="p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <h4 className="text-sm font-medium text-gray-900 mb-1">{app.address}</h4>
                    <div className="flex items-center gap-2 flex-wrap">
                      <Badge variant={getStatusColor(app.status)} size="sm">
                        {app.status}
                      </Badge>
                      <span className="text-xs text-gray-500">{formatDate(app.date)}</span>
                    </div>
                  </div>
                </div>

                {app.description && (
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">{app.description}</p>
                )}

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3 text-xs">
                    {app.opportunityScore !== undefined && (
                      <span className={`px-2 py-1 rounded ${getScoreColor(app.opportunityScore)}`}>
                        Score: {app.opportunityScore}/100
                      </span>
                    )}
                    {app.decisionDays !== undefined && (
                      <span className="text-gray-600">{app.decisionDays}d</span>
                    )}
                  </div>
                  <Link href={`/applications/${app.id}`}>
                    <Button variant="outline" size="sm">
                      View
                    </Button>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Freemium Gate */}
      {showFreemiumGate && applications.length > freeLimit && (
        <FreemiumGate totalResults={applications.length} visibleResults={freeLimit} className="mt-6" />
      )}

      {/* Pagination */}
      {!showFreemiumGate && totalPages > 1 && onPageChange && (
        <div className="flex items-center justify-between mt-6">
          <div className="text-sm text-gray-600">
            Page {currentPage} of {totalPages}
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onPageChange(currentPage - 1)}
              disabled={currentPage === 1}
            >
              <ChevronLeft className="h-4 w-4 mr-1" />
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onPageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
            >
              Next
              <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
