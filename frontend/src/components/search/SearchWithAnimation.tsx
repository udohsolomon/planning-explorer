/**
 * Search With Animation - Example Integration
 * Planning Explorer - Complete search flow with AI animation
 */

'use client';

import { useState } from 'react';
import { AISearchAnimation } from './animation/AISearchAnimation';
import { useSearchAPI } from '@/hooks/useSearchAPI';
import type { SearchRequest } from '@/types/search.types';

interface SearchWithAnimationProps {
  initialQuery?: string;
  searchType?: 'semantic' | 'keyword' | 'hybrid';
}

/**
 * Complete search component with integrated animation
 *
 * @example
 * ```tsx
 * <SearchWithAnimation
 *   initialQuery="approved housing in Manchester"
 *   searchType="semantic"
 * />
 * ```
 */
export function SearchWithAnimation({
  initialQuery = '',
  searchType = 'semantic',
}: SearchWithAnimationProps) {
  const [query, setQuery] = useState(initialQuery);

  const {
    isSearching,
    progress,
    currentStage,
    results,
    error,
    responseTime,
    executeSearch,
    cancelSearch,
    clearError,
  } = useSearchAPI({
    enableWebSocket: true,
    onComplete: (searchResults) => {
      console.log('Search completed:', searchResults);
    },
    onError: (searchError) => {
      console.error('Search error:', searchError);
    },
  });

  const handleSearch = async () => {
    if (!query.trim()) return;

    const request: SearchRequest = {
      query: query.trim(),
      searchType,
    };

    await executeSearch(request);
  };

  const handleAnimationComplete = () => {
    // Animation finished, results are already set
    console.log('Animation complete, showing results');
  };

  const handleAnimationCancel = () => {
    cancelSearch();
  };

  const handleAnimationError = (animationError: any) => {
    console.error('Animation error:', animationError);
  };

  return (
    <div className="w-full">
      {/* Search Input */}
      <div className="mb-6">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          placeholder="Search planning applications..."
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#043F2E]"
          disabled={isSearching}
        />
        <button
          onClick={handleSearch}
          disabled={isSearching || !query.trim()}
          className="mt-2 px-6 py-2 bg-[#043F2E] text-white rounded-lg hover:bg-[#065940] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSearching ? 'Searching...' : 'Search'}
        </button>
      </div>

      {/* Animation */}
      {isSearching && (
        <AISearchAnimation
          query={query}
          searchType={searchType}
          actualProgress={progress}
          actualResponseTime={responseTime ?? undefined}
          enableAcceleration={true}
          onComplete={handleAnimationComplete}
          onCancel={handleAnimationCancel}
          onError={handleAnimationError}
        />
      )}

      {/* Results */}
      {results && results.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-4">
            Found {results.length} results
          </h3>
          <div className="space-y-4">
            {results.map((result) => (
              <div
                key={result.id}
                className="p-4 border border-gray-200 rounded-lg hover:border-[#043F2E] transition-colors"
              >
                <h4 className="font-medium text-[#043F2E]">
                  {result.applicationNumber}
                </h4>
                <p className="text-sm text-gray-600 mt-1">{result.address}</p>
                <p className="text-sm text-gray-700 mt-2">{result.description}</p>
                <div className="flex gap-4 mt-3 text-xs text-gray-500">
                  <span>{result.localAuthority}</span>
                  <span>{result.status}</span>
                  {result.opportunityScore && (
                    <span className="text-[#10B981] font-medium">
                      Score: {result.opportunityScore}/100
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* No Results */}
      {results && results.length === 0 && (
        <div className="mt-6 p-6 text-center text-gray-500">
          No results found for "{query}"
        </div>
      )}

      {/* Error Display (if not handled by animation) */}
      {error && !isSearching && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <h4 className="font-medium text-red-900">{error.userMessage}</h4>
          <p className="text-sm text-red-700 mt-1">{error.message}</p>
          {error.retryable && (
            <button
              onClick={handleSearch}
              className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              Try Again
            </button>
          )}
        </div>
      )}
    </div>
  );
}
