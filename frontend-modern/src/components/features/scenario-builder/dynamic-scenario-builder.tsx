'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  MapPin, 
  Users, 
  Home, 
  GraduationCap, 
  Calendar,
  Play,
  BarChart3,
  Save,
  Trash2
} from 'lucide-react'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'
import { YearRangeControl } from '@/components/ui/year-range-control'
import { ScenarioComparison } from '@/components/features/scenario-comparison/scenario-comparison'
import { ScenarioChart } from '@/components/features/scenario-visualization/scenario-chart'
import { formatCurrency } from '@/lib/utils'
import { getAPIUrl } from '@/lib/config'

interface ScenarioConfiguration {
  id: string
  name: string
  location: string
  spouse1Status: string
  spouse2Status: string
  housing: string
  schoolType: string
  projectionYears: number
  projectedNetWorth?: number
  isRunning?: boolean
  status?: string
  createdAt?: string
  projectionResults?: {
    final_net_worth: number
    annual_growth_rate: number
    total_expenses: number
    retirement_readiness: boolean
    calculated_at: string
  }
}

interface DynamicScenarioBuilderProps {
  onScenarioCreate?: (scenario: ScenarioConfiguration) => void
  onScenarioRun?: (scenario: ScenarioConfiguration) => void
  onCompareScenarios?: (scenarios: ScenarioConfiguration[]) => void
  className?: string
}

// Configuration options based on your existing data
const SCENARIO_OPTIONS = {
  locations: [
    { value: 'Mn', label: 'Minnesota', description: 'Lower cost of living' },
    { value: 'Sd', label: 'San Diego', description: 'Moderate cost, great weather' },
    { value: 'Sf', label: 'San Francisco', description: 'High cost, tech hub' }
  ],
  spouseStatuses: [
    { value: 'Work', label: 'Working', description: 'Active employment' },
    { value: 'Retired', label: 'Retired', description: 'No active income' }
  ],
  housingTypes: [
    { value: 'Own', label: 'Own Home', description: 'Property ownership' },
    { value: 'Rent', label: 'Rent', description: 'Rental property' }
  ],
  schoolTypes: [
    { value: 'Public', label: 'Public School', description: 'Public education' },
    { value: 'Private', label: 'Private School', description: 'Private education' },
    { value: 'Pripub', label: 'Mixed', description: 'Public + Private mix' }
  ]
}

