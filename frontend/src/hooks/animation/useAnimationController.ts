/**
 * AI Search Animation Controller Hook
 * Planning Explorer - Main animation orchestration logic
 */

import { useEffect, useRef, useCallback } from 'react';
import { useAnimationStore } from '@/stores/animationStore';
import { ANIMATION_STAGES } from '@/components/search/animation/config/animationStages';
import { useFastResponseAcceleration } from './useFastResponseAcceleration';
import type { AnimationError } from '@/types/animation.types';

interface UseAnimationControllerProps {
  onComplete: () => void;
  onCancel?: () => void;
  onError?: (error: AnimationError) => void;
  estimatedDuration?: number;
  /**
   * Actual API response time in milliseconds
   * If < 2000ms, animation will be accelerated
   */
  actualResponseTime?: number;
  /**
   * Enable fast response acceleration
   * Default: true
   */
  enableAcceleration?: boolean;
}

/**
 * Main animation controller hook
 * Manages animation lifecycle and stage progression
 */
export function useAnimationController({
  onComplete,
  onCancel,
  onError,
  estimatedDuration,
  actualResponseTime,
  enableAcceleration = true,
}: UseAnimationControllerProps) {
  const stageTimersRef = useRef<NodeJS.Timeout[]>([]);

  const {
    currentStage,
    isAnimating,
    isComplete,
    isCancelled,
    error,
    startAnimation,
    progressToNextStage,
    completeAnimation,
    cancelAnimation: storeCancelAnimation,
    resetAnimation,
  } = useAnimationStore();

  // Calculate accelerated timings for fast responses
  const acceleratedTimings = useFastResponseAcceleration({
    actualResponseTime,
    enableAcceleration,
  });

  /**
   * Start the animation sequence
   */
  const start = useCallback(() => {
    // Reset any existing state
    resetAnimation();

    // Start the animation
    startAnimation();

    // Use accelerated timings if available
    const stageDurations = acceleratedTimings.isAccelerated
      ? acceleratedTimings.stages
      : ANIMATION_STAGES.map((stage) => ({ id: stage.id, duration: stage.duration }));

    // Schedule stage progressions
    let cumulativeTime = 0;

    stageDurations.forEach((stage, index) => {
      cumulativeTime += stage.duration;

      const timer = setTimeout(() => {
        if (index < stageDurations.length - 1) {
          progressToNextStage();
        } else {
          completeAnimation();
        }
      }, cumulativeTime);

      stageTimersRef.current.push(timer);
    });
  }, [
    startAnimation,
    progressToNextStage,
    completeAnimation,
    resetAnimation,
    acceleratedTimings,
  ]);

  /**
   * Cancel the animation
   */
  const cancel = useCallback(() => {
    // Clear all timers
    stageTimersRef.current.forEach((timer) => clearTimeout(timer));
    stageTimersRef.current = [];

    // Update store
    storeCancelAnimation();

    // Call callback
    onCancel?.();
  }, [storeCancelAnimation, onCancel]);

  /**
   * Handle completion
   */
  useEffect(() => {
    if (isComplete) {
      // Clear all timers
      stageTimersRef.current.forEach((timer) => clearTimeout(timer));
      stageTimersRef.current = [];

      // Call completion callback
      onComplete();
    }
  }, [isComplete, onComplete]);

  /**
   * Handle cancellation
   */
  useEffect(() => {
    if (isCancelled) {
      // Clear all timers
      stageTimersRef.current.forEach((timer) => clearTimeout(timer));
      stageTimersRef.current = [];
    }
  }, [isCancelled]);

  /**
   * Handle errors
   */
  useEffect(() => {
    if (error) {
      // Clear all timers
      stageTimersRef.current.forEach((timer) => clearTimeout(timer));
      stageTimersRef.current = [];

      // Call error callback
      onError?.(error);
    }
  }, [error, onError]);

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      // Clear all timers on unmount
      stageTimersRef.current.forEach((timer) => clearTimeout(timer));
      stageTimersRef.current = [];
    };
  }, []);

  return {
    start,
    cancel,
    currentStage,
    isAnimating,
    isComplete,
    isCancelled,
    error,
    isAccelerated: acceleratedTimings.isAccelerated,
    speedFactor: acceleratedTimings.speedFactor,
  };
}
