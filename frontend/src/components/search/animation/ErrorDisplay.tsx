/**
 * Error Display Component
 * Planning Explorer - Error state UI with recovery actions
 */

'use client';

import { motion } from 'framer-motion';
import { getErrorIcon } from './config/animationIcons';
import type { ErrorDisplayProps } from '@/types/animation.types';

export function ErrorDisplay({
  error,
  stage,
  onRetry,
  onCancel,
}: ErrorDisplayProps) {
  const ErrorIcon = getErrorIcon(error.type);

  // Get error color based on type
  const getErrorColor = () => {
    switch (error.type) {
      case 'rate_limit':
      case 'timeout':
        return 'text-[#F59E0B]'; // Orange
      case 'parsing':
        return 'text-[#F59E0B]'; // Orange
      case 'no_results':
        return 'text-[#3B82F6]'; // Blue
      case 'connection':
      case 'server':
      case 'unknown':
      default:
        return 'text-[#EF4444]'; // Red
    }
  };

  // Handle action clicks
  const handleAction = (actionId: string) => {
    switch (actionId) {
      case 'retry':
        onRetry?.();
        break;
      case 'cancel':
      case 'later':
        onCancel?.();
        break;
      case 'upgrade':
        // Navigate to upgrade page
        window.location.href = '/pricing';
        break;
      case 'filters':
        // Navigate to filter-based search
        onCancel?.();
        break;
      case 'rephrase':
      case 'new-search':
        onCancel?.();
        break;
      case 'remove-filters':
        // Trigger filter removal
        onRetry?.();
        break;
      case 'simplify':
        onCancel?.();
        break;
      case 'report':
        // Open support dialog
        window.open('mailto:support@planningexplorer.com', '_blank');
        break;
      default:
        break;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className="flex flex-col items-center text-center py-8"
      role="alert"
      aria-live="assertive"
    >
      {/* Error Icon with shake animation */}
      <motion.div
        initial={{ x: 0 }}
        animate={{ x: [-10, 10, -10, 10, 0] }}
        transition={{ duration: 0.5 }}
        className={`mb-4 ${getErrorColor()}`}
      >
        <ErrorIcon size={48} strokeWidth={1.5} />
      </motion.div>

      {/* Error Title */}
      <h3 className="text-xl font-semibold text-[#1A1A1A] mb-2">
        {error.userMessage}
      </h3>

      {/* Error Message */}
      <p className="text-[#666666] text-sm max-w-md mb-6">
        {error.message}
      </p>

      {/* Action Buttons */}
      {error.actions && error.actions.length > 0 && (
        <div className="flex flex-col sm:flex-row gap-3 w-full max-w-sm">
          {error.actions.map((action) => (
            <button
              key={action.id}
              onClick={() => handleAction(action.id)}
              data-variant={action.variant}
              className={`
                flex-1 px-6 py-3 rounded-lg font-medium text-sm
                transition-all duration-200
                focus:outline-none focus:ring-2 focus:ring-offset-2
                ${
                  action.variant === 'primary'
                    ? 'bg-[#043F2E] text-white hover:bg-[#065940] focus:ring-[#043F2E]'
                    : action.variant === 'danger'
                    ? 'bg-[#EF4444] text-white hover:bg-[#DC2626] focus:ring-[#EF4444]'
                    : 'border-2 border-[#E5E7EB] text-[#6B7280] hover:border-[#6B7280] focus:ring-[#6B7280]'
                }
              `}
            >
              {action.label}
            </button>
          ))}
        </div>
      )}

      {/* Upgrade CTA for rate limit */}
      {error.type === 'rate_limit' && (
        <div className="mt-6 p-4 bg-[#F3F4F6] rounded-lg max-w-md">
          <p className="text-sm text-[#6B7280]">
            <span className="font-semibold text-[#043F2E]">Professional Plan</span> includes:
          </p>
          <ul className="mt-2 text-xs text-[#6B7280] space-y-1 text-left">
            <li>✓ Unlimited AI-enhanced searches</li>
            <li>✓ Advanced opportunity scoring</li>
            <li>✓ Email alerts and saved searches</li>
          </ul>
        </div>
      )}
    </motion.div>
  );
}
