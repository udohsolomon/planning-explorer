'use client'

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

interface VolumeChartProps {
  data?: Array<{
    month: string
    applications: number
    isPeak?: boolean
  }>
  className?: string
}

// Default data matching PDF version
const defaultData = [
  { month: 'Jan', applications: 85, isPeak: false },
  { month: 'Feb', applications: 62, isPeak: false },
  { month: 'Mar', applications: 94, isPeak: false },
  { month: 'Apr', applications: 71, isPeak: false },
  { month: 'May', applications: 83, isPeak: false },
  { month: 'Jun', applications: 78, isPeak: false },
  { month: 'Jul', applications: 100, isPeak: true }, // Peak month
  { month: 'Aug', applications: 58, isPeak: false },
  { month: 'Sep', applications: 89, isPeak: false },
  { month: 'Oct', applications: 76, isPeak: false },
  { month: 'Nov', applications: 64, isPeak: false },
  { month: 'Dec', applications: 69, isPeak: false },
]

export function VolumeChart({ data = defaultData, className = '' }: VolumeChartProps) {
  // Colors matching Planning Insights brand
  const primaryColor = '#043F2E' // Planning green
  const peakColor = '#ef4444' // Red for peak

  return (
    <div className={`bg-slate-50 rounded-lg p-6 print:bg-white ${className}`}>
      <h3 className="text-base font-semibold text-slate-800 mb-4">
        Planning Application Volume Trends
        <span className="text-xs font-normal text-slate-500 ml-2">(Last 12 Months)</span>
      </h3>

      <div className="h-[300px] md:h-[350px] print:h-[250px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />

            <XAxis
              dataKey="month"
              tick={{ fill: '#64748b', fontSize: 12 }}
              axisLine={{ stroke: '#cbd5e1' }}
              tickLine={false}
              angle={-45}
              textAnchor="end"
              height={60}
            />

            <YAxis
              tick={{ fill: '#64748b', fontSize: 12 }}
              axisLine={{ stroke: '#cbd5e1' }}
              tickLine={false}
              label={{
                value: 'Applications Submitted',
                angle: -90,
                position: 'insideLeft',
                style: { fill: '#043F2E', fontSize: 12, fontWeight: 600 }
              }}
            />

            <Tooltip
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                fontSize: '12px'
              }}
              labelStyle={{ color: '#334155', fontWeight: 600 }}
              cursor={{ fill: 'rgba(4, 63, 46, 0.05)' }}
            />

            <Bar
              dataKey="applications"
              radius={[4, 4, 0, 0]}
            >
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.isPeak ? peakColor : primaryColor}
                  opacity={0.9}
                  className="print:opacity-100"
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center gap-6 mt-4 text-xs print:hidden">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded" style={{ backgroundColor: primaryColor }}></div>
          <span className="text-slate-600">Approved</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded" style={{ backgroundColor: peakColor }}></div>
          <span className="text-slate-600">Peak Month</span>
        </div>
      </div>
    </div>
  )
}
