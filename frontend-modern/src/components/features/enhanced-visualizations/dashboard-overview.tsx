'use client'

import { useState, useMemo } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  PieChart, 
  Target, 
  ArrowUpRight,
  ArrowDownRight,
  Zap,
  Eye,
  Download
} from 'lucide-react'
import { 
  ComposedChart,
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  Area,
  AreaChart,
  RadialBarChart,
  RadialBar,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  TreeMap,
  Sankey
} from 'recharts'
import { formatCurrency } from '@/lib/utils'

interface EnhancedVisualizationProps {
  scenarios: Array<{
    id: string
    name: string
    results: {
      final_net_worth: number
      annual_growth_rate: number
      total_expenses: number
      retirement_readiness: boolean
      yearly_projections: Array<{
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
      spouse1Status: string
      spouse2Status: string
    }
  }>
  className?: string
}

export function EnhancedVisualizationDashboard({ scenarios, className = '' }: EnhancedVisualizationProps) {
  const [activeView, setActiveView] = useState<'overview' | 'comparison' | 'trends' | 'impact'>('overview')
  const [selectedScenarios, setSelectedScenarios] = useState<string[]>(scenarios.slice(0, 3).map(s => s.id))

  // Enhanced data processing
  const dashboardData = useMemo(() => {
    if (!scenarios.length) return null

    const currentYear = new Date().getFullYear()
    const allProjections = scenarios.flatMap(s => 
      s.results.yearly_projections?.map(p => ({
        ...p,
        scenario: s.name,
        scenario_id: s.id,
        roi: (p.net_worth - (s.results.yearly_projections?.[0]?.net_worth || 0)) / (s.results.yearly_projections?.[0]?.net_worth || 1)
      })) || []
    )

    // Performance metrics
    const bestScenario = scenarios.reduce((best, current) => 
      current.results.final_net_worth > best.results.final_net_worth ? current : best
    )
    
    const worstScenario = scenarios.reduce((worst, current) => 
      current.results.final_net_worth < worst.results.final_net_worth ? current : worst
    )

    // Risk analysis
    const riskData = scenarios.map(scenario => ({
      name: scenario.name,
      risk: Math.abs(scenario.results.annual_growth_rate - 0.07) * 100, // Risk relative to 7% baseline
      return: scenario.results.annual_growth_rate * 100,
      netWorth: scenario.results.final_net_worth,
      expenses: scenario.results.total_expenses
    }))

    // Trend analysis
    const trendData = Array.from({ length: 8 }, (_, i) => {
      const year = currentYear + i
      const yearData = { year }
      
      scenarios.forEach(scenario => {
        const projection = scenario.results.yearly_projections?.find(p => p.year === year)
        if (projection) {
          yearData[scenario.name] = projection.net_worth
        }
      })
      
      return yearData
    })

    // Financial health scoring
    const healthScores = scenarios.map(scenario => {
      const finalWorth = scenario.results.final_net_worth
      const growthRate = scenario.results.annual_growth_rate
      const expenseRatio = scenario.results.total_expenses / finalWorth
      
      const wealthScore = Math.min(100, (finalWorth / 5000000) * 100)
      const growthScore = Math.min(100, (growthRate / 0.12) * 100)
      const efficiencyScore = Math.max(0, 100 - (expenseRatio * 100))
      
      const overallScore = (wealthScore + growthScore + efficiencyScore) / 3
      
      return {
        name: scenario.name,
        overall: overallScore,
        wealth: wealthScore,
        growth: growthScore,
        efficiency: efficiencyScore,
        retirement: scenario.results.retirement_readiness ? 100 : 50
      }
    })

    return {
      allProjections,
      bestScenario,
      worstScenario,
      riskData,
      trendData,
      healthScores,
      totalScenarios: scenarios.length,
      avgGrowthRate: scenarios.reduce((sum, s) => sum + s.results.annual_growth_rate, 0) / scenarios.length
    }
  }, [scenarios])

  if (!dashboardData) {
    return <div>Loading enhanced visualizations...</div>
  }

  const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00ff88', '#ff8042']

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background border rounded-lg p-3 shadow-lg">
          <p className="font-medium">{`${label}`}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }}>
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
      {/* Header with Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Best Scenario</p>
                <p className="text-2xl font-bold text-green-600">
                  {formatCurrency(dashboardData.bestScenario.results.final_net_worth)}
                </p>
                <p className="text-xs text-muted-foreground">{dashboardData.bestScenario.name}</p>
              </div>
              <TrendingUp className="h-4 w-4 text-green-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Average Growth</p>
                <p className="text-2xl font-bold text-blue-600">
                  {(dashboardData.avgGrowthRate * 100).toFixed(1)}%
                </p>
                <p className="text-xs text-muted-foreground">Annual return</p>
              </div>
              <BarChart3 className="h-4 w-4 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Scenarios Analyzed</p>
                <p className="text-2xl font-bold text-purple-600">
                  {dashboardData.totalScenarios}
                </p>
                <p className="text-xs text-muted-foreground">Life planning options</p>
              </div>
              <Target className="h-4 w-4 text-purple-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Potential Upside</p>
                <p className="text-2xl font-bold text-orange-600">
                  {formatCurrency(
                    dashboardData.bestScenario.results.final_net_worth - 
                    dashboardData.worstScenario.results.final_net_worth
                  )}
                </p>
                <p className="text-xs text-muted-foreground">Best vs worst case</p>
              </div>
              <Zap className="h-4 w-4 text-orange-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Visualization Tabs */}
      <Tabs value={activeView} onValueChange={setActiveView as any} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Portfolio Overview</TabsTrigger>
          <TabsTrigger value="comparison">Scenario Comparison</TabsTrigger>
          <TabsTrigger value="trends">Trend Analysis</TabsTrigger>
          <TabsTrigger value="impact">Impact Analysis</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Net Worth Progression */}
            <Card>
              <CardHeader>
                <CardTitle>Net Worth Progression</CardTitle>
                <CardDescription>Portfolio growth across all scenarios</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={dashboardData.trendData}>
                    <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                    <XAxis dataKey="year" className="text-xs" />
                    <YAxis 
                      tickFormatter={(value) => `$${(value / 1000000).toFixed(1)}M`}
                      className="text-xs"
                    />
                    <Tooltip content={<CustomTooltip />} />
                    {scenarios.map((scenario, index) => (
                      <Line 
                        key={scenario.id}
                        type="monotone" 
                        dataKey={scenario.name} 
                        stroke={colors[index % colors.length]}
                        strokeWidth={2}
                        dot={{ fill: colors[index % colors.length], strokeWidth: 2, r: 3 }}
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Risk vs Return Analysis */}
            <Card>
              <CardHeader>
                <CardTitle>Risk vs Return Matrix</CardTitle>
                <CardDescription>Risk-adjusted return analysis</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <ComposedChart data={dashboardData.riskData}>
                    <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                    <XAxis 
                      dataKey="risk" 
                      label={{ value: 'Risk Level', position: 'insideBottom', offset: -5 }}
                      className="text-xs"
                    />
                    <YAxis 
                      label={{ value: 'Annual Return (%)', angle: -90, position: 'insideLeft' }}
                      className="text-xs"
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="return" fill="#8884d8" opacity={0.6} />
                    <Line 
                      type="monotone" 
                      dataKey="return" 
                      stroke="#ff7300" 
                      strokeWidth={2}
                      dot={{ fill: '#ff7300', strokeWidth: 2, r: 4 }}
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Financial Health Scoring */}
          <Card>
            <CardHeader>
              <CardTitle>Financial Health Scoring</CardTitle>
              <CardDescription>Multi-dimensional analysis of scenario performance</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <RadialBarChart cx="50%" cy="50%" innerRadius="10%" outerRadius="80%" data={dashboardData.healthScores}>
                  <RadialBar
                    minAngle={15}
                    label={{ position: 'insideStart', fill: '#fff' }}
                    background
                    clockWise
                    dataKey="overall"
                    fill="#8884d8"
                  />
                  <Tooltip content={<CustomTooltip />} />
                </RadialBarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="comparison" className="space-y-6">
          {/* Scenario selector */}
          <Card>
            <CardHeader>
              <CardTitle>Select Scenarios to Compare</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {scenarios.map(scenario => (
                  <Badge
                    key={scenario.id}
                    variant={selectedScenarios.includes(scenario.id) ? "default" : "outline"}
                    className="cursor-pointer"
                    onClick={() => {
                      setSelectedScenarios(prev => 
                        prev.includes(scenario.id)
                          ? prev.filter(id => id !== scenario.id)
                          : [...prev, scenario.id]
                      )
                    }}
                  >
                    {scenario.name}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Side-by-side comparison */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Final Net Worth Comparison</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={scenarios.filter(s => selectedScenarios.includes(s.id))}>
                    <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                    <XAxis dataKey="name" className="text-xs" angle={-45} textAnchor="end" height={60} />
                    <YAxis 
                      tickFormatter={(value) => `$${(value / 1000000).toFixed(1)}M`}
                      className="text-xs"
                    />
                    <Tooltip 
                      formatter={(value) => [formatCurrency(Number(value)), 'Final Net Worth']}
                    />
                    <Bar dataKey="results.final_net_worth" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Growth Rate Comparison</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={scenarios.filter(s => selectedScenarios.includes(s.id))}>
                    <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                    <XAxis dataKey="name" className="text-xs" angle={-45} textAnchor="end" height={60} />
                    <YAxis 
                      tickFormatter={(value) => `${(value * 100).toFixed(1)}%`}
                      className="text-xs"
                    />
                    <Tooltip 
                      formatter={(value) => [`${(Number(value) * 100).toFixed(1)}%`, 'Annual Growth']}
                    />
                    <Bar dataKey="results.annual_growth_rate" fill="#82ca9d" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="trends" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Multi-Scenario Trend Analysis</CardTitle>
              <CardDescription>Comprehensive view of all scenario trajectories</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={500}>
                <AreaChart data={dashboardData.trendData}>
                  <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                  <XAxis dataKey="year" className="text-xs" />
                  <YAxis 
                    tickFormatter={(value) => `$${(value / 1000000).toFixed(1)}M`}
                    className="text-xs"
                  />
                  <Tooltip content={<CustomTooltip />} />
                  {scenarios.map((scenario, index) => (
                    <Area
                      key={scenario.id}
                      type="monotone"
                      dataKey={scenario.name}
                      stackId="1"
                      stroke={colors[index % colors.length]}
                      fill={colors[index % colors.length]}
                      fillOpacity={0.6}
                    />
                  ))}
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="impact" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Decision Impact Matrix</CardTitle>
                <CardDescription>How different choices affect outcomes</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {['housing', 'schoolType', 'spouse1Status'].map(param => {
                    const impacts = scenarios.reduce((acc, scenario) => {
                      const key = scenario.parameters[param as keyof typeof scenario.parameters]
                      if (!acc[key]) acc[key] = []
                      acc[key].push(scenario.results.final_net_worth)
                      return acc
                    }, {} as Record<string, number[]>)

                    const impactData = Object.entries(impacts).map(([key, values]) => ({
                      option: key,
                      avgImpact: values.reduce((sum, val) => sum + val, 0) / values.length,
                      count: values.length
                    }))

                    return (
                      <div key={param} className="space-y-2">
                        <h4 className="font-medium capitalize">{param} Impact</h4>
                        <ResponsiveContainer width="100%" height={100}>
                          <BarChart data={impactData}>
                            <XAxis dataKey="option" className="text-xs" />
                            <YAxis tickFormatter={(value) => `$${(value / 1000000).toFixed(1)}M`} className="text-xs" />
                            <Tooltip 
                              formatter={(value) => [formatCurrency(Number(value)), 'Avg Impact']}
                            />
                            <Bar dataKey="avgImpact" fill="#8884d8" />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Expense Efficiency Analysis</CardTitle>
                <CardDescription>Cost vs benefit of different scenarios</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <ComposedChart 
                    data={scenarios.map(s => ({
                      name: s.name,
                      expenses: s.results.total_expenses,
                      netWorth: s.results.final_net_worth,
                      efficiency: (s.results.final_net_worth / s.results.total_expenses) * 100
                    }))}
                  >
                    <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                    <XAxis dataKey="name" className="text-xs" angle={-45} textAnchor="end" height={60} />
                    <YAxis 
                      yAxisId="left"
                      tickFormatter={(value) => `$${(value / 1000000).toFixed(1)}M`}
                      className="text-xs"
                    />
                    <YAxis 
                      yAxisId="right" 
                      orientation="right"
                      tickFormatter={(value) => `${value.toFixed(0)}x`}
                      className="text-xs"
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar yAxisId="left" dataKey="expenses" fill="#ff7300" name="Total Expenses" />
                    <Line 
                      yAxisId="right"
                      type="monotone" 
                      dataKey="efficiency" 
                      stroke="#8884d8" 
                      strokeWidth={3}
                      name="Efficiency Ratio"
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Export Controls */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium">Export Analysis</h3>
              <p className="text-sm text-muted-foreground">
                Download your enhanced visualization analysis
              </p>
            </div>
            <div className="flex space-x-2">
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                PDF Report
              </Button>
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Excel Data
              </Button>
              <Button variant="outline" size="sm">
                <Eye className="h-4 w-4 mr-2" />
                Full Screen
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}