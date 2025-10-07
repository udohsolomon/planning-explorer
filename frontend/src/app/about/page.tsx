'use client'

import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import { Footer } from '@/components/sections/Footer'
import { Sparkles, Target, Lightbulb, Users, TrendingUp, Award, Shield, Zap, Globe, Heart } from 'lucide-react'
import Link from 'next/link'

const mission = [
  {
    icon: Target,
    title: 'Our Mission',
    description: 'To democratize planning intelligence by making comprehensive UK planning data accessible, actionable, and intelligent for every property professional.',
    color: 'bg-cyan-50'
  },
  {
    icon: Lightbulb,
    title: 'Our Vision',
    description: 'To become the UK\'s most trusted AI-powered planning intelligence platform, transforming how property professionals discover, analyze, and act on development opportunities.',
    color: 'bg-orange-50'
  },
  {
    icon: Heart,
    title: 'Our Values',
    description: 'We believe in transparency, innovation, and customer success. Every decision we make is guided by our commitment to delivering exceptional value and building long-term partnerships.',
    color: 'bg-pink-50'
  }
]

const story = [
  {
    year: '2023',
    title: 'The Beginning',
    description: 'Founded by property and AI experts who experienced firsthand the frustration of manual planning research. We saw an opportunity to revolutionize the industry with AI.',
    color: 'bg-green-50'
  },
  {
    year: '2024',
    title: 'Product Launch',
    description: 'Launched Planning Explorer with 336K+ UK planning applications, AI-powered semantic search, and predictive analytics. Early adopters saw 90% time savings.',
    color: 'bg-cyan-50'
  },
  {
    year: '2025',
    title: 'Rapid Growth',
    description: 'Serving hundreds of property professionals across the UK. Continuously enhancing our AI models and expanding our data coverage to provide unmatched planning intelligence.',
    color: 'bg-orange-50'
  }
]

const values = [
  {
    icon: Zap,
    title: 'Innovation First',
    description: 'We leverage cutting-edge AI and machine learning to solve real problems for property professionals.',
    color: 'bg-yellow-50'
  },
  {
    icon: Shield,
    title: 'Data Security',
    description: 'Your data is protected with enterprise-grade security. We are committed to maintaining the highest standards of privacy and compliance.',
    color: 'bg-cyan-50'
  },
  {
    icon: Users,
    title: 'Customer Success',
    description: 'Your success is our success. We provide dedicated support, training, and resources to help you maximize value from our platform.',
    color: 'bg-pink-50'
  },
  {
    icon: Globe,
    title: 'Transparency',
    description: 'We believe in open communication, honest pricing, and clear data sourcing. No hidden fees, no surprises.',
    color: 'bg-green-50'
  }
]

const team = [
  {
    name: 'Leadership Team',
    description: 'Experienced property and technology leaders with deep expertise in AI, data science, and UK planning systems.',
    icon: Award
  },
  {
    name: 'Engineering Team',
    description: 'World-class engineers and data scientists building cutting-edge AI models and scalable infrastructure.',
    icon: Zap
  },
  {
    name: 'Customer Success',
    description: 'Dedicated support specialists with planning industry knowledge, ensuring you get maximum value from our platform.',
    icon: Users
  }
]

const achievements = [
  {
    metric: '336K+',
    label: 'Planning Applications Indexed',
    description: 'Comprehensive UK coverage'
  },
  {
    metric: '90%',
    label: 'Time Savings',
    description: 'Reported by customers'
  },
  {
    metric: '95%+',
    label: 'Customer Satisfaction',
    description: 'Based on user feedback'
  },
  {
    metric: '24/7',
    label: 'AI Processing',
    description: 'Real-time data updates'
  }
]

