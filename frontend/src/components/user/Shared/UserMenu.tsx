'use client'

import { useState, useRef, useEffect } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { UserAvatar } from './UserAvatar'
import { SubscriptionBadge } from './SubscriptionBadge'
import { useUserStore } from '@/stores/userStore'
import {
  User,
  Settings,
  CreditCard,
  Bell,
  Search,
  FileText,
  LogOut,
  ChevronDown,
  Crown,
  HelpCircle
} from 'lucide-react'

export function UserMenu() {
  const [isOpen, setIsOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)
  const {
    user,
    isAuthenticated,
    logout,
    unreadNotifications,
    savedSearches,
    alerts,
    reports
  } = useUserStore()

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleLogout = () => {
    logout()
    setIsOpen(false)
  }

  if (!isAuthenticated || !user) {
    return (
      <div className="flex items-center space-x-3">
        <Link href="/auth/login">
          <Button variant="ghost" size="sm">
            <User className="w-4 h-4 mr-2" />
            Sign In
          </Button>
        </Link>
        <Link href="/auth/register">
          <Button size="sm">
            Get Started
          </Button>
        </Link>
      </div>
    )
  }

  const menuItems = [
    {
      group: 'Account',
      items: [
        {
          label: 'Profile',
          href: '/dashboard/profile',
          icon: User,
          description: 'Manage your account settings'
        },
        {
          label: 'Subscription',
          href: '/dashboard/subscription',
          icon: Crown,
          description: 'Billing and plan management',
          badge: user.subscriptionTier.name
        },
        {
          label: 'Settings',
          href: '/dashboard/settings',
          icon: Settings,
          description: 'Preferences and notifications'
        }
      ]
    },
    {
      group: 'Dashboard',
      items: [
        {
          label: 'Saved Searches',
          href: '/dashboard/searches',
          icon: Search,
          description: `${savedSearches.length} saved`,
          count: savedSearches.length
        },
        {
          label: 'Alerts',
          href: '/dashboard/alerts',
          icon: Bell,
          description: `${alerts.filter(a => a.isActive).length} active`,
          count: alerts.filter(a => a.isActive).length
        },
        {
          label: 'Reports',
          href: '/dashboard/reports',
          icon: FileText,
          description: `${reports.length} generated`,
          count: reports.length
        }
      ]
    }
  ]

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-50 transition-colors"
      >
        <div className="relative">
          <UserAvatar user={user} size="sm" />
          {unreadNotifications > 0 && (
            <div className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
              {unreadNotifications > 9 ? '9+' : unreadNotifications}
            </div>
          )}
        </div>

        <div className="hidden md:block text-left">
          <p className="text-sm font-medium text-planning-text-dark">
            {user.firstName} {user.lastName}
          </p>
          <p className="text-xs text-planning-text-light">
            {user.company || user.email}
          </p>
        </div>

        <ChevronDown className={`w-4 h-4 text-planning-text-light transition-transform ${
          isOpen ? 'rotate-180' : ''
        }`} />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-planning-border z-50">
          {/* User Info Header */}
          <div className="p-4 border-b border-planning-border">
            <div className="flex items-center space-x-3">
              <UserAvatar user={user} size="md" />
              <div className="flex-1 min-w-0">
                <h3 className="font-medium text-planning-text-dark">
                  {user.firstName} {user.lastName}
                </h3>
                <p className="text-sm text-planning-text-light truncate">
                  {user.email}
                </p>
                <div className="mt-2">
                  <SubscriptionBadge subscription={user.subscriptionTier} size="sm" />
                </div>
              </div>
            </div>
          </div>

          {/* Menu Items */}
          <div className="max-h-96 overflow-y-auto">
            {menuItems.map((group) => (
              <div key={group.group} className="p-2">
                <h4 className="px-3 py-2 text-xs font-semibold text-planning-text-light uppercase tracking-wide">
                  {group.group}
                </h4>
                {group.items.map((item) => {
                  const Icon = item.icon
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => setIsOpen(false)}
                      className="flex items-center space-x-3 px-3 py-2 rounded-md hover:bg-gray-50 transition-colors"
                    >
                      <Icon className="w-4 h-4 text-planning-text-light" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-planning-text-dark">
                          {item.label}
                        </p>
                        <p className="text-xs text-planning-text-light">
                          {item.description}
                        </p>
                      </div>
                      {(item as any).count !== undefined && (
                        <Badge variant="outline" size="sm">
                          {(item as any).count}
                        </Badge>
                      )}
                      {(item as any).badge && (
                        <Badge variant="secondary" size="sm">
                          {(item as any).badge}
                        </Badge>
                      )}
                    </Link>
                  )
                })}
              </div>
            ))}
          </div>

          {/* Footer */}
          <div className="p-2 border-t border-planning-border">
            <Link
              href="/help"
              onClick={() => setIsOpen(false)}
              className="flex items-center space-x-3 px-3 py-2 rounded-md hover:bg-gray-50 transition-colors"
            >
              <HelpCircle className="w-4 h-4 text-planning-text-light" />
              <span className="text-sm text-planning-text-dark">Help & Support</span>
            </Link>

            <button
              onClick={handleLogout}
              className="w-full flex items-center space-x-3 px-3 py-2 rounded-md hover:bg-gray-50 transition-colors text-left"
            >
              <LogOut className="w-4 h-4 text-planning-text-light" />
              <span className="text-sm text-planning-text-dark">Sign Out</span>
            </button>
          </div>
        </div>
      )}
    </div>
  )
}