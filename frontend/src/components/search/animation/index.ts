/**
 * AI Search Animation - Component Exports
 * Planning Explorer
 */

// Main Components
export { AISearchAnimation } from './AISearchAnimation';
export { SearchStage } from './SearchStage';
export { StageIcon } from './StageIcon';
export { SearchSubStep } from './SearchSubStep';
export { AnimationBackdrop } from './AnimationBackdrop';
export { AnimationCard } from './AnimationCard';

// Phase 2 Components
export { ConnectionLine } from './ConnectionLine';
export { ProgressBar } from './ProgressBar';
export { StageCounter } from './StageCounter';
export { CancelButton } from './CancelButton';

// Phase 3 Components
export { ErrorDisplay } from './ErrorDisplay';

// Re-export configuration
export { ANIMATION_STAGES, TOTAL_STAGES, TOTAL_DURATION } from './config/animationStages';
export { DEFAULT_TIMINGS, MOBILE_TIMINGS, EASING } from './config/animationTimings';
export { STAGE_ICONS, ERROR_ICONS, ICON_SIZES } from './config/animationIcons';
export {
  ERROR_MESSAGES,
  ERROR_STAGE_MAP,
  getErrorConfig,
  createError,
} from './config/errorMessages';
