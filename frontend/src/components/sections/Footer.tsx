'use client'

import Link from 'next/link'
import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import { Facebook, Instagram, Twitter, Youtube } from 'lucide-react'

const footerLinks = {
  product: [
    { label: 'Overview', href: '/product/overview' },
    { label: 'Features', href: '/product/features' },
    { label: 'Solutions', href: '/product/solutions' },
    { label: 'Tutorials', href: '/tutorials' },
    { label: 'Pricing', href: '/pricing' }
  ],
  company: [
    { label: 'About Us', href: '/about' },
    { label: 'Careers', href: '/careers' },
    { label: 'News', href: '/news' },
    { label: 'Media Kit', href: '/media-kit' },
    { label: 'Contact', href: '/contact' }
  ],
  resources: [
    { label: 'Blog', href: '/blog' },
    { label: 'Help Center', href: '/help' },
    { label: 'Tutorials', href: '/tutorials' },
    { label: 'Support', href: '/support' },
    { label: 'Services', href: '/services' }
  ],
  collaborate: [
    { label: 'Partners', href: '/partners' },
    { label: 'Partners Program', href: '/partners/program' },
    { label: 'Affiliate Program', href: '/affiliate' },
    { label: 'Community', href: '/community' },
    { label: 'HR Partner Program', href: '/hr-partners' }
  ]
}

export function Footer() {
  return (
    <>
      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-r from-planning-accent to-planning-bright relative overflow-hidden">
        {/* Background Image */}
        <div className="absolute inset-0">
          <img
            src="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1200&h=600&fit=crop"
            alt="UK cityscape with development sites"
            className="w-full h-full object-cover opacity-30"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-planning-accent/90 to-planning-bright/90"></div>
        </div>

        <Container className="relative z-10">
          <div className="max-w-3xl">
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-6 leading-tight">
              Ready to Unlock AI-Powered Planning Intelligence?
            </h2>
            <p className="text-lg text-white/90 mb-8 leading-relaxed max-w-2xl">
              Start your free trial of Planning Explorer today. Get instant access to 336K+ UK planning applications, AI-powered insights, and predictive analytics. No credit card required.
            </p>
            <Button
              size="lg"
              className="bg-planning-button hover:bg-planning-button/90 text-white font-semibold px-8 py-4"
            >
              Start Free Trial - Unlock AI Insights →
            </Button>
          </div>
        </Container>
      </section>

      {/* Main Footer */}
      <footer className="bg-planning-primary text-white">
        <Container>
          <div className="py-16">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-8">
              {/* Logo and Description */}
              <div className="lg:col-span-2">
                <div className="flex items-center space-x-2 mb-6">
                  <div className="w-8 h-8 bg-white rounded-md flex items-center justify-center">
                    <span className="text-planning-primary font-bold text-sm">PE</span>
                  </div>
                  <span className="text-xl font-bold">Planning Explorer</span>
                </div>
                <p className="text-white/80 leading-relaxed mb-6 max-w-sm">
                  Revolutionising property intelligence by transforming weeks of manual research into minutes of AI-powered insights for UK property professionals.
                </p>

                {/* Social Links */}
                <div className="flex space-x-4">
                  <Link
                    href="#"
                    className="w-10 h-10 bg-white/10 rounded-full flex items-center justify-center hover:bg-white/20 transition-colors"
                  >
                    <Facebook className="w-5 h-5" />
                  </Link>
                  <Link
                    href="#"
                    className="w-10 h-10 bg-white/10 rounded-full flex items-center justify-center hover:bg-white/20 transition-colors"
                  >
                    <Instagram className="w-5 h-5" />
                  </Link>
                  <Link
                    href="#"
                    className="w-10 h-10 bg-white/10 rounded-full flex items-center justify-center hover:bg-white/20 transition-colors"
                  >
                    <Twitter className="w-5 h-5" />
                  </Link>
                  <Link
                    href="#"
                    className="w-10 h-10 bg-white/10 rounded-full flex items-center justify-center hover:bg-white/20 transition-colors"
                  >
                    <Youtube className="w-5 h-5" />
                  </Link>
                </div>
              </div>

              {/* Product */}
              <div>
                <h3 className="font-semibold text-lg mb-4 uppercase tracking-wider text-sm">
                  PRODUCT
                </h3>
                <ul className="space-y-3">
                  {footerLinks.product.map((link, index) => (
                    <li key={index}>
                      <Link
                        href={link.href}
                        className="text-white/80 hover:text-white transition-colors"
                      >
                        {link.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Company */}
              <div>
                <h3 className="font-semibold text-lg mb-4 uppercase tracking-wider text-sm">
                  COMPANY
                </h3>
                <ul className="space-y-3">
                  {footerLinks.company.map((link, index) => (
                    <li key={index}>
                      <Link
                        href={link.href}
                        className="text-white/80 hover:text-white transition-colors"
                      >
                        {link.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Resources */}
              <div>
                <h3 className="font-semibold text-lg mb-4 uppercase tracking-wider text-sm">
                  RESOURCES
                </h3>
                <ul className="space-y-3">
                  {footerLinks.resources.map((link, index) => (
                    <li key={index}>
                      <Link
                        href={link.href}
                        className="text-white/80 hover:text-white transition-colors"
                      >
                        {link.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Collaborate */}
              <div>
                <h3 className="font-semibold text-lg mb-4 uppercase tracking-wider text-sm">
                  COLLABORATE
                </h3>
                <ul className="space-y-3">
                  {footerLinks.collaborate.map((link, index) => (
                    <li key={index}>
                      <Link
                        href={link.href}
                        className="text-white/80 hover:text-white transition-colors"
                      >
                        {link.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Bottom Section */}
          <div className="border-t border-white/20 py-8">
            <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
              <div className="text-white/60 text-sm">
                © 2025 Planning Explorer. All rights reserved. AI-Powered Planning Intelligence.
              </div>
              <div className="flex space-x-6 text-sm">
                <Link href="/privacy" className="text-white/60 hover:text-white transition-colors">
                  Privacy Policy
                </Link>
                <Link href="/terms" className="text-white/60 hover:text-white transition-colors">
                  Terms of Service
                </Link>
                <Link href="/cookies" className="text-white/60 hover:text-white transition-colors">
                  Cookie Policy
                </Link>
              </div>
            </div>
          </div>
        </Container>
      </footer>
    </>
  )
}