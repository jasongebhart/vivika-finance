'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  ChevronDown,
  ChevronRight,
  Calendar,
  TrendingUp,
  Calculator,
  Home,
  Car,
  GraduationCap,
  Heart,
  Plane,
  Zap,
  Shield,
  CreditCard,
  Activity,
  Edit3,
  Save,
  X
} from 'lucide-react'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { YearRangeControl } from '@/components/ui/year-range-control'
import { formatCurrency, formatPercentage } from '@/lib/utils'

interface DetailedExpense {
  name: string
  annual_amount: number
  start_age?: number
  end_age?: number
  inflation_adjusted?: boolean
  line_items?: Record<string, number>
}

interface ExpenseGroup {
  category: string
  items: DetailedExpense[]
  totalAmount: number
  icon: React.ReactNode
  color: string
}

interface DetailedExpenseBreakdownProps {
  expenses: DetailedExpense[]
  totalAnnualExpenses: number
  yearRange?: number
  startYear?: number
  currentAge?: number
  className?: string
  onYearRangeChange?: (years: number) => void
  onStartYearChange?: (year: number) => void
  showYearControls?: boolean
}

// Function to categorize expenses into logical groups
const categorizeExpenses = (expenses: DetailedExpense[]): ExpenseGroup[] => {
  const groups: Record<string, DetailedExpense[]> = {
    'Housing & Home': [],
    'Education': [],
    'Activities & Sports': [],
    'Transportation': [],
    'Healthcare & Insurance': [],
    'Travel & Vacation': [],
    'Utilities & Services': [],
    'General Living': [],
    'Other': []
  }

  expenses.forEach(expense => {
    const name = expense.name.toLowerCase()
    
    if (name.includes('housing') || name.includes('property') || name.includes('rent') || name.includes('mortgage')) {
      groups['Housing & Home'].push(expense)
    } else if (name.includes('school') || name.includes('college') || name.includes('education') || name.includes('tuition')) {
      groups['Education'].push(expense)
    } else if (name.includes('ski') || name.includes('baseball') || name.includes('sports') || name.includes('activities') || name.includes('team')) {
      groups['Activities & Sports'].push(expense)
    } else if (name.includes('transport') || name.includes('car') || name.includes('vehicle') || name.includes('gas') || name.includes('fuel')) {
      groups['Transportation'].push(expense)
    } else if (name.includes('health') || name.includes('medical') || name.includes('insurance') || name.includes('dental')) {
      groups['Healthcare & Insurance'].push(expense)
    } else if (name.includes('travel') || name.includes('vacation') || name.includes('trip')) {
      groups['Travel & Vacation'].push(expense)
    } else if (name.includes('utilities') || name.includes('electric') || name.includes('water') || name.includes('subscription')) {
      groups['Utilities & Services'].push(expense)
    } else if (name.includes('living') || name.includes('food') || name.includes('grocery')) {
      groups['General Living'].push(expense)
    } else {
      groups['Other'].push(expense)
    }
  })

  // Convert to ExpenseGroup format and filter out empty groups
  const result: ExpenseGroup[] = []
  
  Object.entries(groups).forEach(([category, items]) => {
    if (items.length > 0) {
      const totalAmount = items.reduce((sum, item) => sum + item.annual_amount, 0)
      
      let icon: React.ReactNode
      let color: string
      
      switch (category) {
        case 'Housing & Home':
          icon = <Home className="h-5 w-5" />
          color = 'bg-blue-500'
          break
        case 'Education':
          icon = <GraduationCap className="h-5 w-5" />
          color = 'bg-purple-500'
          break
        case 'Activities & Sports':
          icon = <Activity className="h-5 w-5" />
          color = 'bg-green-500'
          break
        case 'Transportation':
          icon = <Car className="h-5 w-5" />
          color = 'bg-orange-500'
          break
        case 'Healthcare & Insurance':
          icon = <Heart className="h-5 w-5" />
          color = 'bg-red-500'
          break
        case 'Travel & Vacation':
          icon = <Plane className="h-5 w-5" />
          color = 'bg-cyan-500'
          break
        case 'Utilities & Services':
          icon = <Zap className="h-5 w-5" />
          color = 'bg-yellow-500'
          break
        case 'General Living':
          icon = <CreditCard className="h-5 w-5" />
          color = 'bg-indigo-500'
          break
        default:
          icon = <Calculator className="h-5 w-5" />
          color = 'bg-gray-500'
      }
      
      result.push({
        category,
        items,
        totalAmount,
        icon,
        color
      })
    }
  })

  // Sort by total amount (highest first)
  return result.sort((a, b) => b.totalAmount - a.totalAmount)
}

