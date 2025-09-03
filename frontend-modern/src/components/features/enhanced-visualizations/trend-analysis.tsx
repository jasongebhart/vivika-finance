'use client'

import { useState, useMemo } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Slider } from '@/components/ui/slider'
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  BarChart3, 
  LineChart as LineChartIcon,
  AlertTriangle,
  CheckCircle
} from 'lucide-react'
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area,
  ComposedChart,
  Bar,
  Scatter,
  ScatterChart,
  ReferenceLine,
  ReferenceArea
} from 'recharts'
import { formatCurrency } from '@/lib/utils'

interface TrendAnalysisProps {
  data: {
    scenarios: Array<{
      id: string
      name: string
      results: {
        final_net_worth: number
        annual_growth_rate: number
        yearly_projections?: Array<{
          year: number
          age: number
          net_worth: number
          income: number
          expenses: number
          net_cash_flow: number
        }>
      }
      parameters: {
        location: string
        housing: string
        schoolType: string
      }
    }>
  }
  className?: string
}

interface TrendPoint {
  year: number
  value: number
  scenario: string
  volatility: number
  momentum: number
  risk_score: number
}

export function TrendAnalysisVisualization({ data, className = '' }: TrendAnalysisProps) {
  const [selectedTimeframe, setSelectedTimeframe] = useState([1, 8]) // Default 1-8 years
  const [analysisType, setAnalysisType] = useState<'growth' | 'momentum' | 'volatility' | 'correlation'>('growth')
  const [showConfidenceIntervals, setShowConfidenceIntervals] = useState(true)

  // Advanced trend calculations
  const trendAnalysis = useMemo(() => {
    if (!data.scenarios.length) return null

    const currentYear = new Date().getFullYear()
    const timeRange = Array.from(
      { length: selectedTimeframe[1] - selectedTimeframe[0] + 1 }, 
      (_, i) => currentYear + selectedTimeframe[0] - 1 + i
    )

    // Calculate trend metrics for each scenario
    const scenarioTrends = data.scenarios.map(scenario => {
      const projections = scenario.results.yearly_projections || []
      const relevantProjections = projections.filter(p => 
        p.year >= timeRange[0] && p.year <= timeRange[timeRange.length - 1]
      )

      if (relevantProjections.length < 2) return null

      // Growth rate analysis
      const growthRates = relevantProjections.slice(1).map((proj, i) => ({
        year: proj.year,
        rate: (proj.net_worth - relevantProjections[i].net_worth) / relevantProjections[i].net_worth
      }))

      // Momentum calculation (acceleration of growth)
      const momentum = growthRates.slice(1).map((rate, i) => ({
        year: rate.year,
        momentum: rate.rate - growthRates[i].rate
      }))

      // Volatility (standard deviation of growth rates)
      const avgGrowthRate = growthRates.reduce((sum, r) => sum + r.rate, 0) / growthRates.length
      const volatility = Math.sqrt(
        growthRates.reduce((sum, r) => sum + Math.pow(r.rate - avgGrowthRate, 2), 0) / growthRates.length
      )

      // Risk score based on volatility and downside potential
      const downsideYears = growthRates.filter(r => r.rate < 0).length
      const riskScore = (volatility * 100) + (downsideYears / growthRates.length * 50)

      return {
        scenario: scenario.name,
        scenarioId: scenario.id,
        projections: relevantProjections,
        growthRates,
        momentum,
        volatility,
        riskScore,
        avgGrowthRate,
        finalValue: relevantProjections[relevantProjections.length - 1]?.net_worth || 0,
        totalReturn: ((relevantProjections[relevantProjections.length - 1]?.net_worth || 0) / 
                     (relevantProjections[0]?.net_worth || 1) - 1) * 100
      }
    }).filter(Boolean)

    // Correlation analysis between scenarios
    const correlationMatrix = scenarioTrends.map(scenario1 => 
      scenarioTrends.map(scenario2 => {
        if (scenario1.scenarioId === scenario2.scenarioId) return 1

        const values1 = scenario1.projections.map(p => p.net_worth)
        const values2 = scenario2.projections.map(p => p.net_worth)
        
        if (values1.length !== values2.length) return 0

        const mean1 = values1.reduce((sum, v) => sum + v, 0) / values1.length
        const mean2 = values2.reduce((sum, v) => sum + v, 0) / values2.length

        const numerator = values1.reduce((sum, v1, i) => 
          sum + (v1 - mean1) * (values2[i] - mean2), 0
        )
        
        const denominator = Math.sqrt(
          values1.reduce((sum, v) => sum + Math.pow(v - mean1, 2), 0) *
          values2.reduce((sum, v) => sum + Math.pow(v - mean2, 2), 0)
        )

        return denominator === 0 ? 0 : numerator / denominator
      })
    )

    // Combined timeline data
    const timelineData = timeRange.map(year => {
      const yearData: any = { year }
      
      scenarioTrends.forEach(trend => {
        const projection = trend.projections.find(p => p.year === year)
        if (projection) {
          yearData[trend.scenario] = projection.net_worth
          yearData[`${trend.scenario}_income`] = projection.income
          yearData[`${trend.scenario}_expenses`] = projection.expenses
          yearData[`${trend.scenario}_flow`] = projection.net_cash_flow
        }
      })

      return yearData
    })

    // Confidence intervals (simplified Monte Carlo simulation)
    const confidenceData = timeRange.map(year => {
      const yearValues = scenarioTrends.map(trend => {
        const projection = trend.projections.find(p => p.year === year)
        return projection ? projection.net_worth : 0
      }).filter(v => v > 0)

      if (yearValues.length === 0) return { year, lower: 0, upper: 0, median: 0 }

      yearValues.sort((a, b) => a - b)
      const lower = yearValues[Math.floor(yearValues.length * 0.25)]
      const upper = yearValues[Math.floor(yearValues.length * 0.75)]
      const median = yearValues[Math.floor(yearValues.length * 0.5)]

      return { year, lower, upper, median }
    })

    return {
      scenarioTrends,
      correlationMatrix,
      timelineData,
      confidenceData,
      bestPerformer: scenarioTrends.reduce((best, current) => 
        current.totalReturn > best.totalReturn ? current : best
      ),
      worstPerformer: scenarioTrends.reduce((worst, current) => 
        current.totalReturn < worst.totalReturn ? current : worst
      ),
      leastVolatile: scenarioTrends.reduce((least, current) => 
        current.volatility < least.volatility ? current : least
      )
    }
  }, [data.scenarios, selectedTimeframe])

  if (!trendAnalysis) {
    return <div>Loading trend analysis...</div>
  }

  const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00ff88', '#ff8042']

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background border rounded-lg p-3 shadow-lg max-w-xs">
          <p className="font-medium mb-2">{`Year: ${label}`}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }} className="text-sm">
              {`${entry.dataKey}: ${
                typeof entry.value === 'number' && entry.value > 1000 
                  ? formatCurrency(entry.value)
                  : entry.value
              }`}
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Analysis Controls */}
      <Card>
        <CardHeader>
          <CardTitle>Trend Analysis Configuration</CardTitle>
          <CardDescription>
            Customize your analysis timeframe and metrics
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <label className="text-sm font-medium">Analysis Timeframe (Years)</label>
            <Slider
              value={selectedTimeframe}
              onValueChange={setSelectedTimeframe}
              max={10}
              min={1}
              step={1}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Year {selectedTimeframe[0]}</span>
              <span>Year {selectedTimeframe[1]}</span>
            </div>
          </div>

          <div className="flex space-x-2">
            {[
              { id: 'growth', label: 'Growth Analysis', icon: TrendingUp },
              { id: 'momentum', label: 'Momentum', icon: Activity },
              { id: 'volatility', label: 'Risk Analysis', icon: AlertTriangle },
              { id: 'correlation', label: 'Correlation', icon: BarChart3 }
            ].map(({ id, label, icon: Icon }) => (
              <Button
                key={id}
                variant={analysisType === id ? 'default' : 'outline'}
                size="sm"
                onClick={() => setAnalysisType(id as any)}
              >
                <Icon className="h-4 w-4 mr-1" />
                {label}
              </Button>
            ))}
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="confidence"
              checked={showConfidenceIntervals}
              onChange={(e) => setShowConfidenceIntervals(e.target.checked)}
              className="rounded border-gray-300"
            />
            <label htmlFor="confidence" className="text-sm">
              Show Confidence Intervals
            </label>
          </div>
        </CardContent>
      </Card>

      {/* Key Insights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Best Performer</p>
                <p className="text-xl font-bold text-green-600">
                  {trendAnalysis.bestPerformer.scenario}
                </p>
                <p className="text-sm text-green-600">
                  +{trendAnalysis.bestPerformer.totalReturn.toFixed(1)}% total return
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Least Volatile</p>
                <p className="text-xl font-bold text-blue-600">
                  {trendAnalysis.leastVolatile.scenario}
                </p>
                <p className="text-sm text-blue-600">
                  {(trendAnalysis.leastVolatile.volatility * 100).toFixed(1)}% volatility
                </p>
              </div>
              <CheckCircle className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Highest Risk</p>
                <p className="text-xl font-bold text-red-600">
                  {trendAnalysis.worstPerformer.scenario}
                </p>
                <p className="text-sm text-red-600">
                  {trendAnalysis.worstPerformer.totalReturn.toFixed(1)}% total return
                </p>
              </div>
              <TrendingDown className="h-8 w-8 text-red-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Trend Visualization */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <LineChartIcon className="h-5 w-5 mr-2" />
            {analysisType === 'growth' && 'Portfolio Growth Trajectories'}
            {analysisType === 'momentum' && 'Growth Momentum Analysis'}
            {analysisType === 'volatility' && 'Risk and Volatility Analysis'}
            {analysisType === 'correlation' && 'Scenario Correlation Matrix'}
          </CardTitle>
          <CardDescription>
            Advanced trend analysis across selected timeframe
          </CardDescription>
        </CardHeader>
        <CardContent>
          {analysisType === 'growth' && (
            <ResponsiveContainer width="100%" height={500}>
              <ComposedChart data={trendAnalysis.timelineData}>
                <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                <XAxis dataKey="year" className="text-xs" />
                <YAxis 
                  tickFormatter={(value) => `$${(value / 1000000).toFixed(1)}M`}
                  className="text-xs"
                />
                <Tooltip content={<CustomTooltip />} />
                
                {/* Confidence intervals */}
                {showConfidenceIntervals && (
                  <Area
                    data={trendAnalysis.confidenceData}
                    type="monotone"
                    dataKey="upper"
                    stroke="none"
                    fill="#8884d8"
                    fillOpacity={0.2}
                    stackId="1"
                  />
                )}
                
                {/* Scenario lines */}
                {trendAnalysis.scenarioTrends.map((trend, index) => (
                  <Line
                    key={trend.scenarioId}
                    type="monotone"
                    dataKey={trend.scenario}
                    stroke={colors[index % colors.length]}
                    strokeWidth={3}
                    dot={{ fill: colors[index % colors.length], strokeWidth: 2, r: 4 }}
                  />
                ))}
                
                {/* Reference lines for key milestones */}
                <ReferenceLine 
                  y={5000000} 
                  stroke="#ff7300" 
                  strokeDasharray="5 5" 
                  label="$5M Target"
                />
              </ComposedChart>
            </ResponsiveContainer>
          )}

          {analysisType === 'momentum' && (
            <ResponsiveContainer width="100%" height={400}>
              <AreaChart data={trendAnalysis.timelineData}>
                <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                <XAxis dataKey="year" className="text-xs" />
                <YAxis className="text-xs" />
                <Tooltip content={<CustomTooltip />} />
                <ReferenceLine y={0} stroke="#666" strokeDasharray="2 2" />
                {trendAnalysis.scenarioTrends.map((trend, index) => (
                  <Area
                    key={trend.scenarioId}
                    type="monotone"
                    dataKey={`${trend.scenario}_flow`}
                    stackId="1"
                    stroke={colors[index % colors.length]}
                    fill={colors[index % colors.length]}
                    fillOpacity={0.6}
                  />
                ))}
              </AreaChart>
            </ResponsiveContainer>
          )}

          {analysisType === 'volatility' && (
            <ResponsiveContainer width="100%" height={400}>
              <ScatterChart>
                <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                <XAxis 
                  type="number"
                  dataKey="volatility"
                  domain={['dataMin', 'dataMax']}
                  tickFormatter={(value) => `${(value * 100).toFixed(1)}%`}
                  label={{ value: 'Volatility', position: 'insideBottom', offset: -5 }}
                  className="text-xs"
                />
                <YAxis 
                  type="number"
                  dataKey="totalReturn"
                  domain={['dataMin', 'dataMax']}
                  tickFormatter={(value) => `${value.toFixed(1)}%`}
                  label={{ value: 'Total Return', angle: -90, position: 'insideLeft' }}
                  className="text-xs"
                />
                <Tooltip 
                  cursor={{ strokeDasharray: '3 3' }}
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload
                      return (
                        <div className="bg-background border rounded-lg p-3 shadow-lg">
                          <p className="font-medium">{data.scenario}</p>
                          <p className="text-sm">Return: {data.totalReturn.toFixed(1)}%</p>
                          <p className="text-sm">Volatility: {(data.volatility * 100).toFixed(1)}%</p>
                          <p className="text-sm">Risk Score: {data.riskScore.toFixed(1)}</p>
                        </div>
                      )
                    }
                    return null
                  }}
                />
                <Scatter
                  data={trendAnalysis.scenarioTrends}
                  fill="#8884d8"
                />
              </ScatterChart>
            </ResponsiveContainer>
          )}

          {analysisType === 'correlation' && (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Correlation coefficients between scenario performance (-1 to +1)
              </p>
              <div className="grid gap-2" style={{ 
                gridTemplateColumns: `repeat(${trendAnalysis.scenarioTrends.length + 1}, 1fr)` 
              }}>
                <div></div>
                {trendAnalysis.scenarioTrends.map(trend => (
                  <div key={trend.scenarioId} className="text-xs font-medium text-center p-2">
                    {trend.scenario.substring(0, 8)}...
                  </div>
                ))}
                {trendAnalysis.correlationMatrix.map((row, i) => (
                  <>
                    <div key={`label-${i}`} className="text-xs font-medium p-2">
                      {trendAnalysis.scenarioTrends[i].scenario.substring(0, 8)}...
                    </div>
                    {row.map((corr, j) => (
                      <div 
                        key={`cell-${i}-${j}`}
                        className="text-xs text-center p-2 rounded"
                        style={{
                          backgroundColor: `hsl(${corr > 0 ? '120' : '0'}, ${Math.abs(corr) * 100}%, 90%)`
                        }}
                      >
                        {corr.toFixed(2)}
                      </div>
                    ))}
                  </>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Detailed Analysis Table */}
      <Card>
        <CardHeader>
          <CardTitle>Detailed Trend Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Scenario</th>
                  <th className="text-right p-2">Total Return</th>
                  <th className="text-right p-2">Avg Growth Rate</th>
                  <th className="text-right p-2">Volatility</th>
                  <th className="text-right p-2">Risk Score</th>
                  <th className="text-right p-2">Final Value</th>
                </tr>
              </thead>
              <tbody>
                {trendAnalysis.scenarioTrends.map((trend, index) => (
                  <tr key={trend.scenarioId} className="border-b">
                    <td className="p-2">
                      <div className="flex items-center">
                        <div 
                          className="w-3 h-3 rounded-full mr-2" 
                          style={{ backgroundColor: colors[index % colors.length] }}
                        />
                        {trend.scenario}
                      </div>
                    </td>
                    <td className="text-right p-2">
                      <Badge variant={trend.totalReturn > 0 ? "default" : "destructive"}>
                        {trend.totalReturn > 0 ? '+' : ''}{trend.totalReturn.toFixed(1)}%
                      </Badge>
                    </td>
                    <td className="text-right p-2">{(trend.avgGrowthRate * 100).toFixed(1)}%</td>
                    <td className="text-right p-2">{(trend.volatility * 100).toFixed(1)}%</td>
                    <td className="text-right p-2">
                      <Badge variant={trend.riskScore < 30 ? "default" : trend.riskScore < 60 ? "secondary" : "destructive"}>
                        {trend.riskScore.toFixed(1)}
                      </Badge>
                    </td>
                    <td className="text-right p-2">{formatCurrency(trend.finalValue)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}