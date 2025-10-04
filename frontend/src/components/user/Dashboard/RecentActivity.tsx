'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { UserActivity } from '@/types/user'
import {
  Search,
  Bell,
  FileText,
  Download,
  LogIn,
  Calendar,
  Clock,
  MoreHorizontal,
  Activity
} from 'lucide-react'
import { formatDate } from '@/lib/utils'

interface RecentActivityProps {
  activities: UserActivity[]
}

const activityIcons = {
  search: Search,
  alert_created: Bell,
  report_generated: FileText,
  export: Download,
  login: LogIn
}

const activityColors = {
  search: 'text-blue-600',
  alert_created: 'text-green-600',
  report_generated: 'text-purple-600',
  export: 'text-orange-600',
  login: 'text-gray-600'
}

const activityBgColors = {
  search: 'bg-blue-50',
  alert_created: 'bg-green-50',
  report_generated: 'bg-purple-50',
  export: 'bg-orange-50',
  login: 'bg-gray-50'
}

function getRelativeTime(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  if (days < 7) return `${days}d ago`
  return formatDate(date)
}

function ActivityItem({ activity }: { activity: UserActivity }) {
  const Icon = activityIcons[activity.type] || Activity
  const color = activityColors[activity.type] || 'text-gray-600'
  const bgColor = activityBgColors[activity.type] || 'bg-gray-50'

  return (
    <div className="flex items-start space-x-3 p-3 hover:bg-gray-50 rounded-lg transition-colors">
      <div className={`w-8 h-8 ${bgColor} rounded-full flex items-center justify-center mt-0.5`}>
        <Icon className={`w-4 h-4 ${color}`} />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-planning-text-dark">
          {activity.description}
        </p>
        <div className="flex items-center space-x-2 mt-1">
          <Clock className="w-3 h-3 text-planning-text-light" />
          <span className="text-xs text-planning-text-light">
            {getRelativeTime(activity.createdAt)}
          </span>
          {activity.metadata?.location && (
            <>
              <span className="text-xs text-planning-text-light">•</span>
              <span className="text-xs text-planning-text-light">
                {activity.metadata.location}
              </span>
            </>
          )}
        </div>
      </div>
      <button className="p-1 text-planning-text-light hover:text-planning-primary transition-colors">
        <MoreHorizontal className="w-4 h-4" />
      </button>
    </div>
  )
}

export function RecentActivity({ activities }: RecentActivityProps) {
  // Group activities by date
  const groupedActivities = activities.reduce((groups, activity) => {
    const date = new Date(activity.createdAt).toDateString()
    if (!groups[date]) {
      groups[date] = []
    }
    groups[date].push(activity)
    return groups
  }, {} as Record<string, UserActivity[]>)

  const sortedDates = Object.keys(groupedActivities).sort(
    (a, b) => new Date(b).getTime() - new Date(a).getTime()
  )

  if (activities.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center">
            <Activity className="w-5 h-5 mr-2 text-planning-primary" />
            Recent Activity
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Activity className="w-12 h-12 text-planning-text-light mx-auto mb-4" />
            <h3 className="font-medium text-planning-text-dark mb-2">
              No activity yet
            </h3>
            <p className="text-sm text-planning-text-light mb-4">
              Your recent searches, alerts, and reports will appear here
            </p>
            <Button variant="outline">
              Start Exploring
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center">
            <Activity className="w-5 h-5 mr-2 text-planning-primary" />
            Recent Activity
          </CardTitle>
          <Badge variant="outline" size="sm">
            {activities.length} items
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {sortedDates.slice(0, 7).map((date) => (
            <div key={date}>
              <div className="flex items-center space-x-2 mb-3">
                <Calendar className="w-4 h-4 text-planning-text-light" />
                <h4 className="text-sm font-medium text-planning-text-light">
                  {new Date(date).toLocaleDateString('en-GB', {
                    weekday: 'long',
                    month: 'long',
                    day: 'numeric'
                  })}
                </h4>
              </div>
              <div className="space-y-1 ml-6">
                {groupedActivities[date].map((activity) => (
                  <ActivityItem key={activity.id} activity={activity} />
                ))}
              </div>
            </div>
          ))}

          {activities.length > 20 && (
            <div className="pt-4 border-t">
              <Button variant="ghost" className="w-full">
                View All Activity
              </Button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}