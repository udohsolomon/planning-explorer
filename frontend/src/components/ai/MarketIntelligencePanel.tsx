'use client'

import { useState, useEffect } from 'react'
import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  MapPin,
  Clock,
  CheckCircle,
  AlertTriangle,
  Building,
  Users,
  Calendar,
  Target,
  Activity,
  Zap,
  RefreshCw
} from 'lucide-react'
import { useAIStore, MarketInsights } from '@/lib/store'

interface MarketIntelligencePanelProps {
  location?: string
  authority?: string
  developmentType?: string
  radiusKm?: number
  autoLoad?: boolean
  className?: string
}

export function MarketIntelligencePanel({
  location,
  authority,
  developmentType,
  radiusKm = 5,
  autoLoad = true,
  className = ''
}: MarketIntelligencePanelProps) {
  const [selectedTab, setSelectedTab] = useState<'overview' | 'trends' | 'comparables' | 'authority'>('overview')
  const [isExpanded, setIsExpanded] = useState(false)

  const {
    getMarketInsights,
    fetchMarketInsights,
    isProcessing,
    error
  } = useAIStore()

  const insights = getMarketInsights(location || authority || 'default')

  useEffect(() => {
    if (autoLoad && (location || authority) && !insights) {
      fetchMarketInsights({
        postcode: location,
        authority,
        development_type: developmentType,
        radius_km: radiusKm
      })
    }
  }, [location, authority, developmentType, radiusKm, autoLoad, insights, fetchMarketInsights])

  const handleRefresh = () => {
    fetchMarketInsights({
      postcode: location,
      authority,
      development_type: developmentType,
      radius_km: radiusKm
    })
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'increasing':
      case 'improving':
        return <TrendingUp className="w-4 h-4 text-planning-highlight" />
      case 'decreasing':
      case 'declining':
        return <TrendingDown className="w-4 h-4 text-red-500" />
      default:
        return <Activity className="w-4 h-4 text-planning-accent" />
    }
  }

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'increasing':
      case 'improving':
        return 'text-planning-highlight'
      case 'decreasing':
      case 'declining':
        return 'text-red-500'
      default:
        return 'text-planning-accent'
    }
  }

  const formatPercentage = (value: number) => {
    return `${Math.round(value * 100)}%`
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency: 'GBP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value)
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'trends', label: 'Market Trends', icon: TrendingUp },
    { id: 'comparables', label: 'Comparables', icon: Building },
    { id: 'authority', label: 'Authority', icon: Users }
  ]

  if (isProcessing) {
    return (
      <div className={`bg-white rounded-xl border border-planning-border p-6 ${className}`}>
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-8 h-8 bg-planning-primary/10 rounded-full flex items-center justify-center">
            <BarChart3 className="w-4 h-4 text-planning-primary animate-pulse" />
          </div>
          <div>
            <h3 className="font-semibold text-planning-primary">Market Intelligence</h3>
            <p className="text-sm text-planning-text-light">Analyzing market data...</p>
          </div>
          <div className="ml-auto w-6 h-6 border-2 border-planning-primary border-t-transparent rounded-full animate-spin"></div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="p-4 bg-planning-primary/5 rounded-lg">
              <div className="h-4 bg-planning-border rounded animate-pulse mb-2"></div>
              <div className="h-6 bg-planning-border rounded animate-pulse mb-2"></div>
              <div className="h-3 bg-planning-border rounded animate-pulse w-3/4"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (error && !insights) {
    return (
      <div className={`bg-white rounded-xl border border-red-200 p-6 ${className}`}>
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-8 h-8 bg-red-50 rounded-full flex items-center justify-center">
            <AlertTriangle className="w-4 h-4 text-red-500" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-red-700">Market Data Unavailable</h3>
            <p className="text-sm text-red-600">Unable to load market insights at this time</p>
          </div>
          <button
            onClick={handleRefresh}
            className="text-sm text-planning-primary hover:text-planning-accent transition-colors font-medium"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  if (!insights) {
    return (
      <div className={`bg-white rounded-xl border border-planning-border p-6 ${className}`}>
        <div className="text-center">
          <div className="w-12 h-12 bg-planning-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <BarChart3 className="w-6 h-6 text-planning-primary" />
          </div>
          <h3 className="font-semibold text-planning-primary mb-2">Market Intelligence</h3>
          <p className="text-sm text-planning-text-light mb-4">
            Get AI-powered market insights for your area
          </p>
          <button
            onClick={handleRefresh}
            className="px-4 py-2 bg-planning-button text-white rounded-lg hover:bg-planning-primary hover:text-white transition-colors"
          >
            Load Market Data
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className={`bg-white rounded-xl border border-planning-border overflow-hidden ${className}`}>
      {/* Header */}
      <div className="p-6 pb-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-planning-primary/10 rounded-full flex items-center justify-center">
              <BarChart3 className="w-4 h-4 text-planning-primary" />
            </div>
            <div>
              <h3 className="font-semibold text-planning-primary">Market Intelligence</h3>
              <p className="text-sm text-planning-text-light flex items-center space-x-1">
                <MapPin className="w-3 h-3" />
                <span>{insights.locationInsights?.area_description || 'Market Analysis'}</span>
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-2 text-planning-text-light hover:text-planning-primary transition-colors"
              title={isExpanded ? "Collapse" : "Expand"}
            >
              <Activity className="w-4 h-4" />
            </button>
            <button
              onClick={handleRefresh}
              className="p-2 text-planning-text-light hover:text-planning-primary transition-colors"
              title="Refresh data"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Key Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Approval Rate */}
          <div className="p-4 bg-planning-highlight/10 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-planning-highlight" />
                <span className="text-sm font-medium text-planning-primary">Approval Rate</span>
              </div>
              {getTrendIcon(insights.marketTrends?.approval_rate_trend)}
            </div>
            <div className="text-2xl font-bold text-planning-highlight">
              {formatPercentage(insights.locationInsights?.average_approval_rate || 0.73)}
            </div>
            <p className="text-xs text-planning-text-light">
              Average for this area
            </p>
          </div>

          {/* Processing Time */}
          <div className="p-4 bg-planning-bright/10 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4 text-planning-bright" />
                <span className="text-sm font-medium text-planning-primary">Processing Time</span>
              </div>
              {getTrendIcon(insights.marketTrends?.processing_time_trend)}
            </div>
            <div className="text-2xl font-bold text-planning-bright">
              {insights.locationInsights?.median_processing_time_weeks || 12}w
            </div>
            <p className="text-xs text-planning-text-light">
              Median processing time
            </p>
          </div>

          {/* Market Activity */}
          <div className="p-4 bg-planning-accent/10 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <Activity className="w-4 h-4 text-planning-accent" />
                <span className="text-sm font-medium text-planning-primary">Market Activity</span>
              </div>
              {getTrendIcon(insights.marketTrends?.application_volume_trend)}
            </div>
            <div className="text-2xl font-bold text-planning-accent">
              {insights.locationInsights?.market_activity_level || 'High'}
            </div>
            <p className="text-xs text-planning-text-light">
              Current activity level
            </p>
          </div>
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <>
          {/* Tab Navigation */}
          <div className="px-6">
            <div className="flex border-b border-planning-border">
              {tabs.map((tab) => {
                const IconComponent = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setSelectedTab(tab.id as any)}
                    className={`flex items-center space-x-2 px-4 py-3 text-sm font-medium transition-colors ${
                      selectedTab === tab.id
                        ? 'text-planning-primary border-b-2 border-planning-primary'
                        : 'text-planning-text-light hover:text-planning-primary'
                    }`}
                  >
                    <IconComponent className="w-4 h-4" />
                    <span>{tab.label}</span>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {selectedTab === 'overview' && (
              <div className="space-y-6">
                {/* Price Trends */}
                {insights.locationInsights?.price_trends && (
                  <div>
                    <h4 className="font-medium text-planning-primary mb-3">Property Prices</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="p-4 bg-planning-primary/5 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm text-planning-text-light">Residential</span>
                          <span className={getTrendColor(insights.locationInsights.price_trends.trend)}>
                            {getTrendIcon(insights.locationInsights.price_trends.trend)}
                          </span>
                        </div>
                        <div className="text-lg font-semibold text-planning-primary">
                          {formatCurrency(insights.locationInsights.price_trends.residential_per_sqm)}/m²
                        </div>
                      </div>
                      <div className="p-4 bg-planning-primary/5 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm text-planning-text-light">Commercial</span>
                          <span className={getTrendColor(insights.locationInsights.price_trends.trend)}>
                            {getTrendIcon(insights.locationInsights.price_trends.trend)}
                          </span>
                        </div>
                        <div className="text-lg font-semibold text-planning-primary">
                          {formatCurrency(insights.locationInsights.price_trends.commercial_per_sqm)}/m²
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Development Types */}
                {insights.locationInsights?.dominant_development_types && (
                  <div>
                    <h4 className="font-medium text-planning-primary mb-3">Popular Development Types</h4>
                    <div className="flex flex-wrap gap-2">
                      {insights.locationInsights.dominant_development_types.map((type: string, index: number) => (
                        <span
                          key={index}
                          className="px-3 py-1 bg-planning-button text-planning-primary rounded-full text-sm font-medium"
                        >
                          {type.charAt(0).toUpperCase() + type.slice(1)}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {selectedTab === 'trends' && (
              <div className="space-y-6">
                {/* Market Trends */}
                {insights.marketTrends?.popular_development_types && (
                  <div>
                    <h4 className="font-medium text-planning-primary mb-3">Development Type Distribution</h4>
                    <div className="space-y-3">
                      {insights.marketTrends.popular_development_types.map((item: any, index: number) => (
                        <div key={index} className="flex items-center justify-between">
                          <span className="text-sm text-planning-text-light capitalize">{item.type}</span>
                          <div className="flex items-center space-x-3">
                            <div className="w-32 h-2 bg-planning-border rounded-full overflow-hidden">
                              <div
                                className="h-full bg-planning-bright transition-all duration-300"
                                style={{ width: `${item.percentage}%` }}
                              />
                            </div>
                            <span className="text-sm font-medium text-planning-primary w-10 text-right">
                              {item.percentage}%
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Trend Indicators */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 border border-planning-border rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-sm font-medium text-planning-primary">Approval Rate</span>
                      {getTrendIcon(insights.marketTrends?.approval_rate_trend)}
                    </div>
                    <p className="text-xs text-planning-text-light">
                      {insights.marketTrends?.approval_rate_trend || 'Stable'} trend
                    </p>
                  </div>
                  <div className="p-4 border border-planning-border rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-sm font-medium text-planning-primary">Application Volume</span>
                      {getTrendIcon(insights.marketTrends?.application_volume_trend)}
                    </div>
                    <p className="text-xs text-planning-text-light">
                      {insights.marketTrends?.application_volume_trend || 'Stable'} trend
                    </p>
                  </div>
                  <div className="p-4 border border-planning-border rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-sm font-medium text-planning-primary">Processing Time</span>
                      {getTrendIcon(insights.marketTrends?.processing_time_trend)}
                    </div>
                    <p className="text-xs text-planning-text-light">
                      {insights.marketTrends?.processing_time_trend || 'Stable'} trend
                    </p>
                  </div>
                </div>
              </div>
            )}

            {selectedTab === 'comparables' && (
              <div className="space-y-4">
                <h4 className="font-medium text-planning-primary">Similar Applications</h4>
                {insights.comparableApplications?.length > 0 ? (
                  <div className="space-y-3">
                    {insights.comparableApplications.map((app: any, index: number) => (
                      <div key={index} className="p-4 border border-planning-border rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium text-planning-primary">
                            Application {app.application_id}
                          </span>
                          <div className="flex items-center space-x-2">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              app.outcome === 'approved'
                                ? 'bg-planning-highlight/10 text-planning-highlight'
                                : 'bg-red-50 text-red-600'
                            }`}>
                              {app.outcome}
                            </span>
                            <span className="text-sm text-planning-text-light">
                              {Math.round(app.similarity_score * 100)}% match
                            </span>
                          </div>
                        </div>
                        <p className="text-sm text-planning-text-light">
                          Processing time: {app.processing_weeks} weeks
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Building className="w-8 h-8 text-planning-text-light mx-auto mb-2" />
                    <p className="text-sm text-planning-text-light">No comparable applications found</p>
                  </div>
                )}
              </div>
            )}

            {selectedTab === 'authority' && (
              <div className="space-y-4">
                <h4 className="font-medium text-planning-primary">Authority Performance</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-planning-primary/5 rounded-lg">
                    <h5 className="font-medium text-planning-primary mb-2">Statistics</h5>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-planning-text-light">Approval Rate:</span>
                        <span className="font-medium text-planning-primary">
                          {formatPercentage(insights.authorityPerformance?.approval_rate || 0.73)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-planning-text-light">Avg. Processing:</span>
                        <span className="font-medium text-planning-primary">
                          {insights.authorityPerformance?.average_processing_weeks || 12} weeks
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-planning-text-light">Efficiency:</span>
                        <span className="font-medium text-planning-primary">
                          {insights.authorityPerformance?.efficiency_rating || 'Good'}
                        </span>
                      </div>
                    </div>
                  </div>

                  {insights.authorityPerformance?.recent_policy_changes && (
                    <div className="p-4 bg-planning-primary/5 rounded-lg">
                      <h5 className="font-medium text-planning-primary mb-2">Recent Changes</h5>
                      <ul className="space-y-1 text-sm">
                        {insights.authorityPerformance.recent_policy_changes.map((change: string, index: number) => (
                          <li key={index} className="flex items-start space-x-2">
                            <div className="w-1.5 h-1.5 bg-planning-bright rounded-full mt-2 flex-shrink-0"></div>
                            <span className="text-planning-text-light">{change}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* AI Recommendations */}
          {insights.recommendations && insights.recommendations.length > 0 && (
            <div className="px-6 pb-6">
              <div className="border-t border-planning-border pt-4">
                <h4 className="font-medium text-planning-primary mb-3 flex items-center space-x-2">
                  <Zap className="w-4 h-4" />
                  <span>AI Recommendations</span>
                </h4>
                <div className="space-y-2">
                  {insights.recommendations.map((rec, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 bg-planning-button/10 rounded-lg">
                      <Target className="w-4 h-4 text-planning-primary mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-planning-text-light">{rec}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {/* Footer */}
      <div className="px-6 py-3 bg-planning-primary/5 border-t border-planning-border">
        <div className="flex items-center justify-between text-xs text-planning-text-light">
          <span>Market intelligence powered by AI</span>
          <span>Updated: {new Date(insights.lastUpdated).toLocaleDateString()}</span>
        </div>
      </div>
    </div>
  )
}