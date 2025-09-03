'use client'

import { useMemo } from 'react'
import { 
  ResponsiveContainer as RechartsResponsiveContainer,
  LineChart,
  AreaChart,
  BarChart,
  PieChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Line,
  Area,
  Bar,
  Cell
} from 'recharts'
import { formatCurrency, formatPercentage, cn } from '@/lib/utils'
import type { ChartConfig, ChartDataPoint } from '@/types'

interface ResponsiveChartProps {
  config: ChartConfig
  data: any[]
  height?: number
  className?: string
}

export function ResponsiveChart({ 
  config, 
  data, 
  height = 400, 
  className 
}: ResponsiveChartProps) {
  const formatValue = useMemo(() => {
    switch (config.yAxis.format) {
      case 'currency':
        return (value: number) => formatCurrency(value)
      case 'percentage':
        return (value: number) => formatPercentage(value / 100)
      case 'number':
      default:
        return (value: number) => new Intl.NumberFormat('en-US').format(value)
    }
  }, [config.yAxis.format])

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background border border rounded-lg p-3 shadow-lg">
          <p className="font-medium text-foreground">{`${config.xAxis.label}: ${label}`}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {`${entry.name}: ${formatValue(entry.value)}`}
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  const renderChart = () => {
    const commonProps = {
      data,
      margin: { top: 5, right: 30, left: 20, bottom: 5 }
    }

    if (config.series.length === 1 && config.series[0].type === 'area') {
      return (
        <AreaChart {...commonProps}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
          <XAxis 
            dataKey="x" 
            className="text-muted-foreground text-xs"
            tickLine={false}
            axisLine={false}
          />
          <YAxis 
            className="text-muted-foreground text-xs"
            tickFormatter={formatValue}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          {config.showLegend && <Legend />}
          {config.series.map((series, index) => (
            <Area
              key={index}
              type="monotone"
              dataKey="y"
              stroke={series.color || `hsl(${index * 137.5 % 360}, 70%, 50%)`}
              fill={series.color || `hsl(${index * 137.5 % 360}, 70%, 50%)`}
              fillOpacity={0.3}
              strokeWidth={2}
            />
          ))}
        </AreaChart>
      )
    }

    if (config.series.some(s => s.type === 'bar')) {
      return (
        <BarChart {...commonProps}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
          <XAxis 
            dataKey="x" 
            className="text-muted-foreground text-xs"
            tickLine={false}
            axisLine={false}
          />
          <YAxis 
            className="text-muted-foreground text-xs"
            tickFormatter={formatValue}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          {config.showLegend && <Legend />}
          {config.series.map((series, index) => (
            <Bar
              key={index}
              dataKey="y"
              fill={series.color || `hsl(${index * 137.5 % 360}, 70%, 50%)`}
            />
          ))}
        </BarChart>
      )
    }

    // Default to line chart
    return (
      <LineChart {...commonProps}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
        <XAxis 
          dataKey="x" 
          className="text-muted-foreground text-xs"
          tickLine={false}
          axisLine={false}
        />
        <YAxis 
          className="text-muted-foreground text-xs"
          tickFormatter={formatValue}
          tickLine={false}
          axisLine={false}
        />
        <Tooltip content={<CustomTooltip />} />
        {config.showLegend && <Legend />}
        {config.series.map((series, index) => (
          <Line
            key={index}
            type="monotone"
            dataKey="y"
            stroke={series.color || `hsl(${index * 137.5 % 360}, 70%, 50%)`}
            strokeWidth={2}
            dot={{ fill: series.color || `hsl(${index * 137.5 % 360}, 70%, 50%)`, strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, stroke: series.color || `hsl(${index * 137.5 % 360}, 70%, 50%)`, strokeWidth: 2 }}
          />
        ))}
      </LineChart>
    )
  }

  return (
    <div className={cn("w-full", className)}>
      {config.title && (
        <h3 className="text-lg font-semibold text-foreground mb-4 text-center">
          {config.title}
        </h3>
      )}
      <RechartsResponsiveContainer width="100%" height={height}>
        {renderChart()}
      </RechartsResponsiveContainer>
    </div>
  )
}

interface NetWorthProjectionChartProps {
  data: Array<{
    year: number
    netWorth: number
    portfolioValue: number
    age: number
  }>
  className?: string
}

export function NetWorthProjectionChart({ data, className }: NetWorthProjectionChartProps) {
  const chartData = data.map(item => ({
    x: item.year,
    y: item.netWorth,
    portfolio: item.portfolioValue,
    age: item.age
  }))

  const config: ChartConfig = {
    title: "Net Worth Projection",
    xAxis: {
      label: "Year",
      type: "category"
    },
    yAxis: {
      label: "Value",
      format: "currency"
    },
    series: [
      {
        name: "Net Worth",
        data: chartData.map(d => ({ x: d.x, y: d.y })),
        color: "hsl(142, 76%, 36%)",
        type: "area"
      }
    ],
    interactive: true,
    showLegend: true
  }

  return (
    <ResponsiveChart 
      config={config} 
      data={chartData}
      height={400}
      className={className}
    />
  )
}

interface MonteCarloDistributionProps {
  data: Array<{
    value: number
    probability: number
  }>
  className?: string
}

export function MonteCarloDistribution({ data, className }: MonteCarloDistributionProps) {
  const chartData = data.map(item => ({
    x: formatCurrency(item.value),
    y: item.probability
  }))

  const config: ChartConfig = {
    title: "Monte Carlo Outcome Distribution",
    xAxis: {
      label: "Final Net Worth",
      type: "category"
    },
    yAxis: {
      label: "Probability",
      format: "percentage"
    },
    series: [
      {
        name: "Probability",
        data: chartData,
        color: "hsl(262, 83%, 58%)",
        type: "bar"
      }
    ],
    interactive: true,
    showLegend: false
  }

  return (
    <ResponsiveChart 
      config={config} 
      data={chartData} 
      className={className}
    />
  )
}