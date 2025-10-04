/**
 * Fast Response Acceleration Hook
 * Planning Explorer - Handles sub-2s API response acceleration
 */

import { useMemo } from 'react';
import { ANIMATION_STAGES } from '@/components/search/animation/config/animationStages';

interface FastResponseAccelerationProps {
  /**
   * Actual API response time in milliseconds
   * If < 2000ms, animation will be accelerated
   */
  actualResponseTime?: number;

  /**
   * Whether to apply acceleration
   * Default: true if actualResponseTime < 2000ms
   */
  enableAcceleration?: boolean;
}

interface AcceleratedTimings {
  /**
   * Adjusted stage durations (80% of original for fast responses)
   */
  stages: Array<{ id: number; duration: number }>;

  /**
   * Total animation duration after acceleration
   */
  totalDuration: number;

  /**
   * Whether acceleration was applied
   */
  isAccelerated: boolean;

  /**
   * Speed factor applied (1.0 = normal, 1.25 = accelerated)
   */
  speedFactor: number;
}

const FAST_RESPONSE_THRESHOLD = 2000; // 2 seconds
const ACCELERATION_FACTOR = 0.8; // 80% of original duration
const MINIMUM_ANIMATION_DURATION = 2500; // 2.5s minimum display time

/**
 * Calculate accelerated timings for fast API responses
 *
 * When API responds in < 2s, we want to:
 * 1. Show minimum 2.5s of animation (maintain good UX)
 * 2. Speed up stages proportionally (80% duration)
 * 3. Still show all stages and sub-steps
 *
 * @example
 * const { stages, isAccelerated } = useFastResponseAcceleration({
 *   actualResponseTime: 1200, // 1.2s response
 * });
 * // stages will have 80% of original durations
 * // isAccelerated = true
 */
export function useFastResponseAcceleration({
  actualResponseTime,
  enableAcceleration = true,
}: FastResponseAccelerationProps = {}): AcceleratedTimings {
  return useMemo(() => {
    // Default: no acceleration
    if (!enableAcceleration || !actualResponseTime) {
      return {
        stages: ANIMATION_STAGES.map((stage) => ({
          id: stage.id,
          duration: stage.duration,
        })),
        totalDuration: ANIMATION_STAGES.reduce((sum, stage) => sum + stage.duration, 0),
        isAccelerated: false,
        speedFactor: 1.0,
      };
    }

    // Check if response is fast enough for acceleration
    const isFastResponse = actualResponseTime < FAST_RESPONSE_THRESHOLD;

    if (!isFastResponse) {
      // Normal timings
      return {
        stages: ANIMATION_STAGES.map((stage) => ({
          id: stage.id,
          duration: stage.duration,
        })),
        totalDuration: ANIMATION_STAGES.reduce((sum, stage) => sum + stage.duration, 0),
        isAccelerated: false,
        speedFactor: 1.0,
      };
    }

    // Apply acceleration: reduce durations by 20% (80% of original)
    const acceleratedStages = ANIMATION_STAGES.map((stage) => ({
      id: stage.id,
      duration: Math.round(stage.duration * ACCELERATION_FACTOR),
    }));

    const acceleratedTotal = acceleratedStages.reduce((sum, stage) => sum + stage.duration, 0);

    // Ensure minimum animation duration
    if (acceleratedTotal < MINIMUM_ANIMATION_DURATION) {
      // Scale back up to meet minimum duration
      const scaleFactor = MINIMUM_ANIMATION_DURATION / acceleratedTotal;
      const adjustedStages = acceleratedStages.map((stage) => ({
        id: stage.id,
        duration: Math.round(stage.duration * scaleFactor),
      }));

      return {
        stages: adjustedStages,
        totalDuration: MINIMUM_ANIMATION_DURATION,
        isAccelerated: true,
        speedFactor: 1.0 / (ACCELERATION_FACTOR * scaleFactor),
      };
    }

    return {
      stages: acceleratedStages,
      totalDuration: acceleratedTotal,
      isAccelerated: true,
      speedFactor: 1.25, // 1 / 0.8 = 1.25x speed
    };
  }, [actualResponseTime, enableAcceleration]);
}

/**
 * Get stage duration from accelerated timings
 */
export function getStageDuration(
  stageId: number,
  acceleratedTimings: AcceleratedTimings
): number {
  const stage = acceleratedTimings.stages.find((s) => s.id === stageId);
  return stage?.duration ?? ANIMATION_STAGES[stageId - 1]?.duration ?? 0;
}
