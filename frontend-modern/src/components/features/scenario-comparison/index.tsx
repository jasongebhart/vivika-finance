'use client'

import { useState, useEffect, useMemo } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { motion } from 'framer-motion'
import {
  ArrowLeft,
  Plus,
  X,
  Edit3,
  TrendingUp,
  BarChart3,
  Calculator,
  Settings,
  Save,
  RotateCcw
} from 'lucide-react'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useScenarios, useProjections } from '@/hooks/use-scenarios'
import { useToast } from '@/hooks/use-toast'
import { formatCurrency, formatPercentage } from '@/lib/utils'
import type { Scenario } from '@/types'

interface EditableScenarioData {
  id: string
  name: string
  user_profile: {
    current_age: number
    retirement_age: number
    annual_salary: number
    life_expectancy: number
  }
  assets: Array<{
    name: string
    current_value: number
    expected_return: number
    allocation_percentage: number
  }>
  expenses: Array<{
    name: string
    annual_amount: number
    start_age: number
    end_age?: number
  }>
  assumptions: {
    inflation_rate: number
    investment_return: number
    salary_growth_rate: number
    tax_rate: number
  }
}

// Helper function to extract timeline information from scenario names
function extractTimelineInfo(scenarioName: string) {
  const timelineMatch = scenarioName.match(/(\d+)yrs?/i)
  if (timelineMatch) {
    const years = parseInt(timelineMatch[1])
    return {
      years,
      label: `${years} Year${years !== 1 ? 's' : ''}`,
      color: getTimelineColor(years)
    }
  }
  return null
}

