'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { useDynamicScenarios } from '@/hooks/use-dynamic-scenarios'
import { 
  TrendingUp, 
  Calculator, 
  Home,
  Car,
  GraduationCap,
  Briefcase,
  Target,
  DollarSign,
  Calendar,
  BarChart3,
  PlusCircle,
  Settings,
  Download,
  ArrowLeft,
  ChevronDown,
  MapPin,
  Users
} from 'lucide-react'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { YearRangeControl } from '@/components/ui/year-range-control'
import { AffordabilityCalculator } from '@/components/features/goal-planning/affordability-calculator'
import { FinancialTimeline } from '@/components/features/timeline/financial-timeline'
import { useYearRangeStore } from '@/stores/app-store'
import { formatCurrency } from '@/lib/utils'
import { getAPIUrl } from '@/lib/config'

// Financial Decision Templates
const decisionTemplates = [
  {
    id: 'home-purchase',
    title: 'Home Purchase',
    description: 'Analyze affordability and timing for buying a home',
    icon: <Home className="h-5 w-5" />,
    color: 'bg-blue-500',
    questions: [
      'What home price range can I afford?',
      'When should I buy to maximize cash flow?',
      'How does down payment size affect my finances?'
    ]
  },
  {
    id: 'major-expense',
    title: 'Major Purchase',
    description: 'Plan for large expenses like renovations or vehicles',
    icon: <Car className="h-5 w-5" />,
    color: 'bg-green-500',
    questions: [
      'When can I afford this major expense?',
      'Should I finance or pay cash?',
      'How will this impact my other goals?'
    ]
  },
  {
    id: 'career-change',
    title: 'Career Transition',
    description: 'Model income changes and career moves',
    icon: <Briefcase className="h-5 w-5" />,
    color: 'bg-purple-500',
    questions: [
      'Can I afford a salary reduction?',
      'When is the best time to change careers?',
      'How long can I sustain reduced income?'
    ]
  },
  {
    id: 'education',
    title: 'Education Investment',
    description: 'Plan for education costs and ROI',
    icon: <GraduationCap className="h-5 w-5" />,
    color: 'bg-orange-500',
    questions: [
      'Can I afford additional education?',
      'What\'s the ROI on this degree/certification?',
      'Should I study part-time or full-time?'
    ]
  },
  {
    id: 'investment',
    title: 'Investment Strategy',
    description: 'Optimize investment timing and allocation',
    icon: <TrendingUp className="h-5 w-5" />,
    color: 'bg-indigo-500',
    questions: [
      'When should I increase investment contributions?',
      'Is now a good time to rebalance?',
      'How much should I allocate to different assets?'
    ]
  },
  {
    id: 'cash-flow',
    title: 'Cash Flow Planning',
    description: 'Optimize spending and saving patterns',
    icon: <DollarSign className="h-5 w-5" />,
    color: 'bg-cyan-500',
    questions: [
      'How much emergency fund do I need?',
      'Can I afford to increase my spending?',
      'What\'s my optimal savings rate?'
    ]
  }
]

// Correct birth dates
const HAVILAH_BIRTH_DATE = new Date('1974-07-15')
const JASON_BIRTH_DATE = new Date('1973-03-24')

// Calculate current ages
const calculateAge = (birthDate: Date) => {
  const today = new Date()
  let age = today.getFullYear() - birthDate.getFullYear()
  const monthDiff = today.getMonth() - birthDate.getMonth()
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--
  }
  return age
}

