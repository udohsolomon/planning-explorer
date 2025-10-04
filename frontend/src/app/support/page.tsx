'use client'

import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import { Footer } from '@/components/sections/Footer'
import { Sparkles, HelpCircle, BookOpen, MessageSquare, Video, FileText, Search, Zap, Shield, Users } from 'lucide-react'
import Link from 'next/link'

const supportOptions = [
  {
    icon: MessageSquare,
    title: 'Live Chat Support',
    description: 'Get instant help from our support team',
    availability: 'Mon-Fri, 9am-6pm GMT',
    action: 'Start Chat',
    href: '#chat',
    color: 'bg-cyan-50'
  },
  {
    icon: HelpCircle,
    title: 'Help Center',
    description: 'Browse FAQs and troubleshooting guides',
    availability: 'Available 24/7',
    action: 'Visit Help Center',
    href: '/help',
    color: 'bg-orange-50'
  },
  {
    icon: Video,
    title: 'Video Tutorials',
    description: 'Watch step-by-step video guides',
    availability: 'On-demand access',
    action: 'Watch Tutorials',
    href: '/tutorials',
    color: 'bg-pink-50'
  },
  {
    icon: FileText,
    title: 'Email Support',
    description: 'Send us a detailed support request',
    availability: '24-hour response time',
    action: 'Send Email',
    href: 'mailto:support@planningexplorer.co.uk',
    color: 'bg-green-50'
  }
]

const faqs = [
  {
    category: 'Getting Started',
    questions: [
      {
        q: 'How do I create an account?',
        a: 'Click "Start Free Trial" on our homepage, enter your email, and follow the onboarding steps. No credit card required for the 14-day trial.'
      },
      {
        q: 'What is semantic search and how does it work?',
        a: 'Semantic search uses AI to understand the meaning behind your query, not just keywords. You can search using natural language like "residential developments near London" and get highly relevant results.'
      },
      {
        q: 'How current is your planning data?',
        a: 'Our database is updated in real-time from official UK planning authorities. New applications are typically indexed within 24 hours of submission.'
      }
    ]
  },
  {
    category: 'Account & Billing',
    questions: [
      {
        q: 'Can I change my plan at any time?',
        a: 'Yes! You can upgrade or downgrade your plan anytime. Changes take effect in your next billing cycle, and we'll prorate any adjustments.'
      },
      {
        q: 'What payment methods do you accept?',
        a: 'We accept all major credit cards (Visa, Mastercard, American Express) and bank transfers for Enterprise plans.'
      },
      {
        q: 'Is there a free trial?',
        a: 'Yes! All plans come with a 14-day free trial. No credit card required to start your trial.'
      }
    ]
  },
  {
    category: 'Features & Usage',
    questions: [
      {
        q: 'What are saved searches and how do I use them?',
        a: 'Saved searches let you bookmark your queries for quick access. Run a search, click "Save Search", and it will appear in your dashboard for one-click access.'
      },
      {
        q: 'How do AI alerts work?',
        a: 'Our AI monitors new planning applications matching your criteria and sends real-time email alerts. Configure alerts in Settings > Notifications.'
      },
      {
        q: 'Can I export search results?',
        a: 'Yes! All plans include CSV export. Professional and Enterprise plans also support PDF reports and custom data exports via API.'
      }
    ]
  },
  {
    category: 'Technical Support',
    questions: [
      {
        q: 'What browsers are supported?',
        a: 'Planning Explorer works best on the latest versions of Chrome, Firefox, Safari, and Edge. We recommend Chrome for optimal performance.'
      },
      {
        q: 'Do you have an API?',
        a: 'Yes! Starter plans include limited API access. Professional and Enterprise plans get full API access with comprehensive documentation.'
      },
      {
        q: 'Is my data secure?',
        a: 'Absolutely. We use enterprise-grade encryption, SOC 2 compliance, and regular security audits. Your data is never shared with third parties.'
      }
    ]
  }
]

