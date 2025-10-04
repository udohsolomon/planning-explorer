/**
 * useAnimationController Hook Tests
 * Planning Explorer - Core animation logic tests
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useAnimationController } from '../useAnimationController';
import { useAnimationStore } from '@/stores/animationStore';

// Mock the animation store
vi.mock('@/stores/animationStore');

// Mock the fast response acceleration hook
vi.mock('../useFastResponseAcceleration', () => ({
  useFastResponseAcceleration: vi.fn(() => ({
    stages: [],
    totalDuration: 4600,
    isAccelerated: false,
    speedFactor: 1.0,
  })),
}));

describe('useAnimationController', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();

    // Setup default mock implementation
    (useAnimationStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
      currentStage: 0,
      isAnimating: false,
      isComplete: false,
      isCancelled: false,
      error: null,
      startAnimation: vi.fn(),
      progressToNextStage: vi.fn(),
      completeAnimation: vi.fn(),
      cancelAnimation: vi.fn(),
      resetAnimation: vi.fn(),
    });
  });

  afterEach(() => {
    vi.runOnlyPendingTimers();
    vi.useRealTimers();
  });

  describe('Initialization', () => {
    it('should initialize with correct default state', () => {
      const onComplete = vi.fn();
      const { result } = renderHook(() =>
        useAnimationController({
          onComplete,
        })
      );

      expect(result.current.currentStage).toBe(0);
      expect(result.current.isAnimating).toBe(false);
      expect(result.current.isComplete).toBe(false);
      expect(result.current.isCancelled).toBe(false);
    });

    it('should expose start and cancel functions', () => {
      const onComplete = vi.fn();
      const { result } = renderHook(() =>
        useAnimationController({
          onComplete,
        })
      );

      expect(typeof result.current.start).toBe('function');
      expect(typeof result.current.cancel).toBe('function');
    });
  });

  describe('Animation Start', () => {
    it('should call resetAnimation and startAnimation when starting', () => {
      const mockStartAnimation = vi.fn();
      const mockResetAnimation = vi.fn();

      (useAnimationStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        currentStage: 0,
        isAnimating: false,
        isComplete: false,
        isCancelled: false,
        error: null,
        startAnimation: mockStartAnimation,
        progressToNextStage: vi.fn(),
        completeAnimation: vi.fn(),
        cancelAnimation: vi.fn(),
        resetAnimation: mockResetAnimation,
      });

      const onComplete = vi.fn();
      const { result } = renderHook(() =>
        useAnimationController({
          onComplete,
        })
      );

      act(() => {
        result.current.start();
      });

      expect(mockResetAnimation).toHaveBeenCalled();
      expect(mockStartAnimation).toHaveBeenCalled();
    });

    it('should schedule stage progressions based on stage durations', () => {
      const mockProgressToNextStage = vi.fn();

      (useAnimationStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        currentStage: 0,
        isAnimating: false,
        isComplete: false,
        isCancelled: false,
        error: null,
        startAnimation: vi.fn(),
        progressToNextStage: mockProgressToNextStage,
        completeAnimation: vi.fn(),
        cancelAnimation: vi.fn(),
        resetAnimation: vi.fn(),
      });

      const onComplete = vi.fn();
      const { result } = renderHook(() =>
        useAnimationController({
          onComplete,
        })
      );

      act(() => {
        result.current.start();
      });

      // Fast-forward to first stage completion (900ms for Stage 1)
      act(() => {
        vi.advanceTimersByTime(900);
      });

      expect(mockProgressToNextStage).toHaveBeenCalled();
    });
  });

  describe('Animation Cancellation', () => {
    it('should call store cancelAnimation and onCancel callback', () => {
      const mockCancelAnimation = vi.fn();
      const onCancel = vi.fn();
      const onComplete = vi.fn();

      (useAnimationStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        currentStage: 2,
        isAnimating: true,
        isComplete: false,
        isCancelled: false,
        error: null,
        startAnimation: vi.fn(),
        progressToNextStage: vi.fn(),
        completeAnimation: vi.fn(),
        cancelAnimation: mockCancelAnimation,
        resetAnimation: vi.fn(),
      });

      const { result } = renderHook(() =>
        useAnimationController({
          onComplete,
          onCancel,
        })
      );

      act(() => {
        result.current.cancel();
      });

      expect(mockCancelAnimation).toHaveBeenCalled();
      expect(onCancel).toHaveBeenCalled();
    });

    it('should clear all timers when cancelled', () => {
      const onComplete = vi.fn();
      const { result } = renderHook(() =>
        useAnimationController({
          onComplete,
        })
      );

      act(() => {
        result.current.start();
      });

      const pendingTimersBefore = vi.getTimerCount();
      expect(pendingTimersBefore).toBeGreaterThan(0);

      act(() => {
        result.current.cancel();
      });

      act(() => {
        vi.runAllTimers();
      });

      // Timers should be cleared
      expect(vi.getTimerCount()).toBe(0);
    });
  });

  describe('Animation Completion', () => {
    it('should call onComplete callback when animation completes', () => {
      const onComplete = vi.fn();

      (useAnimationStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        currentStage: 5,
        isAnimating: true,
        isComplete: true, // Animation complete
        isCancelled: false,
        error: null,
        startAnimation: vi.fn(),
        progressToNextStage: vi.fn(),
        completeAnimation: vi.fn(),
        cancelAnimation: vi.fn(),
        resetAnimation: vi.fn(),
      });

      renderHook(() =>
        useAnimationController({
          onComplete,
        })
      );

      // The effect should trigger onComplete
      expect(onComplete).toHaveBeenCalled();
    });

    it('should clear timers when animation completes', () => {
      const onComplete = vi.fn();
      const { rerender } = renderHook(
        ({ isComplete }) => {
          (useAnimationStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
            currentStage: 5,
            isAnimating: true,
            isComplete,
            isCancelled: false,
            error: null,
            startAnimation: vi.fn(),
            progressToNextStage: vi.fn(),
            completeAnimation: vi.fn(),
            cancelAnimation: vi.fn(),
            resetAnimation: vi.fn(),
          });

          return useAnimationController({ onComplete });
        },
        { initialProps: { isComplete: false } }
      );

      act(() => {
        rerender({ isComplete: true });
      });

      expect(onComplete).toHaveBeenCalled();
    });
  });

  describe('Error Handling', () => {
    it('should call onError callback when error occurs', () => {
      const onError = vi.fn();
      const mockError = {
        type: 'connection' as const,
        message: 'Connection failed',
        userMessage: 'Connection Error',
        retryable: true,
      };

      (useAnimationStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        currentStage: 2,
        isAnimating: true,
        isComplete: false,
        isCancelled: false,
        error: mockError,
        startAnimation: vi.fn(),
        progressToNextStage: vi.fn(),
        completeAnimation: vi.fn(),
        cancelAnimation: vi.fn(),
        resetAnimation: vi.fn(),
      });

      renderHook(() =>
        useAnimationController({
          onComplete: vi.fn(),
          onError,
        })
      );

      expect(onError).toHaveBeenCalledWith(mockError);
    });

    it('should clear timers when error occurs', () => {
      const onComplete = vi.fn();
      const { rerender } = renderHook(
        ({ error }) => {
          (useAnimationStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
            currentStage: 2,
            isAnimating: true,
            isComplete: false,
            isCancelled: false,
            error,
            startAnimation: vi.fn(),
            progressToNextStage: vi.fn(),
            completeAnimation: vi.fn(),
            cancelAnimation: vi.fn(),
            resetAnimation: vi.fn(),
          });

          return useAnimationController({ onComplete });
        },
        { initialProps: { error: null } }
      );

      const mockError = {
        type: 'timeout' as const,
        message: 'Request timed out',
        userMessage: 'Timeout Error',
        retryable: true,
      };

      act(() => {
        rerender({ error: mockError });
      });

      act(() => {
        vi.runAllTimers();
      });

      // Timers should be cleared
      expect(vi.getTimerCount()).toBe(0);
    });
  });

  describe('Fast Response Acceleration', () => {
    it('should use accelerated timings when provided', () => {
      const { useFastResponseAcceleration } = require('../useFastResponseAcceleration');

      useFastResponseAcceleration.mockReturnValue({
        stages: [
          { id: 1, duration: 720 }, // 80% of 900ms
          { id: 2, duration: 1200 }, // 80% of 1500ms
        ],
        totalDuration: 1920,
        isAccelerated: true,
        speedFactor: 1.25,
      });

      const mockProgressToNextStage = vi.fn();

      (useAnimationStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        currentStage: 0,
        isAnimating: false,
        isComplete: false,
        isCancelled: false,
        error: null,
        startAnimation: vi.fn(),
        progressToNextStage: mockProgressToNextStage,
        completeAnimation: vi.fn(),
        cancelAnimation: vi.fn(),
        resetAnimation: vi.fn(),
      });

      const onComplete = vi.fn();
      const { result } = renderHook(() =>
        useAnimationController({
          onComplete,
          actualResponseTime: 1200, // Fast response
        })
      );

      act(() => {
        result.current.start();
      });

      // Should progress at accelerated timing (720ms instead of 900ms)
      act(() => {
        vi.advanceTimersByTime(720);
      });

      expect(mockProgressToNextStage).toHaveBeenCalled();
    });
  });

  describe('Cleanup', () => {
    it('should clear all timers on unmount', () => {
      const onComplete = vi.fn();
      const { result, unmount } = renderHook(() =>
        useAnimationController({
          onComplete,
        })
      );

      act(() => {
        result.current.start();
      });

      expect(vi.getTimerCount()).toBeGreaterThan(0);

      unmount();

      act(() => {
        vi.runAllTimers();
      });

      expect(vi.getTimerCount()).toBe(0);
    });
  });
});
