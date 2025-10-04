/**
 * Connection Line Component
 * Planning Explorer - Animated connecting line between stages
 */

'use client';

import { motion } from 'framer-motion';
import type { ConnectionLineProps } from '@/types/animation.types';

export function ConnectionLine({
  isActive,
  isCompleted,
  height,
}: ConnectionLineProps) {
  return (
    <div
      className="w-0.5 relative overflow-hidden"
      style={{ height: `${height}px` }}
    >
      {/* Base dashed line (always visible) */}
      <div className="absolute inset-0 border-l-2 border-dashed border-[#E5E7EB]" />

      {/* Animated gradient line (shown when active or completed) */}
      {(isActive || isCompleted) && (
        <svg
          className="absolute inset-0 w-full h-full"
          preserveAspectRatio="none"
          viewBox="0 0 2 100"
        >
          <defs>
            {/* Gradient from Primary Green to Success Green */}
            <linearGradient
              id="connection-gradient"
              x1="0%"
              y1="0%"
              x2="0%"
              y2="100%"
            >
              <stop offset="0%" stopColor="#043F2E" />
              <stop offset="100%" stopColor="#10B981" />
            </linearGradient>
          </defs>

          {/* Animated line with drawing effect */}
          <motion.line
            x1="1"
            y1="0"
            x2="1"
            y2="100"
            stroke="url(#connection-gradient)"
            strokeWidth="2"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{
              pathLength: 1,
              opacity: 1,
            }}
            transition={{
              pathLength: {
                duration: 0.4,
                ease: 'easeInOut',
              },
              opacity: {
                duration: 0.2,
              },
            }}
          />
        </svg>
      )}
    </div>
  );
}
