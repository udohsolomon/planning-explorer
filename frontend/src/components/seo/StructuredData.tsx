/**
 * StructuredData Component
 * Schema.org JSON-LD generator for SEO
 * PRD Requirement: Schema.org markup for all content pages
 * Supports: GovernmentOrganization, Place, Dataset, Article
 */

import { ReactElement } from 'react'

export interface GovernmentOrganizationSchema {
  type: 'GovernmentOrganization'
  name: string
  description?: string
  url?: string
  address?: {
    streetAddress?: string
    addressLocality?: string
    addressRegion?: string
    postalCode?: string
    addressCountry?: string
  }
  telephone?: string
  email?: string
  areaServed?: string
}

export interface PlaceSchema {
  type: 'Place'
  name: string
  description?: string
  address?: {
    streetAddress?: string
    addressLocality?: string
    addressRegion?: string
    postalCode?: string
    addressCountry?: string
  }
  geo?: {
    latitude: number
    longitude: number
  }
  url?: string
}

export interface DatasetSchema {
  type: 'Dataset'
  name: string
  description: string
  url?: string
  creator?: {
    name: string
    url?: string
  }
  datePublished?: string
  dateModified?: string
  keywords?: string[]
  license?: string
  distribution?: {
    contentUrl: string
    encodingFormat: string
  }[]
}

export interface ArticleSchema {
  type: 'Article'
  headline: string
  description?: string
  image?: string | string[]
  datePublished?: string
  dateModified?: string
  author?: {
    name: string
    url?: string
  }
  publisher?: {
    name: string
    logo?: {
      url: string
      width?: number
      height?: number
    }
  }
}

export interface BreadcrumbSchema {
  type: 'BreadcrumbList'
  items: Array<{
    name: string
    url: string
  }>
}

type SchemaInput =
  | GovernmentOrganizationSchema
  | PlaceSchema
  | DatasetSchema
  | ArticleSchema
  | BreadcrumbSchema

export interface StructuredDataProps {
  schema: SchemaInput | SchemaInput[]
}

export function StructuredData({ schema }: StructuredDataProps): ReactElement | null {
  // Handle null/undefined schema
  if (!schema) {
    return null
  }

  const schemas = Array.isArray(schema) ? schema : [schema]

  const jsonLdObjects = schemas
    .filter((s) => s && s.type) // Filter out undefined/null schemas
    .map((s) => {
      switch (s.type) {
        case 'GovernmentOrganization':
          return buildGovernmentOrganization(s)
        case 'Place':
          return buildPlace(s)
        case 'Dataset':
          return buildDataset(s)
        case 'Article':
          return buildArticle(s)
        case 'BreadcrumbList':
          return buildBreadcrumb(s)
        default:
          return null
      }
    })
    .filter(Boolean)

  // If no valid schemas, return null
  if (jsonLdObjects.length === 0) {
    return null
  }

  return (
    <>
      {jsonLdObjects.map((jsonLd, index) => (
        <script
          key={index}
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify(jsonLd, null, 2),
          }}
        />
      ))}
    </>
  )
}

function buildGovernmentOrganization(schema: GovernmentOrganizationSchema) {
  return {
    '@context': 'https://schema.org',
    '@type': 'GovernmentOrganization',
    name: schema.name,
    ...(schema.description && { description: schema.description }),
    ...(schema.url && { url: schema.url }),
    ...(schema.address && {
      address: {
        '@type': 'PostalAddress',
        ...schema.address,
      },
    }),
    ...(schema.telephone && { telephone: schema.telephone }),
    ...(schema.email && { email: schema.email }),
    ...(schema.areaServed && { areaServed: schema.areaServed }),
  }
}

function buildPlace(schema: PlaceSchema) {
  return {
    '@context': 'https://schema.org',
    '@type': 'Place',
    name: schema.name,
    ...(schema.description && { description: schema.description }),
    ...(schema.url && { url: schema.url }),
    ...(schema.address && {
      address: {
        '@type': 'PostalAddress',
        ...schema.address,
      },
    }),
    ...(schema.geo && {
      geo: {
        '@type': 'GeoCoordinates',
        latitude: schema.geo.latitude,
        longitude: schema.geo.longitude,
      },
    }),
  }
}

function buildDataset(schema: DatasetSchema) {
  return {
    '@context': 'https://schema.org',
    '@type': 'Dataset',
    name: schema.name,
    description: schema.description,
    ...(schema.url && { url: schema.url }),
    ...(schema.creator && {
      creator: {
        '@type': 'Organization',
        name: schema.creator.name,
        ...(schema.creator.url && { url: schema.creator.url }),
      },
    }),
    ...(schema.datePublished && { datePublished: schema.datePublished }),
    ...(schema.dateModified && { dateModified: schema.dateModified }),
    ...(schema.keywords && { keywords: schema.keywords }),
    ...(schema.license && { license: schema.license }),
    ...(schema.distribution && {
      distribution: schema.distribution.map((d) => ({
        '@type': 'DataDownload',
        contentUrl: d.contentUrl,
        encodingFormat: d.encodingFormat,
      })),
    }),
  }
}

function buildArticle(schema: ArticleSchema) {
  return {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: schema.headline,
    ...(schema.description && { description: schema.description }),
    ...(schema.image && { image: schema.image }),
    ...(schema.datePublished && { datePublished: schema.datePublished }),
    ...(schema.dateModified && { dateModified: schema.dateModified }),
    ...(schema.author && {
      author: {
        '@type': 'Person',
        name: schema.author.name,
        ...(schema.author.url && { url: schema.author.url }),
      },
    }),
    ...(schema.publisher && {
      publisher: {
        '@type': 'Organization',
        name: schema.publisher.name,
        ...(schema.publisher.logo && {
          logo: {
            '@type': 'ImageObject',
            url: schema.publisher.logo.url,
            ...(schema.publisher.logo.width && { width: schema.publisher.logo.width }),
            ...(schema.publisher.logo.height && { height: schema.publisher.logo.height }),
          },
        }),
      },
    }),
  }
}

function buildBreadcrumb(schema: BreadcrumbSchema) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: schema.items.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.name,
      item: item.url,
    })),
  }
}
