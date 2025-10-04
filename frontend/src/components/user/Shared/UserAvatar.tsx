'use client'

import { User } from 'lucide-react'
import { cn } from '@/lib/utils'

interface UserAvatarProps {
  user?: {
    firstName?: string
    lastName?: string
    avatar?: string
    email?: string
  }
  size?: 'sm' | 'md' | 'lg' | 'xl'
  className?: string
  showStatus?: boolean
  status?: 'online' | 'offline' | 'away'
}

const sizeClasses = {
  sm: 'w-8 h-8 text-sm',
  md: 'w-10 h-10 text-base',
  lg: 'w-12 h-12 text-lg',
  xl: 'w-16 h-16 text-xl'
}

const statusColors = {
  online: 'bg-green-500',
  offline: 'bg-gray-400',
  away: 'bg-yellow-500'
}

function getInitials(firstName?: string, lastName?: string, email?: string): string {
  if (firstName && lastName) {
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase()
  }

  if (firstName) {
    return firstName.charAt(0).toUpperCase()
  }

  if (email) {
    return email.charAt(0).toUpperCase()
  }

  return 'U'
}

function getAvatarColor(name: string): string {
  const colors = [
    'bg-red-500',
    'bg-blue-500',
    'bg-green-500',
    'bg-yellow-500',
    'bg-purple-500',
    'bg-pink-500',
    'bg-indigo-500',
    'bg-teal-500'
  ]

  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }

  return colors[Math.abs(hash) % colors.length]
}

export function UserAvatar({
  user,
  size = 'md',
  className,
  showStatus = false,
  status = 'offline'
}: UserAvatarProps) {
  const initials = getInitials(user?.firstName, user?.lastName, user?.email)
  const colorClass = getAvatarColor(user?.firstName || user?.email || 'User')

  if (user?.avatar) {
    return (
      <div className={cn('relative', className)}>
        <img
          src={user.avatar}
          alt={`${user.firstName || 'User'} avatar`}
          className={cn(
            'rounded-full object-cover ring-2 ring-white',
            sizeClasses[size]
          )}
        />
        {showStatus && (
          <div className={cn(
            'absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full ring-2 ring-white',
            statusColors[status]
          )} />
        )}
      </div>
    )
  }

  return (
    <div className={cn('relative', className)}>
      <div
        className={cn(
          'rounded-full flex items-center justify-center text-white font-semibold ring-2 ring-white',
          sizeClasses[size],
          colorClass
        )}
      >
        {initials === 'U' ? (
          <User className={cn(
            size === 'sm' ? 'w-4 h-4' :
            size === 'md' ? 'w-5 h-5' :
            size === 'lg' ? 'w-6 h-6' :
            'w-8 h-8'
          )} />
        ) : (
          initials
        )}
      </div>
      {showStatus && (
        <div className={cn(
          'absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full ring-2 ring-white',
          statusColors[status]
        )} />
      )}
    </div>
  )
}