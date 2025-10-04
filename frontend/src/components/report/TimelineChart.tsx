'use client'

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, LabelList } from 'recharts'

interface TimelineChartProps {
  data?: Array<{
    type: string
    days: number
  }>
  className?: string
}

// Default data matching PDF version
const defaultData = [
  { type: 'Householder', days: 42 },
  { type: 'Full Planning', days: 78 },
  { type: 'Listed Building', days: 65 },
  { type: 'Prior Approval', days: 28 },
]

export function TimelineChart({ data = defaultData, className = '' }: TimelineChartProps) {
  // Colors matching Planning Insights brand
  const primaryColor = '#043F2E' // Planning green
  const maxDays = 90

  return (
    <div className={`bg-slate-50 rounded-lg p-6 print:bg-white ${className}`}>
      <h3 className="text-base font-semibold text-slate-800 mb-4">
        Average Decision Timeline by Application Type
      </h3>

      <div className="h-[280px] md:h-[300px] print:h-[220px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 5, right: 80, left: 120, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />

            <XAxis
              type="number"
              tick={{ fill: '#64748b', fontSize: 11 }}
              axisLine={{ stroke: '#cbd5e1' }}
              tickLine={false}
              domain={[0, maxDays]}
              ticks={[0, 25, 50, 75, maxDays]}
              label={{
                value: 'Average Days',
                position: 'bottom',
                offset: -5,
                style: { fill: '#64748b', fontSize: 11 }
              }}
            />

            <YAxis
              type="category"
              dataKey="type"
              tick={{ fill: '#334155', fontSize: 12 }}
              axisLine={{ stroke: '#cbd5e1' }}
              tickLine={false}
              width={110}
            />

            <Tooltip
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                fontSize: '12px'
              }}
              labelStyle={{ color: '#334155', fontWeight: 600 }}
              formatter={(value: number) => [`${value} days`, 'Average Time']}
              cursor={{ fill: 'rgba(4, 63, 46, 0.05)' }}
            />

            <Bar
              dataKey="days"
              fill={primaryColor}
              radius={[0, 4, 4, 0]}
              opacity={0.9}
              className="print:opacity-100"
            >
              <LabelList
                dataKey="days"
                position="right"
                formatter={(value: number) => `${value} days`}
                style={{ fill: '#043F2E', fontSize: 11, fontWeight: 600 }}
              />
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={primaryColor}
                  opacity={0.85 + (index * 0.05)}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Info note */}
      <p className="text-xs text-slate-500 mt-4 print:mt-2">
        Average processing times based on historical data. Actual timelines may vary by authority.
      </p>
    </div>
  )
}
