'use client'

import { Container } from '@/components/ui/Container'
import { Footer } from '@/components/sections/Footer'
import { Sparkles, Shield, Lock, Eye, Server, FileText, Mail } from 'lucide-react'
import Link from 'next/link'

export default function PrivacyPage() {
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
                <span className="block">Privacy Policy</span>
                <span className="block">& Data Protection</span>
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
            <div className="bg-cyan-50 rounded-3xl p-8 mb-12">
              <div className="flex items-start gap-4">
                <Shield className="w-8 h-8 text-planning-primary flex-shrink-0 mt-1" />
                <div>
                  <h2 className="text-2xl font-bold text-planning-primary mb-3">Our Commitment to Your Privacy</h2>
                  <p className="text-planning-text-light leading-relaxed">
                    At Planning Explorer, we take your privacy seriously. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our AI-powered planning intelligence platform. We are committed to protecting your data and maintaining transparency about our practices.
                  </p>
                </div>
              </div>
            </div>

            <div className="prose prose-lg max-w-none space-y-12">
              <section>
                <div className="flex items-center gap-3 mb-4">
                  <FileText className="w-6 h-6 text-planning-primary" />
                  <h2 className="text-2xl font-bold text-planning-primary m-0">1. Information We Collect</h2>
                </div>
                <div className="bg-gray-50 rounded-2xl p-6 space-y-4">
                  <div>
                    <h3 className="text-lg font-bold text-planning-primary mb-2">Account Information</h3>
                    <p className="text-planning-text-light leading-relaxed">
                      When you create an account, we collect your name, email address, company name, and billing information. This information is necessary to provide you with access to our services and process payments.
                    </p>
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-planning-primary mb-2">Usage Data</h3>
                    <p className="text-planning-text-light leading-relaxed">
                      We automatically collect information about how you use Planning Explorer, including search queries, saved searches, reports generated, features accessed, and pages viewed. This helps us improve our AI models and user experience.
                    </p>
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-planning-primary mb-2">Technical Information</h3>
                    <p className="text-planning-text-light leading-relaxed">
                      We collect IP addresses, browser type, device information, operating system, and cookies to ensure platform security, prevent fraud, and optimize performance.
                    </p>
                  </div>
                </div>
              </section>

              <section>
                <div className="flex items-center gap-3 mb-4">
                  <Eye className="w-6 h-6 text-planning-primary" />
                  <h2 className="text-2xl font-bold text-planning-primary m-0">2. How We Use Your Information</h2>
                </div>
                <div className="bg-gray-50 rounded-2xl p-6">
                  <ul className="space-y-3 text-planning-text-light">
                    <li className="flex items-start">
                      <span className="mr-3 text-planning-primary font-bold">•</span>
                      <span><strong>Provide Services:</strong> To operate Planning Explorer, process searches, generate AI insights, and deliver requested features</span>
                    </li>
                    <li className="flex items-start">
                      <span className="mr-3 text-planning-primary font-bold">•</span>
                      <span><strong>Improve AI Models:</strong> To train and enhance our machine learning models, semantic search, and predictive analytics</span>
                    </li>
                    <li className="flex items-start">
                      <span className="mr-3 text-planning-primary font-bold">•</span>
                      <span><strong>Personalization:</strong> To customize your experience, recommend relevant applications, and optimize search results</span>
                    </li>
                    <li className="flex items-start">
                      <span className="mr-3 text-planning-primary font-bold">•</span>
                      <span><strong>Communication:</strong> To send service updates, feature announcements, and support responses</span>
                    </li>
                    <li className="flex items-start">
                      <span className="mr-3 text-planning-primary font-bold">•</span>
                      <span><strong>Security:</strong> To detect fraud, prevent abuse, and maintain platform integrity</span>
                    </li>
                    <li className="flex items-start">
                      <span className="mr-3 text-planning-primary font-bold">•</span>
                      <span><strong>Analytics:</strong> To understand usage patterns, measure performance, and guide product development</span>
                    </li>
                  </ul>
                </div>
              </section>

              <section>
                <div className="flex items-center gap-3 mb-4">
                  <Server className="w-6 h-6 text-planning-primary" />
                  <h2 className="text-2xl font-bold text-planning-primary m-0">3. Data Storage & Security</h2>
                </div>
                <div className="bg-gray-50 rounded-2xl p-6 space-y-4">
                  <p className="text-planning-text-light leading-relaxed">
                    We implement industry-standard security measures to protect your data:
                  </p>
                  <ul className="space-y-2 text-planning-text-light">
                    <li className="flex items-start">
                      <Lock className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0 text-planning-primary" />
                      <span><strong>Encryption:</strong> All data is encrypted in transit (TLS 1.3) and at rest (AES-256)</span>
                    </li>
                    <li className="flex items-start">
                      <Lock className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0 text-planning-primary" />
                      <span><strong>Access Controls:</strong> Strict role-based access controls and multi-factor authentication</span>
                    </li>
                    <li className="flex items-start">
                      <Lock className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0 text-planning-primary" />
                      <span><strong>Monitoring:</strong> 24/7 security monitoring and regular penetration testing</span>
                    </li>
                    <li className="flex items-start">
                      <Lock className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0 text-planning-primary" />
                      <span><strong>Compliance:</strong> SOC 2 Type II certified, GDPR and UK GDPR compliant</span>
                    </li>
                  </ul>
                  <p className="text-planning-text-light leading-relaxed">
                    Your data is stored on secure servers within the UK and EU, in compliance with UK data protection laws.
                  </p>
                </div>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-planning-primary mb-4">4. Data Sharing & Third Parties</h2>
                <div className="bg-gray-50 rounded-2xl p-6">
                  <p className="text-planning-text-light leading-relaxed mb-4">
                    We do not sell your personal data. We may share data with:
                  </p>
                  <ul className="space-y-3 text-planning-text-light">
                    <li><strong>Service Providers:</strong> Payment processors, cloud hosting, email services (under strict data protection agreements)</li>
                    <li><strong>AI Partners:</strong> OpenAI and Anthropic for AI processing (data is anonymized where possible)</li>
                    <li><strong>Legal Requirements:</strong> When required by law, court order, or to protect our rights</li>
                  </ul>
                </div>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-planning-primary mb-4">5. Your Rights (GDPR)</h2>
                <div className="bg-gray-50 rounded-2xl p-6">
                  <p className="text-planning-text-light leading-relaxed mb-4">
                    Under UK GDPR, you have the following rights:
                  </p>
                  <ul className="space-y-2 text-planning-text-light">
                    <li><strong>Access:</strong> Request a copy of your personal data</li>
                    <li><strong>Rectification:</strong> Correct inaccurate or incomplete data</li>
                    <li><strong>Erasure:</strong> Request deletion of your data ("right to be forgotten")</li>
                    <li><strong>Portability:</strong> Receive your data in a machine-readable format</li>
                    <li><strong>Objection:</strong> Object to data processing for legitimate interests</li>
                    <li><strong>Restriction:</strong> Request limitation of data processing</li>
                  </ul>
                  <p className="text-planning-text-light leading-relaxed mt-4">
                    To exercise these rights, contact us at{' '}
                    <a href="mailto:privacy@planningexplorer.co.uk" className="text-planning-primary hover:underline font-semibold">
                      privacy@planningexplorer.co.uk
                    </a>
                  </p>
                </div>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-planning-primary mb-4">6. Cookies & Tracking</h2>
                <div className="bg-gray-50 rounded-2xl p-6">
                  <p className="text-planning-text-light leading-relaxed">
                    We use essential cookies to operate our platform and optional analytics cookies to improve user experience. You can control cookie preferences in your browser settings. For more details, see our{' '}
                    <Link href="/cookies" className="text-planning-primary hover:underline font-semibold">
                      Cookie Policy
                    </Link>.
                  </p>
                </div>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-planning-primary mb-4">7. Data Retention</h2>
                <div className="bg-gray-50 rounded-2xl p-6">
                  <p className="text-planning-text-light leading-relaxed">
                    We retain your data for as long as your account is active or as needed to provide services. After account deletion, we retain anonymized usage data for analytics and AI model training. Billing records are retained for 7 years as required by UK tax law.
                  </p>
                </div>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-planning-primary mb-4">8. Children's Privacy</h2>
                <div className="bg-gray-50 rounded-2xl p-6">
                  <p className="text-planning-text-light leading-relaxed">
                    Planning Explorer is not intended for users under 18. We do not knowingly collect data from children. If you believe a child has provided us with personal information, please contact us immediately.
                  </p>
                </div>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-planning-primary mb-4">9. Changes to This Policy</h2>
                <div className="bg-gray-50 rounded-2xl p-6">
                  <p className="text-planning-text-light leading-relaxed">
                    We may update this Privacy Policy periodically. We will notify you of material changes via email or platform notification. Continued use of Planning Explorer after changes constitutes acceptance of the updated policy.
                  </p>
                </div>
              </section>

              <section>
                <div className="flex items-center gap-3 mb-4">
                  <Mail className="w-6 h-6 text-planning-primary" />
                  <h2 className="text-2xl font-bold text-planning-primary m-0">10. Contact Us</h2>
                </div>
                <div className="bg-gray-50 rounded-2xl p-6">
                  <p className="text-planning-text-light leading-relaxed mb-4">
                    For privacy questions, data requests, or concerns:
                  </p>
                  <p className="text-planning-text-light">
                    <strong>Email:</strong>{' '}
                    <a href="mailto:privacy@planningexplorer.co.uk" className="text-planning-primary hover:underline">
                      privacy@planningexplorer.co.uk
                    </a>
                  </p>
                  <p className="text-planning-text-light">
                    <strong>Data Protection Officer:</strong> Planning Explorer Ltd, 123 Planning Street, London, EC1A 1AA
                  </p>
                  <p className="text-planning-text-light mt-4">
                    You also have the right to lodge a complaint with the UK Information Commissioner's Office (ICO):{' '}
                    <a href="https://ico.org.uk" target="_blank" rel="noopener noreferrer" className="text-planning-primary hover:underline">
                      ico.org.uk
                    </a>
                  </p>
                </div>
              </section>
            </div>

            <div className="mt-12 p-6 bg-cyan-50 rounded-2xl">
              <p className="text-sm text-planning-text-light text-center">
                Related policies:{' '}
                <Link href="/terms" className="text-planning-primary hover:underline font-semibold">
                  Terms of Service
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
