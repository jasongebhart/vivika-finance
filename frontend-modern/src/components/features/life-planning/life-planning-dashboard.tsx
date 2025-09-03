'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { 
  Home, 
  GraduationCap, 
  Calendar, 
  DollarSign,
  MapPin,
  TrendingUp,
  TrendingDown,
  Users,
  Target,
  Clock,
  Award,
  AlertCircle,
  CheckCircle,
  ArrowRight,
  Calculator,
  BarChart3
} from 'lucide-react'
import { formatCurrency } from '@/lib/utils'

interface Child {
  name: string
  current_age: number
  current_grade: number
}

interface LifePlanningScenario {
  scenario: {
    description: string
    move_year: number | null
    location: string
    location_name: string
    education_strategy: string
  }
  financial_summary: {
    total_moving_costs: number
    total_education_costs: number
    total_housing_savings: number
    total_income_impact: number
    net_present_value: number
    break_even_year: number | null
    total_net_benefit: number
  }
  yearly_breakdown: Array<{
    year: number
    costs: { [key: string]: number }
    savings: { [key: string]: number }
    net: number
    income_impact?: number
  }>
  quality_metrics: {
    quality_of_life_score: number
    education_quality: number
    financial_stress_level: string
  }
}

interface LifePlanningAnalysis {
  scenarios: LifePlanningScenario[]
  summary: {
    best_overall: any
    best_financial: any
    best_quality_of_life: any
    fastest_payback: any
    decision_points: Array<{
      year: number
      event: string
      recommendation: string
    }>
    key_insights: string[]
    recommendations: string[]
  }
  analysis_period: string
  children_profiles: Array<{
    name: string
    current_age: number
    current_grade: number
    graduation_year: number
  }>
}

interface LifePlanningDashboardProps {
  className?: string
}

