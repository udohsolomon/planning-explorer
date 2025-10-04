/**
 * Animation Backdrop Component
 * Planning Explorer - Modal overlay with blur effect
 */

'use client';

import { motion } from 'framer-motion';

interface AnimationBackdropProps {
  onClick?: () => void;
}

export function AnimationBackdrop({ onClick }: AnimationBackdropProps) {
  return (
    <motion.div
      initial={{ opacity: 0, backdropFilter: 'blur(0px)' }}
      animate={{ opacity: 1, backdropFilter: 'blur(12px)' }}
      exit={{ opacity: 0, backdropFilter: 'blur(0px)' }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      onClick={onClick}
      className="fixed inset-0 z-40 bg-gradient-to-br from-[#043F2E]/10 via-black/5 to-[#10B981]/5"
      style={{
        backgroundImage: 'radial-gradient(circle at 50% 0%, rgba(16, 185, 129, 0.08), transparent 50%)',
      }}
      aria-hidden="true"
    />
  );
}
