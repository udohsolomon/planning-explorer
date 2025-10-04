/**
 * Slow Response Handler Hook
 * Planning Explorer - Manages timing and messages for slow searches
 */

import { useState, useEffect, useRef } from 'react';
import { SLOW_RESPONSE_DELAYS } from '@/components/search/animation/config/animationTimings';
import { SLOW_SEARCH_MESSAGES } from '@/components/search/animation/config/animationStages';

interface UseSlowResponseHandlerProps {
  isAnimating: boolean;
  currentStage: number;
}

export function useSlowResponseHandler({
  isAnimating,
  currentStage,
}: UseSlowResponseHandlerProps) {
  const [showCancelButton, setShowCancelButton] = useState(false);
  const [isEnhancedCancel, setIsEnhancedCancel] = useState(false);
  const [showSlowWarning, setShowSlowWarning] = useState(false);
  const [rotatingMessageIndex, setRotatingMessageIndex] = useState(0);
  const [showRotatingMessages, setShowRotatingMessages] = useState(false);

  const timersRef = useRef<NodeJS.Timeout[]>([]);

  useEffect(() => {
    if (!isAnimating) {
      // Clear all timers when animation stops
      timersRef.current.forEach(clearTimeout);
      timersRef.current = [];
      setShowCancelButton(false);
      setIsEnhancedCancel(false);
      setShowSlowWarning(false);
      setShowRotatingMessages(false);
      setRotatingMessageIndex(0);
      return;
    }

    // Timer 1: Show rotating messages after 5s
    const rotatingTimer = setTimeout(() => {
      if (currentStage === 2) {
        // Only show on Stage 2 (database search)
        setShowRotatingMessages(true);
      }
    }, SLOW_RESPONSE_DELAYS.showRotatingMessages);
    timersRef.current.push(rotatingTimer);

    // Timer 2: Show cancel button after 8s
    const cancelTimer = setTimeout(() => {
      setShowCancelButton(true);
    }, SLOW_RESPONSE_DELAYS.showCancelButton);
    timersRef.current.push(cancelTimer);

    // Timer 3: Show slow warning after 10s
    const warningTimer = setTimeout(() => {
      setShowSlowWarning(true);
    }, SLOW_RESPONSE_DELAYS.showSlowWarning);
    timersRef.current.push(warningTimer);

    // Timer 4: Enhance cancel button after 15s
    const enhanceTimer = setTimeout(() => {
      setIsEnhancedCancel(true);
    }, SLOW_RESPONSE_DELAYS.enhanceCancelButton);
    timersRef.current.push(enhanceTimer);

    return () => {
      timersRef.current.forEach(clearTimeout);
      timersRef.current = [];
    };
  }, [isAnimating, currentStage]);

  // Rotate messages every 2 seconds when enabled
  useEffect(() => {
    if (!showRotatingMessages || currentStage !== 2) return;

    const interval = setInterval(() => {
      setRotatingMessageIndex(
        (prev) => (prev + 1) % SLOW_SEARCH_MESSAGES.length
      );
    }, 2000); // Rotate every 2 seconds

    return () => clearInterval(interval);
  }, [showRotatingMessages, currentStage]);

  return {
    showCancelButton,
    isEnhancedCancel,
    showSlowWarning,
    rotatingMessage: showRotatingMessages
      ? SLOW_SEARCH_MESSAGES[rotatingMessageIndex]
      : null,
  };
}