const quickLinks = [
  {
    icon: BookOpen,
    title: 'Documentation',
    description: 'Complete guides and API reference',
    href: '/help'
  },
  {
    icon: Video,
    title: 'Video Library',
    description: 'Step-by-step tutorials',
    href: '/tutorials'
  },
  {
    icon: Users,
    title: 'Community Forum',
    description: 'Connect with other users',
    href: '/community'
  },
  {
    icon: Zap,
    title: 'Feature Updates',
    description: 'Latest releases and improvements',
    href: '/news'
  }
]

const supportPlans = [
  {
    name: 'Starter Support',
    features: [
      'Email support (24-hour response)',
      'Help Center access',
      'Video tutorials',
      'Community forum'
    ],
    icon: Shield,
    color: 'bg-cyan-50'
  },
  {
    name: 'Professional Support',
    features: [
      'Priority email support (4-hour response)',
      'Live chat support',
      'Phone support',
      'Dedicated onboarding',
      'Everything in Starter'
    ],
    icon: Zap,
    color: 'bg-orange-50',
    popular: true
  },
  {
    name: 'Enterprise Support',
    features: [
      'Dedicated account manager',
      'Custom SLA guarantees',
      '24/7 emergency support',
      'Personalized training sessions',
      'Everything in Professional'
    ],
    icon: Users,
    color: 'bg-pink-50'
  }
]

