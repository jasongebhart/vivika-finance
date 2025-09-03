'use client'

import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import dynamic from 'next/dynamic'
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  PiggyBank, 
  Target,
  Plus,
  BarChart3,
  Settings,
  Moon,
  Sun,
  Calculator,
  Calendar,
  Info,
  Home,
  MapPin,
  GraduationCap,
  AlertTriangle,
  CheckCircle,
  ArrowRight,
  Clock
} from 'lucide-react'
import { useTheme } from 'next-themes'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { NetWorthProjectionChart } from '@/components/charts/responsive-container'
import { ExpenseBreakdown } from '@/components/features/expense-breakdown'
import { DetailedExpenseBreakdown } from '@/components/features/expense-breakdown/detailed-breakdown'
import { YearRangeControl } from '@/components/ui/year-range-control'
import { formatCurrency, formatPercentage } from '@/lib/utils'
import { useAppStore, useYearRangeStore } from '@/stores/app-store'
import { useDynamicScenarios } from '@/hooks/use-dynamic-scenarios'
import { useConfigUpdates } from '@/hooks/use-websocket'
import { getAPIUrl, API_CONFIG } from '@/lib/config'
import apiClient from '@/lib/api'
import type { Scenario } from '@/types'
import { FinancialHealthScore } from '@/components/features/financial-health/financial-health-score'
import type { FinancialHealthMetrics } from '@/lib/financial-health-scoring'

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

// Extended Scenario type to handle API response format
interface ScenarioWithData extends Scenario {
  user_data?: string // JSON string from API
}

// Mock data for demonstration
const mockDashboardData = {
  net_worth: {
    current: 285000,
    projected: 950000,
    growth_rate: 0.085
  },
  monthly_surplus: 2750,
  investment_balance: 145000,
  retirement_balance: 89000,
  scenarios_count: 3,
  recent_activity: [
    { type: 'scenario_created', name: 'Early Retirement Plan', date: '2025-01-20' },
    { type: 'projection_updated', name: 'Current Plan', date: '2025-01-19' },
    { type: 'monte_carlo_run', name: 'Aggressive Growth', date: '2025-01-18' }
  ]
}

const generateProjectionData = (
  statusQuoScenario: ScenarioWithData | null,
  yearRange: number,
  startYear: number
) => {
  if (!statusQuoScenario) {
    // Fallback mock data
    return Array.from({ length: yearRange }, (_, i) => ({
      year: startYear + i,
      age: 35 + i,
      netWorth: Math.round(285000 * Math.pow(1.085, i)),
      portfolioValue: Math.round(145000 * Math.pow(1.1, i))
    }))
  }

  try {
    const userData = JSON.parse(statusQuoScenario.user_data || '{}')
    const totalAssets = userData.assets?.filter((asset: any) => 
      !asset.name?.toLowerCase().includes('principal') && 
      !asset.name?.toLowerCase().includes('total') && 
      !asset.name?.toLowerCase().includes('summary') &&
      !asset.name?.toLowerCase().includes('general investment account')
    ).reduce((sum: number, asset: any) => sum + (asset.current_value || 0), 0) || 0
    const currentAge = userData.current_age || 52
    const annualSalary = userData.annual_salary || 0
    const totalExpenses = userData.expenses?.reduce((sum: number, expense: any) => sum + (expense.annual_amount || 0), 0) || 0
    const annualSavings = Math.max(0, annualSalary - totalExpenses)

    return Array.from({ length: yearRange }, (_, i) => {
      const year = startYear + i
      const age = currentAge + i
      const investmentGrowth = totalAssets * Math.pow(1.07, i) // 7% growth on existing assets
      const savingsGrowth = annualSavings * (Math.pow(1.07, i) - 1) / 0.07 // Future value of annual savings
      const netWorth = investmentGrowth + savingsGrowth
      
      return {
        year,
        age,
        netWorth: Math.round(netWorth),
        portfolioValue: Math.round(investmentGrowth)
      }
    })
  } catch (error) {
    console.error('Error generating projection data:', error)
    // Fallback to mock data
    return Array.from({ length: yearRange }, (_, i) => ({
      year: startYear + i,
      age: 35 + i,
      netWorth: Math.round(285000 * Math.pow(1.085, i)),
      portfolioValue: Math.round(145000 * Math.pow(1.1, i))
    }))
  }
}


interface MetricCardProps {
  title: string
  value: string
  change: number
  changeLabel: string
  icon: React.ReactNode
  trend: 'up' | 'down' | 'neutral'
  description?: string
}

