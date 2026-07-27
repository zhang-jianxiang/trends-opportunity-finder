'use client'

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'

type ChartDataPoint = Record<string, string | number>

interface SeriesConfig {
  name: string
  color: string
}

interface TrendLineChartProps {
  data: ChartDataPoint[]
  series: SeriesConfig[]
}

export function TrendLineChart({ data, series }: TrendLineChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="h-[300px] flex items-center justify-center text-zinc-600 text-sm">
        暂无趋势数据，等待数据采集...
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#27272f" />
        <XAxis dataKey="date" stroke="#71717a" fontSize={11} tickFormatter={(v) => String(v).slice(5)} />
        <YAxis stroke="#71717a" fontSize={11} />
        <Tooltip
          contentStyle={{ background: '#13131a', border: '1px solid #27272f', borderRadius: '8px' }}
          labelStyle={{ color: '#a1a1aa' }}
        />
        {series.map((s) => (
          <Line
            key={s.name}
            type="monotone"
            dataKey={s.name}
            stroke={s.color}
            strokeWidth={2}
            dot={false}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  )
}

interface DirectionChartProps {
  data: { name: string; value: number; fill: string }[]
}

export function DirectionBarChart({ data }: DirectionChartProps) {
  if (!data || data.every(d => d.value === 0)) {
    return (
      <div className="h-[300px] flex items-center justify-center text-zinc-600 text-sm">
        暂无数据
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#27272f" />
        <XAxis dataKey="name" stroke="#71717a" fontSize={11} />
        <YAxis stroke="#71717a" fontSize={11} />
        <Tooltip
          contentStyle={{ background: '#13131a', border: '1px solid #27272f', borderRadius: '8px' }}
        />
        <Bar dataKey="value" radius={[8, 8, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
