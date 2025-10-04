/**
 * AI Search Animation Type Definitions
 * Planning Explorer - Animation System
 */

export type StageStatus = 'pending' | 'active' | 'completed' | 'error';

export type SearchType = 'semantic' | 'keyword' | 'hybrid';

export type AnimationErrorType =
  | 'connection'
  | 'parsing'
  | 'timeout'
  | 'server'
  | 'rate_limit'
  | 'no_results'
  | 'unknown';

/**
 * Individual animation stage configuration
 */
export interface AnimationStage {
  id: number;
  title: string;
  description: string;
  icon: string; // Icon name from lucide-react
  subSteps: SubStep[];
  duration: number; // milliseconds
  estimatedProgress: number; // 0-100
}

/**
 * Sub-step within a stage
 */
export interface SubStep {
  id: string;
  text: string;
  dynamicValue?: keyof DynamicValues;
  duration: number; // milliseconds
}

/**
 * Dynamic values injected from backend
 */
export interface DynamicValues {
  applicationsFound?: number;
  applicationsFiltered?: number;
  relevanceScore?: number;
  processingTime?: number;
  [key: string]: number | undefined;
}

/**
 * Animation state managed by Zustand
 */
export interface AnimationState {
  // Current stage tracking
  currentStage: number; // 0-4 (5 stages total)
  stageStatuses: StageStatus[]; // Array of 5 statuses

  // Sub-step progress
  currentSubStep: number;
  completedSubSteps: Set<string>;

  // Dynamic data
  dynamicValues: DynamicValues;

  // Animation control
  isAnimating: boolean;
  isPaused: boolean;
  isCancelled: boolean;
  isComplete: boolean;

  // Timing
  startTime: number | null;
  elapsedTime: number;
  estimatedDuration: number;

  // Error handling
  error: AnimationError | null;
  errorStage: number | null;

  // Actions
  startAnimation: () => void;
  pauseAnimation: () => void;
  resumeAnimation: () => void;
  cancelAnimation: () => void;
  completeAnimation: () => void;

  progressToNextStage: () => void;
  completeCurrentStage: () => void;
  completeSubStep: (subStepId: string) => void;

  setError: (error: AnimationError, stage: number) => void;
  clearError: () => void;

  updateDynamicValue: (key: keyof DynamicValues, value: number) => void;
  resetAnimation: () => void;
}

/**
 * Animation error details
 */
export interface AnimationError {
  type: AnimationErrorType;
  message: string;
  userMessage: string;
  retryable: boolean;
  actions?: ErrorAction[];
}

/**
 * Error action buttons
 */
export interface ErrorAction {
  id: string;
  label: string;
  variant: 'primary' | 'secondary' | 'danger';
  onClick: () => void;
}

/**
 * Props for main AISearchAnimation component
 */
export interface AISearchAnimationProps {
  query: string;
  searchType: SearchType;
  actualProgress?: number; // Real-time progress from backend (0-100)
  estimatedDuration?: number; // Override default duration
  actualResponseTime?: number; // Actual API response time in milliseconds (for acceleration)
  enableAcceleration?: boolean; // Enable fast response acceleration (default: true)
  onComplete: () => void;
  onCancel?: () => void;
  onError?: (error: AnimationError) => void;
}

/**
 * Props for individual SearchStage component
 */
export interface SearchStageProps {
  stage: AnimationStage;
  status: StageStatus;
  isActive: boolean;
  isLast: boolean;
  dynamicValues: DynamicValues;
}

/**
 * Props for StageIcon component
 */
export interface StageIconProps {
  iconName: string;
  status: StageStatus;
  isActive: boolean;
  size?: number;
}

/**
 * Props for SearchSubStep component
 */
export interface SearchSubStepProps {
  subStep: SubStep;
  isVisible: boolean;
  dynamicValue?: number;
  delay: number;
}

/**
 * Props for ConnectionLine component
 */
export interface ConnectionLineProps {
  isActive: boolean;
  isCompleted: boolean;
  height: number;
}

/**
 * Props for ProgressBar component
 */
export interface ProgressBarProps {
  progress: number; // 0-100
  isVisible: boolean;
}

/**
 * Props for StageCounter component
 */
export interface StageCounterProps {
  currentStage: number;
  totalStages: number;
}

/**
 * Props for CancelButton component
 */
export interface CancelButtonProps {
  isVisible: boolean;
  isEnhanced: boolean;
  onCancel: () => void;
}

/**
 * Props for ErrorDisplay component
 */
export interface ErrorDisplayProps {
  error: AnimationError;
  stage: number;
  onRetry?: () => void;
  onCancel?: () => void;
}

/**
 * Animation timing configuration
 */
export interface AnimationTimings {
  stageDurations: number[]; // Duration for each stage
  totalDuration: number;
  minDuration: number; // Minimum display time
  subStepStagger: number; // Delay between sub-steps
  iconRevealDuration: number;
  titleSlideDuration: number;
  checkmarkBounceDuration: number;
  connectionLineDuration: number;
}

/**
 * Responsive breakpoint configuration
 */
export interface ResponsiveConfig {
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  reducedMotion: boolean;
}

/**
 * Animation easing functions
 */
export type EasingFunction =
  | 'linear'
  | 'easeIn'
  | 'easeOut'
  | 'easeInOut'
  | 'elastic'
  | number[]; // Cubic bezier array [x1, y1, x2, y2]

/**
 * Framer Motion animation variants
 */
export interface AnimationVariants {
  initial: Record<string, any>;
  animate: Record<string, any>;
  exit?: Record<string, any>;
}
