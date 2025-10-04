'use client'

import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import { Footer } from '@/components/sections/Footer'
import { Sparkles, Search, HelpCircle, Book, Video, MessageSquare, FileText, Zap, Settings, Users, BarChart, Bell } from 'lucide-react'
import Link from 'next/link'

const popularTopics = [
  {
    icon: Search,
    title: 'Search & Discovery',
    description: 'Learn how to find planning applications',
    articleCount: '12 articles',
    color: 'bg-cyan-50',
    link: '#search'
  },
  {
    icon: BarChart,
    title: 'Analytics & Insights',
    description: 'Understanding AI predictions',
    articleCount: '8 articles',
    color: 'bg-orange-50',
    link: '#analytics'
  },
  {
    icon: Bell,
    title: 'Alerts & Notifications',
    description: 'Setting up smart alerts',
    articleCount: '6 articles',
    color: 'bg-pink-50',
    link: '#alerts'
  },
  {
    icon: Settings,
    title: 'Account & Settings',
    description: 'Managing your account',
    articleCount: '10 articles',
    color: 'bg-green-50',
    link: '#account'
  },
  {
    icon: FileText,
    title: 'Reports & Export',
    description: 'Creating reports and exporting data',
    articleCount: '7 articles',
    color: 'bg-yellow-50',
    link: '#reports'
  },
  {
    icon: Users,
    title: 'Team Collaboration',
    description: 'Working with your team',
    articleCount: '5 articles',
    color: 'bg-cyan-50',
    link: '#team'
  }
]

const faqs = [
  {
    q: 'How do I create an account?',
    a: 'Click "Start Free Trial" on the homepage, enter your email, and follow the registration steps. No credit card required for the 14-day trial.'
  },
  {
    q: 'What is semantic search?',
    a: 'Semantic search uses AI to understand the meaning behind your query, not just keywords. Search using natural language like "new residential developments near schools in London".'
  },
  {
    q: 'How do I save a search?',
    a: 'After running a search, click the "Save Search" button in the top right. Give it a name and it will appear in your dashboard for quick access.'
  },
  {
    q: 'Can I export search results?',
    a: 'Yes! All plans include CSV export. Professional and Enterprise plans also support PDF reports and API access for custom exports.'
  },
  {
    q: 'How do AI opportunity scores work?',
    a: 'Our AI analyzes multiple factors including location, application type, authority performance, and historical data to calculate an opportunity score from 0-100.'
  },
  {
    q: 'What are real-time alerts?',
    a: 'Alerts notify you via email when new planning applications match your saved search criteria. Configure frequency in Settings > Notifications.'
  },
  {
    q: 'How do I upgrade my plan?',
    a: 'Go to Settings > Billing and click "Upgrade Plan". Choose your new plan and your card will be charged prorated for the current billing period.'
  },
  {
    q: 'Can I cancel anytime?',
    a: 'Yes! Cancel from Settings > Billing. You\'ll retain access until the end of your billing period. No cancellation fees.'
  }
]

const quickLinks = [
  {
    icon: Video,
    title: 'Video Tutorials',
    description: 'Watch step-by-step guides',
    link: '/tutorials'
  },
  {
    icon: MessageSquare,
    title: 'Contact Support',
    description: 'Get help from our team',
    link: '/support'
  },
  {
    icon: Book,
    title: 'Documentation',
    description: 'Detailed API and feature docs',
    link: '#docs'
  },
  {
    icon: Users,
    title: 'Community Forum',
    description: 'Connect with other users',
    link: '/community'
  }
]

