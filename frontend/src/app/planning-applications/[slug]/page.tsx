import { Metadata } from 'next'
import { getPSEOPage } from '@/lib/pseo-api'
import PSEOPageClient from './PSEOPageClient'
import PlanningApplicationsClient from './PlanningApplicationsClient'

// ISR revalidation every hour
export const revalidate = 3600

// Dynamic metadata generation from pSEO data
export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params

  try {
    // Try to fetch pSEO page data for metadata
    const response = await getPSEOPage(slug)

    if (response.success && response.data) {
      const seo = response.data.seo.meta_tags

      return {
        title: seo.title,
        description: seo.description,
        keywords: seo.keywords.join(', '),
        openGraph: {
          title: response.data.seo.og_tags['og:title'] || seo.title,
          description: response.data.seo.og_tags['og:description'] || seo.description,
          type: 'website',
          locale: 'en_GB',
        },
        twitter: {
          card: 'summary_large_image',
          title: seo.title,
          description: seo.description,
        },
      }
    }
  } catch (error) {
    console.error('Error fetching pSEO metadata:', error)
  }

  // Fallback metadata
  const authorityName = slug.replace(/-/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())
  return {
    title: `Planning Applications in ${authorityName} | Planning Explorer`,
    description: `View planning applications, statistics, trends, and insights for ${authorityName}.`,
  }
}

export default async function PlanningApplicationsPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params

  // Check if pSEO page exists
  const pseoResponse = await getPSEOPage(slug)

  // If pSEO page exists, use pSEO client, otherwise use legacy client
  if (pseoResponse.success && pseoResponse.data) {
    return <PSEOPageClient slug={slug} />
  }

  // Fallback to legacy content-discovery client
  return <PlanningApplicationsClient slug={slug} />
}
