'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import {
  ArrowLeft,
  Calculator,
  TrendingUp,
  PiggyBank,
  Home,
  GraduationCap,
  Car,
  Target,
  BarChart3,
  Settings,
  Play,
  MapPin,
  Users,
  Building,
  School,
  Calendar,
  DollarSign,
  Activity,
  ChevronDown,
  ChevronUp
} from 'lucide-react'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { useDynamicScenarios, type DynamicScenario } from '@/hooks/use-dynamic-scenarios'
import { formatCurrency, formatPercentage } from '@/lib/utils'

interface DynamicScenarioDetailProps {
  scenarioId: string
}

interface ExpenseLineItemsProps {
  items: Record<string, number>
  isExpanded: boolean
  onToggle: () => void
}

function ExpenseLineItems({ items, isExpanded, onToggle }: ExpenseLineItemsProps) {
  const hasItems = Object.keys(items).length > 0
  
  if (!hasItems) return null
  
  return (
    <div className="mt-2">
      <Button
        variant="ghost" 
        size="sm"
        onClick={onToggle}
        className="flex items-center space-x-1 text-xs text-muted-foreground hover:text-foreground"
      >
        <span>Details ({Object.keys(items).length} items)</span>
        {isExpanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
      </Button>
      
      {isExpanded && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="mt-2 p-3 bg-muted/50 rounded-md"
        >
          <div className="grid grid-cols-2 gap-2 text-xs">
            {Object.entries(items).map(([key, value]) => (
              <div key={key} className="flex justify-between">
                <span className="capitalize text-muted-foreground">
                  {key.replace(/_/g, ' ')}:
                </span>
                <span>{formatCurrency(value * 12)}/year</span>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  )
}

function LoadingState() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
    </div>
  )
}

function ErrorState({ error, onRetry }: { error: string; onRetry: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen space-y-4">
      <p className="text-red-600 text-center">{error}</p>
      <Button onClick={onRetry}>Try Again</Button>
    </div>
  )
}

function ScenarioHeader({ scenario }: { scenario: DynamicScenario }) {
  const router = useRouter()
  
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
      case 'running': return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
      case 'failed': return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400'
    }
  }
  
  return (
    <header className="border-b border bg-card">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.back()}
              className="flex items-center space-x-2"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Back</span>
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-foreground">
                {scenario.name}
              </h1>
              <div className="flex items-center space-x-4 mt-2">
                <Badge className={`capitalize ${getStatusColor(scenario.status)}`}>
                  {scenario.status}
                </Badge>
                <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                  <MapPin className="h-3 w-3" />
                  <span>{scenario.location}</span>
                </div>
                <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                  <Building className="h-3 w-3" />
                  <span>{scenario.housing}</span>
                </div>
                <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                  <School className="h-3 w-3" />
                  <span>{scenario.school_type}</span>
                </div>
                <span className="text-sm text-muted-foreground">
                  Created: {new Date(scenario.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
          <div className="flex space-x-2">
            <Button variant="outline">
              <Settings className="mr-2 h-4 w-4" />
              Edit Parameters
            </Button>
            <Button>
              <Play className="mr-2 h-4 w-4" />
              Run Projection
            </Button>
          </div>
        </div>
      </div>
    </header>
  )
}

function ScenarioSummary({ scenario }: { scenario: DynamicScenario }) {
  const results = scenario.projection_results
  
  if (!results) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center text-muted-foreground">
            <Calculator className="mx-auto h-12 w-12 mb-4" />
            <h3 className="text-lg font-medium mb-2">No Results Yet</h3>
            <p>Run the projection to see detailed financial analysis.</p>
          </div>
        </CardContent>
      </Card>
    )
  }
  
  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Final Net Worth</CardTitle>
          <TrendingUp className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-green-600">
            {formatCurrency(results.final_net_worth)}
          </div>
          <p className="text-xs text-muted-foreground">
            After {scenario.projection_years} years
          </p>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Annual Growth Rate</CardTitle>
          <BarChart3 className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {formatPercentage(results.annual_growth_rate, 1)}
          </div>
          <p className="text-xs text-muted-foreground">
            Average annual return
          </p>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Expenses</CardTitle>
          <DollarSign className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {formatCurrency(results.total_expenses)}
          </div>
          <p className="text-xs text-muted-foreground">
            Over {scenario.projection_years} years
          </p>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Retirement Ready</CardTitle>
          <PiggyBank className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className={`text-2xl font-bold ${results.retirement_readiness ? 'text-green-600' : 'text-orange-600'}`}>
            {results.retirement_readiness ? 'Yes' : 'No'}
          </div>
          <p className="text-xs text-muted-foreground">
            Based on projections
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

function DetailedExpenseBreakdown({ scenario }: { scenario: DynamicScenario }) {
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set())
  
  const expenses = scenario.projection_results?.detailed_expenses || []
  
  // Debug logging
  console.log('DetailedExpenseBreakdown Debug:')
  console.log('- scenario:', scenario)
  console.log('- projection_results:', scenario.projection_results)
  console.log('- detailed_expenses:', scenario.projection_results?.detailed_expenses)
  console.log('- expenses.length:', expenses.length)
  
  if (expenses.length === 0) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center text-muted-foreground">
            <Target className="mx-auto h-12 w-12 mb-4" />
            <h3 className="text-lg font-medium mb-2">No Expense Details</h3>
            <p>Run the projection to see detailed expense breakdown.</p>
          </div>
        </CardContent>
      </Card>
    )
  }
  
  const toggleExpanded = (expenseName: string) => {
    const newExpanded = new Set(expandedItems)
    if (newExpanded.has(expenseName)) {
      newExpanded.delete(expenseName)
    } else {
      newExpanded.add(expenseName)
    }
    setExpandedItems(newExpanded)
  }
  
  // Group expenses by category
  const expenseCategories = {
    'Housing & Property': expenses.filter(e => 
      e.name.toLowerCase().includes('housing') || 
      e.name.toLowerCase().includes('property') ||
      e.name.toLowerCase().includes('rent')
    ),
    'Education': expenses.filter(e => 
      e.name.toLowerCase().includes('school') || 
      e.name.toLowerCase().includes('college') ||
      e.name.toLowerCase().includes('education')
    ),
    'Living Expenses': expenses.filter(e => 
      e.name.toLowerCase().includes('living') || 
      e.name.toLowerCase().includes('utilities') ||
      e.name.toLowerCase().includes('transportation') ||
      e.name.toLowerCase().includes('insurance') ||
      e.name.toLowerCase().includes('subscriptions')
    ),
    'Activities & Travel': expenses.filter(e => 
      e.name.toLowerCase().includes('activities') || 
      e.name.toLowerCase().includes('travel') ||
      e.name.toLowerCase().includes('vacation') ||
      e.name.toLowerCase().includes('baseball') ||
      e.name.toLowerCase().includes('ski')
    )
  }
  
  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'Housing & Property': return <Home className="h-5 w-5" />
      case 'Education': return <GraduationCap className="h-5 w-5" />
      case 'Living Expenses': return <DollarSign className="h-5 w-5" />
      case 'Activities & Travel': return <Activity className="h-5 w-5" />
      default: return <Target className="h-5 w-5" />
    }
  }
  
  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'Housing & Property': return 'bg-blue-500'
      case 'Education': return 'bg-purple-500'
      case 'Living Expenses': return 'bg-green-500'
      case 'Activities & Travel': return 'bg-orange-500'
      default: return 'bg-gray-500'
    }
  }
  
  return (
    <div className="space-y-6">
      {Object.entries(expenseCategories).map(([category, categoryExpenses]) => {
        if (categoryExpenses.length === 0) return null
        
        const totalCategoryAmount = categoryExpenses.reduce((sum, exp) => sum + exp.annual_amount, 0)
        
        return (
          <Card key={category}>
            <CardHeader>
              <CardTitle className="flex items-center space-x-3">
                <div className={`p-2 rounded-lg ${getCategoryColor(category)} text-white`}>
                  {getCategoryIcon(category)}
                </div>
                <div>
                  <span>{category}</span>
                  <div className="text-sm font-normal text-muted-foreground">
                    {formatCurrency(totalCategoryAmount)}/year • {categoryExpenses.length} items
                  </div>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {categoryExpenses.map((expense) => (
                  <div key={expense.name} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium">{expense.name}</h4>
                        <div className="flex items-center space-x-4 mt-1 text-sm text-muted-foreground">
                          <span>{formatCurrency(expense.annual_amount)}/year</span>
                          <span>Ages {expense.start_age}-{expense.end_age || '∞'}</span>
                          {expense.inflation_adjusted && (
                            <Badge variant="outline" className="text-xs">Inflation Adjusted</Badge>
                          )}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-semibold">
                          {formatCurrency(expense.annual_amount)}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {formatCurrency(expense.annual_amount / 12)}/month
                        </div>
                      </div>
                    </div>
                    
                    {expense.line_items && (
                      <ExpenseLineItems
                        items={expense.line_items}
                        isExpanded={expandedItems.has(expense.name)}
                        onToggle={() => toggleExpanded(expense.name)}
                      />
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}

function AssetsBreakdown({ scenario }: { scenario: DynamicScenario }) {
  const assets = scenario.projection_results?.assets_detail || []
  
  // Debug logging
  console.log('AssetsBreakdown Debug:')
  console.log('- assets_detail:', scenario.projection_results?.assets_detail)
  console.log('- assets.length:', assets.length)
  
  if (assets.length === 0) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center text-muted-foreground">
            <PiggyBank className="mx-auto h-12 w-12 mb-4" />
            <h3 className="text-lg font-medium mb-2">No Asset Details</h3>
            <p>Run the projection to see detailed asset breakdown.</p>
          </div>
        </CardContent>
      </Card>
    )
  }
  
  const totalValue = assets.reduce((sum, asset) => sum + asset.current_value, 0)
  
  // Group assets by type
  const assetCategories = {
    'Retirement Accounts': assets.filter(a => 
      a.name.includes('401') || a.name.includes('IRA') || a.name.includes('Roth')
    ),
    'Investment Accounts': assets.filter(a => 
      !a.name.includes('401') && !a.name.includes('IRA') && !a.name.includes('Roth')
    )
  }
  
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Total Assets</CardTitle>
          <CardDescription>Current investment portfolio breakdown</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold text-green-600 mb-4">
            {formatCurrency(totalValue)}
          </div>
          <div className="text-sm text-muted-foreground">
            Across {assets.length} accounts
          </div>
        </CardContent>
      </Card>
      
      {Object.entries(assetCategories).map(([category, categoryAssets]) => {
        if (categoryAssets.length === 0) return null
        
        const categoryValue = categoryAssets.reduce((sum, asset) => sum + asset.current_value, 0)
        const categoryPercentage = (categoryValue / totalValue) * 100
        
        return (
          <Card key={category}>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>{category}</span>
                <div className="text-right">
                  <div className="text-lg font-semibold">{formatCurrency(categoryValue)}</div>
                  <div className="text-sm text-muted-foreground">{categoryPercentage.toFixed(1)}% of total</div>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {categoryAssets.map((asset) => {
                  const assetPercentage = (asset.current_value / totalValue) * 100
                  return (
                    <div key={asset.name} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex-1">
                        <h4 className="font-medium">{asset.name}</h4>
                        <div className="flex items-center space-x-4 mt-1 text-sm text-muted-foreground">
                          {asset.asset_type && (
                            <span className="capitalize">{asset.asset_type}</span>
                          )}
                          {asset.expected_return && (
                            <span>{formatPercentage(asset.expected_return, 1)} expected return</span>
                          )}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold">{formatCurrency(asset.current_value)}</div>
                        <div className="text-sm text-muted-foreground">{assetPercentage.toFixed(1)}%</div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}

export function DynamicScenarioDetail({ scenarioId }: DynamicScenarioDetailProps) {
  const { getScenarioById } = useDynamicScenarios()
  const [scenario, setScenario] = useState<DynamicScenario | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  const loadScenario = async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      const data = await getScenarioById(scenarioId)
      if (!data) {
        throw new Error('Scenario not found')
      }
      
      setScenario(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load scenario')
    } finally {
      setIsLoading(false)
    }
  }
  
  useEffect(() => {
    loadScenario()
  }, [scenarioId])
  
  if (isLoading) return <LoadingState />
  if (error) return <ErrorState error={error} onRetry={loadScenario} />
  if (!scenario) return <ErrorState error="Scenario not found" onRetry={loadScenario} />
  
  return (
    <div className="min-h-screen bg-background">
      <ScenarioHeader scenario={scenario} />
      
      <main className="container mx-auto px-6 py-8">
        {/* Summary Cards */}
        <div className="mb-8">
          <ScenarioSummary scenario={scenario} />
        </div>
        
        {/* Detailed Tabs */}
        <Tabs defaultValue="expenses" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="expenses">Expense Details</TabsTrigger>
            <TabsTrigger value="assets">Asset Breakdown</TabsTrigger>
            <TabsTrigger value="projections">Year-by-Year</TabsTrigger>
          </TabsList>
          
          <TabsContent value="expenses">
            <DetailedExpenseBreakdown scenario={scenario} />
          </TabsContent>
          
          <TabsContent value="assets">
            <AssetsBreakdown scenario={scenario} />
          </TabsContent>
          
          <TabsContent value="projections">
            <Card>
              <CardHeader>
                <CardTitle>Year-by-Year Projections</CardTitle>
                <CardDescription>
                  Detailed financial projections over {scenario.projection_years} years
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center text-muted-foreground py-12">
                  <BarChart3 className="mx-auto h-12 w-12 mb-4" />
                  <h3 className="text-lg font-medium mb-2">Chart Coming Soon</h3>
                  <p>Detailed year-by-year projection visualization</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}