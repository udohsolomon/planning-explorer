/**
 * LeagueTable Component
 * Sortable league table for authorities, regions, sectors, and agents
 * PRD Requirement: Enhanced Content Discovery - Insights Hub league table
 * Features: Sortable columns, trend indicators, click-through navigation
 */

'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { ArrowUp, ArrowDown, Minus, TrendingUp, TrendingDown, ExternalLink } from 'lucide-react'
import { useRouter } from 'next/navigation'

export interface LeagueTableRow {
  rank: number
  name: string
  slug: string
  total_applications: number
  percentage: number
  success_rate: number
  avg_decision_days: number
  trend: 'up' | 'down' | 'stable'
  trend_percentage?: number
}

export interface LeagueTableProps {
  data: LeagueTableRow[]
  onRowClick?: (row: LeagueTableRow) => void
  type: 'authorities' | 'regions' | 'sectors' | 'agents'
  title?: string
  description?: string
  showRank?: boolean
  className?: string
  isLoading?: boolean
}

type SortField = 'rank' | 'name' | 'total_applications' | 'percentage' | 'success_rate' | 'avg_decision_days'
type SortDirection = 'asc' | 'desc'

export function LeagueTable({
  data,
  onRowClick,
  type,
  title,
  description,
  showRank = true,
  className = '',
  isLoading = false,
}: LeagueTableProps) {
  const router = useRouter()
  const [sortField, setSortField] = useState<SortField>('rank')
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc')

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('asc')
    }
  }

  const sortedData = [...data].sort((a, b) => {
    const aVal = a[sortField]
    const bVal = b[sortField]

    if (typeof aVal === 'string' && typeof bVal === 'string') {
      return sortDirection === 'asc'
        ? aVal.localeCompare(bVal)
        : bVal.localeCompare(aVal)
    }

    if (typeof aVal === 'number' && typeof bVal === 'number') {
      return sortDirection === 'asc' ? aVal - bVal : bVal - aVal
    }

    return 0
  })

  const handleRowClick = (row: LeagueTableRow) => {
    if (onRowClick) {
      onRowClick(row)
    } else {
      // Default navigation based on type
      const baseRoute = type === 'agents' ? '/agents' : `/${type.slice(0, -1)}`
      router.push(`${baseRoute}/${row.slug}`)
    }
  }

  const getTrendIcon = (trend: LeagueTableRow['trend'], percentage?: number) => {
    if (trend === 'up') {
      return (
        <div className="flex items-center gap-1 text-green-600">
          <ArrowUp className="h-3 w-3" />
          {percentage && <span className="text-xs">{percentage}%</span>}
        </div>
      )
    }
    if (trend === 'down') {
      return (
        <div className="flex items-center gap-1 text-red-600">
          <ArrowDown className="h-3 w-3" />
          {percentage && <span className="text-xs">{percentage}%</span>}
        </div>
      )
    }
    return (
      <div className="flex items-center gap-1 text-gray-400">
        <Minus className="h-3 w-3" />
      </div>
    )
  }

  const getTypeLabel = (type: string): string => {
    const labels = {
      authorities: 'Authority',
      regions: 'Region',
      sectors: 'Sector',
      agents: 'Agent',
    }
    return labels[type as keyof typeof labels] || type
  }

  const SortableHeader = ({ field, label }: { field: SortField; label: string }) => (
    <th
      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
      onClick={() => handleSort(field)}
    >
      <div className="flex items-center gap-2">
        {label}
        {sortField === field && (
          <span className="text-planning-primary">
            {sortDirection === 'asc' ? '↑' : '↓'}
          </span>
        )}
      </div>
    </th>
  )

  if (isLoading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>{title || `${getTypeLabel(type)} League Table`}</CardTitle>
          {description && <CardDescription>{description}</CardDescription>}
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(10)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-100 rounded animate-pulse" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>{title || `${getTypeLabel(type)} League Table`}</CardTitle>
            {description && <CardDescription>{description}</CardDescription>}
          </div>
          <Badge variant="default" size="sm">
            {data.length} {type}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        {/* Desktop Table View */}
        <div className="hidden md:block overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                {showRank && <SortableHeader field="rank" label="Rank" />}
                <SortableHeader field="name" label={getTypeLabel(type)} />
                <SortableHeader field="total_applications" label="Applications" />
                <SortableHeader field="percentage" label="% of Total" />
                <SortableHeader field="success_rate" label="Success Rate" />
                <SortableHeader field="avg_decision_days" label="Avg Time (days)" />
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Trend
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {sortedData.map((row) => (
                <tr
                  key={row.slug}
                  className="hover:bg-gray-50 transition-colors cursor-pointer"
                  onClick={() => handleRowClick(row)}
                >
                  {showRank && (
                    <td className="px-6 py-4">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-planning-primary/10 text-planning-primary font-bold text-sm">
                        {row.rank}
                      </div>
                    </td>
                  )}
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-gray-900">{row.name}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900 font-semibold">
                      {row.total_applications.toLocaleString()}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-600">{row.percentage.toFixed(1)}%</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2 max-w-[100px]">
                        <div
                          className="bg-planning-primary h-2 rounded-full transition-all"
                          style={{ width: `${row.success_rate}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium text-gray-900 min-w-[45px]">
                        {row.success_rate.toFixed(0)}%
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">{row.avg_decision_days}</div>
                  </td>
                  <td className="px-6 py-4">{getTrendIcon(row.trend, row.trend_percentage)}</td>
                  <td className="px-6 py-4">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleRowClick(row)
                      }}
                    >
                      View
                      <ExternalLink className="ml-2 h-3 w-3" />
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Mobile Card View */}
        <div className="md:hidden divide-y divide-gray-200">
          {sortedData.map((row) => (
            <div
              key={row.slug}
              className="p-4 hover:bg-gray-50 transition-colors cursor-pointer"
              onClick={() => handleRowClick(row)}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3 flex-1">
                  {showRank && (
                    <div className="flex items-center justify-center w-10 h-10 rounded-full bg-planning-primary/10 text-planning-primary font-bold">
                      {row.rank}
                    </div>
                  )}
                  <div className="flex-1">
                    <h4 className="text-sm font-medium text-gray-900 mb-1">{row.name}</h4>
                    <div className="flex items-center gap-2 text-xs text-gray-600">
                      <span className="font-semibold">{row.total_applications.toLocaleString()} apps</span>
                      <span>·</span>
                      <span>{row.percentage.toFixed(1)}%</span>
                    </div>
                  </div>
                  {getTrendIcon(row.trend, row.trend_percentage)}
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Success Rate:</span>
                  <div className="flex items-center gap-2">
                    <div className="w-20 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-planning-primary h-2 rounded-full"
                        style={{ width: `${row.success_rate}%` }}
                      />
                    </div>
                    <span className="font-medium text-gray-900 min-w-[35px]">
                      {row.success_rate.toFixed(0)}%
                    </span>
                  </div>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Avg Decision Time:</span>
                  <span className="font-medium text-gray-900">{row.avg_decision_days} days</span>
                </div>
              </div>

              <div className="mt-3 flex justify-end">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation()
                    handleRowClick(row)
                  }}
                >
                  View Details
                  <ExternalLink className="ml-2 h-3 w-3" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
