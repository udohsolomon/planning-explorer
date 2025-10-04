'use client'

import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import { Footer } from '@/components/sections/Footer'
import { Check, X, Star, Sparkles } from 'lucide-react'
import Link from 'next/link'
import { cn } from '@/lib/utils'

const plans = [
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

const comparisonFeatures = [
  {
    category: 'Core Features',
    features: [
      { name: 'Planning Application Search', starter: true, professional: true, enterprise: true },
      { name: 'Search Queries per Month', starter: '10,000', professional: '50,000', enterprise: 'Unlimited' },
      { name: 'AI-Powered Semantic Search', starter: true, professional: true, enterprise: true },
      { name: 'Natural Language Queries', starter: true, professional: true, enterprise: true },
      { name: 'Real-Time Alerts', starter: false, professional: true, enterprise: true },
      { name: 'Saved Searches', starter: '5', professional: 'Unlimited', enterprise: 'Unlimited' }
    ]
  },
  {
    category: 'AI & Analytics',
    features: [
      { name: 'Basic AI Analytics', starter: true, professional: true, enterprise: true },
      { name: 'Advanced AI Analytics', starter: false, professional: true, enterprise: true },
      { name: 'Predictive Analytics', starter: false, professional: true, enterprise: true },
      { name: 'Approval Likelihood Predictions', starter: false, professional: true, enterprise: true },
      { name: 'Timeline Forecasting', starter: false, professional: true, enterprise: true },
      { name: 'Custom AI Model Training', starter: false, professional: false, enterprise: true }
    ]
  },
  {
    category: 'Reports & Data Export',
    features: [
      { name: 'Standard Reports', starter: true, professional: true, enterprise: true },
      { name: 'Custom Reports', starter: false, professional: true, enterprise: true },
      { name: 'Interactive Dashboards', starter: false, professional: true, enterprise: true },
      { name: 'PDF Export', starter: true, professional: true, enterprise: true },
      { name: 'CSV/Excel Export', starter: true, professional: true, enterprise: true },
      { name: 'White-Label Reports', starter: false, professional: false, enterprise: true }
    ]
  },
  {
    category: 'Geographic & Market Intelligence',
    features: [
      { name: 'Geographic Search', starter: true, professional: true, enterprise: true },
      { name: 'Authority Performance Analysis', starter: false, professional: true, enterprise: true },
      { name: 'Geographic Heat Maps', starter: false, professional: true, enterprise: true },
      { name: 'Market Trend Analysis', starter: false, professional: true, enterprise: true },
      { name: 'Competitor Tracking', starter: false, professional: true, enterprise: true }
    ]
  },
  {
    category: 'API & Integrations',
    features: [
      { name: 'API Access', starter: 'Limited', professional: 'Full', enterprise: 'Full' },
      { name: 'Webhooks', starter: false, professional: true, enterprise: true },
      { name: 'Custom Integrations', starter: false, professional: false, enterprise: true },
      { name: 'On-Premise Deployment', starter: false, professional: false, enterprise: true }
    ]
  },
  {
    category: 'Support & Security',
    features: [
      { name: 'Email Support', starter: true, professional: true, enterprise: true },
      { name: 'Priority Support', starter: false, professional: true, enterprise: true },
      { name: 'Phone Support', starter: false, professional: false, enterprise: true },
      { name: 'Dedicated Account Manager', starter: false, professional: false, enterprise: true },
      { name: 'SLA Guarantees', starter: false, professional: false, enterprise: true },
      { name: 'Advanced Security Features', starter: false, professional: false, enterprise: true }
    ]
  }
]

export default function PricingPage() {
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
                <span className="text-sm font-semibold text-white">Transparent Pricing</span>
              </div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold mb-4 leading-tight" style={{ color: '#FFFFFF' }}>
                <span className="block">Choose the Perfect Plan</span>
                <span className="block">For Your Business</span>
              </h1>
              <p className="text-xl md:text-2xl mb-8 text-white/90">
                Flexible pricing options to suit businesses of all sizes. Start with a free trial and scale as you grow.
              </p>
            </div>
          </Container>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="py-24 bg-white relative -mt-20 z-30">
        <Container>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {plans.map((plan, index) => (
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
                    'w-full',
                    plan.popular
                      ? 'bg-white text-planning-primary hover:bg-gray-100'
                      : 'bg-planning-primary text-white hover:bg-planning-accent'
                  )}
                >
                  {plan.cta}
                </Button>
              </div>
            ))}
          </div>
        </Container>
      </section>

      {/* Detailed Comparison Table */}
      <section className="py-24 bg-gray-50">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-planning-primary mb-4">
              Compare Plans & Features
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              Detailed feature comparison to help you choose the right plan
            </p>
          </div>

          <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-planning-primary text-white">
                  <tr>
                    <th className="text-left py-4 px-6 font-semibold">Features</th>
                    <th className="text-center py-4 px-6 font-semibold">Starter</th>
                    <th className="text-center py-4 px-6 font-semibold relative">
                      <div className="absolute -top-2 left-1/2 transform -translate-x-1/2">
                        <div className="bg-planning-button text-white px-3 py-1 rounded-full text-xs font-bold">
                          POPULAR
                        </div>
                      </div>
                      Professional
                    </th>
                    <th className="text-center py-4 px-6 font-semibold">Enterprise</th>
                  </tr>
                </thead>
                <tbody>
                  {comparisonFeatures.map((category, categoryIndex) => (
                    <>
                      <tr key={`category-${categoryIndex}`} className="bg-gray-100">
                        <td colSpan={4} className="py-3 px-6 font-bold text-planning-primary">
                          {category.category}
                        </td>
                      </tr>
                      {category.features.map((feature, featureIndex) => (
                        <tr
                          key={`feature-${categoryIndex}-${featureIndex}`}
                          className={cn(
                            'border-b border-gray-200',
                            featureIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'
                          )}
                        >
                          <td className="py-4 px-6 text-planning-text-light">{feature.name}</td>
                          <td className="py-4 px-6 text-center">
                            {typeof feature.starter === 'boolean' ? (
                              feature.starter ? (
                                <Check className="w-5 h-5 text-planning-bright mx-auto" />
                              ) : (
                                <X className="w-5 h-5 text-gray-300 mx-auto" />
                              )
                            ) : (
                              <span className="text-planning-primary font-medium">{feature.starter}</span>
                            )}
                          </td>
                          <td className="py-4 px-6 text-center bg-planning-primary/5">
                            {typeof feature.professional === 'boolean' ? (
                              feature.professional ? (
                                <Check className="w-5 h-5 text-planning-bright mx-auto" />
                              ) : (
                                <X className="w-5 h-5 text-gray-300 mx-auto" />
                              )
                            ) : (
                              <span className="text-planning-primary font-medium">{feature.professional}</span>
                            )}
                          </td>
                          <td className="py-4 px-6 text-center">
                            {typeof feature.enterprise === 'boolean' ? (
                              feature.enterprise ? (
                                <Check className="w-5 h-5 text-planning-bright mx-auto" />
                              ) : (
                                <X className="w-5 h-5 text-gray-300 mx-auto" />
                              )
                            ) : (
                              <span className="text-planning-primary font-medium">{feature.enterprise}</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="text-center mt-12">
            <p className="text-planning-text-light mb-6">
              All plans include a 14-day free trial. No credit card required.
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <Button size="lg" className="bg-planning-primary text-white hover:bg-planning-accent">
                Start Free Trial
              </Button>
              <Button size="lg" variant="outline">
                Contact Sales
              </Button>
            </div>
          </div>
        </Container>
      </section>

      {/* FAQ Section */}
      <section className="py-24 bg-white">
        <Container>
          <div className="max-w-3xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-planning-primary mb-4">
                Frequently Asked Questions
              </h2>
            </div>

            <div className="space-y-6">
              <div className="bg-gray-50 rounded-xl p-6">
                <h3 className="text-lg font-bold text-planning-primary mb-2">
                  Can I switch plans at any time?
                </h3>
                <p className="text-planning-text-light">
                  Yes! You can upgrade or downgrade your plan at any time. Changes will be reflected in your next billing cycle.
                </p>
              </div>

              <div className="bg-gray-50 rounded-xl p-6">
                <h3 className="text-lg font-bold text-planning-primary mb-2">
                  Is there a free trial?
                </h3>
                <p className="text-planning-text-light">
                  All paid plans come with a 14-day free trial. No credit card required to start your trial.
                </p>
              </div>

              <div className="bg-gray-50 rounded-xl p-6">
                <h3 className="text-lg font-bold text-planning-primary mb-2">
                  What payment methods do you accept?
                </h3>
                <p className="text-planning-text-light">
                  We accept all major credit cards (Visa, Mastercard, American Express) and bank transfers for Enterprise plans.
                </p>
              </div>

              <div className="bg-gray-50 rounded-xl p-6">
                <h3 className="text-lg font-bold text-planning-primary mb-2">
                  Can I cancel anytime?
                </h3>
                <p className="text-planning-text-light">
                  Yes, you can cancel your subscription at any time. You'll continue to have access until the end of your billing period.
                </p>
              </div>

              <div className="bg-gray-50 rounded-xl p-6">
                <h3 className="text-lg font-bold text-planning-primary mb-2">
                  Do you offer custom Enterprise solutions?
                </h3>
                <p className="text-planning-text-light">
                  Yes! Our Enterprise plan is fully customizable. Contact our sales team to discuss your specific requirements.
                </p>
              </div>
            </div>
          </div>
        </Container>
      </section>

      <Footer />
    </div>
  )
}
