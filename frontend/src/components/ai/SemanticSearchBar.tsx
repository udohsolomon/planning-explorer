'use client'

import { useState, useEffect, useRef } from 'react'
import { Search, Brain, Sparkles, MapPin, Filter, History, Zap, MessageSquare } from 'lucide-react'
import { useSearchStore } from '@/lib/store'
import { apiClient } from '@/lib/api'
import { useRouter } from 'next/navigation'

interface SemanticSearchBarProps {
  placeholder?: string
  showSuggestions?: boolean
  showSearchType?: boolean
  autoFocus?: boolean
  className?: string
  onSearch?: (query: string, searchType: 'traditional' | 'semantic' | 'natural_language') => void
}

export function SemanticSearchBar({
  placeholder = "Try: 'Show me approved residential developments in London from 2024'",
  showSuggestions = true,
  showSearchType = true,
  autoFocus = false,
  className = '',
  onSearch
}: SemanticSearchBarProps) {
  const router = useRouter()
  const [isActive, setIsActive] = useState(false)
  const [showDropdown, setShowDropdown] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const {
    query,
    searchType,
    suggestions,
    isLoadingSuggestions,
    setQuery,
    setSearchType,
    setSuggestions,
    setLoadingSuggestions
  } = useSearchStore()

  useEffect(() => {
    if (autoFocus && inputRef.current) {
      inputRef.current.focus()
    }
  }, [autoFocus])

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Debounce suggestions
  useEffect(() => {
    if (!query.trim() || query.length < 2) {
      setSuggestions({
        queries: [],
        addresses: [],
        authorities: [],
        developmentTypes: [],
        smartSuggestions: []
      })
      return
    }

    const timeoutId = setTimeout(async () => {
      if (showSuggestions) {
        setLoadingSuggestions(true)
        try {
          const response = await apiClient.getSearchSuggestions(query, 8)
          if (response.success) {
            setSuggestions(response.data)
          }
        } catch (error) {
          console.error('Failed to get suggestions:', error)
        } finally {
          setLoadingSuggestions(false)
        }
      }
    }, 300)

    return () => clearTimeout(timeoutId)
  }, [query, showSuggestions, setSuggestions, setLoadingSuggestions])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setQuery(value)
    if (value.trim() && showSuggestions) {
      setShowDropdown(true)
    } else {
      setShowDropdown(false)
    }
  }

  const handleSearch = () => {
    if (query.trim()) {
      if (onSearch) {
        onSearch(query, searchType)
      }

      // Always navigate to search page
      const params = new URLSearchParams({
        q: query,
        type: searchType
      })
      router.push(`/search?${params.toString()}`)
      setShowDropdown(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch()
    } else if (e.key === 'Escape') {
      setShowDropdown(false)
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion)
    setShowDropdown(false)

    if (onSearch) {
      onSearch(suggestion, searchType)
    }

    // Always navigate to search page
    const params = new URLSearchParams({
      q: suggestion,
      type: searchType
    })
    router.push(`/search?${params.toString()}`)
  }

  const searchTypeOptions = [
    {
      value: 'traditional' as const,
      label: 'Traditional',
      icon: Search,
      description: 'Keyword-based search'
    },
    {
      value: 'semantic' as const,
      label: 'Semantic',
      icon: Brain,
      description: 'AI-powered meaning search'
    },
    {
      value: 'natural_language' as const,
      label: 'Natural Language',
      icon: MessageSquare,
      description: 'Ask questions naturally'
    }
  ]

  const getSearchTypeIcon = () => {
    const option = searchTypeOptions.find(opt => opt.value === searchType)
    const IconComponent = option?.icon || Search
    return <IconComponent className="w-4 h-4" />
  }

  const getSearchTypeColor = () => {
    switch (searchType) {
      case 'semantic':
        return 'text-planning-bright'
      case 'natural_language':
        return 'text-planning-highlight'
      default:
        return 'text-planning-accent'
    }
  }

  const exampleQueries = [
    "Show me approved residential developments in London",
    "Find commercial applications submitted this year",
    "What extensions were approved near SW1A 1AA?",
    "Planning applications with high opportunity scores",
    "Recent refusals for housing developments"
  ]

  return (
    <div className={`relative ${className}`}>
      <div className={`relative bg-white rounded-xl border-2 transition-all duration-200 ${
        isActive
          ? 'border-planning-primary shadow-lg'
          : 'border-planning-border hover:border-planning-accent'
      }`}>
        {/* Search Type Selector */}
        {showSearchType && (
          <div className="flex border-b border-planning-border">
            {searchTypeOptions.map((option) => {
              const IconComponent = option.icon
              return (
                <button
                  key={option.value}
                  onClick={() => setSearchType(option.value)}
                  className={`flex-1 flex items-center justify-center space-x-2 px-4 py-3 text-sm transition-colors ${
                    searchType === option.value
                      ? 'bg-planning-primary text-white'
                      : 'text-planning-text-light hover:bg-planning-primary/5 hover:text-planning-primary'
                  }`}
                  title={option.description}
                >
                  <IconComponent className="w-4 h-4" />
                  <span className="font-medium">{option.label}</span>
                  {searchType === option.value && searchType !== 'traditional' && (
                    <Sparkles className="w-3 h-3" />
                  )}
                </button>
              )
            })}
          </div>
        )}

        {/* Search Input */}
        <div className="flex items-center p-4">
          <div className={`mr-3 ${getSearchTypeColor()}`}>
            {getSearchTypeIcon()}
          </div>

          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            onFocus={() => {
              setIsActive(true)
              if (query.trim() && showSuggestions) {
                setShowDropdown(true)
              }
            }}
            onBlur={() => setIsActive(false)}
            placeholder={placeholder}
            className="flex-1 text-lg placeholder-planning-text-light focus:outline-none"
          />

          {query && (
            <button
              onClick={() => setQuery('')}
              className="mr-3 p-1 text-planning-text-light hover:text-planning-primary transition-colors"
            >
              ×
            </button>
          )}

          <button
            onClick={handleSearch}
            disabled={!query.trim()}
            className="px-6 py-2 bg-planning-button text-white rounded-lg hover:bg-planning-primary hover:text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Search
          </button>
        </div>

        {/* AI Enhancement Indicator */}
        {searchType !== 'traditional' && (
          <div className="px-4 pb-2">
            <div className="flex items-center space-x-2 text-xs text-planning-text-light">
              <Zap className="w-3 h-3 text-planning-bright" />
              <span>
                {searchType === 'semantic'
                  ? 'AI-powered semantic search will find similar meanings'
                  : 'Natural language processing will understand your question'
                }
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Search Suggestions Dropdown */}
      {showDropdown && showSuggestions && (
        <div
          ref={dropdownRef}
          className="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl border border-planning-border shadow-lg z-50 max-h-96 overflow-y-auto"
        >
          {isLoadingSuggestions ? (
            <div className="p-4 text-center">
              <div className="w-6 h-6 border-2 border-planning-primary border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
              <p className="text-sm text-planning-text-light">Loading suggestions...</p>
            </div>
          ) : (
            <div className="p-2">
              {/* Smart AI Suggestions */}
              {suggestions.smartSuggestions.length > 0 && (
                <div className="mb-4">
                  <h4 className="px-3 py-2 text-xs font-medium text-planning-primary uppercase tracking-wider flex items-center space-x-2">
                    <Sparkles className="w-3 h-3" />
                    <span>AI Suggestions</span>
                  </h4>
                  {suggestions.smartSuggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="w-full text-left px-3 py-2 hover:bg-planning-primary/5 rounded-lg transition-colors"
                    >
                      <div className="flex items-center space-x-3">
                        <Brain className="w-4 h-4 text-planning-bright flex-shrink-0" />
                        <span className="text-sm text-planning-text-dark">{suggestion}</span>
                      </div>
                    </button>
                  ))}
                </div>
              )}

              {/* Quick Suggestions */}
              {suggestions.queries.length > 0 && (
                <div className="mb-4">
                  <h4 className="px-3 py-2 text-xs font-medium text-planning-primary uppercase tracking-wider flex items-center space-x-2">
                    <Search className="w-3 h-3" />
                    <span>Search Suggestions</span>
                  </h4>
                  {suggestions.queries.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="w-full text-left px-3 py-2 hover:bg-planning-primary/5 rounded-lg transition-colors"
                    >
                      <div className="flex items-center space-x-3">
                        <History className="w-4 h-4 text-planning-text-light flex-shrink-0" />
                        <span className="text-sm text-planning-text-dark">{suggestion}</span>
                      </div>
                    </button>
                  ))}
                </div>
              )}

              {/* Location Suggestions */}
              {(suggestions.addresses.length > 0 || suggestions.authorities.length > 0) && (
                <div className="mb-4">
                  <h4 className="px-3 py-2 text-xs font-medium text-planning-primary uppercase tracking-wider flex items-center space-x-2">
                    <MapPin className="w-3 h-3" />
                    <span>Locations</span>
                  </h4>
                  {[...suggestions.addresses, ...suggestions.authorities].map((location, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionClick(location)}
                      className="w-full text-left px-3 py-2 hover:bg-planning-primary/5 rounded-lg transition-colors"
                    >
                      <div className="flex items-center space-x-3">
                        <MapPin className="w-4 h-4 text-planning-accent flex-shrink-0" />
                        <span className="text-sm text-planning-text-dark">{location}</span>
                      </div>
                    </button>
                  ))}
                </div>
              )}

              {/* Development Type Suggestions */}
              {suggestions.developmentTypes.length > 0 && (
                <div className="mb-4">
                  <h4 className="px-3 py-2 text-xs font-medium text-planning-primary uppercase tracking-wider flex items-center space-x-2">
                    <Filter className="w-3 h-3" />
                    <span>Development Types</span>
                  </h4>
                  {suggestions.developmentTypes.map((type, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionClick(type)}
                      className="w-full text-left px-3 py-2 hover:bg-planning-primary/5 rounded-lg transition-colors"
                    >
                      <div className="flex items-center space-x-3">
                        <Filter className="w-4 h-4 text-planning-text-light flex-shrink-0" />
                        <span className="text-sm text-planning-text-dark capitalize">{type}</span>
                      </div>
                    </button>
                  ))}
                </div>
              )}

              {/* Example Queries (when no suggestions) */}
              {Object.values(suggestions).every(arr => arr.length === 0) && !isLoadingSuggestions && (
                <div>
                  <h4 className="px-3 py-2 text-xs font-medium text-planning-primary uppercase tracking-wider">
                    Try These Examples
                  </h4>
                  {exampleQueries.map((example, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionClick(example)}
                      className="w-full text-left px-3 py-2 hover:bg-planning-primary/5 rounded-lg transition-colors"
                    >
                      <div className="flex items-center space-x-3">
                        <MessageSquare className="w-4 h-4 text-planning-highlight flex-shrink-0" />
                        <span className="text-sm text-planning-text-dark">{example}</span>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}