import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import type { AppState, Scenario, ScenarioProjection } from '@/types'

interface AppStore extends AppState {
  // Year Range Control State
  yearRange: number
  startYear: number
  
  // Actions
  setTheme: (theme: AppState['theme']) => void
  toggleSidebar: () => void
  setSidebarOpen: (open: boolean) => void
  setSelectedScenario: (scenario: Scenario | null) => void
  setScenarios: (scenarios: Scenario[]) => void
  addScenario: (scenario: Scenario) => void
  updateScenario: (id: string, scenario: Partial<Scenario>) => void
  removeScenario: (id: string) => void
  setProjections: (projections: ScenarioProjection | null) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearError: () => void
  
  // Year Range Actions
  setYearRange: (years: number) => void
  setStartYear: (year: number) => void
  resetYearRange: () => void
}

export const useAppStore = create<AppStore>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        theme: 'system',
        sidebarOpen: true,
        selectedScenario: null,
        scenarios: [],
        projections: null,
        isLoading: false,
        error: null,
        
        // Year Range Initial State
        yearRange: 5, // Default to 5 years
        startYear: new Date().getFullYear(),

        // Actions
        setTheme: (theme) => {
          set({ theme }, false, 'setTheme')
        },

        toggleSidebar: () => {
          set({ sidebarOpen: !get().sidebarOpen }, false, 'toggleSidebar')
        },

        setSidebarOpen: (open) => {
          set({ sidebarOpen: open }, false, 'setSidebarOpen')
        },

        setSelectedScenario: (scenario) => {
          set({ selectedScenario: scenario }, false, 'setSelectedScenario')
        },

        setScenarios: (scenarios) => {
          set({ scenarios }, false, 'setScenarios')
        },

        addScenario: (scenario) => {
          set(
            (state) => ({
              scenarios: [scenario, ...state.scenarios],
            }),
            false,
            'addScenario'
          )
        },

        updateScenario: (id, updates) => {
          set(
            (state) => ({
              scenarios: state.scenarios.map((scenario) =>
                scenario.id === id ? { ...scenario, ...updates } : scenario
              ),
              selectedScenario:
                state.selectedScenario?.id === id
                  ? { ...state.selectedScenario, ...updates }
                  : state.selectedScenario,
            }),
            false,
            'updateScenario'
          )
        },

        removeScenario: (id) => {
          set(
            (state) => ({
              scenarios: state.scenarios.filter((scenario) => scenario.id !== id),
              selectedScenario:
                state.selectedScenario?.id === id ? null : state.selectedScenario,
            }),
            false,
            'removeScenario'
          )
        },

        setProjections: (projections) => {
          set({ projections }, false, 'setProjections')
        },

        setLoading: (loading) => {
          set({ isLoading: loading }, false, 'setLoading')
        },

        setError: (error) => {
          set({ error }, false, 'setError')
        },

        clearError: () => {
          set({ error: null }, false, 'clearError')
        },

        // Year Range Actions
        setYearRange: (years) => {
          if (get().yearRange !== years) {
            set({ yearRange: years }, false, 'setYearRange')
          }
        },

        setStartYear: (year) => {
          if (get().startYear !== year) {
            set({ startYear: year }, false, 'setStartYear')
          }
        },

        resetYearRange: () => {
          const currentYear = new Date().getFullYear()
          const state = get()
          if (state.yearRange !== 5 || state.startYear !== currentYear) {
            set({ 
              yearRange: 5, 
              startYear: currentYear 
            }, false, 'resetYearRange')
          }
        },
      }),
      {
        name: 'finance-planner-store',
        partialize: (state) => ({
          theme: state.theme,
          sidebarOpen: state.sidebarOpen,
          scenarios: state.scenarios,
          selectedScenario: state.selectedScenario,
          yearRange: state.yearRange,
          startYear: state.startYear,
        }),
      }
    ),
    {
      name: 'FinancePlannerStore',
    }
  )
)

// Selectors for better performance
export const useTheme = () => useAppStore((state) => state.theme)
export const useSidebar = () => useAppStore((state) => ({ 
  isOpen: state.sidebarOpen, 
  toggle: state.toggleSidebar,
  setOpen: state.setSidebarOpen 
}))
export const useScenarios = () => useAppStore((state) => ({
  scenarios: state.scenarios,
  selectedScenario: state.selectedScenario,
  setScenarios: state.setScenarios,
  setSelectedScenario: state.setSelectedScenario,
  addScenario: state.addScenario,
  updateScenario: state.updateScenario,
  removeScenario: state.removeScenario,
}))
export const useProjections = () => useAppStore((state) => ({
  projections: state.projections,
  setProjections: state.setProjections,
}))
export const useAppStatus = () => useAppStore((state) => ({
  isLoading: state.isLoading,
  error: state.error,
  setLoading: state.setLoading,
  setError: state.setError,
  clearError: state.clearError,
}))

export const useYearRangeStore = () => {
  const yearRange = useAppStore((state) => state.yearRange)
  const startYear = useAppStore((state) => state.startYear)
  const setYearRange = useAppStore((state) => state.setYearRange)
  const setStartYear = useAppStore((state) => state.setStartYear)
  const resetYearRange = useAppStore((state) => state.resetYearRange)

  // Calculate derived values
  const endYear = startYear + yearRange - 1
  const yearArray = Array.from({ length: yearRange }, (_, i) => startYear + i)
  const isYearInRange = (year: number) => year >= startYear && year <= endYear

  return {
    yearRange,
    startYear,
    endYear,
    yearArray,
    setYearRange,
    setStartYear,
    resetYearRange,
    isYearInRange,
  }
}