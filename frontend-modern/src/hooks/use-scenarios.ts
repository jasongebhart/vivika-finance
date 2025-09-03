import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '@/lib/api'
import { simpleApi } from '@/lib/simple-api'
import { useAppStore } from '@/stores/app-store'
import { useToast } from '@/hooks/use-toast'
import type { Scenario, ScenarioFormData, ScenarioProjection } from '@/types'

export function useScenarios() {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const setScenarios = useAppStore((state) => state.setScenarios)
  const addScenario = useAppStore((state) => state.addScenario)
  const removeScenarioFromStore = useAppStore((state) => state.removeScenario)

  // Query to fetch all scenarios
  console.log('useScenarios: Hook called, setting up query...')
  
  const scenariosQuery = useQuery({
    queryKey: ['scenarios'],
    queryFn: async (): Promise<Scenario[]> => {
      console.log('useScenarios: QueryFn called - query is actually running!')
      try {
        console.log('Fetching scenarios from API...')
        console.log('API URL:', process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api')
        
        // Try simple API first
        try {
          const data = await simpleApi.getScenarios()
          console.log('Successfully fetched scenarios via simpleApi:', data.length)
          console.log('First scenario:', data[0])
          setScenarios(data)
          return data
        } catch (simpleError) {
          console.warn('SimpleApi failed, trying regular apiClient:', simpleError)
          
          // Fallback to regular API client
          const data = await apiClient.getScenarios()
          console.log('Successfully fetched scenarios via apiClient:', data.length)
          console.log('First scenario:', data[0])
          setScenarios(data)
          return data
        }
      } catch (error) {
        console.error('Both API methods failed:', error)
        setScenarios([])
        return []
      }
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  // Mutation to create a new scenario
  const createScenarioMutation = useMutation({
    mutationFn: (data: ScenarioFormData) => apiClient.createScenario(data),
    onSuccess: (scenarioId, variables) => {
      // Invalidate and refetch scenarios
      queryClient.invalidateQueries({ queryKey: ['scenarios'] })
      
      toast({
        title: "Scenario Created",
        description: `Successfully created "${variables.name}" scenario.`,
        variant: "default"
      })
    },
    onError: (error) => {
      console.error('Failed to create scenario:', error)
      toast({
        title: "Error",
        description: "Failed to create scenario. Please try again.",
        variant: "destructive"
      })
    }
  })

  // Mutation to update a scenario
  const updateScenarioMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<ScenarioFormData> }) => 
      apiClient.updateScenario(id, data),
    onSuccess: (_, variables) => {
      // Invalidate and refetch scenarios
      queryClient.invalidateQueries({ queryKey: ['scenarios'] })
      queryClient.invalidateQueries({ queryKey: ['scenario', variables.id] })
      
      toast({
        title: "Scenario Updated",
        description: "Scenario has been successfully updated.",
        variant: "default"
      })
    },
    onError: (error) => {
      console.error('Failed to update scenario:', error)
      toast({
        title: "Error",
        description: "Failed to update scenario. Please try again.",
        variant: "destructive"
      })
    }
  })

  // Mutation to delete a scenario
  const deleteScenarioMutation = useMutation({
    mutationFn: (id: string) => apiClient.deleteScenario(id),
    onSuccess: (_, scenarioId) => {
      // Remove from store and invalidate queries
      removeScenarioFromStore(scenarioId)
      queryClient.invalidateQueries({ queryKey: ['scenarios'] })
      queryClient.removeQueries({ queryKey: ['scenario', scenarioId] })
      
      toast({
        title: "Scenario Deleted",
        description: "Scenario has been successfully deleted.",
        variant: "default"
      })
    },
    onError: (error) => {
      console.error('Failed to delete scenario:', error)
      toast({
        title: "Error",
        description: "Failed to delete scenario. Please try again.",
        variant: "destructive"
      })
    }
  })

  return {
    // Data
    scenarios: scenariosQuery.data || [],
    isLoading: scenariosQuery.isLoading,
    error: scenariosQuery.error,
    
    // Actions
    createScenario: createScenarioMutation.mutate,
    updateScenario: updateScenarioMutation.mutate,
    deleteScenario: deleteScenarioMutation.mutate,
    
    // Status
    isCreating: createScenarioMutation.isPending,
    isUpdating: updateScenarioMutation.isPending,
    isDeleting: deleteScenarioMutation.isPending,
    
    // Refetch
    refetch: scenariosQuery.refetch
  }
}

