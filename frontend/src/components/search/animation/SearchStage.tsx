/**
 * Search Stage Component
 * Planning Explorer - Individual animation stage with icon, title, and sub-steps
 */

'use client';

import { motion } from 'framer-motion';
import { StageIcon } from './StageIcon';
import { SearchSubStep } from './SearchSubStep';
import { ConnectionLine } from './ConnectionLine';
import { DEFAULT_TIMINGS } from './config/animationTimings';
import type { SearchStageProps } from '@/types/animation.types';

export function SearchStage({
  stage,
  status,
  isActive,
  isLast,
  dynamicValues,
}: SearchStageProps) {
  const isCompleted = status === 'completed';
  const isPending = status === 'pending';

  // Title opacity based on status
  const getTitleOpacity = () => {
    if (isPending) return 'opacity-50';
    if (isCompleted) return 'opacity-80';
    return 'opacity-100';
  };

  // Title color
  const getTitleColor = () => {
    if (isPending || isCompleted) return 'text-[#6B7280]';
    return 'text-[#1A1A1A]';
  };

  return (
    <div className="flex gap-4 relative">
      {/* Icon column */}
      <div className="flex flex-col items-center relative">
        <StageIcon
          iconName={stage.id.toString()}
          status={status}
          isActive={isActive}
          size={48}
        />

        {/* Connection line to next stage */}
        {!isLast && (
          <div className="mt-2 mb-2 flex-1">
            <ConnectionLine
              isActive={isActive}
              isCompleted={isCompleted}
              height={80}
            />
          </div>
        )}
      </div>

      {/* Content column */}
      <div className="flex-1 pb-6">
        {/* Stage title */}
        <motion.h3
          initial={{ opacity: 0, x: -12, y: 4 }}
          animate={{ opacity: 1, x: 0, y: 0 }}
          transition={{
            duration: 0.4,
            ease: [0.16, 1, 0.3, 1],
          }}
          className={`
            text-xl font-bold mb-3 tracking-tight
            ${getTitleColor()}
            ${getTitleOpacity()}
            transition-all duration-300
          `}
        >
          {stage.title}
        </motion.h3>

        {/* Sub-steps */}
        {(isActive || isCompleted) && (
          <ul className="space-y-1.5">
            {stage.subSteps.map((subStep, index) => (
              <SearchSubStep
                key={subStep.id}
                subStep={subStep}
                isVisible={isActive || isCompleted}
                dynamicValue={
                  subStep.dynamicValue
                    ? dynamicValues[subStep.dynamicValue]
                    : undefined
                }
                delay={isActive ? index * (DEFAULT_TIMINGS.subStepStagger / 1000) : 0}
              />
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
