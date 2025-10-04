import * as React from 'react'
import { cn } from '@/lib/utils'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost'
  size?: 'sm' | 'md' | 'lg' | 'xl'
  children: React.ReactNode
  asChild?: boolean
}

const buttonVariants = {
  primary: 'bg-planning-button text-white hover:bg-planning-primary hover:text-white',
  secondary: 'bg-planning-primary text-planning-white hover:bg-planning-accent',
  outline: 'border-2 border-planning-primary text-planning-primary hover:bg-planning-primary hover:text-planning-white',
  ghost: 'text-planning-primary hover:bg-planning-primary/10'
}

const buttonSizes = {
  sm: 'px-4 py-2 text-sm',
  md: 'px-6 py-3 text-base',
  lg: 'px-8 py-4 text-lg',
  xl: 'px-9 py-5 text-lg' // Planning Insights large button: 36px horizontal padding
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'lg', children, ...props }, ref) => {
    return (
      <button
        className={cn(
          // Base styles
          'inline-flex items-center justify-center',
          'font-semibold rounded-lg',
          'transition-all duration-150 ease-in-out',
          'focus:outline-none focus:ring-2 focus:ring-planning-primary focus:ring-offset-2',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          'transform hover:-translate-y-0.5',
          // Variant styles
          buttonVariants[variant],
          // Size styles
          buttonSizes[size],
          className
        )}
        ref={ref}
        {...props}
      >
        {children}
      </button>
    )
  }
)

Button.displayName = 'Button'