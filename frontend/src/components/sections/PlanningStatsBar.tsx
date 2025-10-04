'use client'

import { useEffect, useState } from 'react'
import { Container } from '@/components/ui/Container'
import { apiClient } from '@/lib/api'

interface StatItem {
  value: string
  line1: string
  line2?: string
  subtext: string
}

// Format large numbers for display
function formatNumber(num: number): string {
  if (num >= 1000000) {
    return `+${(num / 1000000).toFixed(1)}M`
  } else if (num >= 1000) {
    return `+${(num / 1000).toFixed(0)}K`
  }
  return `+${num}`
}

// Format percentage with arrow
function formatYoY(percent: number): string {
  const arrow = percent >= 0 ? '↑' : '↓'
  return `${arrow} ${Math.abs(percent)}% YoY`
}

export function PlanningStatsBar() {
  const [stats, setStats] = useState<StatItem[]>([
    {
      value: '+336K',
      line1: 'Planning Applications Received',
      line2: '',
      subtext: '(Year to Sept \'25) ↓ 9% YoY'
    },
    {
      value: '+321K',
      line1: 'Planning Application Decisions',
      line2: '',
      subtext: 'Made 321,400 ↓ 9% YoY'
    },
    {
      value: '+69K',
      line1: 'Planning Permission Granted',
      line2: '',
      subtext: '69,200 - 87% granted'
    },
    {
      value: '+239K',
      line1: 'New Housing Units with Planning',
      line2: '',
      subtext: 'Permission 239,000 ↓ 6% YoY'
    }
  ])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchStats() {
      try {
        const response = await apiClient.getPlanningStats()

        if (response.success && response.data) {
          const data = response.data

          setStats([
            {
              value: formatNumber(data.totalApplications),
              line1: 'Planning Applications Received',
              line2: '',
              subtext: `(Year to Sept '25) ${formatYoY(data.applicationsYoY)}`
            },
            {
              value: formatNumber(data.totalDecisions),
              line1: 'Planning Application Decisions',
              line2: '',
              subtext: `Made ${data.totalDecisions.toLocaleString()} ${formatYoY(data.decisionsYoY)}`
            },
            {
              value: formatNumber(data.totalGranted),
              line1: 'Planning Permission Granted',
              line2: '',
              subtext: `${data.totalGranted.toLocaleString()} - ${Math.round(data.grantedPercentage)}% granted`
            },
            {
              value: formatNumber(data.totalHousingUnits),
              line1: 'New Housing Units with Planning',
              line2: '',
              subtext: `Permission ${data.totalHousingUnits.toLocaleString()} ${formatYoY(data.housingUnitsYoY)}`
            }
          ])
        }
      } catch (error) {
        console.error('Failed to fetch planning stats:', error)
        // Keep default values on error
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  return (
    <div className="bg-gradient-to-r from-[#065940] via-[#087952] to-[#0A9963] py-8 relative z-10">
      <Container>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {stats.map((stat, index) => {
            return (
              <div
                key={index}
                className="text-center"
              >
                {/* Large Value */}
                <div className={`text-5xl lg:text-6xl font-bold text-white mb-2 ${loading ? 'animate-pulse' : ''}`}>
                  {stat.value}
                </div>

                {/* Description Lines */}
                <div className="text-sm lg:text-base font-semibold text-white mb-1 leading-tight">
                  {stat.line1}
                </div>
                {stat.line2 && (
                  <div className="text-sm lg:text-base font-semibold text-white mb-1 leading-tight">
                    {stat.line2}
                  </div>
                )}

                {/* Subtext */}
                <div className="text-sm text-white/90 mt-1">
                  {stat.subtext}
                </div>
              </div>
            )
          })}
        </div>
      </Container>
    </div>
  )
}