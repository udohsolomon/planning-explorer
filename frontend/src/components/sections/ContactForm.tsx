'use client'

import { useState } from 'react'
import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import { Mail, Phone, MapPin, Send, CheckCircle } from 'lucide-react'

interface FormData {
  firstName: string
  lastName: string
  email: string
  company: string
  phone: string
  service: string
  message: string
}

const services = [
  'Planning Intelligence',
  'Market Analysis',
  'Risk Assessment',
  'Custom Solutions',
  'API Integration',
  'Enterprise Package'
]

export function ContactForm() {
  const [formData, setFormData] = useState<FormData>({
    firstName: '',
    lastName: '',
    email: '',
    company: '',
    phone: '',
    service: '',
    message: ''
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    // Simulate form submission
    await new Promise(resolve => setTimeout(resolve, 2000))

    setIsSubmitting(false)
    setIsSubmitted(true)

    // Reset form after 3 seconds
    setTimeout(() => {
      setIsSubmitted(false)
      setFormData({
        firstName: '',
        lastName: '',
        email: '',
        company: '',
        phone: '',
        service: '',
        message: ''
      })
    }, 3000)
  }

  if (isSubmitted) {
    return (
      <section className="py-24 bg-white">
        <Container>
          <div className="max-w-2xl mx-auto text-center">
            <div className="w-20 h-20 bg-planning-bright/10 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle className="w-10 h-10 text-planning-bright" />
            </div>
            <h2 className="text-3xl font-heading font-bold text-planning-primary mb-4">
              Thank You!
            </h2>
            <p className="text-lg text-planning-text-light mb-8">
              We've received your message and will get back to you within 24 hours.
            </p>
            <div className="inline-flex items-center space-x-2 bg-planning-bright/10 px-4 py-2 rounded-full">
              <div className="w-2 h-2 bg-planning-bright rounded-full animate-pulse" />
              <span className="text-planning-primary text-sm font-medium">
                Expect a response soon
              </span>
            </div>
          </div>
        </Container>
      </section>
    )
  }

  return (
    <section className="py-24 bg-white">
      <Container>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-start">
          {/* Contact Information */}
          <div>
            <div className="inline-block px-4 py-2 bg-planning-button/10 rounded-full mb-6">
              <span className="text-planning-primary font-medium text-sm uppercase tracking-wider">
                Get In Touch
              </span>
            </div>

            <h2 className="text-3xl md:text-4xl lg:text-5xl font-heading font-bold text-planning-primary mb-6">
              Ready to Get Started?
            </h2>

            <p className="text-lg text-planning-text-light mb-8 leading-relaxed">
              Have questions about Planning Explorer? Our team is here to help you find the perfect solution for your planning intelligence needs.
            </p>

            {/* Contact Details */}
            <div className="space-y-6 mb-8">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-planning-primary/10 rounded-lg flex items-center justify-center">
                  <Mail className="w-6 h-6 text-planning-primary" />
                </div>
                <div>
                  <div className="font-semibold text-planning-primary">Email</div>
                  <div className="text-planning-text-light">hello@planningexplorer.ai</div>
                </div>
              </div>

              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-planning-primary/10 rounded-lg flex items-center justify-center">
                  <Phone className="w-6 h-6 text-planning-primary" />
                </div>
                <div>
                  <div className="font-semibold text-planning-primary">Phone</div>
                  <div className="text-planning-text-light">0800 123 4567</div>
                </div>
              </div>

              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-planning-primary/10 rounded-lg flex items-center justify-center">
                  <MapPin className="w-6 h-6 text-planning-primary" />
                </div>
                <div>
                  <div className="font-semibold text-planning-primary">Office</div>
                  <div className="text-planning-text-light">
                    123 Planning Street<br />
                    London, SW1A 1AA
                  </div>
                </div>
              </div>
            </div>

            {/* Business Hours */}
            <div className="bg-gray-50 rounded-xl p-6">
              <h3 className="font-semibold text-planning-primary mb-4">Business Hours</h3>
              <div className="space-y-2 text-sm text-planning-text-light">
                <div className="flex justify-between">
                  <span>Monday - Friday</span>
                  <span>9:00 AM - 6:00 PM</span>
                </div>
                <div className="flex justify-between">
                  <span>Saturday</span>
                  <span>10:00 AM - 4:00 PM</span>
                </div>
                <div className="flex justify-between">
                  <span>Sunday</span>
                  <span>Closed</span>
                </div>
              </div>
            </div>
          </div>

          {/* Contact Form */}
          <div className="bg-gray-50 rounded-2xl p-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Name Fields */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="firstName" className="block text-sm font-medium text-planning-primary mb-2">
                    First Name *
                  </label>
                  <input
                    type="text"
                    id="firstName"
                    name="firstName"
                    value={formData.firstName}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 border border-planning-border rounded-lg focus:ring-2 focus:ring-planning-primary focus:border-planning-primary transition-colors"
                    placeholder="John"
                  />
                </div>
                <div>
                  <label htmlFor="lastName" className="block text-sm font-medium text-planning-primary mb-2">
                    Last Name *
                  </label>
                  <input
                    type="text"
                    id="lastName"
                    name="lastName"
                    value={formData.lastName}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 border border-planning-border rounded-lg focus:ring-2 focus:ring-planning-primary focus:border-planning-primary transition-colors"
                    placeholder="Smith"
                  />
                </div>
              </div>

              {/* Email */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-planning-primary mb-2">
                  Email Address *
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-3 border border-planning-border rounded-lg focus:ring-2 focus:ring-planning-primary focus:border-planning-primary transition-colors"
                  placeholder="john.smith@company.com"
                />
              </div>

              {/* Company and Phone */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="company" className="block text-sm font-medium text-planning-primary mb-2">
                    Company
                  </label>
                  <input
                    type="text"
                    id="company"
                    name="company"
                    value={formData.company}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-planning-border rounded-lg focus:ring-2 focus:ring-planning-primary focus:border-planning-primary transition-colors"
                    placeholder="Your Company Ltd"
                  />
                </div>
                <div>
                  <label htmlFor="phone" className="block text-sm font-medium text-planning-primary mb-2">
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    id="phone"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-planning-border rounded-lg focus:ring-2 focus:ring-planning-primary focus:border-planning-primary transition-colors"
                    placeholder="+44 7XXX XXXXXX"
                  />
                </div>
              </div>

              {/* Service Interest */}
              <div>
                <label htmlFor="service" className="block text-sm font-medium text-planning-primary mb-2">
                  Service Interest
                </label>
                <select
                  id="service"
                  name="service"
                  value={formData.service}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-planning-border rounded-lg focus:ring-2 focus:ring-planning-primary focus:border-planning-primary transition-colors"
                >
                  <option value="">Select a service...</option>
                  {services.map((service) => (
                    <option key={service} value={service}>
                      {service}
                    </option>
                  ))}
                </select>
              </div>

              {/* Message */}
              <div>
                <label htmlFor="message" className="block text-sm font-medium text-planning-primary mb-2">
                  Message *
                </label>
                <textarea
                  id="message"
                  name="message"
                  value={formData.message}
                  onChange={handleInputChange}
                  required
                  rows={4}
                  className="w-full px-4 py-3 border border-planning-border rounded-lg focus:ring-2 focus:ring-planning-primary focus:border-planning-primary transition-colors resize-none"
                  placeholder="Tell us about your planning intelligence needs..."
                />
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                disabled={isSubmitting}
                className="w-full"
                size="lg"
              >
                {isSubmitting ? (
                  <>
                    <div className="w-4 h-4 border-2 border-planning-primary border-t-transparent rounded-full animate-spin mr-2" />
                    Sending...
                  </>
                ) : (
                  <>
                    Send Message
                    <Send className="w-4 h-4 ml-2" />
                  </>
                )}
              </Button>

              {/* Privacy Notice */}
              <p className="text-xs text-planning-text-light text-center">
                By submitting this form, you agree to our privacy policy and terms of service.
                We'll only use your information to respond to your inquiry.
              </p>
            </form>
          </div>
        </div>
      </Container>
    </section>
  )
}