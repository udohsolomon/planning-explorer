'use client'

import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import { Footer } from '@/components/sections/Footer'
import {
  Ruler, Target, TrendingUp, Clock, Brain, BarChart3,
  Bell, CheckCircle, FileText, Search, Database, Zap,
  Eye, Award, Building2, Layers, Download, Users, Sparkles, Check
} from 'lucide-react'

const painPoints = [
  {
    icon: Search,
    title: 'Difficult Precedent Research',
    description: 'Hours spent searching for relevant planning precedents and design examples.'
  },
  {
    icon: Target,
    title: 'Policy Interpretation',
    description: 'Uncertainty about local planning policies and their practical application.'
  },
  {
    icon: Clock,
    title: 'Approval Delays',
    description: 'Applications delayed or refused due to lack of local planning intelligence.'
  },
  {
    icon: TrendingUp,
    title: 'Competitive Pressure',
    description: 'Need to demonstrate planning viability to win more commissions.'
  }
]

const solutions = [
  {
    icon: Brain,
    title: 'Instant Precedent Research',
    description: 'Find relevant approved designs and precedents in seconds.',
    benefits: [
      'Search by design type, location, and authority',
      'AI identifies the most relevant precedents',
      'Access full design documents and decisions'
    ]
  },
  {
    icon: Database,
    title: 'Comprehensive Planning Records',
    description: 'Access complete planning history for any site or area.',
    benefits: [
      'Previous applications and amendments',
      'Appeal decisions and outcomes',
      'Conservation area and policy constraints'
    ]
  },
  {
    icon: BarChart3,
    title: 'Authority Intelligence',
    description: 'Understand what each planning authority approves and why.',
    benefits: [
      'Approval rates by design type',
      'Common refusal reasons',
      'Officer and committee preferences'
    ]
  },
  {
    icon: TrendingUp,
    title: 'Success Prediction',
    description: 'AI-powered predictions for design approval likelihood.',
    benefits: [
      '95% accuracy in outcome predictions',
      'Identify potential design issues early',
      'Evidence-based design recommendations'
    ]
  },
  {
    icon: Eye,
    title: 'Local Design Trends',
    description: 'Understand what designs are being approved in your target areas.',
    benefits: [
      'Recent approval patterns',
      'Material and design preferences',
      'Emerging planning policy trends'
    ]
  },
  {
    icon: FileText,
    title: 'Professional Reports',
    description: 'Generate planning analysis reports to strengthen proposals.',
    benefits: [
      'Precedent analysis for design statements',
      'Policy compliance evidence',
      'Professional PDF exports'
    ]
  }
]

const outcomes = [
  {
    metric: '80%',
    label: 'Time Saved',
    description: 'Reduce precedent research from hours to minutes'
  },
  {
    metric: '45%',
    label: 'Higher Approval Rate',
    description: 'Design with confidence using local intelligence'
  },
  {
    metric: '95%',
    label: 'Prediction Accuracy',
    description: 'Know approval likelihood before submission'
  },
  {
    metric: '100%',
    label: 'UK Coverage',
    description: 'Every council, every precedent'
  }
]

const workflow = [
  {
    step: '1',
    title: 'Research Site',
    description: 'Understand site planning history and constraints instantly.',
    icon: Search
  },
  {
    step: '2',
    title: 'Find Precedents',
    description: 'AI identifies relevant approved designs in the area.',
    icon: Brain
  },
  {
    step: '3',
    title: 'Assess Viability',
    description: 'Review approval predictions and authority preferences.',
    icon: BarChart3
  },
  {
    step: '4',
    title: 'Strengthen Proposal',
    description: 'Use precedent analysis to support design statements.',
    icon: FileText
  }
]

const testimonial = {
  quote: "Planning Explorer has transformed how we approach planning applications. The precedent research that used to take hours now takes minutes, and the AI predictions help us design with confidence. We've seen our approval rate increase by 45% since adopting the platform.",
  author: "Emma Richardson",
  role: "Associate Director",
  company: "Studio Architecture",
  metrics: [
    { label: 'Approval Rate', value: '+45%' },
    { label: 'Research Time', value: '-80%' },
    { label: 'Win Rate', value: '+35%' }
  ]
}

const features = [
  {
    icon: Search,
    title: 'Design Precedents',
    description: 'Find approved designs similar to your proposals'
  },
  {
    icon: BarChart3,
    title: 'Authority Analysis',
    description: 'Understand council preferences and patterns'
  },
  {
    icon: TrendingUp,
    title: 'Approval Predictions',
    description: 'AI-powered success likelihood analysis'
  },
  {
    icon: FileText,
    title: 'Planning Reports',
    description: 'Generate precedent analysis for proposals'
  },
  {
    icon: Bell,
    title: 'Design Alerts',
    description: 'Get notified of relevant new approvals'
  },
  {
    icon: Database,
    title: 'Full Records',
    description: 'Access all planning documents and drawings'
  }
]

export default function ArchitectsPage() {
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
                <span className="text-sm font-semibold text-white">For Architects</span>
              </div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold mb-4 leading-tight" style={{ color: '#FFFFFF' }}>
                <span className="block">Design with Planning</span>
                <span className="block">Confidence and AI Insights</span>
              </h1>
              <p className="text-xl md:text-2xl mb-8 text-white/90">
                Stop guessing what will be approved. Use AI to research precedents instantly,
                understand local planning policies, and predict approval likelihood before you design.
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
              The Challenges Architects Face
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              Traditional planning research slows down your design process
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
              How Planning Explorer Empowers Architects
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              AI-powered intelligence for smarter, more successful designs
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
              Your Design Workflow, Enhanced
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              From initial research to planning submission with confidence
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
              Measurable Impact on Your Practice
            </h2>
            <p className="text-xl text-white/90 max-w-3xl mx-auto">
              Join architects designing with planning confidence
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
                  ER
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
              Essential Tools for Architects
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Everything you need for planning-led design
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
              Ready to Design with Planning Confidence?
            </h2>
            <p className="text-xl mb-8 text-white/90">
              Join architects creating more successful designs with AI-powered planning intelligence
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
