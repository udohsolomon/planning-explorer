'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { useUserStore } from '@/stores/userStore'
import {
  Search,
  Bell,
  FileText,
  TrendingUp,
  MapPin,
  Calendar,
  Clock,
  Star
} from 'lucide-react'

export function DashboardOverview() {
  const {
    user,
    savedSearches,
    alerts,
    reports,
    usageMetrics,
    notifications
  } = useUserStore()

  // Calculate stats
  const stats = [
    {
      label: 'Saved Searches',
      value: savedSearches.length,
      icon: Search,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      change: '+12%',
      changeType: 'positive' as const
    },
    {
      label: 'Active Alerts',
      value: alerts.filter(alert => alert.isActive).length,
      icon: Bell,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      change: '+5%',
      changeType: 'positive' as const
    },
    {
      label: 'Reports Generated',
      value: reports.length,
      icon: FileText,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      change: '+23%',
      changeType: 'positive' as const
    },
    {
      label: 'Searches This Month',
      value: usageMetrics?.searches.used || 0,
      icon: TrendingUp,
      color: 'text-planning-primary',
      bgColor: 'bg-planning-primary/10',
      change: usageMetrics?.searches.limit ?
        `${Math.round((usageMetrics.searches.used / usageMetrics.searches.limit) * 100)}% used` :
        'Unlimited',
      changeType: 'neutral' as const
    }
  ]

  const unreadNotifications = notifications.filter(n => !n.isRead).length

  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <Card key={stat.label}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-planning-text-light">
                      {stat.label}
                    </p>
                    <p className="text-2xl font-bold text-planning-text-dark">
                      {stat.value}
                    </p>
                  </div>
                  <div className={`w-12 h-12 ${stat.bgColor} rounded-lg flex items-center justify-center`}>
                    <Icon className={`w-6 h-6 ${stat.color}`} />
                  </div>
                </div>
                <div className="mt-4 flex items-center">
                  <span className={`text-sm font-medium ${
                    stat.changeType === 'positive' ? 'text-green-600' :
                    (stat.changeType as any) === 'negative' ? 'text-red-600' :
                    'text-planning-text-light'
                  }`}>
                    {stat.change}
                  </span>
                  <span className="text-sm text-planning-text-light ml-2">
                    vs last month
                  </span>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Today's Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Stats */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center">
              <Calendar className="w-5 h-5 mr-2 text-planning-primary" />
              Today's Activity
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-planning-text-light">New applications</span>
              <Badge variant="secondary">24</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-planning-text-light">Decisions made</span>
              <Badge variant="secondary">8</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-planning-text-light">Alert notifications</span>
              <Badge variant={unreadNotifications > 0 ? 'warning' : 'secondary'}>
                {unreadNotifications}
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Recent Searches */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center">
              <Clock className="w-5 h-5 mr-2 text-planning-primary" />
              Recent Searches
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {savedSearches.slice(0, 3).map((search) => (
              <div key={search.id} className="flex items-center space-x-3">
                <MapPin className="w-4 h-4 text-planning-text-light" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-planning-text-dark truncate">
                    {search.name}
                  </p>
                  <p className="text-xs text-planning-text-light">
                    {search.lastExecuted ?
                      new Date(search.lastExecuted).toLocaleDateString() :
                      'Never executed'
                    }
                  </p>
                </div>
              </div>
            ))}
            {savedSearches.length === 0 && (
              <p className="text-sm text-planning-text-light text-center py-4">
                No saved searches yet
              </p>
            )}
          </CardContent>
        </Card>

        {/* Performance Insights */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center">
              <Star className="w-5 h-5 mr-2 text-planning-primary" />
              Performance
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-planning-text-light">Search accuracy</span>
                <span className="text-sm font-medium text-planning-text-dark">94%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-planning-bright h-2 rounded-full" style={{ width: '94%' }} />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-planning-text-light">Alert relevance</span>
                <span className="text-sm font-medium text-planning-text-dark">87%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-planning-accent h-2 rounded-full" style={{ width: '87%' }} />
              </div>
            </div>
            <div className="pt-2 border-t">
              <p className="text-xs text-planning-text-light">
                AI learning from your preferences
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}