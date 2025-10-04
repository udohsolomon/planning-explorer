'use client'

import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import { Footer } from '@/components/sections/Footer'
import { Sparkles, Mail, Phone, MapPin, Clock, Send, MessageSquare, HeadphonesIcon } from 'lucide-react'
import Link from 'next/link'

const contactMethods = [
  {
    icon: Mail,
    title: 'Email Us',
    description: 'Get in touch via email for general inquiries',
    contact: 'hello@planningexplorer.co.uk',
    action: 'Send Email',
    href: 'mailto:hello@planningexplorer.co.uk',
    color: 'bg-cyan-50'
  },
  {
    icon: Phone,
    title: 'Call Us',
    description: 'Speak directly with our team',
    contact: '+44 20 1234 5678',
    action: 'Call Now',
    href: 'tel:+442012345678',
    color: 'bg-orange-50'
  },
  {
    icon: HeadphonesIcon,
    title: 'Live Chat',
    description: 'Chat with our support team in real-time',
    contact: 'Available Mon-Fri, 9am-6pm GMT',
    action: 'Start Chat',
    href: '/support',
    color: 'bg-green-50'
  },
  {
    icon: MapPin,
    title: 'Visit Us',
    description: 'Meet us at our London office',
    contact: '123 Planning Street, London, EC1A 1AA',
    action: 'Get Directions',
    href: 'https://maps.google.com',
    color: 'bg-pink-50'
  }
]

const officeHours = [
  { day: 'Monday - Friday', hours: '9:00 AM - 6:00 PM GMT' },
  { day: 'Saturday', hours: '10:00 AM - 2:00 PM GMT' },
  { day: 'Sunday', hours: 'Closed' }
]

const departments = [
  {
    name: 'Sales Inquiries',
    email: 'sales@planningexplorer.co.uk',
    description: 'Questions about pricing, plans, and enterprise solutions',
    link: '/pricing'
  },
  {
    name: 'Technical Support',
    email: 'support@planningexplorer.co.uk',
    description: 'Help with your account, features, and troubleshooting',
    link: '/support'
  },
  {
    name: 'Partnership Opportunities',
    email: 'partners@planningexplorer.co.uk',
    description: 'Collaborate with us on strategic partnerships',
    link: '/partners'
  },
  {
    name: 'Media & Press',
    email: 'press@planningexplorer.co.uk',
    description: 'Media inquiries, press kits, and news',
    link: '/news'
  }
]

