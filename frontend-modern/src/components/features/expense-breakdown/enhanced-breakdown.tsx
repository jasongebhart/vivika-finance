'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  BarChart3, 
  PieChart, 
  TrendingUp, 
  TrendingDown,
  Calculator,
  MapPin,
  AlertTriangle,
  CheckCircle,
  DollarSign,
  Target,
  Lightbulb,
  Eye,
  EyeOff
} from 'lucide-react'
import { formatCurrency } from '@/lib/utils'

interface LineItem {
  [key: string]: number
}

interface ExpenseAnalysis {
  total_annual: number
  total_monthly: number
  essential_total: number
  non_essential_total: number
  essential_percentage: number
  categories: {
    [key: string]: {
      total: number
      percentage: number
      expenses: Array<{
        name: string
        amount: number
        percentage: number
      }>
      essential: boolean
    }
  }
  summary: {
    highest_category: string
    lowest_category: string
    category_count: number
  }
}

interface OptimizationSuggestion {
  category: string
  suggestion: string
  potential_savings: number
  difficulty: string
}

interface OptimizationAnalysis {
  target_reduction: number
  potential_total_savings: number
  suggestions: OptimizationSuggestion[]
  feasibility: string
}

interface LocationComparison {
  comparison: {
    [location: string]: {
      total_annual: number
      total_monthly: number
      essential_total: number
      non_essential_total: number
      difference_from_base?: number
      percentage_difference?: number
    }
  }
  summary: {
    cheapest_location: string
    most_expensive_location: string
    max_savings: number
  }
}

interface EnhancedExpenseBreakdownProps {
  expenses: Array<{
    name: string
    annual_amount: number
    line_items?: LineItem
    category?: string
    essential?: boolean
  }>
  className?: string
}

