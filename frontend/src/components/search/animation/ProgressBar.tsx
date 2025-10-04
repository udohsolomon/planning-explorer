/**
 * Progress Bar Component
 * Planning Explorer - Top progress indicator with gradient
 */

'use client';

import { motion } from 'framer-motion';
import type { ProgressBarProps } from '@/types/animation.types';

export function ProgressBar({ progress, isVisible }: ProgressBarProps) {
  if (!isVisible) return null;

  return (
    <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-[#F3F4F6] to-[#E5E7EB] rounded-t-3xl overflow-hidden">
      <motion.div
        className="h-full relative"
        style={{
          background: 'linear-gradient(90deg, #043F2E 0%, #087952 50%, #10B981 100%)',
          boxShadow: '0 0 12px rgba(16, 185, 129, 0.4)',
        }}
        initial={{ width: '0%', opacity: 0.8 }}
        animate={{ width: `${progress}%`, opacity: 1 }}
        transition={{
          width: { duration: 0.5, ease: [0.16, 1, 0.3, 1] },
          opacity: { duration: 0.2 },
        }}
      >
        {/* Shimmer effect */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
          animate={{
            x: ['-100%', '200%'],
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: 'linear',
          }}
        />
      </motion.div>
    </div>
  );
}
