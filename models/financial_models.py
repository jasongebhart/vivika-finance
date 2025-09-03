"""
Pydantic models for financial planning data structures.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from enum import Enum

class ScenarioType(str, Enum):
    CURRENT = "current"
    RETIREMENT = "retirement"
    RELOCATION = "relocation"
    EDUCATION = "education"
    MAJOR_PURCHASE = "major_purchase"

class InvestmentType(str, Enum):
    STOCKS = "stocks"
    BONDS = "bonds"
    REAL_ESTATE = "real_estate"
    CASH = "cash"
    CRYPTO = "crypto"

class RetirementAccountType(str, Enum):
    TRADITIONAL_401K = "traditional_401k"
    ROTH_401K = "roth_401k"
    TRADITIONAL_IRA = "traditional_ira"
    ROTH_IRA = "roth_ira"
    PENSION = "pension"

class FinancialAssumptions(BaseModel):
    """Core financial assumptions for projections."""
    inflation_rate: float = Field(default=0.03, ge=0, le=0.2, description="Annual inflation rate")
    investment_return: float = Field(default=0.07, ge=0, le=0.5, description="Expected annual investment return")
    salary_growth_rate: float = Field(default=0.03, ge=0, le=0.2, description="Annual salary growth rate")
    social_security_cola: float = Field(default=0.025, ge=0, le=0.1, description="Social Security COLA rate")
    tax_rate: float = Field(default=0.22, ge=0, le=0.5, description="Effective tax rate")
    
    @validator('inflation_rate', 'investment_return', 'salary_growth_rate')
    def validate_rates(cls, v):
        if v < 0 or v > 1:
            raise ValueError('Rate must be between 0 and 1')
        return v

class Asset(BaseModel):
    """Individual asset definition."""
    name: str
    asset_type: InvestmentType
    current_value: float = Field(ge=0)
    expected_return: float = Field(default=0.07, ge=-1, le=1)
    allocation_percentage: float = Field(ge=0, le=1)

class Liability(BaseModel):
    """Individual liability definition."""
    name: str
    current_balance: float = Field(ge=0)
    interest_rate: float = Field(ge=0, le=1)
    minimum_payment: float = Field(ge=0)
    payoff_date: Optional[date] = None

class IncomeSource(BaseModel):
    """Income source definition."""
    name: str
    annual_amount: float = Field(ge=0)
    start_age: int = Field(ge=0, le=120)
    end_age: Optional[int] = Field(default=None, ge=0, le=120)
    growth_rate: float = Field(default=0.03, ge=0, le=1)
    is_taxable: bool = True

class ExpenseCategory(BaseModel):
    """Expense category definition."""
    name: str
    annual_amount: float = Field(ge=0)
    start_age: int = Field(ge=0, le=120)
    end_age: Optional[int] = Field(default=None, ge=0, le=120)
    inflation_adjusted: bool = True

class RetirementAccount(BaseModel):
    """Retirement account details."""
    account_type: RetirementAccountType
    current_balance: float = Field(ge=0)
    annual_contribution: float = Field(ge=0)
    employer_match: float = Field(default=0, ge=0)
    contribution_limit: float = Field(default=23000, ge=0)

class UserProfile(BaseModel):
    """User profile and current financial situation."""
    name: str
    birth_date: date
    current_age: int = Field(ge=18, le=120)
    retirement_age: int = Field(default=65, ge=50, le=100)
    life_expectancy: int = Field(default=90, ge=60, le=120)
    current_city: str
    target_city: Optional[str] = None
    
    # Financial data
    annual_salary: float = Field(ge=0)
    assets: List[Asset] = []
    liabilities: List[Liability] = []
    income_sources: List[IncomeSource] = []
    expenses: List[ExpenseCategory] = []
    retirement_accounts: List[RetirementAccount] = []
    
    @validator('retirement_age')
    def retirement_after_current_age(cls, v, values):
        if 'current_age' in values and v <= values['current_age']:
            raise ValueError('Retirement age must be after current age')
        return v

class MonteCarloParameters(BaseModel):
    """Parameters for Monte Carlo simulation."""
    num_simulations: int = Field(default=1000, ge=100, le=10000)
    stock_volatility: float = Field(default=0.2, ge=0.05, le=1.0)
    bond_volatility: float = Field(default=0.05, ge=0.01, le=0.5)
    correlation_stock_bond: float = Field(default=-0.2, ge=-1, le=1)
    sequence_risk_adjustment: bool = True

class ProjectionSettings(BaseModel):
    """Settings for financial projections."""
    start_year: int = Field(default_factory=lambda: datetime.now().year)
    projection_years: int = Field(default=40, ge=1, le=100)
    assumptions: FinancialAssumptions = FinancialAssumptions()
    monte_carlo: MonteCarloParameters = MonteCarloParameters()
    include_social_security: bool = True
    include_inflation: bool = True

class ScenarioInput(BaseModel):
    """Input for creating a financial scenario."""
    name: str
    description: Optional[str] = None
    scenario_type: ScenarioType
    user_profile: UserProfile
    projection_settings: ProjectionSettings
    
    # Scenario-specific parameters
    retirement_income_target: Optional[float] = None
    relocation_city: Optional[str] = None
    education_costs: Optional[Dict[str, float]] = None
    major_purchase_amount: Optional[float] = None
    major_purchase_timeline: Optional[int] = None

class ProjectionYear(BaseModel):
    """Single year projection data."""
    year: int
    age: int
    beginning_assets: float
    income: float
    expenses: float
    net_cash_flow: float
    ending_assets: float
    tax_liability: float

class MonteCarloResult(BaseModel):
    """Monte Carlo simulation results."""
    success_probability: float = Field(ge=0, le=1)
    percentile_10: float
    percentile_25: float
    percentile_50: float
    percentile_75: float
    percentile_90: float
    final_asset_distribution: List[float]
    worst_case_scenario: float
    best_case_scenario: float

class ScenarioProjection(BaseModel):
    """Complete scenario projection results."""
    scenario_id: str
    scenario_name: str
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Projection data
    yearly_projections: List[ProjectionYear]
    monte_carlo_results: Optional[MonteCarloResult] = None
    
    # Summary metrics
    final_net_worth: float
    retirement_income_replacement: float
    years_of_expenses_covered: float
    is_goal_achievable: bool
    
    # Assumptions used
    assumptions_used: FinancialAssumptions

class CityComparisonData(BaseModel):
    """Cost of living comparison between cities."""
    city_name: str
    state: str
    cost_index: float
    housing_cost: float
    utilities_cost: float
    grocery_cost: float
    transportation_cost: float
    healthcare_cost: float
    overall_cost_difference: float

class CityComparison(BaseModel):
    """Comparison between current and target cities."""
    current_city: CityComparisonData
    target_city: CityComparisonData
    annual_cost_difference: float
    net_worth_impact_10_year: float
    net_worth_impact_retirement: float

class EducationExpenseProjection(BaseModel):
    """Education expense projection."""
    institution_type: str  # "private_k12", "public_college", "private_college"
    annual_cost: float
    duration_years: int
    inflation_rate: float
    total_cost_present_value: float
    total_cost_future_value: float
    monthly_savings_required: float

class VehicleOwnershipProjection(BaseModel):
    """Vehicle ownership cost projection."""
    vehicle_type: str  # "economy", "midsize", "luxury", "electric"
    purchase_price: float
    financing_cost: float
    insurance_annual: float
    fuel_annual: float
    maintenance_annual: float
    depreciation_total: float
    total_cost_ownership: float

class GoalDefinition(BaseModel):
    """Financial goal definition."""
    goal_id: str
    name: str
    target_amount: float = Field(ge=0)
    target_date: date
    current_amount: float = Field(default=0, ge=0)
    monthly_contribution: float = Field(default=0, ge=0)
    expected_return: float = Field(default=0.05, ge=0, le=1)
    priority: int = Field(default=1, ge=1, le=10)

class GoalProjection(BaseModel):
    """Financial goal projection results."""
    goal: GoalDefinition
    projected_final_amount: float
    shortfall_amount: float
    probability_of_success: float
    required_monthly_contribution: float
    recommended_adjustments: List[str]

class SimulationResult(BaseModel):
    """Single simulation result for one year."""
    net_worth: float
    portfolio_value: float
    annual_income: float
    withdrawal_rate: float

class MonteCarloProjectionYear(BaseModel):
    """Monte Carlo projection data for a single year."""
    year: int
    simulation_results: List[SimulationResult]

class MonteCarloResult(BaseModel):
    """Enhanced Monte Carlo simulation results."""
    simulations_run: int
    projection_years: int
    success_probability: float = Field(ge=0, le=1)
    median_final_value: float
    mean_final_value: float
    std_dev_final_value: float
    worst_case_10th_percentile: float
    best_case_90th_percentile: float
    annual_projections: List[MonteCarloProjectionYear]
    final_year_distribution: Dict[str, List[float]]

class WithdrawalStrategy(BaseModel):
    """Individual withdrawal strategy analysis."""
    name: str
    description: str
    success_rate: float = Field(ge=0, le=1)
    median_final_value: float
    worst_case_10th_percentile: float

class WithdrawalStrategyAnalysis(BaseModel):
    """Analysis of different withdrawal strategies."""
    strategies: List[WithdrawalStrategy]

class GoalType(str, Enum):
    """Types of financial goals."""
    EMERGENCY_FUND = "emergency_fund"
    RETIREMENT = "retirement"
    MAJOR_PURCHASE = "major_purchase"
    EDUCATION = "education"
    DEBT_PAYOFF = "debt_payoff"

class Expense(BaseModel):
    """Individual expense definition."""
    name: str
    category: str
    annual_amount: float = Field(ge=0)
    start_age: int = Field(ge=0, le=120)
    end_age: Optional[int] = Field(default=None, ge=0, le=120)
    inflation_adjusted: bool = True