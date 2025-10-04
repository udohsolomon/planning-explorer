'use client'

import { Container } from '@/components/ui/Container'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Brain, TrendingUp, MapPin, Calendar, ArrowRight, Sparkles } from 'lucide-react'

interface InsightCardProps {
  title: string
  description: string
  insights: string[]
  location: string
  timeframe: string
  score: number
  trend: 'up' | 'down' | 'stable'
  isAIPowered?: boolean
}

function InsightCard({ title, description, insights, location, timeframe, score, trend, isAIPowered = true }: InsightCardProps) {
  const getTrendColor = () => {
    switch (trend) {
      case 'up': return 'text-planning-bright'
      case 'down': return 'text-red-500'
      default: return 'text-planning-text-light'
    }
  }

  const getTrendIcon = () => {
    switch (trend) {
      case 'up': return '↗'
      case 'down': return '↘'
      default: return '→'
    }
  }

  const getScoreColor = () => {
    if (score >= 80) return 'bg-planning-bright text-white'
    if (score >= 60) return 'bg-planning-accent text-white'
    return 'bg-planning-text-light text-white'
  }

  return (
    <Card className="p-6 hover:shadow-xl transition-all duration-300 border-2 hover:border-planning-accent/20">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-2">
          {isAIPowered && (
            <div className="flex items-center space-x-1">
              <Brain className="w-4 h-4 text-planning-bright" />
              <Badge variant="secondary" className="bg-planning-bright/10 text-planning-bright border-none">
                AI Insight
              </Badge>
            </div>
          )}
        </div>
        <div className={`px-3 py-1 rounded-full text-sm font-bold ${getScoreColor()}`}>
          {score}
        </div>
      </div>

      <h3 className="text-xl font-bold text-planning-primary mb-3">
        {title}
      </h3>

      <p className="text-planning-text-light mb-4 leading-relaxed">
        {description}
      </p>

      <div className="space-y-2 mb-6">
        {insights.map((insight, index) => (
          <div key={index} className="flex items-start space-x-2">
            <Sparkles className="w-4 h-4 text-planning-bright mt-0.5 flex-shrink-0" />
            <span className="text-sm text-planning-text-dark">{insight}</span>
          </div>
        ))}
      </div>

      <div className="flex items-center justify-between text-sm text-planning-text-light mb-4">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1">
            <MapPin className="w-4 h-4" />
            <span>{location}</span>
          </div>
          <div className="flex items-center space-x-1">
            <Calendar className="w-4 h-4" />
            <span>{timeframe}</span>
          </div>
        </div>
        <div className={`flex items-center space-x-1 ${getTrendColor()}`}>
          <TrendingUp className="w-4 h-4" />
          <span className="font-medium">{getTrendIcon()}</span>
        </div>
      </div>

      <button className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-planning-primary/5 hover:bg-planning-primary hover:text-white rounded-lg transition-colors text-planning-primary font-medium">
        <span>View Full Analysis</span>
        <ArrowRight className="w-4 h-4" />
      </button>
    </Card>
  )
}

export function FeaturedInsights() {
  const insights = [
    {
      title: 'London Residential Boom Continues',
      description: 'AI analysis reveals a 34% increase in residential approvals across Greater London boroughs, with emerging opportunities in previously overlooked areas.',
      insights: [
        'Croydon showing 67% approval rate increase',
        'New sustainable development incentives driving growth',
        'Average processing time reduced to 8.2 weeks'
      ],
      location: 'Greater London',
      timeframe: 'Last 30 days',
      score: 92,
      trend: 'up' as const
    },
    {
      title: 'Manchester Commercial Surge',
      description: 'Major commercial developments gaining momentum with AI-predicted high approval probability based on recent planning policy changes.',
      insights: [
        'Tech hub development applications up 45%',
        'City center regeneration projects accelerating',
        'Green building standards creating new opportunities'
      ],
      location: 'Manchester',
      timeframe: 'This Quarter',
      score: 87,
      trend: 'up' as const
    },
    {
      title: 'Edinburgh Housing Market Shifts',
      description: 'Planning data reveals changing patterns in Edinburgh housing approvals, with AI identifying optimal submission windows and authority preferences.',
      insights: [
        'New affordable housing quotas affecting strategies',
        'Heritage considerations becoming more flexible',
        'Student accommodation demand driving innovation'
      ],
      location: 'Edinburgh',
      timeframe: 'Last 60 days',
      score: 78,
      trend: 'stable' as const
    }
  ]

  return (
    <section className="py-20 bg-white">
      <Container>
        <div className="text-center mb-16">
          <div className="inline-block px-4 py-2 bg-planning-bright/10 rounded-full mb-6">
            <span className="text-planning-bright font-semibold text-sm uppercase tracking-wider">
              AI-Generated Market Intelligence
            </span>
          </div>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-planning-primary mb-6">
            Featured Planning Insights
          </h2>
          <p className="text-lg text-planning-text-light max-w-3xl mx-auto leading-relaxed">
            Our AI continuously analyzes planning patterns, approval trends, and market shifts to surface the most valuable insights for property professionals.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
          {insights.map((insight, index) => (
            <InsightCard key={index} {...insight} />
          ))}
        </div>

        <div className="text-center">
          <div className="bg-gradient-to-r from-planning-primary/5 to-planning-bright/5 rounded-2xl p-8">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <Brain className="w-6 h-6 text-planning-bright" />
              <h3 className="text-xl font-bold text-planning-primary">Get Personalized AI Insights</h3>
            </div>
            <p className="text-planning-text-light mb-6 max-w-2xl mx-auto">
              Our AI learns your preferences and business focus to deliver personalized insights, opportunity alerts, and market intelligence tailored specifically for your needs.
            </p>
            <button className="inline-flex items-center space-x-2 px-8 py-3 bg-planning-accent hover:bg-planning-primary text-white rounded-lg font-semibold transition-colors">
              <span>Start Your Free Trial</span>
              <ArrowRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </Container>
    </section>
  )
}