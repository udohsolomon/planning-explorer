/**
 * StatsCard Component
 * Reusable card component for displaying key statistics with optional trend indicators
 * PRD Requirement: shadcn/ui Card with stat value + trend indicator + icon
 */

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { ArrowUp, ArrowDown, TrendingUp } from 'lucide-react'
import { ReactNode } from 'react'

export interface StatsCardProps {
  title: string
  value: string | number
  trend?: {
    value: number
    direction: 'up' | 'down'
    label?: string
  }
  icon?: ReactNode
  description?: string
  className?: string
  valueClassName?: string
}

export function StatsCard({
  title,
  value,
  trend,
  icon,
  description,
  className = '',
  valueClassName = '',
}: StatsCardProps) {
  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardDescription className="text-sm font-medium text-gray-600">{title}</CardDescription>
          {icon && <div className="text-planning-primary opacity-80">{icon}</div>}
        </div>
        <CardTitle className={`text-3xl font-bold ${valueClassName || 'text-gray-900'}`}>
          {typeof value === 'number' ? value.toLocaleString() : value}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          {description && <p className="text-sm text-gray-600">{description}</p>}
          {trend && (
            <div
              className={`flex items-center gap-1 text-sm font-medium ${
                trend.direction === 'up' ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {trend.direction === 'up' ? (
                <ArrowUp className="h-4 w-4" />
              ) : (
                <ArrowDown className="h-4 w-4" />
              )}
              <span>{Math.abs(trend.value)}%</span>
              {trend.label && <span className="text-gray-500 ml-1">{trend.label}</span>}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

/**
 * StatsCardGrid Component
 * Grid layout for multiple stats cards with responsive breakpoints
 */
export function StatsCardGrid({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 ${className}`}>
      {children}
    </div>
  )
}