export default function AboutPage() {
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
                <span className="text-sm font-semibold text-white">About Planning Explorer</span>
              </div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold mb-4 leading-tight" style={{ color: '#FFFFFF' }}>
                <span className="block">Revolutionizing Property Intelligence</span>
                <span className="block">with AI-Powered Insights</span>
              </h1>
              <p className="text-xl md:text-2xl mb-8 text-white/90">
                We're on a mission to transform weeks of manual planning research into minutes of AI-powered insights for UK property professionals.
              </p>
            </div>
          </Container>
        </div>
      </section>

      {/* Mission, Vision, Values */}
      <section className="py-24 bg-white relative -mt-20 z-30">
        <Container>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {mission.map((item, index) => (
              <div
                key={index}
                className={`${item.color} rounded-3xl p-8 hover:shadow-lg hover:scale-105 transition-all duration-300`}
              >
                <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-sm">
                  <item.icon className="w-8 h-8 text-planning-primary" />
                </div>
                <h3 className="text-2xl font-bold text-planning-primary mb-4 text-center">{item.title}</h3>
                <p className="text-planning-text-light leading-relaxed text-center">{item.description}</p>
              </div>
            ))}
          </div>
        </Container>
      </section>

      {/* Our Story */}
      <section className="py-24 bg-gray-50">
        <Container>
          <div className="text-center mb-16">
            <div className="inline-block px-4 py-2 bg-planning-button/10 rounded-full mb-6">
              <span className="text-planning-primary font-medium text-sm uppercase tracking-wider">
                Our Journey
              </span>
            </div>
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-planning-primary mb-6">
              The Story Behind Planning Explorer
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              From frustration to innovation - how we built the UK's first AI-native planning intelligence platform
            </p>
          </div>

          <div className="max-w-5xl mx-auto space-y-8">
            {story.map((milestone, index) => (
              <div
                key={index}
                className={`${milestone.color} rounded-3xl p-8 md:p-12 hover:shadow-lg transition-all duration-300`}
              >
                <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
                  <div className="w-24 h-24 bg-white rounded-2xl flex items-center justify-center flex-shrink-0 shadow-sm">
                    <span className="text-3xl font-bold text-planning-primary">{milestone.year}</span>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-2xl md:text-3xl font-bold text-planning-primary mb-3">{milestone.title}</h3>
                    <p className="text-planning-text-light leading-relaxed text-lg">{milestone.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Container>
      </section>

      {/* Core Values */}
      <section className="py-24 bg-white">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-planning-primary mb-6">
              Our Core Values
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              The principles that guide everything we do
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
            {values.map((value, index) => (
              <div
                key={index}
                className={`${value.color} rounded-3xl p-8 text-center hover:shadow-lg hover:scale-105 transition-all duration-300`}
              >
                <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-sm">
                  <value.icon className="w-8 h-8 text-planning-primary" />
                </div>
                <h3 className="text-xl font-bold text-planning-primary mb-3">{value.title}</h3>
                <p className="text-planning-text-light text-sm leading-relaxed">{value.description}</p>
              </div>
            ))}
          </div>
        </Container>
      </section>

      {/* Achievements */}
      <section className="py-24 bg-gray-50">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-planning-primary mb-4">
              Our Impact in Numbers
            </h2>
            <p className="text-xl text-planning-text-light">
              Real results driving the UK property industry forward
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
            {achievements.map((achievement, index) => (
              <div
                key={index}
                className="bg-white rounded-3xl p-8 text-center hover:shadow-lg transition-all duration-300 border-2 border-planning-border"
              >
                <div className="text-5xl md:text-6xl font-bold text-planning-primary mb-3">
                  {achievement.metric}
                </div>
                <div className="text-lg font-semibold text-planning-primary mb-2">
                  {achievement.label}
                </div>
                <p className="text-sm text-planning-text-light">{achievement.description}</p>
              </div>
            ))}
          </div>
        </Container>
      </section>

      {/* Team Section */}
      <section className="py-24 bg-white">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-planning-primary mb-6">
              Meet Our Team
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              Passionate experts committed to your success
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {team.map((dept, index) => (
              <div
                key={index}
                className="bg-gradient-to-br from-planning-primary to-planning-accent rounded-3xl p-8 text-white text-center hover:shadow-xl hover:scale-105 transition-all duration-300"
              >
                <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <dept.icon className="w-8 h-8 text-planning-primary" />
                </div>
                <h3 className="text-xl font-bold mb-4">{dept.name}</h3>
                <p className="text-white/90 leading-relaxed">{dept.description}</p>
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <p className="text-planning-text-light mb-6">
              Interested in joining our team?
            </p>
            <Link href="/careers">
              <Button size="lg" className="bg-planning-primary text-white hover:bg-planning-accent">
                View Open Positions
              </Button>
            </Link>
          </div>
        </Container>
      </section>

      {/* Why Choose Us */}
      <section className="py-24 bg-gray-50">
        <Container>
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-planning-primary mb-6">
                Why Property Professionals Choose Us
              </h2>
            </div>

            <div className="bg-white rounded-3xl shadow-xl p-8 md:p-12 space-y-8">
              <div className="flex items-start gap-6">
                <div className="w-12 h-12 bg-cyan-50 rounded-xl flex items-center justify-center flex-shrink-0">
                  <TrendingUp className="w-6 h-6 text-planning-primary" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-planning-primary mb-2">AI-Powered Intelligence</h3>
                  <p className="text-planning-text-light leading-relaxed">
                    Our advanced AI models analyze planning data to surface insights you'd never find manually. Predictive analytics, approval likelihood, and trend forecasting give you a competitive edge.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-6">
                <div className="w-12 h-12 bg-orange-50 rounded-xl flex items-center justify-center flex-shrink-0">
                  <Shield className="w-6 h-6 text-planning-primary" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-planning-primary mb-2">Trusted Data Sources</h3>
                  <p className="text-planning-text-light leading-relaxed">
                    We source our data directly from official UK planning authorities, ensuring accuracy and completeness. Our database is updated in real-time, so you never miss an opportunity.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-6">
                <div className="w-12 h-12 bg-pink-50 rounded-xl flex items-center justify-center flex-shrink-0">
                  <Users className="w-6 h-6 text-planning-primary" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-planning-primary mb-2">Expert Support</h3>
                  <p className="text-planning-text-light leading-relaxed">
                    Our team combines planning industry expertise with technical knowledge. We provide comprehensive onboarding, training, and ongoing support to ensure your success.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-6">
                <div className="w-12 h-12 bg-green-50 rounded-xl flex items-center justify-center flex-shrink-0">
                  <Zap className="w-6 h-6 text-planning-primary" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-planning-primary mb-2">Continuous Innovation</h3>
                  <p className="text-planning-text-light leading-relaxed">
                    We're constantly enhancing our AI models, adding new features, and expanding our data coverage. Your feedback directly shapes our product roadmap.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </Container>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-white">
        <Container>
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-planning-primary mb-6">
              Ready to Experience the Future of Planning Intelligence?
            </h2>
            <p className="text-xl text-planning-text-light mb-8">
              Join hundreds of property professionals who are already saving 90% of their research time
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <Link href="/pricing">
                <Button size="lg" className="bg-planning-primary text-white hover:bg-planning-accent">
                  Start Free Trial
                </Button>
              </Link>
              <Link href="/contact">
                <Button size="lg" variant="outline">
                  Contact Sales
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
