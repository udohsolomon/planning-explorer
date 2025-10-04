/**
 * Animation Analytics Hook
 * Planning Explorer - Tracks AI search animation events
 */

import { useEffect, useRef, useCallback } from 'react';
import { track } from '@/lib/lazyAnalytics';
import type { AnimationError } from '@/types/animation.types';

interface AnimationAnalyticsOptions {
  query: string;
  searchType: 'semantic' | 'keyword' | 'hybrid';
  isAnimating: boolean;
  currentStage: number;
  error: AnimationError | null;
  wasAccelerated?: boolean;
}

export function useAnimationAnalytics({
  query,
  searchType,
  isAnimating,
  currentStage,
  error,
  wasAccelerated,
}: AnimationAnalyticsOptions) {
  const startTimeRef = useRef<number | null>(null);
  const stagesReachedRef = useRef<Set<number>>(new Set());
  const hasTrackedStartRef = useRef(false);
  const hasTrackedCompleteRef = useRef(false);

  /**
   * Track animation start
   */
  useEffect(() => {
    if (isAnimating && !hasTrackedStartRef.current) {
      startTimeRef.current = Date.now();
      stagesReachedRef.current.clear();
      hasTrackedStartRef.current = true;
      hasTrackedCompleteRef.current = false;

      track('animation_started', {
        query,
        searchType,
        timestamp: startTimeRef.current,
      });
    }

    // Reset when animation stops
    if (!isAnimating && hasTrackedStartRef.current) {
      hasTrackedStartRef.current = false;
    }
  }, [isAnimating, query, searchType]);

  /**
   * Track stage progression
   */
  useEffect(() => {
    if (isAnimating && currentStage > 0 && !stagesReachedRef.current.has(currentStage)) {
      stagesReachedRef.current.add(currentStage);

      const elapsed = startTimeRef.current ? Date.now() - startTimeRef.current : 0;

      track('animation_stage_reached', {
        stage: currentStage,
        elapsed_ms: elapsed,
        query,
        searchType,
      });
    }
  }, [isAnimating, currentStage, query, searchType]);

  /**
   * Track animation completion
   */
  const trackComplete = useCallback(
    (resultsCount?: number) => {
      if (hasTrackedCompleteRef.current) return;

      const duration = startTimeRef.current ? Date.now() - startTimeRef.current : 0;
      hasTrackedCompleteRef.current = true;

      track('animation_completed', {
        duration_ms: duration,
        results_count: resultsCount,
        was_accelerated: wasAccelerated,
        query,
        searchType,
        stages_reached: Array.from(stagesReachedRef.current),
      });
    },
    [query, searchType, wasAccelerated]
  );

  /**
   * Track animation cancellation
   */
  const trackCancel = useCallback(
    (reason?: string) => {
      const elapsed = startTimeRef.current ? Date.now() - startTimeRef.current : 0;

      track('animation_cancelled', {
        stage: currentStage,
        elapsed_ms: elapsed,
        reason: reason || 'user_cancelled',
        query,
        searchType,
      });
    },
    [currentStage, query, searchType]
  );

  /**
   * Track errors
   */
  useEffect(() => {
    if (error) {
      const elapsed = startTimeRef.current ? Date.now() - startTimeRef.current : 0;

      track('animation_error', {
        error_type: error.type,
        error_message: error.message,
        user_message: error.userMessage,
        stage: currentStage,
        elapsed_ms: elapsed,
        retryable: error.retryable,
        query,
        searchType,
      });
    }
  }, [error, currentStage, query, searchType]);

  /**
   * Track user interactions
   */
  const trackCancelClick = useCallback(() => {
    const elapsed = startTimeRef.current ? Date.now() - startTimeRef.current : 0;

    track('cancel_button_clicked', {
      elapsed_ms: elapsed,
      stage: currentStage,
      query,
      searchType,
    });
  }, [currentStage, query, searchType]);

  const trackRetry = useCallback(
    (errorType: string, attempt: number) => {
      track('animation_retry', {
        attempt,
        error_type: errorType,
        query,
        searchType,
      });
    },
    [query, searchType]
  );

  const trackErrorAction = useCallback(
    (actionId: string, errorType: string) => {
      track('error_action_clicked', {
        action_id: actionId,
        error_type: errorType,
        query,
        searchType,
      });
    },
    [query, searchType]
  );

  const trackUpgradeCTA = useCallback(
    (source: string) => {
      track('upgrade_cta_clicked', {
        source,
        query,
        searchType,
      });
    },
    [query, searchType]
  );

  /**
   * Track performance metrics
   */
  const trackPerformance = useCallback(
    (metrics: {
      totalDuration: number;
      apiResponseTime?: number;
      wasAccelerated?: boolean;
    }) => {
      track('animation_performance', {
        total_duration_ms: metrics.totalDuration,
        api_response_time_ms: metrics.apiResponseTime,
        was_accelerated: metrics.wasAccelerated,
        query,
        searchType,
      });
    },
    [query, searchType]
  );

  return {
    trackComplete,
    trackCancel,
    trackCancelClick,
    trackRetry,
    trackErrorAction,
    trackUpgradeCTA,
    trackPerformance,
  };
}
