'use client'

import { useState } from 'react'
import { Container } from '@/components/ui/Container'
import { ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'

const faqs = [
  {
    id: 1,
    question: 'What makes Planning Explorer different from other planning data platforms?',
    answer: 'Planning Explorer is the UK\'s first AI-native planning intelligence platform. Unlike traditional portals that just display raw data, we use advanced AI to automatically score opportunities, predict approval likelihood, generate insights, and deliver personalised recommendations tailored to your business needs.',
    isExpanded: true
  },
  {
    id: 2,
    question: 'How accurate are the AI predictions and opportunity scores?',
    answer: 'Our AI models achieve 85%+ accuracy in predicting planning outcomes. We analyse historical patterns, authority performance, application characteristics, and market trends using machine learning. The system continuously improves as it processes more data and feedback.'
  },
  {
    id: 3,
    question: 'What data coverage does Planning Explorer provide?',
    answer: 'We provide complete UK coverage with 336K+ planning applications from all 321 local authorities. Every application is processed with AI enhancements including opportunity scoring, semantic embeddings, and predictive analytics. Data is updated regularly with new submissions.'
  },
  {
    id: 4,
    question: 'Can I search using natural language instead of complex filters?',
    answer: 'Yes! Our natural language search lets you ask questions like "Show me approved housing schemes in Manchester over £5M" or "Find solar panel installations in London from the last 6 months." The AI understands context and intent to deliver precisely what you need.'
  },
  {
    id: 5,
    question: 'What subscription plans are available?',
    answer: 'We offer flexible plans for everyone: Starter (Free) with limited searches and basic features, Professional (£199.99/month) with unlimited searches and advanced AI features, and Enterprise (£499.99/month) with priority support, API access, and custom integrations.'
  }
]

export function FAQ() {
  const [expandedFAQ, setExpandedFAQ] = useState<number | null>(1) // Default expanded

  const toggleFAQ = (id: number) => {
    setExpandedFAQ(expandedFAQ === id ? null : id)
  }

  return (
    <section className="py-24 bg-gradient-to-br from-planning-accent to-planning-bright relative overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-0 right-0 w-96 h-96">
          <svg viewBox="0 0 200 200" className="w-full h-full">
            <defs>
              <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                <path d="M 20 0 L 0 0 0 20" fill="none" stroke="white" strokeWidth="0.5"/>
              </pattern>
            </defs>
            <rect width="200" height="200" fill="url(#grid)" />
          </svg>
        </div>
      </div>

      <Container className="relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          {/* Left Column - Image */}
          <div className="order-2 lg:order-1">
            <div className="relative">
              <div className="bg-white/10 backdrop-blur-sm rounded-3xl overflow-hidden">
                <img
                  src="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=500&h=400&fit=crop"
                  alt="UK property development and planning"
                  className="w-full h-[400px] object-cover"
                />
              </div>
            </div>
          </div>

          {/* Right Column - FAQ Content */}
          <div className="order-1 lg:order-2">
            {/* Header */}
            <div className="mb-12">
              <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-6 leading-tight">
                Frequently Asked Questions
              </h2>
              <p className="text-white/90 text-lg">
                Learn more about Planning Explorer's AI-powered planning intelligence platform
              </p>
            </div>

            {/* FAQ Items */}
            <div className="space-y-4">
              {faqs.map((faq) => (
                <div
                  key={faq.id}
                  className="bg-white/10 backdrop-blur-sm rounded-2xl overflow-hidden border border-white/20"
                >
                  {/* Question */}
                  <button
                    onClick={() => toggleFAQ(faq.id)}
                    className="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-white/5 transition-colors"
                  >
                    <span className="text-white font-semibold text-lg">
                      {faq.question}
                    </span>
                    <ChevronDown
                      className={cn(
                        'w-5 h-5 text-white transition-transform duration-200',
                        expandedFAQ === faq.id ? 'rotate-180' : ''
                      )}
                    />
                  </button>

                  {/* Answer */}
                  <div
                    className={cn(
                      'overflow-hidden transition-all duration-300 ease-in-out',
                      expandedFAQ === faq.id
                        ? 'max-h-96 opacity-100'
                        : 'max-h-0 opacity-0'
                    )}
                  >
                    <div className="px-6 pb-6">
                      <div className="border-t border-white/20 pt-4">
                        <p className="text-white/90 leading-relaxed">
                          {faq.answer}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </Container>
    </section>
  )
}