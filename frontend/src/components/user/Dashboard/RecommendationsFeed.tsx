'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Recommendation } from '@/types/user'
import { useUserStore } from '@/stores/userStore'
import {
  Lightbulb,
  Search,
  Bell,
  TrendingUp,
  MapPin,
  Eye,
  X,
  ExternalLink,
  Star,
  Target
} from 'lucide-react'

interface RecommendationsFeedProps {
  recommendations: Recommendation[]
}

const recommendationIcons = {
  opportunity: Target,
  search: Search,
  alert: Bell,
  insight: Lightbulb
}

const recommendationColors = {
  opportunity: 'text-green-600',
  search: 'text-blue-600',
  alert: 'text-orange-600',
  insight: 'text-purple-600'
}

const recommendationBgColors = {
  opportunity: 'bg-green-50',
  search: 'bg-blue-50',
  alert: 'bg-orange-50',
  insight: 'bg-purple-50'
}

const priorityColors = {
  low: 'text-gray-600',
  medium: 'text-yellow-600',
  high: 'text-red-600'
}

function RecommendationCard({ recommendation }: { recommendation: Recommendation }) {
  const {
    markRecommendationViewed,
    markRecommendationActioned,
    dismissRecommendation
  } = useUserStore()

  const Icon = recommendationIcons[recommendation.type] || Lightbulb
  const color = recommendationColors[recommendation.type] || 'text-gray-600'
  const bgColor = recommendationBgColors[recommendation.type] || 'bg-gray-50'

  const handleView = () => {
    if (!recommendation.isViewed) {
      markRecommendationViewed(recommendation.id)
    }
  }

  const handleAction = () => {
    markRecommendationActioned(recommendation.id)
    if (recommendation.actionUrl) {
      window.open(recommendation.actionUrl, '_blank')
    }
  }

  const handleDismiss = () => {
    dismissRecommendation(recommendation.id)
  }

  return (
    <div className={`p-4 border rounded-lg transition-all hover:shadow-sm ${
      recommendation.isViewed ? 'bg-white' : 'bg-blue-50/30 border-blue-200'
    }`}>
      <div className="flex items-start space-x-3">
        <div className={`w-8 h-8 ${bgColor} rounded-full flex items-center justify-center mt-0.5`}>
          <Icon className={`w-4 h-4 ${color}`} />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between">
            <h4 className="font-medium text-planning-text-dark pr-2">
              {recommendation.title}
            </h4>
            <div className="flex items-center space-x-1">
              <Badge
                variant={recommendation.priority === 'high' ? 'warning' : 'outline'}
                size="sm"
                className="text-xs"
              >
                {recommendation.priority}
              </Badge>
              <button
                onClick={handleDismiss}
                className="p-1 text-planning-text-light hover:text-planning-primary transition-colors"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          </div>

          <p className="text-sm text-planning-text-light mt-1 mb-3">
            {recommendation.description}
          </p>

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-1">
                <Star className="w-3 h-3 text-yellow-500" />
                <span className="text-xs text-planning-text-light">
                  {Math.round(recommendation.confidence * 100)}% confidence
                </span>
              </div>
              <span className="text-xs text-planning-text-light">
                {new Date(recommendation.createdAt).toLocaleDateString()}
              </span>
            </div>

            <div className="flex items-center space-x-2">
              {!recommendation.isViewed && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleView}
                  className="text-xs"
                >
                  <Eye className="w-3 h-3 mr-1" />
                  View
                </Button>
              )}
              {recommendation.actionUrl && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleAction}
                  className="text-xs"
                >
                  {recommendation.actionLabel || 'View'}
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

export function RecommendationsFeed({ recommendations }: RecommendationsFeedProps) {
  const unviewedCount = recommendations.filter(r => !r.isViewed).length

  if (recommendations.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center">
            <Lightbulb className="w-5 h-5 mr-2 text-planning-primary" />
            AI Recommendations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Lightbulb className="w-12 h-12 text-planning-text-light mx-auto mb-4" />
            <h3 className="font-medium text-planning-text-dark mb-2">
              No recommendations yet
            </h3>
            <p className="text-sm text-planning-text-light mb-4">
              Our AI will learn from your activity and provide personalized insights
            </p>
            <Button variant="outline">
              Explore Planning Data
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
            <Lightbulb className="w-5 h-5 mr-2 text-planning-primary" />
            AI Recommendations
          </CardTitle>
          {unviewedCount > 0 && (
            <Badge variant="warning" size="sm">
              {unviewedCount} new
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {recommendations.slice(0, 10).map((recommendation) => (
            <RecommendationCard
              key={recommendation.id}
              recommendation={recommendation}
            />
          ))}

          {recommendations.length > 10 && (
            <div className="pt-4 border-t">
              <Button variant="ghost" className="w-full">
                View All Recommendations ({recommendations.length})
              </Button>
            </div>
          )}
        </div>

        {/* AI Learning Status */}
        <div className="mt-6 p-4 bg-planning-primary/5 border border-planning-primary/20 rounded-lg">
          <div className="flex items-start space-x-3">
            <TrendingUp className="w-5 h-5 text-planning-primary mt-0.5" />
            <div>
              <h4 className="font-medium text-planning-primary">AI Learning Progress</h4>
              <p className="text-sm text-planning-text-light mt-1">
                Our AI has analyzed your preferences and is providing increasingly relevant recommendations.
              </p>
              <div className="mt-3">
                <div className="flex items-center justify-between text-xs text-planning-text-light mb-1">
                  <span>Learning progress</span>
                  <span>78%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-1.5">
                  <div className="bg-planning-primary h-1.5 rounded-full" style={{ width: '78%' }} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}