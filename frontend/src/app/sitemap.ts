import { MetadataRoute } from 'next'
import slugsData from '@/data/slugs.json'

/**
 * Sitemap Generation for Content Discovery Pages
 * Phase 1 Frontend Deliverable
 *
 * Generates sitemap for:
 * - 425 UK authority pages
 * - 82 location pages
 * - 20 sector pages
 *
 * Total: 527 URLs
 */

const BASE_URL = 'https://planningexplorer.com'

export default function sitemap(): MetadataRoute.Sitemap {
  const currentDate = new Date()

  // Static pages
  const staticPages: MetadataRoute.Sitemap = [
    {
      url: BASE_URL,
      lastModified: currentDate,
      changeFrequency: 'daily',
      priority: 1.0,
    },
    {
      url: `${BASE_URL}/search`,
      lastModified: currentDate,
      changeFrequency: 'daily',
      priority: 0.9,
    },
    {
      url: `${BASE_URL}/planning-applications`,
      lastModified: currentDate,
      changeFrequency: 'daily',
      priority: 0.9,
    },
    {
      url: `${BASE_URL}/locations`,
      lastModified: currentDate,
      changeFrequency: 'weekly',
      priority: 0.8,
    },
    {
      url: `${BASE_URL}/sectors`,
      lastModified: currentDate,
      changeFrequency: 'weekly',
      priority: 0.8,
    },
  ]

  // Authority pages (425 pages)
  const authorityPages: MetadataRoute.Sitemap = Object.entries(slugsData.authorities).map(
    ([name, slug]) => ({
      url: `${BASE_URL}/planning-applications/${slug}`,
      lastModified: currentDate,
      changeFrequency: 'daily' as const,
      priority: 0.8,
    })
  )

  // Location pages (82 pages)
  const locationPages: MetadataRoute.Sitemap = Object.entries(slugsData.locations).map(
    ([name, slug]) => ({
      url: `${BASE_URL}/locations/${slug}`,
      lastModified: currentDate,
      changeFrequency: 'weekly' as const,
      priority: 0.7,
    })
  )

  // Sector pages (20 pages)
  const sectorPages: MetadataRoute.Sitemap = Object.entries(slugsData.sectors).map(
    ([name, slug]) => ({
      url: `${BASE_URL}/sectors/${slug}`,
      lastModified: currentDate,
      changeFrequency: 'weekly' as const,
      priority: 0.7,
    })
  )

  return [...staticPages, ...authorityPages, ...locationPages, ...sectorPages]
}