export function useScenario(id: string) {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  // Query to fetch a specific scenario
  const scenarioQuery = useQuery({
    queryKey: ['scenario', id],
    queryFn: () => apiClient.getScenario(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  return {
    scenario: scenarioQuery.data,
    isLoading: scenarioQuery.isLoading,
    error: scenarioQuery.error,
    refetch: scenarioQuery.refetch
  }
}

export function useProjections() {
  const { toast } = useToast()

  // Mutation to run projection for a scenario
  const runProjectionMutation = useMutation({
    mutationFn: ({ 
      scenarioId, 
      options 
    }: { 
      scenarioId: string; 
      options?: {
        includeMonteCarlo?: boolean;
        projectionMode?: 'years' | 'retirement';
        projectionValue?: number;
      }
    }) => apiClient.runProjection(scenarioId, options),
    onSuccess: () => {
      toast({
        title: "Projection Complete",
        description: "Financial projection has been calculated successfully.",
        variant: "default"
      })
    },
    onError: (error) => {
      console.error('Failed to run projection:', error)
      toast({
        title: "Error",
        description: "Failed to run projection. Please try again.",
        variant: "destructive"
      })
    }
  })

  // Mutation to compare scenarios
  const compareScenariosMutation = useMutation({
    mutationFn: (scenarioIds: string[]) => apiClient.compareScenarios(scenarioIds),
    onSuccess: () => {
      toast({
        title: "Comparison Complete",
        description: "Scenario comparison has been generated successfully.",
        variant: "default"
      })
    },
    onError: (error) => {
      console.error('Failed to compare scenarios:', error)
      toast({
        title: "Error",
        description: "Failed to compare scenarios. Please try again.",
        variant: "destructive"
      })
    }
  })

  return {
    // Actions
    runProjection: runProjectionMutation.mutate,
    compareScenarios: compareScenariosMutation.mutate,
    
    // Status
    isRunningProjection: runProjectionMutation.isPending,
    isComparingScenarios: compareScenariosMutation.isPending,
    
    // Data
    projectionResult: runProjectionMutation.data,
    comparisonResult: compareScenariosMutation.data,
    
    // Errors
    projectionError: runProjectionMutation.error,
    comparisonError: compareScenariosMutation.error
  }
}

export function useMonteCarloSimulation() {
  const { toast } = useToast()

  // Mutation to run Monte Carlo simulation
  const runSimulationMutation = useMutation({
    mutationFn: ({ 
      scenarioId, 
      parameters 
    }: { 
      scenarioId: string; 
      parameters?: any 
    }) => apiClient.runMonteCarloSimulation(scenarioId, parameters),
    onSuccess: () => {
      toast({
        title: "Simulation Complete",
        description: "Monte Carlo simulation has been completed successfully.",
        variant: "default"
      })
    },
    onError: (error) => {
      console.error('Failed to run Monte Carlo simulation:', error)
      toast({
        title: "Error", 
        description: "Failed to run simulation. Please try again.",
        variant: "destructive"
      })
    }
  })

  // Mutation to analyze withdrawal strategies
  const analyzeWithdrawalMutation = useMutation({
    mutationFn: (scenarioId: string) => apiClient.analyzeWithdrawalStrategies(scenarioId),
    onSuccess: () => {
      toast({
        title: "Analysis Complete",
        description: "Withdrawal strategy analysis has been completed successfully.",
        variant: "default"
      })
    },
    onError: (error) => {
      console.error('Failed to analyze withdrawal strategies:', error)
      toast({
        title: "Error",
        description: "Failed to analyze withdrawal strategies. Please try again.",
        variant: "destructive"
      })
    }
  })

  return {
    // Actions
    runSimulation: runSimulationMutation.mutate,
    analyzeWithdrawal: analyzeWithdrawalMutation.mutate,
    
    // Status
    isRunningSimulation: runSimulationMutation.isPending,
    isAnalyzingWithdrawal: analyzeWithdrawalMutation.isPending,
    
    // Data
    simulationResult: runSimulationMutation.data,
    withdrawalAnalysis: analyzeWithdrawalMutation.data,
    
    // Errors
    simulationError: runSimulationMutation.error,
    withdrawalError: analyzeWithdrawalMutation.error
  }
}