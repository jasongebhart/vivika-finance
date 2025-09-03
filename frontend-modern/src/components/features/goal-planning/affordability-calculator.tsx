'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Slider } from '@/components/ui/slider'
import { Progress } from '@/components/ui/progress'
import { 
  Calculator, 
  Home, 
  Car, 
  GraduationCap, 
  Target,
  Calendar,
  DollarSign,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Clock
} from 'lucide-react'
import { formatCurrency } from '@/lib/utils'

interface FinancialState {
  monthlyIncome: number
  monthlyExpenses: number
  monthlySurplus: number
  liquidSavings: number
  investments: number
  totalAssets: number
  monthlyGrowth: number
  annualGrowthRate: number
}

interface GoalType {
  id: string
  name: string
  icon: React.ReactNode
  color: string
  defaultAmount: number
  description: string
  considerations: string[]
}

interface AffordabilityCalculatorProps {
  financialState: FinancialState
  className?: string
}

const goalTypes: GoalType[] = [
  {
    id: 'house',
    name: 'Home Purchase',
    icon: <Home className="h-5 w-5" />,
    color: 'bg-blue-500',
    defaultAmount: 800000,
    description: 'Down payment + closing costs',
    considerations: [
      'Down payment typically 10-20% of home value',
      'Closing costs are usually 2-3% of purchase price',
      'Consider monthly mortgage payments in budget',
      'Property taxes and maintenance costs'
    ]
  },
  {
    id: 'car',
    name: 'Vehicle Purchase',
    icon: <Car className="h-5 w-5" />,
    color: 'bg-green-500',
    defaultAmount: 50000,
    description: 'Full purchase price or down payment',
    considerations: [
      'Consider total cost of ownership',
      'Insurance, maintenance, and fuel costs',
      'Depreciation affects resale value',
      'Financing vs cash purchase trade-offs'
    ]
  },
  {
    id: 'education',
    name: 'Education Expenses',
    icon: <GraduationCap className="h-5 w-5" />,
    color: 'bg-purple-500',
    defaultAmount: 200000,
    description: 'College tuition and expenses',
    considerations: [
      'Education costs inflate at ~5% annually',
      'Consider 529 plan tax advantages',
      'Public vs private school cost differences',
      'Room, board, and living expenses'
    ]
  },
  {
    id: 'emergency',
    name: 'Emergency Fund',
    icon: <Target className="h-5 w-5" />,
    color: 'bg-orange-500',
    defaultAmount: 50000,
    description: '6-12 months of expenses',
    considerations: [
      'Should cover 6-12 months of expenses',
      'Keep in high-yield savings account',
      'Adjust based on job security',
      'Separate from other investments'
    ]
  }
]

