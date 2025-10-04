'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/Button'
import { Container } from '@/components/ui/Container'
import { ArrowRight, Play, Sparkles } from 'lucide-react'
import { EnhancedSearchBar } from '@/components/ai/EnhancedSearchBar'
import { PlanningStatsBar } from '@/components/sections/PlanningStatsBar'
import { cn } from '@/lib/utils'

export function HeroSlider() {
  const [isLoaded, setIsLoaded] = useState(false)
  const router = useRouter()

  useEffect(() => {
    setIsLoaded(true)
  }, [])

  const handleSearch = (query: string, searchType: 'traditional' | 'semantic' | 'natural_language') => {
    // Navigate to search results page with query and search type
    const searchParams = new URLSearchParams({
      q: query,
      type: searchType
    })

    router.push(`/search?${searchParams.toString()}`)
  }

  return (
    <>
      {/* Hero Section */}
      <section className="relative z-20 bg-gradient-to-br from-planning-primary via-planning-primary to-planning-accent overflow-visible">
        {/* Hero Background Image */}
        <div className="absolute inset-0 overflow-hidden">
          <div
            className="w-full h-full bg-cover bg-center bg-no-repeat opacity-25"
            style={{
              backgroundImage: `url('https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1920&h=1080&fit=crop&crop=center')`
            }}
          />
          <div className="absolute inset-0 bg-gradient-to-br from-planning-primary/80 via-planning-primary/75 to-planning-accent/80"></div>
        </div>

        {/* Animated Background Elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
          <div className="absolute top-20 left-10 w-64 h-64 bg-planning-bright/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-planning-button/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
          <div className="absolute top-1/2 left-1/3 w-32 h-32 bg-white/5 rounded-full blur-2xl animate-bounce delay-500"></div>
        </div>

        {/* Main Content */}
        <div className="relative z-10 flex items-center py-16 pb-20 overflow-visible">
          <Container className="overflow-visible">
            <div className="text-center max-w-5xl mx-auto">
              {/* Badge */}
              <div className={cn(
                'inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full border border-white/20 mb-6',
                'transform transition-all duration-700 delay-200',
                isLoaded ? 'translate-y-0 opacity-100' : 'translate-y-8 opacity-0'
              )}>
                <Sparkles className="w-4 h-4 text-planning-bright" />
                <span className="text-sm font-semibold text-white">AI-Powered Planning Intelligence</span>
              </div>

              {/* Main Title - Centralized and White */}
              <h1 className={cn(
                'text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold mb-4 leading-tight',
                'transform transition-all duration-700 delay-400',
                isLoaded ? 'translate-y-0 opacity-100' : 'translate-y-8 opacity-0'
              )} style={{ color: '#FFFFFF' }}>
                <span className="block">Transform Weeks of Research</span>
                <span className="block">Into Minutes of AI-Powered Insights</span>
              </h1>

              {/* Description */}
              <p className={cn(
                'text-lg md:text-xl text-white/90 mb-6 leading-relaxed max-w-3xl mx-auto',
                'transform transition-all duration-700 delay-600',
                isLoaded ? 'translate-y-0 opacity-100' : 'translate-y-8 opacity-0'
              )}>
                Planning Explorer revolutionises property intelligence with AI that instantly analyses every UK planning application, predicts approval likelihood, and identifies hidden opportunities tailored to your business.
              </p>

              {/* Enhanced Search Bar */}
              <div className={cn(
                'max-w-4xl mx-auto relative z-30',
                'transform transition-all duration-700 delay-800',
                isLoaded ? 'translate-y-0 opacity-100' : 'translate-y-8 opacity-0'
              )}>
                <EnhancedSearchBar
                  onSearch={handleSearch}
                  placeholder="Ask anything about UK planning data..."
                />
              </div>

            </div>
          </Container>
        </div>

      </section>

      {/* Planning Stats Bar */}
      <PlanningStatsBar />
    </>
  )
}