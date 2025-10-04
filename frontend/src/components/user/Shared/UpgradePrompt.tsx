'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Crown, Zap, ArrowRight, Check, X } from 'lucide-react'
import { SubscriptionTier } from '@/types/user'

interface UpgradePromptProps {
  currentTier: SubscriptionTier
  onUpgrade?: () => void
  onDismiss?: () => void
  reason?: 'limit_reached' | 'feature_locked' | 'general'
  feature?: string
  compact?: boolean
}

const upgradeReasons = {
  limit_reached: {
    title: 'Usage limit reached',
    description: 'You\'ve reached your monthly limit. Upgrade to continue exploring.',
    icon: Zap
  },
  feature_locked: {
    title: 'Premium feature',
    description: 'This feature is available for Professional and Enterprise users.',
    icon: Crown
  },
  general: {
    title: 'Unlock more with Pro',
    description: 'Get unlimited searches, advanced analytics, and priority support.',
    icon: Crown
  }
}

const tierBenefits = {
  Professional: [
    'Unlimited searches',
    'Advanced AI insights',
    'Export capabilities',
    'Priority support',
    'Custom alerts'
  ],
  Enterprise: [
    'Everything in Professional',
    'Team collaboration',
    'API access',
    'Custom reporting',
    'Dedicated support'
  ]
}

export function UpgradePrompt({
  currentTier,
  onUpgrade,
  onDismiss,
  reason = 'general',
  feature,
  compact = false
}: UpgradePromptProps) {
  const config = upgradeReasons[reason]
  const Icon = config.icon

  const targetTier = currentTier.name === 'Free' ? 'Professional' : 'Enterprise'
  const benefits = tierBenefits[targetTier as keyof typeof tierBenefits]

  if (compact) {
    return (
      <div className="flex items-center justify-between p-4 bg-gradient-to-r from-planning-primary to-planning-accent rounded-lg text-white">
        <div className="flex items-center space-x-3">
          <Icon className="w-5 h-5" />
          <div>
            <h4 className="font-medium">{config.title}</h4>
            {feature && (
              <p className="text-sm opacity-90">Unlock {feature} and more</p>
            )}
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="secondary" size="sm" onClick={onUpgrade}>
            Upgrade
          </Button>
          {onDismiss && (
            <button
              onClick={onDismiss}
              className="p-1 hover:bg-white/10 rounded transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    )
  }

  return (
    <Card className="border-planning-primary/20 bg-gradient-to-br from-planning-primary/5 to-planning-accent/5">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-planning-primary/10 rounded-lg flex items-center justify-center">
              <Icon className="w-5 h-5 text-planning-primary" />
            </div>
            <div>
              <CardTitle className="text-lg">{config.title}</CardTitle>
              <p className="text-sm text-planning-text-light">
                {feature ? `Unlock ${feature} and more` : config.description}
              </p>
            </div>
          </div>
          {onDismiss && (
            <button
              onClick={onDismiss}
              className="p-1 text-planning-text-light hover:text-planning-primary transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <div className="flex items-center space-x-2 mb-3">
              <Badge variant="success" size="sm">
                <Crown className="w-3 h-3 mr-1" />
                {targetTier}
              </Badge>
              <span className="text-sm text-planning-text-light">
                Starting at £{targetTier === 'Professional' ? '49' : '149'}/month
              </span>
            </div>
            <ul className="space-y-2">
              {benefits.map((benefit, index) => (
                <li key={index} className="flex items-center space-x-2 text-sm">
                  <Check className="w-4 h-4 text-planning-bright" />
                  <span>{benefit}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="flex space-x-3">
            <Button onClick={onUpgrade} className="flex-1">
              Upgrade Now
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
            <Button variant="outline">
              Compare Plans
            </Button>
          </div>

          <p className="text-xs text-planning-text-light text-center">
            30-day money-back guarantee • Cancel anytime
          </p>
        </div>
      </CardContent>
    </Card>
  )
}