export function LifePlanningDashboard({ className = '' }: LifePlanningDashboardProps) {
  const [analysis, setAnalysis] = useState<LifePlanningAnalysis | null>(null)
  const [loading, setLoading] = useState(false)
  const [children, setChildren] = useState<Child[]>([
    { name: 'Emma', current_age: 12, current_grade: 7 },
    { name: 'Jake', current_age: 9, current_grade: 4 }
  ])
  const [currentIncome, setCurrentIncome] = useState(500000)
  const [currentExpenses, setCurrentExpenses] = useState(200000)
  const [analysisYears, setAnalysisYears] = useState(10)
  const [selectedScenario, setSelectedScenario] = useState<LifePlanningScenario | null>(null)
  const [initialLoadComplete, setInitialLoadComplete] = useState(false)
  const [detailModalScenario, setDetailModalScenario] = useState<LifePlanningScenario | null>(null)

  const runAnalysis = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/life-planning/move-analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          children: children,
          current_annual_income: currentIncome,
          current_annual_expenses: currentExpenses,
          analysis_years: analysisYears
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        setAnalysis(data)
        setSelectedScenario(data.scenarios[0]) // Select best scenario by default
      }
    } catch (error) {
      console.error('Failed to run life planning analysis:', error)
    } finally {
      setLoading(false)
    }
  }

  const addChild = () => {
    setChildren([...children, { 
      name: `Child ${children.length + 1}`, 
      current_age: 10, 
      current_grade: 5 
    }])
  }

  const updateChild = (index: number, field: keyof Child, value: string | number) => {
    const updated = [...children]
    updated[index] = { ...updated[index], [field]: value }
    setChildren(updated)
  }

  const removeChild = (index: number) => {
    setChildren(children.filter((_, i) => i !== index))
  }

  // Automatically run analysis when component loads
  useEffect(() => {
    if (!initialLoadComplete) {
      runAnalysis()
      setInitialLoadComplete(true)
    }
  }, [initialLoadComplete])

  const getScenarioColor = (scenario: LifePlanningScenario, index: number) => {
    if (index === 0) return 'border-green-500 bg-green-50'
    if (scenario.financial_summary.net_present_value < 0) return 'border-red-200'
    return 'border-gray-200'
  }

  const getStressColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'low': return 'text-green-600'
      case 'moderate': return 'text-yellow-600'
      case 'high': return 'text-orange-600'
      case 'very high': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  // Scenario Detail Modal Component
  const ScenarioDetailModal = ({ scenario, onClose }: { scenario: LifePlanningScenario, onClose: () => void }) => {
    if (!scenario) return null

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
          <div className="p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{scenario.scenario.description}</h2>
                <p className="text-gray-600 mt-1">
                  {scenario.scenario.location_name} • {scenario.scenario.education_strategy.charAt(0).toUpperCase() + 
                   scenario.scenario.education_strategy.slice(1)} Education
                </p>
              </div>
              <Button variant="outline" onClick={onClose}>
                Close
              </Button>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <Card>
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {formatCurrency(scenario.financial_summary.net_present_value)}
                  </div>
                  <div className="text-sm text-gray-600">Net Present Value</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {scenario.financial_summary.break_even_year || 'Never'}
                  </div>
                  <div className="text-sm text-gray-600">Break Even Year</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {scenario.quality_metrics.quality_of_life_score}/10
                  </div>
                  <div className="text-sm text-gray-600">Quality of Life</div>
                </CardContent>
              </Card>
            </div>

            {/* Financial Breakdown */}
            <Card className="mb-6">
              <CardHeader>
                <CardTitle>Financial Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <div className="text-sm text-gray-600">Moving Costs</div>
                    <div className="font-medium text-red-600">
                      -{formatCurrency(scenario.financial_summary.total_moving_costs)}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Housing Savings</div>
                    <div className="font-medium text-green-600">
                      +{formatCurrency(scenario.financial_summary.total_housing_savings)}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Education Costs</div>
                    <div className="font-medium text-red-600">
                      -{formatCurrency(scenario.financial_summary.total_education_costs)}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Income Impact</div>
                    <div className={`font-medium ${scenario.financial_summary.total_income_impact >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {scenario.financial_summary.total_income_impact >= 0 ? '+' : ''}{formatCurrency(scenario.financial_summary.total_income_impact)}
                    </div>
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t">
                  <div className="flex justify-between items-center">
                    <span className="font-medium">Total Net Benefit (10 years):</span>
                    <span className={`text-xl font-bold ${scenario.financial_summary.total_net_benefit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {scenario.financial_summary.total_net_benefit >= 0 ? '+' : ''}{formatCurrency(scenario.financial_summary.total_net_benefit)}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Quality Metrics */}
            <Card className="mb-6">
              <CardHeader>
                <CardTitle>Quality & Risk Assessment</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="text-center">
                    <div className="text-lg font-bold">{scenario.quality_metrics.quality_of_life_score}/10</div>
                    <div className="text-sm text-gray-600">Quality of Life</div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${scenario.quality_metrics.quality_of_life_score * 10}%` }}
                      ></div>
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold">{scenario.quality_metrics.education_quality}/10</div>
                    <div className="text-sm text-gray-600">Education Quality</div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                      <div 
                        className="bg-green-600 h-2 rounded-full" 
                        style={{ width: `${scenario.quality_metrics.education_quality * 10}%` }}
                      ></div>
                    </div>
                  </div>
                  <div className="text-center">
                    <div className={`text-lg font-bold ${getStressColor(scenario.quality_metrics.financial_stress_level)}`}>
                      {scenario.quality_metrics.financial_stress_level}
                    </div>
                    <div className="text-sm text-gray-600">Financial Stress</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Timeline Preview */}
            <Card>
              <CardHeader>
                <CardTitle>10-Year Financial Timeline</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {scenario.yearly_breakdown.map((year, index) => (
                    <div key={year.year} className="flex items-center justify-between p-2 border rounded text-sm">
                      <div className="flex items-center space-x-4">
                        <div className="font-medium w-12">{year.year}</div>
                        <div className="flex space-x-3">
                          {year.savings.housing && (
                            <span className="text-green-600 text-xs">Housing: +{formatCurrency(year.savings.housing)}</span>
                          )}
                          {year.costs.education > 0 && (
                            <span className="text-red-600 text-xs">Education: -{formatCurrency(year.costs.education)}</span>
                          )}
                          {year.costs.living_expenses && (
                            <span className="text-orange-600 text-xs">Living: {formatCurrency(year.costs.living_expenses)}</span>
                          )}
                        </div>
                      </div>
                      <div className={`font-medium ${year.net >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {year.net >= 0 ? '+' : ''}{formatCurrency(year.net)}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Action Buttons */}
            <div className="flex justify-end space-x-3 mt-6">
              <Button 
                variant="outline" 
                onClick={() => {
                  setSelectedScenario(scenario)
                  onClose()
                  // Switch to timeline tab
                  document.querySelector('[value="timeline"]')?.click()
                }}
              >
                View Full Timeline
              </Button>
              <Button onClick={onClose}>
                Close
              </Button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Target className="h-6 w-6 mr-2" />
            Life Planning Decision Dashboard
          </CardTitle>
          <CardDescription>
            Analyze optimal timing for major life decisions: moving, education choices, and family planning
          </CardDescription>
        </CardHeader>
      </Card>

      <Tabs defaultValue="analysis" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="setup">Setup</TabsTrigger>
          <TabsTrigger value="analysis">Analysis</TabsTrigger>
          <TabsTrigger value="scenarios">Scenarios</TabsTrigger>
          <TabsTrigger value="timeline">Timeline</TabsTrigger>
        </TabsList>

        {/* Setup Tab */}
        <TabsContent value="setup" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Family Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Users className="h-5 w-5 mr-2" />
                  Family Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {children.map((child, index) => (
                  <div key={index} className="flex items-center space-x-2 p-3 border rounded">
                    <Input
                      placeholder="Child name"
                      value={child.name}
                      onChange={(e) => updateChild(index, 'name', e.target.value)}
                      className="flex-1"
                    />
                    <Input
                      type="number"
                      placeholder="Age"
                      value={child.current_age}
                      onChange={(e) => updateChild(index, 'current_age', parseInt(e.target.value) || 0)}
                      className="w-20"
                    />
                    <Input
                      type="number"
                      placeholder="Grade"
                      value={child.current_grade}
                      onChange={(e) => updateChild(index, 'current_grade', parseInt(e.target.value) || 0)}
                      className="w-20"
                    />
                    {children.length > 1 && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => removeChild(index)}
                      >
                        Remove
                      </Button>
                    )}
                  </div>
                ))}
                <Button onClick={addChild} variant="outline" className="w-full">
                  Add Child
                </Button>
              </CardContent>
            </Card>

            {/* Financial Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <DollarSign className="h-5 w-5 mr-2" />
                  Financial Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="income">Current Annual Income</Label>
                  <Input
                    id="income"
                    type="number"
                    value={currentIncome}
                    onChange={(e) => setCurrentIncome(parseInt(e.target.value) || 0)}
                  />
                </div>
                <div>
                  <Label htmlFor="expenses">Current Annual Expenses</Label>
                  <Input
                    id="expenses"
                    type="number"
                    value={currentExpenses}
                    onChange={(e) => setCurrentExpenses(parseInt(e.target.value) || 0)}
                  />
                </div>
                <div>
                  <Label htmlFor="years">Analysis Period (Years)</Label>
                  <Input
                    id="years"
                    type="number"
                    value={analysisYears}
                    onChange={(e) => setAnalysisYears(parseInt(e.target.value) || 10)}
                    min="5"
                    max="20"
                  />
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="flex justify-center">
            <Button onClick={runAnalysis} disabled={loading} size="lg">
              {loading ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Analyzing...
                </div>
              ) : (
                <div className="flex items-center">
                  <Calculator className="h-4 w-4 mr-2" />
                  Run Life Planning Analysis
                </div>
              )}
            </Button>
          </div>
        </TabsContent>

        {/* Analysis Tab */}
        <TabsContent value="analysis" className="space-y-4">
          {loading ? (
            <Card>
              <CardContent className="p-8 text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-muted-foreground mb-2">Analyzing your life planning scenarios...</p>
                <p className="text-sm text-muted-foreground">Evaluating 25+ scenarios across different locations and education strategies</p>
              </CardContent>
            </Card>
          ) : analysis ? (
            <>
              {/* Analysis Header Info */}
              <Card className="bg-blue-50 border-blue-200">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Users className="h-5 w-5 text-blue-600" />
                      <div>
                        <p className="text-sm font-medium text-blue-900">
                          Analysis for Emma (12, Grade 7) & Jake (9, Grade 4)
                        </p>
                        <p className="text-xs text-blue-700">
                          Income: {formatCurrency(currentIncome)}, Expenses: {formatCurrency(currentExpenses)}, Analysis: {analysisYears} years
                        </p>
                      </div>
                    </div>
                    <Button variant="outline" size="sm" onClick={() => document.querySelector('[value="setup"]')?.click()}>
                      Customize Settings
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center">
                      <Award className="h-4 w-4 text-green-600" />
                      <div className="ml-2">
                        <p className="text-sm font-medium text-muted-foreground">Best Overall</p>
                        <p className="text-lg font-bold">{analysis.summary.best_overall?.location_name || 'None'}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center">
                      <DollarSign className="h-4 w-4 text-blue-600" />
                      <div className="ml-2">
                        <p className="text-sm font-medium text-muted-foreground">Best Financial</p>
                        <p className="text-lg font-bold">{analysis.summary.best_financial?.location_name || 'None'}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center">
                      <Home className="h-4 w-4 text-purple-600" />
                      <div className="ml-2">
                        <p className="text-sm font-medium text-muted-foreground">Best Quality</p>
                        <p className="text-lg font-bold">{analysis.summary.best_quality_of_life?.location_name || 'None'}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center">
                      <Clock className="h-4 w-4 text-orange-600" />
                      <div className="ml-2">
                        <p className="text-sm font-medium text-muted-foreground">Fastest Payback</p>
                        <p className="text-lg font-bold">
                          {analysis.summary.fastest_payback?.move_year || 'N/A'}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Key Insights */}
              <Card>
                <CardHeader>
                  <CardTitle>Key Insights</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {analysis.summary.key_insights.map((insight, index) => (
                      <div key={index} className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                        <CheckCircle className="h-5 w-5 text-blue-600 mt-0.5" />
                        <span className="text-blue-900">{insight}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Recommendations */}
              <Card>
                <CardHeader>
                  <CardTitle>Recommendations</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {analysis.summary.recommendations.map((recommendation, index) => (
                      <div key={index} className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg">
                        <ArrowRight className="h-5 w-5 text-green-600 mt-0.5" />
                        <span className="text-green-900">{recommendation}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Decision Points */}
              {analysis.summary.decision_points.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Critical Decision Points</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {analysis.summary.decision_points.map((point, index) => (
                        <div key={index} className="flex items-start space-x-3 p-3 border rounded-lg">
                          <Calendar className="h-5 w-5 text-orange-600 mt-0.5" />
                          <div>
                            <div className="font-medium">{point.year}: {point.event}</div>
                            <div className="text-sm text-muted-foreground">{point.recommendation}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <BarChart3 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">Run analysis to see results</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Scenarios Tab */}
        <TabsContent value="scenarios" className="space-y-4">
          {loading ? (
            <Card>
              <CardContent className="p-8 text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-muted-foreground">Loading scenario comparisons...</p>
              </CardContent>
            </Card>
          ) : analysis ? (
            <>
              {/* Scenarios Header Info */}
              <Card className="bg-green-50 border-green-200">
                <CardContent className="p-4">
                  <div className="flex items-center space-x-3">
                    <BarChart3 className="h-5 w-5 text-green-600" />
                    <div>
                      <p className="text-sm font-medium text-green-900">
                        {analysis.scenarios.length} scenarios analyzed - Top 6 shown below
                      </p>
                      <p className="text-xs text-green-700">
                        Click any scenario to view its detailed timeline. Green border = best option.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <div className="grid grid-cols-1 gap-4">
              {analysis.scenarios.slice(0, 6).map((scenario, index) => (
                <Card 
                  key={index} 
                  className={`cursor-pointer transition-colors ${getScenarioColor(scenario, index)} ${
                    selectedScenario === scenario ? 'ring-2 ring-blue-500' : ''
                  }`}
                  onClick={() => setSelectedScenario(scenario)}
                >
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                          {index === 0 && <Badge className="bg-green-100 text-green-800">Best</Badge>}
                          <MapPin className="h-4 w-4" />
                          <div>
                            <div className="font-medium">{scenario.scenario.description}</div>
                            <div className="text-sm text-muted-foreground">
                              {scenario.scenario.education_strategy.charAt(0).toUpperCase() + 
                               scenario.scenario.education_strategy.slice(1)} Education
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`text-lg font-bold ${
                          scenario.financial_summary.net_present_value >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {formatCurrency(scenario.financial_summary.net_present_value)}
                        </div>
                        <div className="text-sm text-muted-foreground">Net Present Value</div>
                      </div>
                    </div>
                    
                    <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <div className="text-muted-foreground">Moving Costs</div>
                        <div className="font-medium">{formatCurrency(scenario.financial_summary.total_moving_costs)}</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Education Costs</div>
                        <div className="font-medium">{formatCurrency(scenario.financial_summary.total_education_costs)}</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Break Even</div>
                        <div className="font-medium">
                          {scenario.financial_summary.break_even_year || 'Never'}
                        </div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Stress Level</div>
                        <div className={`font-medium ${getStressColor(scenario.quality_metrics.financial_stress_level)}`}>
                          {scenario.quality_metrics.financial_stress_level}
                        </div>
                      </div>
                    </div>
                    
                    {/* Action Buttons */}
                    <div className="mt-4 flex space-x-2">
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="flex-1"
                        onClick={(e) => {
                          e.stopPropagation()
                          setDetailModalScenario(scenario)
                        }}
                      >
                        View Details
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="flex-1"
                        onClick={(e) => {
                          e.stopPropagation()
                          setSelectedScenario(scenario)
                          document.querySelector('[value="timeline"]')?.click()
                        }}
                      >
                        View Timeline
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
            </>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <Target className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">Run analysis to see scenarios</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Timeline Tab */}
        <TabsContent value="timeline" className="space-y-4">
          {loading ? (
            <Card>
              <CardContent className="p-8 text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-muted-foreground">Loading timeline analysis...</p>
              </CardContent>
            </Card>
          ) : selectedScenario ? (
            <Card>
              <CardHeader>
                <CardTitle>Financial Timeline: {selectedScenario.scenario.description}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {selectedScenario.yearly_breakdown.map((year, index) => (
                    <div key={year.year} className="flex items-center justify-between p-3 border rounded">
                      <div className="flex items-center space-x-4">
                        <div className="font-medium text-sm w-16">{year.year}</div>
                        <div className="flex space-x-4 text-sm">
                          {year.savings.housing && (
                            <span className="text-green-600">+{formatCurrency(year.savings.housing)}</span>
                          )}
                          {year.costs.education && (
                            <span className="text-red-600">-{formatCurrency(year.costs.education)}</span>
                          )}
                          {year.costs.living_expenses && (
                            <span className="text-orange-600">-{formatCurrency(year.costs.living_expenses)}</span>
                          )}
                        </div>
                      </div>
                      <div className={`font-medium ${
                        year.net >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {year.net >= 0 ? '+' : ''}{formatCurrency(year.net)}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <Calendar className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">Select a scenario to see timeline</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      {/* Scenario Detail Modal */}
      {detailModalScenario && (
        <ScenarioDetailModal 
          scenario={detailModalScenario} 
          onClose={() => setDetailModalScenario(null)} 
        />
      )}
    </div>
  )
}