'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Slider } from '@/components/ui/slider'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { 
  MapPin, 
  Home, 
  GraduationCap, 
  DollarSign, 
  TrendingUp,
  Users,
  Calendar,
  RefreshCw,
  Calculator
} from 'lucide-react'
import { formatCurrency } from '@/lib/utils'

interface WhatIfParams {
  location: string
  housing: string
  schoolType: string
  projectionYears: number
  salaryMultiplier: number
  expenseMultiplier: number
  investmentReturn: number
}

interface WhatIfSlidersProps {
  initialScenario: {
    location: string
    housing: string
    schoolType: string
    projectionYears: number
    spouse1Status: string
    spouse2Status: string
  }
  onParameterChange: (params: WhatIfParams) => void
  isCalculating?: boolean
  results?: {
    finalNetWorth: number
    totalExpenses: number
    monthlyAvailableCash: number
  }
  className?: string
}

export function WhatIfSliders({ 
  initialScenario, 
  onParameterChange, 
  isCalculating = false,
  results,
  className = '' 
}: WhatIfSlidersProps) {
  const [params, setParams] = useState<WhatIfParams>({
    location: initialScenario.location,
    housing: initialScenario.housing,
    schoolType: initialScenario.schoolType,
    projectionYears: initialScenario.projectionYears,
    salaryMultiplier: 1.0,
    expenseMultiplier: 1.0,
    investmentReturn: 0.07
  })

  const [isRealTime, setIsRealTime] = useState(false)

  // Base financial assumptions for calculations
  const baseSalary = 451117
  const baseExpenses = 180000
  const baseNetWorth = 4500000

  // Calculate estimated results based on parameter changes
  const calculateEstimate = (currentParams: WhatIfParams) => {
    const adjustedSalary = baseSalary * currentParams.salaryMultiplier
    const adjustedExpenses = baseExpenses * currentParams.expenseMultiplier
    const netCashFlow = adjustedSalary - adjustedExpenses
    const monthlyAvailableCash = netCashFlow / 12
    
    // Simple compound growth calculation
    const years = currentParams.projectionYears
    const finalNetWorth = baseNetWorth * Math.pow(1 + currentParams.investmentReturn, years) + 
                         (netCashFlow * years * (1 + currentParams.investmentReturn / 2))
    
    return {
      finalNetWorth: Math.max(0, finalNetWorth),
      totalExpenses: adjustedExpenses * years,
      monthlyAvailableCash
    }
  }

  const estimatedResults = calculateEstimate(params)

  const handleParameterChange = (key: keyof WhatIfParams, value: any) => {
    const newParams = { ...params, [key]: value }
    setParams(newParams)
    
    if (isRealTime) {
      onParameterChange(newParams)
    }
  }

  const handleManualUpdate = () => {
    onParameterChange(params)
  }

  const resetToDefaults = () => {
    const defaultParams = {
      location: initialScenario.location,
      housing: initialScenario.housing,
      schoolType: initialScenario.schoolType,
      projectionYears: initialScenario.projectionYears,
      salaryMultiplier: 1.0,
      expenseMultiplier: 1.0,
      investmentReturn: 0.07
    }
    setParams(defaultParams)
    onParameterChange(defaultParams)
  }

  const getLocationMultiplier = (location: string) => {
    switch (location) {
      case 'Sf': return { salary: 1.3, expenses: 1.4 }
      case 'Sd': return { salary: 1.15, expenses: 1.2 }
      case 'Mn': return { salary: 0.9, expenses: 0.85 }
      default: return { salary: 1.0, expenses: 1.0 }
    }
  }

  const getSchoolCost = (schoolType: string) => {
    switch (schoolType) {
      case 'Private': return 124000
      case 'Pripub': return 62000
      case 'Public': return 50000
      default: return 50000
    }
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center">
                <Calculator className="h-5 w-5 mr-2" />
                What-If Analysis
              </CardTitle>
              <CardDescription>
                Adjust parameters to see how changes affect your financial projections
              </CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={resetToDefaults}
              >
                <RefreshCw className="h-4 w-4 mr-1" />
                Reset
              </Button>
              {!isRealTime && (
                <Button
                  onClick={handleManualUpdate}
                  disabled={isCalculating}
                  size="sm"
                >
                  {isCalculating ? 'Calculating...' : 'Update'}
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Parameter Controls */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Adjustable Parameters</CardTitle>
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="realtime"
                checked={isRealTime}
                onChange={(e) => setIsRealTime(e.target.checked)}
              />
              <Label htmlFor="realtime" className="text-sm">
                Real-time updates
              </Label>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Location Selector */}
            <div>
              <Label className="flex items-center mb-3">
                <MapPin className="h-4 w-4 mr-2" />
                Location
              </Label>
              <div className="grid grid-cols-3 gap-2">
                {['Mn', 'Sd', 'Sf'].map((location) => (
                  <Button
                    key={location}
                    variant={params.location === location ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => handleParameterChange('location', location)}
                  >
                    {location === 'Mn' ? 'Minnesota' : location === 'Sd' ? 'San Diego' : 'San Francisco'}
                  </Button>
                ))}
              </div>
              <div className="text-xs text-muted-foreground mt-1">
                {(() => {
                  const mult = getLocationMultiplier(params.location)
                  return `Salary: ${(mult.salary * 100).toFixed(0)}%, Expenses: ${(mult.expenses * 100).toFixed(0)}%`
                })()}
              </div>
            </div>

            {/* Housing Type */}
            <div>
              <Label className="flex items-center mb-3">
                <Home className="h-4 w-4 mr-2" />
                Housing
              </Label>
              <div className="grid grid-cols-2 gap-2">
                {['Own', 'Rent'].map((housing) => (
                  <Button
                    key={housing}
                    variant={params.housing === housing ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => handleParameterChange('housing', housing)}
                  >
                    {housing}
                  </Button>
                ))}
              </div>
            </div>

            {/* Education Type */}
            <div>
              <Label className="flex items-center mb-3">
                <GraduationCap className="h-4 w-4 mr-2" />
                Education Strategy
              </Label>
              <div className="grid grid-cols-3 gap-2">
                {['Public', 'Pripub', 'Private'].map((school) => (
                  <Button
                    key={school}
                    variant={params.schoolType === school ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => handleParameterChange('schoolType', school)}
                  >
                    {school === 'Pripub' ? 'Mixed' : school}
                  </Button>
                ))}
              </div>
              <div className="text-xs text-muted-foreground mt-1">
                Annual cost: {formatCurrency(getSchoolCost(params.schoolType))}
              </div>
            </div>

            {/* Projection Years */}
            <div>
              <Label className="flex items-center mb-3">
                <Calendar className="h-4 w-4 mr-2" />
                Projection Years: {params.projectionYears}
              </Label>
              <Slider
                value={[params.projectionYears]}
                onValueChange={([value]) => handleParameterChange('projectionYears', value)}
                min={2}
                max={15}
                step={1}
                className="w-full"
              />
            </div>

            {/* Salary Multiplier */}
            <div>
              <Label className="flex items-center mb-3">
                <DollarSign className="h-4 w-4 mr-2" />
                Salary Adjustment: {(params.salaryMultiplier * 100).toFixed(0)}%
              </Label>
              <Slider
                value={[params.salaryMultiplier]}
                onValueChange={([value]) => handleParameterChange('salaryMultiplier', value)}
                min={0.5}
                max={2.0}
                step={0.05}
                className="w-full"
              />
              <div className="text-xs text-muted-foreground mt-1">
                Adjusted salary: {formatCurrency(baseSalary * params.salaryMultiplier)}
              </div>
            </div>

            {/* Expense Multiplier */}
            <div>
              <Label className="flex items-center mb-3">
                <TrendingUp className="h-4 w-4 mr-2" />
                Expense Adjustment: {(params.expenseMultiplier * 100).toFixed(0)}%
              </Label>
              <Slider
                value={[params.expenseMultiplier]}
                onValueChange={([value]) => handleParameterChange('expenseMultiplier', value)}
                min={0.5}
                max={1.5}
                step={0.05}
                className="w-full"
              />
              <div className="text-xs text-muted-foreground mt-1">
                Adjusted expenses: {formatCurrency(baseExpenses * params.expenseMultiplier)}
              </div>
            </div>

            {/* Investment Return */}
            <div>
              <Label className="flex items-center mb-3">
                <TrendingUp className="h-4 w-4 mr-2" />
                Investment Return: {(params.investmentReturn * 100).toFixed(1)}%
              </Label>
              <Slider
                value={[params.investmentReturn]}
                onValueChange={([value]) => handleParameterChange('investmentReturn', value)}
                min={0.03}
                max={0.12}
                step={0.005}
                className="w-full"
              />
            </div>
          </CardContent>
        </Card>

        {/* Results Preview */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Impact Preview</CardTitle>
            <CardDescription>
              {isCalculating ? 'Calculating real projections...' : 'Estimated results based on your adjustments'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="p-4 bg-primary/5 rounded-lg">
                <div className="text-2xl font-bold text-primary">
                  {formatCurrency(results?.finalNetWorth || estimatedResults.finalNetWorth)}
                </div>
                <div className="text-sm text-muted-foreground">
                  Projected Net Worth ({params.projectionYears} years)
                </div>
                {results && (
                  <Badge variant="outline" className="mt-1">
                    Real Calculation
                  </Badge>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="text-center">
                  <div className="text-lg font-bold text-green-600">
                    {formatCurrency(results?.monthlyAvailableCash || estimatedResults.monthlyAvailableCash)}
                  </div>
                  <div className="text-sm text-muted-foreground">Monthly Cash Flow</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-orange-600">
                    {formatCurrency(results?.totalExpenses || estimatedResults.totalExpenses)}
                  </div>
                  <div className="text-sm text-muted-foreground">Total Expenses</div>
                </div>
              </div>

              <div className="pt-4 border-t">
                <div className="text-sm font-medium mb-2">Key Changes:</div>
                <div className="space-y-1 text-sm text-muted-foreground">
                  {params.salaryMultiplier !== 1.0 && (
                    <div>• Salary {params.salaryMultiplier > 1 ? 'increased' : 'decreased'} by {Math.abs((params.salaryMultiplier - 1) * 100).toFixed(0)}%</div>
                  )}
                  {params.expenseMultiplier !== 1.0 && (
                    <div>• Expenses {params.expenseMultiplier > 1 ? 'increased' : 'decreased'} by {Math.abs((params.expenseMultiplier - 1) * 100).toFixed(0)}%</div>
                  )}
                  {params.investmentReturn !== 0.07 && (
                    <div>• Investment return adjusted to {(params.investmentReturn * 100).toFixed(1)}%</div>
                  )}
                  {params.projectionYears !== initialScenario.projectionYears && (
                    <div>• Timeline adjusted to {params.projectionYears} years</div>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}