export function AffordabilityCalculator({ financialState, className = '' }: AffordabilityCalculatorProps) {
  const [selectedGoal, setSelectedGoal] = useState<GoalType>(goalTypes[0])
  const [goalAmount, setGoalAmount] = useState(goalTypes[0].defaultAmount)
  const [downPaymentPercent, setDownPaymentPercent] = useState(20)
  const [timelineYears, setTimelineYears] = useState(5)
  
  // Calculate affordability metrics
  const calculateAffordability = () => {
    const targetAmount = selectedGoal.id === 'house' 
      ? goalAmount * (downPaymentPercent / 100) + (goalAmount * 0.03) // Down payment + closing costs
      : goalAmount
    
    // Current liquid assets available
    const availableNow = financialState.liquidSavings
    
    // Amount that can be saved monthly
    const monthlySavingsCapacity = financialState.monthlySurplus * 0.8 // Use 80% of surplus for goals
    
    // Amount needed beyond current assets
    const amountNeeded = Math.max(0, targetAmount - availableNow)
    
    // Time to save needed amount
    const monthsToSave = amountNeeded > 0 ? Math.ceil(amountNeeded / monthlySavingsCapacity) : 0
    const yearsToSave = monthsToSave / 12
    
    // With investment growth
    const monthlyReturn = financialState.annualGrowthRate / 12
    let monthsToSaveWithGrowth = 0
    
    if (amountNeeded > 0 && monthlySavingsCapacity > 0) {
      // Future value of current assets
      const futureValueCurrent = availableNow * Math.pow(1 + monthlyReturn, timelineYears * 12)
      const remainingNeeded = Math.max(0, targetAmount - futureValueCurrent)
      
      if (remainingNeeded > 0) {
        // PMT calculation for annuity
        if (monthlyReturn > 0) {
          monthsToSaveWithGrowth = Math.log(1 + (remainingNeeded * monthlyReturn) / monthlySavingsCapacity) / Math.log(1 + monthlyReturn)
        } else {
          monthsToSaveWithGrowth = remainingNeeded / monthlySavingsCapacity
        }
      }
    }
    
    const yearsToSaveWithGrowth = monthsToSaveWithGrowth / 12
    
    // Affordability assessment
    const canAffordNow = availableNow >= targetAmount
    const canAffordIn1Year = (availableNow + monthlySavingsCapacity * 12) >= targetAmount
    const canAffordIn5Years = yearsToSaveWithGrowth <= 5
    
    return {
      targetAmount,
      availableNow,
      amountNeeded,
      monthlySavingsCapacity,
      monthsToSave,
      yearsToSave,
      yearsToSaveWithGrowth,
      canAffordNow,
      canAffordIn1Year,
      canAffordIn5Years,
      progressPercent: Math.min(100, (availableNow / targetAmount) * 100)
    }
  }
  
  const results = calculateAffordability()
  
  const getAffordabilityStatus = () => {
    if (results.canAffordNow) {
      return { status: 'now', color: 'text-green-600', icon: <CheckCircle className="h-5 w-5" />, message: 'You can afford this now!' }
    } else if (results.canAffordIn1Year) {
      return { status: 'soon', color: 'text-blue-600', icon: <Clock className="h-5 w-5" />, message: 'Affordable within 1 year' }
    } else if (results.canAffordIn5Years) {
      return { status: 'future', color: 'text-yellow-600', icon: <Calendar className="h-5 w-5" />, message: 'Achievable with planning' }
    } else {
      return { status: 'difficult', color: 'text-red-600', icon: <AlertCircle className="h-5 w-5" />, message: 'Requires significant planning' }
    }
  }
  
  const affordabilityStatus = getAffordabilityStatus()
  
  useEffect(() => {
    setGoalAmount(selectedGoal.defaultAmount)
  }, [selectedGoal])
  
  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Calculator className="h-5 w-5 mr-2" />
            Affordability Calculator
          </CardTitle>
          <CardDescription>
            Find out when you can afford your financial goals
          </CardDescription>
        </CardHeader>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Goal Configuration */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">What do you want to afford?</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Goal Type Selection */}
            <div>
              <Label className="text-sm font-medium mb-3 block">Goal Type</Label>
              <div className="grid grid-cols-2 gap-3">
                {goalTypes.map((goal) => (
                  <Button
                    key={goal.id}
                    variant={selectedGoal.id === goal.id ? 'default' : 'outline'}
                    onClick={() => setSelectedGoal(goal)}
                    className="h-auto p-3 flex flex-col items-center"
                  >
                    <div className={`p-2 rounded-lg ${goal.color} text-white mb-1`}>
                      {goal.icon}
                    </div>
                    <span className="text-xs">{goal.name}</span>
                  </Button>
                ))}
              </div>
            </div>

            {/* Goal Amount */}
            <div>
              <Label htmlFor="goalAmount" className="text-sm font-medium">
                {selectedGoal.name} Amount
              </Label>
              <Input
                id="goalAmount"
                type="number"
                value={goalAmount}
                onChange={(e) => setGoalAmount(Number(e.target.value))}
                className="mt-1"
                min="1000"
                step="1000"
              />
              <div className="text-xs text-muted-foreground mt-1">
                {selectedGoal.description}
              </div>
            </div>

            {/* Down Payment Percentage (for house) */}
            {selectedGoal.id === 'house' && (
              <div>
                <Label className="text-sm font-medium mb-2 block">
                  Down Payment: {downPaymentPercent}%
                </Label>
                <Slider
                  value={[downPaymentPercent]}
                  onValueChange={([value]) => setDownPaymentPercent(value)}
                  min={5}
                  max={30}
                  step={1}
                  className="w-full"
                />
                <div className="text-xs text-muted-foreground mt-1">
                  {formatCurrency(goalAmount * (downPaymentPercent / 100))} down payment + {formatCurrency(goalAmount * 0.03)} closing costs
                </div>
              </div>
            )}

            {/* Timeline Preference */}
            <div>
              <Label className="text-sm font-medium mb-2 block">
                Target Timeline: {timelineYears} years
              </Label>
              <Slider
                value={[timelineYears]}
                onValueChange={([value]) => setTimelineYears(value)}
                min={1}
                max={10}
                step={1}
                className="w-full"
              />
            </div>
          </CardContent>
        </Card>

        {/* Results */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Affordability Analysis</span>
              <div className={`flex items-center space-x-2 ${affordabilityStatus.color}`}>
                {affordabilityStatus.icon}
                <span className="font-medium text-sm">{affordabilityStatus.status}</span>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Progress to Goal */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Progress to Goal</span>
                <span className="text-sm text-muted-foreground">
                  {results.progressPercent.toFixed(0)}%
                </span>
              </div>
              <Progress value={results.progressPercent} className="mb-2" />
              <div className="flex justify-between text-sm text-muted-foreground">
                <span>{formatCurrency(results.availableNow)} available</span>
                <span>{formatCurrency(results.targetAmount)} needed</span>
              </div>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-3 bg-muted rounded-lg">
                <div className="text-lg font-bold text-primary">
                  {formatCurrency(results.amountNeeded)}
                </div>
                <div className="text-sm text-muted-foreground">Still Needed</div>
              </div>
              <div className="text-center p-3 bg-muted rounded-lg">
                <div className="text-lg font-bold text-green-600">
                  {formatCurrency(results.monthlySavingsCapacity)}
                </div>
                <div className="text-sm text-muted-foreground">Monthly Capacity</div>
              </div>
            </div>

            {/* Timeline Analysis */}
            <div className="space-y-3">
              <div className="text-sm font-medium">Timeline Options:</div>
              
              <div className="p-3 border rounded-lg">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Without Investment Growth</span>
                  <Badge variant="outline">
                    {results.yearsToSave > 0 ? `${results.yearsToSave.toFixed(1)} years` : 'Now'}
                  </Badge>
                </div>
              </div>
              
              <div className="p-3 border rounded-lg">
                <div className="flex items-center justify-between">
                  <span className="text-sm">With Investment Growth</span>
                  <Badge variant="default">
                    {results.yearsToSaveWithGrowth > 0 ? `${results.yearsToSaveWithGrowth.toFixed(1)} years` : 'Now'}
                  </Badge>
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  Assuming {(financialState.annualGrowthRate * 100).toFixed(1)}% annual return
                </div>
              </div>
            </div>

            {/* Status Message */}
            <div className={`p-4 rounded-lg ${
              affordabilityStatus.status === 'now' ? 'bg-green-50 dark:bg-green-950/20' :
              affordabilityStatus.status === 'soon' ? 'bg-blue-50 dark:bg-blue-950/20' :
              affordabilityStatus.status === 'future' ? 'bg-yellow-50 dark:bg-yellow-950/20' :
              'bg-red-50 dark:bg-red-950/20'
            }`}>
              <div className={`font-medium ${affordabilityStatus.color} mb-1`}>
                {affordabilityStatus.message}
              </div>
              <div className="text-sm text-muted-foreground">
                {results.canAffordNow 
                  ? `You have ${formatCurrency(results.availableNow)} available now.`
                  : `Save ${formatCurrency(results.monthlySavingsCapacity)}/month to reach your goal.`
                }
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Considerations */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Important Considerations</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-2">
            {selectedGoal.considerations.map((consideration, index) => (
              <div key={index} className="flex items-start space-x-2">
                <div className="h-1.5 w-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                <span className="text-sm text-muted-foreground">{consideration}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}