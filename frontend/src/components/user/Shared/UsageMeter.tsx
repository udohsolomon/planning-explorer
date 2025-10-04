'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { UsageMetrics } from '@/types/user'
import { TrendingUp, AlertTriangle, Search, Bell, FileText, Download, Zap } from 'lucide-react'
import { cn } from '@/lib/utils'

interface UsageMeterProps {
  metrics: UsageMetrics
  compact?: boolean
  showUpgrade?: boolean
  onUpgrade?: () => void
}

interface UsageBarProps {
  label: string
  used: number
  limit: number
  icon: React.ReactNode
  color?: 'default' | 'warning' | 'danger'
}

function UsageBar({ label, used, limit, icon, color = 'default' }: UsageBarProps) {
  const percentage = limit > 0 ? Math.min((used / limit) * 100, 100) : 0
  const isUnlimited = limit === -1

  const colorClasses = {
    default: 'bg-planning-primary',
    warning: 'bg-yellow-500',
    danger: 'bg-red-500'
  }

  const getColor = () => {
    if (isUnlimited) return 'default'
    if (percentage >= 90) return 'danger'
    if (percentage >= 75) return 'warning'
    return 'default'
  }

  const currentColor = color === 'default' ? getColor() : color

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="text-planning-text-light">{icon}</div>
          <span className="text-sm font-medium text-planning-text-dark">{label}</span>
        </div>
        <div className="text-sm text-planning-text-light">
          {isUnlimited ? (
            <Badge variant="success" size="sm">Unlimited</Badge>
          ) : (
            <span>
              <span className={cn(
                'font-medium',
                currentColor === 'danger' ? 'text-red-600' :
                currentColor === 'warning' ? 'text-yellow-600' :
                'text-planning-text-dark'
              )}>
                {used.toLocaleString()}
              </span>
              <span className="text-planning-text-light"> / {limit.toLocaleString()}</span>
            </span>
          )}
        </div>
      </div>

      {!isUnlimited && (
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={cn('h-2 rounded-full transition-all duration-300', colorClasses[currentColor])}
            style={{ width: `${Math.min(percentage, 100)}%` }}
          />
        </div>
      )}
    </div>
  )
}

export function UsageMeter({ metrics, compact = false, showUpgrade = true, onUpgrade }: UsageMeterProps) {
  const [selectedPeriod, setSelectedPeriod] = useState<'current_month' | 'last_month'>('current_month')

  const usageItems = [
    {
      label: 'Searches',
      used: metrics.searches.used,
      limit: metrics.searches.limit,
      icon: <Search className="w-4 h-4" />
    },
    {
      label: 'Alerts',
      used: metrics.alerts.used,
      limit: metrics.alerts.limit,
      icon: <Bell className="w-4 h-4" />
    },
    {
      label: 'Reports',
      used: metrics.reports.used,
      limit: metrics.reports.limit,
      icon: <FileText className="w-4 h-4" />
    },
    {
      label: 'Exports',
      used: metrics.exports.used,
      limit: metrics.exports.limit,
      icon: <Download className="w-4 h-4" />
    },
    {
      label: 'API Calls',
      used: metrics.apiCalls.used,
      limit: metrics.apiCalls.limit,
      icon: <Zap className="w-4 h-4" />
    }
  ]

  // Check if user is approaching limits
  const hasWarnings = usageItems.some(item => {
    if (item.limit === -1) return false
    const percentage = (item.used / item.limit) * 100
    return percentage >= 75
  })

  if (compact) {
    const criticalUsage = usageItems.find(item => {
      if (item.limit === -1) return false
      const percentage = (item.used / item.limit) * 100
      return percentage >= 90
    })

    if (criticalUsage) {
      return (
        <div className="flex items-center space-x-2 p-3 bg-red-50 border border-red-200 rounded-lg">
          <AlertTriangle className="w-4 h-4 text-red-600" />
          <span className="text-sm text-red-700">
            {criticalUsage.label} limit almost reached ({criticalUsage.used}/{criticalUsage.limit})
          </span>
          {showUpgrade && (
            <Button size="sm" variant="secondary" onClick={onUpgrade}>
              Upgrade
            </Button>
          )}
        </div>
      )
    }

    return null
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Usage Overview</CardTitle>
          {hasWarnings && (
            <Badge variant="warning" size="sm">
              <AlertTriangle className="w-3 h-3 mr-1" />
              Approaching limits
            </Badge>
          )}
        </div>
        <div className="flex space-x-1">
          <Button
            variant={selectedPeriod === 'current_month' ? 'secondary' : 'ghost'}
            size="sm"
            onClick={() => setSelectedPeriod('current_month')}
          >
            This Month
          </Button>
          <Button
            variant={selectedPeriod === 'last_month' ? 'secondary' : 'ghost'}
            size="sm"
            onClick={() => setSelectedPeriod('last_month')}
          >
            Last Month
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {usageItems.map((item) => (
          <UsageBar key={item.label} {...item} />
        ))}

        {hasWarnings && showUpgrade && (
          <div className="mt-6 p-4 bg-planning-primary/5 border border-planning-primary/20 rounded-lg">
            <div className="flex items-start space-x-3">
              <TrendingUp className="w-5 h-5 text-planning-primary mt-0.5" />
              <div className="flex-1">
                <h4 className="font-medium text-planning-primary">Upgrade for more</h4>
                <p className="text-sm text-planning-text-light mt-1">
                  You're approaching your limits. Upgrade to unlock higher quotas and advanced features.
                </p>
                <Button size="sm" className="mt-3" onClick={onUpgrade}>
                  View Plans
                </Button>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}