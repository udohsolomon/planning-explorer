/**
 * Cancel Button Component
 * Planning Explorer - Cancellation control with timing logic
 */

'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import type { CancelButtonProps } from '@/types/animation.types';

export function CancelButton({
  isVisible,
  isEnhanced,
  onCancel,
}: CancelButtonProps) {
  return (
    <AnimatePresence>
      {isVisible && (
        <motion.button
          initial={{ opacity: 0, y: 12, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 8, scale: 0.97 }}
          whileHover={{ scale: 1.02, y: -2 }}
          whileTap={{ scale: 0.98 }}
          transition={{
            duration: 0.4,
            ease: [0.16, 1, 0.3, 1],
          }}
          onClick={onCancel}
          data-cancel-button
          className={`
            mt-8 w-full md:w-auto
            px-8 py-3.5
            rounded-xl
            font-semibold text-sm
            transition-all duration-300
            flex items-center justify-center gap-2.5
            focus:outline-none focus:ring-2 focus:ring-[#043F2E]/50 focus:ring-offset-2
            shadow-lg hover:shadow-xl
            ${
              isEnhanced
                ? 'bg-gradient-to-r from-[#043F2E] to-[#065940] text-white border border-[#043F2E]/20 hover:from-[#065940] hover:to-[#087952]'
                : 'bg-white border-2 border-[#E5E7EB] text-[#6B7280] hover:border-[#9CA3AF] hover:text-[#1F2937]'
            }
          `}
          style={{
            boxShadow: isEnhanced
              ? '0 4px 16px rgba(4, 63, 46, 0.2), 0 0 0 1px rgba(16, 185, 129, 0.1)'
              : '0 2px 8px rgba(0, 0, 0, 0.08)',
          }}
          aria-label="Cancel search"
        >
          <X size={18} strokeWidth={2.5} />
          {isEnhanced ? 'Cancel Search' : 'Cancel'}
        </motion.button>
      )}
    </AnimatePresence>
  );
}
