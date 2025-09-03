"""
Database models for financial configuration data.
"""

from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime

class UserProfile(BaseModel):
    """User profile information."""
    parent_one: str
    parent_two: str

class HousingDetails(BaseModel):
    """Housing configuration details."""
    include_new_house: bool
    home_tenure: str
    residence_location: str

class TaxRates(BaseModel):
    """Tax rate configuration."""
    assumed: float
    federal_single: float
    state_single: float
    federal_dual: float
    state_dual: float

class FinancialAssumptions(BaseModel):
    """Financial projection assumptions."""
    assumption_description: str
    interest_rate: float
    years: int

class IncomeVariant(BaseModel):
    """Income configuration for spouse variants."""
    base: float
    bonus: float
    quarterly: float

class InvestmentContributions(BaseModel):
    """Investment contribution configuration."""
    retirement_contribution: float
    hsa: float
    serplus: float

class PostTaxInvestments(BaseModel):
    """Post-tax investment configuration."""
    retirement_contribution: float
    employee_stock_purchase_plan: float

class SpouseVariant(BaseModel):
    """Spouse income and investment variant."""
    yearly_income: IncomeVariant
    pretax_investments: InvestmentContributions
    posttax_investments: PostTaxInvestments

class RetirementAccount(BaseModel):
    """Individual retirement account."""
    name: str
    amount: float

class PersonRetirement(BaseModel):
    """Retirement accounts for one person."""
    name: str
    roth_accounts: List[RetirementAccount] = []
    ira_accounts: List[RetirementAccount] = []
    k401_accounts: List[RetirementAccount] = []

class Investment(BaseModel):
    """Investment details."""
    name: str
    type: str
    amount: float

class SchoolYear(BaseModel):
    """Individual school year cost."""
    year: int
    cost: float
    name: str
    type: str

class ChildEducation(BaseModel):
    """Child's education plan."""
    name: str
    college: List[SchoolYear] = []
    high_school: List[SchoolYear] = []

class EducationVariant(BaseModel):
    """Education scenario variant."""
    type: str
    children: List[ChildEducation] = []

class HouseData(BaseModel):
    """House property information."""
    description: str
    cost_basis: float
    closing_costs: float = 0
    home_improvement: float = 0
    value: float
    mortgage_principal: float
    commission_rate: float
    annual_growth_rate: float
    interest_rate: float
    monthly_payment: float
    payments_made: int
    number_of_payments: int
    annual_property_tax: float
    sell_house: bool = False

class ExpenseCategory(BaseModel):
    """A category of expenses with individual line items."""
    category_name: str
    line_items: Dict[str, float]

class FinancialConfiguration(BaseModel):
    """Complete financial configuration data."""
    # User information
    user_profile: UserProfile
    housing_details: HousingDetails
    tax_rates: TaxRates
    financial_assumptions: FinancialAssumptions
    
    # Expense categories
    vacation_expenses: Dict[str, float]
    miscellaneous_expenses: Dict[str, Any]
    miscellaneous_income: Dict[str, Any]
    housing_expenses: Dict[str, float]
    living_expenses: Dict[str, float]
    leisure_activities: Dict[str, float]
    transportation: Dict[str, float]
    kids_activities: Dict[str, Any]
    excluded_expenses: List[str]
    utilities: Dict[str, float]
    insurance: Dict[str, float]
    subscriptions: Dict[str, float]
    
    # Income and investment variants
    spouse1_variants: Dict[str, SpouseVariant]
    spouse2_variants: Dict[str, SpouseVariant]
    
    # Retirement and investment data
    retirement: List[PersonRetirement]
    retirement_contribution_scenarios: Dict[str, Any]
    investments: Dict[str, Investment]
    
    # Education scenarios
    children_variants: Dict[str, EducationVariant]
    
    # House data
    house: HouseData
    new_house: HouseData
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None