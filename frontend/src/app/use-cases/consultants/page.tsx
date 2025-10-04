'use client'

import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import { Footer } from '@/components/sections/Footer'
import {
  Briefcase, Target, TrendingUp, Clock, Brain, BarChart3,
  Bell, CheckCircle, FileText, Users, Shield, Database,
  Search, Zap, Award, MessageSquare, Download, Eye, Sparkles, Check
} from 'lucide-react'
import Link from 'next/link'

const painPoints = [
  {
    icon: Clock,
    title: 'Time-Intensive Research',
    description: 'Hours spent searching for precedents and analyzing planning history manually.'
  },
  {
    icon: FileText,
    title: 'Incomplete Data',
    description: 'Difficulty accessing comprehensive planning records and supporting documents.'
  },
  {
    icon: Target,
    title: 'Inconsistent Analysis',
    description: 'Challenges in providing consistent, data-driven advice across all applications.'
  },
  {
    icon: Users,
    title: 'Client Expectations',
    description: 'Clients demanding faster turnaround and more comprehensive market intelligence.'
  }
]

const solutions = [
  {
    icon: Brain,
    title: 'Instant Precedent Research',
    description: 'Find relevant precedents in seconds with AI-powered semantic search.',
    benefits: [
      'Natural language queries like "similar residential extensions in Westminster"',
      'AI identifies the most relevant cases automatically',
      'Compare outcomes across different authorities'
    ]
  },
  {
    icon: Database,
    title: 'Complete Planning Records',
    description: 'Access 336,000+ applications with full documentation and decision history.',
    benefits: [
      'All planning documents in one place',
      'Decision notices and consultation responses',
      'Complete application history for any site'
    ]
  },
  {
    icon: BarChart3,
    title: 'Authority Intelligence',
    description: 'Understand council performance, approval rates, and decision patterns.',
    benefits: [
      'Approval rate analysis by application type',
      'Decision timeline statistics',
      'Officer and committee decision patterns'
    ]
  },
  {
    icon: TrendingUp,
    title: 'Predictive Success Analysis',
    description: 'AI-powered predictions for application outcomes and approval likelihood.',
    benefits: [
      '95% accuracy in outcome predictions',
      'Identify potential issues before submission',
      'Evidence-based recommendations for clients'
    ]
  },
  {
    icon: FileText,
    title: 'Professional Reports',
    description: 'Generate comprehensive, bank-grade reports in minutes.',
    benefits: [
      'White-label reports with your branding',
      'Precedent analysis and recommendations',
      'Professional PDF exports for clients'
    ]
  },
  {
    icon: Bell,
    title: 'Automated Monitoring',
    description: 'Stay informed about relevant applications and decisions automatically.',
    benefits: [
      'Track applications for your clients',
      'Get alerts on relevant precedents',
      'Monitor competitor activity'
    ]
  }
]

const outcomes = [
  {
    metric: '75%',
    label: 'Time Saved',
    description: 'Reduce research time from hours to minutes'
  },
  {
    metric: '3x',
    label: 'More Clients',
    description: 'Handle more applications with same resources'
  },
  {
    metric: '95%',
    label: 'Prediction Accuracy',
    description: 'Provide data-driven advice with confidence'
  },
  {
    metric: '100%',
    label: 'Client Satisfaction',
    description: 'Deliver comprehensive insights every time'
  }
]

const workflow = [
  {
    step: '1',
    title: 'Client Enquiry',
    description: 'Receive new planning application or advice request from client.',
    icon: MessageSquare
  },
  {
    step: '2',
    title: 'Instant Research',
    description: 'Use AI search to find relevant precedents and planning history.',
    icon: Search
  },
  {
    step: '3',
    title: 'Analysis & Recommendations',
    description: 'Review AI predictions, approval rates, and authority performance.',
    icon: BarChart3
  },
  {
    step: '4',
    title: 'Client Report',
    description: 'Generate professional white-label report with comprehensive insights.',
    icon: FileText
  }
]