// Extract financial data from dynamic scenarios
const getFinancialStateFromDynamicScenario = (scenario: any) => {
  if (!scenario?.projection_results) {
    return getFinancialStateFromScenario(null)
  }

  try {
    const results = scenario.projection_results
    const finalNetWorth = results.final_net_worth || 0
    const annualExpenses = results.total_expenses / (scenario.projection_years || 8) || 180000
    const monthlyExpenses = annualExpenses / 12
    
    // Estimate monthly income based on location and employment status
    const baseSalary = 451117
    const locationMultipliers = {
      'Sf': 1.3,
      'Sd': 1.15,
      'Mn': 0.9
    }
    const locationMult = locationMultipliers[scenario.location as keyof typeof locationMultipliers] || 1.0
    const employmentMult = (scenario.spouse1_status === 'Work' ? 0.6 : 0) + (scenario.spouse2_status === 'Work' ? 0.4 : 0)
    
    const estimatedAnnualIncome = baseSalary * locationMult * employmentMult
    const monthlyIncome = estimatedAnnualIncome / 12
    const monthlySurplus = monthlyIncome - monthlyExpenses
    
    // Estimate current asset distribution
    const totalAssets = finalNetWorth / Math.pow(1 + (results.annual_growth_rate || 0.07), scenario.projection_years || 8)
    const liquidSavings = Math.min(200000, totalAssets * 0.05) // 5% liquid or max $200k
    const investments = totalAssets - liquidSavings
    
    return {
      monthlyIncome,
      monthlyExpenses,
      monthlySurplus,
      liquidSavings,
      investments,
      totalAssets,
      monthlyGrowth: monthlySurplus + (investments * (results.annual_growth_rate || 0.07) / 12),
      havilahAge: calculateAge(HAVILAH_BIRTH_DATE),
      jasonAge: calculateAge(JASON_BIRTH_DATE),
      // Additional data from dynamic scenario
      projectedNetWorth: finalNetWorth,
      annualGrowthRate: results.annual_growth_rate || 0.07,
      retirementReadiness: results.retirement_readiness || false,
      scenarioLocation: scenario.location,
      scenarioName: scenario.name
    }
  } catch (error) {
    console.error('Error parsing dynamic scenario data:', error)
    return getFinancialStateFromScenario(null)
  }
}

// This will be replaced with real data from scenarios
const getFinancialStateFromScenario = (scenarioData: any) => {
  if (!scenarioData?.user_data) {
    // Fallback mock data with correct ages
    return {
      monthlyIncome: 12500,
      monthlyExpenses: 8750,
      monthlySurplus: 3750,
      liquidSavings: 85000,
      investments: 245000,
      totalAssets: 4890000,
      monthlyGrowth: 2850,
      havilahAge: calculateAge(HAVILAH_BIRTH_DATE),
      jasonAge: calculateAge(JASON_BIRTH_DATE)
    }
  }

  try {
    const userData = JSON.parse(scenarioData.user_data)
    const totalAssets = userData.assets?.filter((asset: any) => 
      !asset.name?.toLowerCase().includes('principal') && 
      !asset.name?.toLowerCase().includes('total') && 
      !asset.name?.toLowerCase().includes('summary') &&
      !asset.name?.toLowerCase().includes('general investment account')
    ).reduce((sum: number, asset: any) => sum + (asset.current_value || 0), 0) || 0
    const totalExpenses = userData.expenses?.reduce((sum: number, expense: any) => sum + (expense.annual_amount || 0), 0) || 0
    const monthlyExpenses = totalExpenses / 12
    const monthlyIncome = (userData.annual_salary || 0) / 12
    const monthlySurplus = monthlyIncome - monthlyExpenses
    
    // Separate retirement vs non-retirement assets (exclude summary accounts)
    const retirementAssets = userData.assets?.filter((asset: any) => 
      (asset.name?.includes('401') || 
       asset.name?.includes('IRA') || 
       asset.name?.includes('Roth')) &&
      !asset.name?.toLowerCase().includes('principal') && // Exclude summary accounts
      !asset.name?.toLowerCase().includes('total') && 
      !asset.name?.toLowerCase().includes('summary') &&
      !asset.name?.toLowerCase().includes('general investment account')
    ).reduce((sum: number, asset: any) => sum + (asset.current_value || 0), 0) || 0
    
    // Calculate liquid assets (conservative estimate)
    const liquidAssets = userData.assets?.filter((asset: any) => 
      asset.name?.toLowerCase().includes('savings') || 
      asset.name?.toLowerCase().includes('cash') ||
      asset.name?.toLowerCase().includes('checking')
    ).reduce((sum: number, asset: any) => sum + (asset.current_value || 0), 0) || Math.min(200000, totalAssets * 0.05)
    
    // Non-retirement investments (excluding liquid assets)
    const nonRetirementAssets = totalAssets - retirementAssets
    const investments = Math.max(0, nonRetirementAssets - liquidAssets)
    
    return {
      monthlyIncome,
      monthlyExpenses,
      monthlySurplus,
      liquidSavings: liquidAssets,
      investments,
      totalAssets,
      monthlyGrowth: monthlySurplus + (investments * 0.07 / 12), // 7% annual return
      havilahAge: userData.havilah_age || calculateAge(HAVILAH_BIRTH_DATE),
      jasonAge: userData.jason_age || calculateAge(JASON_BIRTH_DATE)
    }
  } catch (error) {
    console.error('Error parsing scenario data:', error)
    // Fallback mock data
    return {
      monthlyIncome: 12500,
      monthlyExpenses: 8750,
      monthlySurplus: 3750,
      liquidSavings: 85000,
      investments: 245000,
      totalAssets: 4890000,
      monthlyGrowth: 2850,
      havilahAge: calculateAge(HAVILAH_BIRTH_DATE),
      jasonAge: calculateAge(JASON_BIRTH_DATE)
    }
  }
}

