'use client'

import { Container } from '@/components/ui/Container'
import { Star } from 'lucide-react'

const testimonials = [
  {
    id: 1,
    name: 'Sarah Mitchell',
    role: 'Property Developer, Manchester',
    content: 'Planning Explorer\'s AI predictions saved us weeks of research. We identified three major opportunities in our target area within minutes. The approval probability scores have been remarkably accurate.',
    avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=64&h=64&fit=crop&crop=face'
  },
  {
    id: 2,
    name: 'James Richardson',
    role: 'Planning Consultant, London',
    content: 'The natural language search is a game-changer. I can ask complex questions in plain English and get exactly what I need. It\'s like having a planning research assistant working 24/7.',
    avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=64&h=64&fit=crop&crop=face'
  },
  {
    id: 3,
    name: 'Emma Thompson',
    role: 'Solar Installation Director',
    content: 'Planning Explorer identified 47 qualified leads for our solar installation business in the first month. The AI filters applications perfectly matched to our criteria. Our conversion rate has increased 60%.',
    avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=64&h=64&fit=crop&crop=face'
  },
  {
    id: 4,
    name: 'David Chen',
    role: 'Investment Analyst, Birmingham',
    content: 'The predictive analytics and market intelligence features give us competitive advantage. We can assess development viability faster than ever before and make data-driven investment decisions with confidence.',
    avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=64&h=64&fit=crop&crop=face'
  }
]

const featuredTestimonial = {
  name: 'Michael Foster',
  role: 'MD, Foster Development Group',
  content: 'Planning Explorer has transformed how we approach development opportunities. The AI-powered insights, predictive analytics, and comprehensive UK coverage have given us an edge our competitors simply don\'t have. What used to take our team weeks now takes minutes.'
}

export function Testimonials() {
  return (
    <section className="py-24 bg-white">
      <Container>
        {/* Section Header */}
        <div className="mb-16">
          <div className="text-sm text-planning-text-light uppercase tracking-wider font-medium mb-6">
            🏆 TESTIMONIALS
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-start">
            {/* Left side - Title */}
            <div>
              <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-planning-primary leading-tight">
                Find out what others are really saying about us
              </h2>
            </div>

            {/* Right side - User Satisfaction Rating */}
            <div className="lg:pt-8">
              <div className="bg-gray-50 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="text-4xl font-bold text-planning-primary">98%</div>
                  <div className="text-right">
                    <div className="text-sm text-planning-text-light mb-1">
                      Customer satisfaction rate from
                    </div>
                    <div className="text-sm text-planning-text-light">
                      property professionals
                    </div>
                  </div>
                </div>

                {/* Stars */}
                <div className="flex items-center mb-4">
                  <div className="bg-planning-bright px-3 py-1 rounded-md flex items-center space-x-1">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <Star key={star} className="w-4 h-4 text-white fill-current" />
                    ))}
                  </div>
                  <span className="ml-2 text-sm text-planning-text-light">5.0/5.0</span>
                </div>

                {/* Platform Badge */}
                <div className="flex items-center">
                  <div className="flex items-center space-x-2">
                    <Star className="w-5 h-5 text-planning-bright fill-current" />
                    <span className="font-bold text-planning-primary">Trusted by UK Professionals</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Featured Testimonial */}
          <div className="lg:col-span-1">
            <div className="bg-gradient-to-br from-planning-bright to-planning-accent rounded-3xl p-8 text-white h-full flex flex-col justify-between min-h-[500px]">
              {/* Logo/Brand */}
              <div className="mb-8">
                <div className="flex items-center space-x-2">
                  <div className="w-10 h-10 bg-white rounded-md flex items-center justify-center">
                    <span className="text-planning-primary font-bold text-base">PE</span>
                  </div>
                  <span className="text-2xl font-bold">Planning Explorer</span>
                </div>
              </div>

              {/* Featured Quote */}
              <div className="flex-1 flex flex-col justify-center">
                <blockquote className="text-lg md:text-xl leading-relaxed mb-8">
                  "{featuredTestimonial.content}"
                </blockquote>

                {/* Author */}
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
                    <span className="text-white font-semibold">
                      {featuredTestimonial.name.split(' ').map(n => n[0]).join('')}
                    </span>
                  </div>
                  <div>
                    <div className="font-semibold">{featuredTestimonial.name}</div>
                    <div className="text-white/80 text-sm">{featuredTestimonial.role}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Testimonial Cards Grid */}
          <div className="lg:col-span-2">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {testimonials.map((testimonial) => (
                <div key={testimonial.id} className="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
                  {/* Content */}
                  <blockquote className="text-planning-text-light mb-6 leading-relaxed">
                    "{testimonial.content}"
                  </blockquote>

                  {/* Author */}
                  <div className="flex items-center space-x-3">
                    <img
                      src={testimonial.avatar}
                      alt={testimonial.name}
                      className="w-12 h-12 rounded-full object-cover"
                    />
                    <div>
                      <div className="font-semibold text-planning-primary">{testimonial.name}</div>
                      <div className="text-planning-text-light text-sm">{testimonial.role}</div>
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