import { HeroSlider } from '@/components/sections/HeroSlider'
import { ServiceHighlights } from '@/components/sections/ServiceHighlights'
import { HowItWorks } from '@/components/sections/HowItWorks'
import { PricingPlans } from '@/components/sections/PricingPlans'
import { Testimonials } from '@/components/sections/Testimonials'
import { FAQ } from '@/components/sections/FAQ'
import { Footer } from '@/components/sections/Footer'

export default function Home() {
  return (
    <>
      {/* Hero Section */}
      <HeroSlider />

      {/* Service Highlights */}
      <ServiceHighlights />

      {/* How It Works */}
      <HowItWorks />

      {/* Pricing Plans */}
      <PricingPlans />

      {/* Testimonials */}
      <Testimonials />

      {/* FAQ Section */}
      <FAQ />

      {/* Footer with CTA */}
      <Footer />
    </>
  )
}