// Get color based on timeline years
function getTimelineColor(years: number) {
  switch (years) {
    case 2: return { bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-200' }
    case 4: return { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-200' }
    case 6: return { bg: 'bg-yellow-100', text: 'text-yellow-700', border: 'border-yellow-200' }
    case 8: return { bg: 'bg-red-100', text: 'text-red-700', border: 'border-red-200' }
    default: return { bg: 'bg-gray-100', text: 'text-gray-700', border: 'border-gray-200' }
  }
}

// Extract base strategy name (everything before the year indicator)
function extractBaseStrategy(scenarioName: string) {
  const timelineMatch = scenarioName.match(/(.+?)\s*\d+yrs?/i)
  if (timelineMatch) {
    return timelineMatch[1].trim()
  }
  return scenarioName
}

function ScenarioSelector({ 
  scenarios, 
  selectedIds, 
  onSelectionChange 
}: {
  scenarios: Scenario[]
  selectedIds: string[]
  onSelectionChange: (ids: string[]) => void
}) {
  // Group scenarios by base strategy
  const groupedScenarios = useMemo(() => {
    const groups: Record<string, Scenario[]> = {}
    
    scenarios.forEach(scenario => {
      const baseStrategy = extractBaseStrategy(scenario.name)
      if (!groups[baseStrategy]) {
        groups[baseStrategy] = []
      }
      groups[baseStrategy].push(scenario)
    })
    
    // Sort scenarios within each group by timeline years
    Object.keys(groups).forEach(strategy => {
      groups[strategy].sort((a, b) => {
        const timelineA = extractTimelineInfo(a.name)
        const timelineB = extractTimelineInfo(b.name)
        if (timelineA && timelineB) {
          return timelineA.years - timelineB.years
        }
        return a.name.localeCompare(b.name)
      })
    })
    
    return groups
  }, [scenarios])

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Settings className="h-5 w-5" />
          <span>Select Scenarios to Compare</span>
        </CardTitle>
        <CardDescription>
          Choose 2-4 scenarios for side-by-side comparison • Grouped by strategy and timeline
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {Object.entries(groupedScenarios).map(([strategy, strategyScenarios]) => (
            <div key={strategy}>
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-sm text-foreground">{strategy}</h3>
                <span className="text-xs text-muted-foreground">
                  {strategyScenarios.length} timeline{strategyScenarios.length !== 1 ? 's' : ''}
                </span>
              </div>
              
              <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
                {strategyScenarios.map((scenario) => {
                  const isSelected = selectedIds.includes(scenario.id)
                  const timelineInfo = extractTimelineInfo(scenario.name)
                  
                  return (
                    <div
                      key={scenario.id}
                      className={`border rounded-lg p-3 cursor-pointer transition-colors ${
                        isSelected 
                          ? 'border-primary bg-primary/5' 
                          : 'border-border hover:border-primary/50'
                      }`}
                      onClick={() => {
                        if (isSelected) {
                          onSelectionChange(selectedIds.filter(id => id !== scenario.id))
                        } else if (selectedIds.length < 4) {
                          onSelectionChange([...selectedIds, scenario.id])
                        }
                      }}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-start gap-2 mb-1">
                            <h4 className="font-medium text-sm">{scenario.name}</h4>
                            {timelineInfo && (
                              <Badge 
                                variant="outline" 
                                className={`text-xs ${timelineInfo.color.bg} ${timelineInfo.color.text} ${timelineInfo.color.border}`}
                              >
                                {timelineInfo.label}
                              </Badge>
                            )}
                          </div>
                          <p className="text-xs text-muted-foreground">
                            {scenario.scenario_type?.replace('_', ' ')}
                          </p>
                        </div>
                        {isSelected && (
                          <div className="h-4 w-4 rounded-full bg-primary flex items-center justify-center ml-2">
                            <div className="h-2 w-2 rounded-full bg-white" />
                          </div>
                        )}
                      </div>
                      <div className="mt-2 text-xs text-muted-foreground">
                        Age {scenario.user_profile?.current_age} • {formatCurrency(scenario.user_profile?.annual_salary || 0)}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          ))}
        </div>
        
        {selectedIds.length > 4 && (
          <p className="text-sm text-destructive mt-4">
            Maximum 4 scenarios can be compared at once
          </p>
        )}
      </CardContent>
    </Card>
  )
}

function EditableField({ 
  label, 
  value, 
  type = 'text',
  format = 'none',
  onChange,
  disabled = false
}: {
  label: string
  value: number | string
  type?: 'text' | 'number'
  format?: 'currency' | 'percentage' | 'none'
  onChange: (value: number | string) => void
  disabled?: boolean
}) {
  const [isEditing, setIsEditing] = useState(false)
  const [editValue, setEditValue] = useState(value)

  const displayValue = useMemo(() => {
    if (format === 'currency') return formatCurrency(Number(value))
    if (format === 'percentage') return formatPercentage(Number(value))
    return String(value)
  }, [value, format])

  const handleSave = () => {
    const newValue = type === 'number' ? Number(editValue) : editValue
    onChange(newValue)
    setIsEditing(false)
  }

  const handleCancel = () => {
    setEditValue(value)
    setIsEditing(false)
  }

  if (disabled) {
    return (
      <div>
        <span className="text-xs text-muted-foreground">{label}</span>
        <p className="font-medium">{displayValue}</p>
      </div>
    )
  }

  return (
    <div className="group">
      <div className="flex items-center justify-between">
        <span className="text-xs text-muted-foreground">{label}</span>
        {!isEditing && (
          <Button
            variant="ghost"
            size="sm"
            className="h-4 w-4 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
            onClick={() => setIsEditing(true)}
          >
            <Edit3 className="h-3 w-3" />
          </Button>
        )}
      </div>
      
      {isEditing ? (
        <div className="flex items-center space-x-1 mt-1">
          <Input
            type={type}
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
            className="h-7 text-sm"
            autoFocus
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleSave()
              if (e.key === 'Escape') handleCancel()
            }}
          />
          <Button
            variant="ghost"
            size="sm"
            className="h-7 w-7 p-0"
            onClick={handleSave}
          >
            <Save className="h-3 w-3 text-green-600" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="h-7 w-7 p-0"
            onClick={handleCancel}
          >
            <RotateCcw className="h-3 w-3 text-red-600" />
          </Button>
        </div>
      ) : (
        <p className="font-medium cursor-pointer hover:text-primary transition-colors" onClick={() => setIsEditing(true)}>
          {displayValue}
        </p>
      )}
    </div>
  )
}

function ScenarioComparisonCard({ 
  scenario, 
  editableData, 
  onDataChange, 
  onRemove,
  canRemove = true
}: {
  scenario: Scenario
  editableData: EditableScenarioData
  onDataChange: (data: EditableScenarioData) => void
  onRemove: () => void
  canRemove?: boolean
}) {
  const updateUserProfile = (field: string, value: number) => {
    onDataChange({
      ...editableData,
      user_profile: {
        ...editableData.user_profile,
        [field]: value
      }
    })
  }

  const updateAssumptions = (field: string, value: number) => {
    onDataChange({
      ...editableData,
      assumptions: {
        ...editableData.assumptions,
        [field]: value
      }
    })
  }

  // Extract timeline and strategy information
  const timelineInfo = extractTimelineInfo(editableData.name)
  const baseStrategy = extractBaseStrategy(editableData.name)

  return (
    <Card className="h-fit">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-start gap-2 mb-2">
              <CardTitle className="text-lg">{editableData.name}</CardTitle>
              {canRemove && (
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 w-6 p-0 ml-auto"
                  onClick={onRemove}
                >
                  <X className="h-4 w-4" />
                </Button>
              )}
            </div>
            
            <div className="flex flex-wrap gap-2">
              <Badge variant="secondary" className="capitalize">
                {scenario.scenario_type?.replace('_', ' ')}
              </Badge>
              {timelineInfo && (
                <Badge 
                  variant="outline" 
                  className={`${timelineInfo.color.bg} ${timelineInfo.color.text} ${timelineInfo.color.border} font-semibold`}
                >
                  📊 {timelineInfo.label} Projection
                </Badge>
              )}
            </div>
            
            {baseStrategy !== editableData.name && (
              <p className="text-xs text-muted-foreground mt-1">
                Strategy: {baseStrategy}
              </p>
            )}
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Basic Profile */}
        <div>
          <h4 className="font-medium text-sm mb-3 flex items-center">
            <TrendingUp className="h-4 w-4 mr-1" />
            Personal Profile
          </h4>
          <div className="grid grid-cols-2 gap-3">
            <EditableField
              label="Current Age"
              value={editableData.user_profile.current_age}
              type="number"
              onChange={(value) => updateUserProfile('current_age', Number(value))}
            />
            <EditableField
              label="Retirement Age"
              value={editableData.user_profile.retirement_age}
              type="number"
              onChange={(value) => updateUserProfile('retirement_age', Number(value))}
            />
            <EditableField
              label="Annual Salary"
              value={editableData.user_profile.annual_salary}
              type="number"
              format="currency"
              onChange={(value) => updateUserProfile('annual_salary', Number(value))}
            />
            <EditableField
              label="Life Expectancy"
              value={editableData.user_profile.life_expectancy}
              type="number"
              onChange={(value) => updateUserProfile('life_expectancy', Number(value))}
            />
          </div>
        </div>

        {/* Assumptions */}
        <div>
          <h4 className="font-medium text-sm mb-3 flex items-center">
            <Calculator className="h-4 w-4 mr-1" />
            Economic Assumptions
          </h4>
          <div className="grid grid-cols-2 gap-3">
            <EditableField
              label="Inflation Rate"
              value={editableData.assumptions.inflation_rate}
              type="number"
              format="percentage"
              onChange={(value) => updateAssumptions('inflation_rate', Number(value))}
            />
            <EditableField
              label="Investment Return"
              value={editableData.assumptions.investment_return}
              type="number"
              format="percentage"
              onChange={(value) => updateAssumptions('investment_return', Number(value))}
            />
            <EditableField
              label="Salary Growth"
              value={editableData.assumptions.salary_growth_rate}
              type="number"
              format="percentage"
              onChange={(value) => updateAssumptions('salary_growth_rate', Number(value))}
            />
            <EditableField
              label="Tax Rate"
              value={editableData.assumptions.tax_rate}
              type="number"
              format="percentage"
              onChange={(value) => updateAssumptions('tax_rate', Number(value))}
            />
          </div>
        </div>

        {/* Timeline-Specific Metrics */}
        <div>
          <h4 className="font-medium text-sm mb-3 flex items-center">
            <BarChart3 className="h-4 w-4 mr-1" />
            {timelineInfo ? `${timelineInfo.years}-Year Projection Metrics` : 'Summary Metrics'}
          </h4>
          <div className="grid grid-cols-2 gap-3">
            {timelineInfo && (
              <div className="col-span-2">
                <div className={`p-3 rounded-lg ${timelineInfo.color.bg} border ${timelineInfo.color.border}`}>
                  <div className="flex items-center justify-between">
                    <span className={`text-sm font-medium ${timelineInfo.color.text}`}>
                      Projection Timeline
                    </span>
                    <span className={`text-lg font-bold ${timelineInfo.color.text}`}>
                      {timelineInfo.years} Years
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    Analysis from age {editableData.user_profile.current_age} to {editableData.user_profile.current_age + timelineInfo.years}
                  </p>
                </div>
              </div>
            )}
            
            <div>
              <span className="text-xs text-muted-foreground">Total Assets</span>
              <p className="font-medium">
                {formatCurrency(editableData.assets.reduce((sum, asset) => sum + asset.current_value, 0))}
              </p>
            </div>
            <div>
              <span className="text-xs text-muted-foreground">Annual Expenses</span>
              <p className="font-medium">
                {formatCurrency(editableData.expenses.reduce((sum, expense) => sum + expense.annual_amount, 0))}
              </p>
            </div>
            
            {timelineInfo && (
              <>
                <div>
                  <span className="text-xs text-muted-foreground">Projection End Age</span>
                  <p className="font-medium">
                    {editableData.user_profile.current_age + timelineInfo.years} years old
                  </p>
                </div>
                <div>
                  <span className="text-xs text-muted-foreground">Analysis Period</span>
                  <p className="font-medium">
                    {timelineInfo.years === 2 ? 'Short-term' : 
                     timelineInfo.years === 4 ? 'Medium-term' :
                     timelineInfo.years === 6 ? 'Long-term' : 
                     timelineInfo.years === 8 ? 'Extended' : 'Custom'}
                  </p>
                </div>
              </>
            )}
            
            {!timelineInfo && (
              <>
                <div>
                  <span className="text-xs text-muted-foreground">Years to Retirement</span>
                  <p className="font-medium">
                    {editableData.user_profile.retirement_age - editableData.user_profile.current_age} years
                  </p>
                </div>
                <div>
                  <span className="text-xs text-muted-foreground">Working Years Left</span>
                  <p className="font-medium">
                    {Math.max(0, editableData.user_profile.retirement_age - editableData.user_profile.current_age)} years
                  </p>
                </div>
              </>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export function ScenarioComparison() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { scenarios, isLoading } = useScenarios()
  const { compareScenarios, isComparingScenarios, comparisonResult } = useProjections()
  const { toast } = useToast()

  // Get initial scenario IDs from URL params
  const initialScenarioIds = useMemo(() => {
    const ids = searchParams.get('scenarios')?.split(',') || []
    return ids.filter(id => id.length > 0)
  }, [searchParams])

  const [selectedScenarioIds, setSelectedScenarioIds] = useState<string[]>(initialScenarioIds)
  const [editableScenarios, setEditableScenarios] = useState<Record<string, EditableScenarioData>>({})

  // Initialize editable scenarios when scenarios are loaded
  useEffect(() => {
    if (scenarios.length > 0 && selectedScenarioIds.length > 0) {
      const newEditableScenarios: Record<string, EditableScenarioData> = {}
      
      selectedScenarioIds.forEach(id => {
        const scenario = scenarios.find(s => s.id === id)
        if (scenario) {
          // Parse user data
          let userData = {}
          try {
            userData = JSON.parse(scenario.user_data || '{}')
          } catch (error) {
            console.error('Error parsing user_data:', error)
          }

          // Parse projection data for assumptions
          let projectionData = {}
          try {
            projectionData = JSON.parse(scenario.projection_data || '{}')
          } catch (error) {
            console.error('Error parsing projection_data:', error)
          }

          newEditableScenarios[id] = {
            id: scenario.id,
            name: scenario.name,
            user_profile: {
              current_age: scenario.user_profile?.current_age || userData.current_age || 30,
              retirement_age: scenario.user_profile?.retirement_age || userData.retirement_age || 65,
              annual_salary: scenario.user_profile?.annual_salary || userData.annual_salary || 75000,
              life_expectancy: scenario.user_profile?.life_expectancy || userData.life_expectancy || 85
            },
            assets: userData.assets || [],
            expenses: userData.expenses || [],
            assumptions: {
              inflation_rate: projectionData.assumptions?.inflation_rate || 0.03,
              investment_return: projectionData.assumptions?.investment_return || 0.07,
              salary_growth_rate: projectionData.assumptions?.salary_growth_rate || 0.03,
              tax_rate: projectionData.assumptions?.tax_rate || 0.25
            }
          }
        }
      })
      
      setEditableScenarios(newEditableScenarios)
    }
  }, [scenarios, selectedScenarioIds])

  const selectedScenarios = useMemo(() => {
    return scenarios.filter(s => selectedScenarioIds.includes(s.id))
  }, [scenarios, selectedScenarioIds])

  const handleScenarioSelectionChange = (ids: string[]) => {
    setSelectedScenarioIds(ids)
    
    // Update URL params
    const params = new URLSearchParams(searchParams)
    if (ids.length > 0) {
      params.set('scenarios', ids.join(','))
    } else {
      params.delete('scenarios')
    }
    router.replace(`/scenarios/compare?${params.toString()}`)
  }

  const handleDataChange = (scenarioId: string, data: EditableScenarioData) => {
    setEditableScenarios(prev => ({
      ...prev,
      [scenarioId]: data
    }))
  }

  const handleRemoveScenario = (scenarioId: string) => {
    const newIds = selectedScenarioIds.filter(id => id !== scenarioId)
    handleScenarioSelectionChange(newIds)
  }

  const handleRunComparison = () => {
    if (selectedScenarioIds.length < 2) {
      toast({
        title: "Error",
        description: "Please select at least 2 scenarios to compare.",
        variant: "destructive"
      })
      return
    }

    compareScenarios(selectedScenarioIds)
  }

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
                  Scenario Comparison
                </h1>
                <p className="text-sm text-muted-foreground mt-1">
                  Compare projection timelines and modify scenarios side-by-side
                </p>
              </div>
            </div>
            <div className="flex space-x-2">
              <Button
                onClick={handleRunComparison}
                disabled={selectedScenarioIds.length < 2 || isComparingScenarios}
                className="flex items-center space-x-2"
                title={selectedScenarioIds.length < 2 ? 'Select at least 2 scenarios to compare projection timelines' : 'Run projection timeline analysis'}
              >
                <Calculator className="h-4 w-4" />
                <span>
                  {isComparingScenarios ? 'Analyzing...' : 'Analyze Projections'}
                </span>
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="space-y-8"
        >
          {/* Scenario Selector */}
          <ScenarioSelector
            scenarios={scenarios}
            selectedIds={selectedScenarioIds}
            onSelectionChange={handleScenarioSelectionChange}
          />

          {/* Scenario Comparison Grid */}
          {selectedScenarios.length > 0 && (
            <div className={`grid gap-6 ${
              selectedScenarios.length === 1 ? 'grid-cols-1 max-w-md mx-auto' :
              selectedScenarios.length === 2 ? 'grid-cols-1 lg:grid-cols-2' :
              selectedScenarios.length === 3 ? 'grid-cols-1 lg:grid-cols-3' :
              'grid-cols-1 md:grid-cols-2 lg:grid-cols-4'
            }`}>
              {selectedScenarios.map((scenario) => (
                <ScenarioComparisonCard
                  key={scenario.id}
                  scenario={scenario}
                  editableData={editableScenarios[scenario.id]}
                  onDataChange={(data) => handleDataChange(scenario.id, data)}
                  onRemove={() => handleRemoveScenario(scenario.id)}
                  canRemove={selectedScenarios.length > 1}
                />
              ))}
            </div>
          )}

          {/* Comparison Results */}
          {comparisonResult && (
            <Card>
              <CardHeader>
                <CardTitle>Projection Timeline Analysis</CardTitle>
                <CardDescription>
                  Cross-timeline comparison showing how different projection periods impact the same strategy
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {/* Timeline Summary */}
                  {selectedScenarios.length > 0 && (
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                      {selectedScenarios.map((scenario) => {
                        const timelineInfo = extractTimelineInfo(scenario.name)
                        const baseStrategy = extractBaseStrategy(scenario.name)
                        
                        return (
                          <div key={scenario.id} className="text-center p-4 border rounded-lg">
                            <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium mb-2 ${
                              timelineInfo ? `${timelineInfo.color.bg} ${timelineInfo.color.text}` : 'bg-gray-100 text-gray-700'
                            }`}>
                              {timelineInfo ? `${timelineInfo.years} Years` : 'Custom'}
                            </div>
                            <p className="text-xs text-muted-foreground">{baseStrategy}</p>
                          </div>
                        )
                      })}
                    </div>
                  )}
                  
                  <div className="text-center py-8">
                    <BarChart3 className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                    <p className="text-muted-foreground mb-2">
                      Detailed projection timeline comparison will be displayed here
                    </p>
                    <p className="text-xs text-muted-foreground">
                      This will show how the same financial strategy performs across different time horizons
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Empty State */}
          {selectedScenarios.length === 0 && (
            <Card>
              <CardContent className="py-12 text-center">
                <BarChart3 className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium text-foreground mb-2">
                  Select scenarios to compare
                </h3>
                <p className="text-muted-foreground mb-4">
                  Choose 2-4 scenarios from above to start your projection timeline analysis.
                </p>
                <div className="flex justify-center gap-2 text-xs text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <div className="w-3 h-3 bg-green-100 border border-green-200 rounded"></div>
                    <span>2-Year</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="w-3 h-3 bg-blue-100 border border-blue-200 rounded"></div>
                    <span>4-Year</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="w-3 h-3 bg-yellow-100 border border-yellow-200 rounded"></div>
                    <span>6-Year</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="w-3 h-3 bg-red-100 border border-red-200 rounded"></div>
                    <span>8-Year</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </motion.div>
      </main>
    </div>
  )
}

export default ScenarioComparison