function MetricCard({ title, value, change, changeLabel, icon, trend, description }: MetricCardProps) {
  const getTrendColor = () => {
    switch (trend) {
      case 'up': return 'text-green-600 dark:text-green-400'
      case 'down': return 'text-red-600 dark:text-red-400'
      default: return 'text-muted-foreground'
    }
  }

  const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : BarChart3

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="hover:shadow-lg transition-shadow duration-200">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {title}
          </CardTitle>
          <div className="h-4 w-4 text-muted-foreground">
            {icon}
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{value}</div>
          <div className={`flex items-center text-xs ${getTrendColor()}`}>
            <TrendIcon className="mr-1 h-3 w-3" />
            <span>{formatPercentage(Math.abs(change), 1)} {changeLabel}</span>
          </div>
          {description && (
            <div className="mt-2 text-xs text-muted-foreground">
              {description}
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}

function QuickActions({ router }: { router: any }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Life Planning Actions</CardTitle>
        <CardDescription>
          Make key financial decisions with confidence
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Button 
          className="w-full justify-start bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white" 
          onClick={() => router.push('/life-planning')}
        >
          <Home className="mr-2 h-4 w-4" />
          Should We Move? (Life Planning)
        </Button>
        <Button 
          className="w-full justify-start" 
          variant="outline"
          onClick={() => router.push('/scenario-builder')}
        >
          <Plus className="mr-2 h-4 w-4" />
          Create New Scenario
        </Button>
        <Button 
          className="w-full justify-start" 
          variant="outline"
          onClick={() => router.push('/scenario-comparison')}
        >
          <BarChart3 className="mr-2 h-4 w-4" />
          Compare Scenarios
        </Button>
        <Button 
          className="w-full justify-start" 
          variant="outline"
          onClick={() => router.push('/scenario-management')}
        >
          <Settings className="mr-2 h-4 w-4" />
          Manage All Scenarios
        </Button>
      </CardContent>
    </Card>
  )
}

function LifePlanningInsights({ router }: { router: any }) {
  const currentYear = new Date().getFullYear()
  const emmaHighSchoolYear = 2027  // Grade 7 -> Grade 9 in 2027
  const jakeHighSchoolYear = 2030   // Grade 4 -> Grade 9 in 2030
  
  return (
    <Card className="border-blue-200 bg-gradient-to-br from-blue-50 to-purple-50">
      <CardHeader>
        <CardTitle className="flex items-center text-blue-900">
          <GraduationCap className="mr-2 h-5 w-5" />
          Life Planning Insights
        </CardTitle>
        <CardDescription className="text-blue-700">
          Key decisions approaching for your family
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Emma's High School Decision */}
        <div className="flex items-start space-x-3 p-3 bg-white/60 rounded-lg border border-blue-100">
          <Clock className="h-5 w-5 text-orange-500 mt-0.5" />
          <div className="flex-1">
            <div className="font-medium text-blue-900">Emma starts high school in {emmaHighSchoolYear}</div>
            <div className="text-sm text-blue-700 mt-1">
              Moving before {emmaHighSchoolYear} avoids school transition stress. 
              {emmaHighSchoolYear - currentYear <= 2 ? ' Time is running out!' : ' Still time to plan.'}
            </div>
            <div className="text-xs text-blue-600 mt-1">
              Years until decision: {emmaHighSchoolYear - currentYear}
            </div>
          </div>
        </div>

        {/* Jake's High School Decision */}
        <div className="flex items-start space-x-3 p-3 bg-white/60 rounded-lg border border-blue-100">
          <Clock className="h-5 w-5 text-blue-500 mt-0.5" />
          <div className="flex-1">
            <div className="font-medium text-blue-900">Jake starts high school in {jakeHighSchoolYear}</div>
            <div className="text-sm text-blue-700 mt-1">
              More flexible timing - can move anytime before {jakeHighSchoolYear}
            </div>
            <div className="text-xs text-blue-600 mt-1">
              Years until decision: {jakeHighSchoolYear - currentYear}
            </div>
          </div>
        </div>

        {/* Quick Decision Recommendation */}
        <div className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg border border-green-200">
          <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
          <div className="flex-1">
            <div className="font-medium text-green-900">Optimal Move Window</div>
            <div className="text-sm text-green-700 mt-1">
              Analysis shows moving to Minnesota in 2025 saves $1.79M over 10 years with immediate break-even
            </div>
          </div>
        </div>

        {/* Call to Action */}
        <div className="pt-2">
          <Button 
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
            onClick={() => router.push('/life-planning')}
          >
            <ArrowRight className="mr-2 h-4 w-4" />
            Get Full Life Planning Analysis
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

function RecentActivity() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
        <CardDescription>
          Your latest financial planning activities
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {mockDashboardData.recent_activity.map((activity, index) => (
            <div key={index} className="flex items-center space-x-4">
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-foreground">
                  {activity.name}
                </p>
                <p className="text-sm text-muted-foreground">
                  {activity.type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </p>
              </div>
              <div className="text-sm text-muted-foreground">
                {new Date(activity.date).toLocaleDateString()}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

function HouseInformationCard() {
  const [houseData, setHouseData] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  // Handle real-time configuration updates
  const handleConfigUpdate = (configType: string, data: any) => {
    console.log('Received config update:', configType, data)
    if (configType === 'house_data') {
      setHouseData(data)
      setLastUpdated(new Date())
    }
  }

  // Connect to WebSocket for real-time updates (graceful degradation if not available)
  const { isConnected: wsConnected, error: wsError } = useConfigUpdates(handleConfigUpdate)
  
  // Hide WebSocket errors from console after initial attempt
  useEffect(() => {
    if (wsError) {
      // Suppress further WebSocket error logging after first attempt
      console.warn('WebSocket real-time updates unavailable - using API polling')
    }
  }, [wsError])

  useEffect(() => {
    // Fetch house data from API endpoint using proper configuration
    const apiUrl = getAPIUrl(API_CONFIG.endpoints.houseData)
    
    fetch(apiUrl)
      .then(res => {
        if (!res.ok) {
          throw new Error(`API request failed: ${res.status} ${res.statusText}`)
        }
        return res.json()
      })
      .then(data => {
        setHouseData(data)
        setIsLoading(false)
      })
      .catch(err => {
        console.error('Error fetching house data from API:', err)
        // Fallback to JSON file if API fails
        console.log('Falling back to general.finance.json file...')
        fetch('/general.finance.json')
          .then(res => {
            if (!res.ok) {
              throw new Error('Failed to fetch house data from fallback')
            }
            return res.json()
          })
          .then(data => {
            setHouseData(data)
            setIsLoading(false)
          })
          .catch(fallbackErr => {
            console.error('Error fetching house data from fallback:', fallbackErr)
            setError(`API Error: ${err.message}, Fallback Error: ${fallbackErr.message}`)
            setIsLoading(false)
          })
      })
  }, [])

  if (isLoading) {
    return (
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center">
            <Home className="h-5 w-5 mr-2" />
            House Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-muted-foreground py-4">
            Loading house information...
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error || !houseData?.house) {
    return (
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center">
            <Home className="h-5 w-5 mr-2" />
            House Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-muted-foreground py-4">
            {error ? `Error: ${error}` : 'No house data available'}
          </div>
        </CardContent>
      </Card>
    )
  }

  const house = houseData.house
  const newHouse = houseData.new_house
  const netEquity = house.value - house.mortgage_principal
  const newHouseEquity = newHouse.value - newHouse.mortgage_principal

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center">
            <Home className="h-5 w-5 mr-2" />
            House Information
          </div>
          <div className="flex items-center space-x-2">
            {lastUpdated && (
              <span className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded">
                Updated {lastUpdated.toLocaleTimeString()}
              </span>
            )}
            <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-gray-400'}`} 
                 title={wsConnected ? 'Connected to real-time updates' : 'Not connected to real-time updates'} />
          </div>
        </CardTitle>
        <CardDescription>
          Property details and financial information{wsConnected ? ' (Live updates enabled)' : ''}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Current House */}
          <div className="space-y-4">
            <h3 className="font-semibold text-lg border-b pb-2">{house.description}</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-sm text-muted-foreground">Current Value</span>
                <p className="font-medium text-green-600">{formatCurrency(house.value)}</p>
              </div>
              <div>
                <span className="text-sm text-muted-foreground">Mortgage Balance</span>
                <p className="font-medium text-red-600">{formatCurrency(house.mortgage_principal)}</p>
              </div>
              <div>
                <span className="text-sm text-muted-foreground">Net Equity</span>
                <p className="font-medium text-blue-600">{formatCurrency(netEquity)}</p>
              </div>
              <div>
                <span className="text-sm text-muted-foreground">Monthly Payment</span>
                <p className="font-medium">{formatCurrency(house.monthly_payment)}</p>
              </div>
              <div>
                <span className="text-sm text-muted-foreground">Property Tax</span>
                <p className="font-medium">{formatCurrency(house.annual_property_tax)}/year</p>
              </div>
              <div>
                <span className="text-sm text-muted-foreground">Growth Rate</span>
                <p className="font-medium">{formatPercentage(house.annual_growth_rate, 1)}</p>
              </div>
            </div>
            <div className="text-xs text-muted-foreground space-y-1 pt-2 border-t">
              <p>Interest Rate: {formatPercentage(house.interest_rate, 2)}</p>
              <p>Payments Made: {house.payments_made}/{house.number_of_payments}</p>
              <p>Cost Basis: {formatCurrency(house.cost_basis)}</p>
            </div>
          </div>

          {/* Relocation Home */}
          <div className="space-y-4">
            <h3 className="font-semibold text-lg border-b pb-2">{newHouse.description}</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-sm text-muted-foreground">Current Value</span>
                <p className="font-medium text-green-600">{formatCurrency(newHouse.value)}</p>
              </div>
              <div>
                <span className="text-sm text-muted-foreground">Mortgage Balance</span>
                <p className="font-medium text-red-600">{formatCurrency(newHouse.mortgage_principal)}</p>
              </div>
              <div>
                <span className="text-sm text-muted-foreground">Net Equity</span>
                <p className="font-medium text-blue-600">{formatCurrency(newHouseEquity)}</p>
              </div>
              <div>
                <span className="text-sm text-muted-foreground">Monthly Payment</span>
                <p className="font-medium">{formatCurrency(newHouse.monthly_payment)}</p>
              </div>
              <div>
                <span className="text-sm text-muted-foreground">Property Tax</span>
                <p className="font-medium">{formatCurrency(newHouse.annual_property_tax)}/year</p>
              </div>
              <div>
                <span className="text-sm text-muted-foreground">Growth Rate</span>
                <p className="font-medium">{formatPercentage(newHouse.annual_growth_rate, 1)}</p>
              </div>
            </div>
            <div className="text-xs text-muted-foreground space-y-1 pt-2 border-t">
              <p>Interest Rate: {formatPercentage(newHouse.interest_rate, 2)}</p>
              <p>Payments Made: {newHouse.payments_made}/{newHouse.number_of_payments}</p>
              <p>Cost Basis: {formatCurrency(newHouse.cost_basis)}</p>
            </div>
          </div>
        </div>

        {/* Comparison */}
        <div className="mt-6 pt-4 border-t">
          <h4 className="font-medium mb-3">Comparison</h4>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <span className="text-sm text-muted-foreground">Equity Difference</span>
              <p className="font-medium">
                {formatCurrency(Math.abs(netEquity - newHouseEquity))}
                <span className="text-xs text-muted-foreground ml-1">
                  ({netEquity > newHouseEquity ? 'SF higher' : 'MN higher'})
                </span>
              </p>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">Payment Difference</span>
              <p className="font-medium">
                {formatCurrency(Math.abs(house.monthly_payment - newHouse.monthly_payment))}
                <span className="text-xs text-muted-foreground ml-1">
                  ({house.monthly_payment > newHouse.monthly_payment ? 'SF higher' : 'MN higher'})
                </span>
              </p>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">Tax Difference</span>
              <p className="font-medium">
                {formatCurrency(Math.abs(house.annual_property_tax - newHouse.annual_property_tax))}
                <span className="text-xs text-muted-foreground ml-1">
                  ({house.annual_property_tax > newHouse.annual_property_tax ? 'SF higher' : 'MN higher'})
                </span>
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  
  return (
    <Button
      variant="outline"
      size="icon"
      onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
      className="ml-auto"
    >
      <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
      <span className="sr-only">Toggle theme</span>
    </Button>
  )
}

export function Dashboard() {
  const router = useRouter()
  const { 
    scenarios: dynamicScenarios, 
    isLoading: scenariosLoading, 
    getDefaultScenario,
    getCompletedScenarios,
    getBestScenario 
  } = useDynamicScenarios()
  
  // State to track client-side hydration
  const [isClient, setIsClient] = useState(false)
  
  // Year range controls from global state
  const { 
    yearRange, 
    startYear, 
    endYear,
    setYearRange, 
    setStartYear 
  } = useYearRangeStore()

  // Set client flag after hydration
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsClient(true)
    }, 0)
    return () => clearTimeout(timer)
  }, [])
  
  // State for scenarios and default selection
  const [manualScenarios, setManualScenarios] = useState<ScenarioWithData[]>([])
  const [statusQuoScenario, setStatusQuoScenario] = useState<any>(null)
  const [usingDynamicScenarios, setUsingDynamicScenarios] = useState(false)
  
  // Function to determine the best default scenario
  const findDefaultScenario = (scenarios: ScenarioWithData[]) => {
    if (scenarios.length === 0) return null
    
    // Priority order for default scenario selection:
    // 1. Look for 8-year projection scenarios (most comprehensive)
    // 2. Look for "Work Work" scenarios (both working)
    // 3. Look for scenarios with "Current" type
    // 4. Fall back to first available scenario
    
    // Try to find 8-year work scenario first
    let defaultScenario = scenarios.find(scenario => 
      scenario.name.toLowerCase().includes('8yrs') && 
      scenario.name.toLowerCase().includes('work work')
    )
    
    // If not found, try any 8-year scenario
    if (!defaultScenario) {
      defaultScenario = scenarios.find(scenario => 
        scenario.name.toLowerCase().includes('8yrs')
      )
    }
    
    // If still not found, try current type scenarios
    if (!defaultScenario) {
      defaultScenario = scenarios.find(scenario => 
        scenario.scenario_type === 'current'
      )
    }
    
    // Fall back to first scenario
    if (!defaultScenario) {
      defaultScenario = scenarios[0]
    }
    
    return defaultScenario
  }

  // Load dynamic scenarios first, fallback to manual scenarios
  useEffect(() => {
    if (dynamicScenarios.length > 0) {
      console.log('Dashboard: Using dynamic scenarios:', dynamicScenarios.length)
      const defaultScenario = getDefaultScenario()
      if (defaultScenario) {
        console.log('Dashboard: Selected dynamic default scenario:', defaultScenario.name)
        setStatusQuoScenario(defaultScenario)
        setUsingDynamicScenarios(true)
        return
      }
    }
    
    // Fallback to loading manual scenarios if no dynamic scenarios
    if (!scenariosLoading && dynamicScenarios.length === 0) {
      console.log('Dashboard: Loading manual scenarios as fallback...')
      fetch(getAPIUrl('/api/scenarios'))
        .then(res => res.json())
        .then(data => {
          console.log('Dashboard: Loaded', data.length, 'manual scenarios')
          setManualScenarios(data.slice(0, 5))
          
          const defaultScenario = findDefaultScenario(data)
          console.log('Dashboard: Selected manual default scenario:', defaultScenario?.name)
          if (defaultScenario) {
            fetch(getAPIUrl(`/api/scenarios/${defaultScenario.id}?t=${Date.now()}`))
              .then(res => res.json())
              .then(fullScenario => {
                console.log('Dashboard: Loaded full manual scenario data:', fullScenario)
                setStatusQuoScenario(fullScenario)
                setUsingDynamicScenarios(false)
              })
              .catch(err => {
                console.error('Dashboard: Failed to load full manual scenario:', err)
                setStatusQuoScenario(defaultScenario)
                setUsingDynamicScenarios(false)
              })
          }
        })
        .catch(err => {
          console.error('Dashboard: Failed to load manual scenarios:', err)
        })
    }
  }, [dynamicScenarios, scenariosLoading, getDefaultScenario])
  
  // This effect is now handled by the dynamic scenarios loading above
  
  // Function to convert scenario data to health metrics format
  const convertToHealthMetrics = (scenario: any, dashboardData: any): FinancialHealthMetrics | null => {
    if (!scenario || !dashboardData) return null
    
    try {
      if (scenario.projection_results) {
        // Dynamic scenario with results
        const results = scenario.projection_results
        const finalNetWorth = results.final_net_worth || 0
        const totalExpenses = results.total_expenses || 0
        const annualExpenses = totalExpenses / (scenario.projection_years || 8)
        const monthlyExpenses = annualExpenses / 12
        
        // Estimate current assets from final net worth projection
        const currentAssets = finalNetWorth / Math.pow(1 + (results.annual_growth_rate || 0.07), scenario.projection_years || 8)
        
        // Estimate salary based on location and employment status
        const baseSalary = 451117
        const locationMultipliers = { 'Sf': 1.3, 'Sd': 1.15, 'Mn': 0.9 }
        const locationMult = locationMultipliers[scenario.location as keyof typeof locationMultipliers] || 1.0
        const employmentMult = (scenario.spouse1_status === 'Work' ? 0.6 : 0) + (scenario.spouse2_status === 'Work' ? 0.4 : 0)
        const estimatedSalary = baseSalary * locationMult * employmentMult
        const monthlyIncome = estimatedSalary / 12
        
        return {
          netWorth: currentAssets,
          monthlyIncome,
          monthlyExpenses,
          monthlySurplus: monthlyIncome - monthlyExpenses,
          liquidSavings: Math.min(200000, currentAssets * 0.05), // Estimate 5% liquid or max $200k
          investments: currentAssets * 0.95, // Estimate 95% invested
          annualGrowthRate: results.annual_growth_rate || 0.07,
          currentAge: Math.max(calculateAge(JASON_BIRTH_DATE), calculateAge(HAVILAH_BIRTH_DATE)),
          projectionYears: scenario.projection_years || 8,
          projectedNetWorth: finalNetWorth,
          retirementReadiness: results.retirement_readiness || false,
          location: scenario.location,
          housingType: scenario.housing,
          schoolType: scenario.school_type
        }
      } else {
        // Manual scenario - parse user_data
        const userData = JSON.parse(scenario.user_data || '{}')
        const totalAssets = userData.assets?.filter((asset: any) => 
          !asset.name?.toLowerCase().includes('principal') && 
          !asset.name?.toLowerCase().includes('total') && 
          !asset.name?.toLowerCase().includes('summary') &&
          !asset.name?.toLowerCase().includes('general investment account')
        ).reduce((sum: number, asset: any) => sum + (asset.current_value || 0), 0) || 0
        const totalExpenses = userData.expenses?.reduce((sum: number, expense: any) => sum + (expense.annual_amount || 0), 0) || 0
        const annualSalary = userData.annual_salary || 0
        const monthlyIncome = annualSalary / 12
        const monthlyExpenses = totalExpenses / 12
        
        // Estimate liquid assets
        const liquidAssets = userData.assets?.filter((asset: any) => 
          asset.name?.toLowerCase().includes('savings') || 
          asset.name?.toLowerCase().includes('cash') ||
          asset.name?.toLowerCase().includes('checking')
        ).reduce((sum: number, asset: any) => sum + (asset.current_value || 0), 0) || Math.min(200000, totalAssets * 0.05)
        
        return {
          netWorth: totalAssets,
          monthlyIncome,
          monthlyExpenses,
          monthlySurplus: monthlyIncome - monthlyExpenses,
          liquidSavings: liquidAssets,
          investments: totalAssets - liquidAssets,
          annualGrowthRate: 0.07, // Default assumption
          currentAge: userData.current_age || Math.max(calculateAge(JASON_BIRTH_DATE), calculateAge(HAVILAH_BIRTH_DATE)),
          projectionYears: 8, // Default projection
          projectedNetWorth: totalAssets * Math.pow(1.07, 8), // Simple projection
          retirementReadiness: undefined
        }
      }
    } catch (error) {
      console.error('Error converting to health metrics:', error)
      return null
    }
  }
  
  // Function to extract financial data from dynamic scenarios
  const extractDynamicScenarioData = (scenario: any) => {
    if (!scenario) return null
    
    try {
      if (scenario.projection_results) {
        // This is a dynamic scenario with results
        const results = scenario.projection_results
        const finalNetWorth = results.final_net_worth || 0
        const totalExpenses = results.total_expenses || 0
        const annualExpenses = totalExpenses / (scenario.projection_years || 8)
        
        // Estimate current assets from final net worth projection
        const currentAssets = finalNetWorth / Math.pow(1 + (results.annual_growth_rate || 0.07), scenario.projection_years || 8)
        
        // Estimate salary based on location and employment status
        const baseSalary = 451117
        const locationMultipliers = { 'Sf': 1.3, 'Sd': 1.15, 'Mn': 0.9 }
        const locationMult = locationMultipliers[scenario.location as keyof typeof locationMultipliers] || 1.0
        const employmentMult = (scenario.spouse1_status === 'Work' ? 0.6 : 0) + (scenario.spouse2_status === 'Work' ? 0.4 : 0)
        const estimatedSalary = baseSalary * locationMult * employmentMult
        
        return {
          totalAssets: currentAssets,
          annualSalary: estimatedSalary,
          totalExpenses: annualExpenses,
          projectedNetWorth: finalNetWorth,
          growthRate: results.annual_growth_rate || 0.07,
          isDynamic: true
        }
      }
    } catch (error) {
      console.error('Error extracting dynamic scenario data:', error)
    }
    
    return null
  }
  
  // Debug current state
  useEffect(() => {
    console.log('Dashboard state update:')
    console.log('- statusQuoScenario:', statusQuoScenario?.name)
    console.log('- dynamicScenarios.length:', dynamicScenarios.length)
    console.log('- manualScenarios.length:', manualScenarios.length)
    console.log('- usingDynamicScenarios:', usingDynamicScenarios)
    console.log('- scenariosLoading:', scenariosLoading)
  }, [statusQuoScenario, dynamicScenarios, manualScenarios, usingDynamicScenarios, scenariosLoading])
  
  
  // Query for dashboard data - now uses real scenario data
  const { data: dashboardData, isLoading, error } = useQuery({
    queryKey: ['dashboard', statusQuoScenario?.id, isClient ? yearRange : 5, isClient ? startYear : new Date().getFullYear()],
    queryFn: async () => {
      console.log('Dashboard query running for scenario:', statusQuoScenario?.name)
      if (statusQuoScenario) {
        try {
          // Try dynamic scenario data first
          const dynamicData = extractDynamicScenarioData(statusQuoScenario)
          if (dynamicData) {
            console.log('Dashboard query: Using dynamic scenario data')
            return {
              net_worth: {
                current: dynamicData.totalAssets,
                projected: dynamicData.projectedNetWorth,
                growth_rate: dynamicData.growthRate
              },
              monthly_surplus: Math.max(0, dynamicData.annualSalary - dynamicData.totalExpenses) / 12,
              investment_balance: dynamicData.totalAssets * 0.4, // Estimate 40% in investments
              retirement_balance: dynamicData.totalAssets * 0.6, // Estimate 60% in retirement accounts
              scenarios_count: dynamicScenarios.length,
              recent_activity: [
                { type: 'dynamic_scenario', name: statusQuoScenario.name, date: statusQuoScenario.created_at },
                { type: 'projection_complete', name: 'Real Financial Analysis', date: statusQuoScenario.updated_at || new Date().toISOString().split('T')[0] },
                { type: 'data_updated', name: 'Dynamic Parameters', date: new Date().toISOString().split('T')[0] }
              ]
            }
          }
          
          // Fallback to manual scenario parsing
          console.log('Dashboard query: Using manual scenario data')
          const userData = JSON.parse(statusQuoScenario.user_data || '{}')
          const totalAssets = userData.assets?.filter((asset: any) => 
      !asset.name?.toLowerCase().includes('principal') && 
      !asset.name?.toLowerCase().includes('total') && 
      !asset.name?.toLowerCase().includes('summary') &&
      !asset.name?.toLowerCase().includes('general investment account')
    ).reduce((sum: number, asset: any) => sum + (asset.current_value || 0), 0) || 0
          const totalExpenses = userData.expenses?.reduce((sum: number, expense: any) => sum + (expense.annual_amount || 0), 0) || 0
          const retirementAccounts = userData.assets?.filter((asset: any) => 
            (asset.name?.includes('401') || 
             asset.name?.includes('IRA') || 
             asset.name?.includes('Roth')) &&
            !asset.name?.toLowerCase().includes('principal') && // Exclude summary accounts
            !asset.name?.toLowerCase().includes('total') && 
            !asset.name?.toLowerCase().includes('summary') &&
            !asset.name?.toLowerCase().includes('general investment account')
          ) || []
          const totalRetirement = retirementAccounts.reduce((sum: number, account: any) => sum + (account.current_value || 0), 0)
          const investmentAccounts = userData.assets?.filter((asset: any) => 
            !asset.name?.includes('401') && 
            !asset.name?.includes('IRA') && 
            !asset.name?.includes('Roth') &&
            !asset.name?.toLowerCase().includes('principal') && // Exclude summary accounts
            !asset.name?.toLowerCase().includes('total') && 
            !asset.name?.toLowerCase().includes('summary') &&
            !asset.name?.toLowerCase().includes('general investment account')
          ) || []
          const totalInvestments = investmentAccounts.reduce((sum: number, account: any) => sum + (account.current_value || 0), 0)
          
          return {
            net_worth: {
              current: totalAssets,
              projected: totalAssets * Math.pow(1.07, yearRange), // Use selected year range
              growth_rate: 0.07
            },
            monthly_surplus: Math.max(0, (userData.annual_salary || 0) - totalExpenses) / 12,
            investment_balance: totalInvestments,
            retirement_balance: totalRetirement,
            scenarios_count: dynamicScenarios.length || manualScenarios.length,
            recent_activity: [
              { type: 'scenario_loaded', name: statusQuoScenario.name, date: statusQuoScenario.created_at },
              { type: 'data_updated', name: 'Financial Profile', date: new Date().toISOString().split('T')[0] },
              { type: 'projection_ready', name: 'Status Quo Analysis', date: new Date().toISOString().split('T')[0] }
            ]
          }
        } catch (error) {
          console.error('Dashboard query: Error parsing status quo scenario:', error)
          return mockDashboardData
        }
      }
      console.log('Dashboard query: Using mock data fallback')
      return mockDashboardData
    },
    enabled: true, // Always enable the query
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  // Use dashboardData if available, otherwise fallback to mock data
  const data = dashboardData || mockDashboardData
  
  console.log('Dashboard render:')
  console.log('- Using data from:', dashboardData ? 'real scenario' : 'mock data')
  console.log('- Current scenario:', statusQuoScenario?.name || 'none')
  console.log('- Query loading:', isLoading)
  console.log('- Query error:', error)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border bg-card">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-foreground">
                Life Planning & Financial Dashboard
              </h1>
              <p className="text-muted-foreground">
                Make confident decisions about moving, education, and your family's financial future
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <Button 
                className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white"
                onClick={() => router.push('/life-planning')}
              >
                <Home className="h-4 w-4 mr-2" />
                Life Planning
              </Button>
              <Button 
                variant="outline"
                onClick={() => router.push('/scenario-builder')}
              >
                <Plus className="h-4 w-4 mr-2" />
                New Scenario
              </Button>
              <Button 
                variant="outline"
                onClick={() => router.push('/admin')}
              >
                <Settings className="h-4 w-4 mr-2" />
                Admin
              </Button>
              <ThemeToggle />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {/* Urgent Decision Alert */}
        <div className="mb-6">
          <Card className="border-l-4 border-l-orange-500 bg-orange-50 border-orange-200">
            <CardContent className="pt-6">
              <div className="flex items-start space-x-4">
                <AlertTriangle className="h-6 w-6 text-orange-600 mt-0.5" />
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold text-orange-900">Time-Sensitive Decision Required</h3>
                      <p className="text-sm text-orange-700 mt-1">
                        Emma starts high school in 2027 (2 years). Moving before then avoids educational disruption and could save your family $1.79M over 10 years.
                      </p>
                    </div>
                    <Button 
                      className="ml-4 bg-orange-600 hover:bg-orange-700 text-white"
                      onClick={() => router.push('/life-planning')}
                    >
                      Analyze Now
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Metrics Grid */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-5 mb-8">
          <MetricCard
            title="Net Worth"
            value={formatCurrency(data.net_worth.current)}
            change={8.5}
            changeLabel="from last month"
            icon={<DollarSign />}
            trend="up"
          />
          <MetricCard
            title="Monthly Surplus"
            value={formatCurrency(data.monthly_surplus)}
            change={-2.1}
            changeLabel="from last month"
            icon={<TrendingUp />}
            trend="down"
          />
          <MetricCard
            title="Investment Balance"
            value={formatCurrency(data.investment_balance)}
            change={12.3}
            changeLabel="YTD return"
            icon={<BarChart3 />}
            trend="up"
            description="Non-retirement investment accounts (excludes 401k, IRA, Roth)"
          />
          <MetricCard
            title="Retirement Balance"
            value={formatCurrency(data.retirement_balance)}
            change={6.8}
            changeLabel="YTD growth"
            icon={<PiggyBank />}
            trend="up"
            description="401k, IRA, and Roth retirement accounts"
          />
          <MetricCard
            title="Current Ages"
            value={`${calculateAge(JASON_BIRTH_DATE)} / ${calculateAge(HAVILAH_BIRTH_DATE)}`}
            change={0}
            changeLabel="Jason / Havilah"
            icon={<Calendar />}
            trend="neutral"
          />
        </div>

        {/* Financial Health Score */}
        {(() => {
          const healthMetrics = convertToHealthMetrics(statusQuoScenario, data)
          return healthMetrics ? (
            <FinancialHealthScore 
              metrics={healthMetrics} 
              className="mb-6"
            />
          ) : null
        })()}

        {/* House Information */}
        <HouseInformationCard />

        {/* Default Scenario Selector */}
        {statusQuoScenario && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Current Dashboard Scenario</span>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => router.push('/scenarios')}
                >
                  Change Scenario
                </Button>
              </CardTitle>
              <CardDescription>
                Dashboard metrics and projections are based on: <strong>{statusQuoScenario.name}</strong>
              </CardDescription>
            </CardHeader>
          </Card>
        )}

        {/* Life Planning Decision Summary */}
        <Card className="mb-6 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
          <CardHeader>
            <CardTitle className="flex items-center text-xl">
              <MapPin className="mr-2 h-6 w-6" />
              Critical Life Decision: Should We Move?
            </CardTitle>
            <CardDescription className="text-blue-100">
              Your family is approaching key education milestones that could significantly impact your financial future
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-4 mb-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-white">$1.79M</div>
                <div className="text-sm text-blue-100">Potential NPV Savings</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-white">2025</div>
                <div className="text-sm text-blue-100">Optimal Move Year</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-white">Minnesota</div>
                <div className="text-sm text-blue-100">Best Location</div>
              </div>
            </div>
            <Button 
              className="w-full bg-white text-blue-600 hover:bg-blue-50 font-semibold"
              onClick={() => router.push('/life-planning')}
            >
              <ArrowRight className="mr-2 h-4 w-4" />
              Analyze Full Life Planning Decision
            </Button>
          </CardContent>
        </Card>

        {/* Charts and Activity */}
        <div className="grid gap-6 lg:grid-cols-3 mb-8">
          <div className="lg:col-span-2 space-y-6">
            {/* Year Range Control - Only render on client */}
            {isClient && (
              <YearRangeControl
                value={yearRange}
                onChange={setYearRange}
                startYear={startYear}
                onStartYearChange={setStartYear}
                compact={true}
                className="w-fit"
              />
            )}
            
            <Card>
              <CardHeader>
                <CardTitle>Net Worth Projection</CardTitle>
                <CardDescription>
                  Based on {statusQuoScenario ? statusQuoScenario.name : 'default scenario'} - projected growth over {isClient ? yearRange : 5} years ({isClient ? startYear : new Date().getFullYear()} - {isClient ? endYear : new Date().getFullYear() + 4})
                </CardDescription>
              </CardHeader>
              <CardContent>
                <NetWorthProjectionChart 
                  data={generateProjectionData(
                    statusQuoScenario, 
                    isClient ? yearRange : 5, 
                    isClient ? startYear : new Date().getFullYear()
                  )}
                  className="h-[400px]"
                />
              </CardContent>
            </Card>
          </div>
          <div className="space-y-6">
            <QuickActions router={router} />
            <LifePlanningInsights router={router} />
          </div>
        </div>

        {/* Expense Breakdown */}
        {statusQuoScenario && (() => {
          try {
            const userData = JSON.parse(statusQuoScenario.user_data || '{}')
            const expenses = userData.expenses || []
            const totalExpenses = expenses.reduce((sum: number, expense: any) => sum + (expense.annual_amount || 0), 0)
            
            // Debug logging
            console.log('Dashboard: Processing expenses for breakdown:', expenses)
            console.log('Dashboard: Sample expense with line items:', expenses.find((e: any) => e.line_items))
            
            if (expenses.length > 0) {
              return (
                <DetailedExpenseBreakdown 
                  expenses={expenses}
                  totalAnnualExpenses={totalExpenses}
                  yearRange={isClient ? yearRange : 5}
                  startYear={isClient ? startYear : new Date().getFullYear()}
                  currentAge={userData.current_age || 52}
                  className="mb-8"
                />
              )
            }
          } catch (error) {
            console.error('Error parsing expense data:', error)
          }
          return null
        })()}

        {/* Scenarios Overview */}
        <Card>
          <CardHeader>
            <CardTitle>Scenario Overview</CardTitle>
            <CardDescription>
              Your financial planning scenarios and their projections
            </CardDescription>
          </CardHeader>
          <CardContent>
            
            {/* Use dynamic scenarios first, then manual scenarios */}
            {(dynamicScenarios.length === 0 && manualScenarios.length === 0) ? (
              <div className="text-center py-12">
                <Target className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium text-foreground mb-2">
                  No scenarios yet
                </h3>
                <p className="text-muted-foreground mb-6">
                  Create your first financial scenario to start planning your future.
                </p>
                <Button onClick={() => router.push('/scenario-builder')}>
                  <Plus className="mr-2 h-4 w-4" />
                  Create First Scenario
                </Button>
              </div>
            ) : (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {/* Show dynamic scenarios if available, otherwise manual scenarios */}
                {(dynamicScenarios.length > 0 ? dynamicScenarios : manualScenarios).map((scenario) => {
                  const isCurrentDefault = statusQuoScenario?.id === scenario.id
                  
                  return (
                    <Card key={scenario.id} 
                          className={`hover:shadow-lg transition-shadow duration-200 cursor-pointer ${
                            isCurrentDefault ? 'ring-2 ring-primary bg-primary/5' : ''
                          }`}
                          onClick={() => {
                            // Route to appropriate detail page based on scenario type
                            if ('location' in scenario) {
                              router.push(`/dynamic-scenarios/${scenario.id}`)
                            } else {
                              router.push(`/scenarios/${scenario.id}`)
                            }
                          }}>
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <CardTitle className="text-lg">{scenario.name}</CardTitle>
                            <CardDescription>
                              {'description' in scenario ? scenario.description : 
                               'location' in scenario ? `${scenario.location} - ${scenario.housing} - ${scenario.school_type}` : 
                               'Dynamic scenario'}
                            </CardDescription>
                          </div>
                          {isCurrentDefault && (
                            <div className="ml-2">
                              <div className="px-2 py-1 bg-primary text-primary-foreground text-xs rounded-full font-medium">
                                Dashboard Default
                              </div>
                            </div>
                          )}
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Type:</span>
                            <span className="capitalize">
                              {'scenario_type' in scenario ? (scenario.scenario_type?.replace('_', ' ') || 'Unknown') : 
                               'location' in scenario ? 'Dynamic' : 'Unknown'}
                            </span>
                          </div>
                          
                          {/* Dynamic scenario info */}
                          {'location' in scenario ? (
                            <>
                              <div className="flex justify-between">
                                <span className="text-muted-foreground">Location:</span>
                                <span>{scenario.location}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-muted-foreground">Housing:</span>
                                <span>{scenario.housing}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-muted-foreground">School:</span>
                                <span>{scenario.school_type}</span>
                              </div>
                              {scenario.projection_results && (
                                <div className="flex justify-between">
                                  <span className="text-muted-foreground">Projected Net Worth:</span>
                                  <span>{formatCurrency(scenario.projection_results.final_net_worth)}</span>
                                </div>
                              )}
                            </>
                          ) : (
                            <>
                              <div className="flex justify-between">
                                <span className="text-muted-foreground">Age Range:</span>
                                <span>
                                  {'user_profile' in scenario ? `${scenario.user_profile?.current_age || 'N/A'} - ${scenario.user_profile?.retirement_age || 'N/A'}` : 'N/A'}
                                </span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-muted-foreground">Salary:</span>
                                <span>
                                  {'user_profile' in scenario ? formatCurrency(scenario.user_profile?.annual_salary || 0) : 'N/A'}
                                </span>
                              </div>
                            </>
                          )}
                          
                          {/* House Information Display - only for manual scenarios */}
                          {'user_data' in scenario && (() => {
                            try {
                              const userData = JSON.parse(scenario.user_data || '{}')
                              const houseData = userData.house || userData.new_house
                              const assets = userData.assets || []
                              const houseAsset = assets.find((asset: any) => 
                                asset.name?.toLowerCase().includes('residence')
                              )
                              
                              if (houseData || houseAsset) {
                                const houseValue = houseData?.value || houseAsset?.current_value || 0
                                const description = houseData?.description || 'House'
                                
                                return (
                                  <div className="flex justify-between">
                                    <span className="text-muted-foreground">🏠 {description}:</span>
                                    <span>{formatCurrency(houseValue)}</span>
                                  </div>
                                )
                              }
                            } catch (error) {
                              // Silently handle parsing errors
                            }
                            return null
                          })()}
                        </div>
                        <div className="mt-4 space-y-2">
                          <Button variant="outline" className="w-full"
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    // Route to appropriate detail page based on scenario type
                                    if ('location' in scenario) {
                                      router.push(`/dynamic-scenarios/${scenario.id}`)
                                    } else {
                                      router.push(`/scenarios/${scenario.id}`)
                                    }
                                  }}>
                            View Details
                          </Button>
                          {!isCurrentDefault && (
                            <Button variant="ghost" size="sm" className="w-full text-xs"
                                    onClick={(e) => {
                                      e.stopPropagation()
                                      // Fetch full scenario details when setting as default directly from backend
                                      fetch(getAPIUrl(`/api/scenarios/${scenario.id}`))
                                        .then(res => res.json())
                                        .then(fullScenario => {
                                          setStatusQuoScenario(fullScenario)
                                        })
                                        .catch(err => {
                                          console.error('Failed to load full scenario:', err)
                                          setStatusQuoScenario(scenario)
                                        })
                                    }}>
                              Set as Dashboard Default
                            </Button>
                          )}
                        </div>
                    </CardContent>
                  </Card>
                  )
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  )
}