'use client'

import { useUserStore } from '@/stores/userStore'
import { Container } from '@/components/ui/Container'
import { DashboardOverview } from './DashboardOverview'
import { QuickActions } from './QuickActions'
import { RecentActivity } from './RecentActivity'
import { RecommendationsFeed } from './RecommendationsFeed'
import { UsageMeter } from '../Shared/UsageMeter'
import { UpgradePrompt } from '../Shared/UpgradePrompt'

export function UserDashboard() {
  const {
    user,
    usageMetrics,
    recommendations,
    recentActivity,
    notifications
  } = useUserStore()

  if (!user) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-planning-primary mb-2">
            Please sign in
          </h2>
          <p className="text-planning-text-light">
            You need to be signed in to access your dashboard
          </p>
        </div>
      </div>
    )
  }

  const showUpgradePrompt = user.subscriptionTier.name === 'Free' && usageMetrics && (
    usageMetrics.searches.used / usageMetrics.searches.limit > 0.8
  )

  return (
    <div className="min-h-screen bg-gray-50">
      <Container>
        <div className="py-8">
          {/* Welcome Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-planning-primary">
              Welcome back, {user.firstName}!
            </h1>
            <p className="text-planning-text-light mt-2">
              Here's what's happening with your planning insights
            </p>
          </div>

          {/* Upgrade Prompt (if applicable) */}
          {showUpgradePrompt && (
            <div className="mb-8">
              <UpgradePrompt
                currentTier={user.subscriptionTier}
                reason="limit_reached"
                onDismiss={() => {}}
              />
            </div>
          )}

          {/* Dashboard Overview */}
          <div className="mb-8">
            <DashboardOverview />
          </div>

          {/* Quick Actions */}
          <div className="mb-8">
            <QuickActions />
          </div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Column - Recent Activity */}
            <div className="lg:col-span-2 space-y-8">
              <RecentActivity activities={recentActivity} />

              {/* Usage Metrics */}
              {usageMetrics && (
                <UsageMeter
                  metrics={usageMetrics}
                  showUpgrade={user.subscriptionTier.name !== 'Enterprise'}
                />
              )}
            </div>

            {/* Right Column - Recommendations & Notifications */}
            <div className="space-y-8">
              <RecommendationsFeed recommendations={recommendations} />

              {/* Compact Usage for mobile/tablet */}
              {usageMetrics && (
                <div className="lg:hidden">
                  <UsageMeter
                    metrics={usageMetrics}
                    compact
                    showUpgrade={user.subscriptionTier.name !== 'Enterprise'}
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      </Container>
    </div>
  )
}