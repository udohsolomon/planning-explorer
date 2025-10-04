import React, { useState } from 'react'
import { ErrorState, SearchErrorState } from './ui/ErrorState'
import { ErrorType, ErrorInfo } from '@/lib/errors'
import { Button } from './ui/Button'

// Demo component to test different error states
export function ErrorStateDemo() {
  const [selectedError, setSelectedError] = useState<ErrorType>(ErrorType.NETWORK)

  const errorExamples: Record<ErrorType, ErrorInfo> = {
    [ErrorType.NETWORK]: {
      type: ErrorType.NETWORK,
      title: 'Connection Problem',
      message: 'Unable to connect to Planning Explorer servers. Please check your internet connection.',
      suggestions: [
        'Check your internet connection',
        'Try refreshing the page',
        'Contact support if the problem persists'
      ],
      actions: [],
      canRetry: true,
      retryDelay: 3000
    },
    [ErrorType.RATE_LIMIT]: {
      type: ErrorType.RATE_LIMIT,
      title: 'Search Limit Reached',
      message: 'You\'ve reached your search limit. Upgrade your plan for unlimited searches.',
      suggestions: [
        'Wait a few minutes before searching again',
        'Upgrade to Professional plan (£199.99/month)',
        'Sign up for Enterprise plan (£499.99/month)'
      ],
      actions: [],
      canRetry: true,
      retryDelay: 60000
    },
    [ErrorType.AUTHENTICATION]: {
      type: ErrorType.AUTHENTICATION,
      title: 'Authentication Required',
      message: 'Please sign in to access advanced search features.',
      suggestions: [
        'Sign in to your account',
        'Create a free account for basic searches',
        'Upgrade to Professional for unlimited access'
      ],
      actions: [],
      canRetry: false
    },
    [ErrorType.NOT_FOUND]: {
      type: ErrorType.NOT_FOUND,
      title: 'No Planning Data Found',
      message: 'No planning applications match your search criteria in our database.',
      suggestions: [
        'Try broader search terms',
        'Search in nearby areas',
        'Check if the location name is spelled correctly',
        'Try searching by postcode instead'
      ],
      actions: [],
      canRetry: false
    },
    [ErrorType.SERVER_ERROR]: {
      type: ErrorType.SERVER_ERROR,
      title: 'Server Error',
      message: 'Our servers are experiencing issues. Please try again in a few moments.',
      suggestions: [
        'Try again in a few minutes',
        'Check our status page for updates',
        'Contact support if the problem persists'
      ],
      actions: [],
      canRetry: true,
      retryDelay: 10000
    },
    [ErrorType.TIMEOUT]: {
      type: ErrorType.TIMEOUT,
      title: 'Search Timeout',
      message: 'Your search is taking too long. Try a more specific search query.',
      suggestions: [
        'Use more specific search terms',
        'Search in a smaller area',
        'Try searching by postcode',
        'Switch to basic search mode'
      ],
      actions: [],
      canRetry: true,
      retryDelay: 3000
    },
    [ErrorType.VALIDATION]: {
      type: ErrorType.VALIDATION,
      title: 'Invalid Search Query',
      message: 'Your search query contains invalid parameters. Please revise your search terms.',
      suggestions: [
        'Use simpler search terms',
        'Check for typos in location names',
        'Try searching for specific planning application types'
      ],
      actions: [],
      canRetry: false
    },
    [ErrorType.ELASTICSEARCH]: {
      type: ErrorType.ELASTICSEARCH,
      title: 'Search Service Unavailable',
      message: 'Our search service is temporarily unavailable. Please try a simpler search.',
      suggestions: [
        'Try using basic keyword search instead of AI search',
        'Use fewer search terms',
        'Search by location only',
        'Try again in a few minutes'
      ],
      actions: [],
      canRetry: true,
      retryDelay: 5000
    },
    [ErrorType.API_ERROR]: {
      type: ErrorType.API_ERROR,
      title: 'API Error',
      message: 'There was a problem with our search API. Please try again.',
      suggestions: [
        'Try refreshing the page',
        'Use different search terms',
        'Contact support if the problem continues'
      ],
      actions: [],
      canRetry: true,
      retryDelay: 3000
    },
    [ErrorType.UNKNOWN]: {
      type: ErrorType.UNKNOWN,
      title: 'Something Went Wrong',
      message: 'An unexpected error occurred while searching. Please try again.',
      suggestions: [
        'Try refreshing the page',
        'Use different search terms',
        'Contact support if the problem continues'
      ],
      actions: [],
      canRetry: true,
      retryDelay: 3000
    }
  }

  const noResultsError: ErrorInfo = {
    type: 'no_results' as any,
    title: 'No Planning Applications Found',
    message: 'No planning applications match your search for "luxury apartments Manchester". Try adjusting your search terms or exploring nearby areas.',
    suggestions: [
      'Try broader search terms (e.g., "housing" instead of "luxury apartments")',
      'Search in nearby areas or use a larger radius',
      'Check spelling of location names',
      'Use postcode search for more precise results',
      'Try different property types (residential, commercial, industrial)'
    ],
    actions: [],
    canRetry: false
  }

  const handleRetry = () => {
    console.log('Retry clicked for:', selectedError)
  }

  const handleNewSearch = (query: string) => {
    console.log('New search:', query)
  }

  const handleGoHome = () => {
    console.log('Go home clicked')
  }

  const handleContactSupport = () => {
    console.log('Contact support clicked')
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-planning-primary mb-4">
          Error State Demo
        </h1>
        <p className="text-gray-600">
          Test different error states to ensure they match the Planning Explorer design system
        </p>
      </div>

      {/* Error Type Selector */}
      <div className="bg-white rounded-lg border p-4">
        <h2 className="text-lg font-semibold mb-4">Select Error Type</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-2">
          {Object.values(ErrorType).map((errorType) => (
            <Button
              key={errorType}
              onClick={() => setSelectedError(errorType)}
              variant={selectedError === errorType ? 'primary' : 'outline'}
              size="sm"
              className="text-xs"
            >
              {errorType.replace('_', ' ')}
            </Button>
          ))}
          <Button
            onClick={() => setSelectedError('no_results' as any)}
            variant={selectedError === 'no_results' ? 'primary' : 'outline'}
            size="sm"
            className="text-xs"
          >
            No Results
          </Button>
        </div>
      </div>

      {/* Error State Preview */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Error State Preview</h2>

        {selectedError === 'no_results' ? (
          <SearchErrorState
            errorInfo={noResultsError}
            searchQuery="luxury apartments Manchester"
            onNewSearch={handleNewSearch}
            onGoHome={handleGoHome}
            onContactSupport={handleContactSupport}
          />
        ) : selectedError === ErrorType.NOT_FOUND ? (
          <SearchErrorState
            errorInfo={errorExamples[selectedError]}
            searchQuery="luxury apartments Manchester"
            onRetry={handleRetry}
            onNewSearch={handleNewSearch}
            onGoHome={handleGoHome}
            onContactSupport={handleContactSupport}
          />
        ) : (
          <ErrorState
            errorInfo={errorExamples[selectedError]}
            onRetry={handleRetry}
            onGoHome={handleGoHome}
            onContactSupport={handleContactSupport}
          />
        )}
      </div>

      {/* Compact Error State Preview */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Compact Error State Preview</h2>
        <ErrorState
          errorInfo={errorExamples[selectedError]}
          onRetry={handleRetry}
          compact={true}
        />
      </div>

      {/* Design System Check */}
      <div className="bg-white rounded-lg border p-4">
        <h2 className="text-lg font-semibold mb-4">Design System Verification</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <h3 className="font-medium text-gray-900 mb-2">Colors Used</h3>
            <ul className="space-y-1 text-gray-600">
              <li>• Primary: planning-primary</li>
              <li>• Accent: planning-accent</li>
              <li>• Error states: Contextual colors</li>
              <li>• Backgrounds: Gray scale</li>
            </ul>
          </div>
          <div>
            <h3 className="font-medium text-gray-900 mb-2">Components Used</h3>
            <ul className="space-y-1 text-gray-600">
              <li>• Button component with variants</li>
              <li>• Lucide React icons</li>
              <li>• Tailwind CSS utilities</li>
              <li>• Planning Explorer typography</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}