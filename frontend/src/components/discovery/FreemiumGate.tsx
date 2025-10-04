/**
 * FreemiumGate Component
 * Displays a soft paywall overlay encouraging users to sign up to see more results
 * PRD Requirement: "Sign up to see all" overlay after 5 results
 */

import { Button } from '@/components/ui/Button'
import { Lock, ArrowRight } from 'lucide-react'
import Link from 'next/link'

export interface FreemiumGateProps {
  totalResults: number
  visibleResults?: number
  ctaText?: string
  className?: string
}

export function FreemiumGate({
  totalResults,
  visibleResults = 5,
  ctaText = 'Sign up to see all results',
  className = '',
}: FreemiumGateProps) {
  const hiddenResults = totalResults - visibleResults

  if (hiddenResults <= 0) {
    return null
  }

  return (
    <div className={`relative ${className}`}>
      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-white/80 to-white z-10 pointer-events-none" />

      {/* CTA Card */}
      <div className="relative z-20 bg-white border border-gray-200 rounded-lg shadow-lg p-8 text-center max-w-2xl mx-auto mt-8">
        <div className="flex justify-center mb-4">
          <div className="bg-planning-primary/10 rounded-full p-3">
            <Lock className="h-8 w-8 text-planning-primary" />
          </div>
        </div>

        <h3 className="text-2xl font-bold text-gray-900 mb-2">
          {hiddenResults.toLocaleString()} more results available
        </h3>

        <p className="text-gray-600 mb-6 max-w-md mx-auto">
          Create a free account to view all {totalResults.toLocaleString()} planning applications with full
          details, AI insights, and advanced filtering.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link href="/auth/register">
            <Button size="lg" className="w-full sm:w-auto">
              {ctaText}
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>

          <Link href="/auth/login">
            <Button variant="outline" size="lg" className="w-full sm:w-auto">
              Already have an account? Sign in
            </Button>
          </Link>
        </div>

        <p className="text-xs text-gray-500 mt-4">
          Free forever • No credit card required • Cancel anytime
        </p>
      </div>
    </div>
  )
}

/**
 * InlineFreemiumGate Component
 * Smaller inline version for use within tables or lists
 */
export function InlineFreemiumGate({ totalResults, className = '' }: { totalResults: number; className?: string }) {
  return (
    <div className={`bg-gray-50 border border-gray-200 rounded-lg p-6 text-center ${className}`}>
      <Lock className="h-6 w-6 text-planning-primary mx-auto mb-2" />
      <p className="text-sm font-medium text-gray-700 mb-3">
        Sign up to see all {totalResults.toLocaleString()} applications
      </p>
      <Link href="/auth/register">
        <Button size="sm" className="text-sm">
          Create free account
          <ArrowRight className="ml-2 h-3 w-3" />
        </Button>
      </Link>
    </div>
  )
}
