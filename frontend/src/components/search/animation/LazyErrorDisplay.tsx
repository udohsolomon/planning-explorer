/**
 * Lazy-loaded Error Display
 * Planning Explorer - Code-split error component
 */

import dynamic from 'next/dynamic';
import type { ErrorDisplayProps } from './ErrorDisplay';

/**
 * Lazy-loaded ErrorDisplay component
 * Only loads when an error occurs (saves ~4KB initial bundle)
 */
export const LazyErrorDisplay = dynamic<ErrorDisplayProps>(
  () => import('./ErrorDisplay').then((mod) => ({ default: mod.ErrorDisplay })),
  {
    loading: () => (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin h-8 w-8 border-4 border-[#043F2E] border-t-transparent rounded-full" />
      </div>
    ),
    ssr: false,
  }
);
