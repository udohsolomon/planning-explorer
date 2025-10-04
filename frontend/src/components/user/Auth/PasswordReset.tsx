'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Mail, ArrowLeft, CheckCircle } from 'lucide-react'
import { isValidEmail } from '@/lib/utils'

interface PasswordResetProps {
  onBack?: () => void
}

export function PasswordReset({ onBack }: PasswordResetProps) {
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)

  const validateForm = () => {
    if (!email.trim()) {
      setError('Email is required')
      return false
    }

    if (!isValidEmail(email)) {
      setError('Please enter a valid email address')
      return false
    }

    setError('')
    return true
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) return

    setIsLoading(true)

    try {
      // Simulate API call - replace with actual password reset
      await new Promise(resolve => setTimeout(resolve, 1000))
      setIsSuccess(true)
    } catch (error) {
      setError('Failed to send reset email. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  if (isSuccess) {
    return (
      <div className="w-full max-w-md mx-auto">
        <Card>
          <CardHeader className="text-center">
            <div className="mx-auto w-12 h-12 bg-planning-bright/10 rounded-full flex items-center justify-center mb-4">
              <CheckCircle className="w-6 h-6 text-planning-bright" />
            </div>
            <CardTitle className="text-2xl">Check your email</CardTitle>
            <CardDescription>
              We've sent a password reset link to {email}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-center text-sm text-planning-text-light">
              <p>Didn't receive the email? Check your spam folder or</p>
              <button
                onClick={() => setIsSuccess(false)}
                className="text-planning-primary hover:text-planning-accent font-medium"
              >
                try a different email address
              </button>
            </div>

            <Button asChild className="w-full">
              <Link href="/auth/login">
                Back to sign in
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="w-full max-w-md mx-auto">
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-2 mb-4">
            {onBack ? (
              <button
                onClick={onBack}
                className="p-1 text-planning-text-light hover:text-planning-primary"
              >
                <ArrowLeft className="w-4 h-4" />
              </button>
            ) : (
              <Link
                href="/auth/login"
                className="p-1 text-planning-text-light hover:text-planning-primary"
              >
                <ArrowLeft className="w-4 h-4" />
              </Link>
            )}
            <div>
              <CardTitle className="text-2xl">Reset your password</CardTitle>
              <CardDescription>
                Enter your email and we'll send you a reset link
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              leftIcon={<Mail />}
              error={error}
              placeholder="Enter your email address"
              disabled={isLoading}
            />

            <Button
              type="submit"
              className="w-full"
              disabled={isLoading}
            >
              {isLoading ? 'Sending...' : 'Send reset link'}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-planning-text-light">
              Remember your password?{' '}
              <Link
                href="/auth/login"
                className="text-planning-primary hover:text-planning-accent font-medium"
              >
                Sign in
              </Link>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}