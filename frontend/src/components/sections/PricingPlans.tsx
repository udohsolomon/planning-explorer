'use client'

import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import { Check, Star } from 'lucide-react'
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

export function PricingPlans() {
  return (
    <section className="py-24 bg-white">
      <Container>
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-block px-4 py-2 bg-planning-button/10 rounded-full mb-6">
            <span className="text-planning-primary font-medium text-sm uppercase tracking-wider">
              Pricing Plans
            </span>
          </div>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-heading font-bold text-planning-primary mb-6">
            Choose Your Plan
          </h2>
          <p className="text-lg text-planning-text-light max-w-3xl mx-auto leading-relaxed">
            Flexible pricing options to suit businesses of all sizes. Start with a free trial and scale as you grow.
          </p>
        </div>

        {/* Pricing Cards */}
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
              {/* Popular Badge */}
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <div className="bg-planning-button text-white px-4 py-2 rounded-full text-sm font-semibold flex items-center space-x-1">
                    <Star className="w-4 h-4" />
                    <span>Most Popular</span>
                  </div>
                </div>
              )}

              {/* Plan Header */}
              <div className="text-center mb-8">
                <h3 className={cn(
                  'text-xl font-heading font-semibold mb-2',
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

              {/* Features */}
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

              {/* CTA Button */}
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

        {/* Additional Info */}
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
  )
}