export default function SupportPage() {
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
                <span className="text-sm font-semibold text-white">Support Center</span>
              </div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold mb-4 leading-tight" style={{ color: '#FFFFFF' }}>
                <span className="block">We're Here to Help You</span>
                <span className="block">Succeed with Planning Explorer</span>
              </h1>
              <p className="text-xl md:text-2xl mb-8 text-white/90">
                Get the support you need, when you need it. From quick answers to dedicated account management.
              </p>
              <div className="max-w-2xl mx-auto">
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-planning-text-light w-5 h-5" />
                  <input
                    type="text"
                    placeholder="Search for help articles, guides, and FAQs..."
                    className="w-full pl-12 pr-4 py-4 rounded-2xl border-2 border-white/20 bg-white/10 backdrop-blur-sm text-white placeholder-white/60 focus:border-white/40 focus:outline-none transition-colors"
                  />
                </div>
              </div>
            </div>
          </Container>
        </div>
      </section>

      {/* Support Options */}
      <section className="py-24 bg-white relative -mt-20 z-30">
        <Container>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
            {supportOptions.map((option, index) => (
              <div
                key={index}
                className={`${option.color} rounded-3xl p-8 text-center hover:shadow-lg hover:scale-105 transition-all duration-300`}
              >
                <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-sm">
                  <option.icon className="w-8 h-8 text-planning-primary" />
                </div>
                <h3 className="text-xl font-bold text-planning-primary mb-2">{option.title}</h3>
                <p className="text-planning-text-light text-sm mb-3 leading-relaxed">{option.description}</p>
                <p className="text-xs text-planning-text-light mb-4 font-medium">{option.availability}</p>
                <Link href={option.href}>
                  <Button size="sm" className="bg-planning-primary text-white hover:bg-planning-accent">
                    {option.action}
                  </Button>
                </Link>
              </div>
            ))}
          </div>
        </Container>
      </section>

      {/* Support Plans */}
      <section className="py-24 bg-gray-50">
        <Container>
          <div className="text-center mb-16">
            <div className="inline-block px-4 py-2 bg-planning-button/10 rounded-full mb-6">
              <span className="text-planning-primary font-medium text-sm uppercase tracking-wider">
                Support Tiers
              </span>
            </div>
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-planning-primary mb-6">
              Choose Your Support Level
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              Support options tailored to your needs - from self-service to dedicated account management
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {supportPlans.map((plan, index) => (
              <div
                key={index}
                className={`${plan.color} rounded-3xl p-8 hover:shadow-lg hover:scale-105 transition-all duration-300 ${
                  plan.popular ? 'ring-4 ring-planning-primary/20' : ''
                }`}
              >
                {plan.popular && (
                  <div className="text-center mb-4">
                    <span className="inline-block px-3 py-1 bg-planning-primary text-white text-xs font-bold rounded-full">
                      MOST POPULAR
                    </span>
                  </div>
                )}
                <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-sm">
                  <plan.icon className="w-8 h-8 text-planning-primary" />
                </div>
                <h3 className="text-2xl font-bold text-planning-primary mb-6 text-center">{plan.name}</h3>
                <ul className="space-y-3">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-start">
                      <div className="w-5 h-5 bg-planning-primary rounded-full flex items-center justify-center mr-3 mt-0.5 flex-shrink-0">
                        <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                      <span className="text-planning-text-light text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <p className="text-planning-text-light mb-6">
              Want to learn more about support options?
            </p>
            <Link href="/pricing">
              <Button size="lg" className="bg-planning-primary text-white hover:bg-planning-accent">
                View All Plans & Pricing
              </Button>
            </Link>
          </div>
        </Container>
      </section>

      {/* FAQs */}
      <section className="py-24 bg-white">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-planning-primary mb-6">
              Frequently Asked Questions
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              Quick answers to common questions
            </p>
          </div>

          <div className="max-w-5xl mx-auto space-y-12">
            {faqs.map((section, sectionIndex) => (
              <div key={sectionIndex}>
                <h3 className="text-2xl font-bold text-planning-primary mb-6 pb-3 border-b-2 border-planning-border">
                  {section.category}
                </h3>
                <div className="space-y-6">
                  {section.questions.map((faq, faqIndex) => (
                    <div key={faqIndex} className="bg-gray-50 rounded-2xl p-6 hover:shadow-md transition-all">
                      <h4 className="text-lg font-bold text-planning-primary mb-3">{faq.q}</h4>
                      <p className="text-planning-text-light leading-relaxed">{faq.a}</p>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="text-center mt-16">
            <p className="text-planning-text-light mb-6">
              Can't find what you're looking for?
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <Link href="/contact">
                <Button size="lg" className="bg-planning-primary text-white hover:bg-planning-accent">
                  Contact Support
                </Button>
              </Link>
              <Link href="/help">
                <Button size="lg" variant="outline">
                  Browse Help Center
                </Button>
              </Link>
            </div>
          </div>
        </Container>
      </section>

      {/* Quick Links */}
      <section className="py-24 bg-gray-50">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-planning-primary mb-4">
              Additional Resources
            </h2>
            <p className="text-xl text-planning-text-light">
              Explore more ways to get help and stay informed
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
            {quickLinks.map((link, index) => (
              <Link key={index} href={link.href}>
                <div className="bg-white rounded-3xl p-8 text-center hover:shadow-lg hover:scale-105 transition-all duration-300 cursor-pointer">
                  <link.icon className="w-12 h-12 text-planning-primary mx-auto mb-4" />
                  <h3 className="text-lg font-bold text-planning-primary mb-2">{link.title}</h3>
                  <p className="text-sm text-planning-text-light">{link.description}</p>
                </div>
              </Link>
            ))}
          </div>
        </Container>
      </section>

      {/* Emergency Support */}
      <section className="py-24 bg-white">
        <Container>
          <div className="max-w-4xl mx-auto bg-gradient-to-br from-planning-primary to-planning-accent rounded-3xl p-8 md:p-12 text-white text-center">
            <Shield className="w-16 h-16 mx-auto mb-6" />
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Need Urgent Help?
            </h2>
            <p className="text-xl text-white/90 mb-8">
              Enterprise customers have access to 24/7 emergency support
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <a href="mailto:urgent@planningexplorer.co.uk">
                <Button size="lg" className="bg-white text-planning-primary hover:bg-gray-100">
                  Email Urgent Support
                </Button>
              </a>
              <Link href="/pricing">
                <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10">
                  Upgrade to Enterprise
                </Button>
              </Link>
            </div>
          </div>
        </Container>
      </section>

      <Footer />
    </div>
  )
}
