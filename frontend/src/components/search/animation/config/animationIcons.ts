/**
 * AI Search Animation Icon Mappings
 * Planning Explorer - Icon Configuration
 */

import {
  Brain,
  Database,
  Filter,
  TrendingUp,
  Sparkles,
  Check,
  AlertTriangle,
  HelpCircle,
  XCircle,
  Clock,
  X,
  Loader2,
  Info,
  type LucideIcon,
} from 'lucide-react';

/**
 * Stage icons mapping (by stage ID)
 */
export const STAGE_ICONS: Record<number, LucideIcon> = {
  1: Brain, // Understanding Query
  2: Database, // Searching Database
  3: Filter, // Filtering Results
  4: TrendingUp, // Ranking Matches
  5: Sparkles, // Preparing Results
};

/**
 * Status icons
 */
export const STATUS_ICONS = {
  completed: Check,
  error: AlertTriangle,
  loading: Loader2,
} as const;

/**
 * Error type icons
 */
export const ERROR_ICONS: Record<string, LucideIcon> = {
  connection: AlertTriangle,
  parsing: HelpCircle,
  timeout: Clock,
  server: XCircle,
  rate_limit: Clock,
  no_results: Info,
  unknown: XCircle,
};

/**
 * Action icons
 */
export const ACTION_ICONS = {
  cancel: X,
  retry: Loader2,
  close: X,
} as const;

/**
 * Get icon component by stage ID
 */
export function getStageIcon(stageId: number): LucideIcon {
  return STAGE_ICONS[stageId] || Brain;
}

/**
 * Get icon component by error type
 */
export function getErrorIcon(errorType: string): LucideIcon {
  return ERROR_ICONS[errorType] || XCircle;
}

/**
 * Icon size configurations (in pixels)
 */
export const ICON_SIZES = {
  desktop: {
    stage: 48,
    checkmark: 24,
    error: 32,
  },
  tablet: {
    stage: 44,
    checkmark: 22,
    error: 28,
  },
  mobile: {
    stage: 40,
    checkmark: 20,
    error: 24,
  },
} as const;

/**
 * Get icon size based on device type
 */
export function getIconSize(
  type: keyof typeof ICON_SIZES.desktop,
  isMobile: boolean,
  isTablet: boolean
): number {
  if (isMobile) {
    return ICON_SIZES.mobile[type];
  }
  if (isTablet) {
    return ICON_SIZES.tablet[type];
  }
  return ICON_SIZES.desktop[type];
}
