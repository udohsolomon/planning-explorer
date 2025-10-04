'use client'

import { useState, useMemo } from 'react'
import Link from 'next/link'
import { Container } from '@/components/ui/Container'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Badge } from '@/components/ui/Badge'
import { getAllAuthorities, searchAuthorities } from '@/lib/content-discovery-api'
import { AuthorityListItem } from '@/types/content-discovery'

export default function AuthoritiesListPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedRegion, setSelectedRegion] = useState<string>('all')

  // Get all authorities
  const allAuthorities = useMemo(() => getAllAuthorities(), [])

  // Get unique regions
  const regions = useMemo(() => {
    const regionSet = new Set<string>()
    allAuthorities.forEach((auth) => {
      if (auth.region) regionSet.add(auth.region)
    })
    return Array.from(regionSet).sort()
  }, [allAuthorities])

  // Filter authorities based on search and region
  const filteredAuthorities = useMemo(() => {
    let filtered = searchAuthorities(searchQuery, allAuthorities)

    if (selectedRegion !== 'all') {
      filtered = filtered.filter((auth) => auth.region === selectedRegion)
    }

    return filtered.sort((a, b) => a.name.localeCompare(b.name))
  }, [searchQuery, selectedRegion, allAuthorities])

  // Group authorities by region
  const groupedAuthorities = useMemo(() => {
    const groups: Record<string, AuthorityListItem[]> = {}

    filteredAuthorities.forEach((auth) => {
      const region = auth.region || 'Other'
      if (!groups[region]) {
        groups[region] = []
      }
      groups[region].push(auth)
    })

    return groups
  }, [filteredAuthorities])

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header Section */}
      <div className="bg-white border-b border-gray-200">
        <Container className="py-12">
          <div className="max-w-3xl">
            <h1 className="text-4xl font-bold text-planning-primary mb-4">
              UK Planning Authorities
            </h1>
            <p className="text-lg text-gray-600 mb-6">
              Explore planning statistics and insights for {allAuthorities.length} local planning authorities across the UK.
              View application trends, approval rates, and sector breakdowns.
            </p>

            {/* Search Bar */}
            <div className="relative">
              <Input
                type="text"
                placeholder="Search authorities by name or region..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 text-base"
              />
              <svg
                className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>
          </div>
        </Container>
      </div>

      {/* Filters and Results */}
      <Container className="py-8">
        {/* Region Filter Pills */}
        <div className="mb-8">
          <p className="text-sm font-medium text-gray-700 mb-3">Filter by Region:</p>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedRegion('all')}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                selectedRegion === 'all'
                  ? 'bg-planning-primary text-white'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              All Regions ({allAuthorities.length})
            </button>
            {regions.map((region) => {
              const count = allAuthorities.filter((a) => a.region === region).length
              return (
                <button
                  key={region}
                  onClick={() => setSelectedRegion(region)}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                    selectedRegion === region
                      ? 'bg-planning-primary text-white'
                      : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  {region} ({count})
                </button>
              )
            })}
          </div>
        </div>

        {/* Results Count */}
        <div className="mb-6">
          <p className="text-sm text-gray-600">
            Showing <span className="font-semibold text-planning-primary">{filteredAuthorities.length}</span> authorities
            {searchQuery && ` matching "${searchQuery}"`}
            {selectedRegion !== 'all' && ` in ${selectedRegion}`}
          </p>
        </div>

        {/* Authorities Grid (Grouped by Region) */}
        {filteredAuthorities.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <svg
                className="w-16 h-16 text-gray-300 mx-auto mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <h3 className="text-lg font-semibold text-gray-700 mb-2">No Authorities Found</h3>
              <p className="text-gray-600 mb-4">Try adjusting your search or filter criteria</p>
              <button
                onClick={() => {
                  setSearchQuery('')
                  setSelectedRegion('all')
                }}
                className="inline-flex items-center justify-center rounded-md bg-planning-primary px-4 py-2 text-sm font-medium text-white hover:bg-planning-secondary transition-colors"
              >
                Clear Filters
              </button>
            </CardContent>
          </Card>
        ) : selectedRegion === 'all' ? (
          // Show grouped by region
          <div className="space-y-8">
            {Object.entries(groupedAuthorities)
              .sort(([a], [b]) => a.localeCompare(b))
              .map(([region, authorities]) => (
                <div key={region}>
                  <h2 className="text-2xl font-bold text-planning-primary mb-4">{region}</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {authorities.map((authority) => (
                      <Link key={authority.slug} href={`/authorities/${authority.slug}`}>
                        <Card className="h-full hover:shadow-lg transition-shadow cursor-pointer hover:border-planning-primary">
                          <CardHeader>
                            <div className="flex items-start justify-between gap-2">
                              <CardTitle className="text-base leading-tight">{authority.name}</CardTitle>
                              <svg
                                className="w-5 h-5 text-planning-primary flex-shrink-0"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                              >
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2}
                                  d="M9 5l7 7-7 7"
                                />
                              </svg>
                            </div>
                          </CardHeader>
                          <CardContent>
                            {authority.region && (
                              <Badge variant="outline" size="sm">
                                {authority.region}
                              </Badge>
                            )}
                            <p className="text-xs text-gray-500 mt-2">
                              Click to view detailed statistics
                            </p>
                          </CardContent>
                        </Card>
                      </Link>
                    ))}
                  </div>
                </div>
              ))}
          </div>
        ) : (
          // Show flat list for selected region
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filteredAuthorities.map((authority) => (
              <Link key={authority.slug} href={`/authorities/${authority.slug}`}>
                <Card className="h-full hover:shadow-lg transition-shadow cursor-pointer hover:border-planning-primary">
                  <CardHeader>
                    <div className="flex items-start justify-between gap-2">
                      <CardTitle className="text-base leading-tight">{authority.name}</CardTitle>
                      <svg
                        className="w-5 h-5 text-planning-primary flex-shrink-0"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 5l7 7-7 7"
                        />
                      </svg>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {authority.region && (
                      <Badge variant="outline" size="sm">
                        {authority.region}
                      </Badge>
                    )}
                    <p className="text-xs text-gray-500 mt-2">
                      Click to view detailed statistics
                    </p>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </Container>
    </div>
  )
}
