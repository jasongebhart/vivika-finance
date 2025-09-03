'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts'
import { formatCurrency } from '@/lib/utils'
import { ExpenseBreakdown } from '@/components/features/expense-breakdown/expense-breakdown'
import { WhatIfSliders } from '@/components/features/what-if-analysis/what-if-sliders'
import { RetirementFeasibility } from '@/components/features/retirement-analysis/retirement-feasibility'
import { TrendingUp, DollarSign, PieChart as PieChartIcon, BarChart3, Calculator, Sliders, Target } from 'lucide-react'

interface ScenarioResults {
  final_net_worth: number
  annual_growth_rate: number
  total_expenses: number
  retirement_readiness: boolean
  calculated_at: string
  yearly_projections?: Array<{
    year: number
    age: number
    net_worth: number
    income: number
    expenses: number
    net_cash_flow: number
  }>
}

interface ScenarioChartProps {
  scenarioName: string
  results: ScenarioResults
  location: string
  parameters: {
    housing: string
    schoolType: string
    spouse1Status: string
    spouse2Status: string
  }
  className?: string
}

export function ScenarioChart({ 
  scenarioName, 
  results, 
  location, 
  parameters, 
  className = '' 
}: ScenarioChartProps) {
  const [activeChart, setActiveChart] = useState<'projection' | 'cashflow' | 'breakdown' | 'expenses' | 'whatif' | 'retirement'>('projection')
  const [whatIfParams, setWhatIfParams] = useState<any>(null)
  const [isCalculatingWhatIf, setIsCalculatingWhatIf] = useState(false)

  // Sample data for visualization (in real app, this would come from results)
  const projectionData = results.yearly_projections || [
    { year: 2025, age: 52, net_worth: 4500000, income: 450000, expenses: 180000, net_cash_flow: 270000 },
    { year: 2026, age: 53, net_worth: 4850000, income: 465000, expenses: 185000, net_cash_flow: 280000 },
    { year: 2027, age: 54, net_worth: 5220000, income: 480000, expenses: 190000, net_cash_flow: 290000 },
    { year: 2028, age: 55, net_worth: 5610000, income: 495000, expenses: 195000, net_cash_flow: 300000 },
    { year: 2029, age: 56, net_worth: 6025000, income: 510000, expenses: 200000, net_cash_flow: 310000 }
  ]

  const expenseBreakdown = [
    { name: 'Housing', value: 60000, color: '#8884d8' },
    { name: 'Living', value: 45000, color: '#82ca9d' },
    { name: 'Education', value: 35000, color: '#ffc658' },
    { name: 'Transportation', value: 25000, color: '#ff7300' },
    { name: 'Insurance', value: 15000, color: '#00ff88' }
  ]

  const formatYearTick = (tickItem: any) => {
    return `'${tickItem.toString().slice(-2)}`
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background border rounded-lg p-3 shadow-lg">
          <p className="font-medium">{`Year ${label}`}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }}>
              {`${entry.dataKey === 'net_worth' ? 'Net Worth' : 
                 entry.dataKey === 'income' ? 'Income' : 
                 entry.dataKey === 'expenses' ? 'Expenses' : 
                 'Cash Flow'}: ${formatCurrency(entry.value)}`}
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Results Summary */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center">
                <TrendingUp className="h-5 w-5 mr-2" />
                {scenarioName}
              </CardTitle>
              <CardDescription>
                Financial projection results • {location}
              </CardDescription>
            </div>
            <div className="flex space-x-2">
              <Badge variant="outline">{parameters.housing}</Badge>
              <Badge variant="outline">{parameters.schoolType}</Badge>
              <Badge variant="outline">{parameters.spouse1Status}/{parameters.spouse2Status}</Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">
                {formatCurrency(results.final_net_worth)}
              </div>
              <div className="text-sm text-muted-foreground">Final Net Worth</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {(results.annual_growth_rate * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-muted-foreground">Annual Growth</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {formatCurrency(results.total_expenses)}
              </div>
              <div className="text-sm text-muted-foreground">Total Expenses</div>
            </div>
            <div className="text-center">
              <div className={`text-2xl font-bold ${results.retirement_readiness ? 'text-green-600' : 'text-red-600'}`}>
                {results.retirement_readiness ? '✓ Ready' : '⚠ Risk'}
              </div>
              <div className="text-sm text-muted-foreground">Retirement</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Chart Controls */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Financial Analysis</CardTitle>
            <div className="flex space-x-2">
              <Button
                variant={activeChart === 'projection' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setActiveChart('projection')}
              >
                <TrendingUp className="h-4 w-4 mr-1" />
                Projection
              </Button>
              <Button
                variant={activeChart === 'cashflow' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setActiveChart('cashflow')}
              >
                <BarChart3 className="h-4 w-4 mr-1" />
                Cash Flow
              </Button>
              <Button
                variant={activeChart === 'breakdown' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setActiveChart('breakdown')}
              >
                <PieChartIcon className="h-4 w-4 mr-1" />
                Summary
              </Button>
              <Button
                variant={activeChart === 'expenses' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setActiveChart('expenses')}
              >
                <Calculator className="h-4 w-4 mr-1" />
                Impact
              </Button>
              <Button
                variant={activeChart === 'whatif' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setActiveChart('whatif')}
              >
                <Sliders className="h-4 w-4 mr-1" />
                What-If
              </Button>
              <Button
                variant={activeChart === 'retirement' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setActiveChart('retirement')}
              >
                <Target className="h-4 w-4 mr-1" />
                Retirement
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {activeChart === 'expenses' ? (
            <ExpenseBreakdown 
              scenario={{
                name: scenarioName,
                location,
                housing: parameters.housing,
                schoolType: parameters.schoolType,
                spouse1Status: parameters.spouse1Status,
                spouse2Status: parameters.spouse2Status
              }}
            />
          ) : activeChart === 'whatif' ? (
            <WhatIfSliders
              initialScenario={{
                location,
                housing: parameters.housing,
                schoolType: parameters.schoolType,
                projectionYears: 8, // Default from results
                spouse1Status: parameters.spouse1Status,
                spouse2Status: parameters.spouse2Status
              }}
              onParameterChange={(params) => {
                setWhatIfParams(params)
                setIsCalculatingWhatIf(true)
                // Here you would normally call an API to recalculate
                setTimeout(() => setIsCalculatingWhatIf(false), 2000)
              }}
              isCalculating={isCalculatingWhatIf}
            />
          ) : activeChart === 'retirement' ? (
            <RetirementFeasibility
              scenarioName={scenarioName}
              results={results}
              parameters={parameters}
            />
          ) : (
          <div className="h-80">
            {activeChart === 'projection' && (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={projectionData}>
                  <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                  <XAxis 
                    dataKey="year" 
                    tickFormatter={formatYearTick}
                    className="text-xs"
                  />
                  <YAxis 
                    tickFormatter={(value) => `$${(value / 1000000).toFixed(1)}M`}
                    className="text-xs"
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Line 
                    type="monotone" 
                    dataKey="net_worth" 
                    stroke="#8884d8" 
                    strokeWidth={3}
                    dot={{ fill: '#8884d8', strokeWidth: 2, r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}

            {activeChart === 'cashflow' && (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={projectionData}>
                  <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                  <XAxis 
                    dataKey="year" 
                    tickFormatter={formatYearTick}
                    className="text-xs"
                  />
                  <YAxis 
                    tickFormatter={(value) => `$${(value / 1000).toFixed(0)}K`}
                    className="text-xs"
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="income" fill="#82ca9d" name="Income" />
                  <Bar dataKey="expenses" fill="#ff7300" name="Expenses" />
                  <Bar dataKey="net_cash_flow" fill="#8884d8" name="Net Cash Flow" />
                </BarChart>
              </ResponsiveContainer>
            )}

            {activeChart === 'breakdown' && (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={expenseBreakdown}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={120}
                    paddingAngle={5}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {expenseBreakdown.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}