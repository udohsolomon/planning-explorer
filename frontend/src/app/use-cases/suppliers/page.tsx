'use client'

import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import { Footer } from '@/components/sections/Footer'
import {
  Truck, Target, TrendingUp, Clock, Brain, BarChart3,
  Bell, CheckCircle, FileText, Search, Database, Zap,
  Eye, Award, Building2, Users, Download, MapPin, Sparkles, Check
} from 'lucide-react'

const painPoints = [
  {
    icon: Search,
    title: 'Finding Projects Early',
    description: 'Missing opportunities because you hear about projects too late.'
  },
  {
    icon: Target,
    title: 'Identifying Prospects',
    description: 'Difficulty finding the right contacts and decision makers.'
  },
  {
    icon: Clock,
    title: 'Sales Cycle Length',
    description: 'Long, uncertain sales cycles with unclear project timelines.'
  },
  {
    icon: TrendingUp,
    title: 'Pipeline Visibility',
    description: 'Limited visibility into upcoming development projects.'
  }
]

const solutions = [
  {
    icon: Brain,
    title: 'Early Project Intelligence',
    description: 'Identify upcoming projects at planning application stage.',
    benefits: [
      'Know about projects months before construction',
      'Filter by project type and location',
      'AI identifies relevant opportunities automatically'
    ]
  },
  {
    icon: Database,
    title: 'Complete Project Details',
    description: 'Access full planning records including developer and architect details.',
    benefits: [
      'Developer and architect contact information',
      'Project specifications and timelines',
      'Planning documents and drawings'
    ]
  },
  {
    icon: Bell,
    title: 'Real-Time Project Alerts',
    description: 'Get notified immediately when relevant projects are submitted.',
    benefits: [
      'Custom alerts for your target sectors',
      'Email and mobile notifications',
      'First-mover advantage with prospects'
    ]
  },
  {
    icon: BarChart3,
    title: 'Market Intelligence',
    description: 'Understand development trends and identify growth areas.',
    benefits: [
      'Project volume by area and type',
      'Emerging development hotspots',
      'Developer activity tracking'
    ]
  },
  {
    icon: Target,
    title: 'Prospect Identification',
    description: 'Build targeted lists of developers and projects.',
    benefits: [
      'Active developer identification',
      'Project pipeline visibility',
      'Contact and company details'
    ]
  },
  {
    icon: FileText,
    title: 'Sales Intelligence Reports',
    description: 'Generate prospect lists and market analysis for your sales team.',
    benefits: [
      'Exportable prospect lists',
      'Project pipeline reports',
      'Market opportunity analysis'
    ]
  }
]

const outcomes = [
  {
    metric: '3x',
    label: 'More Opportunities',
    description: 'Identify projects months earlier'
  },
  {
    metric: '60%',
    label: 'Shorter Sales Cycle',
    description: 'Engage prospects at planning stage'
  },
  {
    metric: '90%',
    label: 'Time Saved',
    description: 'Automate prospect research'
  },
  {
    metric: '100%',
    label: 'UK Coverage',
    description: 'Every project, every area'
  }
]

const workflow = [
  {
    step: '1',
    title: 'Define Target Projects',
    description: 'Set up alerts for your target project types and locations.',
    icon: Target
  },
  {
    step: '2',
    title: 'Get Instant Alerts',
    description: 'Receive notifications as soon as relevant projects are submitted.',
    icon: Bell
  },
  {
    step: '3',
    title: 'Research Prospects',
    description: 'Access developer details, project specs, and timelines.',
    icon: Search
  },
  {
    step: '4',
    title: 'Engage Early',
    description: 'Contact prospects before your competition.',
    icon: Users
  }
]

const testimonial = {
  quote: "Planning Explorer has transformed our business development. We now know about relevant projects months before they go to tender, giving us time to build relationships with developers. Our pipeline has tripled and our win rate has increased by 45%.",
  author: "Robert Williams",
  role: "Business Development Director",
  company: "BuildTech Supplies",
  metrics: [
    { label: 'Pipeline', value: '3x' },
    { label: 'Win Rate', value: '+45%' },
    { label: 'Sales Cycle', value: '-60%' }
  ]
}

const features = [
  {
    icon: Search,
    title: 'Project Search',
    description: 'Find upcoming projects by type and location'
  },
  {
    icon: Bell,
    title: 'Project Alerts',
    description: 'Real-time notifications for new opportunities'
  },
  {
    icon: Users,
    title: 'Developer Intelligence',
    description: 'Track active developers and their projects'
  },
  {
    icon: MapPin,
    title: 'Geographic Targeting',
    description: 'Focus on your service areas'
  },
  {
    icon: BarChart3,
    title: 'Market Trends',
    description: 'Identify growth areas and opportunities'
  },
  {
    icon: Download,
    title: 'Prospect Lists',
    description: 'Export projects and contacts for CRM'
  }
]

const supplierTypes = [
  {
    title: 'Building Materials',
    description: 'Connect with developers at planning stage for early specification',
    icon: Building2
  },
  {
    title: 'Construction Equipment',
    description: 'Identify upcoming projects requiring your equipment and services',
    icon: Truck
  },
  {
    title: 'Professional Services',
    description: 'Find projects needing surveying, engineering, or specialist services',
    icon: Award
  },
  {
    title: 'Utilities & Infrastructure',
    description: 'Track major developments requiring utility connections and infrastructure',
    icon: Zap
  }
]

export default function SuppliersPage() {
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
                <span className="text-sm font-semibold text-white">For Construction & Development Suppliers</span>
              </div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold mb-4 leading-tight" style={{ color: '#FFFFFF' }}>
                <span className="block">Find Your Next Customers</span>
                <span className="block">Before Your Competition</span>
              </h1>
              <p className="text-xl md:text-2xl mb-8 text-white/90">
                Stop chasing projects too late. Use AI to identify upcoming developments at planning stage,
                build relationships early, and grow your business with a predictable pipeline.
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
              The Challenges Suppliers Face
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              Traditional lead generation leaves you one step behind
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
              How Planning Explorer Fills Your Pipeline
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              AI-powered business development for construction suppliers
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

      {/* Supplier Types */}
      <div className="py-20 bg-white">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-planning-primary mb-4">
              Built for Every Type of Supplier
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              Whether you supply materials, equipment, or services
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {supplierTypes.map((type, index) => {
              const Icon = type.icon
              const colors = ['bg-cyan-50', 'bg-green-50', 'bg-orange-50', 'bg-pink-50']
              return (
                <div key={index} className={`${colors[index % 4]} rounded-3xl p-8 hover:shadow-lg hover:scale-105 transition-all`}>
                  <div className="w-12 h-12 bg-white rounded-2xl flex items-center justify-center mb-4 shadow-sm">
                    <Icon className="w-6 h-6 text-planning-primary" />
                  </div>
                  <h3 className="text-2xl font-bold text-planning-primary mb-3">{type.title}</h3>
                  <p className="text-planning-text-light text-lg">{type.description}</p>
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
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Your Business Development Workflow, Automated
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              From lead generation to customer engagement in four steps
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
              Measurable Growth for Your Business
            </h2>
            <p className="text-xl text-white/90 max-w-3xl mx-auto">
              Join suppliers building predictable pipelines
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
                  RW
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
              Complete Business Development Intelligence
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Everything you need to find and win new customers
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
              Ready to Fill Your Pipeline?
            </h2>
            <p className="text-xl mb-8 text-white/90">
              Join suppliers finding more customers faster with AI-powered planning intelligence
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
