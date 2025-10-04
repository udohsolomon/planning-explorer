/**
 * Error Messages Configuration
 * Planning Explorer - Error handling definitions
 */

import type { AnimationError, AnimationErrorType } from '@/types/animation.types';

/**
 * Error message templates for each error type
 */
export const ERROR_MESSAGES: Record<AnimationErrorType, Omit<AnimationError, 'type'>> = {
  connection: {
    message: 'Unable to reach planning database',
    userMessage: 'Connection Error',
    retryable: true,
    actions: [
      {
        id: 'retry',
        label: 'Try Again',
        variant: 'primary',
        onClick: () => {}, // Will be set by component
      },
      {
        id: 'cancel',
        label: 'Go Back',
        variant: 'secondary',
        onClick: () => {}, // Will be set by component
      },
    ],
  },

  parsing: {
    message: 'We couldn\'t parse your search query. Try: "Approved housing in Manchester"',
    userMessage: 'Query Not Understood',
    retryable: true,
    actions: [
      {
        id: 'filters',
        label: 'Use Filters Instead',
        variant: 'primary',
        onClick: () => {}, // Will be set by component
      },
      {
        id: 'rephrase',
        label: 'Rephrase Search',
        variant: 'secondary',
        onClick: () => {}, // Will be set by component
      },
    ],
  },

  timeout: {
    message: 'Search timed out. Please try again with a simpler query.',
    userMessage: 'Search Timed Out',
    retryable: true,
    actions: [
      {
        id: 'retry',
        label: 'Try Again',
        variant: 'primary',
        onClick: () => {}, // Will be set by component
      },
      {
        id: 'simplify',
        label: 'Simplify Search',
        variant: 'secondary',
        onClick: () => {}, // Will be set by component
      },
    ],
  },

  server: {
    message: 'Something went wrong on our end. Please try again.',
    userMessage: 'Server Error',
    retryable: true,
    actions: [
      {
        id: 'retry',
        label: 'Try Again',
        variant: 'primary',
        onClick: () => {}, // Will be set by component
      },
      {
        id: 'report',
        label: 'Report Issue',
        variant: 'secondary',
        onClick: () => {}, // Will be set by component
      },
    ],
  },

  rate_limit: {
    message: 'You\'ve used your free searches for today. Upgrade to Professional for unlimited searches.',
    userMessage: 'Rate Limit Reached',
    retryable: false,
    actions: [
      {
        id: 'upgrade',
        label: 'Upgrade Now',
        variant: 'primary',
        onClick: () => {}, // Will be set by component
      },
      {
        id: 'later',
        label: 'Try Later',
        variant: 'secondary',
        onClick: () => {}, // Will be set by component
      },
    ],
  },

  no_results: {
    message: 'No matching applications found. Try broadening your search criteria.',
    userMessage: 'No Results Found',
    retryable: true,
    actions: [
      {
        id: 'remove-filters',
        label: 'Remove Filters',
        variant: 'primary',
        onClick: () => {}, // Will be set by component
      },
      {
        id: 'new-search',
        label: 'Start Over',
        variant: 'secondary',
        onClick: () => {}, // Will be set by component
      },
    ],
  },

  unknown: {
    message: 'An unexpected error occurred. Please try again.',
    userMessage: 'Unexpected Error',
    retryable: true,
    actions: [
      {
        id: 'retry',
        label: 'Try Again',
        variant: 'primary',
        onClick: () => {}, // Will be set by component
      },
      {
        id: 'cancel',
        label: 'Go Back',
        variant: 'secondary',
        onClick: () => {}, // Will be set by component
      },
    ],
  },
};

/**
 * Get error configuration by type
 */
export function getErrorConfig(errorType: AnimationErrorType): Omit<AnimationError, 'type'> {
  return ERROR_MESSAGES[errorType] || ERROR_MESSAGES.unknown;
}

/**
 * Create a complete AnimationError object
 */
export function createError(
  errorType: AnimationErrorType,
  customMessage?: string
): AnimationError {
  const config = getErrorConfig(errorType);

  return {
    type: errorType,
    ...config,
    ...(customMessage && { message: customMessage }),
  };
}

/**
 * Stage-specific error mapping
 * Determines which stage should show error based on error type
 */
export const ERROR_STAGE_MAP: Record<AnimationErrorType, number> = {
  parsing: 1, // Stage 1 - Understanding Query
  connection: 2, // Stage 2 - Searching Database
  timeout: 2, // Stage 2 - Searching Database
  server: 2, // Stage 2 - Generic server errors
  rate_limit: 2, // Stage 2 - Searching Database
  no_results: 5, // Stage 5 - Preparing Results
  unknown: 2, // Stage 2 - Default to search stage
};
