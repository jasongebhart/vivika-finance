'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  Target, 
  TrendingUp, 
  Calendar, 
  DollarSign,
  AlertTriangle,
  CheckCircle,
  Clock,
  PiggyBank
} from 'lucide-react'
import { formatCurrency } from '@/lib/utils'

interface RetirementFeasibilityProps {
  scenarioName: string
  results: {
    final_net_worth: number
    annual_growth_rate: number
    total_expenses: number
    retirement_readiness: boolean
    calculated_at: string
  }
  parameters: {
    location: string
    housing: string
    schoolType: string
    spouse1Status: string
    spouse2Status: string
  }
  className?: string
}

export function RetirementFeasibility({ 
  scenarioName, 
  results, 
  parameters, 
  className = '' 
}: RetirementFeasibilityProps) {
  
  // Retirement analysis calculations
  const currentAge = 52 // Based on existing data
  const retirementAge = 65
  const lifeExpectancy = 90
  const yearsToRetirement = retirementAge - currentAge
  const yearsInRetirement = lifeExpectancy - retirementAge
  
  // Current annual expenses (estimated)
  const currentAnnualExpenses = 180000
  const retirementExpenseRatio = 0.8 // 80% of current expenses in retirement
  const retirementAnnualExpenses = currentAnnualExpenses * retirementExpenseRatio
  
  // Calculate retirement needs
  const totalRetirementNeeds = retirementAnnualExpenses * yearsInRetirement
  const safeWithdrawalRate = 0.04 // 4% rule
  const requiredRetirementFund = retirementAnnualExpenses / safeWithdrawalRate
  
  // Calculate shortfall/surplus
  const shortfall = Math.max(0, requiredRetirementFund - results.final_net_worth)
  const surplus = Math.max(0, results.final_net_worth - requiredRetirementFund)
  
  // Calculate annual savings needed if shortfall
  const additionalAnnualSavingsNeeded = shortfall > 0 ? 
    shortfall / ((Math.pow(1 + results.annual_growth_rate, yearsToRetirement) - 1) / results.annual_growth_rate) : 0
  
  // Calculate retirement income from portfolio
  const projectedRetirementIncome = results.final_net_worth * safeWithdrawalRate
  const incomeReplacementRatio = projectedRetirementIncome / currentAnnualExpenses
  
  // Years of expenses covered
  const yearsCovered = results.final_net_worth / retirementAnnualExpenses
  
  const getReadinessStatus = () => {
    if (incomeReplacementRatio >= 0.8) return { status: 'excellent', color: 'text-green-600', icon: <CheckCircle className="h-5 w-5" /> }
    if (incomeReplacementRatio >= 0.6) return { status: 'good', color: 'text-blue-600', icon: <Target className="h-5 w-5" /> }
    if (incomeReplacementRatio >= 0.4) return { status: 'fair', color: 'text-yellow-600', icon: <Clock className="h-5 w-5" /> }
    return { status: 'needs improvement', color: 'text-red-600', icon: <AlertTriangle className="h-5 w-5" /> }
  }
  
  const readinessStatus = getReadinessStatus()
  
  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Target className="h-5 w-5 mr-2" />
            Retirement Feasibility Analysis
          </CardTitle>
          <CardDescription>
            Analysis for {scenarioName} • {parameters.location}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <Badge variant="outline">{parameters.housing}</Badge>
            <Badge variant="outline">{parameters.schoolType}</Badge>
            <Badge variant="outline">{parameters.spouse1Status}/{parameters.spouse2Status}</Badge>
          </div>
        </CardContent>
      </Card>

      {/* Retirement Readiness Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Retirement Readiness</span>
            <div className={`flex items-center space-x-2 ${readinessStatus.color}`}>
              {readinessStatus.icon}
              <span className="font-medium capitalize">{readinessStatus.status}</span>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">
                {(incomeReplacementRatio * 100).toFixed(0)}%
              </div>
              <div className="text-sm text-muted-foreground">Income Replacement</div>
              <Progress value={incomeReplacementRatio * 100} className="mt-2" />
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {yearsCovered.toFixed(1)}
              </div>
              <div className="text-sm text-muted-foreground">Years Covered</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {formatCurrency(projectedRetirementIncome)}
              </div>
              <div className="text-sm text-muted-foreground">Annual Income</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {yearsToRetirement}
              </div>
              <div className="text-sm text-muted-foreground">Years to Retire</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Detailed Analysis */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Retirement Timeline */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Calendar className="h-5 w-5 mr-2" />
              Retirement Timeline
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
              <div>
                <div className="font-medium">Current Age</div>
                <div className="text-sm text-muted-foreground">Starting point</div>
              </div>
              <div className="text-xl font-bold text-blue-600">{currentAge}</div>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-orange-50 dark:bg-orange-950/20 rounded-lg">
              <div>
                <div className="font-medium">Retirement Age</div>
                <div className="text-sm text-muted-foreground">Stop working</div>
              </div>
              <div className="text-xl font-bold text-orange-600">{retirementAge}</div>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-purple-50 dark:bg-purple-950/20 rounded-lg">
              <div>
                <div className="font-medium">Life Expectancy</div>
                <div className="text-sm text-muted-foreground">Planning horizon</div>
              </div>
              <div className="text-xl font-bold text-purple-600">{lifeExpectancy}</div>
            </div>
            
            <div className="mt-4 p-3 border rounded-lg">
              <div className="text-sm font-medium mb-2">Key Periods:</div>
              <div className="space-y-1 text-sm text-muted-foreground">
                <div>• {yearsToRetirement} years of saving</div>
                <div>• {yearsInRetirement} years in retirement</div>
                <div>• Need to sustain {formatCurrency(retirementAnnualExpenses)}/year</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Financial Requirements */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <PiggyBank className="h-5 w-5 mr-2" />
              Financial Requirements
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-950/20 rounded-lg">
              <div>
                <div className="font-medium">Required Fund</div>
                <div className="text-sm text-muted-foreground">4% rule target</div>
              </div>
              <div className="text-lg font-bold text-green-600">
                {formatCurrency(requiredRetirementFund)}
              </div>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-primary/10 rounded-lg">
              <div>
                <div className="font-medium">Projected Fund</div>
                <div className="text-sm text-muted-foreground">Your scenario</div>
              </div>
              <div className="text-lg font-bold text-primary">
                {formatCurrency(results.final_net_worth)}
              </div>
            </div>
            
            {shortfall > 0 ? (
              <div className="p-3 bg-red-50 dark:bg-red-950/20 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-red-900 dark:text-red-100">Shortfall</div>
                    <div className="text-sm text-red-700 dark:text-red-300">
                      Additional needed
                    </div>
                  </div>
                  <div className="text-lg font-bold text-red-600">
                    {formatCurrency(shortfall)}
                  </div>
                </div>
                <div className="mt-2 text-sm text-red-700 dark:text-red-300">
                  Need to save additional {formatCurrency(additionalAnnualSavingsNeeded)}/year
                </div>
              </div>
            ) : (
              <div className="p-3 bg-green-50 dark:bg-green-950/20 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-green-900 dark:text-green-100">Surplus</div>
                    <div className="text-sm text-green-700 dark:text-green-300">
                      Above requirement
                    </div>
                  </div>
                  <div className="text-lg font-bold text-green-600">
                    {formatCurrency(surplus)}
                  </div>
                </div>
                <div className="mt-2 text-sm text-green-700 dark:text-green-300">
                  You're on track for a comfortable retirement!
                </div>
              </div>
            )}
            
            <div className="mt-4 p-3 border rounded-lg">
              <div className="text-sm font-medium mb-2">Assumptions:</div>
              <div className="space-y-1 text-sm text-muted-foreground">
                <div>• 4% safe withdrawal rate</div>
                <div>• 80% of current expenses in retirement</div>
                <div>• {(results.annual_growth_rate * 100).toFixed(1)}% annual growth</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <TrendingUp className="h-5 w-5 mr-2" />
            Recommendations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {incomeReplacementRatio >= 0.8 ? (
              <div className="p-4 bg-green-50 dark:bg-green-950/20 rounded-lg">
                <div className="font-medium text-green-900 dark:text-green-100 mb-2">
                  🎉 Excellent Retirement Position
                </div>
                <div className="text-sm text-green-700 dark:text-green-300">
                  You're well-positioned for retirement! Consider maximizing tax-advantaged accounts and exploring early retirement options.
                </div>
              </div>
            ) : shortfall > 0 ? (
              <>
                <div className="p-4 bg-red-50 dark:bg-red-950/20 rounded-lg">
                  <div className="font-medium text-red-900 dark:text-red-100 mb-2">
                    ⚠️ Action Required
                  </div>
                  <div className="text-sm text-red-700 dark:text-red-300">
                    Increase annual savings by {formatCurrency(additionalAnnualSavingsNeeded)} or consider:
                  </div>
                </div>
                <div className="grid gap-3 md:grid-cols-2">
                  <div className="p-3 border rounded-lg">
                    <div className="font-medium mb-1">Extend Working Years</div>
                    <div className="text-sm text-muted-foreground">
                      Working 2-3 additional years could significantly improve outcomes
                    </div>
                  </div>
                  <div className="p-3 border rounded-lg">
                    <div className="font-medium mb-1">Reduce Expenses</div>
                    <div className="text-sm text-muted-foreground">
                      Consider relocating to lower-cost areas in retirement
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
                <div className="font-medium text-blue-900 dark:text-blue-100 mb-2">
                  📈 Good Progress
                </div>
                <div className="text-sm text-blue-700 dark:text-blue-300">
                  You're on a solid path. Consider maximizing employer matches and exploring higher-yield investment options.
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}