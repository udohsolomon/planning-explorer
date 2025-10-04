'use client'

import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import {
  Brain, Search, Bell, BarChart3, FileText, MapPin,
  Zap, Shield, Clock, Database, Target, TrendingUp,
  Filter, Eye, Download, Share2, Check, ArrowRight,
  Sparkles, Globe, Layers, Lock, RefreshCw, Users,
  ChartBar, Calendar, AlertCircle, MessageSquare, Star
} from 'lucide-react'
import Link from 'next/link'
import { Footer } from '@/components/sections/Footer'
import { cn } from '@/lib/utils'

const featureCategories = [
  {
    category: 'AI-Powered Intelligence',
    icon: Brain,
    bgColor: 'bg-cyan-50',
    features: [
      {
        title: 'Semantic Search',
        description: 'Ask questions in natural language and get intelligent, context-aware results.',
        icon: Search,
        iconBg: 'bg-blue-100',
        iconColor: 'text-blue-600',
        details: [
          'Understands meaning, not just keywords',
          'Contextual relevance ranking',
          'Natural language queries',
          'Intent recognition'
        ]
      },
      {
        title: 'Predictive Analytics',
        description: 'AI-powered predictions for application outcomes and approval timelines.',
        icon: TrendingUp,
        iconBg: 'bg-orange-100',
        iconColor: 'text-orange-600',
        details: [
          '95% prediction accuracy',
          'Outcome probability scoring',
          'Timeline forecasting',
          'Risk assessment'
        ]
      },
      {
        title: 'Opportunity Scoring',
        description: 'Automatically identify and score opportunities based on your criteria.',
        icon: Target,
        iconBg: 'bg-green-100',
        iconColor: 'text-green-600',
        details: [
          'Personalized scoring algorithms',
          'Automatic deal prioritization',
          'Custom scoring criteria',
          'Comparative analysis'
        ]
      },
      {
        title: 'Smart Recommendations',
        description: 'Get intelligent suggestions for similar applications and comparable cases.',
        icon: Sparkles,
        iconBg: 'bg-pink-100',
        iconColor: 'text-pink-600',
        details: [
          'ML-powered recommendations',
          'Similar case identification',
          'Precedent analysis',
          'Best practice suggestions'
        ]
      }
    ]
  },
  {
    category: 'Comprehensive Data',
    icon: Database,
    bgColor: 'bg-green-50',
    features: [
      {
        title: 'Complete UK Coverage',
        description: 'Access 336,000+ planning applications from every UK council.',
        icon: Globe,
        iconBg: 'bg-green-100',
        iconColor: 'text-green-600',
        details: [
          '321+ councils covered',
          'England, Scotland, Wales',
          'Real-time updates',
          '10+ years historical data'
        ]
      },
      {
        title: 'Advanced Search & Filters',
        description: 'Find exactly what you need with powerful search and filtering tools.',
        icon: Filter,
        iconBg: 'bg-yellow-100',
        iconColor: 'text-yellow-600',
        details: [
          '50+ filter options',
          'Geographic search',
          'Date range filtering',
          'Status and type filters'
        ]
      },
      {
        title: 'Real-Time Updates',
        description: 'Get the latest planning data with daily automatic updates.',
        icon: RefreshCw,
        iconBg: 'bg-orange-100',
        iconColor: 'text-orange-600',
        details: [
          'Daily data synchronization',
          'Instant decision updates',
          'New application alerts',
          'Status change tracking'
        ]
      },
      {
        title: 'Document Access',
        description: 'Direct links to all planning documents and supporting materials.',
        icon: FileText,
        iconBg: 'bg-cyan-100',
        iconColor: 'text-cyan-600',
        details: [
          'Planning statements',
          'Design documents',
          'Decision notices',
          'Consultation responses'
        ]
      }
    ]
  },
  {
    category: 'Monitoring & Alerts',
    icon: Bell,
    bgColor: 'bg-yellow-50',
    features: [
      {
        title: 'Smart Alerts',
        description: 'Never miss opportunities with intelligent, customizable alerts.',
        icon: Bell,
        iconBg: 'bg-yellow-100',
        iconColor: 'text-yellow-600',
        details: [
          'Custom trigger criteria',
          'Email & SMS notifications',
          'Real-time alerts',
          'Frequency control'
        ]
      },
      {
        title: 'Saved Searches',
        description: 'Save your searches and get automatic updates when new matches appear.',
        icon: Layers,
        iconBg: 'bg-blue-100',
        iconColor: 'text-blue-600',
        details: [
          'Unlimited saved searches',
          'Automatic new match alerts',
          'Search sharing',
          'Quick access dashboard'
        ]
      },
      {
        title: 'Competitor Tracking',
        description: 'Monitor competitor activity and planning applications.',
        icon: Eye,
        iconBg: 'bg-pink-100',
        iconColor: 'text-pink-600',
        details: [
          'Track specific developers',
          'Activity notifications',
          'Strategy insights',
          'Competitive intelligence'
        ]
      },
      {
        title: 'Portfolio Management',
        description: 'Track and manage your planning applications and interests.',
        icon: Layers,
        iconBg: 'bg-green-100',
        iconColor: 'text-green-600',
        details: [
          'Application tracking',
          'Status monitoring',
          'Milestone alerts',
          'Team collaboration'
        ]
      }
    ]
  },
  {
    category: 'Analytics & Insights',
    icon: BarChart3,
    bgColor: 'bg-pink-50',
    features: [
      {
        title: 'Interactive Dashboards',
        description: 'Visualize planning trends and authority performance.',
        icon: ChartBar,
        iconBg: 'bg-pink-100',
        iconColor: 'text-pink-600',
        details: [
          'Customizable dashboards',
          'Interactive charts',
          'Trend analysis',
          'Performance metrics'
        ]
      },
      {
        title: 'Authority Intelligence',
        description: 'Understand council performance, approval rates, and decision patterns.',
        icon: Target,
        iconBg: 'bg-orange-100',
        iconColor: 'text-orange-600',
        details: [
          'Approval rate analysis',
          'Decision timeline stats',
          'Authority comparison',
          'Performance trends'
        ]
      },
      {
        title: 'Market Analysis',
        description: 'Gain insights into planning market trends and patterns.',
        icon: TrendingUp,
        iconBg: 'bg-green-100',
        iconColor: 'text-green-600',
        details: [
          'Geographic heat maps',
          'Application volume trends',
          'Approval patterns',
          'Market opportunities'
        ]
      },
      {
        title: 'Custom Reports',
        description: 'Generate professional reports with comprehensive analysis.',
        icon: FileText,
        iconBg: 'bg-blue-100',
        iconColor: 'text-blue-600',
        details: [
          'Bank-grade reports',
          'White-label options',
          'PDF export',
          'Custom branding'
        ]
      }
    ]
  },
  {
    category: 'Collaboration & Workflow',
    icon: Users,
    bgColor: 'bg-orange-50',
    features: [
      {
        title: 'Team Access',
        description: 'Collaborate with your team on planning research and analysis.',
        icon: Users,
        iconBg: 'bg-orange-100',
        iconColor: 'text-orange-600',
        details: [
          'Multi-user access',
          'Role-based permissions',
          'Shared workspaces',
          'Activity tracking'
        ]
      },
      {
        title: 'Notes & Annotations',
        description: 'Add notes, tags, and comments to applications.',
        icon: MessageSquare,
        iconBg: 'bg-cyan-100',
        iconColor: 'text-cyan-600',
        details: [
          'Application notes',
          'Team comments',
          'Custom tags',
          'File attachments'
        ]
      },
      {
        title: 'Data Export',
        description: 'Export data in multiple formats for further analysis.',
        icon: Download,
        iconBg: 'bg-green-100',
        iconColor: 'text-green-600',
        details: [
          'CSV export',
          'Excel compatible',
          'PDF reports',
          'API access'
        ]
      },
      {
        title: 'Sharing & Collaboration',
        description: 'Share findings and reports with clients and colleagues.',
        icon: Share2,
        iconBg: 'bg-pink-100',
        iconColor: 'text-pink-600',
        details: [
          'Secure sharing links',
          'Permission control',
          'Client portals',
          'Report distribution'
        ]
      }
    ]
  },
  {
    category: 'Security & Compliance',
    icon: Shield,
    bgColor: 'bg-cyan-50',
    features: [
      {
        title: 'Enterprise Security',
        description: 'Bank-level security with encryption and access controls.',
        icon: Lock,
        iconBg: 'bg-blue-100',
        iconColor: 'text-blue-600',
        details: [
          'AES-256 encryption',
          'SOC 2 certified',
          'Two-factor authentication',
          'Audit logs'
        ]
      },
      {
        title: 'GDPR Compliance',
        description: 'Fully compliant with UK and EU data protection regulations.',
        icon: Shield,
        iconBg: 'bg-green-100',
        iconColor: 'text-green-600',
        details: [
          'GDPR compliant',
          'Data processing agreements',
          'Privacy controls',
          'Right to be forgotten'
        ]
      },
      {
        title: 'API Access',
        description: 'Integrate planning data into your own systems and workflows.',
        icon: Zap,
        iconBg: 'bg-yellow-100',
        iconColor: 'text-yellow-600',
        details: [
          'REST API',
          'Webhooks',
          'Custom integrations',
          'Developer documentation'
        ]
      },
      {
        title: '24/7 Support',
        description: 'Expert support whenever you need it.',
        icon: Clock,
        iconBg: 'bg-pink-100',
        iconColor: 'text-pink-600',
        details: [
          'Email support',
          'Phone support (Enterprise)',
          'Knowledge base',
          'Video tutorials'
        ]
      }
    ]
  }
]

