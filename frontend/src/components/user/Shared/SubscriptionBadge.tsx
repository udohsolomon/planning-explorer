'use client'

import { Badge } from '@/components/ui/Badge'
import { Crown, Zap, Gift } from 'lucide-react'
import { SubscriptionTier } from '@/types/user'

interface SubscriptionBadgeProps {
  subscription: SubscriptionTier
  size?: 'sm' | 'md' | 'lg'
  showIcon?: boolean
  className?: string
}

const tierConfig = {
  Free: {
    icon: Gift,
    variant: 'outline' as const,
    color: 'text-gray-600'
  },
  Professional: {
    icon: Zap,
    variant: 'default' as const,
    color: 'text-planning-primary'
  },
  Enterprise: {
    icon: Crown,
    variant: 'success' as const,
    color: 'text-planning-bright'
  }
}

export function SubscriptionBadge({
  subscription,
  size = 'md',
  showIcon = true,
  className
}: SubscriptionBadgeProps) {
  const config = tierConfig[subscription.name]
  const Icon = config.icon

  return (
    <Badge
      variant={config.variant}
      size={size}
      className={className}
    >
      {showIcon && <Icon className="w-3 h-3 mr-1" />}
      {subscription.name}
    </Badge>
  )
}