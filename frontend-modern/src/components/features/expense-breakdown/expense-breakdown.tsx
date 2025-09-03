'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { 
  Home, 
  Car, 
  GraduationCap, 
  Heart, 
  Zap, 
  ShoppingCart,
  Users,
  MapPin,
  TrendingUp,
  TrendingDown,
  Minus
} from 'lucide-react'
import { formatCurrency } from '@/lib/utils'

interface ExpenseCategory {
  name: string
  annual_amount: number
  line_items?: { [key: string]: number }
  icon: React.ReactNode
  color: string
}

interface ExpenseBreakdownProps {
  scenario: {
    name: string
    location: string
    housing: string
    schoolType: string
    spouse1Status: string
    spouse2Status: string
    expenses?: ExpenseCategory[]
  }
  className?: string
}

// Sample expense data with location multipliers
const getExpenseComparison = (location: string, housing: string, schoolType: string) => {
  const baseExpenses = {
    'Living Expenses': { base: 19800, icon: <ShoppingCart className="h-4 w-4" />, color: 'bg-blue-500' },
    'Housing Expenses': { base: 30000, icon: <Home className="h-4 w-4" />, color: 'bg-green-500' },
    'Utilities': { base: 6600, icon: <Zap className="h-4 w-4" />, color: 'bg-yellow-500' },
    'Transportation': { base: 12300, icon: <Car className="h-4 w-4" />, color: 'bg-purple-500' },
    'Insurance': { base: 15600, icon: <Heart className="h-4 w-4" />, color: 'bg-red-500' },
    'Education': { base: schoolType === 'Private' ? 124000 : schoolType === 'Pripub' ? 62000 : 50000, icon: <GraduationCap className="h-4 w-4" />, color: 'bg-indigo-500' }
  }

  const locationMultipliers = {
    'Sf': { living: 1.4, housing: 2.8, utilities: 1.4, transport: 1.4, insurance: 1.4 },
    'Sd': { living: 1.2, housing: 1.8, utilities: 1.2, transport: 1.2, insurance: 1.2 },
    'Mn': { living: 0.85, housing: 0.7, utilities: 0.85, transport: 0.85, insurance: 0.85 }
  }

  const mult = locationMultipliers[location as keyof typeof locationMultipliers] || locationMultipliers['Sf']

  return {
    'Living Expenses': {
      ...baseExpenses['Living Expenses'],
      current: Math.round(baseExpenses['Living Expenses'].base * mult.living),
      sf: Math.round(baseExpenses['Living Expenses'].base * locationMultipliers['Sf'].living),
      sd: Math.round(baseExpenses['Living Expenses'].base * locationMultipliers['Sd'].living),
      mn: Math.round(baseExpenses['Living Expenses'].base * locationMultipliers['Mn'].living)
    },
    'Housing Expenses': {
      ...baseExpenses['Housing Expenses'],
      current: housing === 'Own' ? Math.round(baseExpenses['Housing Expenses'].base * mult.housing) : Math.round(baseExpenses['Housing Expenses'].base * mult.housing * 0.6),
      sf: housing === 'Own' ? Math.round(baseExpenses['Housing Expenses'].base * locationMultipliers['Sf'].housing) : Math.round(baseExpenses['Housing Expenses'].base * locationMultipliers['Sf'].housing * 0.6),
      sd: housing === 'Own' ? Math.round(baseExpenses['Housing Expenses'].base * locationMultipliers['Sd'].housing) : Math.round(baseExpenses['Housing Expenses'].base * locationMultipliers['Sd'].housing * 0.6),
      mn: housing === 'Own' ? Math.round(baseExpenses['Housing Expenses'].base * locationMultipliers['Mn'].housing) : Math.round(baseExpenses['Housing Expenses'].base * locationMultipliers['Mn'].housing * 0.6)
    },
    'Utilities': {
      ...baseExpenses['Utilities'],
      current: Math.round(baseExpenses['Utilities'].base * mult.utilities),
      sf: Math.round(baseExpenses['Utilities'].base * locationMultipliers['Sf'].utilities),
      sd: Math.round(baseExpenses['Utilities'].base * locationMultipliers['Sd'].utilities),
      mn: Math.round(baseExpenses['Utilities'].base * locationMultipliers['Mn'].utilities)
    },
    'Transportation': {
      ...baseExpenses['Transportation'],
      current: Math.round(baseExpenses['Transportation'].base * mult.transport),
      sf: Math.round(baseExpenses['Transportation'].base * locationMultipliers['Sf'].transport),
      sd: Math.round(baseExpenses['Transportation'].base * locationMultipliers['Sd'].transport),
      mn: Math.round(baseExpenses['Transportation'].base * locationMultipliers['Mn'].transport)
    },
    'Insurance': {
      ...baseExpenses['Insurance'],
      current: Math.round(baseExpenses['Insurance'].base * mult.insurance),
      sf: Math.round(baseExpenses['Insurance'].base * locationMultipliers['Sf'].insurance),
      sd: Math.round(baseExpenses['Insurance'].base * locationMultipliers['Sd'].insurance),
      mn: Math.round(baseExpenses['Insurance'].base * locationMultipliers['Mn'].insurance)
    },
    'Education': {
      ...baseExpenses['Education'],
      current: baseExpenses['Education'].base,
      sf: baseExpenses['Education'].base,
      sd: baseExpenses['Education'].base,
      mn: baseExpenses['Education'].base
    }
  }
}