const comparisonFeatures = [
  { feature: 'AI-Powered Search', starter: true, professional: true, enterprise: true },
  { feature: 'Planning Application Data', starter: '50/month', professional: 'Unlimited', enterprise: 'Unlimited' },
  { feature: 'Real-Time Alerts', starter: false, professional: true, enterprise: true },
  { feature: 'Advanced Analytics', starter: false, professional: true, enterprise: true },
  { feature: 'Custom Reports', starter: false, professional: true, enterprise: true },
  { feature: 'API Access', starter: false, professional: true, enterprise: true },
  { feature: 'Team Collaboration', starter: false, professional: false, enterprise: true },
  { feature: 'White-Label Reports', starter: false, professional: false, enterprise: true },
  { feature: 'Dedicated Support', starter: false, professional: false, enterprise: true },
  { feature: 'Custom Integrations', starter: false, professional: false, enterprise: true }
]

export default function FeaturesPage() {
  return (
    <>
      <div className="min-h-screen bg-white">
        {/* Hero Section - Matching Homepage Style */}
        <section className="relative z-20 bg-gradient-to-br from-planning-primary via-planning-primary to-planning-accent overflow-hidden">
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
          </div>

          {/* Main Content */}
          <div className="relative z-10 py-20">
            <Container>
              <div className="text-center max-w-4xl mx-auto">
                {/* Badge */}
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full border border-white/20 mb-6">
                  <Sparkles className="w-4 h-4 text-planning-bright" />
                  <span className="text-sm font-semibold text-white">AI-Powered Planning Intelligence</span>
                </div>

                {/* Main Title */}
                <h1 className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold mb-4 leading-tight" style={{ color: '#FFFFFF' }}>
                  <span className="block">Powerful Features for</span>
                  <span className="block">Planning Intelligence</span>
                </h1>

                {/* Description */}
                <p className="text-lg md:text-xl text-white/90 mb-8 leading-relaxed">
                  Everything you need to make faster, smarter planning decisions with AI-powered insights and comprehensive UK planning data coverage.
                </p>

                {/* CTA Buttons */}
                <div className="flex flex-col sm:flex-row justify-center gap-4">
                  <Button
                    size="lg"
                    className="bg-planning-button hover:bg-planning-button/90 text-white font-semibold"
                  >
                    Start 14-Day Free Trial
                  </Button>
                  <Button
                    size="lg"
                    className="bg-white/10 backdrop-blur-sm text-white hover:bg-white/20 border border-white/20"
                  >
                    Book a Demo
                  </Button>
                </div>

                <p className="mt-6 text-sm text-white/70">
                  No credit card required • Cancel anytime • Full access during trial
                </p>
              </div>
            </Container>
          </div>
        </section>

        {/* Feature Categories - Using Colorful Cards Pattern */}
        {featureCategories.map((category, categoryIndex) => {
          const CategoryIcon = category.icon
          return (
            <section key={categoryIndex} className="py-24 bg-white">
              <Container>
                <div className="text-center mb-16">
                  <div className="inline-flex items-center gap-3 mb-6">
                    <div className="w-12 h-12 bg-planning-primary rounded-xl flex items-center justify-center">
                      <CategoryIcon className="w-6 h-6 text-white" />
                    </div>
                    <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-planning-primary">{category.category}</h2>
                  </div>
                  <p className="text-lg text-planning-text-light max-w-3xl mx-auto leading-relaxed">
                    Comprehensive capabilities designed for planning professionals
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  {category.features.map((feature, featureIndex) => {
                    const FeatureIcon = feature.icon
                    return (
                      <div key={featureIndex} className={`${category.bgColor} rounded-3xl p-8 transition-all duration-300 hover:shadow-lg hover:scale-105`}>
                        <div className="flex items-start gap-4 mb-4">
                          <div className={`w-12 h-12 ${feature.iconBg} rounded-xl flex items-center justify-center flex-shrink-0`}>
                            <FeatureIcon className={`w-6 h-6 ${feature.iconColor}`} />
                          </div>
                          <div>
                            <h3 className="text-xl font-bold text-planning-primary mb-2 leading-tight">{feature.title}</h3>
                            <p className="text-planning-text-light leading-relaxed">{feature.description}</p>
                          </div>
                        </div>
                        <ul className="space-y-2 ml-16">
                          {feature.details.map((detail, detailIndex) => (
                            <li key={detailIndex} className="flex items-start text-sm text-planning-text-light">
                              <Check className="w-4 h-4 text-planning-bright mr-3 flex-shrink-0 mt-0.5" />
                              {detail}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )
                  })}
                </div>
              </Container>
            </section>
          )
        })}

        {/* Feature Comparison */}
        <section className="py-24 bg-white border-t border-gray-200">
          <Container>
            <div className="text-center mb-16">
              <div className="inline-block px-4 py-2 bg-planning-button/10 rounded-full mb-6">
                <span className="text-planning-primary font-medium text-sm uppercase tracking-wider">
                  Pricing Plans
                </span>
              </div>
              <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-planning-primary mb-6">
                Compare Plans & Features
              </h2>
              <p className="text-lg text-planning-text-light max-w-3xl mx-auto leading-relaxed">
                Choose the plan that's right for you
              </p>
            </div>

            <div className="max-w-5xl mx-auto overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="border-b-2 border-gray-200">
                    <th className="text-left py-4 px-6 font-semibold text-planning-primary">Feature</th>
                    <th className="text-center py-4 px-6 font-semibold text-planning-primary">Starter</th>
                    <th className="text-center py-4 px-6 font-semibold text-planning-primary bg-planning-primary/5">Professional</th>
                    <th className="text-center py-4 px-6 font-semibold text-planning-primary">Enterprise</th>
                  </tr>
                </thead>
                <tbody>
                  {comparisonFeatures.map((row, index) => (
                    <tr key={index} className="border-b border-gray-100">
                      <td className="py-4 px-6 text-planning-text-light">{row.feature}</td>
                      <td className="py-4 px-6 text-center">
                        {typeof row.starter === 'boolean' ? (
                          row.starter ? (
                            <Check className="w-5 h-5 text-planning-bright mx-auto" />
                          ) : (
                            <span className="text-gray-300">—</span>
                          )
                        ) : (
                          <span className="text-sm text-planning-text-light">{row.starter}</span>
                        )}
                      </td>
                      <td className="py-4 px-6 text-center bg-planning-primary/5">
                        {typeof row.professional === 'boolean' ? (
                          row.professional ? (
                            <Check className="w-5 h-5 text-planning-bright mx-auto" />
                          ) : (
                            <span className="text-gray-300">—</span>
                          )
                        ) : (
                          <span className="text-sm text-planning-text-light font-medium">{row.professional}</span>
                        )}
                      </td>
                      <td className="py-4 px-6 text-center">
                        {typeof row.enterprise === 'boolean' ? (
                          row.enterprise ? (
                            <Check className="w-5 h-5 text-planning-bright mx-auto" />
                          ) : (
                            <span className="text-gray-300">—</span>
                          )
                        ) : (
                          <span className="text-sm text-planning-text-light">{row.enterprise}</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="text-center mt-12">
              <Link href="/pricing">
                <Button size="lg" className="bg-planning-primary text-white hover:bg-planning-accent">
                  View Full Pricing & Features
                </Button>
              </Link>
            </div>
          </Container>
        </section>
      </div>

      {/* Footer with CTA */}
      <Footer />
    </>
  )
}
