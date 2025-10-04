import React from 'react'
import { Search, MapPin, Building2, Home, Store, Factory } from 'lucide-react'
import { Button } from './ui/Button'

interface SearchSuggestionsProps {
  originalQuery: string
  onSuggestionClick: (suggestion: string) => void
  className?: string
}

interface Suggestion {
  query: string
  label: string
  icon: React.ComponentType<any>
  category: string
}

export function SearchSuggestions({ originalQuery, onSuggestionClick, className }: SearchSuggestionsProps) {
  // Generate contextual suggestions based on the original query
  const generateSuggestions = (query: string): Suggestion[] => {
    const suggestions: Suggestion[] = []
    const lowerQuery = query.toLowerCase()

    // Location-based suggestions
    if (lowerQuery.includes('london')) {
      suggestions.push(
        { query: 'Westminster housing', label: 'Westminster Housing', icon: Home, category: 'London Areas' },
        { query: 'Camden residential', label: 'Camden Residential', icon: Building2, category: 'London Areas' },
        { query: 'Tower Hamlets apartments', label: 'Tower Hamlets Apartments', icon: Home, category: 'London Areas' }
      )
    } else if (lowerQuery.includes('manchester')) {
      suggestions.push(
        { query: 'Manchester city centre', label: 'City Centre', icon: Building2, category: 'Manchester Areas' },
        { query: 'Salford residential', label: 'Salford Residential', icon: Home, category: 'Manchester Areas' },
        { query: 'Trafford commercial', label: 'Trafford Commercial', icon: Store, category: 'Manchester Areas' }
      )
    } else if (lowerQuery.includes('birmingham')) {
      suggestions.push(
        { query: 'Birmingham city centre', label: 'City Centre', icon: Building2, category: 'Birmingham Areas' },
        { query: 'Solihull housing', label: 'Solihull Housing', icon: Home, category: 'Birmingham Areas' },
        { query: 'Edgbaston residential', label: 'Edgbaston Residential', icon: Home, category: 'Birmingham Areas' }
      )
    }

    // Property type suggestions
    if (lowerQuery.includes('residential') || lowerQuery.includes('housing') || lowerQuery.includes('homes')) {
      suggestions.push(
        { query: 'new apartments', label: 'New Apartments', icon: Building2, category: 'Residential' },
        { query: 'housing developments', label: 'Housing Developments', icon: Home, category: 'Residential' },
        { query: 'residential extensions', label: 'Extensions', icon: Home, category: 'Residential' }
      )
    } else if (lowerQuery.includes('commercial') || lowerQuery.includes('office') || lowerQuery.includes('retail')) {
      suggestions.push(
        { query: 'office buildings', label: 'Office Buildings', icon: Building2, category: 'Commercial' },
        { query: 'retail developments', label: 'Retail Developments', icon: Store, category: 'Commercial' },
        { query: 'commercial premises', label: 'Commercial Premises', icon: Building2, category: 'Commercial' }
      )
    } else if (lowerQuery.includes('industrial')) {
      suggestions.push(
        { query: 'industrial units', label: 'Industrial Units', icon: Factory, category: 'Industrial' },
        { query: 'warehouse developments', label: 'Warehouses', icon: Factory, category: 'Industrial' },
        { query: 'manufacturing facilities', label: 'Manufacturing', icon: Factory, category: 'Industrial' }
      )
    }

    // Popular general suggestions if no specific matches
    if (suggestions.length === 0) {
      suggestions.push(
        { query: 'approved developments', label: 'Approved Developments', icon: Building2, category: 'Popular' },
        { query: 'London residential', label: 'London Residential', icon: Home, category: 'Popular' },
        { query: 'commercial applications', label: 'Commercial Applications', icon: Store, category: 'Popular' },
        { query: 'housing developments', label: 'Housing Developments', icon: Home, category: 'Popular' }
      )
    }

    return suggestions.slice(0, 6) // Limit to 6 suggestions
  }

  const suggestions = generateSuggestions(originalQuery)

  // Group suggestions by category
  const groupedSuggestions = suggestions.reduce((groups, suggestion) => {
    const { category } = suggestion
    if (!groups[category]) {
      groups[category] = []
    }
    groups[category].push(suggestion)
    return groups
  }, {} as Record<string, Suggestion[]>)

  return (
    <div className={className}>
      <div className="text-center mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Try These Popular Searches
        </h3>
        <p className="text-sm text-gray-600">
          Based on your search, here are some suggestions that might help
        </p>
      </div>

      <div className="space-y-4">
        {Object.entries(groupedSuggestions).map(([category, categorySuggestions]) => (
          <div key={category}>
            <h4 className="text-sm font-medium text-gray-700 mb-2">{category}</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {categorySuggestions.map((suggestion) => {
                const IconComponent = suggestion.icon
                return (
                  <button
                    key={suggestion.query}
                    onClick={() => onSuggestionClick(suggestion.query)}
                    className="flex items-center p-3 bg-white border border-gray-200 rounded-lg hover:border-planning-primary hover:bg-planning-primary/5 transition-all duration-200 text-left group"
                  >
                    <div className="flex-shrink-0 w-8 h-8 bg-planning-primary/10 rounded-lg flex items-center justify-center mr-3 group-hover:bg-planning-primary/20 transition-colors">
                      <IconComponent className="w-4 h-4 text-planning-primary" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900 group-hover:text-planning-primary transition-colors">
                        {suggestion.label}
                      </p>
                    </div>
                  </button>
                )
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Quick Search Tips */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-start">
          <Search className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
          <div>
            <h4 className="text-sm font-medium text-blue-900 mb-1">Search Tips</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Use specific locations (e.g., "Camden", "Birmingham city centre")</li>
              <li>• Include property types (e.g., "apartments", "offices", "retail")</li>
              <li>• Try postcode searches for precise results (e.g., "M1 1AA")</li>
              <li>• Use natural language (e.g., "new housing in Manchester")</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}