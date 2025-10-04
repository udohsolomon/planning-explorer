/**
 * Animation Card Component
 * Planning Explorer - Modal container with brand styling
 */

'use client';

import { motion } from 'framer-motion';
import { ReactNode, forwardRef } from 'react';

interface AnimationCardProps {
  children: ReactNode;
}

export const AnimationCard = forwardRef<HTMLDivElement, AnimationCardProps>(
  ({ children }, ref) => {
    return (
      <motion.div
        ref={ref}
        initial={{ opacity: 0, scale: 0.92, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 10 }}
        transition={{
          duration: 0.5,
          ease: [0.16, 1, 0.3, 1], // Premium spring easing
          opacity: { duration: 0.3 },
        }}
        className="
          relative z-50
          w-full max-w-[720px]
          mx-4
          md:mx-auto
          bg-white/95
          backdrop-blur-xl
          rounded-3xl
          border border-[#043F2E]/10
          p-8 md:p-14
          shadow-[0_20px_60px_-15px_rgba(4,63,46,0.25),0_0_0_1px_rgba(16,185,129,0.05)]
          overflow-hidden
        "
        style={{
          boxShadow: `
            0 20px 60px -15px rgba(4, 63, 46, 0.25),
            0 0 0 1px rgba(16, 185, 129, 0.05),
            inset 0 1px 0 0 rgba(255, 255, 255, 0.8)
          `,
        }}
        role="dialog"
        aria-modal="true"
        aria-labelledby="search-animation-title"
        aria-describedby="search-animation-description"
      >
        {/* Screen reader only title */}
        <h2 id="search-animation-title" className="sr-only">
          AI Search in Progress
        </h2>
        <p id="search-animation-description" className="sr-only">
          We're analyzing your search query across 336,000+ planning applications
        </p>

        {children}
      </motion.div>
    );
  }
);

AnimationCard.displayName = 'AnimationCard';
