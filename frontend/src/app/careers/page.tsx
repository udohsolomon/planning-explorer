'use client'

import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import { Footer } from '@/components/sections/Footer'
import { Sparkles, Briefcase, Heart, TrendingUp, Users, Globe, Zap, Coffee, Laptop, Gift, GraduationCap, MapPin } from 'lucide-react'
import Link from 'next/link'

const benefits = [
  {
    icon: Heart,
    title: 'Health & Wellness',
    description: 'Comprehensive health insurance, mental health support, and wellness programs',
    color: 'bg-pink-50'
  },
  {
    icon: TrendingUp,
    title: 'Career Growth',
    description: 'Clear career progression paths, mentorship programs, and continuous learning opportunities',
    color: 'bg-cyan-50'
  },
  {
    icon: Laptop,
    title: 'Remote-First',
    description: 'Work from anywhere in the UK with flexible hours and home office stipend',
    color: 'bg-orange-50'
  },
  {
    icon: Coffee,
    title: 'Work-Life Balance',
    description: '25 days holiday plus bank holidays, flexible working hours, and unlimited sick leave',
    color: 'bg-green-50'
  },
  {
    icon: Gift,
    title: 'Competitive Compensation',
    description: 'Market-leading salaries, equity options, performance bonuses, and annual reviews',
    color: 'bg-yellow-50'
  },
  {
    icon: GraduationCap,
    title: 'Learning Budget',
    description: '£2,000 annual budget for courses, conferences, books, and professional development',
    color: 'bg-cyan-50'
  }
]

const values = [
  {
    icon: Zap,
    title: 'Innovation',
    description: 'We encourage experimentation and creative problem-solving. Your ideas matter here.',
    color: 'bg-orange-50'
  },
  {
    icon: Users,
    title: 'Collaboration',
    description: 'We work together, share knowledge freely, and celebrate team wins.',
    color: 'bg-pink-50'
  },
  {
    icon: TrendingUp,
    title: 'Growth',
    description: 'We invest in your development and create opportunities for advancement.',
    color: 'bg-green-50'
  },
  {
    icon: Heart,
    title: 'Impact',
    description: 'Our work transforms the UK property industry and creates real value for customers.',
    color: 'bg-cyan-50'
  }
]

const openPositions = [
  {
    title: 'Senior Full-Stack Engineer',
    department: 'Engineering',
    location: 'London (Remote)',
    type: 'Full-time',
    description: 'Build and scale our AI-powered planning intelligence platform using Next.js, FastAPI, and Elasticsearch.',
    requirements: ['5+ years full-stack experience', 'Next.js/React expertise', 'Python/FastAPI knowledge', 'Experience with AI/ML integration'],
    color: 'bg-cyan-50'
  },
  {
    title: 'AI/ML Engineer',
    department: 'AI Research',
    location: 'London (Remote)',
    type: 'Full-time',
    description: 'Develop and optimize AI models for semantic search, opportunity scoring, and predictive analytics.',
    requirements: ['3+ years ML experience', 'NLP and embeddings expertise', 'Python proficiency', 'Experience with OpenAI/Claude APIs'],
    color: 'bg-orange-50'
  },
  {
    title: 'Product Designer',
    department: 'Design',
    location: 'London (Remote)',
    type: 'Full-time',
    description: 'Create beautiful, intuitive user experiences for property professionals using our platform.',
    requirements: ['4+ years product design', 'Figma expert', 'Data-heavy UI experience', 'User research skills'],
    color: 'bg-pink-50'
  },
  {
    title: 'Customer Success Manager',
    department: 'Customer Success',
    location: 'London (Hybrid)',
    type: 'Full-time',
    description: 'Help property professionals succeed with Planning Explorer through onboarding, training, and ongoing support.',
    requirements: ['3+ years customer success', 'SaaS experience', 'Planning industry knowledge (preferred)', 'Excellent communication'],
    color: 'bg-green-50'
  },
  {
    title: 'Data Engineer',
    department: 'Engineering',
    location: 'London (Remote)',
    type: 'Full-time',
    description: 'Build data pipelines to ingest, process, and enrich UK planning application data at scale.',
    requirements: ['4+ years data engineering', 'Python expertise', 'Elasticsearch experience', 'ETL pipeline knowledge'],
    color: 'bg-yellow-50'
  },
  {
    title: 'Marketing Manager',
    department: 'Marketing',
    location: 'London (Hybrid)',
    type: 'Full-time',
    description: 'Drive growth through content marketing, SEO, partnerships, and demand generation in the property sector.',
    requirements: ['5+ years B2B marketing', 'Content strategy expertise', 'SEO/SEM knowledge', 'Property industry experience (preferred)'],
    color: 'bg-cyan-50'
  }
]