export function ExpenseBreakdown({ scenario, className = '' }: ExpenseBreakdownProps) {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  
  const expenseData = getExpenseComparison(scenario.location, scenario.housing, scenario.schoolType)
  const totalCurrent = Object.values(expenseData).reduce((sum, cat) => sum + cat.current, 0)
  const totalSF = Object.values(expenseData).reduce((sum, cat) => sum + cat.sf, 0)
  const totalSD = Object.values(expenseData).reduce((sum, cat) => sum + cat.sd, 0)
  const totalMN = Object.values(expenseData).reduce((sum, cat) => sum + cat.mn, 0)

  const getChangeIndicator = (current: number, comparison: number) => {
    const diff = current - comparison
    const percentChange = Math.abs(diff / comparison * 100)
    
    if (Math.abs(diff) < 100) return <Minus className="h-3 w-3 text-gray-500" />
    if (diff > 0) return <TrendingUp className="h-3 w-3 text-red-500" />
    return <TrendingDown className="h-3 w-3 text-green-500" />
  }

  const getChangeBadge = (current: number, comparison: number, label: string) => {
    const diff = current - comparison
    const percentChange = Math.abs(diff / comparison * 100)
    
    if (Math.abs(diff) < 100) return null
    
    return (
      <Badge 
        variant={diff > 0 ? "destructive" : "default"} 
        className="text-xs"
      >
        {diff > 0 ? '+' : ''}{formatCurrency(diff)} vs {label}
      </Badge>
    )
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Home className="h-5 w-5 mr-2" />
            Expense Impact Analysis
          </CardTitle>
          <CardDescription>
            See how your location, housing, and education choices affect each expense category
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2 mb-4">
            <Badge variant="outline" className="flex items-center">
              <MapPin className="h-3 w-3 mr-1" />
              {scenario.location}
            </Badge>
            <Badge variant="outline">{scenario.housing}</Badge>
            <Badge variant="outline">{scenario.schoolType}</Badge>
            <Badge variant="outline">{scenario.spouse1Status}/{scenario.spouse2Status}</Badge>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">
                {formatCurrency(totalCurrent)}
              </div>
              <div className="text-sm text-muted-foreground">Current Total</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-blue-600">
                {formatCurrency(totalSF)}
              </div>
              <div className="text-sm text-muted-foreground">San Francisco</div>
              {getChangeBadge(totalCurrent, totalSF, 'SF')}
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-green-600">
                {formatCurrency(totalSD)}
              </div>
              <div className="text-sm text-muted-foreground">San Diego</div>
              {getChangeBadge(totalCurrent, totalSD, 'SD')}
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-purple-600">
                {formatCurrency(totalMN)}
              </div>
              <div className="text-sm text-muted-foreground">Minnesota</div>
              {getChangeBadge(totalCurrent, totalMN, 'MN')}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Category Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Category Details</CardTitle>
          <CardDescription>
            Click on a category to see detailed breakdown
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Object.entries(expenseData).map(([categoryName, data]) => (
              <div 
                key={categoryName}
                className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                  selectedCategory === categoryName ? 'border-primary bg-primary/5' : 'border-border hover:bg-muted/50'
                }`}
                onClick={() => setSelectedCategory(selectedCategory === categoryName ? null : categoryName)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-lg ${data.color} text-white`}>
                      {data.icon}
                    </div>
                    <div>
                      <div className="font-medium">{categoryName}</div>
                      <div className="text-sm text-muted-foreground">
                        {formatCurrency(data.current)} annually
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Progress 
                      value={(data.current / totalCurrent) * 100} 
                      className="w-20 h-2"
                    />
                    <span className="text-sm text-muted-foreground w-12">
                      {((data.current / totalCurrent) * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>

                {selectedCategory === categoryName && (
                  <div className="mt-4 pt-4 border-t">
                    <div className="grid grid-cols-3 gap-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm">San Francisco</span>
                        <div className="flex items-center space-x-2">
                          {getChangeIndicator(data.sf, data.current)}
                          <span className="font-medium">{formatCurrency(data.sf)}</span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">San Diego</span>
                        <div className="flex items-center space-x-2">
                          {getChangeIndicator(data.sd, data.current)}
                          <span className="font-medium">{formatCurrency(data.sd)}</span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Minnesota</span>
                        <div className="flex items-center space-x-2">
                          {getChangeIndicator(data.mn, data.current)}
                          <span className="font-medium">{formatCurrency(data.mn)}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="mt-3 text-xs text-muted-foreground">
                      {categoryName === 'Housing Expenses' && scenario.housing === 'Rent' && 
                        'Rental costs are typically 60% of ownership costs'}
                      {categoryName === 'Education' && scenario.schoolType === 'Private' && 
                        'Private school costs remain constant across locations'}
                      {categoryName === 'Living Expenses' && 
                        'Includes groceries, clothing, personal care, and household supplies'}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Key Insights */}
      <Card>
        <CardHeader>
          <CardTitle>Key Financial Insights</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
              <div className="font-medium text-blue-900 dark:text-blue-100">Location Impact</div>
              <div className="text-sm text-blue-700 dark:text-blue-300">
                Living in {scenario.location} {
                  scenario.location === 'Sf' ? 'increases total expenses by ~40% due to high housing and living costs' :
                  scenario.location === 'Sd' ? 'increases expenses by ~20% with moderate cost of living' :
                  'reduces expenses by ~15% with lower cost of living'
                }
              </div>
            </div>
            
            <div className="p-3 bg-green-50 dark:bg-green-950/20 rounded-lg">
              <div className="font-medium text-green-900 dark:text-green-100">Housing Choice</div>
              <div className="text-sm text-green-700 dark:text-green-300">
                {scenario.housing === 'Own' ? 
                  'Homeownership includes property tax, maintenance, and mortgage payments' :
                  'Renting reduces housing costs by ~40% but provides less equity building'}
              </div>
            </div>
            
            <div className="p-3 bg-purple-50 dark:bg-purple-950/20 rounded-lg">
              <div className="font-medium text-purple-900 dark:text-purple-100">Education Strategy</div>
              <div className="text-sm text-purple-700 dark:text-purple-300">
                {scenario.schoolType === 'Private' ? 
                  'Private education adds ~$124K annually but remains constant across locations' :
                  scenario.schoolType === 'Pripub' ?
                  'Mixed approach saves ~$62K annually compared to full private' :
                  'Public education saves ~$74K annually compared to private'}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}