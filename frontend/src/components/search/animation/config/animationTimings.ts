/**
 * AI Search Animation Timing Configurations
 * Planning Explorer - Animation Durations & Easing
 */

import type { AnimationTimings, EasingFunction } from '@/types/animation.types';

/**
 * Default animation timings configuration
 */
export const DEFAULT_TIMINGS: AnimationTimings = {
  // Stage durations (matches animationStages.ts)
  stageDurations: [900, 1500, 800, 800, 600], // milliseconds

  // Total and min durations
  totalDuration: 4600, // 4.6 seconds
  minDuration: 2500, // 2.5 seconds minimum display

  // Sub-step timings
  subStepStagger: 80, // 80ms delay between sub-steps

  // Individual animation durations
  iconRevealDuration: 300, // Icon scale + fade in
  titleSlideDuration: 200, // Title slide from left
  checkmarkBounceDuration: 300, // Checkmark bounce effect
  connectionLineDuration: 400, // Line drawing animation
};

/**
 * Mobile-optimized timings (faster for performance)
 */
export const MOBILE_TIMINGS: AnimationTimings = {
  stageDurations: [700, 1200, 600, 600, 500],
  totalDuration: 3600,
  minDuration: 2000,
  subStepStagger: 60,
  iconRevealDuration: 250,
  titleSlideDuration: 150,
  checkmarkBounceDuration: 250,
  connectionLineDuration: 300,
};

/**
 * Reduced motion timings (instant transitions)
 */
export const REDUCED_MOTION_TIMINGS: AnimationTimings = {
  stageDurations: [200, 200, 200, 200, 200],
  totalDuration: 1000,
  minDuration: 1000,
  subStepStagger: 0,
  iconRevealDuration: 0,
  titleSlideDuration: 0,
  checkmarkBounceDuration: 0,
  connectionLineDuration: 0,
};

/**
 * Easing functions for animations
 */
export const EASING: Record<string, EasingFunction> = {
  // Standard easing
  linear: 'linear',
  easeIn: 'easeIn',
  easeOut: 'easeOut',
  easeInOut: 'easeInOut',

  // Custom cubic bezier curves
  elastic: [0.34, 1.56, 0.64, 1], // Elastic bounce effect
  smooth: [0.4, 0.0, 0.2, 1], // Material Design easing
  snappy: [0.8, 0.0, 0.2, 1], // Quick acceleration
  gentle: [0.25, 0.46, 0.45, 0.94], // Slow and gentle
};

/**
 * Animation delays for slow API responses
 */
export const SLOW_RESPONSE_DELAYS = {
  showRotatingMessages: 5000, // Show rotating messages after 5s
  showCancelButton: 8000, // Show cancel button after 8s
  showSlowWarning: 10000, // Show "taking longer" message after 10s
  enhanceCancelButton: 15000, // Make cancel more prominent after 15s
  timeout: 30000, // Hard timeout after 30s
};

/**
 * Animation delays for fast API responses
 */
export const FAST_RESPONSE_CONFIG = {
  threshold: 2000, // Consider "fast" if < 2 seconds
  accelerationFactor: 0.8, // Speed up to 80% of normal
  minDisplayTime: 2500, // Still show at least 2.5s
};

/**
 * Calculate adaptive stage duration based on actual API progress
 */
export function calculateAdaptiveDuration(
  stageIndex: number,
  defaultDuration: number,
  actualProgress: number,
  isMobile: boolean
): number {
  const baseDuration = isMobile
    ? MOBILE_TIMINGS.stageDurations[stageIndex]
    : defaultDuration;

  // If we have real-time progress, sync timing
  if (actualProgress > 0 && actualProgress < 100) {
    return Math.max(baseDuration * 0.8, 500); // Min 500ms per stage
  }

  return baseDuration;
}

/**
 * Calculate total adjusted duration for fast responses
 */
export function calculateFastResponseDuration(apiResponseTime: number): number {
  if (apiResponseTime >= FAST_RESPONSE_CONFIG.threshold) {
    return DEFAULT_TIMINGS.totalDuration;
  }

  const adjusted =
    DEFAULT_TIMINGS.totalDuration * FAST_RESPONSE_CONFIG.accelerationFactor;

  return Math.max(adjusted, FAST_RESPONSE_CONFIG.minDisplayTime);
}

/**
 * Get appropriate timing config based on device and motion preferences
 */
export function getTimingConfig(
  isMobile: boolean,
  reducedMotion: boolean
): AnimationTimings {
  if (reducedMotion) {
    return REDUCED_MOTION_TIMINGS;
  }

  if (isMobile) {
    return MOBILE_TIMINGS;
  }

  return DEFAULT_TIMINGS;
}

/**
 * Stagger delay calculation for sub-steps
 */
export function calculateSubStepDelay(
  index: number,
  baseDelay: number = DEFAULT_TIMINGS.subStepStagger
): number {
  return index * baseDelay;
}
