'use client'

import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import { Footer } from '@/components/sections/Footer'
import {
  TrendingUp, Target, BarChart3, Clock, Brain, Shield,
  Bell, CheckCircle, FileText, Search, Database, Zap,
  Eye, Award, Building2, LineChart, Download, Users, Sparkles, Check
} from 'lucide-react'

const painPoints = [
  {
    icon: Eye,
    title: 'Limited Market Visibility',
    description: 'Difficulty identifying viable investment opportunities early enough.'
  },
  {
    icon: Shield,
    title: 'Risk Assessment Challenges',
    description: 'Uncertainty about planning risk and project viability.'
  },
  {
    icon: Clock,
    title: 'Slow Due Diligence',
    description: 'Weeks spent on planning research during investment evaluation.'
  },
  {
    icon: BarChart3,
    title: 'Market Intelligence Gaps',
    description: 'Limited data on planning trends and approval patterns.'
  }
]

const solutions = [
  {
    icon: Brain,
    title: 'AI-Powered Deal Sourcing',
    description: 'Automatically identify investment opportunities with development potential.',
    benefits: [
      'AI spots opportunities in planning pipeline',
      'Filter by investment criteria and location',
      'Opportunity scoring based on planning viability'
    ]
  },
  {
    icon: Shield,
    title: 'Comprehensive Risk Analysis',
    description: 'Assess planning risk with AI-powered predictions and historical data.',
    benefits: [
      '95% accuracy in outcome predictions',
      'Planning constraint identification',
      'Historical success rate analysis'
    ]
  },
  {
    icon: BarChart3,
    title: 'Market Intelligence',
    description: 'Understand planning trends and development dynamics in any area.',
    benefits: [
      'Planning approval trends',
      'Authority performance metrics',
      'Development activity heat maps'
    ]
  },
  {
    icon: Database,
    title: 'Complete Due Diligence Data',
    description: 'Access comprehensive planning records for investment evaluation.',
    benefits: [
      '10+ years of planning history',
      'All planning documents and decisions',
      'Appeals and enforcement records'
    ]
  },
  {
    icon: Bell,
    title: 'Real-Time Deal Flow',
    description: 'Get instant alerts on new investment opportunities.',
    benefits: [
      'Custom deal flow criteria',
      'Email and mobile notifications',
      'First-mover advantage'
    ]
  },
  {
    icon: FileText,
    title: 'Investment Reports',
    description: 'Generate professional reports for investment committees.',
    benefits: [
      'Comprehensive planning analysis',
      'Risk assessment summaries',
      'Professional PDF exports'
    ]
  }
]

const outcomes = [
  {
    metric: '70%',
    label: 'Faster Deal Evaluation',
    description: 'Reduce due diligence from weeks to days'
  },
  {
    metric: '50%',
    label: 'More Opportunities',
    description: 'Identify viable deals earlier'
  },
  {
    metric: '95%',
    label: 'Risk Accuracy',
    description: 'Confident planning risk assessment'
  },
  {
    metric: '15x',
    label: 'ROI',
    description: 'Average return on subscription'
  }
]

const workflow = [
  {
    step: '1',
    title: 'Define Criteria',
    description: 'Set up alerts for your investment thesis and target areas.',
    icon: Target
  },
  {
    step: '2',
    title: 'AI Identifies Deals',
    description: 'Our AI analyzes planning pipeline for opportunities.',
    icon: Brain
  },
  {
    step: '3',
    title: 'Assess Risk',
    description: 'Review planning predictions, risks, and market data.',
    icon: Shield
  },
  {
    step: '4',
    title: 'Investment Decision',
    description: 'Generate reports for investment committee approval.',
    icon: FileText
  }
]

const testimonial = {
  quote: "Planning Explorer has become an essential part of our investment process. The AI-powered risk analysis and market intelligence help us make faster, more confident decisions. We've increased our deal flow by 50% while actually reducing planning-related losses.",
  author: "Michael Foster",
  role: "Investment Director",
  company: "Property Investment Partners",
  metrics: [
    { label: 'Deal Flow', value: '+50%' },
    { label: 'Due Diligence Time', value: '-70%' },
    { label: 'Planning Losses', value: '-60%' }
  ]
}

const features = [
  {
    icon: Search,
    title: 'Deal Sourcing',
    description: 'Find investment opportunities automatically'
  },
  {
    icon: Shield,
    title: 'Risk Assessment',
    description: 'AI-powered planning risk analysis'
  },
  {
    icon: BarChart3,
    title: 'Market Intelligence',
    description: 'Planning trends and approval patterns'
  },
  {
    icon: LineChart,
    title: 'Performance Tracking',
    description: 'Monitor portfolio planning applications'
  },
  {
    icon: Bell,
    title: 'Deal Alerts',
    description: 'Real-time notifications for new opportunities'
  },
  {
    icon: FileText,
    title: 'Investment Reports',
    description: 'Professional reports for committees'
  }
]

export default function InvestorsPage() {
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
                <span className="text-sm font-semibold text-white">For Property Investors</span>
              </div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold mb-4 leading-tight" style={{ color: '#FFFFFF' }}>
                <span className="block">Invest with Planning</span>
                <span className="block">Confidence and AI Intelligence</span>
              </h1>
              <p className="text-xl md:text-2xl mb-8 text-white/90">
                Stop losing deals to planning risk. Use AI to identify opportunities early,
                assess planning viability accurately, and make confident investment decisions faster.
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
              The Challenges Investors Face
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              Planning risk is the hidden cost in property investment
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
              How Planning Explorer Protects Your Investments
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              AI-powered intelligence for smarter property investment
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
              Your Investment Workflow, Enhanced
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              From deal sourcing to investment committee in record time
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
              Measurable Impact on Your Returns
            </h2>
            <p className="text-xl text-white/90 max-w-3xl mx-auto">
              Join investors making smarter decisions with better outcomes
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
                  MF
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
              Complete Investment Intelligence
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Everything you need to evaluate property investments
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
              Ready to Reduce Planning Risk?
            </h2>
            <p className="text-xl mb-8 text-white/90">
              Join property investors making smarter decisions with AI-powered planning intelligence
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
