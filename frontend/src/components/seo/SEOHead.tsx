/**
 * SEOHead Component
 * Dynamic meta tags helper for Next.js App Router
 * PRD Requirement: Open Graph, Twitter Cards, Canonical URLs
 */

import { Metadata } from 'next'

export interface SEOConfig {
  title: string
  description: string
  canonical?: string
  keywords?: string[]
  openGraph?: {
    title?: string
    description?: string
    image?: string
    type?: 'website' | 'article'
    siteName?: string
  }
  twitter?: {
    card?: 'summary' | 'summary_large_image'
    title?: string
    description?: string
    image?: string
    creator?: string
  }
  robots?: {
    index?: boolean
    follow?: boolean
  }
}

const DEFAULT_SITE_NAME = 'Planning Explorer'
const DEFAULT_OG_IMAGE = '/og-image.png'
const DEFAULT_TWITTER_CREATOR = '@PlanningExplorer'

/**
 * Generate Next.js metadata object for App Router
 * Use this in your page.tsx files:
 *
 * export const metadata = generateMetadata({
 *   title: 'Planning Applications in Milton Keynes',
 *   description: 'View all planning applications...',
 *   canonical: '/planning-applications/milton-keynes',
 * })
 */
export function generateMetadata(config: SEOConfig): Metadata {
  const {
    title,
    description,
    canonical,
    keywords,
    openGraph,
    twitter,
    robots = { index: true, follow: true },
  } = config

  const fullTitle = title.includes(DEFAULT_SITE_NAME) ? title : `${title} | ${DEFAULT_SITE_NAME}`

  return {
    title: fullTitle,
    description,
    ...(keywords && { keywords: keywords.join(', ') }),
    ...(canonical && {
      alternates: {
        canonical,
      },
    }),
    robots: {
      index: robots.index ?? true,
      follow: robots.follow ?? true,
    },
    openGraph: {
      title: openGraph?.title || title,
      description: openGraph?.description || description,
      type: openGraph?.type || 'website',
      siteName: openGraph?.siteName || DEFAULT_SITE_NAME,
      ...(openGraph?.image && {
        images: [
          {
            url: openGraph.image,
            width: 1200,
            height: 630,
            alt: openGraph.title || title,
          },
        ],
      }),
      ...(!openGraph?.image && {
        images: [
          {
            url: DEFAULT_OG_IMAGE,
            width: 1200,
            height: 630,
            alt: title,
          },
        ],
      }),
    },
    twitter: {
      card: twitter?.card || 'summary_large_image',
      title: twitter?.title || title,
      description: twitter?.description || description,
      creator: twitter?.creator || DEFAULT_TWITTER_CREATOR,
      ...(twitter?.image && {
        images: [twitter.image],
      }),
      ...(!twitter?.image && openGraph?.image && {
        images: [openGraph.image],
      }),
      ...(!twitter?.image && !openGraph?.image && {
        images: [DEFAULT_OG_IMAGE],
      }),
    },
  }
}

/**
 * Generate metadata for authority pages
 */
export function generateAuthorityMetadata(authorityName: string, stats?: {
  totalApplications?: number
  approvalRate?: number
  avgDecisionDays?: number
}): Metadata {
  const title = `Planning Applications in ${authorityName}`
  const description = stats
    ? `View ${stats.totalApplications?.toLocaleString() || 'all'} planning applications in ${authorityName}. ${stats.approvalRate ? `${(stats.approvalRate * 100).toFixed(0)}% approval rate` : ''}${stats.avgDecisionDays ? `, avg ${stats.avgDecisionDays.toFixed(0)} days decision time` : ''}. Free planning intelligence.`
    : `Explore planning applications in ${authorityName}. View approval rates, decision times, and trends. Free planning intelligence from Planning Explorer.`

  return generateMetadata({
    title,
    description,
    canonical: `/planning-applications/${authorityName.toLowerCase().replace(/\s+/g, '-')}`,
    keywords: [
      'planning applications',
      authorityName,
      'planning permission',
      'local planning',
      'UK planning',
      'development applications',
    ],
  })
}

/**
 * Generate metadata for location pages
 */
export function generateLocationMetadata(locationName: string, stats?: {
  totalApplications?: number
  radius?: string
}): Metadata {
  const title = `Planning Applications in ${locationName}`
  const description = stats?.totalApplications
    ? `Discover ${stats.totalApplications.toLocaleString()} planning applications within ${stats.radius || '5 miles'} of ${locationName}. Interactive map, approval trends, and AI insights.`
    : `Explore planning applications near ${locationName}. Interactive map, approval rates, and trends. Free planning intelligence from Planning Explorer.`

  return generateMetadata({
    title,
    description,
    canonical: `/planning-applications/${locationName.toLowerCase().replace(/\s+/g, '-')}`,
    keywords: [
      'planning applications',
      locationName,
      'planning permission',
      'local development',
      'UK planning',
      'nearby applications',
    ],
  })
}

/**
 * Generate metadata for sector pages
 */
export function generateSectorMetadata(sectorName: string, stats?: {
  totalApplications?: number
  topAuthority?: string
}): Metadata {
  const title = `${sectorName} Planning Applications`
  const description = stats?.totalApplications
    ? `${stats.totalApplications.toLocaleString()} ${sectorName.toLowerCase()} planning applications across the UK. ${stats.topAuthority ? `Most active in ${stats.topAuthority}` : 'View trends and approval rates'}.`
    : `Explore ${sectorName.toLowerCase()} planning applications across the UK. View trends, approval rates, and opportunities. Free planning intelligence.`

  return generateMetadata({
    title,
    description,
    canonical: `/sectors/${sectorName.toLowerCase().replace(/\s+/g, '-')}`,
    keywords: [
      'planning applications',
      sectorName,
      'sector analysis',
      'UK planning',
      'development trends',
    ],
  })
}

/**
 * Breadcrumb Component (for visual display)
 */
export interface BreadcrumbItem {
  name: string
  url: string
}

export function Breadcrumbs({ items }: { items: BreadcrumbItem[] }) {
  return (
    <nav aria-label="Breadcrumb" className="mb-6">
      <ol className="flex items-center gap-2 text-sm text-gray-600">
        {items.map((item, index) => (
          <li key={item.url} className="flex items-center gap-2">
            {index > 0 && <span className="text-gray-400">/</span>}
            {index === items.length - 1 ? (
              <span className="font-medium text-gray-900">{item.name}</span>
            ) : (
              <a
                href={item.url}
                className="hover:text-planning-primary transition-colors"
              >
                {item.name}
              </a>
            )}
          </li>
        ))}
      </ol>
    </nav>
  )
}
