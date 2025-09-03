'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { 
  Calendar, 
  TrendingUp, 
  Home, 
  GraduationCap, 
  PiggyBank,
  Target,
  Clock,
  DollarSign,
  Users,
  CheckCircle,
  AlertCircle
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
  projectedNetWorth?: number
  havilahAge: number
  jasonAge: number
}

interface Milestone {
  id: string
  title: string
  description: string
  targetAmount: number
  targetDate: Date
  category: 'retirement' | 'education' | 'housing' | 'goal' | 'lifecycle'
  icon: React.ReactNode
  color: string
  priority: 'high' | 'medium' | 'low'
  isAchievable: boolean
  yearsToTarget: number
  projectedAmount: number
}

interface FinancialTimelineProps {
  financialState: FinancialState
  scenarioName?: string
  projectionYears?: number
  className?: string
}

export function FinancialTimeline({ 
  financialState, 
  scenarioName,
  projectionYears = 8,
  className = '' 
}: FinancialTimelineProps) {
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [timeHorizon, setTimeHorizon] = useState<number>(10)
  
  const currentYear = new Date().getFullYear()
  
  // Generate milestones based on financial state
  const generateMilestones = (): Milestone[] => {
    const milestones: Milestone[] = []
    
    // Current ages
    const havilahAge = financialState.havilahAge
    const jasonAge = financialState.jasonAge
    
    // Retirement milestones
    const retirementYear = currentYear + (65 - Math.max(havilahAge, jasonAge))
    const retirementTarget = 2000000 // $2M retirement target
    
    milestones.push({
      id: 'retirement-ready',
      title: 'Retirement Ready',
      description: 'Sufficient funds for comfortable retirement',
      targetAmount: retirementTarget,
      targetDate: new Date(retirementYear, 0, 1),
      category: 'retirement',
      icon: <PiggyBank className="h-4 w-4" />,
      color: 'bg-green-500',
      priority: 'high',
      isAchievable: financialState.projectedNetWorth ? financialState.projectedNetWorth >= retirementTarget * 0.8 : false,
      yearsToTarget: retirementYear - currentYear,
      projectedAmount: financialState.projectedNetWorth || 0
    })
    
    // Education milestones (assuming kids are currently ~15-17)
    const collegeStartYear = currentYear + 2
    milestones.push({
      id: 'college-funding',
      title: 'College Funding Complete',
      description: 'Full funding for children\'s education',
      targetAmount: 400000, // $200k per child
      targetDate: new Date(collegeStartYear, 8, 1),
      category: 'education',
      icon: <GraduationCap className="h-4 w-4" />,
      color: 'bg-purple-500',
      priority: 'high',
      isAchievable: financialState.liquidSavings + (financialState.monthlySurplus * 24) >= 400000,
      yearsToTarget: 2,
      projectedAmount: financialState.liquidSavings + (financialState.monthlySurplus * 24)
    })
    
    // Housing milestones
    if (financialState.totalAssets < 5000000) {
      milestones.push({
        id: 'mortgage-free',
        title: 'Mortgage-Free Home',
        description: 'Home fully paid off',
        targetAmount: 1800000, // Estimated remaining mortgage
        targetDate: new Date(currentYear + 8, 0, 1),
        category: 'housing',
        icon: <Home className="h-4 w-4" />,
        color: 'bg-blue-500',
        priority: 'medium',
        isAchievable: true,
        yearsToTarget: 8,
        projectedAmount: 1800000 // Assumed achievable through normal payments
      })
    }
    
    // Wealth milestones
    const wealthTargets = [
      { amount: 5000000, title: '$5M Net Worth', years: 6 },
      { amount: 10000000, title: '$10M Net Worth', years: 12 }
    ]
    
    wealthTargets.forEach((target, index) => {
      const projectedAmount = financialState.totalAssets * Math.pow(1 + financialState.annualGrowthRate, target.years)
      
      milestones.push({
        id: `wealth-${target.amount}`,
        title: target.title,
        description: `Reach ${formatCurrency(target.amount)} in net worth`,
        targetAmount: target.amount,
        targetDate: new Date(currentYear + target.years, 0, 1),
        category: 'goal',
        icon: <TrendingUp className="h-4 w-4" />,
        color: 'bg-indigo-500',
        priority: index === 0 ? 'high' : 'medium',
        isAchievable: projectedAmount >= target.amount * 0.8,
        yearsToTarget: target.years,
        projectedAmount
      })
    })
    
    // Life event milestones
    const lifeEvents = [
      {
        id: 'havilah-60',
        title: 'Havilah Turns 60',
        description: 'Pre-retirement planning phase',
        age: 60,
        person: 'Havilah',
        currentAge: havilahAge
      },
      {
        id: 'jason-60', 
        title: 'Jason Turns 60',
        description: 'Pre-retirement planning phase',
        age: 60,
        person: 'Jason',
        currentAge: jasonAge
      }
    ]
    
    lifeEvents.forEach(event => {
      if (event.currentAge < event.age) {
        const yearsToEvent = event.age - event.currentAge
        milestones.push({
          id: event.id,
          title: event.title,
          description: event.description,
          targetAmount: 0,
          targetDate: new Date(currentYear + yearsToEvent, 0, 1),
          category: 'lifecycle',
          icon: <Users className="h-4 w-4" />,
          color: 'bg-orange-500',
          priority: 'low',
          isAchievable: true,
          yearsToTarget: yearsToEvent,
          projectedAmount: 0
        })
      }
    })
    
    return milestones.sort((a, b) => a.yearsToTarget - b.yearsToTarget)
  }
  
  const milestones = generateMilestones()
  
  const filteredMilestones = milestones.filter(milestone => {
    if (selectedCategory === 'all') return milestone.yearsToTarget <= timeHorizon
    return milestone.category === selectedCategory && milestone.yearsToTarget <= timeHorizon
  })
  
  const categories = [
    { id: 'all', label: 'All', count: milestones.filter(m => m.yearsToTarget <= timeHorizon).length },
    { id: 'retirement', label: 'Retirement', count: milestones.filter(m => m.category === 'retirement' && m.yearsToTarget <= timeHorizon).length },
    { id: 'education', label: 'Education', count: milestones.filter(m => m.category === 'education' && m.yearsToTarget <= timeHorizon).length },
    { id: 'housing', label: 'Housing', count: milestones.filter(m => m.category === 'housing' && m.yearsToTarget <= timeHorizon).length },
    { id: 'goal', label: 'Wealth Goals', count: milestones.filter(m => m.category === 'goal' && m.yearsToTarget <= timeHorizon).length }
  ]
  
  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Calendar className="h-5 w-5 mr-2" />
            Financial Timeline
          </CardTitle>
          <CardDescription>
            Key financial milestones and goals based on {scenarioName || 'your current scenario'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2 mb-4">
            {categories.map((category) => (
              <Button
                key={category.id}
                variant={selectedCategory === category.id ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedCategory(category.id)}
                className="text-xs"
              >
                {category.label} ({category.count})
              </Button>
            ))}
          </div>
          
          <div className="flex items-center space-x-4">
            <span className="text-sm font-medium">Time Horizon:</span>
            <div className="flex space-x-2">
              {[5, 10, 15, 20].map((years) => (
                <Button
                  key={years}
                  variant={timeHorizon === years ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setTimeHorizon(years)}
                >
                  {years}y
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Timeline */}
      <div className="space-y-4">
        {filteredMilestones.map((milestone, index) => (
          <Card key={milestone.id} className={`${milestone.isAchievable ? 'border-green-200' : 'border-orange-200'}`}>
            <CardContent className="p-4">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4">
                  {/* Timeline Indicator */}
                  <div className="flex flex-col items-center">
                    <div className={`p-2 rounded-full ${milestone.color} text-white`}>
                      {milestone.icon}
                    </div>
                    {index < filteredMilestones.length - 1 && (
                      <div className="w-px h-16 bg-border mt-2" />
                    )}
                  </div>
                  
                  {/* Content */}
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="font-medium">{milestone.title}</h3>
                      <Badge variant={milestone.priority === 'high' ? 'default' : 'outline'} className="text-xs">
                        {milestone.priority}
                      </Badge>
                      {milestone.isAchievable ? (
                        <CheckCircle className="h-4 w-4 text-green-600" />
                      ) : (
                        <AlertCircle className="h-4 w-4 text-orange-600" />
                      )}
                    </div>
                    
                    <p className="text-sm text-muted-foreground mb-2">
                      {milestone.description}
                    </p>
                    
                    <div className="flex items-center space-x-4 text-sm">
                      <div className="flex items-center space-x-1">
                        <Clock className="h-3 w-3" />
                        <span>{milestone.targetDate.getFullYear()} ({milestone.yearsToTarget} years)</span>
                      </div>
                      
                      {milestone.targetAmount > 0 && (
                        <div className="flex items-center space-x-1">
                          <DollarSign className="h-3 w-3" />
                          <span>{formatCurrency(milestone.targetAmount)}</span>
                        </div>
                      )}
                    </div>
                    
                    {/* Progress for financial milestones */}
                    {milestone.targetAmount > 0 && (
                      <div className="mt-3">
                        <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
                          <span>Progress</span>
                          <span>
                            {((milestone.projectedAmount / milestone.targetAmount) * 100).toFixed(0)}%
                          </span>
                        </div>
                        <Progress 
                          value={Math.min(100, (milestone.projectedAmount / milestone.targetAmount) * 100)} 
                          className="h-2"
                        />
                        <div className="flex justify-between text-xs text-muted-foreground mt-1">
                          <span>Projected: {formatCurrency(milestone.projectedAmount)}</span>
                          <span className={milestone.isAchievable ? 'text-green-600' : 'text-orange-600'}>
                            {milestone.isAchievable ? 'On track' : 'Needs attention'}
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
        
        {filteredMilestones.length === 0 && (
          <Card>
            <CardContent className="p-8 text-center">
              <Calendar className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-2">No milestones found</h3>
              <p className="text-muted-foreground">
                Try adjusting your time horizon or category filter.
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}