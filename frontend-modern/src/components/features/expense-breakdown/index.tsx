'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  PieChart, 
  Home, 
  ShoppingCart, 
  Car, 
  Heart, 
  GraduationCap,
  Coffee,
  ChevronDown,
  ChevronUp,
  TrendingUp,
  Calculator
} from 'lucide-react'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { formatCurrency, formatPercentage } from '@/lib/utils'

interface Expense {
  name: string
  annual_amount: number
  start_age?: number
  end_age?: number
  inflation_adjusted?: boolean
}

interface ExpenseBreakdownProps {
  expenses: Expense[]
  totalAnnualExpenses: number
  className?: string
  showInflationImpact?: boolean
}

// Icon mapping for different expense categories
const getExpenseIcon = (expenseName: string) => {
  const name = expenseName.toLowerCase()
  if (name.includes('housing') || name.includes('home') || name.includes('rent') || name.includes('mortgage')) {
    return <Home className="h-4 w-4" />
  }
  if (name.includes('food') || name.includes('grocery') || name.includes('dining')) {
    return <Coffee className="h-4 w-4" />
  }
  if (name.includes('transport') || name.includes('car') || name.includes('vehicle') || name.includes('gas')) {
    return <Car className="h-4 w-4" />
  }
  if (name.includes('health') || name.includes('medical') || name.includes('insurance')) {
    return <Heart className="h-4 w-4" />
  }
  if (name.includes('education') || name.includes('school') || name.includes('tuition')) {
    return <GraduationCap className="h-4 w-4" />
  }
  if (name.includes('living') || name.includes('general') || name.includes('misc')) {
    return <ShoppingCart className="h-4 w-4" />
  }
  return <Calculator className="h-4 w-4" />
}

// Color scheme for expense categories
const getExpenseColor = (index: number) => {
  const colors = [
    'bg-blue-500', 'bg-green-500', 'bg-yellow-500', 'bg-red-500', 
    'bg-purple-500', 'bg-pink-500', 'bg-indigo-500', 'bg-orange-500',
    'bg-teal-500', 'bg-cyan-500'
  ]
  return colors[index % colors.length]
}

function ExpenseCard({ expense, percentage, index, showInflationImpact }: {
  expense: Expense
  percentage: number
  index: number
  showInflationImpact?: boolean
}) {
  const [expanded, setExpanded] = useState(false)
  
  // Calculate inflation impact over 10 years (example)
  const inflationRate = 0.03 // 3% annual inflation
  const futureValue = expense.inflation_adjusted 
    ? expense.annual_amount * Math.pow(1 + inflationRate, 10)
    : expense.annual_amount

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.1 }}
    >
      <Card className="hover:shadow-lg transition-shadow duration-200">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className={`p-2 rounded-lg ${getExpenseColor(index)} text-white`}>
                {getExpenseIcon(expense.name)}
              </div>
              <div>
                <CardTitle className="text-lg">{expense.name}</CardTitle>
                <CardDescription>
                  {formatPercentage(percentage, 1)} of total expenses
                </CardDescription>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setExpanded(!expanded)}
            >
              {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </Button>
          </div>
        </CardHeader>
        
        <CardContent>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Annual Amount</span>
              <span className="text-xl font-bold">{formatCurrency(expense.annual_amount)}</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Monthly Amount</span>
              <span className="text-lg font-semibold">{formatCurrency(expense.annual_amount / 12)}</span>
            </div>

            <AnimatePresence>
              {expanded && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.2 }}
                  className="space-y-3 pt-3 border-t border-border"
                >
                  {expense.start_age && (
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Start Age</span>
                      <span className="text-sm">{expense.start_age}</span>
                    </div>
                  )}
                  
                  {expense.end_age && (
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">End Age</span>
                      <span className="text-sm">{expense.end_age}</span>
                    </div>
                  )}
                  
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Inflation Adjusted</span>
                    <span className="text-sm">
                      {expense.inflation_adjusted ? (
                        <span className="text-green-600 flex items-center">
                          <TrendingUp className="h-3 w-3 mr-1" />
                          Yes
                        </span>
                      ) : (
                        <span className="text-muted-foreground">No</span>
                      )}
                    </span>
                  </div>

                  {showInflationImpact && expense.inflation_adjusted && (
                    <div className="bg-muted p-3 rounded-lg">
                      <div className="text-sm text-muted-foreground mb-1">10-Year Projection (3% inflation)</div>
                      <div className="flex justify-between">
                        <span className="text-sm">Future Annual Cost</span>
                        <span className="text-sm font-semibold">{formatCurrency(futureValue)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Increase</span>
                        <span className="text-sm text-orange-600">
                          +{formatCurrency(futureValue - expense.annual_amount)}
                        </span>
                      </div>
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

export function ExpenseBreakdown({ 
  expenses, 
  totalAnnualExpenses, 
  className = '',
  showInflationImpact = true 
}: ExpenseBreakdownProps) {
  const [sortBy, setSortBy] = useState<'amount' | 'name' | 'percentage'>('amount')
  
  // Sort expenses based on selected criteria
  const sortedExpenses = [...expenses].sort((a, b) => {
    switch (sortBy) {
      case 'amount':
        return b.annual_amount - a.annual_amount
      case 'name':
        return a.name.localeCompare(b.name)
      case 'percentage':
        return (b.annual_amount / totalAnnualExpenses) - (a.annual_amount / totalAnnualExpenses)
      default:
        return 0
    }
  })

  if (expenses.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>Expense Breakdown</CardTitle>
          <CardDescription>No expense data available</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <PieChart className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground">
              No expense categories found in the current scenario.
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Expense Breakdown</CardTitle>
            <CardDescription>
              Detailed view of expense categories - Total: {formatCurrency(totalAnnualExpenses)}/year
            </CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-muted-foreground">Sort by:</span>
            <select 
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'amount' | 'name' | 'percentage')}
              className="text-sm border rounded px-2 py-1 bg-background"
            >
              <option value="amount">Amount</option>
              <option value="percentage">Percentage</option>
              <option value="name">Name</option>
            </select>
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-4">
          {sortedExpenses.map((expense, index) => {
            const percentage = (expense.annual_amount / totalAnnualExpenses) * 100
            
            return (
              <ExpenseCard
                key={`${expense.name}-${index}`}
                expense={expense}
                percentage={percentage}
                index={index}
                showInflationImpact={showInflationImpact}
              />
            )
          })}
        </div>
        
        {/* Summary Stats */}
        <div className="mt-6 pt-6 border-t border-border">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-foreground">{expenses.length}</div>
              <div className="text-sm text-muted-foreground">Categories</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-foreground">
                {formatCurrency(totalAnnualExpenses / 12)}
              </div>
              <div className="text-sm text-muted-foreground">Monthly Total</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-foreground">
                {expenses.filter(e => e.inflation_adjusted).length}
              </div>
              <div className="text-sm text-muted-foreground">Inflation Adjusted</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-foreground">
                {formatCurrency(Math.max(...expenses.map(e => e.annual_amount)))}
              </div>
              <div className="text-sm text-muted-foreground">Largest Category</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}