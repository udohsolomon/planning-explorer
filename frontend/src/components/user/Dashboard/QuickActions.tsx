'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import {
  Search,
  Bell,
  FileText,
  Download,
  MapPin,
  Zap,
  Plus,
  TrendingUp,
  Settings
} from 'lucide-react'
import { useUserStore } from '@/stores/userStore'
import Link from 'next/link'

export function QuickActions() {
  const { user, savedSearches, alerts } = useUserStore()

  const quickActions = [
    {
      title: 'New Search',
      description: 'Start exploring planning applications',
      icon: Search,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      href: '/search',
      primary: true
    },
    {
      title: 'Create Alert',
      description: 'Get notified of relevant applications',
      icon: Bell,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      href: '/dashboard/alerts/new'
    },
    {
      title: 'Generate Report',
      description: 'Create market analysis reports',
      icon: FileText,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      href: '/dashboard/reports/new'
    },
    {
      title: 'AI Insights',
      description: 'View personalized recommendations',
      icon: Zap,
      color: 'text-planning-primary',
      bgColor: 'bg-planning-primary/10',
      href: '/dashboard/insights'
    }
  ]

  const recentActions = [
    {
      title: 'Saved Searches',
      count: savedSearches.length,
      href: '/dashboard/searches',
      icon: Search
    },
    {
      title: 'Active Alerts',
      count: alerts.filter(alert => alert.isActive).length,
      href: '/dashboard/alerts',
      icon: Bell
    },
    {
      title: 'Export Data',
      href: '/dashboard/exports',
      icon: Download
    },
    {
      title: 'Market Trends',
      href: '/dashboard/trends',
      icon: TrendingUp
    }
  ]

  return (
    <div className="space-y-6">
      {/* Primary Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {quickActions.map((action) => {
              const Icon = action.icon
              return (
                <Link key={action.title} href={action.href}>
                  <div className={`p-4 rounded-lg border-2 border-transparent hover:border-planning-primary/20 transition-all cursor-pointer group ${
                    action.primary ? 'bg-gradient-to-br from-planning-primary/5 to-planning-accent/5' : 'hover:bg-gray-50'
                  }`}>
                    <div className="flex items-center space-x-3">
                      <div className={`w-10 h-10 ${action.bgColor} rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform`}>
                        <Icon className={`w-5 h-5 ${action.color}`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium text-planning-text-dark">
                          {action.title}
                        </h3>
                        <p className="text-sm text-planning-text-light">
                          {action.description}
                        </p>
                      </div>
                    </div>
                  </div>
                </Link>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Secondary Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {recentActions.map((action) => {
          const Icon = action.icon
          return (
            <Link key={action.title} href={action.href}>
              <Card className="hover:shadow-md transition-shadow cursor-pointer">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Icon className="w-5 h-5 text-planning-primary" />
                      <span className="font-medium text-planning-text-dark">
                        {action.title}
                      </span>
                    </div>
                    {action.count !== undefined && (
                      <Badge variant="outline" size="sm">
                        {action.count}
                      </Badge>
                    )}
                  </div>
                </CardContent>
              </Card>
            </Link>
          )
        })}
      </div>

      {/* Featured Actions based on subscription tier */}
      {user?.subscriptionTier.name === 'Free' && (
        <Card className="border-planning-primary/20 bg-gradient-to-r from-planning-primary/5 to-planning-accent/5">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-planning-primary/10 rounded-lg flex items-center justify-center">
                  <Zap className="w-6 h-6 text-planning-primary" />
                </div>
                <div>
                  <h3 className="font-semibold text-planning-primary">
                    Unlock Advanced Features
                  </h3>
                  <p className="text-sm text-planning-text-light">
                    Get unlimited searches, AI insights, and advanced analytics
                  </p>
                </div>
              </div>
              <Button>
                Upgrade Now
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Location-based suggestions */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center">
            <MapPin className="w-5 h-5 mr-2 text-planning-primary" />
            Trending in Your Area
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <h4 className="font-medium text-planning-text-dark">
                  Residential Applications
                </h4>
                <p className="text-sm text-planning-text-light">
                  +15% increase this month
                </p>
              </div>
              <Button variant="ghost" size="sm">
                Explore
              </Button>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <h4 className="font-medium text-planning-text-dark">
                  Commercial Developments
                </h4>
                <p className="text-sm text-planning-text-light">
                  New policy updates available
                </p>
              </div>
              <Button variant="ghost" size="sm">
                View Details
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}