export function EnhancedExpenseBreakdown({ expenses, className = '' }: EnhancedExpenseBreakdownProps) {
  const [analysis, setAnalysis] = useState<ExpenseAnalysis | null>(null)
  const [optimization, setOptimization] = useState<OptimizationAnalysis | null>(null)
  const [locationComparison, setLocationComparison] = useState<LocationComparison | null>(null)
  const [selectedExpense, setSelectedExpense] = useState<string | null>(null)
  const [showLineItems, setShowLineItems] = useState<{[key: string]: boolean}>({})
  const [targetReduction, setTargetReduction] = useState(10)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    analyzeExpenses()
    compareLocations()
  }, [expenses])

  const analyzeExpenses = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/expenses/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ expenses })
      })
      
      if (response.ok) {
        const data = await response.json()
        setAnalysis(data)
      }
    } catch (error) {
      console.error('Failed to analyze expenses:', error)
    } finally {
      setLoading(false)
    }
  }

  const generateOptimization = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/expenses/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          expenses, 
          target_reduction_percent: targetReduction 
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        setOptimization(data)
      }
    } catch (error) {
      console.error('Failed to generate optimization:', error)
    } finally {
      setLoading(false)
    }
  }

  const compareLocations = async () => {
    try {
      const response = await fetch('/api/expenses/location-comparison', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ expenses })
      })
      
      if (response.ok) {
        const data = await response.json()
        setLocationComparison(data)
      }
    } catch (error) {
      console.error('Failed to compare locations:', error)
    }
  }

  const toggleLineItems = (expenseName: string) => {
    setShowLineItems(prev => ({
      ...prev,
      [expenseName]: !prev[expenseName]
    }))
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'easy': return 'bg-green-100 text-green-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'hard': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading && !analysis) {
    return (
      <div className={`flex items-center justify-center p-8 ${className}`}>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className={`space-y-6 ${className}`}>
      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="details">Line Items</TabsTrigger>
          <TabsTrigger value="optimization">Optimize</TabsTrigger>
          <TabsTrigger value="locations">Locations</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          {analysis && (
            <>
              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center">
                      <DollarSign className="h-4 w-4 text-blue-600" />
                      <div className="ml-2">
                        <p className="text-sm font-medium text-muted-foreground">Total Annual</p>
                        <p className="text-2xl font-bold">{formatCurrency(analysis.total_annual)}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center">
                      <CheckCircle className="h-4 w-4 text-green-600" />
                      <div className="ml-2">
                        <p className="text-sm font-medium text-muted-foreground">Essential</p>
                        <p className="text-2xl font-bold">{analysis.essential_percentage.toFixed(0)}%</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center">
                      <AlertTriangle className="h-4 w-4 text-orange-600" />
                      <div className="ml-2">
                        <p className="text-sm font-medium text-muted-foreground">Non-Essential</p>
                        <p className="text-2xl font-bold">{formatCurrency(analysis.non_essential_total)}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center">
                      <BarChart3 className="h-4 w-4 text-purple-600" />
                      <div className="ml-2">
                        <p className="text-sm font-medium text-muted-foreground">Categories</p>
                        <p className="text-2xl font-bold">{analysis.summary.category_count}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Category Breakdown */}
              <Card>
                <CardHeader>
                  <CardTitle>Expense Categories</CardTitle>
                  <CardDescription>
                    Breakdown by category with essential vs non-essential classification
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {Object.entries(analysis.categories).map(([categoryName, categoryData]) => (
                      <div key={categoryName} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center space-x-3">
                          <Badge variant={categoryData.essential ? "default" : "secondary"}>
                            {categoryData.essential ? "Essential" : "Optional"}
                          </Badge>
                          <div>
                            <div className="font-medium">{categoryName}</div>
                            <div className="text-sm text-muted-foreground">
                              {categoryData.expenses.length} expense{categoryData.expenses.length !== 1 ? 's' : ''}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-4">
                          <div className="text-right">
                            <div className="font-medium">{formatCurrency(categoryData.total)}</div>
                            <div className="text-sm text-muted-foreground">
                              {categoryData.percentage.toFixed(1)}%
                            </div>
                          </div>
                          <Progress 
                            value={categoryData.percentage} 
                            className="w-20 h-2"
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        {/* Line Items Tab */}
        <TabsContent value="details" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Detailed Line Items</CardTitle>
              <CardDescription>
                Expand expenses to see monthly line item breakdowns
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {expenses.map((expense) => (
                  <div key={expense.name} className="border rounded-lg p-4">
                    <div 
                      className="flex items-center justify-between cursor-pointer"
                      onClick={() => toggleLineItems(expense.name)}
                    >
                      <div className="flex items-center space-x-3">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-6 w-6 p-0"
                        >
                          {showLineItems[expense.name] ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                        </Button>
                        <div>
                          <div className="font-medium">{expense.name}</div>
                          <div className="text-sm text-muted-foreground">
                            {formatCurrency(expense.annual_amount)} annually
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {expense.category && (
                          <Badge variant="outline">{expense.category}</Badge>
                        )}
                        {expense.essential !== undefined && (
                          <Badge variant={expense.essential ? "default" : "secondary"}>
                            {expense.essential ? "Essential" : "Optional"}
                          </Badge>
                        )}
                      </div>
                    </div>

                    {showLineItems[expense.name] && expense.line_items && (
                      <div className="mt-4 pt-4 border-t">
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                          {Object.entries(expense.line_items).map(([itemName, monthlyAmount]) => (
                            <div key={itemName} className="flex justify-between p-2 bg-muted rounded">
                              <span className="text-sm capitalize">
                                {itemName.replace(/_/g, ' ')}
                              </span>
                              <span className="text-sm font-medium">
                                {formatCurrency(monthlyAmount)}/mo
                              </span>
                            </div>
                          ))}
                        </div>
                        <div className="mt-3 text-sm text-muted-foreground">
                          Monthly total: {formatCurrency(Object.values(expense.line_items).reduce((sum, val) => sum + val, 0))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Optimization Tab */}
        <TabsContent value="optimization" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Target className="h-5 w-5 mr-2" />
                Expense Optimization
              </CardTitle>
              <CardDescription>
                Get personalized suggestions to reduce your expenses
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-4 mb-4">
                <label className="text-sm font-medium">Target Reduction:</label>
                <select 
                  value={targetReduction} 
                  onChange={(e) => setTargetReduction(Number(e.target.value))}
                  className="px-3 py-1 border rounded"
                >
                  <option value={5}>5%</option>
                  <option value={10}>10%</option>
                  <option value={15}>15%</option>
                  <option value={20}>20%</option>
                </select>
                <Button onClick={generateOptimization} disabled={loading}>
                  {loading ? "Analyzing..." : "Generate Suggestions"}
                </Button>
              </div>

              {optimization && (
                <div className="space-y-4">
                  <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium">Target: {formatCurrency(optimization.target_reduction)}</div>
                        <div className="text-sm text-muted-foreground">
                          Feasibility: {optimization.feasibility}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-medium text-green-600">
                          Potential: {formatCurrency(optimization.potential_total_savings)}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {((optimization.potential_total_savings / analysis!.total_annual) * 100).toFixed(1)}% reduction
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-3">
                    {optimization.suggestions.map((suggestion, index) => (
                      <div key={index} className="flex items-start space-x-3 p-3 border rounded-lg">
                        <Lightbulb className="h-5 w-5 text-yellow-500 mt-0.5" />
                        <div className="flex-1">
                          <div className="flex items-center justify-between">
                            <div className="font-medium">{suggestion.category}</div>
                            <div className="flex items-center space-x-2">
                              <Badge className={getDifficultyColor(suggestion.difficulty)}>
                                {suggestion.difficulty}
                              </Badge>
                              <span className="font-medium text-green-600">
                                {formatCurrency(suggestion.potential_savings)}
                              </span>
                            </div>
                          </div>
                          <div className="text-sm text-muted-foreground mt-1">
                            {suggestion.suggestion}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Locations Tab */}
        <TabsContent value="locations" className="space-y-4">
          {locationComparison && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <MapPin className="h-5 w-5 mr-2" />
                  Location Impact Analysis
                </CardTitle>
                <CardDescription>
                  See how your expenses would change in different locations
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  {Object.entries(locationComparison.comparison).map(([location, data]) => (
                    <Card key={location} className={location === locationComparison.summary.cheapest_location ? 'border-green-500' : ''}>
                      <CardContent className="p-4">
                        <div className="text-center">
                          <div className="font-medium text-lg">
                            {location === 'Sf' ? 'San Francisco' : location === 'Sd' ? 'San Diego' : 'Minnesota'}
                          </div>
                          <div className="text-2xl font-bold mt-2">
                            {formatCurrency(data.total_annual)}
                          </div>
                          {data.difference_from_base && (
                            <div className={`text-sm mt-1 ${data.difference_from_base > 0 ? 'text-red-600' : 'text-green-600'}`}>
                              {data.difference_from_base > 0 ? '+' : ''}{formatCurrency(data.difference_from_base)}
                            </div>
                          )}
                          {location === locationComparison.summary.cheapest_location && (
                            <Badge className="mt-2 bg-green-100 text-green-800">Cheapest</Badge>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                <div className="p-4 bg-green-50 dark:bg-green-950/20 rounded-lg">
                  <div className="flex items-center">
                    <TrendingDown className="h-5 w-5 text-green-600 mr-2" />
                    <div>
                      <div className="font-medium text-green-900 dark:text-green-100">
                        Maximum Potential Savings
                      </div>
                      <div className="text-sm text-green-700 dark:text-green-300">
                        Moving to {locationComparison.summary.cheapest_location === 'Sf' ? 'San Francisco' : 
                                 locationComparison.summary.cheapest_location === 'Sd' ? 'San Diego' : 'Minnesota'} 
                        could save up to {formatCurrency(locationComparison.summary.max_savings)} annually
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}