'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
// Removed Collapsible import - using simple state-based approach
import { 
  Heart, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  Info,
  ChevronDown,
  ChevronUp,
  DollarSign,
  PiggyBank,
  Shield,
  Target,
  CreditCard,
  BarChart3
} from 'lucide-react'
import { calculateFinancialHealthScore, type FinancialHealthMetrics, type HealthScore } from '@/lib/financial-health-scoring'
import { formatCurrency, formatPercentage } from '@/lib/utils'

interface FinancialHealthScoreProps {
  metrics: FinancialHealthMetrics
  className?: string
}

const categoryIcons = {
  cashFlow: <DollarSign className="h-4 w-4" />,
  netWorth: <BarChart3 className="h-4 w-4" />,
  emergencyFund: <Shield className="h-4 w-4" />,
  growthRate: <TrendingUp className="h-4 w-4" />,
  retirementReadiness: <PiggyBank className="h-4 w-4" />,
  debtToIncome: <CreditCard className="h-4 w-4" />
}

const categoryLabels = {
  cashFlow: 'Cash Flow',
  netWorth: 'Net Worth',
  emergencyFund: 'Emergency Fund',
  growthRate: 'Growth Rate',
  retirementReadiness: 'Retirement',
  debtToIncome: 'Debt Management'
}

function ScoreCircle({ score, size = 'lg' }: { score: number; size?: 'sm' | 'lg' }) {
  const radius = size === 'lg' ? 45 : 30
  const strokeWidth = size === 'lg' ? 8 : 5
  const normalizedRadius = radius - strokeWidth * 2
  const circumference = normalizedRadius * 2 * Math.PI
  const strokeDasharray = `${(score / 100) * circumference} ${circumference}`
  
  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-green-600'
    if (score >= 70) return 'text-blue-600'
    if (score >= 55) return 'text-yellow-600'
    if (score >= 40) return 'text-orange-600'
    return 'text-red-600'
  }
  
  return (
    <div className="relative">
      <svg
        height={radius * 2}
        width={radius * 2}
        className="transform -rotate-90"
      >
        <circle
          stroke="currentColor"
          fill="transparent"
          strokeWidth={strokeWidth}
          r={normalizedRadius}
          cx={radius}
          cy={radius}
          className="text-muted/20"
        />
        <circle
          stroke="currentColor"
          fill="transparent"
          strokeWidth={strokeWidth}
          strokeDasharray={strokeDasharray}
          strokeLinecap="round"
          r={normalizedRadius}
          cx={radius}
          cy={radius}
          className={getScoreColor(score)}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="text-center">
          <div className={`font-bold ${size === 'lg' ? 'text-2xl' : 'text-lg'} ${getScoreColor(score)}`}>
            {score}
          </div>
          {size === 'lg' && (
            <div className="text-xs text-muted-foreground">out of 100</div>
          )}
        </div>
      </div>
    </div>
  )
}

function BreakdownItem({ 
  category, 
  data, 
  isExpanded, 
  onToggle 
}: { 
  category: keyof HealthScore['breakdown']
  data: HealthScore['breakdown'][keyof HealthScore['breakdown']]
  isExpanded: boolean
  onToggle: () => void
}) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
    if (score >= 60) return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
    if (score >= 40) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400'
    return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
  }
  
  return (
    <div className="border rounded-lg">
      <Button 
        variant="ghost" 
        className="w-full justify-between p-4 h-auto rounded-lg"
        onClick={onToggle}
      >
        <div className="flex items-center space-x-3">
          {categoryIcons[category]}
          <div className="text-left">
            <div className="font-medium">{categoryLabels[category]}</div>
            <div className="text-sm text-muted-foreground">
              Weight: {formatPercentage(data.weight, 0)}
            </div>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Badge className={getScoreColor(data.score)}>
            {data.score}/100
          </Badge>
          {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </div>
      </Button>
      {isExpanded && (
        <div className="px-4 pb-4 space-y-2">
          <Progress value={data.score} className="h-2" />
          <p className="text-sm text-muted-foreground">{data.description}</p>
        </div>
      )}
    </div>
  )
}

