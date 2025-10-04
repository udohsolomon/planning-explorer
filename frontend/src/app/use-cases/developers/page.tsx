'use client'

import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import { Footer } from '@/components/sections/Footer'
import {
  Building2, Target, TrendingUp, MapPin, Clock, Brain,
  BarChart3, Bell, CheckCircle, ArrowRight, Zap,
  Search, Eye, FileText, Users, Shield, Database, Sparkles, Check
} from 'lucide-react'
import Link from 'next/link'

const painPoints = [
  {
    icon: Clock,
    title: 'Weeks of Manual Research',
    description: 'Spending countless hours searching through council portals and planning records.'
  },
  {
    icon: Target,
    title: 'Missing Opportunities',
    description: 'Viable development sites slip through the cracks due to information overload.'
  },
  {
    icon: TrendingUp,
    title: 'Uncertain Feasibility',
    description: 'Difficulty assessing approval likelihood and potential planning constraints.'
  },
  {
    icon: Eye,
    title: 'Limited Market Intelligence',
    description: 'Lack of visibility into competitor activity and market trends.'
  }
]

const solutions = [
  {
    icon: Brain,
    title: 'AI-Powered Site Discovery',
    description: 'Instantly find development opportunities with semantic search that understands your criteria.',
    benefits: [
      'Natural language queries like "5+ unit residential sites in South London"',
      'AI identifies opportunities you might have missed',
      'Automatic opportunity scoring based on your preferences'
    ]
  },
  {
    icon: Database,
    title: 'Comprehensive Planning Intelligence',
    description: 'Access 336,000+ planning applications from 321+ UK councils in one place.',
    benefits: [
      'Complete planning history for any site',
      'Real-time updates on new applications and decisions',
      '10+ years of historical data for trend analysis'
    ]
  },
  {
    icon: TrendingUp,
    title: 'Predictive Analytics',
    description: 'AI-powered predictions for approval likelihood and planning timelines.',
    benefits: [
      '95% accuracy in outcome predictions',
      'Timeline forecasting for better project planning',
      'Risk assessment for informed decision-making'
    ]
  },
  {
    icon: Eye,
    title: 'Competitor & Market Tracking',
    description: 'Monitor competitor activity and identify emerging market trends.',
    benefits: [
      'Track specific developers and their applications',
      'Get alerts when competitors submit applications',
      'Analyze market dynamics and approval patterns'
    ]
  },
  {
    icon: Bell,
    title: 'Smart Alerts & Notifications',
    description: 'Never miss opportunities with intelligent, customizable alerts.',
    benefits: [
      'Real-time notifications for new opportunities',
      'Custom triggers based on your criteria',
      'Email and mobile alerts for instant awareness'
    ]
  },
  {
    icon: BarChart3,
    title: 'Advanced Analytics Dashboard',
    description: 'Visualize planning trends and authority performance at a glance.',
    benefits: [
      'Interactive dashboards with customizable views',
      'Council approval rates and decision timelines',
      'Geographic heat maps for opportunity identification'
    ]
  }
]

const outcomes = [
  {
    metric: '85%',
    label: 'Time Saved on Research',
    description: 'Reduce weeks of manual research to minutes'
  },
  {
    metric: '40%',
    label: 'More Opportunities',
    description: 'Identify viable sites you would have missed'
  },
  {
    metric: '95%',
    label: 'Prediction Accuracy',
    description: 'Make confident decisions with AI insights'
  },
  {
    metric: '100%',
    label: 'UK Coverage',
    description: 'Access all planning data in one platform'
  }
]

const workflow = [
  {
    step: '1',
    title: 'Define Your Criteria',
    description: 'Tell Planning Explorer what you\'re looking for in natural language.',
    icon: Search
  },
  {
    step: '2',
    title: 'AI Finds Opportunities',
    description: 'Our AI analyzes 336,000+ applications to identify the best matches.',
    icon: Brain
  },
  {
    step: '3',
    title: 'Assess Feasibility',
    description: 'Review AI-powered predictions, planning history, and market insights.',
    icon: BarChart3
  },
  {
    step: '4',
    title: 'Monitor & Track',
    description: 'Set up alerts and track applications through to decision.',
    icon: Bell
  }
]

const testimonial = {
  quote: "Planning Explorer has transformed how we identify development opportunities. The AI insights save us weeks of research and the predictive analytics have increased our success rate by 40%. It's become an essential tool for our acquisitions team.",
  author: "James Mitchell",
  role: "Development Director",
  company: "Urban Development Ltd",
  metrics: [
    { label: 'Time Saved', value: '20+ hours/week' },
    { label: 'Success Rate', value: '+40%' },
    { label: 'ROI', value: '15x' }
  ]
}

const features = [
  {
    icon: Target,
    title: 'Site Identification',
    description: 'Find development sites that match your exact criteria'
  },
  {
    icon: TrendingUp,
    title: 'Feasibility Analysis',
    description: 'Assess planning constraints and approval likelihood'
  },
  {
    icon: MapPin,
    title: 'Location Intelligence',
    description: 'Analyze local planning trends and authority performance'
  },
  {
    icon: Eye,
    title: 'Competitor Tracking',
    description: 'Monitor competitor applications and strategy'
  },
  {
    icon: FileText,
    title: 'Planning History',
    description: 'Access complete planning records for any site'
  },
  {
    icon: Users,
    title: 'Team Collaboration',
    description: 'Share insights and reports with your team'
  }
]

export default function DevelopersPage() {
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
                <span className="text-sm font-semibold text-white">For Property Developers</span>
              </div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold mb-4 leading-tight" style={{ color: '#FFFFFF' }}>
                <span className="block">Find Development Opportunities</span>
                <span className="block">10x Faster with AI</span>
              </h1>
              <p className="text-xl md:text-2xl mb-8 text-white/90">
                Stop spending weeks on manual research. Use AI to identify viable development sites in minutes,
                with predictive analytics that tell you which opportunities are worth pursuing.
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
              The Challenges Developers Face
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              Traditional planning research is time-consuming, incomplete, and often leads to missed opportunities
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
            <h2 className="text-3xl md:text-4xl font-bold text-planning-primary mb-4">
              How Planning Explorer Helps
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              AI-powered intelligence that transforms your development pipeline
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
              Your Development Workflow, Supercharged
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              From opportunity identification to acquisition in four simple steps
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
              Join hundreds of developers who've transformed their acquisition process
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
                  JM
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
              Everything You Need in One Platform
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Comprehensive tools designed specifically for property developers
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

      <Footer />
    </div>
  )
}
