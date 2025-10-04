'use client'

import { Container } from '@/components/ui/Container'
import { MapPin, Zap, Brain, Search, CreditCard } from 'lucide-react'

const services = [
  {
    icon: Brain,
    title: 'Intelligent Opportunity Detection',
    description: 'AI automatically identifies and scores planning opportunities you\'d never find manually. Our advanced algorithms analyse every application against your business criteria and market trends.',
    bgColor: 'bg-cyan-50',
    iconBg: 'bg-blue-100',
    iconColor: 'text-blue-600'
  },
  {
    icon: Zap,
    title: 'Instant Market Intelligence',
    description: 'Get comprehensive insights in seconds, not weeks. Our AI processes applications, generates predictive analytics, and delivers actionable intelligence faster than any manual research.',
    bgColor: 'bg-orange-50',
    iconBg: 'bg-orange-100',
    iconColor: 'text-orange-600'
  },
  {
    icon: MapPin,
    title: 'Complete UK Coverage',
    description: 'Every planning application from every UK local authority, intelligently analysed. Our database covers 336K+ applications with AI-enhanced insights and semantic search capabilities.',
    bgColor: 'bg-green-50',
    iconBg: 'bg-green-100',
    iconColor: 'text-green-600'
  },
  {
    icon: Search,
    title: 'Natural Language Search',
    description: 'Ask questions in plain English like "Show me approved housing schemes in Manchester over £5M." Our AI understands context and intent, delivering precisely what you need.',
    bgColor: 'bg-yellow-50',
    iconBg: 'bg-yellow-100',
    iconColor: 'text-yellow-600'
  },
  {
    icon: CreditCard,
    title: 'Predictive Analytics',
    description: 'Know approval likelihood and timelines before you apply. Our AI analyses historical patterns and authority performance to forecast planning outcomes with 85%+ accuracy.',
    bgColor: 'bg-pink-50',
    iconBg: 'bg-pink-100',
    iconColor: 'text-pink-600'
  }
]

export function ServiceHighlights() {
  return (
    <section className="py-24 bg-white">
      <Container>
        {/* Intro Text */}
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-planning-primary mb-6">
            AI-First Planning Intelligence That Works For You
          </h2>
          <p className="text-lg text-planning-text-light max-w-4xl mx-auto leading-relaxed">
            Planning Explorer combines complete UK planning coverage with advanced AI to deliver intelligent opportunity detection, predictive analytics, and personalised insights. Built for property developers, consultants, suppliers, and investors who demand speed, accuracy, and actionable intelligence.
          </p>
        </div>

        {/* Service Cards Grid */}
        <div className="relative">
          {/* Background decorative elements */}
          <div className="absolute top-0 right-0 w-64 h-64 opacity-20">
            <svg viewBox="0 0 200 200" className="w-full h-full">
              <defs>
                <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#c8f169" stopOpacity="0.3"/>
                  <stop offset="100%" stopColor="#2DCC9E" stopOpacity="0.1"/>
                </linearGradient>
              </defs>
              <path d="M50 150 Q 150 50 150 150 Q 50 250 50 150" stroke="url(#grad1)" strokeWidth="2" fill="none"/>
              <circle cx="50" cy="150" r="3" fill="#c8f169"/>
              <circle cx="150" cy="150" r="3" fill="#2DCC9E"/>
            </svg>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Service Cards */}
            {services.map((service, index) => {
              const IconComponent = service.icon
              return (
                <div
                  key={index}
                  className={`${service.bgColor} p-8 rounded-3xl transition-all duration-300 hover:shadow-lg hover:scale-105 relative overflow-hidden`}
                >
                  {/* Decorative background pattern */}
                  {index === 2 && (
                    <div className="absolute bottom-0 right-0 opacity-30">
                      <svg width="120" height="120" viewBox="0 0 120 120">
                        <defs>
                          <linearGradient id="greenGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#10b981" stopOpacity="0.2"/>
                            <stop offset="100%" stopColor="#059669" stopOpacity="0.1"/>
                          </linearGradient>
                        </defs>
                        <path d="M20 60 Q60 20 100 60 Q60 100 20 60" fill="url(#greenGrad)"/>
                      </svg>
                    </div>
                  )}

                  {/* Icon */}
                  <div className={`w-12 h-12 ${service.iconBg} rounded-xl flex items-center justify-center mb-6`}>
                    <IconComponent className={`w-6 h-6 ${service.iconColor}`} />
                  </div>

                  {/* Content */}
                  <h3 className="text-xl font-bold text-planning-primary mb-4 leading-tight">
                    {service.title}
                  </h3>
                  <p className="text-planning-text-light leading-relaxed">
                    {service.description}
                  </p>
                </div>
              )
            })}
          </div>

          {/* Standalone 100% Element - Bottom Right */}
          <div className="absolute bottom-0 right-0 lg:bottom-8 lg:right-8">
            <div className="text-right">
              {/* Massive 100% Display */}
              <div className="relative">
                <div className="text-[8rem] md:text-[10rem] lg:text-[12rem] font-black text-planning-primary/10 leading-none">
                  100
                </div>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-4xl md:text-5xl lg:text-6xl font-black text-planning-primary">
                    <span className="text-planning-button">%</span>100
                  </div>
                </div>
              </div>
              {/* Title */}
              <div className="mt-4">
                <h3 className="text-lg font-bold text-planning-primary mb-2">
                  UK Planning Application Coverage
                </h3>
                {/* Feature bullets */}
                <div className="space-y-1 text-right">
                  <div className="flex items-center justify-end space-x-2">
                    <span className="text-planning-text-light text-sm">All UK Local Authorities</span>
                    <div className="w-1.5 h-1.5 bg-planning-accent rounded-full"></div>
                  </div>
                  <div className="flex items-center justify-end space-x-2">
                    <span className="text-planning-text-light text-sm">Historical & Current Data</span>
                    <div className="w-1.5 h-1.5 bg-planning-accent rounded-full"></div>
                  </div>
                  <div className="flex items-center justify-end space-x-2">
                    <span className="text-planning-text-light text-sm">Monthly Updates</span>
                    <div className="w-1.5 h-1.5 bg-planning-accent rounded-full"></div>
                  </div>
                  <div className="flex items-center justify-end space-x-2">
                    <span className="text-planning-text-light text-sm">Expert Verification</span>
                    <div className="w-1.5 h-1.5 bg-planning-accent rounded-full"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Container>
    </section>
  )
}