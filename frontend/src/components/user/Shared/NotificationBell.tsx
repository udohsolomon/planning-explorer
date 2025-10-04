'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { useUserStore } from '@/stores/userStore'
import { Notification } from '@/types/user'
import {
  Bell,
  Check,
  X,
  AlertTriangle,
  Info,
  CheckCircle,
  FileText,
  Lightbulb,
  ExternalLink,
  MoreHorizontal
} from 'lucide-react'
import { formatDate } from '@/lib/utils'

const notificationIcons = {
  alert: AlertTriangle,
  system: Info,
  report: FileText,
  recommendation: Lightbulb
}

const notificationColors = {
  alert: 'text-orange-600',
  system: 'text-blue-600',
  report: 'text-purple-600',
  recommendation: 'text-green-600'
}

const priorityColors = {
  low: 'bg-gray-100',
  medium: 'bg-yellow-100',
  high: 'bg-red-100'
}

function NotificationItem({ notification }: { notification: Notification }) {
  const { markNotificationRead, deleteNotification } = useUserStore()
  const Icon = notificationIcons[notification.type] || Info
  const color = notificationColors[notification.type] || 'text-gray-600'

  const handleMarkRead = () => {
    if (!notification.isRead) {
      markNotificationRead(notification.id)
    }
  }

  const handleDelete = () => {
    deleteNotification(notification.id)
  }

  const handleAction = () => {
    markNotificationRead(notification.id)
    if (notification.actionUrl) {
      window.open(notification.actionUrl, '_blank')
    }
  }

  return (
    <div className={`p-3 border-l-2 ${
      notification.isRead ? 'border-gray-200 bg-white' : 'border-planning-primary bg-blue-50/30'
    } ${priorityColors[notification.priority]} hover:bg-gray-50 transition-colors`}>
      <div className="flex items-start space-x-3">
        <div className="mt-0.5">
          <Icon className={`w-4 h-4 ${color}`} />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between">
            <h4 className={`text-sm font-medium ${
              notification.isRead ? 'text-planning-text-light' : 'text-planning-text-dark'
            }`}>
              {notification.title}
            </h4>
            <div className="flex items-center space-x-1 ml-2">
              {notification.priority === 'high' && (
                <Badge variant="danger" size="sm" className="text-xs">
                  High
                </Badge>
              )}
              <button
                onClick={handleDelete}
                className="p-1 text-planning-text-light hover:text-red-600 transition-colors"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          </div>

          <p className={`text-sm mt-1 ${
            notification.isRead ? 'text-planning-text-light' : 'text-planning-text-dark'
          }`}>
            {notification.message}
          </p>

          <div className="flex items-center justify-between mt-2">
            <span className="text-xs text-planning-text-light">
              {formatDate(notification.createdAt)}
            </span>

            <div className="flex items-center space-x-2">
              {!notification.isRead && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleMarkRead}
                  className="text-xs"
                >
                  <Check className="w-3 h-3 mr-1" />
                  Mark read
                </Button>
              )}
              {notification.actionUrl && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleAction}
                  className="text-xs"
                >
                  {notification.actionLabel || 'View'}
                  <ExternalLink className="w-3 h-3 ml-1" />
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export function NotificationBell() {
  const [isOpen, setIsOpen] = useState(false)
  const [filter, setFilter] = useState<'all' | 'unread'>('all')
  const bellRef = useRef<HTMLDivElement>(null)

  const {
    notifications,
    unreadNotifications,
    markAllNotificationsRead
  } = useUserStore()

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (bellRef.current && !bellRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const filteredNotifications = filter === 'unread'
    ? notifications.filter(n => !n.isRead)
    : notifications

  const sortedNotifications = [...filteredNotifications].sort((a, b) => {
    // Sort by read status (unread first), then by priority, then by date
    if (a.isRead !== b.isRead) return a.isRead ? 1 : -1

    const priorityOrder = { high: 3, medium: 2, low: 1 }
    if (a.priority !== b.priority) {
      return priorityOrder[b.priority] - priorityOrder[a.priority]
    }

    return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
  })

  return (
    <div className="relative" ref={bellRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-planning-text-light hover:text-planning-primary transition-colors"
      >
        <Bell className="w-5 h-5" />
        {unreadNotifications > 0 && (
          <div className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
            {unreadNotifications > 9 ? '9+' : unreadNotifications}
          </div>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-96 max-w-[90vw] bg-white rounded-lg shadow-lg border border-planning-border z-50">
          <div className="p-4 border-b border-planning-border">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold text-planning-primary">
                Notifications
              </h3>
              {unreadNotifications > 0 && (
                <button
                  onClick={markAllNotificationsRead}
                  className="text-sm text-planning-primary hover:text-planning-accent"
                >
                  Mark all read
                </button>
              )}
            </div>

            <div className="flex space-x-2">
              <Button
                variant={filter === 'all' ? 'secondary' : 'ghost'}
                size="sm"
                onClick={() => setFilter('all')}
                className="text-xs"
              >
                All ({notifications.length})
              </Button>
              <Button
                variant={filter === 'unread' ? 'secondary' : 'ghost'}
                size="sm"
                onClick={() => setFilter('unread')}
                className="text-xs"
              >
                Unread ({unreadNotifications})
              </Button>
            </div>
          </div>

          <div className="max-h-96 overflow-y-auto">
            {sortedNotifications.length === 0 ? (
              <div className="p-8 text-center">
                <Bell className="w-12 h-12 text-planning-text-light mx-auto mb-4" />
                <h4 className="font-medium text-planning-text-dark mb-2">
                  {filter === 'unread' ? 'No unread notifications' : 'No notifications'}
                </h4>
                <p className="text-sm text-planning-text-light">
                  {filter === 'unread'
                    ? "You're all caught up!"
                    : 'New notifications will appear here'
                  }
                </p>
              </div>
            ) : (
              <div className="space-y-1">
                {sortedNotifications.slice(0, 20).map((notification) => (
                  <NotificationItem
                    key={notification.id}
                    notification={notification}
                  />
                ))}
                {sortedNotifications.length > 20 && (
                  <div className="p-3 text-center border-t">
                    <Button variant="ghost" size="sm" className="text-xs">
                      View all notifications
                    </Button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}