/**
 * AI Search Animation Stage Configurations
 * Planning Explorer - Stage Definitions
 */

import type { AnimationStage } from '@/types/animation.types';

/**
 * 5-stage animation configuration for AI search process
 * Total default duration: 4.6 seconds
 */
export const ANIMATION_STAGES: AnimationStage[] = [
  // Stage 1: Understanding Query
  {
    id: 1,
    title: 'Understanding Your Question',
    description: 'Analyzing natural language query and extracting parameters',
    icon: 'Brain', // Lucide icon name
    duration: 900, // 0.9s
    estimatedProgress: 20,
    subSteps: [
      {
        id: 'stage1-step1',
        text: 'Analyzing natural language query...',
        duration: 250,
      },
      {
        id: 'stage1-step2',
        text: 'Extracting key parameters (location, type, status)...',
        duration: 250,
      },
      {
        id: 'stage1-step3',
        text: 'Identifying search intent...',
        duration: 250,
      },
    ],
  },

  // Stage 2: AI Semantic Search (Most important - longest duration)
  {
    id: 2,
    title: 'Searching Planning Database',
    description: 'Scanning 336K+ applications with AI semantic matching',
    icon: 'Database', // Lucide icon name
    duration: 1500, // 1.5s
    estimatedProgress: 50,
    subSteps: [
      {
        id: 'stage2-step1',
        text: 'Scanning 336K+ planning applications...',
        duration: 400,
      },
      {
        id: 'stage2-step2',
        text: 'Running AI semantic matching...',
        duration: 400,
      },
      {
        id: 'stage2-step3',
        text: 'applications found that match criteria...',
        dynamicValue: 'applicationsFound',
        duration: 400,
      },
    ],
  },

  // Stage 3: Filtering Results
  {
    id: 3,
    title: 'Filtering Results',
    description: 'Applying location, date, and status filters',
    icon: 'Filter', // Lucide icon name
    duration: 800, // 0.8s
    estimatedProgress: 70,
    subSteps: [
      {
        id: 'stage3-step1',
        text: 'Applying location & date filters...',
        duration: 250,
      },
      {
        id: 'stage3-step2',
        text: 'Cross-checking approval status...',
        duration: 250,
      },
      {
        id: 'stage3-step3',
        text: 'applications remaining after filters...',
        dynamicValue: 'applicationsFiltered',
        duration: 250,
      },
    ],
  },

  // Stage 4: Ranking Matches
  {
    id: 4,
    title: 'Ranking Matches',
    description: 'Calculating relevance scores and opportunity ratings',
    icon: 'TrendingUp', // Lucide icon name
    duration: 800, // 0.8s
    estimatedProgress: 85,
    subSteps: [
      {
        id: 'stage4-step1',
        text: 'Calculating relevance scores...',
        duration: 250,
      },
      {
        id: 'stage4-step2',
        text: 'Analyzing opportunity ratings...',
        duration: 250,
      },
      {
        id: 'stage4-step3',
        text: 'Sorting by best matches...',
        duration: 250,
      },
    ],
  },

  // Stage 5: Preparing Response
  {
    id: 5,
    title: 'Preparing Results',
    description: 'Generating AI insights and formatting display',
    icon: 'Sparkles', // Lucide icon name
    duration: 600, // 0.6s (faster for smooth transition)
    estimatedProgress: 100,
    subSteps: [
      {
        id: 'stage5-step1',
        text: 'Generating AI insights...',
        duration: 200,
      },
      {
        id: 'stage5-step2',
        text: 'Formatting display data...',
        duration: 200,
      },
      {
        id: 'stage5-step3',
        text: 'Ready to display results!',
        duration: 200,
      },
    ],
  },
];

/**
 * Total number of stages
 */
export const TOTAL_STAGES = ANIMATION_STAGES.length;

/**
 * Total default animation duration in milliseconds
 */
export const TOTAL_DURATION = ANIMATION_STAGES.reduce(
  (sum, stage) => sum + stage.duration,
  0
);

/**
 * Minimum animation display time (even if API is faster)
 */
export const MIN_ANIMATION_DURATION = 2500; // 2.5 seconds

/**
 * Maximum animation duration before showing timeout warnings
 */
export const MAX_ANIMATION_DURATION = 15000; // 15 seconds

/**
 * When to show cancel button (milliseconds)
 */
export const SHOW_CANCEL_AFTER = 8000; // 8 seconds

/**
 * When to show "taking longer" message
 */
export const SHOW_SLOW_WARNING_AFTER = 10000; // 10 seconds

/**
 * When to enhance cancel button prominence
 */
export const ENHANCE_CANCEL_AFTER = 15000; // 15 seconds

/**
 * Slow response rotating messages for Stage 2 (database search)
 */
export const SLOW_SEARCH_MESSAGES = [
  'Searching 336,000+ applications...',
  'Analyzing semantic matches...',
  'Cross-referencing locations...',
  'Deep search in progress...',
];

/**
 * Get stage by ID
 */
export function getStageById(id: number): AnimationStage | undefined {
  return ANIMATION_STAGES.find((stage) => stage.id === id);
}

/**
 * Get stage index (0-based) from stage ID (1-based)
 */
export function getStageIndex(stageId: number): number {
  return stageId - 1;
}

/**
 * Calculate total progress percentage based on current stage and substep
 */
export function calculateProgress(
  currentStage: number,
  currentSubStep: number,
  totalSubSteps: number
): number {
  if (currentStage < 1 || currentStage > TOTAL_STAGES) return 0;

  const stage = ANIMATION_STAGES[currentStage - 1];
  const stageBaseProgress = ANIMATION_STAGES.slice(0, currentStage - 1).reduce(
    (sum, s) => sum + s.estimatedProgress,
    0
  );

  const subStepProgress =
    (stage.estimatedProgress / totalSubSteps) * currentSubStep;

  return Math.min(100, stageBaseProgress + subStepProgress);
}
