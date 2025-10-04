/**
 * Search Sub-Step Component
 * Planning Explorer - Individual sub-step item with animation
 */

'use client';

import { memo, useMemo } from 'react';
import { motion } from 'framer-motion';
import type { SearchSubStepProps } from '@/types/animation.types';

export const SearchSubStep = memo(function SearchSubStep({
  subStep,
  isVisible,
  dynamicValue,
  delay,
}: SearchSubStepProps) {
  // Format sub-step text with dynamic value if applicable (memoized)
  const text = useMemo(() => {
    if (dynamicValue !== undefined && subStep.dynamicValue) {
      return `${dynamicValue} ${subStep.text}`;
    }
    return subStep.text;
  }, [dynamicValue, subStep.dynamicValue, subStep.text]);

  return (
    <motion.li
      initial={{ opacity: 0, x: -10 }}
      animate={isVisible ? { opacity: 1, x: 0 } : { opacity: 0, x: -10 }}
      transition={{
        duration: 0.15,
        delay,
        ease: 'easeOut',
      }}
      className="flex items-start gap-2 text-sm text-[#666666] leading-relaxed"
    >
      {/* Diamond bullet */}
      <span className="text-[#087952] mt-0.5 flex-shrink-0" aria-hidden="true">
        ◆
      </span>

      {/* Step text */}
      <span className="flex-1">{text}</span>
    </motion.li>
  );
});