export function FinancialHealthScore({ metrics, className = '' }: FinancialHealthScoreProps) {
  const [expandedBreakdown, setExpandedBreakdown] = useState<string[]>([])
  const [showFullBreakdown, setShowFullBreakdown] = useState(false)
  
  const healthScore = calculateFinancialHealthScore(metrics)
  
  const toggleBreakdownItem = (category: string) => {
    setExpandedBreakdown(prev => 
      prev.includes(category) 
        ? prev.filter(item => item !== category)
        : [...prev, category]
    )
  }
  
  const getScoreIcon = (category: HealthScore['category']) => {
    switch (category) {
      case 'excellent':
        return <CheckCircle className="h-6 w-6 text-green-600" />
      case 'good':
        return <TrendingUp className="h-6 w-6 text-blue-600" />
      case 'fair':
        return <Info className="h-6 w-6 text-yellow-600" />
      case 'needs_improvement':
        return <AlertTriangle className="h-6 w-6 text-orange-600" />
      case 'critical':
        return <AlertTriangle className="h-6 w-6 text-red-600" />
    }
  }
  
  return (
    <div className={`space-y-6 ${className}`}>
      {/* Main Health Score Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Heart className="h-5 w-5 text-red-500" />
            <span>Financial Health Score</span>
          </CardTitle>
          <CardDescription>
            Comprehensive assessment based on your current financial scenario
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <ScoreCircle score={healthScore.overall} />
              <div>
                <div className="flex items-center space-x-2 mb-2">
                  {getScoreIcon(healthScore.category)}
                  <Badge variant="outline" className={`capitalize ${healthScore.color}`}>
                    {healthScore.category.replace('_', ' ')}
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground max-w-md">
                  {healthScore.description}
                </p>
              </div>
            </div>
            <Button 
              variant="outline" 
              onClick={() => setShowFullBreakdown(!showFullBreakdown)}
            >
              {showFullBreakdown ? 'Hide Details' : 'View Breakdown'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Detailed Breakdown */}
      {showFullBreakdown && (
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Score Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle>Score Breakdown</CardTitle>
              <CardDescription>
                How each financial area contributes to your overall health score
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {Object.entries(healthScore.breakdown).map(([category, data]) => (
                <BreakdownItem
                  key={category}
                  category={category as keyof HealthScore['breakdown']}
                  data={data}
                  isExpanded={expandedBreakdown.includes(category)}
                  onToggle={() => toggleBreakdownItem(category)}
                />
              ))}
            </CardContent>
          </Card>

          {/* Insights and Recommendations */}
          <div className="space-y-6">
            {/* Strengths */}
            {healthScore.strengths.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    <span>Financial Strengths</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {healthScore.strengths.map((strength, index) => (
                      <div key={index} className="flex items-start space-x-2">
                        <div className="h-1.5 w-1.5 rounded-full bg-green-600 mt-2 flex-shrink-0" />
                        <span className="text-sm">{strength}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Concerns */}
            {healthScore.concerns.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <AlertTriangle className="h-5 w-5 text-orange-600" />
                    <span>Areas of Concern</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {healthScore.concerns.map((concern, index) => (
                      <div key={index} className="flex items-start space-x-2">
                        <div className="h-1.5 w-1.5 rounded-full bg-orange-600 mt-2 flex-shrink-0" />
                        <span className="text-sm">{concern}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Recommendations */}
            {healthScore.recommendations.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Target className="h-5 w-5 text-blue-600" />
                    <span>Recommendations</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {healthScore.recommendations.map((recommendation, index) => (
                      <div key={index} className="p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
                        <div className="flex items-start space-x-2">
                          <div className="h-1.5 w-1.5 rounded-full bg-blue-600 mt-2 flex-shrink-0" />
                          <span className="text-sm">{recommendation}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      )}

      {/* Quick Stats */}
      <Card>
        <CardHeader>
          <CardTitle>Key Financial Metrics</CardTitle>
          <CardDescription>
            Core numbers used in your health score calculation
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">
                {formatCurrency(metrics.monthlySurplus)}
              </div>
              <div className="text-sm text-muted-foreground">Monthly Surplus</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">
                {formatCurrency(metrics.netWorth)}
              </div>
              <div className="text-sm text-muted-foreground">Net Worth</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">
                {Math.round(metrics.liquidSavings / metrics.monthlyExpenses)}mo
              </div>
              <div className="text-sm text-muted-foreground">Emergency Fund</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">
                {formatPercentage(metrics.annualGrowthRate, 1)}
              </div>
              <div className="text-sm text-muted-foreground">Growth Rate</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}