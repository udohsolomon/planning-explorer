'use client'

import { useState, useEffect } from 'react'
import { Brain, FileText, TrendingUp, AlertTriangle, CheckCircle, Sparkles, Eye, MoreHorizontal } from 'lucide-react'
import { useAIStore } from '@/lib/store'

interface AIInsightsSummaryProps {
  applicationId: string
  focus?: 'general' | 'risks' | 'opportunities' | 'technical' | 'compliance'
  length?: 'short' | 'medium' | 'long'
  autoGenerate?: boolean
  showSentiment?: boolean
  className?: string
}

export function AIInsightsSummary({
  applicationId,
  focus = 'general',
  length = 'medium',
  autoGenerate = true,
  showSentiment = true,
  className = ''
}: AIInsightsSummaryProps) {
  const [selectedFocus, setSelectedFocus] = useState(focus)
  const [selectedLength, setSelectedLength] = useState(length)
  const [isExpanded, setIsExpanded] = useState(false)

  const {
    getSummary,
    generateSummary,
    isProcessing,
    processingQueue,
    error
  } = useAIStore()

  const summary = getSummary(applicationId)
  const isGenerating = processingQueue.includes(applicationId)

  useEffect(() => {
    if (autoGenerate && !summary && !isGenerating) {
      generateSummary(applicationId, { focus: selectedFocus, length: selectedLength })
    }
  }, [applicationId, autoGenerate, summary, isGenerating, generateSummary, selectedFocus, selectedLength])

  const handleRegenerateSummary = () => {
    generateSummary(applicationId, { focus: selectedFocus, length: selectedLength })
  }

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive':
        return 'text-planning-highlight'
      case 'negative':
        return 'text-red-500'
      default:
        return 'text-planning-accent'
    }
  }

  const getSentimentBg = (sentiment: string) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive':
        return 'bg-planning-highlight/10'
      case 'negative':
        return 'bg-red-50'
      default:
        return 'bg-planning-accent/10'
    }
  }

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive':
        return <CheckCircle className="w-4 h-4" />
      case 'negative':
        return <AlertTriangle className="w-4 h-4" />
      default:
        return <TrendingUp className="w-4 h-4" />
    }
  }

  const focusOptions = [
    { value: 'general', label: 'General Overview', icon: FileText },
    { value: 'opportunities', label: 'Opportunities', icon: TrendingUp },
    { value: 'risks', label: 'Risk Analysis', icon: AlertTriangle },
    { value: 'technical', label: 'Technical Details', icon: Brain },
    { value: 'compliance', label: 'Compliance', icon: CheckCircle }
  ]

  const lengthOptions = [
    { value: 'short', label: 'Brief' },
    { value: 'medium', label: 'Standard' },
    { value: 'long', label: 'Detailed' }
  ]

  if (isGenerating) {
    return (
      <div className={`bg-white rounded-xl border border-planning-border p-6 ${className}`}>
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-8 h-8 bg-planning-primary/10 rounded-full flex items-center justify-center">
            <Brain className="w-4 h-4 text-planning-primary animate-pulse" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-planning-primary">AI Summary</h3>
            <p className="text-sm text-planning-text-light">Generating intelligent insights...</p>
          </div>
          <div className="w-6 h-6 border-2 border-planning-primary border-t-transparent rounded-full animate-spin"></div>
        </div>

        <div className="space-y-3">
          <div className="h-4 bg-planning-border rounded-lg animate-pulse"></div>
          <div className="h-4 bg-planning-border rounded-lg w-4/5 animate-pulse"></div>
          <div className="h-4 bg-planning-border rounded-lg w-3/5 animate-pulse"></div>
        </div>
      </div>
    )
  }

  if (error && !summary) {
    return (
      <div className={`bg-white rounded-xl border border-red-200 p-6 ${className}`}>
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-8 h-8 bg-red-50 rounded-full flex items-center justify-center">
            <AlertTriangle className="w-4 h-4 text-red-500" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-red-700">Summary Unavailable</h3>
            <p className="text-sm text-red-600">Unable to generate AI summary at this time</p>
          </div>
          <button
            onClick={handleRegenerateSummary}
            className="text-sm text-planning-primary hover:text-planning-accent transition-colors font-medium"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  if (!summary) {
    return (
      <div className={`bg-white rounded-xl border border-planning-border p-6 ${className}`}>
        <div className="text-center">
          <div className="w-12 h-12 bg-planning-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <Brain className="w-6 h-6 text-planning-primary" />
          </div>
          <h3 className="font-semibold text-planning-primary mb-2">AI Summary</h3>
          <p className="text-sm text-planning-text-light mb-4">
            Generate an intelligent summary of this planning application
          </p>

          {/* Quick Options */}
          <div className="flex flex-wrap gap-2 justify-center mb-4">
            {focusOptions.slice(0, 3).map((option) => {
              const IconComponent = option.icon
              return (
                <button
                  key={option.value}
                  onClick={() => {
                    setSelectedFocus(option.value as any)
                    generateSummary(applicationId, { focus: option.value, length: selectedLength })
                  }}
                  className="flex items-center space-x-2 px-3 py-2 bg-planning-button text-white rounded-lg text-sm hover:bg-planning-primary hover:text-white transition-colors"
                >
                  <IconComponent className="w-4 h-4" />
                  <span>{option.label}</span>
                </button>
              )
            })}
          </div>

          <button
            onClick={handleRegenerateSummary}
            className="px-4 py-2 bg-planning-primary text-white rounded-lg text-sm hover:bg-planning-accent transition-colors"
          >
            Generate Summary
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
              <Brain className="w-4 h-4 text-planning-primary" />
            </div>
            <div>
              <h3 className="font-semibold text-planning-primary">AI Summary</h3>
              {showSentiment && summary.sentiment && (
                <div className="flex items-center space-x-2 mt-1">
                  <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs ${getSentimentBg(summary.sentiment)}`}>
                    <span className={getSentimentColor(summary.sentiment)}>
                      {getSentimentIcon(summary.sentiment)}
                    </span>
                    <span className={`font-medium ${getSentimentColor(summary.sentiment)}`}>
                      {summary.sentiment.charAt(0).toUpperCase() + summary.sentiment.slice(1)} Outlook
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-2 text-planning-text-light hover:text-planning-primary transition-colors"
              title={isExpanded ? "Collapse" : "Expand details"}
            >
              <Eye className="w-4 h-4" />
            </button>
            <button
              onClick={handleRegenerateSummary}
              className="p-2 text-planning-text-light hover:text-planning-primary transition-colors"
              title="Regenerate summary"
            >
              <Sparkles className="w-4 h-4" />
            </button>
            <button className="p-2 text-planning-text-light hover:text-planning-primary transition-colors">
              <MoreHorizontal className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Summary Text */}
        <div className="prose prose-sm max-w-none">
          <p className="text-planning-text-light leading-relaxed">
            {summary.summary}
          </p>
        </div>
      </div>

      {/* Key Points */}
      {summary.keyPoints && summary.keyPoints.length > 0 && (
        <div className="px-6 pb-4">
          <h4 className="font-medium text-planning-primary mb-3 flex items-center space-x-2">
            <CheckCircle className="w-4 h-4" />
            <span>Key Insights</span>
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {summary.keyPoints.map((point: string, index: number) => (
              <div key={index} className="flex items-start space-x-2 p-3 bg-planning-primary/5 rounded-lg">
                <div className="w-2 h-2 bg-planning-bright rounded-full mt-2 flex-shrink-0"></div>
                <span className="text-sm text-planning-text-light">{point}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Expanded Controls */}
      {isExpanded && (
        <div className="p-6 pt-0 border-t border-planning-border">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Focus Selection */}
            <div>
              <label className="block text-sm font-medium text-planning-primary mb-2">
                Summary Focus
              </label>
              <div className="grid grid-cols-2 gap-2">
                {focusOptions.map((option) => {
                  const IconComponent = option.icon
                  return (
                    <button
                      key={option.value}
                      onClick={() => setSelectedFocus(option.value as any)}
                      className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-xs transition-colors ${
                        selectedFocus === option.value
                          ? 'bg-planning-primary text-white'
                          : 'bg-planning-border text-planning-text-light hover:bg-planning-primary/10'
                      }`}
                    >
                      <IconComponent className="w-3 h-3" />
                      <span>{option.label}</span>
                    </button>
                  )
                })}
              </div>
            </div>

            {/* Length Selection */}
            <div>
              <label className="block text-sm font-medium text-planning-primary mb-2">
                Summary Length
              </label>
              <div className="grid grid-cols-3 gap-2">
                {lengthOptions.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => setSelectedLength(option.value as any)}
                    className={`px-3 py-2 rounded-lg text-xs transition-colors ${
                      selectedLength === option.value
                        ? 'bg-planning-primary text-white'
                        : 'bg-planning-border text-planning-text-light hover:bg-planning-primary/10'
                    }`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Regenerate Button */}
          <div className="mt-4 pt-4 border-t border-planning-border">
            <button
              onClick={handleRegenerateSummary}
              disabled={isGenerating}
              className="w-full px-4 py-2 bg-planning-button text-white rounded-lg hover:bg-planning-primary hover:text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isGenerating ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
                  <span>Generating...</span>
                </div>
              ) : (
                <div className="flex items-center justify-center space-x-2">
                  <Sparkles className="w-4 h-4" />
                  <span>Regenerate with New Settings</span>
                </div>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="px-6 py-3 bg-planning-primary/5 border-t border-planning-border">
        <p className="text-xs text-planning-text-light">
          AI-generated summary • Last updated: {new Date(summary.lastUpdated).toLocaleDateString()} at {new Date(summary.lastUpdated).toLocaleTimeString()}
        </p>
      </div>
    </div>
  )
}