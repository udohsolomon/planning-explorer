'use client'

import { useEffect } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { Container } from '@/components/ui/Container'

function createSlug(query: string): string {
  return query
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .substring(0, 60)
}

export default function SearchRedirectPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const query = searchParams.get('q') || ''
  const searchType = searchParams.get('type') || 'semantic'

  useEffect(() => {
    if (query) {
      // Redirect to SEO-friendly URL
      const slug = createSlug(query)
      const params = new URLSearchParams({
        q: query,
        type: searchType
      })
      router.replace(`/search/${slug}?${params.toString()}`)
    } else {
      // If no query, redirect to home
      router.replace('/')
    }
  }, [query, searchType, router])

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <Container>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-planning-primary mx-auto mb-4"></div>
          <p className="text-gray-600">Redirecting to search results...</p>
        </div>
      </Container>
    </div>
  )
}