'use client'

import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import { Footer } from '@/components/sections/Footer'
import { PlanningStatsBar } from '@/components/sections/PlanningStatsBar'
import {
  Brain, Database, TrendingUp, Bell, BarChart3, FileText,
  Zap, Shield, Search, Target, Eye, Users, Download,
  CheckCircle, ArrowRight, Sparkles, MapPin, Clock,
  Award, Layers, Globe, Building2, Briefcase, Ruler, Truck, Check, Star
} from 'lucide-react'
import Link from 'next/link'

const services = [
  {
    category: 'Core Services',
    description: 'Essential planning intelligence tools for every user',
    items: [
      {
        icon: Brain,
        title: 'AI-Powered Semantic Search',
        description: 'Ask questions in natural language and get intelligent, context-aware results from 336,000+ UK planning applications.',
        features: [
          'Natural language queries',
          'Contextual relevance ranking',
          'Intent recognition',
          'Similar application suggestions'
        ],
        benefits: [
          'Find relevant applications 10x faster',
          'No need to learn complex search syntax',
          'Discover applications you might have missed'
        ]
      },
      {
        icon: Database,
        title: 'Comprehensive Planning Data',
        description: 'Access complete planning records from 321+ UK councils with real-time updates and 10+ years of historical data.',
        features: [
          'Complete UK coverage (England, Scotland, Wales)',
          'Daily automatic updates',
          '10+ years historical data',
          'All planning documents and drawings'
        ],
        benefits: [
          'One platform for all UK planning data',
          'Always up-to-date information',
          'Complete planning history for any site'
        ]
      },
      {
        icon: Search,
        title: 'Advanced Search & Filters',
        description: 'Find exactly what you need with 50+ filter options, geographic search, and powerful filtering tools.',
        features: [
          '50+ filter criteria',
          'Geographic radius search',
          'Date range filtering',
          'Application type and status filters'
        ],
        benefits: [
          'Pinpoint relevant applications quickly',
          'Save time with precise filtering',
          'Custom search combinations'
        ]
      }
    ]
  },
  {
    category: 'AI & Analytics Services',
    description: 'Advanced intelligence powered by machine learning',
    items: [
      {
        icon: TrendingUp,
        title: 'Predictive Analytics',
        description: 'AI-powered predictions for application outcomes, approval timelines, and planning success likelihood.',
        features: [
          '95% prediction accuracy',
          'Outcome probability scoring',
          'Timeline forecasting',
          'Risk assessment analysis'
        ],
        benefits: [
          'Make confident decisions with data',
          'Reduce planning risk',
          'Better project planning and timing'
        ]
      },
      {
        icon: Target,
        title: 'Opportunity Scoring',
        description: 'Automatically identify and score planning opportunities based on your custom criteria and preferences.',
        features: [
          'Personalized scoring algorithms',
          'Automatic deal prioritization',
          'Custom scoring criteria',
          'Comparative opportunity analysis'
        ],
        benefits: [
          'Focus on best opportunities first',
          'Never miss high-value deals',
          'Data-driven decision making'
        ]
      },
      {
        icon: BarChart3,
        title: 'Authority Intelligence',
        description: 'Deep insights into council performance, approval rates, decision patterns, and planning policy trends.',
        features: [
          'Approval rate analysis by type',
          'Decision timeline statistics',
          'Authority comparison tools',
          'Performance trend tracking'
        ],
        benefits: [
          'Understand council preferences',
          'Predict approval likelihood',
          'Strategic application planning'
        ]
      },
      {
        icon: Sparkles,
        title: 'Smart Recommendations',
        description: 'ML-powered suggestions for similar applications, comparable cases, and relevant precedents.',
        features: [
          'Similar case identification',
          'Precedent analysis',
          'Best practice suggestions',
          'Automated pattern recognition'
        ],
        benefits: [
          'Learn from similar cases',
          'Strengthen your applications',
          'Discover relevant precedents'
        ]
      }
    ]
  },
  {
    category: 'Monitoring & Alerts',
    description: 'Stay informed with intelligent notifications',
    items: [
      {
        icon: Bell,
        title: 'Smart Alerts & Notifications',
        description: 'Never miss opportunities with customizable, intelligent alerts for new applications and decisions.',
        features: [
          'Custom trigger criteria',
          'Email & SMS notifications',
          'Real-time alerts',
          'Frequency control'
        ],
        benefits: [
          'First to know about opportunities',
          'Stay ahead of competition',
          'Automated monitoring'
        ]
      },
      {
        icon: Layers,
        title: 'Saved Searches',
        description: 'Save your searches and get automatic updates when new matching applications appear.',
        features: [
          'Unlimited saved searches',
          'Automatic new match alerts',
          'Search sharing with team',
          'Quick access dashboard'
        ],
        benefits: [
          'Continuous automated monitoring',
          'Share searches with colleagues',
          'Build custom monitoring workflows'
        ]
      },
      {
        icon: Eye,
        title: 'Competitor Tracking',
        description: 'Monitor competitor activity, planning applications, and development strategies.',
        features: [
          'Track specific developers',
          'Activity notifications',
          'Strategy insights',
          'Competitive intelligence'
        ],
        benefits: [
          'Stay informed on competition',
          'Identify market trends',
          'Strategic advantage'
        ]
      }
    ]
  },
  {
    category: 'Reporting & Collaboration',
    description: 'Professional tools for teams and clients',
    items: [
      {
        icon: FileText,
        title: 'Professional Reports',
        description: 'Generate comprehensive, bank-grade reports with planning analysis, precedents, and recommendations.',
        features: [
          'White-label options',
          'Custom branding',
          'PDF export',
          'Comprehensive analysis'
        ],
        benefits: [
          'Impress clients with professional reports',
          'Save hours on report writing',
          'Evidence-based recommendations'
        ]
      },
      {
        icon: Users,
        title: 'Team Collaboration',
        description: 'Work together with multi-user access, role-based permissions, and shared workspaces.',
        features: [
          'Multi-user access',
          'Role-based permissions',
          'Shared workspaces',
          'Activity tracking'
        ],
        benefits: [
          'Centralized team knowledge',
          'Controlled access levels',
          'Improved team efficiency'
        ]
      },
      {
        icon: Download,
        title: 'Data Export',
        description: 'Export planning data in multiple formats for further analysis and integration.',
        features: [
          'CSV export',
          'Excel compatible',
          'PDF reports',
          'API access'
        ],
        benefits: [
          'Integrate with existing workflows',
          'Custom analysis in Excel',
          'Flexible data usage'
        ]
      }
    ]
  },
  {
    category: 'Enterprise Services',
    description: 'Advanced features for organizations',
    items: [
      {
        icon: Zap,
        title: 'API Access',
        description: 'Integrate planning data into your own systems and workflows with our REST API and webhooks.',
        features: [
          'REST API',
          'Webhooks',
          'Custom integrations',
          'Developer documentation'
        ],
        benefits: [
          'Build custom applications',
          'Automate workflows',
          'Seamless system integration'
        ]
      },
      {
        icon: Shield,
        title: 'Enterprise Security',
        description: 'Bank-level security with AES-256 encryption, SOC 2 certification, and comprehensive audit logs.',
        features: [
          'AES-256 encryption',
          'SOC 2 certified',
          'Two-factor authentication',
          'Comprehensive audit logs'
        ],
        benefits: [
          'Protect sensitive data',
          'Compliance ready',
          'Complete security transparency'
        ]
      },
      {
        icon: Clock,
        title: 'Dedicated Support',
        description: 'Priority support with dedicated account management for Enterprise customers.',
        features: [
          'Email support (all plans)',
          'Phone support (Enterprise)',
          'Knowledge base',
          'Video tutorials'
        ],
        benefits: [
          'Expert help when you need it',
          'Faster issue resolution',
          'Ongoing training and guidance'
        ]
      }
    ]
  }
]

