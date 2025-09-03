'use client'

import { useState } from 'react'
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
  Play
} from 'lucide-react'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { YearRangeControl } from '@/components/ui/year-range-control'
import { useScenario, useProjections } from '@/hooks/use-scenarios'
import { useYearRangeStore } from '@/stores/app-store'
import { formatCurrency, formatPercentage } from '@/lib/utils'
import { NetWorthProjectionChart } from '@/components/charts/responsive-container'
import { DetailedExpenseBreakdown } from '@/components/features/expense-breakdown/detailed-breakdown'

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

interface ScenarioDetailProps {
  scenarioId: string
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

function ScenarioHeader({ scenario }: { scenario: any }) {
  const router = useRouter()
  
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
                <Badge variant="secondary" className="capitalize">
                  {scenario.scenario_type?.replace('_', ' ') || 'Unknown'}
                </Badge>
                <span className="text-sm text-muted-foreground">
                  Created: {new Date(scenario.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
          <div className="flex space-x-2">
            <Button>
              <Play className="mr-2 h-4 w-4" />
              Run Projection
            </Button>
            <Button variant="outline">
              <Settings className="mr-2 h-4 w-4" />
              Edit
            </Button>
          </div>
        </div>
      </div>
    </header>
  )
}

function UserProfile({ scenario }: { scenario: any }) {
  // Parse user_data JSON string
  let userData = null
  try {
    userData = JSON.parse(scenario.user_data || '{}')
  } catch (error) {
    console.error('Error parsing user_data:', error)
  }

  if (!userData) return null

  // Extract parent names (assuming format like "Havilah & Jason")
  const fullName = userData.name || ''
  const parentNames = fullName.includes(' & ') ? fullName.split(' & ') : [fullName]
  const isCouple = parentNames.length === 2

  // Separate assets by parent based on initials (HG = Havilah G, JG = Jason G)
  const getParentAssets = (parentInitial: string) => {
    return userData.assets?.filter((asset: any) => 
      asset.name?.startsWith(parentInitial) || 
      (parentInitial === 'Joint' && (!asset.name?.startsWith('HG') && !asset.name?.startsWith('JG')))
    ) || []
  }

  const havilahAssets = getParentAssets('HG')
  const jasonAssets = getParentAssets('JG')
  const jointAssets = getParentAssets('Joint')

  const calculateTotalValue = (assets: any[]) => 
    assets.reduce((sum, asset) => sum + (asset.current_value || 0), 0)

  if (isCouple) {
    return (
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Havilah's Profile */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-sm font-semibold text-blue-600">H</span>
              </div>
              <span>{parentNames[0]}'s Profile</span>
            </CardTitle>
            <CardDescription>Personal and financial information</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-sm text-muted-foreground">Current Age</span>
                <p className="font-medium">{calculateAge(HAVILAH_BIRTH_DATE)}</p>
                <span className="text-xs text-muted-foreground">Birth: July 15, 1974</span>
              </div>
              <div>
                <span className="text-sm text-muted-foreground">Retirement Age</span>
                <p className="font-medium">{userData.retirement_age || 'N/A'}</p>
              </div>
              <div>
                <span className="text-sm text-muted-foreground">Life Expectancy</span>
                <p className="font-medium">{userData.life_expectancy || 'N/A'}</p>
              </div>
              <div>
                <span className="text-sm text-muted-foreground">Birth Date</span>
                <p className="font-medium">July 15, 1974</p>
              </div>
            </div>
            <div className="pt-2 border-t">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Individual Assets</span>
                <span className="font-semibold text-blue-600">{formatCurrency(calculateTotalValue(havilahAssets))}</span>
              </div>
              <p className="text-xs text-muted-foreground mt-1">{havilahAssets.length} accounts</p>
            </div>
          </CardContent>
        </Card>

        {/* Jason's Profile */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <div className="h-8 w-8 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-sm font-semibold text-green-600">J</span>
              </div>
              <span>{parentNames[1]}'s Profile</span>
            </CardTitle>
            <CardDescription>Personal and financial information</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-sm text-muted-foreground">Current Age</span>
                <p className="font-medium">{calculateAge(JASON_BIRTH_DATE)}</p>
                <span className="text-xs text-muted-foreground">Birth: March 24, 1973</span>
              </div>
              <div>
                <span className="text-sm text-muted-foreground">Retirement Age</span>
                <p className="font-medium">{userData.retirement_age || 'N/A'}</p>
              </div>
              <div>
                <span className="text-sm text-muted-foreground">Life Expectancy</span>
                <p className="font-medium">{userData.life_expectancy || 'N/A'}</p>
              </div>
              <div>
                <span className="text-sm text-muted-foreground">Birth Date</span>
                <p className="font-medium">March 24, 1973</p>
              </div>
            </div>
            <div className="pt-2 border-t">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Individual Assets</span>
                <span className="font-semibold text-green-600">{formatCurrency(calculateTotalValue(jasonAssets))}</span>
              </div>
              <p className="text-xs text-muted-foreground mt-1">{jasonAssets.length} accounts</p>
            </div>
          </CardContent>
        </Card>

        {/* Joint Information */}
        {jointAssets.length > 0 && (
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <div className="h-8 w-8 bg-purple-100 rounded-full flex items-center justify-center">
                  <span className="text-sm font-semibold text-purple-600">J&H</span>
                </div>
                <span>Joint Assets</span>
              </CardTitle>
              <CardDescription>Shared financial accounts and information</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <span className="text-sm text-muted-foreground">Current City</span>
                  <p className="font-medium">{userData.current_city || 'N/A'}</p>
                </div>
                <div>
                  <span className="text-sm text-muted-foreground">Target City</span>
                  <p className="font-medium">{userData.target_city || 'None'}</p>
                </div>
                <div>
                  <span className="text-sm text-muted-foreground">Joint Assets</span>
                  <p className="font-medium text-purple-600">{formatCurrency(calculateTotalValue(jointAssets))}</p>
                </div>
                <div>
                  <span className="text-sm text-muted-foreground">Total Household</span>
                  <p className="font-medium">{formatCurrency(calculateTotalValue(userData.assets))}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    )
  }

  // Single person fallback
  return (
    <Card>
      <CardHeader>
        <CardTitle>Personal Profile</CardTitle>
        <CardDescription>Core demographic and financial information</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <span className="text-sm text-muted-foreground">Name</span>
            <p className="font-medium">{userData.name || 'N/A'}</p>
          </div>
          <div>
            <span className="text-sm text-muted-foreground">Current Age</span>
            <p className="font-medium">{userData.current_age || 'N/A'}</p>
          </div>
          <div>
            <span className="text-sm text-muted-foreground">Retirement Age</span>
            <p className="font-medium">{userData.retirement_age || 'N/A'}</p>
          </div>
          <div>
            <span className="text-sm text-muted-foreground">Life Expectancy</span>
            <p className="font-medium">{userData.life_expectancy || 'N/A'}</p>
          </div>
          <div>
            <span className="text-sm text-muted-foreground">Current City</span>
            <p className="font-medium">{userData.current_city || 'N/A'}</p>
          </div>
          <div>
            <span className="text-sm text-muted-foreground">Annual Salary</span>
            <p className="font-medium">{formatCurrency(userData.annual_salary || 0)}</p>
          </div>
          <div>
            <span className="text-sm text-muted-foreground">Birth Date</span>
            <p className="font-medium">{userData.havilah_birth_date ? new Date(userData.havilah_birth_date).toLocaleDateString() : userData.jason_birth_date ? new Date(userData.jason_birth_date).toLocaleDateString() : 'N/A'}</p>
          </div>
          <div>
            <span className="text-sm text-muted-foreground">Target City</span>
            <p className="font-medium">{userData.target_city || 'None'}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function HouseInformation({ scenario }: { scenario: any }) {
  // Parse user_data to get house information
  let userData = null
  try {
    userData = JSON.parse(scenario.user_data || '{}')
  } catch (error) {
    console.error('Error parsing user_data for house info:', error)
    return null
  }

  // Get house data from various sources
  const houseData = userData.house || userData.new_house
  const assets = userData.assets || []
  const houseAsset = assets.find((asset: any) => 
    asset.name?.toLowerCase().includes('residence')
  )

  // If no house data available, don't render anything
  if (!houseData && !houseAsset) {
    return null
  }

  const houseValue = houseData?.value || houseAsset?.current_value || 0
  const mortgageBalance = houseData?.mortgage_principal || houseAsset?.mortgage_balance || 0
  const description = houseData?.description || houseAsset?.name || 'Primary Residence'
  const netEquity = houseValue - mortgageBalance
  const monthlyPayment = houseData?.monthly_payment || 0
  const propertyTax = houseData?.annual_property_tax || 0
  const growthRate = houseData?.annual_growth_rate || houseAsset?.expected_return || 0
  const costBasis = houseData?.cost_basis || 0

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Home className="h-5 w-5 mr-2" />
          House Information
        </CardTitle>
        <CardDescription>
          Property details and financial information
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <span className="text-sm text-muted-foreground">Property</span>
            <p className="font-medium">{description}</p>
          </div>
          <div>
            <span className="text-sm text-muted-foreground">Current Value</span>
            <p className="font-medium text-green-600">{formatCurrency(houseValue)}</p>
          </div>
          <div>
            <span className="text-sm text-muted-foreground">Mortgage Balance</span>
            <p className="font-medium text-red-600">{formatCurrency(mortgageBalance)}</p>
          </div>
          <div>
            <span className="text-sm text-muted-foreground">Net Equity</span>
            <p className="font-medium text-blue-600">{formatCurrency(netEquity)}</p>
          </div>
          {costBasis > 0 && (
            <div>
              <span className="text-sm text-muted-foreground">Cost Basis</span>
              <p className="font-medium">{formatCurrency(costBasis)}</p>
            </div>
          )}
          {monthlyPayment > 0 && (
            <div>
              <span className="text-sm text-muted-foreground">Monthly Payment</span>
              <p className="font-medium">{formatCurrency(monthlyPayment)}</p>
            </div>
          )}
          {propertyTax > 0 && (
            <div>
              <span className="text-sm text-muted-foreground">Annual Property Tax</span>
              <p className="font-medium">{formatCurrency(propertyTax)}</p>
            </div>
          )}
          {growthRate > 0 && (
            <div>
              <span className="text-sm text-muted-foreground">Growth Rate</span>
              <p className="font-medium">{formatPercentage(growthRate, 1)}</p>
            </div>
          )}
        </div>
        
        {/* Additional house details if available */}
        {houseData && (
          <div className="mt-4 pt-4 border-t">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
              {houseData.interest_rate > 0 && (
                <div>
                  <span className="text-muted-foreground">Interest Rate:</span>
                  <span className="ml-2 font-medium">{formatPercentage(houseData.interest_rate, 2)}</span>
                </div>
              )}
              {houseData.payments_made > 0 && (
                <div>
                  <span className="text-muted-foreground">Payments Made:</span>
                  <span className="ml-2 font-medium">{houseData.payments_made}/{houseData.number_of_payments}</span>
                </div>
              )}
              {houseData.commission_rate > 0 && (
                <div>
                  <span className="text-muted-foreground">Sale Commission:</span>
                  <span className="ml-2 font-medium">{formatPercentage(houseData.commission_rate, 1)}</span>
                </div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function FinancialDetails({ scenario }: { scenario: any }) {
  // Parse user_data to get assets and expenses
  let userData = null
  try {
    userData = JSON.parse(scenario.user_data || '{}')
  } catch (error) {
    console.error('Error parsing user_data for financial details:', error)
    return null
  }

  // Calculate totals from assets
  const totalAssets = userData.assets?.filter((asset: any) => 
    !asset.name?.toLowerCase().includes('principal') && 
    !asset.name?.toLowerCase().includes('total') && 
    !asset.name?.toLowerCase().includes('summary') &&
    !asset.name?.toLowerCase().includes('general investment account')
  ).reduce((sum: number, asset: any) => sum + (asset.current_value || 0), 0) || 0
  const totalExpenses = userData.expenses?.reduce((sum: number, expense: any) => sum + (expense.annual_amount || 0), 0) || 0
  const retirementAccounts = userData.assets?.filter((asset: any) => 
    (asset.name?.includes('401') || asset.name?.includes('IRA') || asset.name?.includes('Roth')) &&
    !asset.name?.toLowerCase().includes('principal') && 
    !asset.name?.toLowerCase().includes('total') && 
    !asset.name?.toLowerCase().includes('summary') &&
    !asset.name?.toLowerCase().includes('general investment account')
  ) || []
  const totalRetirement = retirementAccounts.reduce((sum: number, account: any) => sum + (account.current_value || 0), 0)

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Assets</CardTitle>
          <TrendingUp className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {formatCurrency(totalAssets)}
          </div>
          <p className="text-xs text-muted-foreground">
            {userData.assets?.length || 0} accounts
          </p>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Retirement Accounts</CardTitle>
          <PiggyBank className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {formatCurrency(totalRetirement)}
          </div>
          <p className="text-xs text-muted-foreground">
            {retirementAccounts.length} accounts
          </p>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Annual Expenses</CardTitle>
          <BarChart3 className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {formatCurrency(totalExpenses)}
          </div>
          <p className="text-xs text-muted-foreground">
            {userData.expenses?.length || 0} categories
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Annual Salary</CardTitle>
          <TrendingUp className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {formatCurrency(userData.annual_salary || 0)}
          </div>
          <p className="text-xs text-muted-foreground">
            Current income
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

export function ScenarioDetail({ scenarioId }: ScenarioDetailProps) {
  const { scenario, isLoading, error, refetch } = useScenario(scenarioId)
  const { runProjection, isRunningProjection } = useProjections()
  
  // Year range controls from global state
  const { 
    yearRange, 
    startYear, 
    endYear,
    setYearRange, 
    setStartYear,
    isYearInRange
  } = useYearRangeStore()

  if (isLoading) return <LoadingState />
  if (error) return <ErrorState error={error.message} onRetry={() => refetch()} />
  if (!scenario) return <ErrorState error="Scenario not found" onRetry={() => refetch()} />

  return (
    <div className="min-h-screen bg-background">
      <ScenarioHeader scenario={scenario} />
      
      <main className="container mx-auto px-6 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="space-y-8"
        >
          <UserProfile scenario={scenario} />
          
          <HouseInformation scenario={scenario} />
          
          <FinancialDetails scenario={scenario} />

          {/* Year Range Control */}
          <YearRangeControl
            value={yearRange}
            onChange={setYearRange}
            startYear={startYear}
            onStartYearChange={setStartYear}
            showAdvanced={true}
            className="mb-4"
          />

          <Tabs defaultValue="overview" className="space-y-4">
            <TabsList>
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="projections">Projections</TabsTrigger>
              <TabsTrigger value="assumptions">Assumptions</TabsTrigger>
              <TabsTrigger value="goals">Goals</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-4">
              {(() => {
                let userData = null
                try {
                  userData = JSON.parse(scenario.user_data || '{}')
                } catch (error) {
                  console.error('Error parsing user_data in overview:', error)
                }

                // Separate assets by parent
                const getParentAssets = (parentInitial: string) => {
                  return userData?.assets?.filter((asset: any) => 
                    asset.name?.startsWith(parentInitial) || 
                    (parentInitial === 'Joint' && (!asset.name?.startsWith('HG') && !asset.name?.startsWith('JG')))
                  ) || []
                }

                const havilahAssets = getParentAssets('HG')
                const jasonAssets = getParentAssets('JG')
                const jointAssets = getParentAssets('Joint')

                const renderAssetList = (assets: any[], color: string, initial: string) => (
                  <div className="space-y-2">
                    {assets.map((asset: any, index: number) => (
                      <div key={index} className="flex justify-between items-center py-2 border-b border-border/50 last:border-0">
                        <div>
                          <p className="font-medium text-sm">{asset.name}</p>
                          <p className="text-xs text-muted-foreground">
                            {asset.asset_type} • {formatPercentage(asset.expected_return || 0)} expected return
                          </p>
                        </div>
                        <div className="text-right">
                          <p className={`font-medium ${color}`}>{formatCurrency(asset.current_value || 0)}</p>
                          <p className="text-xs text-muted-foreground">
                            {formatPercentage(asset.allocation_percentage || 0)} allocation
                          </p>
                        </div>
                      </div>
                    ))}
                    {assets.length === 0 && (
                      <p className="text-muted-foreground text-sm py-4">No individual assets</p>
                    )}
                  </div>
                )

                return (
                  <div className="space-y-6">
                    {/* Parent Assets Breakdown */}
                    <div className="grid gap-6 lg:grid-cols-2">
                      {/* Havilah's Assets */}
                      <Card>
                        <CardHeader>
                          <CardTitle className="flex items-center space-x-2">
                            <div className="h-6 w-6 bg-blue-100 rounded-full flex items-center justify-center">
                              <span className="text-xs font-semibold text-blue-600">H</span>
                            </div>
                            <span>Havilah's Assets</span>
                          </CardTitle>
                          <CardDescription>
                            Individual investment accounts ({havilahAssets.length} accounts)
                          </CardDescription>
                        </CardHeader>
                        <CardContent>
                          {renderAssetList(havilahAssets, 'text-blue-600', 'H')}
                        </CardContent>
                      </Card>

                      {/* Jason's Assets */}
                      <Card>
                        <CardHeader>
                          <CardTitle className="flex items-center space-x-2">
                            <div className="h-6 w-6 bg-green-100 rounded-full flex items-center justify-center">
                              <span className="text-xs font-semibold text-green-600">J</span>
                            </div>
                            <span>Jason's Assets</span>
                          </CardTitle>
                          <CardDescription>
                            Individual investment accounts ({jasonAssets.length} accounts)
                          </CardDescription>
                        </CardHeader>
                        <CardContent>
                          {renderAssetList(jasonAssets, 'text-green-600', 'J')}
                        </CardContent>
                      </Card>
                    </div>

                    {/* Joint Assets */}
                    {jointAssets.length > 0 && (
                      <Card>
                        <CardHeader>
                          <CardTitle className="flex items-center space-x-2">
                            <div className="h-6 w-6 bg-purple-100 rounded-full flex items-center justify-center">
                              <span className="text-xs font-semibold text-purple-600">J&H</span>
                            </div>
                            <span>Joint Assets</span>
                          </CardTitle>
                          <CardDescription>
                            Shared investment accounts ({jointAssets.length} accounts)
                          </CardDescription>
                        </CardHeader>
                        <CardContent>
                          {renderAssetList(jointAssets, 'text-purple-600', 'J&H')}
                        </CardContent>
                      </Card>
                    )}

                    {/* Enhanced Expenses Breakdown with Line Items */}
                    {userData?.expenses && userData.expenses.length > 0 && (
                      <DetailedExpenseBreakdown 
                        expenses={userData.expenses}
                        totalAnnualExpenses={userData.expenses.reduce((sum: number, expense: any) => sum + (expense.annual_amount || 0), 0)}
                        yearRange={yearRange}
                        startYear={startYear}
                        currentAge={userData.current_age || 52}
                        className=""
                      />
                    )}
                  </div>
                )
              })()}
            </TabsContent>

            <TabsContent value="projections" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Financial Projections</CardTitle>
                  <CardDescription>
                    Long-term financial projections and growth scenarios
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-center h-64 text-muted-foreground">
                    <div className="text-center space-y-4">
                      <Calculator className="h-12 w-12 mx-auto" />
                      <p>No projections available yet</p>
                      <Button
                        onClick={() => runProjection({ scenarioId })}
                        disabled={isRunningProjection}
                      >
                        {isRunningProjection ? 'Running...' : 'Run Projection'}
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="assumptions" className="space-y-4">
              {(() => {
                let projectionData = null
                try {
                  projectionData = JSON.parse(scenario.projection_data || '{}')
                } catch (error) {
                  console.error('Error parsing projection_data:', error)
                }

                const assumptions = projectionData?.assumptions || {}
                const monteCarlo = projectionData?.monte_carlo || {}

                return (
                  <div className="grid gap-6 lg:grid-cols-2">
                    {/* Economic Assumptions */}
                    <Card>
                      <CardHeader>
                        <CardTitle>Economic Assumptions</CardTitle>
                        <CardDescription>
                          Key economic parameters used in projections
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <span className="text-sm text-muted-foreground">Inflation Rate</span>
                              <p className="font-medium">{formatPercentage(assumptions.inflation_rate || 0)}</p>
                            </div>
                            <div>
                              <span className="text-sm text-muted-foreground">Investment Return</span>
                              <p className="font-medium">{formatPercentage(assumptions.investment_return || 0)}</p>
                            </div>
                            <div>
                              <span className="text-sm text-muted-foreground">Salary Growth</span>
                              <p className="font-medium">{formatPercentage(assumptions.salary_growth_rate || 0)}</p>
                            </div>
                            <div>
                              <span className="text-sm text-muted-foreground">Social Security COLA</span>
                              <p className="font-medium">{formatPercentage(assumptions.social_security_cola || 0)}</p>
                            </div>
                            <div>
                              <span className="text-sm text-muted-foreground">Tax Rate</span>
                              <p className="font-medium">{formatPercentage(assumptions.tax_rate || 0)}</p>
                            </div>
                          </div>
                          
                          <div className="pt-4 border-t">
                            <div className="flex items-center space-x-4 text-sm">
                              <span className="text-muted-foreground">Include Social Security:</span>
                              <span className="font-medium">{projectionData?.include_social_security ? 'Yes' : 'No'}</span>
                            </div>
                            <div className="flex items-center space-x-4 text-sm mt-2">
                              <span className="text-muted-foreground">Include Inflation:</span>
                              <span className="font-medium">{projectionData?.include_inflation ? 'Yes' : 'No'}</span>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    {/* Monte Carlo Settings */}
                    <Card>
                      <CardHeader>
                        <CardTitle>Monte Carlo Parameters</CardTitle>
                        <CardDescription>
                          Risk modeling and simulation settings
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <span className="text-sm text-muted-foreground">Simulations</span>
                              <p className="font-medium">{monteCarlo.num_simulations || 'N/A'}</p>
                            </div>
                            <div>
                              <span className="text-sm text-muted-foreground">Stock Volatility</span>
                              <p className="font-medium">{formatPercentage(monteCarlo.stock_volatility || 0)}</p>
                            </div>
                            <div>
                              <span className="text-sm text-muted-foreground">Bond Volatility</span>
                              <p className="font-medium">{formatPercentage(monteCarlo.bond_volatility || 0)}</p>
                            </div>
                            <div>
                              <span className="text-sm text-muted-foreground">Stock/Bond Correlation</span>
                              <p className="font-medium">{monteCarlo.correlation_stock_bond || 'N/A'}</p>
                            </div>
                          </div>
                          
                          <div className="pt-4 border-t">
                            <div className="flex items-center space-x-4 text-sm">
                              <span className="text-muted-foreground">Sequence Risk Adjustment:</span>
                              <span className="font-medium">{monteCarlo.sequence_risk_adjustment ? 'Yes' : 'No'}</span>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    {/* Projection Settings */}
                    <Card className="lg:col-span-2">
                      <CardHeader>
                        <CardTitle>Projection Settings</CardTitle>
                        <CardDescription>
                          Timeline and projection parameters
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-3 gap-4">
                          <div>
                            <span className="text-sm text-muted-foreground">Start Year</span>
                            <p className="font-medium">{projectionData?.start_year || 'N/A'}</p>
                          </div>
                          <div>
                            <span className="text-sm text-muted-foreground">Projection Years</span>
                            <p className="font-medium">{projectionData?.projection_years || 'N/A'}</p>
                          </div>
                          <div>
                            <span className="text-sm text-muted-foreground">End Year</span>
                            <p className="font-medium">
                              {projectionData?.start_year && projectionData?.projection_years 
                                ? projectionData.start_year + projectionData.projection_years
                                : 'N/A'}
                            </p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                )
              })()}
            </TabsContent>

            <TabsContent value="goals" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Financial Goals</CardTitle>
                  <CardDescription>
                    Target goals and milestones
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center text-muted-foreground py-8">
                    <Target className="h-12 w-12 mx-auto mb-4" />
                    <p>Goals will be displayed here</p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </motion.div>
      </main>
    </div>
  )
}