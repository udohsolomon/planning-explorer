import React from 'react'
import {
  AlertCircle,
  Wifi,
  Server,
  Shield,
  Clock,
  Search,
  MapPin,
  RefreshCw,
  ArrowRight,
  Lightbulb,
  HelpCircle
} from 'lucide-react'
import { Button } from './Button'
import { ErrorInfo, ErrorType } from '@/lib/errors'
import { SearchSuggestions } from '../SearchSuggestions'
import { cn } from '@/lib/utils'

interface ErrorStateProps {
  errorInfo: ErrorInfo
  onRetry?: () => void
  onGoHome?: () => void
  onContactSupport?: () => void
  className?: string
  compact?: boolean
}

// Error type to icon mapping
const errorIcons = {
  [ErrorType.NETWORK]: Wifi,
  [ErrorType.API_ERROR]: Server,
  [ErrorType.AUTHENTICATION]: Shield,
  [ErrorType.RATE_LIMIT]: Clock,
  [ErrorType.VALIDATION]: AlertCircle,
  [ErrorType.NOT_FOUND]: Search,
  [ErrorType.SERVER_ERROR]: Server,
  [ErrorType.TIMEOUT]: Clock,
  [ErrorType.NO_RESULTS]: Search,
  [ErrorType.ELASTICSEARCH]: Server,
  [ErrorType.UNKNOWN]: AlertCircle
}

// Error type to color mapping
const errorColors = {
  [ErrorType.NETWORK]: 'text-orange-500 bg-orange-50 border-orange-200',
  [ErrorType.API_ERROR]: 'text-red-500 bg-red-50 border-red-200',
  [ErrorType.AUTHENTICATION]: 'text-blue-500 bg-blue-50 border-blue-200',
  [ErrorType.RATE_LIMIT]: 'text-yellow-500 bg-yellow-50 border-yellow-200',
  [ErrorType.VALIDATION]: 'text-purple-500 bg-purple-50 border-purple-200',
  [ErrorType.NOT_FOUND]: 'text-gray-500 bg-gray-50 border-gray-200',
  [ErrorType.SERVER_ERROR]: 'text-red-500 bg-red-50 border-red-200',
  [ErrorType.TIMEOUT]: 'text-orange-500 bg-orange-50 border-orange-200',
  [ErrorType.NO_RESULTS]: 'text-gray-500 bg-gray-50 border-gray-200',
  [ErrorType.ELASTICSEARCH]: 'text-red-500 bg-red-50 border-red-200',
  [ErrorType.UNKNOWN]: 'text-gray-500 bg-gray-50 border-gray-200'
}

export function ErrorState({
  errorInfo,
  onRetry,
  onGoHome,
  onContactSupport,
  className,
  compact = false
}: ErrorStateProps) {
  const IconComponent = errorIcons[errorInfo.type]
  const colorClasses = errorColors[errorInfo.type]

  if (compact) {
    return (
      <div className={cn(
        'bg-white border rounded-lg p-4',
        colorClasses,
        className
      )}>
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            <IconComponent className="w-5 h-5" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium">
              {errorInfo.title}
            </p>
            <p className="text-sm opacity-75 mt-1">
              {errorInfo.message}
            </p>
            {errorInfo.canRetry && onRetry && (
              <Button
                onClick={onRetry}
                variant="outline"
                size="sm"
                className="mt-2"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Try Again
              </Button>
            )}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={cn(
      'bg-white rounded-xl shadow-sm border p-8 text-center max-w-2xl mx-auto',
      className
    )}>
      {/* Error Icon */}
      <div className={cn(
        'w-16 h-16 rounded-full mx-auto mb-6 flex items-center justify-center border-2',
        colorClasses
      )}>
        <IconComponent className="w-8 h-8" />
      </div>

      {/* Error Title and Message */}
      <div className="mb-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          {errorInfo.title}
        </h3>
        <p className="text-gray-600 leading-relaxed">
          {errorInfo.message}
        </p>
      </div>

      {/* Suggestions */}
      {errorInfo.suggestions.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 text-left">
          <div className="flex items-center mb-3">
            <Lightbulb className="w-5 h-5 text-blue-600 mr-2" />
            <h4 className="font-medium text-blue-900">Helpful Suggestions</h4>
          </div>
          <ul className="space-y-2">
            {errorInfo.suggestions.map((suggestion, index) => (
              <li key={index} className="flex items-start">
                <ArrowRight className="w-4 h-4 text-blue-500 mr-2 mt-0.5 flex-shrink-0" />
                <span className="text-sm text-blue-800">{suggestion}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-3 justify-center">
        {/* Primary actions */}
        {errorInfo.canRetry && onRetry && (
          <Button
            onClick={onRetry}
            variant="primary"
            size="md"
            className="flex items-center"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Try Again
          </Button>
        )}

        {/* Custom actions from errorInfo */}
        {errorInfo.actions.map((action, index) => (
          <Button
            key={index}
            onClick={action.action}
            variant={action.variant || 'outline'}
            size="md"
          >
            {action.label}
          </Button>
        ))}

        {/* Secondary actions */}
        {onGoHome && (
          <Button
            onClick={onGoHome}
            variant="outline"
            size="md"
          >
            <MapPin className="w-4 h-4 mr-2" />
            Back to Search
          </Button>
        )}
      </div>

      {/* Contact Support Link */}
      {onContactSupport && (
        <div className="mt-6 pt-6 border-t">
          <button
            onClick={onContactSupport}
            className="text-sm text-gray-500 hover:text-planning-primary transition-colors flex items-center mx-auto"
          >
            <HelpCircle className="w-4 h-4 mr-1" />
            Still having issues? Contact our support team
          </button>
        </div>
      )}
    </div>
  )
}

// Specialized component for search-specific errors
interface SearchErrorStateProps {
  errorInfo: ErrorInfo
  searchQuery: string
  onRetry?: () => void
  onNewSearch?: (query: string) => void
  onGoHome?: () => void
  onContactSupport?: () => void
  className?: string
}

export function SearchErrorState({
  errorInfo,
  searchQuery,
  onRetry,
  onNewSearch,
  onGoHome,
  onContactSupport,
  className
}: SearchErrorStateProps) {
  const handleSuggestionClick = (suggestion: string) => {
    if (onNewSearch) {
      // Extract searchable terms from suggestion text
      const searchMatch = suggestion.match(/"([^"]+)"/);
      if (searchMatch) {
        onNewSearch(searchMatch[1]);
      }
    }
  };

  return (
    <div className={cn(
      'bg-white rounded-xl shadow-sm border p-8 text-center max-w-2xl mx-auto',
      className
    )}>
      {/* Search Context */}
      <div className="mb-6">
        <div className="bg-gray-50 rounded-lg px-4 py-3 mb-4">
          <div className="flex items-center justify-center text-sm text-gray-600">
            <Search className="w-4 h-4 mr-2" />
            <span>Searched for: </span>
            <span className="font-medium text-gray-900 ml-1">"{searchQuery}"</span>
          </div>
        </div>
      </div>

      {/* Error State */}
      <ErrorState
        errorInfo={errorInfo}
        onRetry={onRetry}
        onGoHome={onGoHome}
        onContactSupport={onContactSupport}
        className="border-0 shadow-none p-0"
      />

      {/* Enhanced Search Suggestions */}
      {(errorInfo.type === ErrorType.NOT_FOUND || errorInfo.type === 'no_results') && onNewSearch && (
        <div className="mt-6 pt-6 border-t">
          <SearchSuggestions
            originalQuery={searchQuery}
            onSuggestionClick={onNewSearch}
          />
        </div>
      )}
    </div>
  )
}