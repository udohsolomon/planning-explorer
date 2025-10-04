'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { SavedSearch } from '@/types/user'
import { useUserStore } from '@/stores/userStore'
import {
  Search,
  Play,
  Edit,
  Trash2,
  Share,
  Copy,
  MapPin,
  Calendar,
  Clock,
  Eye,
  Star,
  MoreHorizontal,
  Globe,
  Lock
} from 'lucide-react'
import { formatDate } from '@/lib/utils'

interface SearchCardProps {
  search: SavedSearch
  viewMode: 'grid' | 'list'
}

export function SearchCard({ search, viewMode }: SearchCardProps) {
  const [isExecuting, setIsExecuting] = useState(false)
  const { updateSavedSearch, deleteSavedSearch } = useUserStore()

  const handleExecute = async () => {
    setIsExecuting(true)
    try {
      // Simulate search execution
      await new Promise(resolve => setTimeout(resolve, 1000))

      // Update last executed time
      updateSavedSearch(search.id, {
        lastExecuted: new Date().toISOString(),
        resultCount: Math.floor(Math.random() * 100) + 1
      })
    } catch (error) {
      console.error('Failed to execute search:', error)
    } finally {
      setIsExecuting(false)
    }
  }

  const handleDelete = () => {
    if (confirm(`Are you sure you want to delete "${search.name}"?`)) {
      deleteSavedSearch(search.id)
    }
  }

  const handleTogglePublic = () => {
    updateSavedSearch(search.id, {
      isPublic: !search.isPublic
    })
  }

  const handleCopy = () => {
    // Copy search URL to clipboard
    const url = `${window.location.origin}/search?saved=${search.id}`
    navigator.clipboard.writeText(url)
    // Show toast notification
  }

  if (viewMode === 'list') {
    return (
      <Card className="hover:shadow-md transition-shadow">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4 flex-1 min-w-0">
              <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
                <Search className="w-5 h-5 text-blue-600" />
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-1">
                  <h3 className="font-medium text-planning-text-dark truncate">
                    {search.name}
                  </h3>
                  {search.isPublic ? (
                    <Globe className="w-4 h-4 text-green-600" />
                  ) : (
                    <Lock className="w-4 h-4 text-gray-400" />
                  )}
                </div>
                <p className="text-sm text-planning-text-light truncate">
                  {search.description || 'No description'}
                </p>
                <div className="flex items-center space-x-4 mt-2">
                  {search.category && (
                    <Badge variant="outline" size="sm">
                      {search.category}
                    </Badge>
                  )}
                  <span className="text-xs text-planning-text-light">
                    Created {formatDate(search.createdAt)}
                  </span>
                  {search.lastExecuted && (
                    <span className="text-xs text-planning-text-light">
                      Last used {formatDate(search.lastExecuted)}
                    </span>
                  )}
                  {search.resultCount && (
                    <span className="text-xs text-planning-text-light">
                      {search.resultCount} results
                    </span>
                  )}
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleExecute}
                disabled={isExecuting}
              >
                <Play className="w-4 h-4 mr-1" />
                {isExecuting ? 'Running...' : 'Run'}
              </Button>
              <Button variant="ghost" size="sm">
                <Edit className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm" onClick={handleCopy}>
                <Share className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm" onClick={handleDelete}>
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
              <Search className="w-5 h-5 text-blue-600" />
            </div>
            <div className="flex-1 min-w-0">
              <CardTitle className="text-lg truncate">{search.name}</CardTitle>
              {search.category && (
                <Badge variant="outline" size="sm" className="mt-1">
                  {search.category}
                </Badge>
              )}
            </div>
          </div>
          <div className="flex items-center space-x-1">
            {search.isPublic ? (
              <Globe className="w-4 h-4 text-green-600" />
            ) : (
              <Lock className="w-4 h-4 text-gray-400" />
            )}
            <button className="p-1 text-planning-text-light hover:text-planning-primary">
              <MoreHorizontal className="w-4 h-4" />
            </button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        <p className="text-sm text-planning-text-light mb-4 line-clamp-2">
          {search.description || 'No description provided'}
        </p>

        {/* Search Details */}
        <div className="space-y-2 mb-4">
          {search.query.location && (
            <div className="flex items-center space-x-2 text-sm">
              <MapPin className="w-4 h-4 text-planning-text-light" />
              <span className="text-planning-text-light">
                Within {search.query.location.radius} miles
              </span>
            </div>
          )}

          <div className="flex items-center space-x-2 text-sm">
            <Calendar className="w-4 h-4 text-planning-text-light" />
            <span className="text-planning-text-light">
              Created {formatDate(search.createdAt)}
            </span>
          </div>

          {search.lastExecuted && (
            <div className="flex items-center space-x-2 text-sm">
              <Clock className="w-4 h-4 text-planning-text-light" />
              <span className="text-planning-text-light">
                Last used {formatDate(search.lastExecuted)}
              </span>
            </div>
          )}

          {search.resultCount && (
            <div className="flex items-center space-x-2 text-sm">
              <Eye className="w-4 h-4 text-planning-text-light" />
              <span className="text-planning-text-light">
                {search.resultCount} results found
              </span>
            </div>
          )}
        </div>

        {/* Performance Indicator */}
        {search.performance && (
          <div className="mb-4 p-2 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between text-xs">
              <span className="text-planning-text-light">Performance</span>
              <div className="flex items-center space-x-2">
                <span className="text-planning-text-light">
                  {search.performance.avgResponseTime}ms avg
                </span>
                <div className="flex items-center space-x-1">
                  <Star className="w-3 h-3 text-yellow-500" />
                  <span>{Math.round(search.performance.successRate * 100)}%</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tags */}
        {search.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-4">
            {search.tags.slice(0, 3).map((tag) => (
              <Badge key={tag} variant="secondary" size="sm" className="text-xs">
                {tag}
              </Badge>
            ))}
            {search.tags.length > 3 && (
              <Badge variant="outline" size="sm" className="text-xs">
                +{search.tags.length - 3}
              </Badge>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex space-x-2">
          <Button
            className="flex-1"
            onClick={handleExecute}
            disabled={isExecuting}
          >
            <Play className="w-4 h-4 mr-2" />
            {isExecuting ? 'Running...' : 'Run Search'}
          </Button>
          <Button variant="outline" size="sm">
            <Edit className="w-4 h-4" />
          </Button>
          <Button variant="outline" size="sm" onClick={handleCopy}>
            <Copy className="w-4 h-4" />
          </Button>
        </div>

        {/* Secondary Actions */}
        <div className="flex justify-between items-center mt-3 pt-3 border-t border-gray-100">
          <button
            onClick={handleTogglePublic}
            className="text-xs text-planning-primary hover:text-planning-accent"
          >
            Make {search.isPublic ? 'Private' : 'Public'}
          </button>
          <button
            onClick={handleDelete}
            className="text-xs text-red-600 hover:text-red-700"
          >
            Delete
          </button>
        </div>
      </CardContent>
    </Card>
  )
}