'use client'

import { useState } from 'react'
import { Container } from '@/components/ui/Container'
import { OpportunityScoreCard } from './OpportunityScoreCard'
import { AIInsightsSummary } from './AIInsightsSummary'
import { SemanticSearchBar } from './SemanticSearchBar'
import { MarketIntelligencePanel } from './MarketIntelligencePanel'
import { SimilarApplications } from './SimilarApplications'
import { SmartSuggestions } from './SmartSuggestions'
import { EnhancedApplicationCard } from '../enhanced/EnhancedApplicationCard'
import { SearchInterface } from '../sections/SearchInterface'
import { PlanningApplication } from '@/lib/store'
import {
  Brain,
  Sparkles,
  TrendingUp,
  Search,
  BarChart3,
  Target,
  CheckCircle,
  Code,
  Eye
} from 'lucide-react'

export function AIShowcase() {
  const [selectedDemo, setSelectedDemo] = useState<string>('overview')

  // Mock application data for testing
  const mockApplication: PlanningApplication = {
    id: 'demo-app-001',
    reference: '24/DEMO/001',
    description: 'Construction of 12 residential units with associated parking and landscaping',
    address: '123 Planning Street, London SW1A 1AA',
    postcode: 'SW1A 1AA',
    applicationType: 'Full Planning',
    status: 'approved',
    submissionDate: '2024-01-15',
    decisionDate: '2024-03-20',
    localAuthority: 'Westminster City Council',
    ward: 'St James\'s',
    coordinates: { lat: 51.4994, lng: -0.1357 },
    aiScore: 85,
    riskLevel: 'low',
    aiInsights: {
      opportunityScore: 85,
      approvalProbability: 0.87,
      confidenceScore: 0.92,
      breakdown: {
        approval_probability: 0.87,
        market_potential: 0.82,
        project_viability: 0.89,
        strategic_fit: 0.78,
        timeline_score: 0.85,
        risk_score: 0.15
      },
      rationale: 'This application shows strong potential with high approval probability based on similar successful projects in the area.',
      riskFactors: ['Limited parking provision', 'Potential neighbor objections'],
      recommendations: ['Consider additional community consultation', 'Review parking allocation'],
      summary: 'A well-structured residential development proposal with strong market fundamentals and good alignment with local planning policies.',
      keyPoints: [
        'Residential development in established area',
        'Good transport links and amenities',
        'Compliant with local density guidelines',
        'Strong architectural design'
      ],
      sentiment: 'positive',
      similarApplications: ['APP-2024-002', 'APP-2023-015']
    }
  }

  const demos = [
    {
      id: 'overview',
      title: 'AI Components Overview',
      description: 'Complete overview of all AI-powered planning tools',
      icon: Brain,
      color: 'planning-primary'
    },
    {
      id: 'search',
      title: 'Enhanced Search Interface',
      description: 'AI-powered semantic search and natural language processing',
      icon: Search,
      color: 'planning-bright'
    },
    {
      id: 'opportunity-scoring',
      title: 'Opportunity Scoring',
      description: 'AI-powered opportunity analysis with 0-100 scoring',
      icon: TrendingUp,
      color: 'planning-highlight'
    },
    {
      id: 'insights-summary',
      title: 'AI Insights & Summaries',
      description: 'Intelligent document summarization and analysis',
      icon: Sparkles,
      color: 'planning-accent'
    },
    {
      id: 'market-intelligence',
      title: 'Market Intelligence',
      description: 'Comprehensive market analysis and trends',
      icon: BarChart3,
      color: 'planning-bright'
    },
    {
      id: 'similar-applications',
      title: 'Vector Similarity Matching',
      description: 'Find similar applications using AI vector search',
      icon: Target,
      color: 'planning-highlight'
    },
    {
      id: 'smart-suggestions',
      title: 'Smart Recommendations',
      description: 'AI-powered suggestions and recommendations',
      icon: CheckCircle,
      color: 'planning-accent'
    },
    {
      id: 'enhanced-card',
      title: 'Enhanced Application Cards',
      description: 'Application cards with integrated AI features',
      icon: Code,
      color: 'planning-primary'
    }
  ]

  const handleSearch = (query: string, searchType: 'traditional' | 'semantic' | 'natural_language') => {
    console.log(`Demo search: ${query} (${searchType})`)
    // In a real implementation, this would trigger actual search
  }

  return (
    <section className="py-24 bg-gradient-to-br from-gray-50 to-white">
      <Container>
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-block px-4 py-2 bg-planning-button/10 rounded-full mb-6">
            <span className="text-planning-primary font-medium text-sm uppercase tracking-wider">
              AI-Powered Planning Tools
            </span>
          </div>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-heading font-bold text-planning-primary mb-6">
            Planning Explorer AI Showcase
          </h2>
          <p className="text-lg text-planning-text-light max-w-3xl mx-auto leading-relaxed">
            Experience the full suite of AI-powered planning tools designed with Planning Insights visual fidelity.
            All components maintain the exact design system while adding intelligent capabilities.
          </p>
        </div>

        {/* Demo Navigation */}
        <div className="mb-8">
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
            {demos.map((demo) => {
              const IconComponent = demo.icon
              return (
                <button
                  key={demo.id}
                  onClick={() => setSelectedDemo(demo.id)}
                  className={`flex flex-col items-center p-4 rounded-xl transition-all duration-200 text-center ${
                    selectedDemo === demo.id
                      ? `bg-${demo.color} text-white shadow-lg transform scale-105`
                      : 'bg-white border border-planning-border text-planning-text-light hover:border-planning-primary hover:text-planning-primary'
                  }`}
                >
                  <IconComponent className="w-6 h-6 mb-2" />
                  <span className="text-xs font-medium leading-tight">
                    {demo.title.split(' ').slice(0, 2).join(' ')}
                  </span>
                </button>
              )
            })}
          </div>
        </div>

        {/* Demo Content */}
        <div className="max-w-6xl mx-auto">
          {selectedDemo === 'overview' && (
            <div className="space-y-8">
              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-planning-primary mb-4">
                  Complete AI Planning Intelligence Suite
                </h3>
                <p className="text-planning-text-light">
                  All components designed with Planning Insights visual fidelity and enhanced with AI capabilities
                </p>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <OpportunityScoreCard
                  applicationId={mockApplication.id}
                  compact={false}
                  showBreakdown={true}
                  autoCalculate={false}
                />
                <AIInsightsSummary
                  applicationId={mockApplication.id}
                  focus="general"
                  length="medium"
                  autoGenerate={false}
                  showSentiment={true}
                />
              </div>

              <div className="mt-8">
                <SemanticSearchBar
                  placeholder="Try: 'Show me high-scoring residential developments in Westminster'"
                  showSuggestions={true}
                  showSearchType={true}
                  onSearch={handleSearch}
                />
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <SmartSuggestions
                  context="general"
                  location="Westminster"
                  maxSuggestions={4}
                  compact={true}
                />
                <MarketIntelligencePanel
                  location="SW1A 1AA"
                  authority="Westminster City Council"
                  developmentType="residential"
                  autoLoad={false}
                />
              </div>
            </div>
          )}

          {selectedDemo === 'search' && (
            <div className="space-y-8">
              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-planning-primary mb-4">
                  Enhanced Search Interface
                </h3>
                <p className="text-planning-text-light">
                  Traditional search enhanced with AI semantic search and natural language processing
                </p>
              </div>
              <SearchInterface />
            </div>
          )}

          {selectedDemo === 'opportunity-scoring' && (
            <div className="space-y-8">
              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-planning-primary mb-4">
                  AI Opportunity Scoring
                </h3>
                <p className="text-planning-text-light">
                  Comprehensive 0-100 scoring system with detailed breakdown and recommendations
                </p>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <OpportunityScoreCard
                  applicationId={mockApplication.id}
                  compact={false}
                  showBreakdown={true}
                  autoCalculate={false}
                />
                <div className="space-y-4">
                  <div className="bg-white rounded-xl border border-planning-border p-6">
                    <h4 className="font-semibold text-planning-primary mb-4">Scoring Features</h4>
                    <ul className="space-y-2 text-sm text-planning-text-light">
                      <li className="flex items-center space-x-2">
                        <CheckCircle className="w-4 h-4 text-planning-highlight" />
                        <span>Historical approval rate analysis</span>
                      </li>
                      <li className="flex items-center space-x-2">
                        <CheckCircle className="w-4 h-4 text-planning-highlight" />
                        <span>Market demand assessment</span>
                      </li>
                      <li className="flex items-center space-x-2">
                        <CheckCircle className="w-4 h-4 text-planning-highlight" />
                        <span>Planning policy alignment</span>
                      </li>
                      <li className="flex items-center space-x-2">
                        <CheckCircle className="w-4 h-4 text-planning-highlight" />
                        <span>Authority decision patterns</span>
                      </li>
                      <li className="flex items-center space-x-2">
                        <CheckCircle className="w-4 h-4 text-planning-highlight" />
                        <span>Project viability indicators</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {selectedDemo === 'insights-summary' && (
            <div className="space-y-8">
              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-planning-primary mb-4">
                  AI Insights & Document Summarization
                </h3>
                <p className="text-planning-text-light">
                  Intelligent document analysis with customizable focus and length options
                </p>
              </div>
              <AIInsightsSummary
                applicationId={mockApplication.id}
                focus="general"
                length="medium"
                autoGenerate={false}
                showSentiment={true}
              />
            </div>
          )}

          {selectedDemo === 'market-intelligence' && (
            <div className="space-y-8">
              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-planning-primary mb-4">
                  Market Intelligence Dashboard
                </h3>
                <p className="text-planning-text-light">
                  Comprehensive market analysis with trends, comparables, and authority performance
                </p>
              </div>
              <MarketIntelligencePanel
                location="SW1A 1AA"
                authority="Westminster City Council"
                developmentType="residential"
                autoLoad={false}
              />
            </div>
          )}

          {selectedDemo === 'similar-applications' && (
            <div className="space-y-8">
              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-planning-primary mb-4">
                  Vector Similarity Matching
                </h3>
                <p className="text-planning-text-light">
                  AI-powered vector search to find similar applications with detailed similarity analysis
                </p>
              </div>
              <SimilarApplications
                application={mockApplication}
                maxResults={5}
                minSimilarity={0.7}
                showFilters={true}
                autoLoad={false}
              />
            </div>
          )}

          {selectedDemo === 'smart-suggestions' && (
            <div className="space-y-8">
              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-planning-primary mb-4">
                  Smart AI Recommendations
                </h3>
                <p className="text-planning-text-light">
                  Contextual AI-powered suggestions for optimization and strategic planning
                </p>
              </div>
              <SmartSuggestions
                applicationId={mockApplication.id}
                context="application"
                location="Westminster"
                maxSuggestions={8}
                compact={false}
              />
            </div>
          )}

          {selectedDemo === 'enhanced-card' && (
            <div className="space-y-8">
              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-planning-primary mb-4">
                  Enhanced Application Cards
                </h3>
                <p className="text-planning-text-light">
                  Traditional application cards enhanced with integrated AI features and insights
                </p>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-planning-primary mb-4">Standard View</h4>
                  <EnhancedApplicationCard
                    application={mockApplication}
                    showAIFeatures={true}
                    compact={false}
                    showSimilarApplications={false}
                  />
                </div>
                <div>
                  <h4 className="font-medium text-planning-primary mb-4">Compact View</h4>
                  <EnhancedApplicationCard
                    application={mockApplication}
                    showAIFeatures={true}
                    compact={true}
                    showSimilarApplications={false}
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Design Fidelity Note */}
        <div className="mt-16 text-center">
          <div className="bg-planning-primary/5 rounded-xl p-6 max-w-4xl mx-auto">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <Eye className="w-5 h-5 text-planning-primary" />
              <h4 className="font-semibold text-planning-primary">Planning Insights Design Fidelity</h4>
            </div>
            <p className="text-planning-text-light">
              All AI components maintain exact visual fidelity to Planning Insights design system:
              colors, typography, spacing, and component patterns. AI features are seamlessly integrated
              as native functionality, not external additions.
            </p>
            <div className="mt-4 flex flex-wrap justify-center gap-4 text-sm">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-planning-primary rounded-full"></div>
                <span>Planning Primary (#043F2E)</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-planning-bright rounded-full"></div>
                <span>Planning Bright (#2DCC9E)</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-planning-highlight rounded-full"></div>
                <span>Planning Highlight (#01CD52)</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-planning-button rounded-full"></div>
                <span>Planning Button (#c8f169)</span>
              </div>
            </div>
          </div>
        </div>
      </Container>
    </section>
  )
}