const hiringProcess = [
  {
    step: '1',
    title: 'Apply',
    description: 'Submit your CV and cover letter. Tell us why you\'re excited about Planning Explorer.',
    color: 'bg-cyan-50'
  },
  {
    step: '2',
    title: 'Recruiter Call',
    description: '30-minute call to discuss your background, expectations, and answer initial questions.',
    color: 'bg-orange-50'
  },
  {
    step: '3',
    title: 'Technical/Skills Assessment',
    description: 'Role-specific assessment: coding challenge, design task, or case study.',
    color: 'bg-pink-50'
  },
  {
    step: '4',
    title: 'Team Interviews',
    description: 'Meet your potential teammates and hiring manager. We assess cultural fit and technical skills.',
    color: 'bg-green-50'
  },
  {
    step: '5',
    title: 'Offer',
    description: 'Receive your offer! We\'ll discuss compensation, start date, and answer any questions.',
    color: 'bg-yellow-50'
  }
]

export default function CareersPage() {
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
                <span className="text-sm font-semibold text-white">Join Our Team</span>
              </div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold mb-4 leading-tight" style={{ color: '#FFFFFF' }}>
                <span className="block">Build the Future of</span>
                <span className="block">Planning Intelligence</span>
              </h1>
              <p className="text-xl md:text-2xl mb-8 text-white/90">
                Join a team of passionate engineers, designers, and problem-solvers transforming how the UK property industry works.
              </p>
              <Button size="lg" className="bg-white text-planning-primary hover:bg-gray-100">
                View Open Positions
              </Button>
            </div>
          </Container>
        </div>
      </section>

      {/* Why Join Us */}
      <section className="py-24 bg-white relative -mt-20 z-30">
        <Container>
          <div className="text-center mb-16">
            <div className="inline-block px-4 py-2 bg-planning-button/10 rounded-full mb-6">
              <span className="text-planning-primary font-medium text-sm uppercase tracking-wider">
                Why Planning Explorer
              </span>
            </div>
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-planning-primary mb-6">
              Why Work With Us?
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              We're a rapidly growing startup solving real problems for the UK property industry with cutting-edge AI
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

      {/* Benefits */}
      <section className="py-24 bg-gray-50">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-planning-primary mb-6">
              Benefits & Perks
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              We invest in our team's success, wellbeing, and growth
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {benefits.map((benefit, index) => (
              <div
                key={index}
                className={`${benefit.color} rounded-3xl p-8 hover:shadow-lg hover:scale-105 transition-all duration-300`}
              >
                <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center mb-6 shadow-sm">
                  <benefit.icon className="w-8 h-8 text-planning-primary" />
                </div>
                <h3 className="text-xl font-bold text-planning-primary mb-3">{benefit.title}</h3>
                <p className="text-planning-text-light text-sm leading-relaxed">{benefit.description}</p>
              </div>
            ))}
          </div>
        </Container>
      </section>

      {/* Open Positions */}
      <section className="py-24 bg-white">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-planning-primary mb-6">
              Open Positions
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              Find your perfect role and join our growing team
            </p>
          </div>

          <div className="max-w-5xl mx-auto space-y-6">
            {openPositions.map((position, index) => (
              <div
                key={index}
                className={`${position.color} rounded-3xl p-8 hover:shadow-lg transition-all duration-300`}
              >
                <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
                  <div className="flex-1">
                    <div className="flex flex-wrap items-center gap-3 mb-4">
                      <h3 className="text-2xl font-bold text-planning-primary">{position.title}</h3>
                      <span className="inline-block px-3 py-1 bg-planning-primary text-white text-xs font-bold rounded-full">
                        {position.type}
                      </span>
                    </div>
                    <div className="flex flex-wrap items-center gap-4 mb-4 text-sm text-planning-text-light">
                      <div className="flex items-center gap-1">
                        <Briefcase className="w-4 h-4" />
                        <span>{position.department}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <MapPin className="w-4 h-4" />
                        <span>{position.location}</span>
                      </div>
                    </div>
                    <p className="text-planning-text-light mb-4 leading-relaxed">{position.description}</p>
                    <div className="mb-4">
                      <h4 className="font-semibold text-planning-primary mb-2 text-sm">Key Requirements:</h4>
                      <ul className="space-y-1">
                        {position.requirements.map((req, reqIndex) => (
                          <li key={reqIndex} className="flex items-start text-sm text-planning-text-light">
                            <span className="mr-2">•</span>
                            <span>{req}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  <div className="flex-shrink-0">
                    <Link href={`/contact?subject=Application: ${position.title}`}>
                      <Button size="lg" className="bg-planning-primary text-white hover:bg-planning-accent whitespace-nowrap">
                        Apply Now
                      </Button>
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <p className="text-planning-text-light mb-6">
              Don't see a role that fits? We're always looking for talented people.
            </p>
            <Link href="/contact?subject=General Application">
              <Button size="lg" variant="outline">
                Send Us Your CV
              </Button>
            </Link>
          </div>
        </Container>
      </section>

      {/* Hiring Process */}
      <section className="py-24 bg-gray-50">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-planning-primary mb-6">
              Our Hiring Process
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              Transparent, efficient, and designed to help you show your best work
            </p>
          </div>

          <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-5 gap-6">
            {hiringProcess.map((phase, index) => (
              <div key={index} className="relative">
                <div className={`${phase.color} rounded-3xl p-6 text-center hover:shadow-lg transition-all duration-300 h-full`}>
                  <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center mx-auto mb-4 shadow-sm">
                    <span className="text-2xl font-bold text-planning-primary">{phase.step}</span>
                  </div>
                  <h3 className="text-lg font-bold text-planning-primary mb-3">{phase.title}</h3>
                  <p className="text-planning-text-light text-sm leading-relaxed">{phase.description}</p>
                </div>
                {index < hiringProcess.length - 1 && (
                  <div className="hidden md:block absolute top-1/2 -right-3 transform -translate-y-1/2 z-10">
                    <div className="w-6 h-6 bg-planning-primary rounded-full flex items-center justify-center">
                      <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <p className="text-planning-text-light">
              Average time from application to offer: <span className="font-bold text-planning-primary">2-3 weeks</span>
            </p>
          </div>
        </Container>
      </section>

      {/* Team Culture */}
      <section className="py-24 bg-white">
        <Container>
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-planning-primary mb-6">
                Life at Planning Explorer
              </h2>
              <p className="text-xl text-planning-text-light">
                What it's really like to work here
              </p>
            </div>

            <div className="space-y-8">
              <div className="bg-cyan-50 rounded-3xl p-8">
                <h3 className="text-2xl font-bold text-planning-primary mb-4">Remote-First Culture</h3>
                <p className="text-planning-text-light leading-relaxed mb-4">
                  We're fully remote with team members across the UK. Work from home, a coffee shop, or wherever you're most productive. We provide a £500 home office setup budget and £50/month for coworking spaces.
                </p>
              </div>

              <div className="bg-orange-50 rounded-3xl p-8">
                <h3 className="text-2xl font-bold text-planning-primary mb-4">Continuous Learning</h3>
                <p className="text-planning-text-light leading-relaxed mb-4">
                  Weekly tech talks, monthly team learning sessions, and £2,000/year learning budget for conferences, courses, and books. We encourage everyone to experiment with new technologies and share knowledge.
                </p>
              </div>

              <div className="bg-pink-50 rounded-3xl p-8">
                <h3 className="text-2xl font-bold text-planning-primary mb-4">Work-Life Balance</h3>
                <p className="text-planning-text-light leading-relaxed mb-4">
                  Flexible working hours to accommodate your schedule. No unnecessary meetings - we value deep work and respect your time. Regular team socials and optional Friday afternoon hangouts.
                </p>
              </div>

              <div className="bg-green-50 rounded-3xl p-8">
                <h3 className="text-2xl font-bold text-planning-primary mb-4">Impact-Driven Work</h3>
                <p className="text-planning-text-light leading-relaxed mb-4">
                  Your work directly impacts thousands of property professionals. You'll see real results from your contributions and have autonomy to drive projects from idea to launch.
                </p>
              </div>
            </div>
          </div>
        </Container>
      </section>

      {/* CTA */}
      <section className="py-24 bg-gray-50">
        <Container>
          <div className="max-w-4xl mx-auto text-center">
            <div className="bg-gradient-to-br from-planning-primary to-planning-accent rounded-3xl p-8 md:p-12 text-white">
              <Globe className="w-16 h-16 mx-auto mb-6" />
              <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-6">
                Ready to Make an Impact?
              </h2>
              <p className="text-xl text-white/90 mb-8">
                Join us in revolutionizing the UK property industry with AI-powered planning intelligence
              </p>
              <div className="flex flex-col sm:flex-row justify-center gap-4">
                <Link href="#open-positions">
                  <Button size="lg" className="bg-white text-planning-primary hover:bg-gray-100">
                    View Open Positions
                  </Button>
                </Link>
                <Link href="/about">
                  <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10">
                    Learn About Us
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </Container>
      </section>

      <Footer />
    </div>
  )
}
