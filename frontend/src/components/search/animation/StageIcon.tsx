/**
 * Stage Icon Component
 * Planning Explorer - Animated icon with status-based styling
 */

'use client';

import { memo } from 'react';
import { motion } from 'framer-motion';
import { Check } from 'lucide-react';
import { getStageIcon } from './config/animationIcons';
import type { StageIconProps } from '@/types/animation.types';

export const StageIcon = memo(function StageIcon({
  iconName,
  status,
  isActive,
  size = 48,
}: StageIconProps) {
  const Icon = getStageIcon(parseInt(iconName));

  // Background color based on status
  const getBackgroundColor = () => {
    switch (status) {
      case 'active':
        return 'bg-[#043F2E]'; // Primary Green
      case 'completed':
        return 'bg-[#10B981]'; // Success Green
      case 'error':
        return 'bg-[#EF4444]'; // Error Red
      case 'pending':
      default:
        return 'bg-[#F3F4F6]'; // Light Gray
    }
  };

  // Icon color
  const getIconColor = () => {
    return status === 'pending' ? 'text-[#6B7280]' : 'text-white';
  };

  // Show checkmark for completed stages
  const showCheckmark = status === 'completed';

  return (
    <div className="relative flex-shrink-0">
      {/* Icon container */}
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{
          duration: 0.3,
          ease: [0.34, 1.56, 0.64, 1], // Elastic easing
        }}
        className={`
          flex items-center justify-center rounded-full
          ${getBackgroundColor()}
          transition-colors duration-200
        `}
        style={{ width: size, height: size }}
      >
        {showCheckmark ? (
          // Checkmark for completed stage
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: [0, 1.2, 1] }}
            transition={{
              duration: 0.3,
              times: [0, 0.6, 1],
              ease: [0.34, 1.56, 0.64, 1], // Elastic
            }}
          >
            <Check className={getIconColor()} size={size * 0.5} strokeWidth={3} />
          </motion.div>
        ) : (
          // Stage icon with pulse animation when active
          <motion.div
            animate={
              isActive
                ? {
                    opacity: [1, 0.85, 1],
                  }
                : {}
            }
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          >
            <Icon className={getIconColor()} size={size * 0.5} strokeWidth={2} />
          </motion.div>
        )}
      </motion.div>
    </div>
  );
});
