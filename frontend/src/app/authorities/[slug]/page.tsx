import { Metadata } from 'next'
import slugsData from '@/data/slugs.json'
import AuthorityPageClient from './AuthorityPageClient'

// Generate static params for top 100 authorities for build-time generation
export async function generateStaticParams() {
  const authorities = Object.entries(slugsData.authorities)

  // Generate params for top 100 authorities at build time
  return authorities.slice(0, 100).map(([name, slug]) => ({
    slug: slug as string,
  }))
}

// Dynamic metadata generation
export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params

  // Find authority name from slug
  const authorityEntry = Object.entries(slugsData.authorities).find(
    ([name, authoritySlug]) => authoritySlug === slug
  )
  const authorityName = authorityEntry ? authorityEntry[0] : slug.replace(/-/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())

  return {
    title: `${authorityName} Planning Applications | Planning Explorer`,
    description: `View planning application statistics, trends, and insights for ${authorityName}. Track approval rates, decision times, and sector breakdowns.`,
    openGraph: {
      title: `${authorityName} Planning Statistics`,
      description: `Comprehensive planning application data and insights for ${authorityName}`,
      images: ['/og-authority.png'],
    },
  }
}

// ISR revalidation every hour
export const revalidate = 3600

export default async function AuthorityDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  return <AuthorityPageClient slug={slug} />
}
