/**
 * AI Search Animation Component
 * Planning Explorer - Main animation orchestrator
 */

'use client';

import './AnimationAccessibility.css';
import { useEffect } from 'react';
import { AnimatePresence } from 'framer-motion';
import { AnimationBackdrop } from './AnimationBackdrop';
import { AnimationCard } from './AnimationCard';
import { SearchStage } from './SearchStage';
import { ProgressBar } from './ProgressBar';
import { StageCounter } from './StageCounter';
import { CancelButton } from './CancelButton';
import { LazyErrorDisplay } from './LazyErrorDisplay';
import { useAnimationController } from '@/hooks/animation/useAnimationController';
import { useSlowResponseHandler } from '@/hooks/animation/useSlowResponseHandler';
import { useFocusTrap } from '@/hooks/animation/useFocusTrap';
import { useReducedMotion } from '@/hooks/animation/useReducedMotion';
import { useAnimationStore, useAnimationProgress } from '@/stores/animationStore';
import { ANIMATION_STAGES, TOTAL_STAGES } from './config/animationStages';
import type { AISearchAnimationProps } from '@/types/animation.types';

export function AISearchAnimation({
  query,
  searchType,
  actualProgress,
  estimatedDuration,
  actualResponseTime,
  enableAcceleration,
  onComplete,
  onCancel,
  onError,
}: AISearchAnimationProps) {
  const { start, cancel } = useAnimationController({
    onComplete,
    onCancel,
    onError,
    estimatedDuration,
    actualResponseTime,
    enableAcceleration,
  });

  const {
    isAnimating,
    currentStage,
    stageStatuses,
    dynamicValues,
    isCancelled,
    isComplete,
    error,
  } = useAnimationStore();

  const progress = useAnimationProgress();

  const {
    showCancelButton,
    isEnhancedCancel,
    showSlowWarning,
    rotatingMessage,
  } = useSlowResponseHandler({
    isAnimating,
    currentStage,
  });

  // Focus trap for keyboard accessibility
  const focusTrapRef = useFocusTrap({
    isActive: isAnimating,
    autoFocus: true,
    returnFocus: true,
  });

  // Reduced motion detection
  const prefersReducedMotion = useReducedMotion();

  // Start animation on mount
  useEffect(() => {
    start();
  }, [start]);

  // Keyboard handler for ESC key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && onCancel) {
        cancel();
      }
    };

    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [cancel, onCancel]);

  // Screen reader announcement for stage changes
  const getStageAnnouncement = () => {
    if (isComplete) {
      return 'Search complete. Displaying results.';
    }
    if (currentStage > 0 && currentStage <= ANIMATION_STAGES.length) {
      const stage = ANIMATION_STAGES[currentStage - 1];
      return `Stage ${currentStage} of ${ANIMATION_STAGES.length}: ${stage.title}`;
    }
    return '';
  };

  // Don't render if cancelled or complete
  if (isCancelled || isComplete) {
    return null;
  }

  return (
    <AnimatePresence>
      {isAnimating && (
        <div className="ai-search-animation">
          {/* Backdrop */}
          <AnimationBackdrop />

          {/* Main animation card */}
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <AnimationCard ref={focusTrapRef}>
              {/* Progress bar at top */}
              <ProgressBar
                progress={actualProgress ?? progress}
                isVisible={true}
              />

              {/* Stage counter badge */}
              <StageCounter
                currentStage={currentStage}
                totalStages={TOTAL_STAGES}
              />

              {/* Screen reader announcements */}
              <div
                role="status"
                aria-live="polite"
                aria-atomic="true"
                className="sr-only"
              >
                {getStageAnnouncement()}
              </div>

              {/* Progress indicator (optional) */}
              {actualProgress !== undefined && (
                <div
                  role="progressbar"
                  aria-valuenow={actualProgress}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-label="Search progress"
                  className="sr-only"
                >
                  {actualProgress}% complete
                </div>
              )}

              {/* Error Display or Stages */}
              {error ? (
                <LazyErrorDisplay
                  error={error}
                  stage={currentStage}
                  onRetry={() => {
                    // Reset animation and restart
                    start();
                  }}
                  onCancel={cancel}
                />
              ) : (
                <div className="space-y-0 mt-4">
                  {ANIMATION_STAGES.map((stage, index) => (
                    <SearchStage
                      key={stage.id}
                      stage={stage}
                      status={stageStatuses[index]}
                      isActive={currentStage === stage.id}
                      isLast={index === ANIMATION_STAGES.length - 1}
                      dynamicValues={dynamicValues}
                    />
                  ))}
                </div>
              )}

              {/* Slow warning message (only show if no error) */}
              {!error && showSlowWarning && (
                <div className="mt-4 text-center text-sm text-[#6B7280]">
                  🔍 Deep search in progress for best results...
                </div>
              )}

              {/* Rotating message for Stage 2 (only show if no error) */}
              {!error && rotatingMessage && currentStage === 2 && (
                <div className="mt-2 text-center text-sm text-[#087952] font-medium">
                  {rotatingMessage}
                </div>
              )}

              {/* Cancel button (hide when error is shown) */}
              {!error && onCancel && (
                <CancelButton
                  isVisible={showCancelButton}
                  isEnhanced={isEnhancedCancel}
                  onCancel={cancel}
                />
              )}
            </AnimationCard>
          </div>
        </div>
      )}
    </AnimatePresence>
  );
}
