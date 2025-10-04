'use client'

import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import { Footer } from '@/components/sections/Footer'
import {
  MapPin, Target, TrendingUp, Clock, Brain, BarChart3,
  Bell, CheckCircle, FileText, Search, Database, Zap,
  Eye, Award, Briefcase, Building2, Download, Users, Sparkles, Check
} from 'lucide-react'

const painPoints = [
  {
    icon: Search,
    title: 'Land Opportunities Hidden',
    description: 'Viable land opportunities buried in thousands of planning applications.'
  },
  {
    icon: TrendingUp,
    title: 'Difficult Valuations',
    description: 'Lack of comprehensive planning data for accurate land valuations.'
  },
  {
    icon: Clock,
    title: 'Time-Consuming Research',
    description: 'Hours spent searching council websites for planning information.'
  },
  {
    icon: Eye,
    title: 'Market Intelligence Gaps',
    description: 'Limited visibility into planning trends and development activity.'
  }
]

const solutions = [
  {
    icon: Brain,
    title: 'AI-Powered Land Discovery',
    description: 'Automatically identify land opportunities with development potential.',
    benefits: [
      'AI spots opportunities in planning applications',
      'Filter by size, location, and development type',
      'Opportunity scoring based on planning likelihood'
    ]
  },
  {
    icon: Database,
    title: 'Complete Planning History',
    description: 'Access full planning records for accurate land valuations.',
    benefits: [
      '10+ years of planning history for any site',
      'Previous applications and decisions',
      'Appeals and enforcement actions'
    ]
  },
  {
    icon: TrendingUp,
    title: 'Market Intelligence',
    description: 'Understand land values and development trends in any area.',
    benefits: [
      'Planning approval rates by area',
      'Development activity heat maps',
      'Land value trend analysis'
    ]
  },
  {
    icon: Bell,
    title: 'Instant Opportunity Alerts',
    description: 'Get notified immediately when new land opportunities emerge.',
    benefits: [
      'Real-time alerts for new planning applications',
      'Custom search criteria for your target areas',
      'Never miss a viable opportunity'
    ]
  },
  {
    icon: BarChart3,
    title: 'Authority Intelligence',
    description: 'Understand council attitudes and approval patterns.',
    benefits: [
      'Approval rates by development type',
      'Decision timelines and patterns',
      'Planning policy insights'
    ]
  },
  {
    icon: FileText,
    title: 'Professional Valuations',
    description: 'Generate detailed reports to support land valuations.',
    benefits: [
      'Comprehensive planning analysis',
      'Comparable development data',
      'Professional PDF reports'
    ]
  }
]

const outcomes = [
  {
    metric: '60%',
    label: 'More Opportunities',
    description: 'Identify land deals you would have missed'
  },
  {
    metric: '90%',
    label: 'Time Saved',
    description: 'Reduce research from hours to minutes'
  },
  {
    metric: '95%',
    label: 'Valuation Accuracy',
    description: 'More accurate valuations with complete data'
  },
  {
    metric: '100%',
    label: 'UK Coverage',
    description: 'Every council, every application'
  }
]

const workflow = [
  {
    step: '1',
    title: 'Define Target Areas',
    description: 'Set up searches for your target locations and development types.',
    icon: MapPin
  },
  {
    step: '2',
    title: 'AI Finds Opportunities',
    description: 'Our AI analyzes applications and identifies land opportunities.',
    icon: Brain
  },
  {
    step: '3',
    title: 'Assess Potential',
    description: 'Review planning history, approval likelihood, and market data.',
    icon: BarChart3
  },
  {
    step: '4',
    title: 'Secure & Value',
    description: 'Generate professional reports and secure the land.',
    icon: FileText
  }
]

const testimonial = {
  quote: "Planning Explorer has completely transformed how we identify land opportunities. The AI alerts mean we're first to know about new opportunities, and the comprehensive planning data gives us confidence in our valuations. We've increased our deal flow by 60% since adopting the platform.",
  author: "David Chen",
  role: "Land Acquisitions Manager",
  company: "Horizon Properties",
  metrics: [
    { label: 'Deal Flow', value: '+60%' },
    { label: 'Research Time', value: '-85%' },
    { label: 'Valuation Accuracy', value: '+40%' }
  ]
}

