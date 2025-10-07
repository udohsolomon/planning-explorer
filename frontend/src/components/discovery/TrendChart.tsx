/**
 * TrendChart Component
 * Recharts wrapper with responsive configuration and export functionality
 * PRD Requirement: Recharts wrapper with responsive config
 * Supports: LineChart, PieChart, BarChart
 */

'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Download } from 'lucide-react'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  TooltipProps,
} from 'recharts'
import { ReactNode } from 'react'

// Color palette matching Planning Explorer brand (#7CB342)
export const CHART_COLORS = {
  primary: '#7CB342',
  secondary: '#388E3C',
  accent: '#FFA726',
  danger: '#EF5350',
  info: '#42A5F5',
  warning: '#FFCA28',
  success: '#66BB6A',
  palette: ['#7CB342', '#388E3C', '#81C784', '#66BB6A', '#4CAF50', '#43A047', '#2E7D32', '#1B5E20'],
}

export interface TrendChartProps {
  title: string
  description?: string
  data: any[]
  type: 'line' | 'bar' | 'pie'
  dataKeys?: {
    xAxis?: string
    yAxis?: string[]
    nameKey?: string
    valueKey?: string
  }
  height?: number
  colors?: string[]
  showExport?: boolean
  onExport?: () => void
  className?: string
  children?: ReactNode
}

export function TrendChart({
  title,
  description,
  data,
  type,
  dataKeys = {},
  height = 400,
  colors = CHART_COLORS.palette,
  showExport = false,
  onExport,
  className = '',
  children,
}: TrendChartProps) {
  const handleExport = () => {
    if (onExport) {
      onExport()
    } else {
      // Default export to CSV
      const csvContent = convertToCSV(data)
      const blob = new Blob([csvContent], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${title.replace(/\s+/g, '_')}.csv`
      link.click()
      window.URL.revokeObjectURL(url)
    }
  }

  // Validate that we have the necessary data
  const hasValidData = data && data.length > 0
  const hasValidYAxis = type !== 'line' && type !== 'bar' || (dataKeys.yAxis && dataKeys.yAxis.length > 0)

  const renderChart = () => {
    // Validation checks moved outside ResponsiveContainer
    if (!hasValidData) {
      return (
        <div className="flex items-center justify-center" style={{ height }}>
          <p className="text-gray-500 text-sm">No data available</p>
        </div>
      )
    }

    if ((type === 'line' || type === 'bar') && !hasValidYAxis) {
      return (
        <div className="flex items-center justify-center" style={{ height }}>
          <p className="text-gray-500 text-sm">Invalid chart configuration</p>
        </div>
      )
    }

    // ResponsiveContainer wraps valid charts
    return (
      <ResponsiveContainer width="100%" height={height}>
        {type === 'line' ? (
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis
              dataKey={dataKeys.xAxis || 'name'}
              stroke="#666"
              tick={{ fill: '#666', fontSize: 12 }}
            />
            <YAxis stroke="#666" tick={{ fill: '#666', fontSize: 12 }} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            {dataKeys.yAxis?.map((key, index) => (
              <Line
                key={key}
                type="monotone"
                dataKey={key}
                stroke={colors[index % colors.length]}
                strokeWidth={2}
                name={formatLabel(key)}
              />
            ))}
          </LineChart>
        ) : type === 'bar' ? (
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis
              dataKey={dataKeys.xAxis || 'name'}
              stroke="#666"
              tick={{ fill: '#666', fontSize: 12 }}
            />
            <YAxis stroke="#666" tick={{ fill: '#666', fontSize: 12 }} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            {dataKeys.yAxis?.map((key, index) => (
              <Bar
                key={key}
                dataKey={key}
                fill={colors[index % colors.length]}
                name={formatLabel(key)}
              />
            ))}
          </BarChart>
        ) : type === 'pie' ? (
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }: any) => `${name} (${(percent * 100).toFixed(0)}%)`}
              outerRadius={120}
              fill="#8884d8"
              dataKey={dataKeys.valueKey || 'value'}
              nameKey={dataKeys.nameKey || 'name'}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        ) : (
          <></>
        )}
      </ResponsiveContainer>
    )
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>{title}</CardTitle>
            {description && <CardDescription>{description}</CardDescription>}
          </div>
          {showExport && (
            <Button variant="outline" size="sm" onClick={handleExport}>
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {children || renderChart()}
      </CardContent>
    </Card>
  )
}

/**
 * Custom Tooltip Component
 */
function CustomTooltip({ active, payload, label }: TooltipProps<any, any>) {
  if (!active || !payload || !payload.length) {
    return null
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
      {label && <p className="font-medium text-gray-900 mb-2">{label}</p>}
      <div className="space-y-1">
        {payload.map((entry: any, index: number) => (
          <div key={`item-${index}`} className="flex items-center gap-2 text-sm">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-gray-600">{entry.name}:</span>
            <span className="font-medium text-gray-900">
              {typeof entry.value === 'number'
                ? entry.value.toLocaleString()
                : entry.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

/**
 * Utility Functions
 */
function formatLabel(key: string): string {
  return key
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

function convertToCSV(data: any[]): string {
  if (!data || data.length === 0) return ''

  const headers = Object.keys(data[0])
  const rows = data.map((row) => headers.map((header) => row[header]).join(','))

  return [headers.join(','), ...rows].join('\n')
}