const industries = [
  {
    title: 'Property Developers',
    icon: Building2,
    description: 'Find development opportunities faster',
    link: '/use-cases/developers'
  },
  {
    title: 'Planning Consultants',
    icon: Briefcase,
    description: 'Provide better advice in less time',
    link: '/use-cases/consultants'
  },
  {
    title: 'Land Agents',
    icon: MapPin,
    description: 'Discover land opportunities early',
    link: '/use-cases/land-agents'
  },
  {
    title: 'Architects',
    icon: Ruler,
    description: 'Design with planning confidence',
    link: '/use-cases/architects'
  },
  {
    title: 'Investors',
    icon: TrendingUp,
    description: 'Invest with planning intelligence',
    link: '/use-cases/investors'
  },
  {
    title: 'Suppliers',
    icon: Truck,
    description: 'Find projects before competition',
    link: '/use-cases/suppliers'
  }
]

export default function ServicesPage() {
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
                <span className="text-sm font-semibold text-white">Comprehensive Services</span>
              </div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold mb-4 leading-tight" style={{ color: '#FFFFFF' }}>
                <span className="block">Comprehensive Planning</span>
                <span className="block">Intelligence Services</span>
              </h1>
              <p className="text-xl md:text-2xl mb-8 text-white/90">
                AI-powered tools and insights that transform how property professionals
                research, analyze, and act on UK planning data.
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

      {/* Real-Time Stats Bar from Elasticsearch */}
      <PlanningStatsBar />

      {/* Services Sections */}
      {services.map((section, sectionIndex) => {
        const sectionColors = [
          ['bg-cyan-50', 'bg-green-50', 'bg-orange-50'],
          ['bg-pink-50', 'bg-yellow-50', 'bg-cyan-50', 'bg-green-50'],
          ['bg-orange-50', 'bg-pink-50', 'bg-yellow-50'],
          ['bg-cyan-50', 'bg-green-50', 'bg-orange-50'],
          ['bg-pink-50', 'bg-yellow-50', 'bg-cyan-50']
        ]
        return (
          <div key={sectionIndex} className={`py-20 ${sectionIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
            <Container>
              <div className="text-center mb-16">
                <h2 className="text-4xl font-bold text-planning-primary mb-4">{section.category}</h2>
                <p className="text-xl text-planning-text-light max-w-3xl mx-auto">{section.description}</p>
              </div>

              <div className="grid md:grid-cols-1 gap-12">
                {section.items.map((service, serviceIndex) => {
                  const Icon = service.icon
                  const bgColor = sectionColors[sectionIndex % sectionColors.length][serviceIndex % sectionColors[sectionIndex % sectionColors.length].length]
                  return (
                    <div key={serviceIndex} className={`${bgColor} rounded-3xl p-8 hover:shadow-lg hover:scale-105 transition-all`}>
                      <div className="flex items-start gap-6 mb-6">
                        <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center flex-shrink-0 shadow-sm">
                          <Icon className="w-8 h-8 text-planning-primary" />
                        </div>
                        <div className="flex-1">
                          <h3 className="text-2xl font-bold text-planning-primary mb-3">{service.title}</h3>
                          <p className="text-lg text-planning-text-light mb-6">{service.description}</p>

                          <div className="grid md:grid-cols-2 gap-8">
                            {/* Features */}
                            <div>
                              <h4 className="font-semibold text-planning-primary mb-3 flex items-center">
                                <CheckCircle className="w-5 h-5 text-planning-primary mr-2" />
                                Key Features
                              </h4>
                              <ul className="space-y-2">
                                {service.features.map((feature, idx) => (
                                  <li key={idx} className="flex items-start text-sm text-planning-text-light">
                                    <Check className="w-4 h-4 text-planning-bright mr-3 flex-shrink-0 mt-0.5" />
                                    {feature}
                                  </li>
                                ))}
                              </ul>
                            </div>

                            {/* Benefits */}
                            <div>
                              <h4 className="font-semibold text-planning-primary mb-3 flex items-center">
                                <Award className="w-5 h-5 text-planning-bright mr-2" />
                                Benefits
                              </h4>
                              <ul className="space-y-2">
                                {service.benefits.map((benefit, idx) => (
                                  <li key={idx} className="flex items-start text-sm text-planning-text-light">
                                    <Check className="w-4 h-4 text-planning-bright mr-3 flex-shrink-0 mt-0.5" />
                                    {benefit}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </Container>
          </div>
        )
      })}

      {/* Industries Section */}
      <div className="py-20 bg-gradient-to-b from-gray-50 to-white">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-planning-primary mb-4">
              Tailored Solutions for Every Industry
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              See how Planning Explorer serves different property professionals
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {industries.map((industry, index) => {
              const Icon = industry.icon
              return (
                <Link
                  key={index}
                  href={industry.link}
                  className="bg-white rounded-3xl p-6 border border-gray-200 hover:border-planning-primary hover:shadow-lg hover:scale-105 transition-all group"
                >
                  <Icon className="w-10 h-10 text-planning-primary mb-4" />
                  <h3 className="text-xl font-bold text-planning-primary mb-3 group-hover:text-planning-accent transition-colors">
                    {industry.title}
                  </h3>
                  <p className="text-planning-text-light mb-4">{industry.description}</p>
                  <div className="flex items-center text-planning-primary font-medium group-hover:translate-x-2 transition-transform">
                    Learn more <ArrowRight className="w-4 h-4 ml-2" />
                  </div>
                </Link>
              )
            })}
          </div>
        </Container>
      </div>

      {/* Pricing Preview */}
      <div className="py-24 bg-white">
        <Container>
          <div className="text-center mb-16">
            <div className="inline-block px-4 py-2 bg-planning-button/10 rounded-full mb-6">
              <span className="text-planning-primary font-medium text-sm uppercase tracking-wider">
                Pricing Plans
              </span>
            </div>
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-planning-primary mb-6">
              Choose Your Plan
            </h2>
            <p className="text-lg text-planning-text-light max-w-3xl mx-auto leading-relaxed">
              Flexible pricing options to suit businesses of all sizes. Start with a free trial and scale as you grow.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {/* Starter Plan */}
            <div className="relative rounded-2xl border-2 border-planning-border bg-white p-8 transition-all duration-300 flex flex-col hover:border-planning-primary/30 hover:shadow-lg">
              <div className="text-center mb-8">
                <h3 className="text-xl font-semibold text-planning-primary mb-2">Starter</h3>
                <div className="mb-4">
                  <span className="text-4xl font-bold text-planning-primary">£99</span>
                  <span className="text-sm ml-2 text-planning-text-light">per month</span>
                </div>
                <p className="text-sm leading-relaxed text-planning-text-light">
                  Perfect for individuals and small teams getting started with planning intelligence.
                </p>
              </div>
              <ul className="space-y-4 mb-8 flex-grow">
                <li className="flex items-start">
                  <Check className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0 text-planning-bright" />
                  <span className="text-sm text-planning-text-light">10,000 search queries/month</span>
                </li>
                <li className="flex items-start">
                  <Check className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0 text-planning-bright" />
                  <span className="text-sm text-planning-text-light">Basic AI analytics</span>
                </li>
                <li className="flex items-start">
                  <Check className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0 text-planning-bright" />
                  <span className="text-sm text-planning-text-light">Standard reports</span>
                </li>
                <li className="flex items-start">
                  <Check className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0 text-planning-bright" />
                  <span className="text-sm text-planning-text-light">Email support</span>
                </li>
              </ul>
              <Button variant="outline" className="w-full">Start Free Trial</Button>
            </div>

            {/* Professional Plan - Popular */}
            <div className="relative rounded-2xl border-2 border-planning-primary bg-planning-primary text-white p-8 transition-all duration-300 flex flex-col scale-105 shadow-xl">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <div className="bg-planning-button text-white px-4 py-2 rounded-full text-sm font-semibold flex items-center space-x-1">
                  <Star className="w-4 h-4" />
                  <span>Most Popular</span>
                </div>
              </div>
              <div className="text-center mb-8">
                <h3 className="text-xl font-semibold text-white mb-2">Professional</h3>
                <div className="mb-4">
                  <span className="text-4xl font-bold text-white">£299</span>
                  <span className="text-sm ml-2 text-white/80">per month</span>
                </div>
                <p className="text-sm leading-relaxed text-white/90">
                  Advanced features for growing teams and established businesses.
                </p>
              </div>
              <ul className="space-y-4 mb-8 flex-grow">
                <li className="flex items-start">
                  <Check className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0 text-planning-button" />
                  <span className="text-sm text-white">50,000 search queries/month</span>
                </li>
                <li className="flex items-start">
                  <Check className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0 text-planning-button" />
                  <span className="text-sm text-white">Advanced AI analytics</span>
                </li>
                <li className="flex items-start">
                  <Check className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0 text-planning-button" />
                  <span className="text-sm text-white">Custom reports & dashboards</span>
                </li>
                <li className="flex items-start">
                  <Check className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0 text-planning-button" />
                  <span className="text-sm text-white">Priority support</span>
                </li>
              </ul>
              <Button className="w-full bg-white text-planning-primary hover:bg-gray-100">Start Free Trial</Button>
            </div>

            {/* Enterprise Plan */}
            <div className="relative rounded-2xl border-2 border-planning-border bg-white p-8 transition-all duration-300 flex flex-col hover:border-planning-primary/30 hover:shadow-lg">
              <div className="text-center mb-8">
                <h3 className="text-xl font-semibold text-planning-primary mb-2">Enterprise</h3>
                <div className="mb-4">
                  <span className="text-4xl font-bold text-planning-primary">Custom</span>
                  <span className="text-sm ml-2 text-planning-text-light">contact us</span>
                </div>
                <p className="text-sm leading-relaxed text-planning-text-light">
                  Tailored solutions for large organizations with specific requirements.
                </p>
              </div>
              <ul className="space-y-4 mb-8 flex-grow">
                <li className="flex items-start">
                  <Check className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0 text-planning-bright" />
                  <span className="text-sm text-planning-text-light">Unlimited search queries</span>
                </li>
                <li className="flex items-start">
                  <Check className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0 text-planning-bright" />
                  <span className="text-sm text-planning-text-light">Custom AI model training</span>
                </li>
                <li className="flex items-start">
                  <Check className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0 text-planning-bright" />
                  <span className="text-sm text-planning-text-light">White-label solutions</span>
                </li>
                <li className="flex items-start">
                  <Check className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0 text-planning-bright" />
                  <span className="text-sm text-planning-text-light">Dedicated account manager</span>
                </li>
              </ul>
              <Button variant="outline" className="w-full">Contact Sales</Button>
            </div>
          </div>
        </Container>
      </div>

      {/* CTA Section */}
      <div className="py-20 bg-planning-primary text-white">
        <Container>
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-4xl font-bold mb-6">
              Ready to Transform Your Planning Intelligence?
            </h2>
            <p className="text-xl mb-8 text-white/90">
              Join thousands of property professionals making faster, smarter decisions
              with AI-powered planning insights
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