const features = [
  {
    icon: MapPin,
    title: 'Geographic Search',
    description: 'Find opportunities by location, radius, or authority'
  },
  {
    icon: Target,
    title: 'Opportunity Scoring',
    description: 'AI ranks opportunities by development potential'
  },
  {
    icon: TrendingUp,
    title: 'Market Trends',
    description: 'Identify emerging areas and development patterns'
  },
  {
    icon: FileText,
    title: 'Valuation Reports',
    description: 'Professional reports with planning analysis'
  },
  {
    icon: Bell,
    title: 'Real-Time Alerts',
    description: 'Instant notifications for new opportunities'
  },
  {
    icon: Database,
    title: 'Historical Data',
    description: '10+ years of planning records'
  }
]

export default function LandAgentsPage() {
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
                <span className="text-sm font-semibold text-white">For Land Agents</span>
              </div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold mb-4 leading-tight" style={{ color: '#FFFFFF' }}>
                <span className="block">Discover Land Opportunities</span>
                <span className="block">Before Your Competition</span>
              </h1>
              <p className="text-xl md:text-2xl mb-8 text-white/90">
                Stop missing valuable land deals. Use AI to identify opportunities instantly,
                access complete planning records, and provide accurate valuations with confidence.
              </p>
              <div className="flex flex-col sm:flex-row justify-center gap-4">
                <Button size="lg" className="bg-white text-planning-primary hover:bg-gray-100">
                  Start 14-Day Free Trial
                </Button>
                <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10">
                  Book a Demo
                </Button>
              </div>
              <p className="mt-6 text-sm text-white/70">
                No credit card required • Full access during trial • Cancel anytime
              </p>
            </div>
          </Container>
        </div>
      </section>

      {/* Pain Points */}
      <div className="py-20 bg-white">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-planning-primary mb-4">
              The Challenges Land Agents Face
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              Traditional land sourcing methods leave money on the table
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {painPoints.map((point, index) => {
              const Icon = point.icon
              const colors = ['bg-orange-50', 'bg-cyan-50', 'bg-pink-50', 'bg-yellow-50']
              return (
                <div key={index} className={`${colors[index % 4]} rounded-3xl p-8 text-center hover:shadow-lg hover:scale-105 transition-all`}>
                  <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-sm">
                    <Icon className="w-8 h-8 text-planning-primary" />
                  </div>
                  <h3 className="text-lg font-bold text-planning-primary mb-2">{point.title}</h3>
                  <p className="text-planning-text-light">{point.description}</p>
                </div>
              )
            })}
          </div>
        </Container>
      </div>

      {/* Solutions */}
      <div className="py-20 bg-gradient-to-b from-gray-50 to-white">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-planning-primary mb-4">
              How Planning Explorer Helps You Win More Deals
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              AI-powered intelligence for smarter land acquisitions
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {solutions.map((solution, index) => {
              const Icon = solution.icon
              const colors = ['bg-green-50', 'bg-cyan-50', 'bg-orange-50', 'bg-pink-50', 'bg-yellow-50', 'bg-green-50']
              return (
                <div key={index} className={`${colors[index % 6]} rounded-3xl p-8 hover:shadow-lg hover:scale-105 transition-all`}>
                  <div className="flex items-start gap-4 mb-4">
                    <div className="w-12 h-12 bg-white rounded-2xl flex items-center justify-center flex-shrink-0 shadow-sm">
                      <Icon className="w-6 h-6 text-planning-primary" />
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold text-planning-primary mb-2">{solution.title}</h3>
                      <p className="text-planning-text-light">{solution.description}</p>
                    </div>
                  </div>
                  <ul className="space-y-2 ml-16">
                    {solution.benefits.map((benefit, idx) => (
                      <li key={idx} className="flex items-start text-sm text-planning-text-light">
                        <Check className="w-4 h-4 text-planning-bright mr-3 flex-shrink-0 mt-0.5" />
                        {benefit}
                      </li>
                    ))}
                  </ul>
                </div>
              )
            })}
          </div>
        </Container>
      </div>

      {/* Workflow */}
      <div className="py-20 bg-white">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Your Land Sourcing Workflow, Supercharged
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              From opportunity identification to acquisition in four steps
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-8">
            {workflow.map((item, index) => {
              const Icon = item.icon
              return (
                <div key={index} className="text-center">
                  <div className="relative mb-6">
                    <div className="w-20 h-20 bg-planning-primary rounded-2xl flex items-center justify-center mx-auto">
                      <Icon className="w-10 h-10 text-white" />
                    </div>
                    <div className="absolute -top-2 -right-2 w-8 h-8 bg-planning-bright rounded-full flex items-center justify-center text-white font-bold text-sm">
                      {item.step}
                    </div>
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">{item.title}</h3>
                  <p className="text-gray-600">{item.description}</p>
                </div>
              )
            })}
          </div>
        </Container>
      </div>

      {/* Outcomes */}
      <div className="py-20 bg-gradient-to-br from-planning-primary via-planning-accent to-planning-bright text-white">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">
              Measurable Results for Your Business
            </h2>
            <p className="text-xl text-white/90 max-w-3xl mx-auto">
              Join land agents securing more deals with better margins
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-8">
            {outcomes.map((outcome, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm rounded-xl p-8 text-center">
                <div className="text-5xl font-bold mb-2">{outcome.metric}</div>
                <div className="text-xl font-semibold mb-2">{outcome.label}</div>
                <p className="text-white/80">{outcome.description}</p>
              </div>
            ))}
          </div>
        </Container>
      </div>

      {/* Testimonial */}
      <div className="py-20 bg-white">
        <Container>
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-2xl p-12 border border-gray-100 shadow-sm">
              <div className="flex items-start gap-4 mb-8">
                <div className="w-20 h-20 bg-planning-primary rounded-full flex items-center justify-center text-white text-2xl font-bold flex-shrink-0">
                  DC
                </div>
                <div>
                  <p className="text-2xl text-planning-primary italic mb-6">"{testimonial.quote}"</p>
                  <div className="mb-6">
                    <div className="font-bold text-planning-primary text-lg">{testimonial.author}</div>
                    <div className="text-planning-text-light">{testimonial.role}</div>
                    <div className="text-planning-text-light">{testimonial.company}</div>
                  </div>
                </div>
              </div>
              <div className="grid md:grid-cols-3 gap-6 pt-6 border-t border-gray-100">
                {testimonial.metrics.map((metric, index) => (
                  <div key={index} className="text-center">
                    <div className="text-3xl font-bold text-planning-primary mb-1">{metric.value}</div>
                    <div className="text-sm text-planning-text-light">{metric.label}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Container>
      </div>

      {/* Features Grid */}
      <div className="py-20 bg-gray-50">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Everything You Need for Land Acquisition
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Comprehensive tools designed for land professionals
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <div key={index} className="bg-white rounded-xl p-6 border border-gray-200 hover:border-planning-primary hover:shadow-lg transition-all">
                  <Icon className="w-10 h-10 text-planning-primary mb-4" />
                  <h3 className="text-lg font-bold text-gray-900 mb-2">{feature.title}</h3>
                  <p className="text-gray-600">{feature.description}</p>
                </div>
              )
            })}
          </div>
        </Container>
      </div>

      {/* CTA Section */}
      <div className="py-20 bg-planning-primary text-white">
        <Container>
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-4xl font-bold mb-6">
              Ready to Transform Your Land Business?
            </h2>
            <p className="text-xl mb-8 text-white/90">
              Join land agents finding better opportunities faster with AI-powered planning intelligence
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <Button size="lg" className="bg-white text-planning-primary hover:bg-gray-100">
                Start Your Free Trial
              </Button>
              <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10">
                Schedule a Demo
              </Button>
            </div>
            <p className="mt-6 text-sm text-white/70">
              Questions? Contact our team at hello@planningexplorer.co.uk
            </p>
          </div>
        </Container>
      </div>

      <Footer />
    </div>
  )
}
