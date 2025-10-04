'use client'

import { useState, useEffect } from 'react'
import {
  Lightbulb,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Target,
  Clock,
  MapPin,
  Building,
  Users,
  FileText,
  Zap,
  Brain,
  RefreshCw,
  X,
  ArrowRight,
  Star
} from 'lucide-react'
import { useAIStore, PlanningApplication } from '@/lib/store'

interface Suggestion {
  id: string
  type: 'opportunity' | 'risk' | 'action' | 'insight' | 'market'
  priority: 'high' | 'medium' | 'low'
  title: string
  description: string
  confidence: number
  actionable: boolean
  category: string
  relatedData?: any
  dismissible?: boolean
}

interface SmartSuggestionsProps {
  applicationId?: string
  application?: PlanningApplication
  location?: string
  context?: 'application' | 'search' | 'market' | 'general'
  maxSuggestions?: number
  showDismissed?: boolean
  compact?: boolean
  className?: string
  onSuggestionClick?: (suggestion: Suggestion) => void
  onSuggestionDismiss?: (suggestionId: string) => void
}

export function SmartSuggestions({
  applicationId,
  application,
  location,
  context = 'general',
  maxSuggestions = 5,
  showDismissed = false,
  compact = false,
  className = '',
  onSuggestionClick,
  onSuggestionDismiss
}: SmartSuggestionsProps) {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([])
  const [dismissedSuggestions, setDismissedSuggestions] = useState<Set<string>>(new Set())
  const [isLoading, setIsLoading] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')

  const { getOpportunityScore, getSummary, getMarketInsights } = useAIStore()

  useEffect(() => {
    generateSuggestions()
  }, [applicationId, application, location, context])

  const generateSuggestions = async () => {
    setIsLoading(true)

    try {
      // Generate contextual suggestions based on available data
      const generatedSuggestions: Suggestion[] = []

      // Application-specific suggestions
      if (applicationId || application) {
        const score = applicationId ? getOpportunityScore(applicationId) : null
        const summary = applicationId ? getSummary(applicationId) : null

        if (score) {
          // Opportunity score-based suggestions
          if (score.opportunityScore < 50) {
            generatedSuggestions.push({
              id: 'improve-score',
              type: 'action',
              priority: 'high',
              title: 'Improve Opportunity Score',
              description: `Current score is ${score.opportunityScore}/100. Consider addressing key risk factors to increase approval chances.`,
              confidence: 0.85,
              actionable: true,
              category: 'optimization',
              relatedData: { currentScore: score.opportunityScore, riskFactors: score.riskFactors },
              dismissible: true
            })
          }

          if (score.approvalProbability > 0.8) {
            generatedSuggestions.push({
              id: 'high-probability',
              type: 'opportunity',
              priority: 'medium',
              title: 'High Approval Probability',
              description: `Strong ${Math.round(score.approvalProbability * 100)}% approval chance. Consider fast-track submission.`,
              confidence: 0.9,
              actionable: true,
              category: 'strategy',
              relatedData: { probability: score.approvalProbability },
              dismissible: true
            })
          }

          // Risk-based suggestions
          if (score.riskFactors && score.riskFactors.length > 0) {
            generatedSuggestions.push({
              id: 'address-risks',
              type: 'risk',
              priority: 'high',
              title: 'Address Identified Risks',
              description: `${score.riskFactors.length} risk factors detected. Review and mitigate before submission.`,
              confidence: 0.8,
              actionable: true,
              category: 'risk-management',
              relatedData: { risks: score.riskFactors },
              dismissible: true
            })
          }
        }

        // Summary-based suggestions
        if (summary && summary.sentiment === 'negative') {
          generatedSuggestions.push({
            id: 'review-proposal',
            type: 'action',
            priority: 'medium',
            title: 'Review Proposal Details',
            description: 'AI analysis suggests potential concerns with the current proposal. Consider refinements.',
            confidence: 0.75,
            actionable: true,
            category: 'content',
            dismissible: true
          })
        }
      }

      // Location-based suggestions
      if (location) {
        const marketInsights = getMarketInsights(location)

        if (marketInsights) {
          if (marketInsights.locationInsights?.average_approval_rate < 0.6) {
            generatedSuggestions.push({
              id: 'low-approval-area',
              type: 'insight',
              priority: 'medium',
              title: 'Below Average Approval Rate',
              description: `This area has a ${Math.round((marketInsights.locationInsights.average_approval_rate || 0) * 100)}% approval rate. Consider extra due diligence.`,
              confidence: 0.82,
              actionable: true,
              category: 'market',
              relatedData: { approvalRate: marketInsights.locationInsights.average_approval_rate },
              dismissible: true
            })
          }

          if (marketInsights.marketTrends?.application_volume_trend === 'increasing') {
            generatedSuggestions.push({
              id: 'high-competition',
              type: 'market',
              priority: 'low',
              title: 'Increasing Market Activity',
              description: 'Application volumes are rising in this area. Consider timing your submission strategically.',
              confidence: 0.7,
              actionable: true,
              category: 'timing',
              dismissible: true
            })
          }
        }
      }

      // Context-specific suggestions
      switch (context) {
        case 'search':
          generatedSuggestions.push({
            id: 'semantic-search-tip',
            type: 'insight',
            priority: 'low',
            title: 'Try Semantic Search',
            description: 'Use AI-powered semantic search to find applications with similar meanings, not just keywords.',
            confidence: 0.6,
            actionable: true,
            category: 'search-tips',
            dismissible: true
          })
          break

        case 'market':
          generatedSuggestions.push({
            id: 'market-timing',
            type: 'opportunity',
            priority: 'medium',
            title: 'Optimal Submission Timing',
            description: 'Based on authority processing patterns, submit early in Q1 for faster decisions.',
            confidence: 0.78,
            actionable: true,
            category: 'timing',
            dismissible: true
          })
          break
      }

      // General helpful suggestions
      generatedSuggestions.push(
        {
          id: 'pre-app-consultation',
          type: 'action',
          priority: 'medium',
          title: 'Consider Pre-Application Consultation',
          description: 'Pre-application advice can identify issues early and improve approval chances by 15-20%.',
          confidence: 0.85,
          actionable: true,
          category: 'process',
          dismissible: true
        },
        {
          id: 'community-engagement',
          type: 'opportunity',
          priority: 'medium',
          title: 'Early Community Engagement',
          description: 'Proactive community consultation can reduce objections and support applications.',
          confidence: 0.8,
          actionable: true,
          category: 'stakeholders',
          dismissible: true
        },
        {
          id: 'sustainability-focus',
          type: 'insight',
          priority: 'high',
          title: 'Emphasize Sustainability',
          description: 'Applications with strong sustainability credentials have 25% higher approval rates.',
          confidence: 0.9,
          actionable: true,
          category: 'strategy',
          dismissible: true
        }
      )

      // Filter out dismissed suggestions and limit results
      const filteredSuggestions = generatedSuggestions
        .filter(suggestion => showDismissed || !dismissedSuggestions.has(suggestion.id))
        .slice(0, maxSuggestions)

      setSuggestions(filteredSuggestions)
    } catch (error) {
      console.error('Error generating suggestions:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDismiss = (suggestionId: string) => {
    setDismissedSuggestions(prev => new Set([...prev, suggestionId]))
    onSuggestionDismiss?.(suggestionId)
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'opportunity':
        return <TrendingUp className="w-4 h-4" />
      case 'risk':
        return <AlertTriangle className="w-4 h-4" />
      case 'action':
        return <Target className="w-4 h-4" />
      case 'insight':
        return <Lightbulb className="w-4 h-4" />
      case 'market':
        return <Building className="w-4 h-4" />
      default:
        return <Brain className="w-4 h-4" />
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'opportunity':
        return 'text-planning-highlight bg-planning-highlight/10'
      case 'risk':
        return 'text-red-600 bg-red-50'
      case 'action':
        return 'text-planning-primary bg-planning-primary/10'
      case 'insight':
        return 'text-planning-bright bg-planning-bright/10'
      case 'market':
        return 'text-planning-accent bg-planning-accent/10'
      default:
        return 'text-planning-text-light bg-planning-border'
    }
  }

  const getPriorityIndicator = (priority: string) => {
    switch (priority) {
      case 'high':
        return <div className="w-2 h-2 bg-red-500 rounded-full"></div>
      case 'medium':
        return <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
      case 'low':
        return <div className="w-2 h-2 bg-green-500 rounded-full"></div>
      default:
        return null
    }
  }

  const categories = Array.from(new Set(suggestions.map(s => s.category)))

  const filteredSuggestions = selectedCategory === 'all'
    ? suggestions
    : suggestions.filter(s => s.category === selectedCategory)

  if (isLoading) {
    return (
      <div className={`bg-white rounded-xl border border-planning-border p-6 ${className}`}>
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-8 h-8 bg-planning-primary/10 rounded-full flex items-center justify-center">
            <Brain className="w-4 h-4 text-planning-primary animate-pulse" />
          </div>
          <div>
            <h3 className="font-semibold text-planning-primary">Smart Suggestions</h3>
            <p className="text-sm text-planning-text-light">Generating AI recommendations...</p>
          </div>
          <div className="ml-auto w-6 h-6 border-2 border-planning-primary border-t-transparent rounded-full animate-spin"></div>
        </div>

        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="p-4 border border-planning-border rounded-lg">
              <div className="h-4 bg-planning-border rounded animate-pulse mb-2"></div>
              <div className="h-3 bg-planning-border rounded animate-pulse w-3/4"></div>
            </div>
          ))}
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
              <Brain className="w-4 h-4 text-planning-primary" />
            </div>
            <div>
              <h3 className="font-semibold text-planning-primary">Smart Suggestions</h3>
              <p className="text-sm text-planning-text-light flex items-center space-x-1">
                <Zap className="w-3 h-3" />
                <span>AI-powered recommendations</span>
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={generateSuggestions}
              className="p-2 text-planning-text-light hover:text-planning-primary transition-colors"
              title="Refresh suggestions"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Category Filter */}
        {!compact && categories.length > 1 && (
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedCategory('all')}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                selectedCategory === 'all'
                  ? 'bg-planning-primary text-white'
                  : 'bg-planning-border text-planning-text-light hover:bg-planning-primary/10'
              }`}
            >
              All
            </button>
            {categories.map(category => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-colors capitalize ${
                  selectedCategory === category
                    ? 'bg-planning-primary text-white'
                    : 'bg-planning-border text-planning-text-light hover:bg-planning-primary/10'
                }`}
              >
                {category.replace('-', ' ')}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Suggestions List */}
      <div className="px-6 pb-6">
        {filteredSuggestions.length === 0 ? (
          <div className="text-center py-8">
            <Lightbulb className="w-8 h-8 text-planning-text-light mx-auto mb-2" />
            <h4 className="font-medium text-planning-primary mb-1">No Suggestions Available</h4>
            <p className="text-sm text-planning-text-light">
              We'll provide recommendations as more data becomes available
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredSuggestions.map((suggestion) => (
              <div
                key={suggestion.id}
                className="border border-planning-border rounded-lg hover:border-planning-primary transition-colors"
              >
                <div className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-start space-x-3 flex-1">
                      <div className={`p-2 rounded-lg ${getTypeColor(suggestion.type)}`}>
                        {getTypeIcon(suggestion.type)}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <h4 className="font-medium text-planning-primary">{suggestion.title}</h4>
                          {getPriorityIndicator(suggestion.priority)}
                          {suggestion.actionable && (
                            <CheckCircle className="w-3 h-3 text-planning-highlight" />
                          )}
                        </div>
                        <p className="text-sm text-planning-text-light mb-2">
                          {suggestion.description}
                        </p>
                        <div className="flex items-center space-x-4 text-xs text-planning-text-light">
                          <div className="flex items-center space-x-1">
                            <Star className="w-3 h-3" />
                            <span>Confidence: {Math.round(suggestion.confidence * 100)}%</span>
                          </div>
                          <span className="capitalize">{suggestion.category.replace('-', ' ')}</span>
                          <span className="capitalize">{suggestion.priority} priority</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-1 ml-2">
                      {suggestion.actionable && (
                        <button
                          onClick={() => onSuggestionClick?.(suggestion)}
                          className="p-2 text-planning-text-light hover:text-planning-primary transition-colors"
                          title="Take action"
                        >
                          <ArrowRight className="w-4 h-4" />
                        </button>
                      )}
                      {suggestion.dismissible && (
                        <button
                          onClick={() => handleDismiss(suggestion.id)}
                          className="p-2 text-planning-text-light hover:text-red-500 transition-colors"
                          title="Dismiss suggestion"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Related Data Preview */}
                  {suggestion.relatedData && !compact && (
                    <div className="mt-3 pt-3 border-t border-planning-border">
                      <div className="flex flex-wrap gap-2 text-xs">
                        {Object.entries(suggestion.relatedData).map(([key, value]) => (
                          <span
                            key={key}
                            className="px-2 py-1 bg-planning-primary/5 text-planning-primary rounded"
                          >
                            {key.replace(/([A-Z])/g, ' $1').toLowerCase()}: {
                              typeof value === 'number' && value < 1 && value > 0
                                ? `${Math.round(value * 100)}%`
                                : String(value)
                            }
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-6 py-3 bg-planning-primary/5 border-t border-planning-border">
        <div className="flex items-center justify-between text-xs text-planning-text-light">
          <span>AI-powered recommendations updated in real-time</span>
          <span>Showing {filteredSuggestions.length} suggestions</span>
        </div>
      </div>
    </div>
  )
}