// Projection years options
const projectionOptions = [
  { years: 2, label: '2 Years', description: 'Short-term decisions' },
  { years: 3, label: '3 Years', description: 'Medium-term planning' },
  { years: 5, label: '5 Years', description: 'Major life changes' },
  { years: 8, label: '8 Years', description: 'Long-term goals' }
]

function DecisionCard({ template, onSelect }: { template: any, onSelect: (id: string) => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="hover:shadow-lg transition-shadow duration-200 cursor-pointer h-full"
            onClick={() => onSelect(template.id)}>
        <CardHeader>
          <div className="flex items-center space-x-3">
            <div className={`p-3 rounded-lg ${template.color} text-white`}>
              {template.icon}
            </div>
            <div>
              <CardTitle className="text-lg">{template.title}</CardTitle>
              <CardDescription>{template.description}</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="text-sm font-medium text-muted-foreground mb-2">Key Questions:</div>
            {template.questions.map((question, index) => (
              <div key={index} className="text-sm text-foreground flex items-start">
                <span className="text-primary mr-2">•</span>
                <span>{question}</span>
              </div>
            ))}
          </div>
          <Button className="w-full mt-4" variant="outline">
            Analyze This Scenario
          </Button>
        </CardContent>
      </Card>
    </motion.div>
  )
}

