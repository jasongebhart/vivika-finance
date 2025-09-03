// Core data types for the financial planning application

export interface UserProfile {
  id?: string
  name: string
  birth_date: string
  current_age: number
  retirement_age: number
  life_expectancy: number
  current_city: string
  target_city?: string
  annual_salary: number
  assets: Asset[]
  liabilities: Liability[]
  income_sources: IncomeSource[]
  expenses: Expense[]
  retirement_accounts: RetirementAccount[]
}

export interface Asset {
  id?: string
  name: string
  type: 'checking' | 'savings' | 'investment' | 'real_estate' | 'other'
  current_value: number
  growth_rate?: number
  liquid: boolean
}

export interface Liability {
  id?: string
  name: string
  type: 'mortgage' | 'car_loan' | 'credit_card' | 'student_loan' | 'other'
  current_balance: number
  monthly_payment: number
  interest_rate: number
  remaining_payments?: number
}

export interface IncomeSource {
  id?: string
  name: string
  type: 'salary' | 'bonus' | 'rental' | 'business' | 'investment' | 'other'
  annual_amount: number
  growth_rate?: number
  start_age?: number
  end_age?: number
}

export interface Expense {
  id?: string
  name: string
  category: 'housing' | 'transportation' | 'food' | 'healthcare' | 'entertainment' | 'other'
  annual_amount: number
  inflation_adjusted: boolean
  start_age?: number
  end_age?: number
}

export interface RetirementAccount {
  id?: string
  name: string
  type: '401k' | 'ira' | 'roth_ira' | 'pension' | 'other'
  current_balance: number
  annual_contribution: number
  employer_match?: number
  vesting_schedule?: number[]
}

export interface Scenario {
  id: string
  name: string
  description: string
  scenario_type: 'current' | 'retirement' | 'relocation' | 'education' | 'major_purchase'
  user_profile: UserProfile
  projection_settings: ProjectionSettings
  retirement_income_target?: number
  relocation_city?: string
  education_costs?: EducationCosts
  major_purchase_amount?: number
  created_at: string
  updated_at: string
}

export interface ProjectionSettings {
  projection_years: number
  assumptions: FinancialAssumptions
  monte_carlo?: MonteCarloParameters
}

export interface FinancialAssumptions {
  inflation_rate: number
  investment_return: number
  salary_growth_rate: number
  tax_rate: number
  healthcare_inflation?: number
  social_security_start_age?: number
}

export interface MonteCarloParameters {
  num_simulations: number
  return_volatility: number
  inflation_volatility: number
  salary_volatility: number
  confidence_intervals: number[]
}

export interface YearlyProjection {
  year: number
  age: number
  annual_income: number
  annual_expenses: number
  net_cash_flow: number
  investment_contributions: number
  investment_value: number
  retirement_balance: number
  net_worth: number
  portfolio_value: number
}

export interface ScenarioProjection {
  scenario_id: string
  yearly_projections: YearlyProjection[]
  monte_carlo_results?: MonteCarloResults
  summary_statistics: ProjectionSummary
}

export interface MonteCarloResults {
  simulations: MonteCarloSimulation[]
  percentiles: Record<string, number[]>
  success_probability: number
  median_final_value: number
  worst_case_value: number
  best_case_value: number
}

export interface MonteCarloSimulation {
  simulation_id: number
  yearly_values: number[]
  final_value: number
  success: boolean
}

export interface ProjectionSummary {
  final_net_worth: number
  retirement_income_replacement_ratio: number
  years_of_retirement_funding: number
  peak_net_worth_year: number
  total_contributions: number
  total_investment_growth: number
}

export interface CityComparison {
  current_city: string
  target_city: string
  cost_differences: CostCategory[]
  total_cost_difference: number
  impact_on_projections: ProjectionImpact
}

export interface CostCategory {
  category: string
  current_cost: number
  target_cost: number
  difference: number
  difference_percentage: number
}

export interface ProjectionImpact {
  annual_savings_difference: number
  retirement_age_impact: number
  final_net_worth_impact: number
}

export interface EducationCosts {
  institution_type: 'public' | 'private' | 'community'
  annual_tuition: number
  years_of_education: number
  start_year: number
  inflation_rate: number
  financial_aid_percentage?: number
}

export interface VehicleOwnership {
  vehicle_type: string
  purchase_price: number
  financing_details?: VehicleFinancing
  annual_expenses: VehicleExpenses
  ownership_years: number
  depreciation_schedule: number[]
}

export interface VehicleFinancing {
  down_payment: number
  loan_amount: number
  interest_rate: number
  loan_term_months: number
  monthly_payment: number
}

export interface VehicleExpenses {
  insurance: number
  fuel: number
  maintenance: number
  registration: number
  other: number
}

export interface Goal {
  id: string
  name: string
  target_amount: number
  current_amount: number
  target_date: string
  priority: 'high' | 'medium' | 'low'
  category: 'retirement' | 'emergency' | 'house' | 'education' | 'travel' | 'other'
  monthly_contribution: number
  progress_percentage: number
}

// UI State types
export interface AppState {
  theme: 'light' | 'dark' | 'system'
  sidebarOpen: boolean
  selectedScenario: Scenario | null
  scenarios: Scenario[]
  projections: ScenarioProjection | null
  isLoading: boolean
  error: string | null
}

// API Response types
export interface ApiResponse<T> {
  data: T
  message?: string
  status: 'success' | 'error'
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  limit: number
  hasMore: boolean
}

// Form types
export interface ScenarioFormData {
  name: string
  description: string
  scenario_type: Scenario['scenario_type']
  user_profile: Partial<UserProfile>
  projection_settings: Partial<ProjectionSettings>
  retirement_income_target?: number
  relocation_city?: string
  education_costs?: Partial<EducationCosts>
  major_purchase_amount?: number
}

// Chart data types
export interface ChartDataPoint {
  x: number | string
  y: number
  label?: string
  color?: string
}

export interface ChartSeries {
  name: string
  data: ChartDataPoint[]
  color?: string
  type?: 'line' | 'area' | 'bar'
}

export interface ChartConfig {
  title: string
  xAxis: {
    label: string
    type: 'number' | 'category' | 'time'
  }
  yAxis: {
    label: string
    format: 'currency' | 'percentage' | 'number'
  }
  series: ChartSeries[]
  interactive?: boolean
  showLegend?: boolean
}