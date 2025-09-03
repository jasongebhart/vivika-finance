"""
Dynamic Financial Service - Generates real financial scenarios based on parameters.
This service takes the 6 dynamic parameters and creates realistic financial projections
by adjusting base financial data according to location, housing, education choices, etc.
"""

import json
import logging
from typing import Dict, Any, List
from pathlib import Path
from copy import deepcopy

logger = logging.getLogger(__name__)

class DynamicFinancialService:
    """Service to generate realistic financial scenarios based on dynamic parameters."""
    
    def __init__(self, config_path: str = "general.finance.json"):
        self.config_path = config_path
        self.base_financial_data = self._load_base_data()
        
        # Cost-of-living multipliers by location
        self.location_multipliers = {
            'Sf': {  # San Francisco
                'housing_cost': 2.8,
                'property_tax_rate': 0.75,  # Lower property tax rate
                'general_expenses': 1.4,
                'salary_adjustment': 1.3,
                'house_value': 3600000,
                'house_property_tax': 36599.26
            },
            'Sd': {  # San Diego  
                'housing_cost': 1.8,
                'property_tax_rate': 0.85,
                'general_expenses': 1.2,
                'salary_adjustment': 1.15,
                'house_value': 1800000, 
                'house_property_tax': 21000
            },
            'Mn': {  # Minnesota
                'housing_cost': 0.7,
                'property_tax_rate': 1.3,  # Higher property tax rate
                'general_expenses': 0.85,
                'salary_adjustment': 0.9,
                'house_value': 1200000,
                'house_property_tax': 15000
            }
        }
        
        # Housing type adjustments
        self.housing_adjustments = {
            'Own': {
                'mortgage_payment': True,
                'property_tax': True,
                'maintenance': True,
                'rent': 0
            },
            'Rent': {
                'mortgage_payment': False,
                'property_tax': False,
                'maintenance': False,
                'rent_multiplier': 0.7  # Rent is typically 70% of ownership cost
            }
        }
        
        # Education cost adjustments
        self.education_costs = {
            'Public': {
                'high_school_annual': 0,  # Free public education
                'college_annual': 25000   # Public college costs
            },
            'Private': {
                'high_school_annual': 62000,  # Private school
                'college_annual': 80000       # Private college
            },
            'Pripub': {  # Mixed - private high school, public college
                'high_school_annual': 62000,
                'college_annual': 25000
            }
        }
        
        # Retirement status adjustments
        self.retirement_adjustments = {
            'Work': {
                'salary_active': True,
                'retirement_expenses_reduction': 1.0
            },
            'Retired': {
                'salary_active': False,
                'retirement_expenses_reduction': 0.8  # 20% reduction in expenses
            }
        }
    
    def _load_base_data(self) -> Dict[str, Any]:
        """Load base financial configuration data."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load financial data from {self.config_path}: {e}")
            return {}
    
    def generate_scenario_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate complete financial scenario data based on dynamic parameters.
        
        Args:
            parameters: Dict containing location, spouse1Status, spouse2Status, 
                       housing, schoolType, projectionYears
        
        Returns:
            Complete financial scenario data structure
        """
        try:
            location = parameters.get('location', 'Sf')
            spouse1_status = parameters.get('spouse1Status', 'Work')
            spouse2_status = parameters.get('spouse2Status', 'Work')
            housing = parameters.get('housing', 'Own')
            school_type = parameters.get('schoolType', 'Private')
            projection_years = parameters.get('projectionYears', 8)
            
            logger.info(f"Generating scenario data for: {location}, {spouse1_status}/{spouse2_status}, {housing}, {school_type}, {projection_years}y")
            
            # Start with base financial structure
            scenario_data = {
                "name": "Havilah & Jason",
                "birth_date": "1973-01-01",
                "current_age": 52,
                "retirement_age": 65,
                "life_expectancy": 90,
                "current_city": self._get_city_name(location),
                "target_city": None,
                "annual_salary": self._calculate_salary(location, spouse1_status, spouse2_status),
                "assets": self._generate_assets(),
                "liabilities": [],
                "income_sources": self._generate_income_sources(spouse1_status, spouse2_status),
                "expenses": self._generate_expenses(location, housing, school_type, spouse1_status, spouse2_status),
                "retirement_accounts": []
            }
            
            projection_data = {
                "start_year": 2025,
                "projection_years": projection_years,
                "assumptions": {
                    "inflation_rate": 0.03,
                    "investment_return": 0.07,
                    "salary_growth_rate": 0.03,
                    "social_security_cola": 0.025,
                    "tax_rate": self._get_tax_rate(location)
                },
                "monte_carlo": {
                    "num_simulations": 1000,
                    "stock_volatility": 0.2,
                    "bond_volatility": 0.05,
                    "correlation_stock_bond": -0.2,
                    "sequence_risk_adjustment": True
                },
                "include_social_security": True,
                "include_inflation": True
            }
            
            return {
                "user_data": scenario_data,
                "projection_data": projection_data
            }
            
        except Exception as e:
            logger.error(f"Failed to generate scenario data: {e}")
            raise
    
    def _get_city_name(self, location: str) -> str:
        """Convert location code to city name."""
        city_names = {
            'Sf': 'San Francisco',
            'Sd': 'San Diego', 
            'Mn': 'Minnesota'
        }
        return city_names.get(location, 'San Francisco')
    
    def _calculate_salary(self, location: str, spouse1_status: str, spouse2_status: str) -> float:
        """Calculate total household salary based on location and employment status."""
        base_salary = 451117.0  # Base salary from existing data
        location_mult = self.location_multipliers.get(location, {}).get('salary_adjustment', 1.0)
        
        # Adjust for retirement status
        spouse1_mult = 1.0 if spouse1_status == 'Work' else 0.0
        spouse2_mult = 1.0 if spouse2_status == 'Work' else 0.0
        
        # Assume salary is split between spouses
        total_salary = base_salary * location_mult * (spouse1_mult * 0.6 + spouse2_mult * 0.4)
        
        return round(total_salary, 2)
    
    def _generate_assets(self) -> List[Dict[str, Any]]:
        """Generate asset list - same for all scenarios currently."""
        return [
            {
                "name": "HG Roth IRA (Roth)",
                "asset_type": "stocks",
                "current_value": 61753.0,
                "expected_return": 0.07,
                "allocation_percentage": 0.7
            },
            {
                "name": "HG Traditional (IRA)",
                "asset_type": "stocks", 
                "current_value": 194394.0,
                "expected_return": 0.07,
                "allocation_percentage": 0.7
            },
            {
                "name": "HG Intel 401k (401K)",
                "asset_type": "stocks",
                "current_value": 808801.0,
                "expected_return": 0.07,
                "allocation_percentage": 0.7
            },
            {
                "name": "HG Intel Serplus (401K)",
                "asset_type": "stocks",
                "current_value": 80721.0,
                "expected_return": 0.07,
                "allocation_percentage": 0.7
            },
            {
                "name": "HG ML 401K (401K)",
                "asset_type": "stocks",
                "current_value": 552276.0,
                "expected_return": 0.07,
                "allocation_percentage": 0.7
            },
            {
                "name": "JG Roth IRA (Roth)",
                "asset_type": "stocks",
                "current_value": 68977.0,
                "expected_return": 0.07,
                "allocation_percentage": 0.7
            },
            {
                "name": "JG Traditional IRA (IRA)",
                "asset_type": "stocks",
                "current_value": 104754.0,
                "expected_return": 0.07,
                "allocation_percentage": 0.7
            },
            {
                "name": "JG Rollover IRA (IRA)",
                "asset_type": "stocks",
                "current_value": 706258.0,
                "expected_return": 0.07,
                "allocation_percentage": 0.7
            },
            {
                "name": "JG MITRE 401a (401K)",
                "asset_type": "stocks",
                "current_value": 670071.0,
                "expected_return": 0.07,
                "allocation_percentage": 0.7
            },
            {
                "name": "JG MITRE 403b (401K)",
                "asset_type": "stocks",
                "current_value": 1165974.0,
                "expected_return": 0.07,
                "allocation_percentage": 0.7
            },
            {
                "name": "J&H Primecap",
                "asset_type": "stocks",
                "current_value": 475316.0,
                "expected_return": 0.07,
                "allocation_percentage": 0.8
            },
            {
                "name": "HG Intel Stock", 
                "asset_type": "stocks",
                "current_value": 226090.0,
                "expected_return": 0.07,
                "allocation_percentage": 0.8
            },
            {
                "name": "Employee Stock Purchase Plan",
                "asset_type": "stocks",
                "current_value": 25000.0,
                "expected_return": 0.08,
                "allocation_percentage": 0.9
            }
        ]
    
    def _generate_income_sources(self, spouse1_status: str, spouse2_status: str) -> List[Dict[str, Any]]:
        """Generate income sources based on retirement status."""
        income_sources = []
        
        # Add Social Security if either spouse is retired
        if spouse1_status == 'Retired' or spouse2_status == 'Retired':
            # Simplified Social Security calculation
            ss_amount = 35000 if spouse1_status == 'Retired' else 0
            ss_amount += 28000 if spouse2_status == 'Retired' else 0
            
            if ss_amount > 0:
                income_sources.append({
                    "name": "Social Security",
                    "annual_amount": ss_amount,
                    "start_age": 65,
                    "end_age": 90,
                    "growth_rate": 0.025
                })
        
        return income_sources
    
    def _generate_expenses(self, location: str, housing: str, school_type: str, 
                          spouse1_status: str, spouse2_status: str) -> List[Dict[str, Any]]:
        """Generate expense list based on parameters."""
        expenses = []
        location_mult = self.location_multipliers.get(location, {})
        general_mult = location_mult.get('general_expenses', 1.0)
        
        # Living Expenses
        living_base = sum(self.base_financial_data.get('LIVING_EXPENSES', {}).values()) * 12
        expenses.append({
            "name": "Living Expenses",
            "annual_amount": round(living_base * general_mult),
            "start_age": 52,
            "end_age": None,
            "inflation_adjusted": True,
            "line_items": self._adjust_line_items(
                self.base_financial_data.get('LIVING_EXPENSES', {}), general_mult
            )
        })
        
        # Housing Expenses
        housing_expenses = self._generate_housing_expenses(location, housing)
        expenses.extend(housing_expenses)
        
        # Utilities
        utilities_base = sum(self.base_financial_data.get('UTILITIES', {}).values()) * 12
        expenses.append({
            "name": "Utilities",
            "annual_amount": round(utilities_base * general_mult),
            "start_age": 52,
            "end_age": None,
            "inflation_adjusted": True,
            "line_items": self._adjust_line_items(
                self.base_financial_data.get('UTILITIES', {}), general_mult
            )
        })
        
        # Transportation  
        transport_base = sum(self.base_financial_data.get('TRANSPORTATION', {}).values()) * 12
        expenses.append({
            "name": "Transportation",
            "annual_amount": round(transport_base * general_mult),
            "start_age": 52,
            "end_age": None,
            "inflation_adjusted": True,
            "line_items": self._adjust_line_items(
                self.base_financial_data.get('TRANSPORTATION', {}), general_mult
            )
        })
        
        # Insurance
        insurance_base = sum(self.base_financial_data.get('INSURANCE', {}).values()) * 12
        expenses.append({
            "name": "Insurance",
            "annual_amount": round(insurance_base * general_mult),
            "start_age": 52,
            "end_age": None,
            "inflation_adjusted": True,
            "line_items": self._adjust_line_items(
                self.base_financial_data.get('INSURANCE', {}), general_mult
            )
        })
        
        # Subscriptions
        subs_base = sum(self.base_financial_data.get('SUBSCRIPTIONS', {}).values()) * 12
        expenses.append({
            "name": "Subscriptions",
            "annual_amount": round(subs_base),
            "start_age": 52,
            "end_age": None,
            "inflation_adjusted": True,
            "line_items": self.base_financial_data.get('SUBSCRIPTIONS', {})
        })
        
        # Vacation & Travel (location-adjusted)
        travel_base = 46000 * general_mult
        expenses.append({
            "name": "Vacation & Travel",
            "annual_amount": round(travel_base),
            "start_age": 52,
            "end_age": None,
            "inflation_adjusted": True
        })
        
        # Education Expenses
        education_expenses = self._generate_education_expenses(school_type)
        expenses.extend(education_expenses)
        
        # Kids Activities (same for all locations)
        expenses.extend(self._generate_kids_activities())
        
        return expenses
    
    def _generate_housing_expenses(self, location: str, housing: str) -> List[Dict[str, Any]]:
        """Generate housing-related expenses."""
        expenses = []
        location_data = self.location_multipliers.get(location, {})
        
        if housing == 'Own':
            # Property tax (varies significantly by location)
            property_tax = location_data.get('house_property_tax', 15000)
            expenses.append({
                "name": "Property Tax",
                "annual_amount": property_tax,
                "start_age": 52,
                "end_age": None,
                "inflation_adjusted": True
            })
            
            # Housing maintenance and other costs
            housing_base = sum(self.base_financial_data.get('HOUSING_EXPENSES', {}).values()) * 12
            housing_mult = location_data.get('housing_cost', 1.0)
            expenses.append({
                "name": "Housing Expenses",
                "annual_amount": round(housing_base * housing_mult),
                "start_age": 52,
                "end_age": None,
                "inflation_adjusted": True,
                "line_items": self._adjust_line_items(
                    self.base_financial_data.get('HOUSING_EXPENSES', {}), housing_mult
                )
            })
            
        elif housing == 'Rent':
            # Calculate rent based on location
            house_value = location_data.get('house_value', 1200000)
            annual_rent = house_value * 0.04  # 4% of house value as annual rent
            
            expenses.append({
                "name": "Rent",
                "annual_amount": round(annual_rent),
                "start_age": 52,
                "end_age": None,
                "inflation_adjusted": True
            })
            
            # Reduced housing expenses (no maintenance, property tax, etc.)
            housing_base = 2000 * 12  # Basic renter's costs
            expenses.append({
                "name": "Housing Expenses",
                "annual_amount": housing_base,
                "start_age": 52,
                "end_age": None,
                "inflation_adjusted": True,
                "line_items": {
                    "renter_insurance": 100,
                    "utilities_deposit": 50,
                    "maintenance_reserve": 100
                }
            })
        
        return expenses
    
    def _generate_education_expenses(self, school_type: str) -> List[Dict[str, Any]]:
        """Generate education expenses based on school type."""
        expenses = []
        edu_costs = self.education_costs.get(school_type, {})
        
        # High School costs - realistic timing based on kids' ages
        # Assuming Tate (born 2009, currently ~15) and Wynn (born 2012, currently ~12)
        hs_cost = edu_costs.get('high_school_annual', 0)
        if hs_cost > 0:
            expenses.extend([
                {
                    "name": "Tate High School",
                    "annual_amount": hs_cost,
                    "start_age": 52,  # Tate currently 15, already in high school
                    "end_age": 54,    # Through age 17 (when parent is 54)
                    "inflation_adjusted": True
                },
                {
                    "name": "Wynn High School", 
                    "annual_amount": hs_cost,
                    "start_age": 54,  # Wynn will start high school when parent is 54
                    "end_age": 58,    # Through age 17 (when parent is 58)
                    "inflation_adjusted": True
                }
            ])
        
        # College costs - 4 years each child, realistic timing
        # Tate: college age 18-22 (when parent is 55-59)
        # Wynn: college age 18-22 (when parent is 58-62)
        college_cost = edu_costs.get('college_annual', 25000)
        expenses.extend([
            {
                "name": "Tate College",
                "annual_amount": college_cost,
                "start_age": 55,  # Tate starts college at 18 (when parent is 55)
                "end_age": 59,    # 4 years through age 22 (when parent is 59)
                "inflation_adjusted": True
            },
            {
                "name": "Wynn College",
                "annual_amount": college_cost,
                "start_age": 58,  # Wynn starts college at 18 (when parent is 58)
                "end_age": 62,    # 4 years through age 22 (when parent is 62)
                "inflation_adjusted": True
            }
        ])
        
        return expenses
    
    def _generate_kids_activities(self) -> List[Dict[str, Any]]:
        """Generate kids activities expenses based on realistic kid ages."""
        sports_data = self.base_financial_data.get('KIDS_ACTIVITIES', {}).get('SPORTS', {})
        
        return [
            {
                "name": "Baseball Activities",
                "annual_amount": 5800.0,
                "start_age": 52,  # While kids are young enough for baseball
                "end_age": 60,    # Through their teenage years
                "inflation_adjusted": True,
                "line_items": sports_data.get('BASEBALL', {})
            },
            {
                "name": "Ski Team Activities",
                "annual_amount": 23121.0,
                "start_age": 52,  # While kids are young enough for ski team
                "end_age": 58,    # Through their high school years
                "inflation_adjusted": True,
                "line_items": sports_data.get('SKI_TEAM', {})
            }
        ]
    
    def _adjust_line_items(self, line_items: Dict[str, float], multiplier: float) -> Dict[str, float]:
        """Apply multiplier to line items."""
        return {key: round(value * multiplier, 2) for key, value in line_items.items()}
    
    def _get_tax_rate(self, location: str) -> float:
        """Get tax rate based on location."""
        tax_rates = {
            'Sf': 0.37,  # Higher tax rate (CA state + federal)
            'Sd': 0.35,  # CA state + federal  
            'Mn': 0.32   # MN state + federal
        }
        return tax_rates.get(location, 0.32)