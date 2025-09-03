'use client'

import { useMemo } from 'react'
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  ScatterChart,
  Scatter,
  Cell
} from 'recharts'
import { formatCurrency, formatPercentage, cn } from '@/lib/utils'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useYearRangeStore } from '@/stores/app-store'
import type { MonteCarloResults } from '@/types'

interface MonteCarloChartProps {
  data: MonteCarloResults
  className?: string
}

export function MonteCarloDistributionChart({ data, className }: MonteCarloChartProps) {
  const distributionData = useMemo(() => {
    if (!data.percentiles) return []
    
    return Object.entries(data.percentiles).map(([percentile, values]) => ({
      percentile: parseInt(percentile),
      value: values[values.length - 1], // Final value
      label: `${percentile}th percentile`
    })).sort((a, b) => a.percentile - b.percentile)
  }, [data.percentiles])

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background border border rounded-lg p-3 shadow-lg">
          <p className="font-medium text-foreground">{`${label}th Percentile`}</p>
          <p className="text-sm text-primary">
            {`Final Value: ${formatCurrency(payload[0].value)}`}
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Monte Carlo Outcome Distribution</CardTitle>
        <CardDescription>
          Final portfolio values across {data.simulations.length} simulations
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={distributionData}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
            <XAxis 
              dataKey="percentile" 
              className="text-muted-foreground text-xs"
              tickLine={false}
              axisLine={false}
              label={{ value: 'Percentile', position: 'insideBottom', offset: -5 }}
            />
            <YAxis 
              className="text-muted-foreground text-xs"
              tickFormatter={(value) => formatCurrency(value, 'USD')}
              tickLine={false}
              axisLine={false}
              label={{ value: 'Final Value', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="value"
              stroke="hsl(262, 83%, 58%)"
              fill="hsl(262, 83%, 58%)"
              fillOpacity={0.3}
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
        
        {/* Summary Statistics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {formatPercentage(data.success_probability)}
            </div>
            <div className="text-sm text-muted-foreground">Success Rate</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-foreground">
              {formatCurrency(data.median_final_value)}
            </div>
            <div className="text-sm text-muted-foreground">Median Outcome</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">
              {formatCurrency(data.worst_case_value)}
            </div>
            <div className="text-sm text-muted-foreground">Worst Case (5%)</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {formatCurrency(data.best_case_value)}
            </div>
            <div className="text-sm text-muted-foreground">Best Case (95%)</div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

interface PortfolioPathsChartProps {
  data: MonteCarloResults
  maxPaths?: number
  className?: string
}

export function PortfolioPathsChart({ data, maxPaths = 100, className }: PortfolioPathsChartProps) {
  const { yearRange, startYear, isYearInRange } = useYearRangeStore()
  
  const pathsData = useMemo(() => {
    if (!data.simulations.length) return []
    
    const selectedSims = data.simulations
      .slice(0, maxPaths)
      .sort((a, b) => b.final_value - a.final_value)
    
    // Use the year range from global state
    const years = Array.from({ length: Math.min(yearRange, data.simulations[0].yearly_values.length) }, (_, i) => 
      startYear + i
    )
    
    return years.map((year, yearIndex) => {
      const yearData: any = { year }
      
      selectedSims.forEach((sim, simIndex) => {
        yearData[`sim_${simIndex}`] = sim.yearly_values[yearIndex]
      })
      
      // Add percentile bands
      const yearValues = data.simulations.map(sim => sim.yearly_values[yearIndex]).sort((a, b) => a - b)
      yearData.p10 = yearValues[Math.floor(yearValues.length * 0.1)]
      yearData.p25 = yearValues[Math.floor(yearValues.length * 0.25)]
      yearData.p50 = yearValues[Math.floor(yearValues.length * 0.5)]
      yearData.p75 = yearValues[Math.floor(yearValues.length * 0.75)]
      yearData.p90 = yearValues[Math.floor(yearValues.length * 0.9)]
      
      return yearData
    })
  }, [data.simulations, maxPaths, yearRange, startYear])

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const relevantPayload = payload.filter((p: any) => 
        p.dataKey.startsWith('p') && p.value != null
      )
      
      return (
        <div className="bg-background border border rounded-lg p-3 shadow-lg">
          <p className="font-medium text-foreground mb-2">{`Year: ${label}`}</p>
          {relevantPayload.map((entry: any, index: number) => (
            <p key={index} className="text-sm">
              <span style={{ color: entry.color }}>
                {entry.dataKey === 'p10' && '10th percentile: '}
                {entry.dataKey === 'p25' && '25th percentile: '}
                {entry.dataKey === 'p50' && 'Median: '}
                {entry.dataKey === 'p75' && '75th percentile: '}
                {entry.dataKey === 'p90' && '90th percentile: '}
                {formatCurrency(entry.value)}
              </span>
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Portfolio Evolution Paths</CardTitle>
        <CardDescription>
          Portfolio value trajectories with confidence intervals over {yearRange} years (showing {Math.min(maxPaths, data.simulations.length)} of {data.simulations.length} simulations)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={pathsData}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
            <XAxis 
              dataKey="year" 
              className="text-muted-foreground text-xs"
              tickLine={false}
              axisLine={false}
            />
            <YAxis 
              className="text-muted-foreground text-xs"
              tickFormatter={(value) => formatCurrency(value, 'USD')}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip content={<CustomTooltip />} />
            
            {/* Confidence interval bands */}
            <Area
              type="monotone"
              dataKey="p90"
              stroke="none"
              fill="hsl(221, 83%, 53%)"
              fillOpacity={0.1}
              stackId="1"
            />
            <Area
              type="monotone"
              dataKey="p75"
              stroke="none"
              fill="hsl(221, 83%, 53%)"
              fillOpacity={0.2}
              stackId="1"
            />
            <Area
              type="monotone"
              dataKey="p25"
              stroke="none"
              fill="hsl(221, 83%, 53%)"
              fillOpacity={0.3}
              stackId="1"
            />
            <Area
              type="monotone"
              dataKey="p10"
              stroke="none"
              fill="hsl(221, 83%, 53%)"
              fillOpacity={0.1}
              stackId="1"
            />
            
            {/* Median line */}
            <Line
              type="monotone"
              dataKey="p50"
              stroke="hsl(221, 83%, 53%)"
              strokeWidth={3}
              dot={false}
              name="Median"
            />
            
            {/* Individual simulation paths (faded) */}
            {Array.from({ length: Math.min(maxPaths, data.simulations.length) }, (_, i) => (
              <Line
                key={i}
                type="monotone"
                dataKey={`sim_${i}`}
                stroke="hsl(221, 83%, 53%)"
                strokeWidth={1}
                strokeOpacity={0.1}
                dot={false}
                connectNulls={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

interface SuccessProbabilityChartProps {
  data: MonteCarloResults
  targetAmount?: number
  className?: string
}

export function SuccessProbabilityChart({ data, targetAmount, className }: SuccessProbabilityChartProps) {
  const { yearRange, startYear } = useYearRangeStore()
  
  const successData = useMemo(() => {
    if (!data.simulations.length) return []
    
    // Use the year range from global state
    const years = Array.from({ length: Math.min(yearRange, data.simulations[0].yearly_values.length) }, (_, i) => 
      startYear + i
    )
    
    return years.map((year, yearIndex) => {
      const yearValues = data.simulations.map(sim => sim.yearly_values[yearIndex])
      const target = targetAmount || data.median_final_value * 0.8 // Default target
      const successCount = yearValues.filter(value => value >= target).length
      const successRate = successCount / yearValues.length
      
      return {
        year,
        successRate: successRate * 100,
        target,
        avgValue: yearValues.reduce((sum, val) => sum + val, 0) / yearValues.length
      }
    })
  }, [data.simulations, targetAmount, data.median_final_value, yearRange, startYear])

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background border border rounded-lg p-3 shadow-lg">
          <p className="font-medium text-foreground">{`Year: ${label}`}</p>
          <p className="text-sm text-green-600">
            {`Success Rate: ${payload[0].value.toFixed(1)}%`}
          </p>
          <p className="text-sm text-muted-foreground">
            {`Target: ${formatCurrency(payload[0].payload.target)}`}
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Success Probability Over Time</CardTitle>
        <CardDescription>
          Probability of meeting target value over {yearRange} years
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={successData}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
            <XAxis 
              dataKey="year" 
              className="text-muted-foreground text-xs"
              tickLine={false}
              axisLine={false}
            />
            <YAxis 
              className="text-muted-foreground text-xs"
              domain={[0, 100]}
              tickFormatter={(value) => `${value}%`}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="successRate"
              stroke="hsl(142, 76%, 36%)"
              fill="hsl(142, 76%, 36%)"
              fillOpacity={0.3}
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}