function ExpenseItemDetail({ 
  expense, 
  isLast, 
  yearRange, 
  startYear, 
  currentAge 
}: { 
  expense: DetailedExpense; 
  isLast: boolean;
  yearRange?: number;
  startYear?: number;
  currentAge?: number;
}) {
  const [expanded, setExpanded] = useState(false)
  const [editing, setEditing] = useState(false)
  const [editedLineItems, setEditedLineItems] = useState<Record<string, number>>(expense.line_items || {})
  
  // Debug logging
  console.log(`Expense: ${expense.name}, has line_items:`, !!expense.line_items, expense.line_items)
  
  // Calculate some additional metrics
  const monthlyAmount = expense.annual_amount / 12
  const isTimeLimited = expense.start_age !== undefined || expense.end_age !== undefined
  const duration = expense.end_age && expense.start_age ? expense.end_age - expense.start_age : null
  
  // Check if expense is within the selected year range
  const isInYearRange = (() => {
    if (!yearRange || !startYear || !currentAge) return true
    
    const endYear = startYear + yearRange - 1
    const currentYear = new Date().getFullYear()
    
    // If expense has age limits, check if they overlap with the year range
    if (expense.start_age !== undefined || expense.end_age !== undefined) {
      const expenseStartYear = expense.start_age ? currentYear + (expense.start_age - currentAge) : startYear
      const expenseEndYear = expense.end_age ? currentYear + (expense.end_age - currentAge) : endYear
      
      return expenseStartYear <= endYear && expenseEndYear >= startYear
    }
    
    return true // No age limits, so it applies to all years
  })()
  
  const handleSaveLineItems = () => {
    // Here you would typically save to backend
    console.log('Saving line items:', editedLineItems)
    // For now, just update the local state
    expense.line_items = editedLineItems
    setEditing(false)
  }
  
  const handleCancelEdit = () => {
    setEditedLineItems(expense.line_items || {})
    setEditing(false)
  }
  
  const handleLineItemChange = (itemName: string, value: string) => {
    const numValue = parseFloat(value) || 0
    setEditedLineItems(prev => ({
      ...prev,
      [itemName]: numValue
    }))
  }
  
  // Don't render if not in year range
  if (!isInYearRange) {
    return null
  }

  return (
    <div className={`${!isLast ? 'border-b border-border' : ''} py-2`}>
      <div className="flex items-center justify-between hover:bg-muted/30 rounded px-2 py-1">
        <div className="flex-1">
          <div className="flex items-center justify-between mb-0.5">
            <span className="font-medium text-sm text-foreground">{expense.name}</span>
            <span className="font-semibold text-base">{formatCurrency(expense.annual_amount)}</span>
          </div>
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>{formatCurrency(monthlyAmount)}/mo</span>
            <div className="flex items-center space-x-2">
              {isTimeLimited && (
                <span className="flex items-center">
                  <Calendar className="h-3 w-3 mr-0.5" />
                  {expense.start_age && expense.end_age 
                    ? `Ages ${expense.start_age}-${expense.end_age}` 
                    : expense.start_age 
                    ? `From ${expense.start_age}` 
                    : expense.end_age 
                    ? `Until ${expense.end_age}` 
                    : ''}
                </span>
              )}
              {expense.inflation_adjusted && (
                <span className="flex items-center text-green-600">
                  <TrendingUp className="h-3 w-3 mr-0.5" />
                  <span className="text-xs">Adj</span>
                </span>
              )}
            </div>
          </div>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setExpanded(!expanded)}
          className="ml-2 h-6 w-6 p-0"
        >
          {expanded ? (
            <ChevronDown className="h-3 w-3" />
          ) : (
            <ChevronRight className="h-3 w-3" />
          )}
        </Button>
      </div>
      
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="mt-2 p-2 bg-muted/50 rounded-md mx-2"
          >
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">Monthly Cost:</span>
                <div className="font-medium">{formatCurrency(monthlyAmount)}</div>
              </div>
              <div>
                <span className="text-muted-foreground">Annual Cost:</span>
                <div className="font-medium">{formatCurrency(expense.annual_amount)}</div>
              </div>
              {expense.start_age && (
                <div>
                  <span className="text-muted-foreground">Start Age:</span>
                  <div className="font-medium">{expense.start_age}</div>
                </div>
              )}
              {expense.end_age && (
                <div>
                  <span className="text-muted-foreground">End Age:</span>
                  <div className="font-medium">{expense.end_age}</div>
                </div>
              )}
              <div>
                <span className="text-muted-foreground">Inflation Adjusted:</span>
                <div className="font-medium">{expense.inflation_adjusted ? 'Yes' : 'No'}</div>
              </div>
              {duration && (
                <div>
                  <span className="text-muted-foreground">Duration:</span>
                  <div className="font-medium">{duration} years</div>
                </div>
              )}
            </div>
            
            {expense.line_items && Object.keys(expense.line_items).length > 0 && (
              <div className="mt-3 pt-3 border-t border-border">
                <div className="flex items-center justify-between mb-3">
                  <div className="text-sm font-semibold text-foreground">💡 Line Item Breakdown</div>
                  <div className="flex items-center space-x-2">
                    {editing ? (
                      <>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={handleSaveLineItems}
                          className="h-7 px-2"
                        >
                          <Save className="h-3 w-3 mr-1" />
                          Save
                        </Button>
                        <Button 
                          size="sm" 
                          variant="ghost"
                          onClick={handleCancelEdit}
                          className="h-7 px-2"
                        >
                          <X className="h-3 w-3 mr-1" />
                          Cancel
                        </Button>
                      </>
                    ) : (
                      <Button 
                        size="sm" 
                        variant="ghost"
                        onClick={() => setEditing(true)}
                        className="h-7 px-2"
                      >
                        <Edit3 className="h-3 w-3 mr-1" />
                        Edit
                      </Button>
                    )}
                  </div>
                </div>
                <div className="space-y-2 bg-muted/50 p-3 rounded-md">
                  {Object.entries(editing ? editedLineItems : expense.line_items).map(([itemName, amount]) => (
                    <div key={itemName} className="flex justify-between items-center">
                      <span className="text-sm capitalize font-medium">
                        {itemName.replace(/_/g, ' ')}
                      </span>
                      {editing ? (
                        <div className="flex items-center space-x-2">
                          <Input
                            type="number"
                            step="0.01"
                            value={amount}
                            onChange={(e) => handleLineItemChange(itemName, e.target.value)}
                            className="h-7 w-20 text-right text-sm"
                          />
                          <span className="text-sm text-muted-foreground">/month</span>
                        </div>
                      ) : (
                        <span className="text-sm font-semibold text-primary">
                          {formatCurrency(amount)}/month
                        </span>
                      )}
                    </div>
                  ))}
                  <div className="pt-2 mt-2 border-t border-border">
                    <div className="flex justify-between items-center font-semibold">
                      <span className="text-sm">Monthly Total:</span>
                      <span className="text-sm text-primary">
                        {formatCurrency(Object.values(editing ? editedLineItems : expense.line_items).reduce((sum, amount) => sum + amount, 0))}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {(!expense.line_items || Object.keys(expense.line_items).length === 0) && (
              <div className="mt-3 pt-3 border-t border-border">
                <div className="text-sm text-muted-foreground italic">
                  No detailed breakdown available for this expense category.
                </div>
              </div>
            )}

            {expense.inflation_adjusted && (
              <div className="mt-3 pt-3 border-t border-border">
                <div className="text-sm text-muted-foreground mb-2">10-Year Inflation Impact (3% annual)</div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-xs text-muted-foreground">Future Annual Cost:</span>
                    <div className="font-medium text-orange-600">
                      {formatCurrency(expense.annual_amount * Math.pow(1.03, 10))}
                    </div>
                  </div>
                  <div>
                    <span className="text-xs text-muted-foreground">Total Increase:</span>
                    <div className="font-medium text-orange-600">
                      +{formatCurrency(expense.annual_amount * Math.pow(1.03, 10) - expense.annual_amount)}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

function ExpenseGroupCard({ 
  group, 
  totalExpenses, 
  yearRange, 
  startYear, 
  currentAge 
}: { 
  group: ExpenseGroup; 
  totalExpenses: number;
  yearRange?: number;
  startYear?: number;
  currentAge?: number;
}) {
  const [expanded, setExpanded] = useState(false)
  const percentage = (group.totalAmount / totalExpenses) * 100
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="hover:shadow-md transition-shadow duration-200 compact-card">
        <CardHeader 
          className="cursor-pointer pb-3 pt-4"
          onClick={() => setExpanded(!expanded)}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className={`p-1.5 rounded-md ${group.color} text-white`}>
                {group.icon}
              </div>
              <div>
                <CardTitle className="text-base font-semibold">{group.category}</CardTitle>
                <CardDescription className="text-xs">
                  {group.items.length} items • {formatPercentage(percentage, 1)} of total
                </CardDescription>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="text-right">
                <div className="text-lg font-bold">{formatCurrency(group.totalAmount)}</div>
                <div className="text-xs text-muted-foreground">
                  {formatCurrency(group.totalAmount / 12)}/mo
                </div>
              </div>
              {expanded ? (
                <ChevronDown className="h-4 w-4 text-muted-foreground" />
              ) : (
                <ChevronRight className="h-4 w-4 text-muted-foreground" />
              )}
            </div>
          </div>
        </CardHeader>
        
        <AnimatePresence>
          {expanded && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
            >
              <CardContent className="pt-0">
                <div className="space-y-1">
                  {group.items.map((expense, index) => (
                    <ExpenseItemDetail
                      key={expense.name}
                      expense={expense}
                      isLast={index === group.items.length - 1}
                      yearRange={yearRange}
                      startYear={startYear}
                      currentAge={currentAge}
                    />
                  ))}
                </div>
              </CardContent>
            </motion.div>
          )}
        </AnimatePresence>
      </Card>
    </motion.div>
  )
}

export function DetailedExpenseBreakdown({ 
  expenses, 
  totalAnnualExpenses, 
  yearRange = 5,
  startYear = new Date().getFullYear(),
  currentAge,
  className = '',
  onYearRangeChange,
  onStartYearChange,
  showYearControls = true
}: DetailedExpenseBreakdownProps) {
  // Local state for year controls if not controlled externally
  const [localYearRange, setLocalYearRange] = useState(yearRange)
  const [localStartYear, setLocalStartYear] = useState(startYear)
  
  // Use local or external state
  const effectiveYearRange = onYearRangeChange ? yearRange : localYearRange
  const effectiveStartYear = onStartYearChange ? startYear : localStartYear
  
  const handleYearRangeChange = (years: number) => {
    if (onYearRangeChange) {
      onYearRangeChange(years)
    } else {
      setLocalYearRange(years)
    }
  }
  
  const handleStartYearChange = (year: number) => {
    if (onStartYearChange) {
      onStartYearChange(year)
    } else {
      setLocalStartYear(year)
    }
  }
  // Debug logging
  console.log('DetailedExpenseBreakdown: Received expenses:', expenses)
  console.log('DetailedExpenseBreakdown: Expenses with line_items:', expenses.filter(e => e.line_items))
  
  // Update local state when props change
  useEffect(() => {
    setLocalYearRange(yearRange)
    setLocalStartYear(startYear)
  }, [yearRange, startYear])
  
  const expenseGroups = categorizeExpenses(expenses)
  
  if (expenses.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>Detailed Expense Breakdown</CardTitle>
          <CardDescription>No expense data available</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Detailed Expense Breakdown</CardTitle>
            <CardDescription>
              Click on any category to see individual expense items and details
            </CardDescription>
          </div>
          {showYearControls && (
            <YearRangeControl
              value={effectiveYearRange}
              onChange={handleYearRangeChange}
              startYear={effectiveStartYear}
              onStartYearChange={handleStartYearChange}
              compact={true}
              className="flex-shrink-0"
            />
          )}
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-3">
          {expenseGroups.map((group, index) => (
            <ExpenseGroupCard
              key={group.category}
              group={group}
              totalExpenses={totalAnnualExpenses}
              yearRange={effectiveYearRange}
              startYear={effectiveStartYear}
              currentAge={currentAge}
            />
          ))}
        </div>
        
        {/* Summary */}
        <div className="mt-4 pt-4 border-t border-border">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-center">
            <div>
              <div className="text-lg font-bold text-foreground">{expenseGroups.length}</div>
              <div className="text-xs text-muted-foreground">Categories</div>
            </div>
            <div>
              <div className="text-lg font-bold text-foreground">{expenses.length}</div>
              <div className="text-xs text-muted-foreground">Total Items</div>
            </div>
            <div>
              <div className="text-lg font-bold text-foreground">
                {formatCurrency(totalAnnualExpenses)}
              </div>
              <div className="text-xs text-muted-foreground">Annual Total</div>
            </div>
            <div>
              <div className="text-lg font-bold text-foreground">
                {formatCurrency(totalAnnualExpenses / 12)}
              </div>
              <div className="text-xs text-muted-foreground">Monthly Average</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}