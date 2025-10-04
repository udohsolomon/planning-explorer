'use client'

import { useState, useEffect } from 'react'
import { Container } from '@/components/ui/Container'
import { Building, Clock, TrendingUp, CheckCircle } from 'lucide-react'

interface StatisticCardProps {
  icon: React.ComponentType<{ className?: string }>
  value: string
  label: string
  trend?: string
  color?: string
}

function StatisticCard({ icon: Icon, value, label, trend, color = 'text-planning-bright' }: StatisticCardProps) {
  const [displayValue, setDisplayValue] = useState('0')

  useEffect(() => {
    const numericValue = parseInt(value.replace(/[^\d]/g, ''))
    const duration = 2000
    const steps = 60
    const increment = numericValue / steps

    let current = 0
    const timer = setInterval(() => {
      current += increment
      if (current >= numericValue) {
        setDisplayValue(value)
        clearInterval(timer)
      } else {
        setDisplayValue(Math.floor(current).toLocaleString())
      }
    }, duration / steps)

    return () => clearInterval(timer)
  }, [value])

  return (
    <div className="bg-white rounded-2xl p-8 shadow-lg border border-planning-border hover:shadow-xl transition-shadow">
      <div className="flex items-center space-x-4">
        <div className={`p-3 rounded-xl bg-gradient-to-br from-planning-primary/10 to-planning-accent/10`}>
          <Icon className={`w-8 h-8 ${color}`} />
        </div>
        <div className="flex-1">
          <div className="text-3xl font-bold text-planning-primary mb-1">
            {displayValue}
          </div>
          <div className="text-planning-text-light font-medium">
            {label}
          </div>
          {trend && (
            <div className="flex items-center space-x-1 mt-2">
              <TrendingUp className="w-4 h-4 text-planning-bright" />
              <span className="text-sm text-planning-bright font-medium">{trend}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export function LiveStatistics() {
  // Simplified version since statistics are now in hero section
  return (
    <section className="py-16 bg-white">
      <Container>
        <div className="text-center">
          <div className="inline-block px-4 py-2 bg-planning-accent/10 rounded-full mb-4">
            <span className="text-planning-primary font-semibold text-sm uppercase tracking-wider">
              Live Data Feed
            </span>
          </div>
          <div className="flex items-center justify-center space-x-2">
            <div className="w-2 h-2 bg-planning-accent rounded-full animate-pulse"></div>
            <span className="text-sm text-planning-accent font-medium">
              Data updated every 15 minutes from all UK planning authorities
            </span>
          </div>
        </div>
      </Container>
    </section>
  )
}