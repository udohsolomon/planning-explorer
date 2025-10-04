'use client'

import { useState } from 'react'
import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import { SemanticSearchBar } from '@/components/ai/SemanticSearchBar'
import { Brain, Sparkles, Zap, ArrowRight, Play, Star } from 'lucide-react'

interface PreviewCardProps {
  title: string
  location: string
  status: string
  score: number
  isBlurred?: boolean
}

function PreviewCard({ title, location, status, score, isBlurred = false }: PreviewCardProps) {
  return (
    <div className={`bg-white rounded-xl p-6 shadow-lg border border-planning-border transition-all ${isBlurred ? 'filter blur-sm opacity-60' : 'hover:shadow-xl'}`}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="font-semibold text-planning-primary mb-2">{title}</h3>
          <p className="text-sm text-planning-text-light">{location}</p>
        </div>
        <div className="flex flex-col items-end space-y-2">
          <div className={`px-3 py-1 rounded-full text-xs font-bold ${
            score >= 80 ? 'bg-planning-bright text-white' :
            score >= 60 ? 'bg-planning-accent text-white' :
            'bg-planning-text-light text-white'
          }`}>
            AI Score: {score}
          </div>
          <div className={`px-2 py-1 rounded-full text-xs font-medium ${
            status === 'Approved' ? 'bg-planning-bright/20 text-planning-bright' :
            status === 'Pending' ? 'bg-planning-accent/20 text-planning-accent' :
            'bg-planning-text-light/20 text-planning-text-light'
          }`}>
            {status}
          </div>
        </div>
      </div>

      {isBlurred && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="bg-planning-primary/90 text-white px-4 py-2 rounded-lg text-sm font-medium">
            Sign up to view full details
          </div>
        </div>
      )}
    </div>
  )
}

export function HeroSearchSection() {
  const [searchQuery, setSearchQuery] = useState('')

  const previewResults = [
    {
      title: 'Residential Development - 24 Units',
      location: 'Canary Wharf, London E14 9SH',
      status: 'Approved',
      score: 94,
      isBlurred: false
    },
    {
      title: 'Mixed-Use Commercial Development',
      location: 'King\'s Cross, London N1C 4AG',
      status: 'Pending',
      score: 87,
      isBlurred: false
    },
    {
      title: 'Sustainable Housing Project',
      location: 'Shoreditch, London E1 6JN',
      status: 'Approved',
      score: 91,
      isBlurred: false
    },
    {
      title: 'Office Conversion to Residential',
      location: 'Hammersmith, London W6 9JH',
      status: 'Under Review',
      score: 78,
      isBlurred: true
    },
    {
      title: 'Retail & Residential Mixed Development',
      location: 'Stratford, London E20 1EJ',
      status: 'Approved',
      score: 85,
      isBlurred: true
    }
  ]

  return (
    <section className="relative min-h-screen bg-planning-accent pt-20 pb-16">
      {/* Planning overlay pattern */}
      <div className="absolute inset-0" style={{
        backgroundImage: `linear-gradient(135deg, rgba(124, 179, 66, 0.95), rgba(124, 179, 66, 0.9)),
          url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M20 0v40M0 20h40'/%3E%3C/g%3E%3C/svg%3E")`,
        backgroundSize: 'cover, 40px 40px',
        backgroundPosition: 'center'
      }} />

      <Container className="relative z-10">
        {/* Hero Content */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold text-white mb-8 leading-tight">
            Every Planning Application.
            <br />
            Every Council.
          </h1>

          <p className="text-xl md:text-2xl text-white/90 max-w-4xl mx-auto mb-12 leading-relaxed">
            Complete coverage of UK planning applications with real-time updates,
            AI-powered insights, and advanced search capabilities.
          </p>

          {/* Call to Action */}
          <div className="flex flex-col sm:flex-row justify-center items-center gap-4 mb-16">
            <Button size="lg" className="bg-white text-planning-primary hover:bg-white/90 px-8 py-4 text-lg font-semibold">
              <span>Get Started</span>
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
            <button className="flex items-center space-x-2 px-6 py-4 text-white/90 hover:text-white transition-colors">
              <Play className="w-5 h-5" />
              <span className="font-medium">View Demo</span>
            </button>
          </div>
        </div>

        {/* Search Interface - Simplified */}
        <div className="max-w-4xl mx-auto mb-16">
          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8">
            <SemanticSearchBar
              placeholder="Search planning applications across the UK..."
              showSuggestions={true}
              showSearchType={false}
              className="shadow-2xl"
            />
          </div>
        </div>

        {/* Statistics Bar - Green background matching Planning Insights */}
        <div className="absolute bottom-0 left-0 right-0 bg-planning-accent/90 backdrop-blur-sm py-6">
          <Container>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
              <div className="text-white">
                <div className="text-2xl md:text-3xl font-bold mb-1">+336K</div>
                <div className="text-sm text-white/80">Applications Tracked</div>
              </div>
              <div className="text-white">
                <div className="text-2xl md:text-3xl font-bold mb-1">+321K</div>
                <div className="text-sm text-white/80">Councils Covered</div>
              </div>
              <div className="text-white">
                <div className="text-2xl md:text-3xl font-bold mb-1">+69K</div>
                <div className="text-sm text-white/80">Monthly Updates</div>
              </div>
              <div className="text-white">
                <div className="text-2xl md:text-3xl font-bold mb-1">+239K</div>
                <div className="text-sm text-white/80">Active Users</div>
              </div>
            </div>
          </Container>
        </div>
      </Container>
    </section>
  )
}