'use client'

import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import {
  Brain, MapPin, TrendingUp, Bell, FileText, BarChart3,
  Zap, Shield, Clock, Users, Check, Star, Download, Search, Filter, Eye, Target,
  Sparkles, Database, ChartBar, Globe, Building2,
  Briefcase, Ruler, Truck, ArrowRight
} from 'lucide-react'
import Link from 'next/link'
import { useState } from 'react'
import { Footer } from '@/components/sections/Footer'
import { PlanningStatsBar } from '@/components/sections/PlanningStatsBar'
import { cn } from '@/lib/utils'

const pricingPlans = [
  {
    name: 'Starter',
    price: '£99',
    period: 'per month',
    description: 'Perfect for individuals and small teams getting started with planning intelligence.',
    features: [
      '10,000 search queries/month',
      'Basic AI analytics',
      'Standard reports',
      'Email support',
      'API access (limited)',
      'Data export (CSV)'
    ],
    popular: false,
    cta: 'Start Free Trial'
  },
  {
    name: 'Professional',
    price: '£299',
    period: 'per month',
    description: 'Advanced features for growing teams and established businesses.',
    features: [
      '50,000 search queries/month',
      'Advanced AI analytics',
      'Custom reports & dashboards',
      'Priority support',
      'Full API access',
      'Advanced data exports',
      'Geographic analysis tools',
      'Trend forecasting'
    ],
    popular: true,
    cta: 'Start Free Trial'
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: 'contact us',
    description: 'Tailored solutions for large organizations with specific requirements.',
    features: [
      'Unlimited search queries',
      'Custom AI model training',
      'White-label solutions',
      'Dedicated account manager',
      'Custom integrations',
      'Advanced security features',
      'On-premise deployment',
      'SLA guarantees'
    ],
    popular: false,
    cta: 'Contact Sales'
  }
]

const features = [
  {
    icon: Brain,
    title: 'AI-Powered Search',
    description: 'Transform weeks of research into minutes with intelligent semantic search.',
    benefits: ['Natural language queries', 'Contextual understanding', '95% accuracy rate'],
    bgColor: 'bg-cyan-50',
    iconBg: 'bg-blue-100',
    iconColor: 'text-blue-600'
  },
  {
    icon: Database,
    title: 'Comprehensive Database',
    description: 'Access 336,000+ planning applications from 321+ UK councils.',
    benefits: ['Daily updates', '10+ years of history', 'Complete coverage'],
    bgColor: 'bg-green-50',
    iconBg: 'bg-green-100',
    iconColor: 'text-green-600'
  },
  {
    icon: TrendingUp,
    title: 'Predictive Analytics',
    description: 'AI-powered predictions for application outcomes and timelines.',
    benefits: ['Outcome predictions', 'Timeline forecasts', 'Risk assessments'],
    bgColor: 'bg-orange-50',
    iconBg: 'bg-orange-100',
    iconColor: 'text-orange-600'
  },
  {
    icon: Bell,
    title: 'Smart Alerts',
    description: 'Never miss opportunities with intelligent, customizable alerts.',
    benefits: ['Real-time notifications', 'Custom triggers', 'Email & mobile alerts'],
    bgColor: 'bg-yellow-50',
    iconBg: 'bg-yellow-100',
    iconColor: 'text-yellow-600'
  },
  {
    icon: BarChart3,
    title: 'Advanced Analytics',
    description: 'Gain deep insights into planning trends and authority performance.',
    benefits: ['Interactive dashboards', 'Custom reports', 'Trend analysis'],
    bgColor: 'bg-pink-50',
    iconBg: 'bg-pink-100',
    iconColor: 'text-pink-600'
  },
  {
    icon: FileText,
    title: 'Professional Reports',
    description: 'Generate bank-grade reports with comprehensive analysis.',
    benefits: ['PDF exports', 'White-label options', 'Custom branding'],
    bgColor: 'bg-cyan-50',
    iconBg: 'bg-cyan-100',
    iconColor: 'text-cyan-600'
  },
  {
    icon: Target,
    title: 'Opportunity Scoring',
    description: 'AI automatically identifies and scores opportunities.',
    benefits: ['Automated scoring', 'Personalized rankings', 'Deal prioritization'],
    bgColor: 'bg-green-50',
    iconBg: 'bg-green-100',
    iconColor: 'text-green-600'
  },
  {
    icon: Shield,
    title: 'Compliance & Security',
    description: 'Enterprise-grade security with GDPR compliance.',
    benefits: ['Bank-level encryption', 'GDPR compliant', 'SOC 2 certified'],
    bgColor: 'bg-orange-50',
    iconBg: 'bg-orange-100',
    iconColor: 'text-orange-600'
  }
]