export function DynamicScenarioBuilder({ 
  onScenarioCreate, 
  onScenarioRun,
  onCompareScenarios,
  className = '' 
}: DynamicScenarioBuilderProps) {
  const [currentScenario, setCurrentScenario] = useState<ScenarioConfiguration>({
    id: '',
    name: '',
    location: 'Sf',
    spouse1Status: 'Work',
    spouse2Status: 'Work', 
    housing: 'Own',
    schoolType: 'Private',
    projectionYears: 8
  })

  const [savedScenarios, setSavedScenarios] = useState<ScenarioConfiguration[]>([])
  const [selectedForComparison, setSelectedForComparison] = useState<string[]>([])
  const [showComparison, setShowComparison] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [runningProgress, setRunningProgress] = useState<{[key: string]: number}>({})
  const [selectedScenarioForChart, setSelectedScenarioForChart] = useState<ScenarioConfiguration | null>(null)

  // Generate scenario name automatically
  useEffect(() => {
    const name = `${currentScenario.location} Hav Jason ${currentScenario.spouse1Status} ${currentScenario.spouse2Status} ${currentScenario.housing} ${currentScenario.schoolType} ${currentScenario.projectionYears}yrs`
    setCurrentScenario(prev => ({ ...prev, name }))
  }, [
    currentScenario.location,
    currentScenario.spouse1Status,
    currentScenario.spouse2Status,
    currentScenario.housing,
    currentScenario.schoolType,
    currentScenario.projectionYears
  ])

  // Load saved scenarios from database
  useEffect(() => {
    const loadSavedScenarios = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const response = await fetch(getAPIUrl('/api/dynamic-scenarios'))
        
        if (!response.ok) {
          throw new Error(`Failed to load scenarios: ${response.status} ${response.statusText}`)
        }
        
        const scenarios = await response.json()
        const convertedScenarios = scenarios.map((s: any) => ({
          id: s.id,
          name: s.name,
          location: s.location,
          spouse1Status: s.spouse1_status,
          spouse2Status: s.spouse2_status,
          housing: s.housing,
          schoolType: s.school_type,
          projectionYears: s.projection_years,
          status: s.status,
          createdAt: s.created_at
        }))
        
        // Remove duplicates based on ID
        const uniqueScenarios = convertedScenarios.filter((scenario, index, self) => 
          index === self.findIndex(s => s.id === scenario.id)
        )
        
        setSavedScenarios(uniqueScenarios)
        setSuccessMessage(`Loaded ${uniqueScenarios.length} scenarios successfully`)
        setTimeout(() => setSuccessMessage(null), 3000)
      } catch (error) {
        console.error('Failed to load saved scenarios:', error)
        setError(error instanceof Error ? error.message : 'Failed to load scenarios')
      } finally {
        setIsLoading(false)
      }
    }

    loadSavedScenarios()
  }, [])

  const handleSaveScenario = async () => {
    try {
      setIsGenerating(true)
      setError(null)
      
      // Generate scenario via API
      const response = await fetch(getAPIUrl('/api/scenarios/generate'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          location: currentScenario.location,
          spouse1Status: currentScenario.spouse1Status,
          spouse2Status: currentScenario.spouse2Status,
          housing: currentScenario.housing,
          schoolType: currentScenario.schoolType,
          projectionYears: currentScenario.projectionYears
        }),
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`Failed to generate scenario: ${response.status} - ${errorText}`)
      }

      const result = await response.json()
      const newScenario: ScenarioConfiguration = {
        id: result.scenario.id,
        name: result.scenario.name,
        location: result.scenario.location,
        spouse1Status: result.scenario.spouse1Status,
        spouse2Status: result.scenario.spouse2Status,
        housing: result.scenario.housing,
        schoolType: result.scenario.schoolType,
        projectionYears: result.scenario.projectionYears,
        status: result.scenario.status,
        createdAt: result.scenario.created_at
      }

      setSavedScenarios(prev => {
        // Check if scenario already exists to prevent duplicates
        const existingIndex = prev.findIndex(s => s.id === newScenario.id)
        if (existingIndex >= 0) {
          // Update existing scenario
          const updated = [...prev]
          updated[existingIndex] = newScenario
          return updated
        } else {
          // Add new scenario
          return [newScenario, ...prev]
        }
      })
      setSuccessMessage('Scenario saved successfully!')
      setTimeout(() => setSuccessMessage(null), 3000)
      onScenarioCreate?.(newScenario)
    } catch (error) {
      console.error('Failed to generate scenario:', error)
      setError(error instanceof Error ? error.message : 'Failed to generate scenario')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleRunScenario = async (scenario: ScenarioConfiguration) => {
    try {
      // Validate scenario data
      if (!scenario.id) {
        throw new Error('Scenario ID is missing')
      }

      setError(null)
      console.log('Running scenario:', scenario.id, scenario.name)

      // Mark as running and start progress tracking
      setSavedScenarios(prev => 
        prev.map(s => s.id === scenario.id ? { ...s, isRunning: true } : s)
      )
      setRunningProgress(prev => ({ ...prev, [scenario.id]: 0 }))

      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setRunningProgress(prev => {
          const currentProgress = prev[scenario.id] || 0
          if (currentProgress < 90) {
            return { ...prev, [scenario.id]: currentProgress + 10 }
          }
          return prev
        })
      }, 300)

      // Call API to run scenario
      const response = await fetch(getAPIUrl('/api/scenarios/run'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id: scenario.id, name: scenario.name }),
      })

      console.log('Run scenario response status:', response.status)

      if (!response.ok) {
        const errorText = await response.text()
        console.error('Run scenario error response:', errorText)
        throw new Error(`Failed to run scenario: ${response.status} - ${errorText}`)
      }

      const result = await response.json()
      console.log('Scenario running:', result)
      
      // Complete progress
      clearInterval(progressInterval)
      setRunningProgress(prev => ({ ...prev, [scenario.id]: 100 }))
      
      onScenarioRun?.(scenario)
      setSuccessMessage(`Scenario "${scenario.name}" started successfully!`)
      setTimeout(() => setSuccessMessage(null), 3000)

      // Update scenario with running status after a delay to show completed
      setTimeout(() => {
        setSavedScenarios(prev => {
          const updated = prev.map(s => 
            s.id === scenario.id ? { ...s, isRunning: false, status: 'completed' } : s
          )
          // Remove duplicates if any exist
          return updated.filter((scenario, index, self) => 
            index === self.findIndex(s => s.id === scenario.id)
          )
        })
        setRunningProgress(prev => {
          const { [scenario.id]: _, ...rest } = prev
          return rest
        })
      }, 3000)

    } catch (error) {
      console.error('Failed to run scenario:', error)
      setError(error instanceof Error ? error.message : 'Failed to run scenario')
      
      // Remove running status and progress on error
      setSavedScenarios(prev => 
        prev.map(s => s.id === scenario.id ? { ...s, isRunning: false } : s)
      )
      setRunningProgress(prev => {
        const { [scenario.id]: _, ...rest } = prev
        return rest
      })
    }
  }

  const handleDeleteScenario = async (scenarioId: string) => {
    try {
      const response = await fetch(getAPIUrl(`/api/dynamic-scenarios/${scenarioId}`), {
        method: 'DELETE'
      })

      if (!response.ok) {
        throw new Error('Failed to delete scenario')
      }

      setSavedScenarios(prev => prev.filter(s => s.id !== scenarioId))
      setSelectedForComparison(prev => prev.filter(id => id !== scenarioId))
    } catch (error) {
      console.error('Failed to delete scenario:', error)
    }
  }

  const handleComparisonToggle = (scenarioId: string) => {
    setSelectedForComparison(prev => {
      if (prev.includes(scenarioId)) {
        return prev.filter(id => id !== scenarioId)
      } else if (prev.length < 4) { // Limit to 4 comparisons
        return [...prev, scenarioId]
      }
      return prev
    })
  }

  const handleCompare = () => {
    const scenariosToCompare = savedScenarios.filter(s => selectedForComparison.includes(s.id))
    setShowComparison(true)
    onCompareScenarios?.(scenariosToCompare)
  }

  const handleViewResults = async (scenario: ScenarioConfiguration) => {
    try {
      const response = await fetch(getAPIUrl(`/api/dynamic-scenarios/${scenario.id}`))
      if (!response.ok) {
        throw new Error('Failed to fetch scenario results')
      }
      const fullScenario = await response.json()
      setSelectedScenarioForChart({
        ...scenario,
        projectionResults: fullScenario.projection_results
      })
    } catch (error) {
      console.error('Failed to load scenario results:', error)
      setError('Failed to load scenario results')
    }
  }

  if (showComparison) {
    const scenariosToCompare = savedScenarios.filter(s => selectedForComparison.includes(s.id))
    return (
      <ScenarioComparison
        scenarios={scenariosToCompare}
        onBack={() => setShowComparison(false)}
        className={className}
      />
    )
  }

  if (selectedScenarioForChart && selectedScenarioForChart.projectionResults) {
    return (
      <div className={`space-y-6 ${className}`}>
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">Scenario Analysis</h2>
          <Button 
            variant="outline" 
            onClick={() => setSelectedScenarioForChart(null)}
          >
            ← Back to Scenarios
          </Button>
        </div>
        <ScenarioChart
          scenarioName={selectedScenarioForChart.name}
          results={selectedScenarioForChart.projectionResults}
          location={selectedScenarioForChart.location}
          parameters={{
            housing: selectedScenarioForChart.housing,
            schoolType: selectedScenarioForChart.schoolType,
            spouse1Status: selectedScenarioForChart.spouse1Status,
            spouse2Status: selectedScenarioForChart.spouse2Status
          }}
        />
      </div>
    )
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Error and Success Messages */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      {successMessage && (
        <Alert>
          <AlertDescription className="text-green-600">{successMessage}</AlertDescription>
        </Alert>
      )}
      
      {/* Scenario Builder */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Users className="h-5 w-5 mr-2" />
            Dynamic Scenario Builder
          </CardTitle>
          <CardDescription>
            Configure your financial scenario parameters and generate projections
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Location Selection */}
          <div>
            <div className="flex items-center mb-3">
              <MapPin className="h-4 w-4 mr-2" />
              <span className="font-medium">Location</span>
            </div>
            <div className="grid grid-cols-3 gap-3">
              {SCENARIO_OPTIONS.locations.map((location) => (
                <Button
                  key={location.value}
                  variant={currentScenario.location === location.value ? "default" : "outline"}
                  onClick={() => setCurrentScenario(prev => ({ ...prev, location: location.value }))}
                  className="h-auto p-3 text-left"
                >
                  <div>
                    <div className="font-medium">{location.label}</div>
                    <div className="text-xs text-muted-foreground">{location.description}</div>
                  </div>
                </Button>
              ))}
            </div>
          </div>

          {/* Spouse Status Selection */}
          <div className="grid grid-cols-2 gap-6">
            <div>
              <div className="flex items-center mb-3">
                <Users className="h-4 w-4 mr-2" />
                <span className="font-medium">Havilah Status</span>
              </div>
              <div className="space-y-2">
                {SCENARIO_OPTIONS.spouseStatuses.map((status) => (
                  <Button
                    key={status.value}
                    variant={currentScenario.spouse1Status === status.value ? "default" : "outline"}
                    onClick={() => setCurrentScenario(prev => ({ ...prev, spouse1Status: status.value }))}
                    className="w-full justify-start"
                  >
                    {status.label}
                  </Button>
                ))}
              </div>
            </div>

            <div>
              <div className="flex items-center mb-3">
                <Users className="h-4 w-4 mr-2" />
                <span className="font-medium">Jason Status</span>
              </div>
              <div className="space-y-2">
                {SCENARIO_OPTIONS.spouseStatuses.map((status) => (
                  <Button
                    key={status.value}
                    variant={currentScenario.spouse2Status === status.value ? "default" : "outline"}
                    onClick={() => setCurrentScenario(prev => ({ ...prev, spouse2Status: status.value }))}
                    className="w-full justify-start"
                  >
                    {status.label}
                  </Button>
                ))}
              </div>
            </div>
          </div>

          {/* Housing and School Selection */}
          <div className="grid grid-cols-2 gap-6">
            <div>
              <div className="flex items-center mb-3">
                <Home className="h-4 w-4 mr-2" />
                <span className="font-medium">Housing</span>
              </div>
              <div className="space-y-2">
                {SCENARIO_OPTIONS.housingTypes.map((housing) => (
                  <Button
                    key={housing.value}
                    variant={currentScenario.housing === housing.value ? "default" : "outline"}
                    onClick={() => setCurrentScenario(prev => ({ ...prev, housing: housing.value }))}
                    className="w-full justify-start"
                  >
                    {housing.label}
                  </Button>
                ))}
              </div>
            </div>

            <div>
              <div className="flex items-center mb-3">
                <GraduationCap className="h-4 w-4 mr-2" />
                <span className="font-medium">Education</span>
              </div>
              <div className="space-y-2">
                {SCENARIO_OPTIONS.schoolTypes.map((school) => (
                  <Button
                    key={school.value}
                    variant={currentScenario.schoolType === school.value ? "default" : "outline"}
                    onClick={() => setCurrentScenario(prev => ({ ...prev, schoolType: school.value }))}
                    className="w-full justify-start text-xs"
                  >
                    {school.label}
                  </Button>
                ))}
              </div>
            </div>
          </div>

          {/* Year Range Selection */}
          <div>
            <div className="flex items-center mb-3">
              <Calendar className="h-4 w-4 mr-2" />
              <span className="font-medium">Projection Timeline</span>
            </div>
            <YearRangeControl
              value={currentScenario.projectionYears}
              onChange={(years) => setCurrentScenario(prev => ({ ...prev, projectionYears: years }))}
              compact={true}
              min={2}
              max={10}
            />
          </div>

          {/* Current Configuration Preview */}
          <div className="p-4 bg-muted rounded-lg">
            <h3 className="font-medium mb-2">Current Configuration:</h3>
            <p className="text-sm font-mono">{currentScenario.name}</p>
            <div className="flex items-center justify-between mt-3">
              <div className="flex space-x-2">
                <Badge variant="secondary">{currentScenario.location}</Badge>
                <Badge variant="secondary">{currentScenario.spouse1Status}/{currentScenario.spouse2Status}</Badge>
                <Badge variant="secondary">{currentScenario.housing}</Badge>
                <Badge variant="secondary">{currentScenario.schoolType}</Badge>
                <Badge variant="secondary">{currentScenario.projectionYears} years</Badge>
              </div>
              <div className="space-x-2">
                <Button onClick={handleSaveScenario} size="sm" disabled={isGenerating}>
                  <Save className="h-4 w-4 mr-1" />
                  {isGenerating ? 'Generating...' : 'Save'}
                </Button>
                <Button onClick={() => handleRunScenario(currentScenario)} size="sm" variant="default">
                  <Play className="h-4 w-4 mr-1" />
                  Run
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Saved Scenarios */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Saved Scenarios</CardTitle>
              <CardDescription>
                {isLoading ? 'Loading scenarios...' : 'Select scenarios to compare (up to 4)'}
              </CardDescription>
            </div>
            {selectedForComparison.length > 1 && (
              <Button onClick={handleCompare} variant="default">
                <BarChart3 className="h-4 w-4 mr-1" />
                Compare ({selectedForComparison.length})
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
              <p className="text-muted-foreground">Loading saved scenarios...</p>
            </div>
          ) : savedScenarios.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground">No saved scenarios yet. Create your first scenario above!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {savedScenarios.map((scenario, index) => (
                <motion.div
                  key={`scenario-${scenario.id}-${index}`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`p-4 border rounded-lg ${
                    selectedForComparison.includes(scenario.id) 
                      ? 'border-primary bg-primary/5' 
                      : 'border-border'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="font-medium text-sm">{scenario.name}</span>
                        {scenario.isRunning && (
                          <div className="flex items-center space-x-2">
                            <Badge variant="secondary" className="animate-pulse">Running</Badge>
                            {runningProgress[scenario.id] !== undefined && (
                              <div className="flex items-center space-x-1">
                                <Progress value={runningProgress[scenario.id]} className="w-16 h-2" />
                                <span className="text-xs text-muted-foreground">
                                  {runningProgress[scenario.id]}%
                                </span>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                      <div className="flex space-x-2">
                        <Badge variant="outline" className="text-xs">{scenario.location}</Badge>
                        <Badge variant="outline" className="text-xs">{scenario.spouse1Status}/{scenario.spouse2Status}</Badge>
                        <Badge variant="outline" className="text-xs">{scenario.housing}</Badge>
                        <Badge variant="outline" className="text-xs">{scenario.schoolType}</Badge>
                        <Badge variant="outline" className="text-xs">{scenario.projectionYears}y</Badge>
                      </div>
                      {scenario.projectedNetWorth && (
                        <div className="mt-2 text-sm text-muted-foreground">
                          Projected Net Worth: <span className="font-medium text-foreground">
                            {formatCurrency(scenario.projectedNetWorth)}
                          </span>
                        </div>
                      )}
                      {scenario.status === 'completed' && (
                        <div className="mt-2">
                          <Button
                            size="sm"
                            variant="ghost"
                            className="text-xs"
                            onClick={() => handleViewResults(scenario)}
                          >
                            <BarChart3 className="h-3 w-3 mr-1" />
                            View Results
                          </Button>
                        </div>
                      )}
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button
                        variant={selectedForComparison.includes(scenario.id) ? "default" : "outline"}
                        size="sm"
                        onClick={() => handleComparisonToggle(scenario.id)}
                        disabled={!selectedForComparison.includes(scenario.id) && selectedForComparison.length >= 4}
                      >
                        {selectedForComparison.includes(scenario.id) ? 'Selected' : 'Compare'}
                      </Button>
                      <Button
                        onClick={() => handleRunScenario(scenario)}
                        size="sm"
                        variant="secondary"
                        disabled={scenario.isRunning}
                      >
                        <Play className="h-4 w-4" />
                      </Button>
                      <Button
                        onClick={() => handleDeleteScenario(scenario.id)}
                        size="sm"
                        variant="ghost"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}