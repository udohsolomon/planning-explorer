/**
 * AI Search Animation Zustand Store
 * Planning Explorer - Animation State Management
 */

import { create } from 'zustand';
import type {
  AnimationState,
  AnimationError,
  DynamicValues,
  StageStatus,
} from '@/types/animation.types';
import { TOTAL_STAGES, TOTAL_DURATION } from '@/components/search/animation/config/animationStages';

/**
 * Animation store using Zustand
 * Manages all animation state and actions
 */
export const useAnimationStore = create<AnimationState>((set, get) => ({
  // Initial state
  currentStage: 0,
  stageStatuses: Array(TOTAL_STAGES).fill('pending') as StageStatus[],
  currentSubStep: 0,
  completedSubSteps: new Set<string>(),
  dynamicValues: {},
  isAnimating: false,
  isPaused: false,
  isCancelled: false,
  isComplete: false,
  startTime: null,
  elapsedTime: 0,
  estimatedDuration: TOTAL_DURATION,
  error: null,
  errorStage: null,

  // Actions
  startAnimation: () => {
    set({
      isAnimating: true,
      isPaused: false,
      isCancelled: false,
      isComplete: false,
      currentStage: 1,
      stageStatuses: ['active', 'pending', 'pending', 'pending', 'pending'],
      startTime: Date.now(),
      elapsedTime: 0,
      currentSubStep: 0,
      completedSubSteps: new Set<string>(),
      error: null,
      errorStage: null,
    });
  },

  pauseAnimation: () => {
    set({ isPaused: true });
  },

  resumeAnimation: () => {
    set({ isPaused: false });
  },

  cancelAnimation: () => {
    set({
      isCancelled: true,
      isAnimating: false,
      isPaused: false,
    });
  },

  completeAnimation: () => {
    const { startTime } = get();
    const elapsedTime = startTime ? Date.now() - startTime : 0;

    set({
      isComplete: true,
      isAnimating: false,
      currentStage: TOTAL_STAGES,
      stageStatuses: Array(TOTAL_STAGES).fill('completed') as StageStatus[],
      elapsedTime,
    });
  },

  progressToNextStage: () => {
    const { currentStage, stageStatuses } = get();

    if (currentStage >= TOTAL_STAGES) {
      get().completeAnimation();
      return;
    }

    const newStatuses = [...stageStatuses];
    newStatuses[currentStage - 1] = 'completed'; // Complete current stage
    if (currentStage < TOTAL_STAGES) {
      newStatuses[currentStage] = 'active'; // Activate next stage
    }

    set({
      currentStage: currentStage + 1,
      stageStatuses: newStatuses,
      currentSubStep: 0, // Reset sub-step counter
    });
  },

  completeCurrentStage: () => {
    const { currentStage, stageStatuses } = get();

    const newStatuses = [...stageStatuses];
    newStatuses[currentStage - 1] = 'completed';

    set({
      stageStatuses: newStatuses,
    });
  },

  completeSubStep: (subStepId: string) => {
    const { completedSubSteps, currentSubStep } = get();

    const newCompleted = new Set(completedSubSteps);
    newCompleted.add(subStepId);

    set({
      completedSubSteps: newCompleted,
      currentSubStep: currentSubStep + 1,
    });
  },

  setError: (error: AnimationError, stage: number) => {
    const { stageStatuses } = get();

    const newStatuses = [...stageStatuses];
    newStatuses[stage - 1] = 'error';

    set({
      error,
      errorStage: stage,
      stageStatuses: newStatuses,
      isAnimating: false,
      isPaused: false,
    });
  },

  clearError: () => {
    set({
      error: null,
      errorStage: null,
    });
  },

  updateDynamicValue: (key: keyof DynamicValues, value: number) => {
    const { dynamicValues } = get();

    set({
      dynamicValues: {
        ...dynamicValues,
        [key]: value,
      },
    });
  },

  resetAnimation: () => {
    set({
      currentStage: 0,
      stageStatuses: Array(TOTAL_STAGES).fill('pending') as StageStatus[],
      currentSubStep: 0,
      completedSubSteps: new Set<string>(),
      dynamicValues: {},
      isAnimating: false,
      isPaused: false,
      isCancelled: false,
      isComplete: false,
      startTime: null,
      elapsedTime: 0,
      error: null,
      errorStage: null,
    });
  },
}));

/**
 * Selector hooks for common state access patterns
 */

export const useCurrentStage = () =>
  useAnimationStore((state) => state.currentStage);

export const useStageStatus = (stageIndex: number) =>
  useAnimationStore((state) => state.stageStatuses[stageIndex]);

export const useIsAnimating = () =>
  useAnimationStore((state) => state.isAnimating);

export const useAnimationError = () =>
  useAnimationStore((state) => state.error);

export const useDynamicValues = () =>
  useAnimationStore((state) => state.dynamicValues);

export const useAnimationProgress = () =>
  useAnimationStore((state) => {
    const { currentStage, elapsedTime, estimatedDuration } = state;
    if (currentStage === 0) return 0;
    if (currentStage >= TOTAL_STAGES) return 100;

    // Calculate progress based on elapsed time
    const timeProgress = Math.min(
      100,
      (elapsedTime / estimatedDuration) * 100
    );

    // Calculate progress based on stage completion
    const stageProgress = (currentStage / TOTAL_STAGES) * 100;

    // Use the more advanced of the two
    return Math.max(timeProgress, stageProgress);
  });
