/**
 * Stage Counter Component
 * Planning Explorer - "Step X of Y" badge indicator
 */

'use client';

import { motion } from 'framer-motion';
import type { StageCounterProps } from '@/types/animation.types';

export function StageCounter({
  currentStage,
  totalStages,
}: StageCounterProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      key={currentStage} // Re-animate on stage change
      transition={{
        duration: 0.2,
        ease: 'easeOut',
      }}
      className="
        absolute top-6 right-6
        md:top-12 md:right-12
        px-3 py-1.5
        bg-[#F3F4F6]
        rounded-lg
        text-sm font-medium text-[#6B7280]
      "
      role="status"
      aria-live="polite"
    >
      Step {currentStage} of {totalStages}
    </motion.div>
  );
}