function CurrentStateOverview({ currentFinancialState }: { currentFinancialState: any }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <BarChart3 className="h-5 w-5 mr-2" />
          Current Financial State
        </CardTitle>
        <CardDescription>
          Your financial foundation for decision making
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {formatCurrency(currentFinancialState.monthlySurplus)}
            </div>
            <div className="text-sm text-muted-foreground">Monthly Surplus</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {formatCurrency(currentFinancialState.liquidSavings)}
            </div>
            <div className="text-sm text-muted-foreground">Liquid Savings</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {formatCurrency(currentFinancialState.investments)}
            </div>
            <div className="text-sm text-muted-foreground">Investments</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-indigo-600">
              {formatCurrency(currentFinancialState.monthlyGrowth)}
            </div>
            <div className="text-sm text-muted-foreground">Monthly Growth</div>
          </div>
        </div>
        
        <div className="mt-6 p-4 bg-muted rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium">Financial Runway</div>
              <div className="text-sm text-muted-foreground">
                Time you can sustain current expenses without income
              </div>
            </div>
            <div className="text-right">
              <div className="text-xl font-bold text-primary">
                {Math.round(currentFinancialState.liquidSavings / currentFinancialState.monthlyExpenses)} months
              </div>
              <div className="text-sm text-muted-foreground">
                ({formatCurrency(currentFinancialState.liquidSavings)} ÷ {formatCurrency(currentFinancialState.monthlyExpenses)})
              </div>
            </div>
          </div>
          
          {currentFinancialState.scenarioName && (
            <div className="mt-4 pt-4 border-t">
              <div className="text-sm font-medium text-muted-foreground mb-2">Based on Scenario:</div>
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium">{currentFinancialState.scenarioName}</span>
                <Badge variant="outline" className="text-xs">{currentFinancialState.scenarioLocation}</Badge>
                {currentFinancialState.retirementReadiness && (
                  <Badge variant="default" className="text-xs bg-green-600">Retirement Ready</Badge>
                )}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

function QuickProjection({ currentFinancialState }: { currentFinancialState: any }) {
  // Use global year range state instead of local state
  const { yearRange, setYearRange } = useYearRangeStore()
  
  const projectedWealth = currentFinancialState.totalAssets + (currentFinancialState.monthlyGrowth * 12 * yearRange)
  const projectedLiquid = currentFinancialState.liquidSavings + (currentFinancialState.monthlySurplus * 12 * yearRange)
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <TrendingUp className="h-5 w-5 mr-2" />
          Quick Projection
        </CardTitle>
        <CardDescription>
          See where you'll be financially in the future
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Projection Timeline</span>
              <Badge variant="outline">{yearRange} years</Badge>
            </div>
            <div className="flex space-x-2">
              {projectionOptions.map((option) => (
                <Button
                  key={option.years}
                  variant={yearRange === option.years ? "default" : "outline"}
                  size="sm"
                  onClick={() => setYearRange(option.years)}
                >
                  {option.label}
                </Button>
              ))}
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4 pt-4 border-t">
            <div>
              <div className="text-sm text-muted-foreground">Projected Total Wealth</div>
              <div className="text-2xl font-bold text-primary">
                {formatCurrency(projectedWealth)}
              </div>
              <div className="text-sm text-green-600">
                +{formatCurrency(projectedWealth - currentFinancialState.totalAssets)} growth
              </div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground">Projected Liquid Assets</div>
              <div className="text-2xl font-bold text-primary">
                {formatCurrency(projectedLiquid)}
              </div>
              <div className="text-sm text-green-600">
                +{formatCurrency(projectedLiquid - currentFinancialState.liquidSavings)} savings
              </div>
            </div>
          </div>
          
          <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
            <div className="text-sm">
              <strong>In {yearRange} years:</strong> You'll have approximately {formatCurrency(projectedLiquid)} 
              in liquid assets, giving you flexibility for major financial decisions.
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default function ForecastingPage() {
  const [selectedDecision, setSelectedDecision] = useState<string | null>(null)
  const [selectedScenario, setSelectedScenario] = useState<any>(null)
  const [currentFinancialState, setCurrentFinancialState] = useState<any>(null)
  const [showScenarioSelector, setShowScenarioSelector] = useState(false)
  const [showAffordabilityCalculator, setShowAffordabilityCalculator] = useState(false)
  const [showFinancialTimeline, setShowFinancialTimeline] = useState(false)
  
  // Add router for navigation and scenarios hook
  const router = useRouter()
  const { scenarios, isLoading, getDefaultScenario, getCompletedScenarios } = useDynamicScenarios()
  
  // Year range controls - moved to component level
  const { yearRange, setYearRange, startYear, setStartYear } = useYearRangeStore()

  // Close scenario selector when clicking outside
  useEffect(() => {
    const handleClickOutside = () => {
      setShowScenarioSelector(false)
    }
    
    if (showScenarioSelector) {
      document.addEventListener('click', handleClickOutside)
      return () => document.removeEventListener('click', handleClickOutside)
    }
  }, [showScenarioSelector])

  // Find and use the default scenario for financial data
  useEffect(() => {
    if (scenarios.length > 0 && !selectedScenario) {
      const defaultScenario = getDefaultScenario()
      
      if (defaultScenario) {
        console.log('Using default dynamic scenario:', defaultScenario.name)
        setSelectedScenario(defaultScenario)
        const financialState = getFinancialStateFromDynamicScenario(defaultScenario)
        setCurrentFinancialState(financialState)
      } else {
        // Fallback to mock data if no completed scenarios
        console.log('No completed scenarios found, using fallback data')
        const fallbackState = getFinancialStateFromScenario(null)
        setCurrentFinancialState(fallbackState)
      }
    }
  }, [scenarios, selectedScenario, getDefaultScenario])

  // Use fallback data if still loading
  const financialState = currentFinancialState || getFinancialStateFromScenario(null)

  const handleScenarioSelect = (scenario: any) => {
    console.log('Scenario selected:', scenario.name)
    setSelectedScenario(scenario)
    const financialState = getFinancialStateFromDynamicScenario(scenario)
    setCurrentFinancialState(financialState)
    setShowScenarioSelector(false)
  }

  const handleDecisionSelect = (decisionId: string) => {
    console.log('Decision selected:', decisionId)
    setSelectedDecision(decisionId)
    
    // Navigate to specific analysis pages
    switch (decisionId) {
      case 'education':
        console.log('Navigating to private school analysis')
        router.push('/forecasting/private-school')
        break
      default:
        // For other scenarios, log for now (can build out later)
        console.log('No specific page for decision:', decisionId)
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border bg-card">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-foreground">
                Financial Forecasting
              </h1>
              <p className="text-muted-foreground mt-1">
                Make informed money decisions with 2-8 year projections
              </p>
            </div>
            <div className="flex items-center space-x-3">
              {/* Scenario Selector */}
              {getCompletedScenarios().length > 0 && (
                <div className="relative">
                  <Button 
                    variant="outline"
                    onClick={() => setShowScenarioSelector(!showScenarioSelector)}
                    className="min-w-[200px] justify-between"
                  >
                    <div className="flex items-center">
                      <MapPin className="h-4 w-4 mr-2" />
                      <span className="truncate">
                        {selectedScenario?.name || 'Select Scenario'}
                      </span>
                    </div>
                    <ChevronDown className="h-4 w-4" />
                  </Button>
                  
                  {showScenarioSelector && (
                    <div className="absolute top-full left-0 mt-1 w-80 bg-background border rounded-lg shadow-lg z-50 max-h-60 overflow-y-auto">
                      <div className="p-2">
                        <div className="text-sm font-medium text-muted-foreground mb-2">Choose Scenario:</div>
                        {getCompletedScenarios().map((scenario) => (
                          <button
                            key={scenario.id}
                            onClick={() => handleScenarioSelect(scenario)}
                            className={`w-full text-left p-2 rounded hover:bg-muted transition-colors ${
                              selectedScenario?.id === scenario.id ? 'bg-primary/10' : ''
                            }`}
                          >
                            <div className="font-medium text-sm">{scenario.name}</div>
                            <div className="flex items-center space-x-2 mt-1">
                              <Badge variant="outline" className="text-xs">{scenario.location}</Badge>
                              <Badge variant="outline" className="text-xs">{scenario.housing}</Badge>
                              <Badge variant="outline" className="text-xs">{scenario.school_type}</Badge>
                              {scenario.projection_results && (
                                <span className="text-xs text-green-600 font-medium">
                                  {formatCurrency(scenario.projection_results.final_net_worth)}
                                </span>
                              )}
                            </div>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
              
              <Button 
                variant="outline"
                onClick={() => router.push('/')}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
              <Button variant="outline">
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </Button>
              <Button>
                <Download className="h-4 w-4 mr-2" />
                Export Analysis
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {/* Year Range Control */}
        <YearRangeControl
          value={yearRange}
          onChange={setYearRange}
          startYear={startYear}
          onStartYearChange={setStartYear}
          compact={true}
          className="w-fit mb-6"
        />

        {/* Overview Cards */}
        <div className="grid gap-6 lg:grid-cols-2 mb-8">
          <CurrentStateOverview currentFinancialState={financialState} />
          <QuickProjection currentFinancialState={financialState} />
        </div>

        {/* Decision Scenarios */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Target className="h-5 w-5 mr-2" />
              Financial Decision Scenarios
            </CardTitle>
            <CardDescription>
              Choose a scenario to analyze and get data-driven insights for your decision
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {decisionTemplates.map((template) => (
                <DecisionCard
                  key={template.id}
                  template={template}
                  onSelect={handleDecisionSelect}
                />
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Tool Views or Quick Actions */}
        {showAffordabilityCalculator ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Affordability Calculator</h2>
              <Button 
                variant="outline" 
                onClick={() => setShowAffordabilityCalculator(false)}
              >
                ← Back to Overview
              </Button>
            </div>
            <AffordabilityCalculator financialState={financialState} />
          </div>
        ) : showFinancialTimeline ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Financial Timeline</h2>
              <Button 
                variant="outline" 
                onClick={() => setShowFinancialTimeline(false)}
              >
                ← Back to Overview
              </Button>
            </div>
            <FinancialTimeline 
              financialState={financialState} 
              scenarioName={currentFinancialState?.scenarioName}
              projectionYears={8}
            />
          </div>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>
                Common financial planning tasks
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Button 
                  variant="outline" 
                  className="h-auto p-4 flex flex-col items-center"
                  onClick={() => setShowAffordabilityCalculator(true)}
                >
                  <Calculator className="h-6 w-6 mb-2" />
                  <span className="font-medium">Affordability Calculator</span>
                  <span className="text-xs text-muted-foreground mt-1">
                    What can I afford to buy?
                  </span>
                </Button>
                <Button variant="outline" className="h-auto p-4 flex flex-col items-center">
                  <Calendar className="h-6 w-6 mb-2" />
                  <span className="font-medium">Timing Optimizer</span>
                  <span className="text-xs text-muted-foreground mt-1">
                    When should I make this purchase?
                  </span>
                </Button>
                <Button 
                  variant="outline" 
                  className="h-auto p-4 flex flex-col items-center"
                  onClick={() => setShowFinancialTimeline(true)}
                >
                  <Calendar className="h-6 w-6 mb-2" />
                  <span className="font-medium">Financial Timeline</span>
                  <span className="text-xs text-muted-foreground mt-1">
                    Visualize your financial milestones
                  </span>
                </Button>
                <Button variant="outline" className="h-auto p-4 flex flex-col items-center">
                  <PlusCircle className="h-6 w-6 mb-2" />
                  <span className="font-medium">Custom Scenario</span>
                  <span className="text-xs text-muted-foreground mt-1">
                    Build your own analysis
                  </span>
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  )
}