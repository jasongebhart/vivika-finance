import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import type { 
  Scenario, 
  ScenarioProjection, 
  ScenarioFormData, 
  MonteCarloParameters,
  CityComparison,
  ApiResponse,
  PaginatedResponse
} from '@/types'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    const baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'
    console.log('ApiClient: Initializing with baseURL:', baseURL)
    
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor for auth tokens
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getAuthToken()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.handleUnauthorized()
        }
        return Promise.reject(error)
      }
    )
  }

  private getAuthToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token')
    }
    return null
  }

  private handleUnauthorized(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
  }

  // Generic request method
  private async request<T>(config: AxiosRequestConfig): Promise<T> {
    try {
      const response: AxiosResponse<T> = await this.client.request(config)
      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(
          error.response?.data?.message || 
          error.message || 
          'An unexpected error occurred'
        )
      }
      throw error
    }
  }

  // Health check
  async healthCheck(): Promise<{ status: string; service: string }> {
    return this.request({
      method: 'GET',
      url: '/health',
    })
  }

  // Scenario management
  async getScenarios(): Promise<Scenario[]> {
    try {
      console.log('ApiClient.getScenarios: Using Next.js API proxy')
      const response = await fetch('/api/scenarios')
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      
      const data = await response.json()
      console.log('ApiClient.getScenarios: Proxy success, got', data.length, 'scenarios')
      return data
    } catch (error) {
      console.error('ApiClient.getScenarios: Proxy failed:', error)
      // Fallback to direct axios call
      return this.request({
        method: 'GET',
        url: '/scenarios',
      })
    }
  }

  async getScenario(id: string): Promise<Scenario> {
    try {
      console.log('ApiClient.getScenario: Fetching directly from backend for scenario:', id)
      const response = await fetch(`http://localhost:8000/api/scenarios/${id}?t=${Date.now()}`)
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      
      const data = await response.json()
      console.log('ApiClient.getScenario: Backend success for scenario:', id)
      
      // Debug: Check if line items are present
      if (data.user_data) {
        try {
          const userData = JSON.parse(data.user_data)
          const expensesWithLineItems = userData.expenses?.filter((e: any) => e.line_items) || []
          console.log('ApiClient.getScenario: Found', expensesWithLineItems.length, 'expenses with line items')
        } catch (e) {
          console.error('ApiClient.getScenario: Error parsing user_data:', e)
        }
      }
      
      return data
    } catch (error) {
      console.error('ApiClient.getScenario: Backend failed:', error)
      // Fallback to proxy if direct fails
      const response = await fetch(`/api/scenarios/${id}`)
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      return response.json()
    }
  }

  async createScenario(data: ScenarioFormData): Promise<string> {
    return this.request({
      method: 'POST',
      url: '/scenarios',
      data,
    })
  }

  async updateScenario(id: string, data: Partial<ScenarioFormData>): Promise<void> {
    return this.request({
      method: 'PUT',
      url: `/scenarios/${id}`,
      data,
    })
  }

  async deleteScenario(id: string): Promise<void> {
    return this.request({
      method: 'DELETE',
      url: `/scenarios/${id}`,
    })
  }

  // Projections
  async runProjection(
    scenarioId: string,
    options: {
      includeMonteCarlo?: boolean
      projectionMode?: 'years' | 'retirement'
      projectionValue?: number
    } = {}
  ): Promise<ScenarioProjection> {
    const params = new URLSearchParams()
    if (options.includeMonteCarlo) params.append('include_monte_carlo', 'true')
    if (options.projectionMode) params.append('projection_mode', options.projectionMode)
    if (options.projectionValue) params.append('projection_value', String(options.projectionValue))

    return this.request({
      method: 'POST',
      url: `/scenarios/${scenarioId}/project?${params.toString()}`,
    })
  }

  async compareScenarios(scenarioIds: string[]): Promise<any> {
    return this.request({
      method: 'POST',
      url: '/scenarios/compare',
      data: { scenario_ids: scenarioIds },
    })
  }

  // Monte Carlo simulations
  async runMonteCarloSimulation(
    scenarioId: string,
    parameters?: MonteCarloParameters
  ): Promise<any> {
    return this.request({
      method: 'POST',
      url: `/monte-carlo/${scenarioId}`,
      data: parameters,
    })
  }

  async analyzeWithdrawalStrategies(scenarioId: string): Promise<any> {
    return this.request({
      method: 'POST',
      url: `/withdrawal-strategies/${scenarioId}`,
    })
  }

  // City comparison
  async compareCities(currentCity: string, targetCity: string): Promise<CityComparison> {
    return this.request({
      method: 'GET',
      url: `/city-comparison/${encodeURIComponent(currentCity)}/${encodeURIComponent(targetCity)}`,
    })
  }

  async getCityData(cityName: string): Promise<any> {
    return this.request({
      method: 'GET',
      url: `/city-data/${encodeURIComponent(cityName)}`,
    })
  }

  // Education planning
  async projectEducationExpenses(params: {
    institutionType: string
    startYear: number
    durationYears: number
    currentChildAge: number
  }): Promise<any> {
    return this.request({
      method: 'POST',
      url: '/education-projection',
      data: params,
    })
  }

  // Vehicle analysis
  async analyzeVehicleOwnership(params: {
    vehicleType: string
    ownershipYears: number
    annualMileage?: number
  }): Promise<any> {
    return this.request({
      method: 'POST',
      url: '/vehicle-analysis',
      data: params,
    })
  }

  // Goals
  async analyzeGoals(goals: any[]): Promise<any> {
    return this.request({
      method: 'POST',
      url: '/goals/analyze',
      data: { goals },
    })
  }

  // Data import/export
  async importScenarios(scenariosData: any): Promise<any> {
    return this.request({
      method: 'POST',
      url: '/scenarios/import',
      data: scenariosData,
    })
  }

  async exportScenarios(): Promise<any> {
    return this.request({
      method: 'GET',
      url: '/export/scenarios',
    })
  }

  // External data
  async getInflationData(): Promise<any> {
    return this.request({
      method: 'GET',
      url: '/external-data/inflation',
    })
  }

  async getMarketData(): Promise<any> {
    return this.request({
      method: 'GET',
      url: '/external-data/market',
    })
  }
}

// WebSocket client for real-time updates
export class WebSocketClient {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectInterval = 5000

  connect(scenarioId: string, onMessage: (data: any) => void): void {
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'
    
    try {
      this.ws = new WebSocket(`${wsUrl}/ws/simulation/${scenarioId}`)
      
      this.ws.onopen = () => {
        console.log('WebSocket connected')
        this.reconnectAttempts = 0
      }
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          onMessage(data)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }
      
      this.ws.onclose = () => {
        console.log('WebSocket disconnected')
        this.attemptReconnect(scenarioId, onMessage)
      }
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
    } catch (error) {
      console.error('Error creating WebSocket connection:', error)
    }
  }

  private attemptReconnect(scenarioId: string, onMessage: (data: any) => void): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
      
      setTimeout(() => {
        this.connect(scenarioId, onMessage)
      }, this.reconnectInterval)
    }
  }

  send(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}

// Export singleton instance
export const apiClient = new ApiClient()
export default apiClient