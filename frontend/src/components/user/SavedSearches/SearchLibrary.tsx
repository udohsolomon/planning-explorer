'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Badge } from '@/components/ui/Badge'
import { Container } from '@/components/ui/Container'
import { SearchCard } from './SearchCard'
import { useUserStore } from '@/stores/userStore'
import {
  Search,
  Plus,
  Filter,
  SortAsc,
  SortDesc,
  Grid,
  List,
  Folder,
  Star,
  Clock
} from 'lucide-react'

const CATEGORIES = [
  'All',
  'Residential',
  'Commercial',
  'Industrial',
  'Mixed Use',
  'Infrastructure',
  'Other'
]

const SORT_OPTIONS = [
  { value: 'name', label: 'Name', icon: SortAsc },
  { value: 'created', label: 'Date Created', icon: Clock },
  { value: 'lastExecuted', label: 'Last Used', icon: Clock },
  { value: 'category', label: 'Category', icon: Folder }
]

export function SearchLibrary() {
  const { savedSearches } = useUserStore()
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [sortBy, setSortBy] = useState('created')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')

  // Filter and sort searches
  const filteredSearches = savedSearches
    .filter(search => {
      const matchesSearch = search.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           search.description?.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesCategory = selectedCategory === 'All' || search.category === selectedCategory
      return matchesSearch && matchesCategory
    })
    .sort((a, b) => {
      let aValue: any
      let bValue: any

      switch (sortBy) {
        case 'name':
          aValue = a.name.toLowerCase()
          bValue = b.name.toLowerCase()
          break
        case 'created':
          aValue = new Date(a.createdAt).getTime()
          bValue = new Date(b.createdAt).getTime()
          break
        case 'lastExecuted':
          aValue = a.lastExecuted ? new Date(a.lastExecuted).getTime() : 0
          bValue = b.lastExecuted ? new Date(b.lastExecuted).getTime() : 0
          break
        case 'category':
          aValue = a.category || 'Other'
          bValue = b.category || 'Other'
          break
        default:
          return 0
      }

      if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1
      if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1
      return 0
    })

  const toggleSortOrder = () => {
    setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Container>
        <div className="py-8">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h1 className="text-3xl font-bold text-planning-primary">
                  Saved Searches
                </h1>
                <p className="text-planning-text-light mt-2">
                  Manage and organize your saved planning searches
                </p>
              </div>
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                New Search
              </Button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center space-x-3">
                    <Search className="w-8 h-8 text-blue-600" />
                    <div>
                      <p className="text-2xl font-bold text-planning-text-dark">
                        {savedSearches.length}
                      </p>
                      <p className="text-sm text-planning-text-light">Total Searches</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center space-x-3">
                    <Star className="w-8 h-8 text-yellow-600" />
                    <div>
                      <p className="text-2xl font-bold text-planning-text-dark">
                        {savedSearches.filter(s => s.isPublic).length}
                      </p>
                      <p className="text-sm text-planning-text-light">Public Searches</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center space-x-3">
                    <Folder className="w-8 h-8 text-green-600" />
                    <div>
                      <p className="text-2xl font-bold text-planning-text-dark">
                        {new Set(savedSearches.map(s => s.category)).size}
                      </p>
                      <p className="text-sm text-planning-text-light">Categories</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center space-x-3">
                    <Clock className="w-8 h-8 text-purple-600" />
                    <div>
                      <p className="text-2xl font-bold text-planning-text-dark">
                        {savedSearches.filter(s => s.lastExecuted).length}
                      </p>
                      <p className="text-sm text-planning-text-light">Recently Used</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Filters and Controls */}
          <Card className="mb-6">
            <CardContent className="p-6">
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
                {/* Search and Filters */}
                <div className="flex flex-col sm:flex-row sm:items-center space-y-4 sm:space-y-0 sm:space-x-4 flex-1">
                  <div className="flex-1 max-w-md">
                    <Input
                      placeholder="Search saved searches..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      leftIcon={<Search />}
                    />
                  </div>

                  <div className="flex items-center space-x-4">
                    {/* Category Filter */}
                    <select
                      value={selectedCategory}
                      onChange={(e) => setSelectedCategory(e.target.value)}
                      className="px-3 py-2 border border-planning-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-planning-primary focus:border-transparent"
                    >
                      {CATEGORIES.map(category => (
                        <option key={category} value={category}>
                          {category}
                        </option>
                      ))}
                    </select>

                    {/* Sort */}
                    <div className="flex items-center space-x-2">
                      <select
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value)}
                        className="px-3 py-2 border border-planning-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-planning-primary focus:border-transparent"
                      >
                        {SORT_OPTIONS.map(option => (
                          <option key={option.value} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={toggleSortOrder}
                      >
                        {sortOrder === 'asc' ? <SortAsc className="w-4 h-4" /> : <SortDesc className="w-4 h-4" />}
                      </Button>
                    </div>
                  </div>
                </div>

                {/* View Controls */}
                <div className="flex items-center space-x-2">
                  <Button
                    variant={viewMode === 'grid' ? 'secondary' : 'ghost'}
                    size="sm"
                    onClick={() => setViewMode('grid')}
                  >
                    <Grid className="w-4 h-4" />
                  </Button>
                  <Button
                    variant={viewMode === 'list' ? 'secondary' : 'ghost'}
                    size="sm"
                    onClick={() => setViewMode('list')}
                  >
                    <List className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Search Results */}
          {filteredSearches.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <Search className="w-16 h-16 text-planning-text-light mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-planning-text-dark mb-2">
                  {searchTerm || selectedCategory !== 'All'
                    ? 'No searches found'
                    : 'No saved searches yet'
                  }
                </h3>
                <p className="text-planning-text-light mb-6">
                  {searchTerm || selectedCategory !== 'All'
                    ? 'Try adjusting your filters or search terms'
                    : 'Start by creating your first saved search to quickly access your favorite queries'
                  }
                </p>
                <Button>
                  <Plus className="w-4 h-4 mr-2" />
                  Create First Search
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className={viewMode === 'grid'
              ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
              : 'space-y-4'
            }>
              {filteredSearches.map((search) => (
                <SearchCard
                  key={search.id}
                  search={search}
                  viewMode={viewMode}
                />
              ))}
            </div>
          )}
        </div>
      </Container>
    </div>
  )
}