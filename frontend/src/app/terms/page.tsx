'use client'

import { Container } from '@/components/ui/Container'
import { Footer } from '@/components/sections/Footer'
import { Sparkles, FileText, Mail } from 'lucide-react'
import Link from 'next/link'

export default function TermsPage() {
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
                <span className="text-sm font-semibold text-white">Legal</span>
              </div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold mb-4 leading-tight" style={{ color: '#FFFFFF' }}>
                <span className="block">Terms of Service</span>
                <span className="block">& User Agreement</span>
              </h1>
              <p className="text-xl md:text-2xl mb-8 text-white/90">
                Last updated: October 4, 2025
              </p>
            </div>
          </Container>
        </div>
      </section>

      {/* Content */}
      <section className="py-24 bg-white relative -mt-20 z-30">
        <Container>
          <div className="max-w-4xl mx-auto">
            <div className="bg-orange-50 rounded-3xl p-8 mb-12">
              <div className="flex items-start gap-4">
                <FileText className="w-8 h-8 text-planning-primary flex-shrink-0 mt-1" />
                <div>
                  <h2 className="text-2xl font-bold text-planning-primary mb-3">Agreement to Terms</h2>
                  <p className="text-planning-text-light leading-relaxed">
                    By accessing and using Planning Explorer, you agree to be bound by these Terms of Service. If you do not agree with any part of these terms, you may not use our service. Please read these terms carefully before using our AI-powered planning intelligence platform.
                  </p>
                </div>
              </div>
            </div>

            <div className="prose prose-lg max-w-none space-y-12">
              <section>
                <h2 className="text-2xl font-bold text-planning-primary mb-4">1. Service Description</h2>
                <div className="bg-gray-50 rounded-2xl p-6">
                  <p className="text-planning-text-light leading-relaxed mb-4">
                    Planning Explorer is an AI-powered platform that provides access to UK planning application data, semantic search, predictive analytics, and planning intelligence tools. We aggregate publicly available planning data and enhance it with AI-generated insights.
                  </p>
                  <p className="text-planning-text-light leading-relaxed">
                    <strong>Data Accuracy:</strong> While we strive for accuracy, planning data is sourced from third-party authorities and may contain errors or delays. AI predictions are estimates and should not be solely relied upon for investment decisions.
                  </p>
                </div>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-planning-primary mb-4">2. User Accounts</h2>
                <div className="bg-gray-50 rounded-2xl p-6">
                  <ul className="space-y-3 text-planning-text-light">
                    <li><strong>Registration:</strong> You must provide accurate, current information when creating an account. You are responsible for maintaining account security and all activities under your account.</li>
                    <li><strong>Eligibility:</strong> You must be 18+ and have legal capacity to enter into contracts. Business accounts require authorization to bind your organization.</li>
                    <li><strong>Account Termination:</strong> We reserve the right to suspend or terminate accounts for violations of these terms, fraudulent activity, or misuse of the platform.</li>
                  </ul>
                </div>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-planning-primary mb-4">3. Subscription & Billing</h2>
                <div className="bg-gray-50 rounded-2xl p-6 space-y-4">
                  <div>
                    <h3 className="text-lg font-bold text-planning-primary mb-2">Free Trial</h3>
                    <p className="text-planning-text-light leading-relaxed">
                      14-day free trial for new users. No credit card required. Trial converts to paid subscription unless cancelled.
                    </p>
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-planning-primary mb-2">Paid Plans</h3>
                    <p className="text-planning-text-light leading-relaxed">
                      Subscriptions are billed monthly or annually in advance. Prices are listed on our{' '}
                      <Link href="/pricing" className="text-planning-primary hover:underline font-semibold">
                        Pricing page
                      </Link>. We reserve the right to change pricing with 30 days notice.
                    </p>
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-planning-primary mb-2">Refunds</h3>
                    <p className="text-planning-text-light leading-relaxed">
                      Monthly subscriptions are non-refundable. Annual subscriptions may be eligible for prorated refunds within 30 days of initial purchase, at our discretion.
                    </p>
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-planning-primary mb-2">Cancellation</h3>
                    <p className="text-planning-text-light leading-relaxed">
                      Cancel anytime from your account settings. Access continues until the end of your billing period. No refunds for partial months.
                    </p>
                  </div>
                </div>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-planning-primary mb-4">4. Acceptable Use</h2>
                <div className="bg-gray-50 rounded-2xl p-6">
                  <p className="text-planning-text-light leading-relaxed mb-4">
                    You agree NOT to:
                  </p>
                  <ul className="space-y-2 text-planning-text-light">
                    <li>• Scrape, crawl, or systematically extract data beyond your plan limits</li>
                    <li>• Share your account credentials with unauthorized users</li>
                    <li>• Reverse engineer, decompile, or attempt to extract our AI models</li>
                    <li>• Use the platform for illegal purposes or to violate third-party rights</li>
                    <li>• Overload our systems or attempt to bypass rate limits</li>
                    <li>• Resell or redistribute our data without written permission</li>
                    <li>• Create accounts using automated methods or false information</li>
                  </ul>
                  <p className="text-planning-text-light leading-relaxed mt-4">
                    Violations may result in immediate account termination without refund.
                  </p>
                </div>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-planning-primary mb-4">5. Intellectual Property</h2>
                <div className="bg-gray-50 rounded-2xl p-6 space-y-4">
                  <div>
                    <h3 className="text-lg font-bold text-planning-primary mb-2">Our IP</h3>
                    <p className="text-planning-text-light leading-relaxed">
                      Planning Explorer's platform, software, AI models, algorithms, branding, and content are protected by copyright, trademark, and other IP laws. You receive a limited, non-exclusive license to use the platform per these terms.
                    </p>
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-planning-primary mb-2">Your Data</h3>
                    <p className="text-planning-text-light leading-relaxed">
                      You retain ownership of data you input (saved searches, reports, notes). You grant us a license to process this data to provide services and improve our AI.
                    </p>
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-planning-primary mb-2">Planning Data</h3>
                    <p className="text-planning-text-light leading-relaxed">
                      Planning application data is publicly available information sourced from UK planning authorities. AI-generated insights and analytics are our proprietary work product.
                    </p>
                  </div>
                </div>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-planning-primary mb-4">6. Disclaimers & Limitations</h2>
                <div className="bg-gray-50 rounded-2xl p-6 space-y-4">
                  <div>
                    <h3 className="text-lg font-bold text-planning-primary mb-2">No Warranties</h3>
                    <p className="text-planning-text-light leading-relaxed">
                      Planning Explorer is provided "AS IS" without warranties of any kind. We do not guarantee uninterrupted access, error-free operation, or data accuracy.
                    </p>
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-planning-primary mb-2">Not Professional Advice</h3>
                    <p className="text-planning-text-light leading-relaxed">
                      Our platform provides data and insights for informational purposes only. It does not constitute planning, legal, financial, or investment advice. Consult qualified professionals before making decisions.
                    </p>
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-planning-primary mb-2">AI Limitations</h3>
                    <p className="text-planning-text-light leading-relaxed">
                      AI predictions are probabilistic estimates based on historical data. Approval likelihood, timeline forecasts, and opportunity scores should be used as guidance, not guarantees.
                    </p>
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-planning-primary mb-2">Liability Limit</h3>
                    <p className="text-planning-text-light leading-relaxed">
                      Our liability is limited to the amount you paid in the 12 months prior to the claim. We are not liable for indirect, consequential, or punitive damages.
                    </p>
                  </div>
                </div>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-planning-primary mb-4">7. API Usage</h2>
                <div className="bg-gray-50 rounded-2xl p-6">
                  <p className="text-planning-text-light leading-relaxed mb-4">
                    API access is subject to:
                  </p>
                  <ul className="space-y-2 text-planning-text-light">
                    <li>• Rate limits based on your plan (Starter: limited, Professional/Enterprise: full)</li>
                    <li>• Authentication via API keys (keep confidential, rotate regularly)</li>
                    <li>• Compliance with these terms and our API documentation</li>
                    <li>• Usage monitoring and enforcement of fair use policies</li>
                  </ul>
                  <p className="text-planning-text-light leading-relaxed mt-4">
                    Excessive API usage may result in throttling or account suspension. Enterprise customers can request custom limits.
                  </p>
                </div>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-planning-primary mb-4">8. Privacy & Data Protection</h2>
                <div className="bg-gray-50 rounded-2xl p-6">
                  <p className="text-planning-text-light leading-relaxed">
                    Your privacy is important to us. Our data collection, use, and protection practices are detailed in our{' '}
                    <Link href="/privacy" className="text-planning-primary hover:underline font-semibold">
                      Privacy Policy
                    </Link>. By using Planning Explorer, you consent to data processing as described in that policy.
                  </p>
                </div>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-planning-primary mb-4">9. Modifications to Service</h2>
                <div className="bg-gray-50 rounded-2xl p-6">
                  <p className="text-planning-text-light leading-relaxed">
                    We may modify, suspend, or discontinue features at any time. We will provide reasonable notice of material changes. Continued use after changes constitutes acceptance of modified terms.
                  </p>
                </div>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-planning-primary mb-4">10. Governing Law</h2>
                <div className="bg-gray-50 rounded-2xl p-6">
                  <p className="text-planning-text-light leading-relaxed">
                    These terms are governed by the laws of England and Wales. Disputes will be resolved exclusively in UK courts. If you are a consumer in the EU, you retain rights under local consumer protection laws.
                  </p>
                </div>
              </section>

              <section>
                <div className="flex items-center gap-3 mb-4">
                  <Mail className="w-6 h-6 text-planning-primary" />
                  <h2 className="text-2xl font-bold text-planning-primary m-0">11. Contact</h2>
                </div>
                <div className="bg-gray-50 rounded-2xl p-6">
                  <p className="text-planning-text-light leading-relaxed mb-4">
                    For questions about these terms:
                  </p>
                  <p className="text-planning-text-light">
                    <strong>Email:</strong>{' '}
                    <a href="mailto:legal@planningexplorer.co.uk" className="text-planning-primary hover:underline">
                      legal@planningexplorer.co.uk
                    </a>
                  </p>
                  <p className="text-planning-text-light">
                    <strong>Address:</strong> Planning Explorer Ltd, 123 Planning Street, London, EC1A 1AA
                  </p>
                </div>
              </section>
            </div>

            <div className="mt-12 p-6 bg-orange-50 rounded-2xl">
              <p className="text-sm text-planning-text-light text-center">
                Related policies:{' '}
                <Link href="/privacy" className="text-planning-primary hover:underline font-semibold">
                  Privacy Policy
                </Link>{' '}
                |{' '}
                <Link href="/cookies" className="text-planning-primary hover:underline font-semibold">
                  Cookie Policy
                </Link>
              </p>
            </div>
          </div>
        </Container>
      </section>

      <Footer />
    </div>
  )
}
