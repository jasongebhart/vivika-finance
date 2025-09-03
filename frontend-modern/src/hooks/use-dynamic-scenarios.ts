import { useState, useEffect } from 'react'
import { getAPIUrl } from '@/lib/config'

export interface DynamicScenario {
  id: string
  name: string
  location: string
  spouse1_status: string
  spouse2_status: string
  housing: string
  school_type: string
  projection_years: number
  status: string
  created_at: string
  updated_at: string
  user_data?: string // JSON string containing detailed financial data
  projection_data?: string // JSON string containing projection settings
  projection_results?: {
    final_net_worth: number
    annual_growth_rate: number
    total_expenses: number
    retirement_readiness: boolean
    calculated_at: string
    yearly_projections?: Array<{
      year: number
      age: number
      net_worth: number
      income: number
      expenses: number
      net_cash_flow: number
    }>
    detailed_expenses?: Array<{
      name: string
      annual_amount: number
      start_age: number
      end_age?: number
      inflation_adjusted: boolean
      line_items?: Record<string, number>
    }>
    assets_detail?: Array<{
      name: string
      asset_type?: string
      current_value: number
      expected_return?: number
      allocation_percentage?: number
    }>
    income_sources?: Array<{
      name: string
      annual_amount: number
      start_age: number
      end_age?: number
      growth_rate?: number
    }>
    financial_profile?: {
      current_age: number
      retirement_age: number
      annual_salary: number
      current_city: string
      life_expectancy: number
    }
  }
}

export function useDynamicScenarios() {
  const [scenarios, setScenarios] = useState<DynamicScenario[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadScenarios = async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      const response = await fetch(getAPIUrl('/api/dynamic-scenarios?limit=100'))
      if (!response.ok) {
        throw new Error(`Failed to load scenarios: ${response.status} ${response.statusText}`)
      }
      
      const data = await response.json()
      
      // Load full details for scenarios with results
      const scenariosWithDetails = await Promise.all(
        data.map(async (scenario: any) => {
          try {
            if (scenario.status === 'completed') {
              const detailResponse = await fetch(getAPIUrl(`/api/dynamic-scenarios/${scenario.id}`))
              if (detailResponse.ok) {
                return await detailResponse.json()
              }
            }
            return scenario
          } catch (error) {
            console.error(`Failed to load details for scenario ${scenario.id}:`, error)
            return scenario
          }
        })
      )
      
      // Remove duplicates and sort by completion status and creation date
      const uniqueScenarios = scenariosWithDetails
        .filter((scenario, index, self) => 
          index === self.findIndex(s => s.id === scenario.id)
        )
        .sort((a, b) => {
          // Completed scenarios first
          if (a.status === 'completed' && b.status !== 'completed') return -1
          if (b.status === 'completed' && a.status !== 'completed') return 1
          // Then by creation date (newest first)
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        })
      
      setScenarios(uniqueScenarios)
    } catch (error) {
      console.error('Failed to load dynamic scenarios:', error)
      setError(error instanceof Error ? error.message : 'Failed to load scenarios')
    } finally {
      setIsLoading(false)
    }
  }

  const getScenarioById = async (id: string): Promise<DynamicScenario | null> => {
    try {
      const response = await fetch(getAPIUrl(`/api/dynamic-scenarios/${id}`))
      if (!response.ok) {
        throw new Error(`Failed to load scenario: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Failed to load scenario:', error)
      return null
    }
  }

  const runScenario = async (scenarioId: string) => {
    try {
      const response = await fetch(getAPIUrl('/api/scenarios/run'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id: scenarioId }),
      })

      if (!response.ok) {
        throw new Error(`Failed to run scenario: ${response.status}`)
      }

      const result = await response.json()
      
      // Reload scenarios to get updated status
      setTimeout(() => {
        loadScenarios()
      }, 2000)
      
      return result
    } catch (error) {
      console.error('Failed to run scenario:', error)
      throw error
    }
  }

  const deleteScenario = async (scenarioId: string) => {
    try {
      const response = await fetch(getAPIUrl(`/api/dynamic-scenarios/${scenarioId}`), {
        method: 'DELETE'
      })

      if (!response.ok) {
        throw new Error('Failed to delete scenario')
      }

      // Remove from local state
      setScenarios(prev => prev.filter(s => s.id !== scenarioId))
    } catch (error) {
      console.error('Failed to delete scenario:', error)
      throw error
    }
  }

  const generateScenario = async (params: {
    location: string
    spouse1Status: string
    spouse2Status: string
    housing: string
    schoolType: string
    projectionYears: number
  }) => {
    try {
      const response = await fetch(getAPIUrl('/api/scenarios/generate'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(params),
      })

      if (!response.ok) {
        throw new Error(`Failed to generate scenario: ${response.status}`)
      }

      const result = await response.json()
      
      // Reload scenarios to include the new one
      loadScenarios()
      
      return result
    } catch (error) {
      console.error('Failed to generate scenario:', error)
      throw error
    }
  }

  const compareScenarios = async (scenarioIds: string[]) => {
    try {
      const response = await fetch(getAPIUrl('/api/scenarios/compare'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ scenario_ids: scenarioIds }),
      })

      if (!response.ok) {
        throw new Error(`Failed to compare scenarios: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to compare scenarios:', error)
      throw error
    }
  }

  // Get scenarios by filter criteria
  const getScenariosByLocation = (location: string) => {
    return scenarios.filter(s => s.location === location)
  }

  const getCompletedScenarios = () => {
    return scenarios.filter(s => s.status === 'completed' && s.projection_results)
  }

  const getBestScenario = () => {
    const completed = getCompletedScenarios()
    if (completed.length === 0) return null
    
    return completed.reduce((best, current) => {
      const bestNetWorth = best.projection_results?.final_net_worth || 0
      const currentNetWorth = current.projection_results?.final_net_worth || 0
      return currentNetWorth > bestNetWorth ? current : best
    })
  }

  const getDefaultScenario = () => {
    // Find the best 8-year working scenario
    const workingScenarios = scenarios.filter(s => 
      s.spouse1_status === 'Work' && 
      s.spouse2_status === 'Work' && 
      s.projection_years === 8 &&
      s.status === 'completed'
    )
    
    if (workingScenarios.length > 0) {
      return workingScenarios[0]
    }
    
    // Fallback to any completed scenario
    const completed = getCompletedScenarios()
    return completed.length > 0 ? completed[0] : null
  }

  useEffect(() => {
    loadScenarios()
  }, [])

  return {
    // Data
    scenarios,
    isLoading,
    error,
    
    // Actions
    loadScenarios,
    getScenarioById,
    runScenario,
    deleteScenario,
    generateScenario,
    compareScenarios,
    
    // Filters
    getScenariosByLocation,
    getCompletedScenarios,
    getBestScenario,
    getDefaultScenario
  }
}