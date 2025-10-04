'use client'

import { Container } from '@/components/ui/Container'

const steps = [
  {
    number: '01',
    title: 'We Collect Every Planning Application',
    description: 'Our system automatically gathers planning data from every UK local authority, ensuring full nationwide coverage, every month.',
    imageUrl: 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=500&h=300&fit=crop',
    imageAlt: 'Modern office buildings and urban development representing data collection'
  },
  {
    number: '02',
    title: 'We Clean & Verify the Data',
    description: 'Our proprietary tech extracts key details, and our in-house team checks the data for accuracy, completeness, and relevance.',
    imageUrl: 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=500&h=300&fit=crop',
    imageAlt: 'Data analysis and technology visualization representing data verification'
  },
  {
    number: '03',
    title: 'You Search, Filter & Explore',
    description: 'Log in to your dashboard to explore applications by location, status, sector, use class, and more, with export options for reports or CSV.',
    imageUrl: 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=500&h=300&fit=crop',
    imageAlt: 'Person working on laptop with analytics and search interfaces'
  },
  {
    number: '04',
    title: 'You Take Action with Confidence',
    description: 'Use the latest data to uncover opportunities, monitor markets, or guide decisions, backed by real-time insights you can trust.',
    imageUrl: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500&h=300&fit=crop',
    imageAlt: 'Planning and development site showing confident decision making'
  }
]

export function HowItWorks() {
  return (
    <section className="py-24 bg-white">
      <Container>
        {/* Section Header */}
        <div className="mb-20">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-start">
            {/* Left side - Title */}
            <div>
              <div className="text-sm text-planning-text-light uppercase tracking-wider font-medium mb-6">
                HOW IT WORKS
              </div>
              <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-planning-primary leading-tight">
                From nationwide data collection to real time insights
              </h2>
            </div>

            {/* Right side - Description */}
            <div className="lg:pt-16">
              <p className="text-lg text-planning-text-light leading-relaxed">
                Here's how we deliver powerful planning intelligence in just four simple steps.
              </p>
            </div>
          </div>
        </div>

        {/* Timeline Steps */}
        <div className="relative max-w-6xl mx-auto">
          {/* Vertical Timeline Line - Made clearly visible */}
          <div className="hidden lg:block absolute left-1/2 top-0 bottom-0 w-0.5 bg-planning-bright transform -translate-x-1/2 opacity-60">
            {/* Timeline dots */}
            {steps.map((_, index) => (
              <div
                key={index}
                className="absolute w-4 h-4 bg-planning-bright rounded-full transform -translate-x-1/2 border-2 border-white shadow-md"
                style={{ top: `${index * 25 + 15}%` }}
              />
            ))}
          </div>

          {/* Steps with proper spacing */}
          <div className="space-y-32">
            {steps.map((step, index) => (
              <div key={index} className="relative">
                {/* Row layout with proper column spacing */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-16 items-center">
                  {/* Left Column - Image for odd steps (01, 03), Content for even steps (02, 04) */}
                  <div className="lg:col-span-5">
                    {index % 2 === 0 ? (
                      /* Image for steps 01, 03 */
                      <div className="relative group">
                        <div className="bg-gray-100 rounded-2xl overflow-hidden shadow-lg aspect-[4/3] group-hover:shadow-xl transition-shadow duration-300">
                          <img
                            src={step.imageUrl}
                            alt={step.imageAlt}
                            className="w-full h-full object-cover"
                          />
                        </div>
                      </div>
                    ) : (
                      /* Content for steps 02, 04 */
                      <div className="text-right">
                        {/* Step Number and Title on same line */}
                        <div className="flex items-center gap-4 mb-6">
                          <div className="flex items-center justify-center w-16 h-16 bg-planning-button rounded-2xl flex-shrink-0">
                            <span className="text-2xl font-bold text-white">
                              {step.number}
                            </span>
                          </div>
                          <h3 className="text-2xl md:text-3xl font-bold text-planning-primary leading-tight">
                            {step.title}
                          </h3>
                        </div>
                        {/* Description */}
                        <p className="text-lg text-planning-text-light leading-relaxed text-right">
                          {step.description}
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Center spacer for timeline */}
                  <div className="lg:col-span-2 hidden lg:block"></div>

                  {/* Right Column - Content for odd steps (01, 03), Image for even steps (02, 04) */}
                  <div className="lg:col-span-5">
                    {index % 2 === 0 ? (
                      /* Content for steps 01, 03 */
                      <div>
                        {/* Step Number and Title on same line */}
                        <div className="flex items-center gap-4 mb-6">
                          <div className="flex items-center justify-center w-16 h-16 bg-planning-button rounded-2xl flex-shrink-0">
                            <span className="text-2xl font-bold text-white">
                              {step.number}
                            </span>
                          </div>
                          <h3 className="text-2xl md:text-3xl font-bold text-planning-primary leading-tight">
                            {step.title}
                          </h3>
                        </div>
                        {/* Description */}
                        <p className="text-lg text-planning-text-light leading-relaxed">
                          {step.description}
                        </p>
                      </div>
                    ) : (
                      /* Image for steps 02, 04 */
                      <div className="relative group">
                        <div className="bg-gray-100 rounded-2xl overflow-hidden shadow-lg aspect-[4/3] group-hover:shadow-xl transition-shadow duration-300">
                          <img
                            src={step.imageUrl}
                            alt={step.imageAlt}
                            className="w-full h-full object-cover"
                          />
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Container>
    </section>
  )
}