export default function HelpPage() {
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
                <span className="text-sm font-semibold text-white">Help Center</span>
              </div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold mb-4 leading-tight" style={{ color: '#FFFFFF' }}>
                <span className="block">How Can We</span>
                <span className="block">Help You Today?</span>
              </h1>
              <p className="text-xl md:text-2xl mb-8 text-white/90">
                Find answers, learn features, and get the most from Planning Explorer
              </p>
              <div className="max-w-2xl mx-auto">
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-planning-text-light w-5 h-5" />
                  <input
                    type="text"
                    placeholder="Search for help articles..."
                    className="w-full pl-12 pr-4 py-4 rounded-2xl border-2 border-white/20 bg-white/10 backdrop-blur-sm text-white placeholder-white/60 focus:border-white/40 focus:outline-none transition-colors"
                  />
                </div>
              </div>
            </div>
          </Container>
        </div>
      </section>

      {/* Popular Topics */}
      <section className="py-24 bg-white relative -mt-20 z-30">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-planning-primary mb-6">
              Popular Topics
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              Browse help articles by category
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {popularTopics.map((topic, index) => (
              <Link key={index} href={topic.link}>
                <div className={`${topic.color} rounded-3xl p-8 hover:shadow-lg hover:scale-105 transition-all duration-300 cursor-pointer`}>
                  <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center mb-6 shadow-sm">
                    <topic.icon className="w-8 h-8 text-planning-primary" />
                  </div>
                  <h3 className="text-xl font-bold text-planning-primary mb-3">{topic.title}</h3>
                  <p className="text-planning-text-light text-sm mb-4 leading-relaxed">{topic.description}</p>
                  <p className="text-xs text-planning-primary font-semibold">{topic.articleCount}</p>
                </div>
              </Link>
            ))}
          </div>
        </Container>
      </section>

      {/* FAQs */}
      <section className="py-24 bg-gray-50">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-planning-primary mb-6">
              Frequently Asked Questions
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              Quick answers to common questions
            </p>
          </div>

          <div className="max-w-4xl mx-auto space-y-6">
            {faqs.map((faq, index) => (
              <div key={index} className="bg-white rounded-3xl p-8 hover:shadow-md transition-all">
                <h3 className="text-xl font-bold text-planning-primary mb-4 flex items-start">
                  <HelpCircle className="w-6 h-6 mr-3 mt-0.5 flex-shrink-0 text-planning-bright" />
                  {faq.q}
                </h3>
                <p className="text-planning-text-light leading-relaxed pl-9">{faq.a}</p>
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <p className="text-planning-text-light mb-6">
              Can't find what you're looking for?
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <Link href="/support">
                <Button size="lg" className="bg-planning-primary text-white hover:bg-planning-accent">
                  Contact Support
                </Button>
              </Link>
              <Link href="/community">
                <Button size="lg" variant="outline">
                  Ask the Community
                </Button>
              </Link>
            </div>
          </div>
        </Container>
      </section>

      {/* Quick Links */}
      <section className="py-24 bg-white">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-planning-primary mb-4">
              More Ways to Get Help
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
            {quickLinks.map((link, index) => (
              <Link key={index} href={link.link}>
                <div className="bg-gray-50 rounded-3xl p-8 text-center hover:shadow-lg hover:scale-105 transition-all duration-300 cursor-pointer">
                  <link.icon className="w-12 h-12 text-planning-primary mx-auto mb-4" />
                  <h3 className="text-lg font-bold text-planning-primary mb-2">{link.title}</h3>
                  <p className="text-sm text-planning-text-light">{link.description}</p>
                </div>
              </Link>
            ))}
          </div>
        </Container>
      </section>

      {/* Still Need Help */}
      <section className="py-24 bg-gray-50">
        <Container>
          <div className="max-w-4xl mx-auto bg-gradient-to-br from-planning-primary to-planning-accent rounded-3xl p-8 md:p-12 text-white text-center">
            <MessageSquare className="w-16 h-16 mx-auto mb-6" />
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Still Need Help?
            </h2>
            <p className="text-xl text-white/90 mb-8">
              Our support team is here to assist you
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <Link href="/support">
                <Button size="lg" className="bg-white text-planning-primary hover:bg-gray-100">
                  Contact Support
                </Button>
              </Link>
              <Link href="/tutorials">
                <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10">
                  Watch Tutorials
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
