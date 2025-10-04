'use client'

import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import { Footer } from '@/components/sections/Footer'
import { Sparkles, Play, BookOpen, Search, FileText, BarChart, Bell, Download, Filter, TrendingUp, Users, Zap } from 'lucide-react'
import Link from 'next/link'

const categories = [
  {
    icon: Zap,
    title: 'Getting Started',
    description: 'Quick start guides for new users',
    count: '8 tutorials',
    color: 'bg-cyan-50'
  },
  {
    icon: Search,
    title: 'Search & Discovery',
    description: 'Master semantic search and filters',
    count: '12 tutorials',
    color: 'bg-orange-50'
  },
  {
    icon: BarChart,
    title: 'Analytics & Insights',
    description: 'Leverage AI-powered analytics',
    count: '10 tutorials',
    color: 'bg-pink-50'
  },
  {
    icon: Bell,
    title: 'Alerts & Automation',
    description: 'Set up smart alerts and workflows',
    count: '6 tutorials',
    color: 'bg-green-50'
  },
  {
    icon: FileText,
    title: 'Reports & Export',
    description: 'Generate reports and export data',
    count: '7 tutorials',
    color: 'bg-yellow-50'
  },
  {
    icon: Users,
    title: 'Team Collaboration',
    description: 'Work together effectively',
    count: '5 tutorials',
    color: 'bg-cyan-50'
  }
]

const featuredTutorials = [
  {
    title: 'Getting Started with Planning Explorer',
    description: 'Learn the basics: creating an account, running your first search, and navigating the platform.',
    duration: '8 min',
    level: 'Beginner',
    type: 'Video',
    icon: Play,
    color: 'bg-cyan-50',
    link: '#tutorial-1'
  },
  {
    title: 'Mastering Semantic Search',
    description: 'Use natural language queries to find exactly what you need. Examples: "residential developments in Manchester", "planning applications with approval probability > 80%".',
    duration: '12 min',
    level: 'Intermediate',
    type: 'Video',
    icon: Search,
    color: 'bg-orange-50',
    link: '#tutorial-2'
  },
  {
    title: 'Advanced Filtering Techniques',
    description: 'Combine geographic filters, application types, dates, and AI predictions to narrow down results.',
    duration: '10 min',
    level: 'Advanced',
    type: 'Article',
    icon: Filter,
    color: 'bg-pink-50',
    link: '#tutorial-3'
  },
  {
    title: 'Setting Up Smart Alerts',
    description: 'Configure real-time alerts for new applications matching your criteria. Never miss an opportunity.',
    duration: '6 min',
    level: 'Beginner',
    type: 'Video',
    icon: Bell,
    color: 'bg-green-50',
    link: '#tutorial-4'
  },
  {
    title: 'Understanding AI Opportunity Scores',
    description: 'Learn how our AI calculates opportunity scores, approval likelihood, and timeline predictions.',
    duration: '15 min',
    level: 'Intermediate',
    type: 'Article',
    icon: TrendingUp,
    color: 'bg-yellow-50',
    link: '#tutorial-5'
  },
  {
    title: 'Generating Custom Reports',
    description: 'Create professional PDF reports with charts, maps, and insights. Perfect for client presentations.',
    duration: '9 min',
    level: 'Intermediate',
    type: 'Video',
    icon: FileText,
    color: 'bg-cyan-50',
    link: '#tutorial-6'
  }
]

const quickStart = [
  {
    step: '1',
    title: 'Create Your Account',
    description: 'Sign up for a free 14-day trial. No credit card required.',
    color: 'bg-cyan-50'
  },
  {
    step: '2',
    title: 'Run Your First Search',
    description: 'Try a natural language query like "new residential developments in London".',
    color: 'bg-orange-50'
  },
  {
    step: '3',
    title: 'Save & Set Alerts',
    description: 'Save your search and configure alerts for new matching applications.',
    color: 'bg-pink-50'
  },
  {
    step: '4',
    title: 'Explore AI Insights',
    description: 'Review opportunity scores, approval predictions, and market trends.',
    color: 'bg-green-50'
  }
]

