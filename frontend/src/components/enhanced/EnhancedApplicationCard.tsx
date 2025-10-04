'use client'

import { useState } from 'react'
import {
  MapPin,
  Calendar,
  Building,
  User,
  FileText,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Brain,
  Sparkles,
  Target,
  Clock,
  BarChart3
} from 'lucide-react'
import { PlanningApplication } from '@/lib/store'
import { OpportunityScoreCard } from '@/components/ai/OpportunityScoreCard'
import { AIInsightsSummary } from '@/components/ai/AIInsightsSummary'
import { SimilarApplications } from '@/components/ai/SimilarApplications'

interface EnhancedApplicationCardProps {
  application: PlanningApplication
  showAIFeatures?: boolean
  compact?: boolean
  showSimilarApplications?: boolean
  className?: string
  onViewDetails?: (application: PlanningApplication) => void
  onViewLocation?: (coordinates: { lat: number; lng: number }) => void
}

export function EnhancedApplicationCard({
  application,
  showAIFeatures = true,
  compact = false,
  showSimilarApplications = false,
  className = '',
  onViewDetails,
  onViewLocation
}: EnhancedApplicationCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [activeTab, setActiveTab] = useState<'overview' | 'ai-summary' | 'similar'>('overview')

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'approved':
        return 'text-planning-highlight bg-planning-highlight/10 border-planning-highlight/20'
      case 'refused':
        return 'text-red-600 bg-red-50 border-red-200'
      case 'pending':
        return 'text-planning-accent bg-planning-accent/10 border-planning-accent/20'
      case 'withdrawn':
        return 'text-gray-600 bg-gray-50 border-gray-200'
      default:
        return 'text-planning-text-light bg-planning-border border-planning-border'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'approved':
        return <CheckCircle className="w-4 h-4" />
      case 'refused':
        return <AlertTriangle className="w-4 h-4" />
      case 'pending':
        return <Clock className="w-4 h-4" />
      default:
        return <Building className="w-4 h-4" />
    }
  }

  const getRiskLevelColor = (riskLevel?: string) => {
    switch (riskLevel) {
      case 'low':
        return 'text-planning-highlight bg-planning-highlight/10'
      case 'medium':
        return 'text-yellow-600 bg-yellow-50'
      case 'high':
        return 'text-red-600 bg-red-50'
      default:
        return 'text-planning-text-light bg-planning-border'
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    })
  }

  return (
    <div className={`bg-white rounded-xl border border-planning-border hover:border-planning-primary transition-all duration-200 overflow-hidden ${className}`}>
      {/* Main Card Content */}
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-2">
              <h3 className="font-semibold text-planning-primary text-lg">
                {application.reference}
              </h3>
              <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(application.status)}`}>
                {getStatusIcon(application.status)}
                <span>{application.status.charAt(0).toUpperCase() + application.status.slice(1)}</span>
              </div>
              {application.applicationType && (
                <span className="px-2 py-1 bg-planning-primary/5 text-planning-primary rounded text-xs font-medium">
                  {application.applicationType}
                </span>
              )}
            </div>

            {/* AI Score and Risk Level */}
            {showAIFeatures && (application.aiScore || application.riskLevel) && (
              <div className="flex items-center space-x-3 mb-3">
                {application.aiScore && (
                  <div className="flex items-center space-x-2">
                    <Brain className="w-4 h-4 text-planning-bright" />
                    <span className="text-sm font-medium text-planning-primary">
                      AI Score: {application.aiScore}/100
                    </span>
                    <div className="w-16 h-2 bg-planning-border rounded-full overflow-hidden">
                      <div
                        className="h-full bg-planning-bright transition-all duration-300"
                        style={{ width: `${application.aiScore}%` }}
                      />
                    </div>
                  </div>
                )}
                {application.riskLevel && (
                  <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${getRiskLevelColor(application.riskLevel)}`}>
                    <Target className="w-3 h-3" />
                    <span>{application.riskLevel} risk</span>
                  </div>
                )}
              </div>
            )}

            <p className="text-planning-text-light mb-3 leading-relaxed">
              {compact
                ? `${application.description.substring(0, 120)}${application.description.length > 120 ? '...' : ''}`
                : application.description
              }
            </p>
          </div>

          {/* Quick Actions */}
          <div className="flex items-center space-x-2 ml-4">
            {showAIFeatures && (
              <button className="p-2 text-planning-text-light hover:text-planning-bright transition-colors" title="AI Insights">
                <Sparkles className="w-4 h-4" />
              </button>
            )}
            <button
              onClick={() => onViewDetails?.(application)}
              className="p-2 text-planning-text-light hover:text-planning-primary transition-colors"
              title="View details"
            >
              <ExternalLink className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Application Details */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div className="flex items-center space-x-2 text-sm text-planning-text-light">
            <MapPin className="w-4 h-4 flex-shrink-0" />
            <span className="truncate">{application.address}</span>
          </div>
          <div className="flex items-center space-x-2 text-sm text-planning-text-light">
            <Calendar className="w-4 h-4 flex-shrink-0" />
            <span>Submitted: {formatDate(application.submissionDate)}</span>
          </div>
          <div className="flex items-center space-x-2 text-sm text-planning-text-light">
            <Building className="w-4 h-4 flex-shrink-0" />
            <span>{application.localAuthority}</span>
          </div>
          {application.decisionDate && (
            <div className="flex items-center space-x-2 text-sm text-planning-text-light">
              <CheckCircle className="w-4 h-4 flex-shrink-0" />
              <span>Decision: {formatDate(application.decisionDate)}</span>
            </div>
          )}
        </div>

        {/* AI Insights Preview */}
        {showAIFeatures && application.aiInsights && !compact && (
          <div className="mb-4 p-3 bg-planning-primary/5 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <Brain className="w-4 h-4 text-planning-primary" />
              <span className="text-sm font-medium text-planning-primary">AI Insights</span>
            </div>
            <p className="text-sm text-planning-text-light">
              {application.aiInsights.summary || 'AI analysis available'}
            </p>
            {application.aiInsights.keyPoints && application.aiInsights.keyPoints.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {application.aiInsights.keyPoints.slice(0, 3).map((point, index) => (
                  <span key={index} className="px-2 py-1 bg-planning-bright/10 text-planning-bright rounded text-xs">
                    {point.length > 30 ? `${point.substring(0, 30)}...` : point}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Expand/Collapse Button */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {application.coordinates && (
              <button
                onClick={() => onViewLocation?.(application.coordinates!)}
                className="text-sm text-planning-primary hover:text-planning-accent transition-colors font-medium"
              >
                View on Map
              </button>
            )}
            {application.postcode && (
              <span className="text-sm text-planning-text-light">{application.postcode}</span>
            )}
          </div>

          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center space-x-2 text-planning-primary hover:text-planning-accent transition-colors"
          >
            <span className="text-sm font-medium">
              {isExpanded ? 'Show Less' : 'View Details'}
            </span>
            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="border-t border-planning-border">
          {/* Tab Navigation */}
          {showAIFeatures && (
            <div className="px-6 py-3 bg-planning-primary/5">
              <div className="flex space-x-1">
                {[
                  { id: 'overview', label: 'Overview', icon: FileText },
                  { id: 'ai-summary', label: 'AI Summary', icon: Brain },
                  ...(showSimilarApplications ? [{ id: 'similar', label: 'Similar Apps', icon: BarChart3 }] : [])
                ].map((tab) => {
                  const IconComponent = tab.icon
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id as any)}
                      className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                        activeTab === tab.id
                          ? 'bg-white text-planning-primary shadow-sm'
                          : 'text-planning-text-light hover:text-planning-primary hover:bg-white/50'
                      }`}
                    >
                      <IconComponent className="w-4 h-4" />
                      <span>{tab.label}</span>
                    </button>
                  )
                })}
              </div>
            </div>
          )}

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'overview' && (
              <div className="space-y-4">
                {/* Additional Details */}
                <div>
                  <h4 className="font-medium text-planning-primary mb-3">Application Details</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-planning-text-light">Ward:</span>
                      <span className="ml-2 text-planning-primary font-medium">
                        {application.ward || 'Not specified'}
                      </span>
                    </div>
                    <div>
                      <span className="text-planning-text-light">Authority:</span>
                      <span className="ml-2 text-planning-primary font-medium">
                        {application.localAuthority}
                      </span>
                    </div>
                    {application.decisionDate && (
                      <div>
                        <span className="text-planning-text-light">Decision Date:</span>
                        <span className="ml-2 text-planning-primary font-medium">
                          {formatDate(application.decisionDate)}
                        </span>
                      </div>
                    )}
                    <div>
                      <span className="text-planning-text-light">Reference:</span>
                      <span className="ml-2 text-planning-primary font-medium">
                        {application.reference}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Full Description */}
                <div>
                  <h4 className="font-medium text-planning-primary mb-2">Description</h4>
                  <p className="text-planning-text-light leading-relaxed">
                    {application.description}
                  </p>
                </div>
              </div>
            )}

            {activeTab === 'ai-summary' && showAIFeatures && (
              <div className="space-y-6">
                <OpportunityScoreCard
                  applicationId={application.id}
                  compact={false}
                  showBreakdown={true}
                  autoCalculate={true}
                />
                <AIInsightsSummary
                  applicationId={application.id}
                  focus="general"
                  length="medium"
                  autoGenerate={true}
                  showSentiment={true}
                />
              </div>
            )}

            {activeTab === 'similar' && showSimilarApplications && showAIFeatures && (
              <SimilarApplications
                application={application}
                maxResults={5}
                minSimilarity={0.7}
                showFilters={false}
                autoLoad={true}
                onApplicationClick={(similarApp) => {
                  console.log('View similar application:', similarApp)
                }}
              />
            )}
          </div>
        </div>
      )}
    </div>
  )
}