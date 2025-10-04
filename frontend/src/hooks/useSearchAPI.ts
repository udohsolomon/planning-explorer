/**
 * Search API Hook
 * Planning Explorer - Backend integration with real-time progress
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import type {
  SearchRequest,
  SearchResponse,
  SearchResult,
  SearchProgressUpdate,
} from '@/types/search.types';
import type { AnimationError } from '@/types/animation.types';
import {
  executeSearch,
  createProgressWebSocket,
  pollSearchProgress,
  mapAPIErrorToAnimationError,
} from '@/lib/searchClient';

interface UseSearchAPIOptions {
  enableWebSocket?: boolean;
  onProgressUpdate?: (progress: number, stage: number) => void;
  onComplete?: (results: SearchResult[]) => void;
  onError?: (error: AnimationError) => void;
}

interface UseSearchAPIReturn {
  // State
  isSearching: boolean;
  progress: number;
  currentStage: number;
  results: SearchResult[] | null;
  error: AnimationError | null;
  responseTime: number | null;

  // Actions
  executeSearch: (request: SearchRequest) => Promise<void>;
  cancelSearch: () => void;
  clearError: () => void;
}

/**
 * Calculates smooth progress from stage and substep
 */
function calculateProgress(stage: number, substep: number = 0): number {
  const stageProgress = ((stage - 1) / 5) * 100;
  const substepProgress = (substep / 3) * (100 / 5);
  return Math.min(Math.round(stageProgress + substepProgress), 100);
}

/**
 * Hook for executing search with real-time progress updates
 */
export function useSearchAPI(options: UseSearchAPIOptions = {}): UseSearchAPIReturn {
  const {
    enableWebSocket = true,
    onProgressUpdate,
    onComplete,
    onError: onErrorCallback,
  } = options;

  const [isSearching, setIsSearching] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentStage, setCurrentStage] = useState(0);
  const [results, setResults] = useState<SearchResult[] | null>(null);
  const [error, setError] = useState<AnimationError | null>(null);
  const [responseTime, setResponseTime] = useState<number | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const requestIdRef = useRef<string | null>(null);
  const startTimeRef = useRef<number | null>(null);

  /**
   * Handles progress updates from WebSocket or polling
   */
  const handleProgress = useCallback(
    (data: SearchProgressUpdate) => {
      const newProgress = calculateProgress(data.stage, data.substep);
      setProgress(newProgress);
      setCurrentStage(data.stage);
      onProgressUpdate?.(newProgress, data.stage);
    },
    [onProgressUpdate]
  );

  /**
   * Handles search completion
   */
  const handleComplete = useCallback(
    (data: SearchProgressUpdate) => {
      const endTime = Date.now();
      const duration = startTimeRef.current ? endTime - startTimeRef.current : null;

      setProgress(100);
      setCurrentStage(5);
      setIsSearching(false);
      setResponseTime(duration);

      if (data.results) {
        setResults(data.results);
        onComplete?.(data.results);
      }
    },
    [onComplete]
  );

  /**
   * Handles errors
   */
  const handleError = useCallback(
    (animationError: AnimationError) => {
      setError(animationError);
      setIsSearching(false);
      onErrorCallback?.(animationError);
    },
    [onErrorCallback]
  );

  /**
   * Executes search request
   */
  const search = useCallback(
    async (request: SearchRequest) => {
      // Reset state
      setIsSearching(true);
      setProgress(0);
      setCurrentStage(0);
      setResults(null);
      setError(null);
      setResponseTime(null);
      startTimeRef.current = Date.now();

      // Generate request ID
      const requestId = uuidv4();
      requestIdRef.current = requestId;

      // Create abort controller
      const abortController = new AbortController();
      abortControllerRef.current = abortController;

      try {
        // Determine if WebSocket is supported
        const useWebSocket = enableWebSocket && typeof WebSocket !== 'undefined';

        if (useWebSocket) {
          // WebSocket-based real-time progress
          wsRef.current = createProgressWebSocket(
            requestId,
            handleProgress,
            handleComplete,
            handleError
          );

          // Execute search
          await executeSearch(request, abortController.signal);
        } else {
          // Fallback to polling
          const searchPromise = executeSearch(request, abortController.signal);
          const progressPromise = pollSearchProgress(
            requestId,
            handleProgress,
            handleComplete,
            handleError,
            abortController.signal
          );

          const response = await searchPromise;

          // If polling hasn't completed yet, manually complete
          if (isSearching) {
            handleComplete({
              stage: 5,
              progress: 100,
              status: 'complete',
              results: response.results,
              metadata: {
                totalResults: response.totalResults,
                processingTime: response.processingTime,
              },
            });
          }
        }
      } catch (err) {
        // Don't handle error if request was cancelled
        if (abortController.signal.aborted) {
          return;
        }

        // Try to parse as AnimationError
        try {
          const parsedError = JSON.parse((err as Error).message) as AnimationError;
          handleError(parsedError);
        } catch {
          // Fallback to generic error
          handleError({
            type: 'unknown',
            message: (err as Error).message || 'Search request failed',
            userMessage: 'Unexpected Error',
            retryable: true,
          });
        }
      }
    },
    [enableWebSocket, handleProgress, handleComplete, handleError, isSearching]
  );

  /**
   * Cancels active search
   */
  const cancelSearch = useCallback(() => {
    // Close WebSocket
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    // Abort fetch request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }

    // Reset state
    setIsSearching(false);
    setProgress(0);
    setCurrentStage(0);
    requestIdRef.current = null;
    startTimeRef.current = null;
  }, []);

  /**
   * Clears error state
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return {
    isSearching,
    progress,
    currentStage,
    results,
    error,
    responseTime,
    executeSearch: search,
    cancelSearch,
    clearError,
  };
}