const resources = [
  {
    icon: BookOpen,
    title: 'Help Center',
    description: 'Comprehensive documentation and FAQs',
    link: '/help'
  },
  {
    icon: Download,
    title: 'PDF Guides',
    description: 'Downloadable guides and cheat sheets',
    link: '#downloads'
  },
  {
    icon: Play,
    title: 'Video Library',
    description: 'Watch all tutorials on YouTube',
    link: '#videos'
  },
  {
    icon: Users,
    title: 'Community Forum',
    description: 'Ask questions and share tips',
    link: '/community'
  }
]

export default function TutorialsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Hero Section */}
      <section className="relative z-20 bg-gradient-to-br from-planning-primary via-planning-primary to-planning-accent overflow-hidden">
        <div className="absolute inset-0 overflow-hidden">
          <div className="w-full h-full bg-cover bg-center bg-no-repeat opacity-25" style={{backgroundImage: `url('https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1920&h=1080&fit=crop&crop=center')`}} />
          <div className="absolute inset-0 bg-gradient-to-br from-planning-primary/80 via-planning-primary/75 to-planning-accent/80"></div>
        </div>
        <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
          <div className="absolute top-20 left-10 w-64 h-64 bg-planning-bright/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-planning-button/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
        </div>
        <div className="relative z-10 py-20">
          <Container>
            <div className="max-w-4xl mx-auto text-center">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full border border-white/20 mb-6">
                <Sparkles className="w-4 h-4 text-planning-bright" />
                <span className="text-sm font-semibold text-white">Learn Planning Explorer</span>
              </div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold mb-4 leading-tight" style={{ color: '#FFFFFF' }}>
                <span className="block">Master Planning Intelligence</span>
                <span className="block">in Minutes, Not Weeks</span>
              </h1>
              <p className="text-xl md:text-2xl mb-8 text-white/90">
                Step-by-step tutorials, video guides, and best practices to help you get the most from Planning Explorer.
              </p>
              <div className="max-w-2xl mx-auto">
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-planning-text-light w-5 h-5" />
                  <input
                    type="text"
                    placeholder="Search tutorials..."
                    className="w-full pl-12 pr-4 py-4 rounded-2xl border-2 border-white/20 bg-white/10 backdrop-blur-sm text-white placeholder-white/60 focus:border-white/40 focus:outline-none transition-colors"
                  />
                </div>
              </div>
            </div>
          </Container>
        </div>
      </section>

      {/* Quick Start Guide */}
      <section className="py-24 bg-white relative -mt-20 z-30">
        <Container>
          <div className="text-center mb-16">
            <div className="inline-block px-4 py-2 bg-planning-button/10 rounded-full mb-6">
              <span className="text-planning-primary font-medium text-sm uppercase tracking-wider">
                Quick Start
              </span>
            </div>
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-planning-primary mb-6">
              Get Started in 4 Easy Steps
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              New to Planning Explorer? Follow this guide to get up and running
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
            {quickStart.map((item, index) => (
              <div
                key={index}
                className={`${item.color} rounded-3xl p-8 text-center hover:shadow-lg hover:scale-105 transition-all duration-300`}
              >
                <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-4 shadow-sm">
                  <span className="text-3xl font-bold text-planning-primary">{item.step}</span>
                </div>
                <h3 className="text-xl font-bold text-planning-primary mb-3">{item.title}</h3>
                <p className="text-planning-text-light text-sm leading-relaxed">{item.description}</p>
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <Link href="/pricing">
              <Button size="lg" className="bg-planning-primary text-white hover:bg-planning-accent">
                Start Free Trial
              </Button>
            </Link>
          </div>
        </Container>
      </section>

      {/* Tutorial Categories */}
      <section className="py-24 bg-gray-50">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-planning-primary mb-6">
              Tutorial Categories
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              Browse tutorials by topic to find exactly what you need
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {categories.map((category, index) => (
              <div
                key={index}
                className={`${category.color} rounded-3xl p-8 hover:shadow-lg hover:scale-105 transition-all duration-300 cursor-pointer`}
              >
                <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center mb-6 shadow-sm">
                  <category.icon className="w-8 h-8 text-planning-primary" />
                </div>
                <h3 className="text-2xl font-bold text-planning-primary mb-3">{category.title}</h3>
                <p className="text-planning-text-light mb-4 leading-relaxed">{category.description}</p>
                <p className="text-sm text-planning-primary font-semibold">{category.count}</p>
              </div>
            ))}
          </div>
        </Container>
      </section>

      {/* Featured Tutorials */}
      <section className="py-24 bg-white">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-planning-primary mb-6">
              Featured Tutorials
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              Most popular guides to help you master Planning Explorer
            </p>
          </div>

          <div className="max-w-5xl mx-auto space-y-6">
            {featuredTutorials.map((tutorial, index) => (
              <div
                key={index}
                className={`${tutorial.color} rounded-3xl p-8 hover:shadow-lg transition-all duration-300`}
              >
                <div className="flex flex-col md:flex-row md:items-start gap-6">
                  <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center flex-shrink-0 shadow-sm">
                    <tutorial.icon className="w-8 h-8 text-planning-primary" />
                  </div>
                  <div className="flex-1">
                    <div className="flex flex-wrap items-center gap-3 mb-3">
                      <h3 className="text-2xl font-bold text-planning-primary">{tutorial.title}</h3>
                      <span className="inline-block px-3 py-1 bg-planning-primary text-white text-xs font-bold rounded-full">
                        {tutorial.type}
                      </span>
                    </div>
                    <p className="text-planning-text-light mb-4 leading-relaxed">{tutorial.description}</p>
                    <div className="flex flex-wrap items-center gap-4 text-sm text-planning-text-light">
                      <span>⏱️ {tutorial.duration}</span>
                      <span>📊 {tutorial.level}</span>
                    </div>
                  </div>
                  <div className="flex-shrink-0">
                    <Link href={tutorial.link}>
                      <Button size="lg" className="bg-planning-primary text-white hover:bg-planning-accent whitespace-nowrap">
                        {tutorial.type === 'Video' ? 'Watch Now' : 'Read Article'}
                      </Button>
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Container>
      </section>

      {/* Video Series */}
      <section className="py-24 bg-gray-50">
        <Container>
          <div className="max-w-5xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-planning-primary mb-6">
                Complete Video Series
              </h2>
              <p className="text-xl text-planning-text-light">
                Watch our comprehensive video course from beginner to advanced
              </p>
            </div>

            <div className="bg-gradient-to-br from-planning-primary to-planning-accent rounded-3xl p-8 md:p-12 text-white text-center">
              <Play className="w-20 h-20 mx-auto mb-6" />
              <h3 className="text-3xl font-bold mb-4">
                Planning Explorer Masterclass
              </h3>
              <p className="text-xl text-white/90 mb-6">
                12 comprehensive video tutorials covering everything from basics to advanced features
              </p>
              <div className="flex flex-wrap justify-center gap-4 mb-8 text-sm">
                <span className="bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full">2 hours total</span>
                <span className="bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full">12 videos</span>
                <span className="bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full">All levels</span>
                <span className="bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full">Free access</span>
              </div>
              <div className="flex flex-col sm:flex-row justify-center gap-4">
                <Button size="lg" className="bg-white text-planning-primary hover:bg-gray-100">
                  <Play className="w-5 h-5 mr-2" />
                  Start Watching
                </Button>
                <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10">
                  <Download className="w-5 h-5 mr-2" />
                  Download Transcripts
                </Button>
              </div>
            </div>
          </div>
        </Container>
      </section>

      {/* Additional Resources */}
      <section className="py-24 bg-white">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-planning-primary mb-4">
              Additional Resources
            </h2>
            <p className="text-xl text-planning-text-light">
              More ways to learn and get support
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
            {resources.map((resource, index) => (
              <Link key={index} href={resource.link}>
                <div className="bg-gray-50 rounded-3xl p-8 text-center hover:shadow-lg hover:scale-105 transition-all duration-300 cursor-pointer h-full">
                  <resource.icon className="w-12 h-12 text-planning-primary mx-auto mb-4" />
                  <h3 className="text-lg font-bold text-planning-primary mb-2">{resource.title}</h3>
                  <p className="text-sm text-planning-text-light">{resource.description}</p>
                </div>
              </Link>
            ))}
          </div>
        </Container>
      </section>

      {/* Learning Paths */}
      <section className="py-24 bg-gray-50">
        <Container>
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-planning-primary mb-6">
                Recommended Learning Paths
              </h2>
              <p className="text-xl text-planning-text-light">
                Curated tutorial sequences for different roles
              </p>
            </div>

            <div className="space-y-8">
              <div className="bg-white rounded-3xl p-8 border-2 border-planning-border hover:border-planning-primary transition-all">
                <h3 className="text-2xl font-bold text-planning-primary mb-4">🏗️ For Property Developers</h3>
                <p className="text-planning-text-light mb-4">
                  Master site finding, opportunity scoring, and market analysis
                </p>
                <ul className="space-y-2 text-sm text-planning-text-light mb-4">
                  <li>✓ Getting Started → Semantic Search → Advanced Filtering → Opportunity Scores → Saved Searches & Alerts</li>
                </ul>
                <Button size="sm" className="bg-planning-primary text-white hover:bg-planning-accent">
                  Start Learning Path
                </Button>
              </div>

              <div className="bg-white rounded-3xl p-8 border-2 border-planning-border hover:border-planning-primary transition-all">
                <h3 className="text-2xl font-bold text-planning-primary mb-4">📊 For Planning Consultants</h3>
                <p className="text-planning-text-light mb-4">
                  Generate professional reports, track applications, and provide data-driven advice
                </p>
                <ul className="space-y-2 text-sm text-planning-text-light mb-4">
                  <li>✓ Getting Started → Advanced Search → Analytics & Insights → Custom Reports → Team Collaboration</li>
                </ul>
                <Button size="sm" className="bg-planning-primary text-white hover:bg-planning-accent">
                  Start Learning Path
                </Button>
              </div>

              <div className="bg-white rounded-3xl p-8 border-2 border-planning-border hover:border-planning-primary transition-all">
                <h3 className="text-2xl font-bold text-planning-primary mb-4">💼 For Land Agents</h3>
                <p className="text-planning-text-light mb-4">
                  Identify high-value sites, track market trends, and advise clients
                </p>
                <ul className="space-y-2 text-sm text-planning-text-light mb-4">
                  <li>✓ Getting Started → Geographic Search → Market Trends → Alerts → API Integration</li>
                </ul>
                <Button size="sm" className="bg-planning-primary text-white hover:bg-planning-accent">
                  Start Learning Path
                </Button>
              </div>
            </div>
          </div>
        </Container>
      </section>

      {/* CTA */}
      <section className="py-24 bg-white">
        <Container>
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-planning-primary mb-6">
              Ready to Put Your Knowledge to Work?
            </h2>
            <p className="text-xl text-planning-text-light mb-8">
              Start your free 14-day trial and apply what you've learned
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <Link href="/pricing">
                <Button size="lg" className="bg-planning-primary text-white hover:bg-planning-accent">
                  Start Free Trial
                </Button>
              </Link>
              <Link href="/support">
                <Button size="lg" variant="outline">
                  Get Support
                </Button>
              </Link>
            </div>
          </div>
        </Container>
      </section>

      <Footer />
    </div>
  )
}