export default function ContactPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Hero Section */}
      <section className="relative z-20 bg-gradient-to-br from-planning-primary via-planning-primary to-planning-accent overflow-hidden">
        <div className="absolute inset-0 overflow-hidden">
          <div className="w-full h-full bg-cover bg-center bg-no-repeat opacity-25" style={{backgroundImage: `url('https://images.unsplash.com/photo-1423666639041-f56000c27a9a?w=1920&h=1080&fit=crop&crop=center')`}} />
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
                <span className="text-sm font-semibold text-white">Get In Touch</span>
              </div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold mb-4 leading-tight" style={{ color: '#FFFFFF' }}>
                <span className="block">We're Here to Help You</span>
                <span className="block">Unlock Planning Intelligence</span>
              </h1>
              <p className="text-xl md:text-2xl mb-8 text-white/90">
                Have questions? Our expert team is ready to assist you with AI-powered planning insights, technical support, and partnership opportunities.
              </p>
            </div>
          </Container>
        </div>
      </section>

      {/* Contact Methods */}
      <section className="py-24 bg-white relative -mt-20 z-30">
        <Container>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
            {contactMethods.map((method, index) => (
              <div
                key={index}
                className={`${method.color} rounded-3xl p-8 text-center hover:shadow-lg hover:scale-105 transition-all duration-300`}
              >
                <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-sm">
                  <method.icon className="w-8 h-8 text-planning-primary" />
                </div>
                <h3 className="text-xl font-bold text-planning-primary mb-2">{method.title}</h3>
                <p className="text-planning-text-light text-sm mb-4 leading-relaxed">{method.description}</p>
                <p className="text-planning-primary font-semibold text-sm mb-4">{method.contact}</p>
                <Link href={method.href}>
                  <Button size="sm" className="bg-planning-primary text-white hover:bg-planning-accent">
                    {method.action}
                  </Button>
                </Link>
              </div>
            ))}
          </div>
        </Container>
      </section>

      {/* Contact Form Section */}
      <section className="py-24 bg-gray-50">
        <Container>
          <div className="max-w-5xl mx-auto">
            <div className="text-center mb-16">
              <div className="inline-block px-4 py-2 bg-planning-button/10 rounded-full mb-6">
                <span className="text-planning-primary font-medium text-sm uppercase tracking-wider">
                  Send Us a Message
                </span>
              </div>
              <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-planning-primary mb-6">
                Drop Us a Line
              </h2>
              <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
                Fill out the form below and our team will get back to you within 24 hours
              </p>
            </div>

            <div className="bg-white rounded-3xl shadow-xl p-8 md:p-12">
              <form className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label htmlFor="firstName" className="block text-sm font-semibold text-planning-primary mb-2">
                      First Name *
                    </label>
                    <input
                      type="text"
                      id="firstName"
                      name="firstName"
                      required
                      className="w-full px-4 py-3 border-2 border-planning-border rounded-xl focus:border-planning-primary focus:outline-none transition-colors"
                      placeholder="John"
                    />
                  </div>
                  <div>
                    <label htmlFor="lastName" className="block text-sm font-semibold text-planning-primary mb-2">
                      Last Name *
                    </label>
                    <input
                      type="text"
                      id="lastName"
                      name="lastName"
                      required
                      className="w-full px-4 py-3 border-2 border-planning-border rounded-xl focus:border-planning-primary focus:outline-none transition-colors"
                      placeholder="Smith"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label htmlFor="email" className="block text-sm font-semibold text-planning-primary mb-2">
                      Email Address *
                    </label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      required
                      className="w-full px-4 py-3 border-2 border-planning-border rounded-xl focus:border-planning-primary focus:outline-none transition-colors"
                      placeholder="john.smith@example.com"
                    />
                  </div>
                  <div>
                    <label htmlFor="phone" className="block text-sm font-semibold text-planning-primary mb-2">
                      Phone Number
                    </label>
                    <input
                      type="tel"
                      id="phone"
                      name="phone"
                      className="w-full px-4 py-3 border-2 border-planning-border rounded-xl focus:border-planning-primary focus:outline-none transition-colors"
                      placeholder="+44 20 1234 5678"
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="company" className="block text-sm font-semibold text-planning-primary mb-2">
                    Company Name
                  </label>
                  <input
                    type="text"
                    id="company"
                    name="company"
                    className="w-full px-4 py-3 border-2 border-planning-border rounded-xl focus:border-planning-primary focus:outline-none transition-colors"
                    placeholder="Your Company Ltd"
                  />
                </div>

                <div>
                  <label htmlFor="subject" className="block text-sm font-semibold text-planning-primary mb-2">
                    Subject *
                  </label>
                  <select
                    id="subject"
                    name="subject"
                    required
                    className="w-full px-4 py-3 border-2 border-planning-border rounded-xl focus:border-planning-primary focus:outline-none transition-colors"
                  >
                    <option value="">Select a subject</option>
                    <option value="sales">Sales Inquiry</option>
                    <option value="support">Technical Support</option>
                    <option value="partnership">Partnership Opportunity</option>
                    <option value="media">Media & Press</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="message" className="block text-sm font-semibold text-planning-primary mb-2">
                    Message *
                  </label>
                  <textarea
                    id="message"
                    name="message"
                    required
                    rows={6}
                    className="w-full px-4 py-3 border-2 border-planning-border rounded-xl focus:border-planning-primary focus:outline-none transition-colors resize-none"
                    placeholder="Tell us how we can help you..."
                  />
                </div>

                <div className="flex items-start">
                  <input
                    type="checkbox"
                    id="privacy"
                    name="privacy"
                    required
                    className="mt-1 mr-3"
                  />
                  <label htmlFor="privacy" className="text-sm text-planning-text-light">
                    I agree to the{' '}
                    <Link href="/privacy" className="text-planning-primary hover:underline">
                      Privacy Policy
                    </Link>{' '}
                    and{' '}
                    <Link href="/terms" className="text-planning-primary hover:underline">
                      Terms of Service
                    </Link>
                  </label>
                </div>

                <Button
                  type="submit"
                  size="lg"
                  className="w-full bg-planning-primary text-white hover:bg-planning-accent"
                >
                  <Send className="w-5 h-5 mr-2" />
                  Send Message
                </Button>
              </form>
            </div>
          </div>
        </Container>
      </section>

      {/* Departments Section */}
      <section className="py-24 bg-white">
        <Container>
          <div className="max-w-5xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-planning-primary mb-4">
                Contact the Right Department
              </h2>
              <p className="text-xl text-planning-text-light">
                Get faster responses by reaching out to the appropriate team
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {departments.map((dept, index) => (
                <div
                  key={index}
                  className="bg-gray-50 rounded-3xl p-8 hover:shadow-lg transition-all duration-300 border-2 border-transparent hover:border-planning-primary/20"
                >
                  <h3 className="text-xl font-bold text-planning-primary mb-2">{dept.name}</h3>
                  <p className="text-planning-text-light text-sm mb-4 leading-relaxed">{dept.description}</p>
                  <p className="text-planning-primary font-semibold mb-4">{dept.email}</p>
                  <Link href={dept.link}>
                    <Button variant="outline" size="sm">
                      Learn More
                    </Button>
                  </Link>
                </div>
              ))}
            </div>
          </div>
        </Container>
      </section>

      {/* Office Hours */}
      <section className="py-24 bg-gray-50">
        <Container>
          <div className="max-w-3xl mx-auto text-center">
            <div className="bg-white rounded-3xl shadow-lg p-12">
              <div className="w-16 h-16 bg-planning-button/10 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Clock className="w-8 h-8 text-planning-primary" />
              </div>
              <h2 className="text-3xl md:text-4xl font-bold text-planning-primary mb-6">
                Office Hours
              </h2>
              <p className="text-planning-text-light mb-8">
                Our team is available during the following hours
              </p>
              <div className="space-y-4">
                {officeHours.map((schedule, index) => (
                  <div
                    key={index}
                    className="flex justify-between items-center py-4 border-b border-gray-100 last:border-0"
                  >
                    <span className="font-semibold text-planning-primary">{schedule.day}</span>
                    <span className="text-planning-text-light">{schedule.hours}</span>
                  </div>
                ))}
              </div>
              <div className="mt-8 pt-8 border-t border-gray-100">
                <p className="text-sm text-planning-text-light">
                  For urgent support outside business hours, visit our{' '}
                  <Link href="/help" className="text-planning-primary hover:underline font-semibold">
                    Help Center
                  </Link>{' '}
                  or email{' '}
                  <a href="mailto:urgent@planningexplorer.co.uk" className="text-planning-primary hover:underline font-semibold">
                    urgent@planningexplorer.co.uk
                  </a>
                </p>
              </div>
            </div>
          </div>
        </Container>
      </section>

      {/* Quick Links CTA */}
      <section className="py-24 bg-white">
        <Container>
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-planning-primary mb-6">
              Looking for Something Specific?
            </h2>
            <p className="text-xl text-planning-text-light mb-8">
              Explore our resources to find the information you need
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Link href="/help">
                <div className="bg-cyan-50 rounded-2xl p-6 hover:shadow-lg transition-all cursor-pointer">
                  <MessageSquare className="w-12 h-12 text-planning-primary mx-auto mb-4" />
                  <h3 className="font-bold text-planning-primary mb-2">Help Center</h3>
                  <p className="text-sm text-planning-text-light">Browse FAQs and guides</p>
                </div>
              </Link>
              <Link href="/tutorials">
                <div className="bg-orange-50 rounded-2xl p-6 hover:shadow-lg transition-all cursor-pointer">
                  <Sparkles className="w-12 h-12 text-planning-primary mx-auto mb-4" />
                  <h3 className="font-bold text-planning-primary mb-2">Tutorials</h3>
                  <p className="text-sm text-planning-text-light">Learn how to use features</p>
                </div>
              </Link>
              <Link href="/pricing">
                <div className="bg-green-50 rounded-2xl p-6 hover:shadow-lg transition-all cursor-pointer">
                  <Send className="w-12 h-12 text-planning-primary mx-auto mb-4" />
                  <h3 className="font-bold text-planning-primary mb-2">Pricing</h3>
                  <p className="text-sm text-planning-text-light">View plans and pricing</p>
                </div>
              </Link>
            </div>
          </div>
        </Container>
      </section>

      <Footer />
    </div>
  )
}