const testimonial = {
  quote: "Planning Explorer has revolutionized how we provide planning advice. The AI-powered precedent search and predictive analytics give us confidence in our recommendations, and our clients love the comprehensive reports. We've increased our capacity by 40% without hiring additional staff.",
  author: "Sarah Thompson",
  role: "Senior Planning Consultant",
  company: "Thompson Planning Associates",
  metrics: [
    { label: 'Research Time', value: '-80%' },
    { label: 'Client Capacity', value: '+40%' },
    { label: 'Win Rate', value: '+30%' }
  ]
}

const features = [
  {
    icon: Search,
    title: 'Precedent Search',
    description: 'Find relevant cases instantly with AI-powered search'
  },
  {
    icon: BarChart3,
    title: 'Authority Analysis',
    description: 'Understand council performance and decision patterns'
  },
  {
    icon: TrendingUp,
    title: 'Success Predictions',
    description: 'AI-powered outcome probability for applications'
  },
  {
    icon: FileText,
    title: 'White-Label Reports',
    description: 'Professional reports with your branding'
  },
  {
    icon: Bell,
    title: 'Application Monitoring',
    description: 'Track client applications and relevant precedents'
  },
  {
    icon: Users,
    title: 'Team Collaboration',
    description: 'Share research and insights across your team'
  }
]

const benefits = [
  {
    title: 'Win More Applications',
    description: 'Provide evidence-based advice that increases client success rates',
    icon: Award
  },
  {
    title: 'Deliver Faster',
    description: 'Reduce research time from days to minutes, improving client satisfaction',
    icon: Zap
  },
  {
    title: 'Scale Your Practice',
    description: 'Handle more clients without increasing headcount or overhead',
    icon: TrendingUp
  },
  {
    title: 'Stand Out',
    description: 'Differentiate your service with AI-powered insights competitors can\'t match',
    icon: Target
  }
]

export default function ConsultantsPage() {
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
                <span className="text-sm font-semibold text-white">For Planning Consultants</span>
              </div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold mb-4 leading-tight" style={{ color: '#FFFFFF' }}>
                <span className="block">Provide Better Advice</span>
                <span className="block">In a Fraction of the Time</span>
              </h1>
              <p className="text-xl md:text-2xl mb-8 text-white/90">
                Stop spending hours on manual research. Use AI to find relevant precedents instantly,
                predict application outcomes, and deliver comprehensive insights that win client trust.
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
              The Challenges Consultants Face
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              Traditional planning research methods are holding your practice back
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
              How Planning Explorer Empowers Your Practice
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              AI-powered tools that make you a more effective consultant
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

      {/* Benefits */}
      <div className="py-20 bg-white">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-planning-primary mb-4">
              Grow Your Planning Consultancy
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              The competitive advantages that set you apart
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {benefits.map((benefit, index) => {
              const Icon = benefit.icon
              const colors = ['bg-green-50', 'bg-cyan-50', 'bg-orange-50', 'bg-pink-50']
              return (
                <div key={index} className={`${colors[index % 4]} rounded-3xl p-8 hover:shadow-lg hover:scale-105 transition-all`}>
                  <Icon className="w-12 h-12 text-planning-primary mb-4" />
                  <h3 className="text-2xl font-bold text-planning-primary mb-3">{benefit.title}</h3>
                  <p className="text-planning-text-light text-lg">{benefit.description}</p>
                </div>
              )
            })}
          </div>
        </Container>
      </div>

      {/* Workflow */}
      <div className="py-20 bg-gray-50">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-planning-primary mb-4">
              Your Consulting Workflow, Streamlined
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              From client enquiry to professional report in record time
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
                  <h3 className="text-xl font-bold text-planning-primary mb-2">{item.title}</h3>
                  <p className="text-planning-text-light">{item.description}</p>
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
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Measurable Impact on Your Business
            </h2>
            <p className="text-xl text-white/90 max-w-3xl mx-auto">
              Join planning consultants delivering better results, faster
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
                  ST
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
            <h2 className="text-3xl md:text-4xl font-bold text-planning-primary mb-4">
              Professional Tools for Planning Consultants
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              Everything you need to provide exceptional planning advice
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <div key={index} className="bg-white rounded-3xl p-6 hover:shadow-lg hover:scale-105 transition-all">
                  <Icon className="w-10 h-10 text-planning-primary mb-4" />
                  <h3 className="text-lg font-bold text-planning-primary mb-2">{feature.title}</h3>
                  <p className="text-planning-text-light">{feature.description}</p>
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