const useCases = [
  {
    title: 'Property Developers',
    description: 'Find development opportunities, assess feasibility, and track competitor activity.',
    icon: Building2,
    link: '/use-cases/developers'
  },
  {
    title: 'Planning Consultants',
    description: 'Access comprehensive data to provide better advice and win more clients.',
    icon: Briefcase,
    link: '/use-cases/consultants'
  },
  {
    title: 'Land Agents',
    description: 'Discover land opportunities, analyze market trends, and value properties accurately.',
    icon: MapPin,
    link: '/use-cases/land-agents'
  },
  {
    title: 'Architects',
    description: 'Research planning precedents, understand local policies, and strengthen proposals.',
    icon: Ruler,
    link: '/use-cases/architects'
  },
  {
    title: 'Investors',
    description: 'Identify investment opportunities, assess risk, and track market performance.',
    icon: TrendingUp,
    link: '/use-cases/investors'
  },
  {
    title: 'Suppliers',
    description: 'Find upcoming projects, identify prospects, and grow your business.',
    icon: Truck,
    link: '/use-cases/suppliers'
  }
]

const testimonials = [
  {
    quote: "Planning Explorer has transformed how we identify development opportunities. The AI insights save us weeks of research.",
    author: "James Mitchell",
    role: "Development Director",
    company: "Urban Development Ltd"
  },
  {
    quote: "The predictive analytics are incredibly accurate. We've increased our success rate on applications by 40%.",
    author: "Sarah Thompson",
    role: "Planning Consultant",
    company: "Thompson Planning Associates"
  },
  {
    quote: "Finally, a platform that understands planning. The semantic search alone is worth the subscription.",
    author: "David Chen",
    role: "Land Acquisitions Manager",
    company: "Horizon Properties"
  }
]

