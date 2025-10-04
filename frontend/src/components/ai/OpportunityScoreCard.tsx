'use client'

import { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, AlertTriangle, CheckCircle, Brain, Info } from 'lucide-react'
import { useAIStore, OpportunityScore } from '@/lib/store'

interface OpportunityScoreCardProps {
  applicationId: string
  compact?: boolean
  showBreakdown?: boolean
  autoCalculate?: boolean
  className?: string
}

export function OpportunityScoreCard({
  applicationId,
  compact = false,
  showBreakdown = true,
  autoCalculate = true,
  className = ''
}: OpportunityScoreCardProps) {
  const [isExpanded, setIsExpanded] = useState(!compact)
  const [showTooltip, setShowTooltip] = useState(false)

  const {
    getOpportunityScore,
    calculateOpportunityScore,
    isProcessing,
    processingQueue,
    error
  } = useAIStore()

  const score = getOpportunityScore(applicationId)
  const isCalculating = processingQueue.includes(applicationId)

  useEffect(() => {
    if (autoCalculate && !score && !isCalculating) {
      calculateOpportunityScore(applicationId)
    }
  }, [applicationId, autoCalculate, score, isCalculating, calculateOpportunityScore])

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-planning-highlight'
    if (score >= 60) return 'text-planning-bright'
    if (score >= 40) return 'text-planning-accent'
    return 'text-red-500'
  }

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-planning-highlight/10'
    if (score >= 60) return 'bg-planning-bright/10'
    if (score >= 40) return 'bg-planning-accent/10'
    return 'bg-red-50'
  }

  const getScoreIcon = (score: number) => {
    if (score >= 70) return <TrendingUp className="w-4 h-4" />
    if (score >= 40) return <AlertTriangle className="w-4 h-4" />
    return <TrendingDown className="w-4 h-4" />
  }

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent'
    if (score >= 60) return 'Good'
    if (score >= 40) return 'Moderate'
    return 'Limited'
  }

  if (isCalculating) {
    return (
      <div className={`bg-white rounded-xl border border-planning-border p-4 ${className}`}>
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-planning-primary/10 rounded-full flex items-center justify-center">
            <Brain className="w-4 h-4 text-planning-primary animate-pulse" />
          </div>
          <div className="flex-1">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 border-2 border-planning-primary border-t-transparent rounded-full animate-spin"></div>
              <span className="text-sm font-medium text-planning-primary">
                Calculating AI Opportunity Score...
              </span>
            </div>
            <p className="text-xs text-planning-text-light mt-1">
              Analyzing market data and historical patterns
            </p>
          </div>
        </div>
      </div>
    )
  }

  if (error && !score) {
    return (
      <div className={`bg-white rounded-xl border border-red-200 p-4 ${className}`}>
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-red-50 rounded-full flex items-center justify-center">
            <AlertTriangle className="w-4 h-4 text-red-500" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-red-700">Score Unavailable</p>
            <p className="text-xs text-red-600 mt-1">
              Unable to calculate AI score at this time
            </p>
          </div>
          <button
            onClick={() => calculateOpportunityScore(applicationId)}
            className="text-xs text-planning-primary hover:text-planning-accent transition-colors font-medium"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  if (!score) {
    return (
      <div className={`bg-white rounded-xl border border-planning-border p-4 ${className}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-planning-primary/10 rounded-full flex items-center justify-center">
              <Brain className="w-4 h-4 text-planning-primary" />
            </div>
            <div>
              <p className="text-sm font-medium text-planning-primary">AI Opportunity Score</p>
              <p className="text-xs text-planning-text-light">Click to analyze</p>
            </div>
          </div>
          <button
            onClick={() => calculateOpportunityScore(applicationId)}
            className="px-3 py-1 bg-planning-button text-white rounded-lg text-xs font-medium hover:bg-planning-primary hover:text-white transition-colors"
          >
            Calculate
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className={`bg-white rounded-xl border border-planning-border overflow-hidden ${className}`}>
      {/* Main Score Display */}
      <div
        className={`p-4 ${getScoreBgColor(score.opportunityScore)} cursor-pointer`}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`w-10 h-10 rounded-full ${getScoreBgColor(score.opportunityScore)} border-2 border-current ${getScoreColor(score.opportunityScore)} flex items-center justify-center`}>
              {getScoreIcon(score.opportunityScore)}
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="font-semibold text-planning-primary">AI Opportunity Score</h3>
                <div
                  className="relative"
                  onMouseEnter={() => setShowTooltip(true)}
                  onMouseLeave={() => setShowTooltip(false)}
                >
                  <Info className="w-4 h-4 text-planning-text-light hover:text-planning-primary cursor-help" />
                  {showTooltip && (
                    <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-64 p-3 bg-planning-primary text-white text-xs rounded-lg shadow-lg z-10">
                      AI-powered analysis based on historical approval rates, market conditions, and planning policy alignment
                      <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-planning-primary"></div>
                    </div>
                  )}
                </div>
              </div>
              <div className="flex items-baseline space-x-2">
                <span className={`text-2xl font-bold ${getScoreColor(score.opportunityScore)}`}>
                  {score.opportunityScore}
                </span>
                <span className="text-sm text-planning-text-light">/100</span>
                <span className={`text-sm font-medium ${getScoreColor(score.opportunityScore)}`}>
                  {getScoreLabel(score.opportunityScore)}
                </span>
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="flex items-center space-x-1 text-sm text-planning-text-light">
              <CheckCircle className="w-4 h-4" />
              <span>{Math.round(score.approvalProbability * 100)}% approval chance</span>
            </div>
            <div className="text-xs text-planning-text-light mt-1">
              Confidence: {Math.round(score.confidenceScore * 100)}%
            </div>
          </div>
        </div>
      </div>

      {/* Expanded Details */}
      {isExpanded && showBreakdown && (
        <div className="p-4 border-t border-planning-border">
          {/* Score Breakdown */}
          {Object.keys(score.breakdown).length > 0 && (
            <div className="mb-4">
              <h4 className="font-medium text-planning-primary mb-3">Score Breakdown</h4>
              <div className="space-y-2">
                {Object.entries(score.breakdown).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between">
                    <span className="text-sm text-planning-text-light capitalize">
                      {key.replace(/_/g, ' ')}
                    </span>
                    <div className="flex items-center space-x-2">
                      <div className="w-20 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className={`h-full transition-all duration-300 ${
                            value >= 0.7 ? 'bg-planning-highlight' :
                            value >= 0.5 ? 'bg-planning-bright' :
                            value >= 0.3 ? 'bg-planning-accent' : 'bg-red-400'
                          }`}
                          style={{ width: `${value * 100}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium w-8 text-right">
                        {Math.round(value * 100)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* AI Rationale */}
          {score.rationale && (
            <div className="mb-4">
              <h4 className="font-medium text-planning-primary mb-2">AI Analysis</h4>
              <p className="text-sm text-planning-text-light leading-relaxed">
                {score.rationale}
              </p>
            </div>
          )}

          {/* Risk Factors */}
          {score.riskFactors.length > 0 && (
            <div className="mb-4">
              <h4 className="font-medium text-planning-primary mb-2">Risk Factors</h4>
              <ul className="space-y-1">
                {score.riskFactors.map((risk, index) => (
                  <li key={index} className="flex items-start space-x-2 text-sm">
                    <AlertTriangle className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
                    <span className="text-planning-text-light">{risk}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommendations */}
          {score.recommendations.length > 0 && (
            <div>
              <h4 className="font-medium text-planning-primary mb-2">AI Recommendations</h4>
              <ul className="space-y-1">
                {score.recommendations.map((recommendation, index) => (
                  <li key={index} className="flex items-start space-x-2 text-sm">
                    <CheckCircle className="w-4 h-4 text-planning-bright mt-0.5 flex-shrink-0" />
                    <span className="text-planning-text-light">{recommendation}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Last Updated */}
          <div className="mt-4 pt-3 border-t border-planning-border">
            <p className="text-xs text-planning-text-light">
              Last updated: {new Date(score.lastUpdated).toLocaleDateString()} at {new Date(score.lastUpdated).toLocaleTimeString()}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}