export default function ProductsPage() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly')

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
                  <span className="block">Transform Weeks of Research</span>
                  <span className="block">Into Minutes of AI Insights</span>
                </h1>

                {/* Description */}
                <p className="text-lg md:text-xl text-white/90 mb-8 leading-relaxed">
                  The UK's first AI-native planning intelligence platform. Comprehensive tools and insights that transform how property professionals research, analyze, and act on UK planning data.
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

        {/* Real-Time Stats Bar from Elasticsearch */}
        <PlanningStatsBar />

        {/* Core Features - Matching Homepage Service Cards */}
        <section className="py-24 bg-white">
          <Container>
            <div className="text-center mb-16">
              <div className="inline-block px-4 py-2 bg-planning-button/10 rounded-full mb-6">
                <span className="text-planning-primary font-medium text-sm uppercase tracking-wider">
                  Core Features
                </span>
              </div>
              <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-planning-primary mb-6">
                Everything You Need for Planning Intelligence
              </h2>
              <p className="text-lg text-planning-text-light max-w-4xl mx-auto leading-relaxed">
                Comprehensive tools and insights to make faster, smarter planning decisions
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              {features.map((feature, index) => {
                const Icon = feature.icon
                return (
                  <div
                    key={index}
                    className={`${feature.bgColor} p-8 rounded-3xl transition-all duration-300 hover:shadow-lg hover:scale-105`}
                  >
                    <div className={`w-12 h-12 ${feature.iconBg} rounded-xl flex items-center justify-center mb-6`}>
                      <Icon className={`w-6 h-6 ${feature.iconColor}`} />
                    </div>
                    <h3 className="text-xl font-bold text-planning-primary mb-4 leading-tight">
                      {feature.title}
                    </h3>
                    <p className="text-planning-text-light mb-4 leading-relaxed">
                      {feature.description}
                    </p>
                    <ul className="space-y-2">
                      {feature.benefits.map((benefit, idx) => (
                        <li key={idx} className="flex items-center text-sm text-planning-text-light">
                          <Check className="w-4 h-4 text-planning-bright mr-2 flex-shrink-0" />
                          {benefit}
                        </li>
                      ))}
                    </ul>
                  </div>
                )
              })}
            </div>
          </Container>
        </section>

        {/* Pricing Section - Matching Homepage Style */}
        <section className="py-24 bg-white">
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

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
              {pricingPlans.map((plan, index) => (
                <div
                  key={index}
                  className={cn(
                    'relative rounded-2xl border-2 p-8 transition-all duration-300 flex flex-col',
                    plan.popular
                      ? 'border-planning-primary bg-planning-primary text-white scale-105 shadow-xl'
                      : 'border-planning-border bg-white hover:border-planning-primary/30 hover:shadow-lg'
                  )}
                >
                  {plan.popular && (
                    <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                      <div className="bg-planning-button text-white px-4 py-2 rounded-full text-sm font-semibold flex items-center space-x-1">
                        <Star className="w-4 h-4" />
                        <span>Most Popular</span>
                      </div>
                    </div>
                  )}

                  <div className="text-center mb-8">
                    <h3 className={cn(
                      'text-xl font-semibold mb-2',
                      plan.popular ? 'text-white' : 'text-planning-primary'
                    )}>
                      {plan.name}
                    </h3>
                    <div className="mb-4">
                      <span className={cn(
                        'text-4xl font-bold',
                        plan.popular ? 'text-white' : 'text-planning-primary'
                      )}>
                        {plan.price}
                      </span>
                      <span className={cn(
                        'text-sm ml-2',
                        plan.popular ? 'text-white/80' : 'text-planning-text-light'
                      )}>
                        {plan.period}
                      </span>
                    </div>
                    <p className={cn(
                      'text-sm leading-relaxed',
                      plan.popular ? 'text-white/90' : 'text-planning-text-light'
                    )}>
                      {plan.description}
                    </p>
                  </div>

                  <ul className="space-y-4 mb-8 flex-grow">
                    {plan.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-start">
                        <Check className={cn(
                          'w-5 h-5 mr-3 mt-0.5 flex-shrink-0',
                          plan.popular ? 'text-planning-button' : 'text-planning-bright'
                        )} />
                        <span className={cn(
                          'text-sm',
                          plan.popular ? 'text-white' : 'text-planning-text-light'
                        )}>
                          {feature}
                        </span>
                      </li>
                    ))}
                  </ul>

                  <Button
                    className={cn(
                      'w-full mt-auto',
                      plan.popular
                        ? 'bg-white text-planning-primary hover:bg-planning-button hover:text-white'
                        : 'bg-planning-primary text-white hover:bg-planning-accent'
                    )}
                    size="lg"
                  >
                    {plan.cta}
                  </Button>
                </div>
              ))}
            </div>

            <div className="text-center mt-16">
              <p className="text-planning-text-light mb-4">
                All plans include a 14-day free trial. No credit card required.
              </p>
              <div className="flex flex-wrap justify-center gap-6 text-sm text-planning-text-light">
                <span className="flex items-center">
                  <Check className="w-4 h-4 text-planning-bright mr-2" />
                  Cancel anytime
                </span>
                <span className="flex items-center">
                  <Check className="w-4 h-4 text-planning-bright mr-2" />
                  24/7 support
                </span>
                <span className="flex items-center">
                  <Check className="w-4 h-4 text-planning-bright mr-2" />
                  Secure & compliant
                </span>
              </div>
            </div>
          </Container>
        </section>

        {/* Use Cases */}
        <section className="py-24 bg-white">
          <Container>
            <div className="text-center mb-16">
              <div className="inline-block px-4 py-2 bg-planning-button/10 rounded-full mb-6">
                <span className="text-planning-primary font-medium text-sm uppercase tracking-wider">
                  Use Cases
                </span>
              </div>
              <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-planning-primary mb-6">
                Built for Property Professionals
              </h2>
              <p className="text-lg text-planning-text-light max-w-3xl mx-auto leading-relaxed">
                Tailored solutions for every role in the property and planning industry
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {useCases.map((useCase, index) => {
                const Icon = useCase.icon
                return (
                  <Link
                    key={index}
                    href={useCase.link}
                    className="bg-white rounded-2xl p-6 border border-gray-100 hover:border-planning-primary/30 hover:shadow-lg transition-all group"
                  >
                    <Icon className="w-10 h-10 text-planning-primary mb-4" />
                    <h3 className="text-xl font-bold text-planning-primary mb-3 group-hover:text-planning-accent transition-colors">
                      {useCase.title}
                    </h3>
                    <p className="text-planning-text-light mb-4 leading-relaxed">{useCase.description}</p>
                    <div className="flex items-center text-planning-primary font-medium group-hover:translate-x-2 transition-transform">
                      Learn more <ArrowRight className="w-4 h-4 ml-2" />
                    </div>
                  </Link>
                )
              })}
            </div>
          </Container>
        </section>

        {/* Testimonials - Matching Homepage Style */}
        <section className="py-24 bg-white">
          <Container>
            <div className="text-center mb-16">
              <div className="text-sm text-planning-text-light uppercase tracking-wider font-medium mb-6">
                🏆 TESTIMONIALS
              </div>
              <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-planning-primary mb-6">
                Trusted by Property Professionals
              </h2>
              <div className="flex items-center justify-center gap-2 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-6 h-6 fill-planning-bright text-planning-bright" />
                ))}
                <span className="text-planning-text-light ml-2">5.0/5.0 from 500+ reviews</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {testimonials.map((testimonial, index) => (
                <div key={index} className="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
                  <blockquote className="text-planning-text-light mb-6 leading-relaxed">
                    "{testimonial.quote}"
                  </blockquote>
                  <div>
                    <div className="font-semibold text-planning-primary">{testimonial.author}</div>
                    <div className="text-planning-text-light text-sm">{testimonial.role}</div>
                    <div className="text-planning-text-light text-sm">{testimonial.company}</div>
                  </div>
                </div>
              ))}
            </div>
          </Container>
        </section>
      </div>

      {/* Footer with CTA */}
      <Footer />
    </>
  )
}
