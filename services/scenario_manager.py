"""
Scenario management and financial projection services.
"""

import asyncio
import json
import uuid
from datetime import datetime, date
from typing import List, Dict, Optional
from pathlib import Path
import aiosqlite
import logging

from models.financial_models import (
    ScenarioInput,
    ScenarioProjection,
    ProjectionYear,
    UserProfile,
    ProjectionSettings,
    CityComparison,
    CityComparisonData,
    EducationExpenseProjection,
    VehicleOwnershipProjection,
    GoalProjection,
    GoalDefinition
)
from services.monte_carlo_engine import MonteCarloEngine
from services.external_data_service import ExternalDataService
from services.financial_config_service import FinancialConfigService
from services.dynamic_financial_service import DynamicFinancialService

logger = logging.getLogger(__name__)

class ScenarioManager:
    """Manages financial scenarios and projections."""
    
    def __init__(self, db_path: str = "scenarios.db"):
        self.db_path = db_path
        self.monte_carlo = MonteCarloEngine()
        self.external_data = ExternalDataService()
        self.financial_config = FinancialConfigService(db_path)
        self.dynamic_financial = DynamicFinancialService()
    
    async def initialize_database(self):
        """Initialize the SQLite database for scenarios."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS scenarios (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    scenario_type TEXT NOT NULL,
                    user_data TEXT NOT NULL,
                    projection_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS projections (
                    id TEXT PRIMARY KEY,
                    scenario_id TEXT NOT NULL,
                    projection_data TEXT NOT NULL,
                    monte_carlo_results TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (scenario_id) REFERENCES scenarios (id)
                )
            """)
            
            # Enhanced table for dynamic scenarios with 6-parameter structure
            await db.execute("""
                CREATE TABLE IF NOT EXISTS dynamic_scenarios (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    location TEXT NOT NULL,
                    spouse1_status TEXT NOT NULL,
                    spouse2_status TEXT NOT NULL,
                    housing TEXT NOT NULL,
                    school_type TEXT NOT NULL,
                    projection_years INTEGER NOT NULL,
                    scenario_data TEXT NOT NULL,
                    projection_results TEXT,
                    status TEXT DEFAULT 'created',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Index for efficient querying by parameters
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_dynamic_scenarios_params 
                ON dynamic_scenarios (location, spouse1_status, spouse2_status, housing, school_type, projection_years)
            """)
            
            await db.commit()
    
    # Dynamic Scenario CRUD Operations
    async def create_dynamic_scenario(self, scenario_params: Dict) -> str:
        """Create a new dynamic scenario with 6 parameters."""
        scenario_id = str(uuid.uuid4())
        
        # Generate scenario name based on parameters
        name = f"{scenario_params['location']} Hav Jason {scenario_params['spouse1Status']} {scenario_params['spouse2Status']} {scenario_params['housing']} {scenario_params['schoolType']} {scenario_params['projectionYears']}yrs"
        
        # Check if scenario already exists
        existing = await self.get_dynamic_scenario_by_params(scenario_params)
        if existing:
            logger.info(f"Dynamic scenario already exists: {name}")
            return existing['id']
        
        scenario_data = {
            'parameters': scenario_params,
            'created_by': 'dynamic_builder',
            'version': '1.0'
        }
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO dynamic_scenarios 
                (id, name, location, spouse1_status, spouse2_status, housing, school_type, projection_years, scenario_data, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scenario_id,
                name,
                scenario_params['location'],
                scenario_params['spouse1Status'],
                scenario_params['spouse2Status'],
                scenario_params['housing'],
                scenario_params['schoolType'],
                scenario_params['projectionYears'],
                json.dumps(scenario_data),
                'created'
            ))
            await db.commit()
        
        logger.info(f"Created dynamic scenario: {name} ({scenario_id})")
        return scenario_id
    
    async def get_dynamic_scenario(self, scenario_id: str) -> Optional[Dict]:
        """Get dynamic scenario by ID with full detail."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT * FROM dynamic_scenarios WHERE id = ?", (scenario_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    scenario_data = json.loads(row[8])
                    projection_results = json.loads(row[9]) if row[9] else None
                    
                    result = {
                        'id': row[0],
                        'name': row[1],
                        'location': row[2],
                        'spouse1_status': row[3],
                        'spouse2_status': row[4],
                        'housing': row[5],
                        'school_type': row[6],
                        'projection_years': row[7],
                        'scenario_data': scenario_data,
                        'projection_results': projection_results,
                        'status': row[10],
                        'created_at': row[11],
                        'updated_at': row[12]
                    }
                    
                    # If scenario has been run, add the detailed financial data at top level for easy access
                    if projection_results and 'detailed_expenses' in projection_results:
                        result['user_data'] = json.dumps({
                            'current_age': projection_results.get('financial_profile', {}).get('current_age', 52),
                            'retirement_age': projection_results.get('financial_profile', {}).get('retirement_age', 65),
                            'annual_salary': projection_results.get('financial_profile', {}).get('annual_salary', 0),
                            'current_city': projection_results.get('financial_profile', {}).get('current_city', ''),
                            'life_expectancy': projection_results.get('financial_profile', {}).get('life_expectancy', 90),
                            'expenses': projection_results.get('detailed_expenses', []),
                            'assets': projection_results.get('assets_detail', []),
                            'income_sources': projection_results.get('income_sources', [])
                        })
                        
                        # Add projection data for compatibility
                        result['projection_data'] = json.dumps({
                            'start_year': 2025,
                            'projection_years': row[7],
                            'assumptions': {
                                'inflation_rate': 0.03,
                                'investment_return': projection_results.get('annual_growth_rate', 0.07),
                                'salary_growth_rate': 0.03,
                                'tax_rate': 0.32
                            }
                        })
                    
                    return result
        return None
    
    async def get_dynamic_scenario_by_params(self, params: Dict) -> Optional[Dict]:
        """Get dynamic scenario by parameter combination."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT * FROM dynamic_scenarios 
                WHERE location = ? AND spouse1_status = ? AND spouse2_status = ? 
                AND housing = ? AND school_type = ? AND projection_years = ?
            """, (
                params['location'],
                params['spouse1Status'],
                params['spouse2Status'],
                params['housing'],
                params['schoolType'],
                params['projectionYears']
            )) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'name': row[1],
                        'location': row[2],
                        'spouse1_status': row[3],
                        'spouse2_status': row[4],
                        'housing': row[5],
                        'school_type': row[6],
                        'projection_years': row[7],
                        'scenario_data': json.loads(row[8]),
                        'projection_results': json.loads(row[9]) if row[9] else None,
                        'status': row[10],
                        'created_at': row[11],
                        'updated_at': row[12]
                    }
        return None
    
    async def update_dynamic_scenario(self, scenario_id: str, updates: Dict) -> bool:
        """Update a dynamic scenario."""
        async with aiosqlite.connect(self.db_path) as db:
            # Get current scenario
            scenario = await self.get_dynamic_scenario(scenario_id)
            if not scenario:
                return False
            
            # Update fields
            set_clauses = []
            values = []
            
            if 'projection_results' in updates:
                set_clauses.append("projection_results = ?")
                values.append(json.dumps(updates['projection_results']))
            
            if 'status' in updates:
                set_clauses.append("status = ?")
                values.append(updates['status'])
            
            if 'scenario_data' in updates:
                set_clauses.append("scenario_data = ?")
                values.append(json.dumps(updates['scenario_data']))
            
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            values.append(scenario_id)
            
            await db.execute(f"""
                UPDATE dynamic_scenarios 
                SET {', '.join(set_clauses)}
                WHERE id = ?
            """, values)
            await db.commit()
        
        return True
    
    async def delete_dynamic_scenario(self, scenario_id: str) -> bool:
        """Delete a dynamic scenario."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM dynamic_scenarios WHERE id = ?", (scenario_id,)
            )
            await db.commit()
            return cursor.rowcount > 0
    
    async def list_dynamic_scenarios(self, limit: int = 50) -> List[Dict]:
        """List all dynamic scenarios."""
        scenarios = []
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT id, name, location, spouse1_status, spouse2_status, housing, 
                       school_type, projection_years, status, created_at, updated_at
                FROM dynamic_scenarios 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,)) as cursor:
                async for row in cursor:
                    scenarios.append({
                        'id': row[0],
                        'name': row[1],
                        'location': row[2],
                        'spouse1_status': row[3],
                        'spouse2_status': row[4],
                        'housing': row[5],
                        'school_type': row[6],
                        'projection_years': row[7],
                        'status': row[8],
                        'created_at': row[9],
                        'updated_at': row[10]
                    })
        return scenarios
    
    async def run_dynamic_scenario(self, scenario_id: str) -> Dict:
        """Run projection for a dynamic scenario."""
        scenario = await self.get_dynamic_scenario(scenario_id)
        if not scenario:
            raise ValueError(f"Dynamic scenario {scenario_id} not found")
        
        # Update status to running
        await self.update_dynamic_scenario(scenario_id, {'status': 'running'})
        
        try:
            # Generate real financial scenario data based on parameters
            parameters = {
                'location': scenario['location'],
                'spouse1Status': scenario['spouse1_status'], 
                'spouse2Status': scenario['spouse2_status'],
                'housing': scenario['housing'],
                'schoolType': scenario['school_type'],
                'projectionYears': scenario['projection_years']
            }
            
            # Generate realistic financial data
            financial_data = self.dynamic_financial.generate_scenario_data(parameters)
            user_profile_data = financial_data['user_data']
            projection_settings_data = financial_data['projection_data']
            
            # Create proper model objects
            user_profile = UserProfile(**user_profile_data)
            projection_settings = ProjectionSettings(**projection_settings_data)
            
            # Run actual financial projections using existing engine
            yearly_projections = await self._calculate_yearly_projections(
                user_profile, projection_settings
            )
            
            # Calculate summary metrics
            final_net_worth = yearly_projections[-1].ending_assets if yearly_projections else 0
            total_expenses = sum(proj.expenses for proj in yearly_projections)
            retirement_readiness = final_net_worth > 800000
            
            # Estimate annual growth rate
            initial_assets = sum(asset.current_value for asset in user_profile.assets)
            annual_growth_rate = 0.07  # Default assumption
            if len(yearly_projections) > 1 and initial_assets > 0:
                annual_growth_rate = (final_net_worth / initial_assets) ** (1 / len(yearly_projections)) - 1
            
            projection_results = {
                'final_net_worth': final_net_worth,
                'annual_growth_rate': annual_growth_rate,
                'total_expenses': total_expenses,
                'retirement_readiness': retirement_readiness,
                'calculated_at': datetime.now().isoformat(),
                'yearly_projections': [
                    {
                        'year': proj.year,
                        'age': proj.age,
                        'net_worth': proj.ending_assets,
                        'income': proj.income,
                        'expenses': proj.expenses,
                        'net_cash_flow': proj.net_cash_flow
                    } for proj in yearly_projections[:5]  # Store first 5 years for preview
                ],
                # Include detailed expense breakdown from generated data
                'detailed_expenses': user_profile_data.get('expenses', []),
                'assets_detail': user_profile_data.get('assets', []),
                'income_sources': user_profile_data.get('income_sources', []),
                'financial_profile': {
                    'current_age': user_profile_data.get('current_age', 52),
                    'retirement_age': user_profile_data.get('retirement_age', 65),
                    'annual_salary': user_profile_data.get('annual_salary', 0),
                    'current_city': user_profile_data.get('current_city', ''),
                    'life_expectancy': user_profile_data.get('life_expectancy', 90)
                }
            }
            
            # Save results
            await self.update_dynamic_scenario(scenario_id, {
                'projection_results': projection_results,
                'status': 'completed'
            })
            
            return projection_results
            
        except Exception as e:
            logger.error(f"Failed to run dynamic scenario {scenario_id}: {e}")
            await self.update_dynamic_scenario(scenario_id, {'status': 'failed'})
            raise
    
    async def compare_dynamic_scenarios(self, scenario_ids: List[str]) -> Dict:
        """Compare multiple dynamic scenarios."""
        scenarios = []
        
        for scenario_id in scenario_ids:
            scenario = await self.get_dynamic_scenario(scenario_id)
            if scenario:
                # Ensure projection results exist
                if not scenario['projection_results']:
                    await self.run_dynamic_scenario(scenario_id)
                    scenario = await self.get_dynamic_scenario(scenario_id)
                scenarios.append(scenario)
        
        if not scenarios:
            return {'error': 'No valid scenarios found for comparison'}
        
        # Generate comparison metrics
        comparison = {
            'scenarios': scenarios,
            'comparison_timestamp': datetime.now().isoformat(),
            'metrics': {
                'net_worth_projections': {},
                'key_differences': [],
                'recommendations': []
            }
        }
        
        # Calculate relative performance
        net_worths = []
        for scenario in scenarios:
            if scenario['projection_results']:
                net_worth = scenario['projection_results']['final_net_worth']
                net_worths.append(net_worth)
                comparison['metrics']['net_worth_projections'][scenario['name']] = {
                    'final_net_worth': net_worth,
                    'growth_rate': scenario['projection_results'].get('annual_growth_rate', 0.07),
                    'key_factors': [
                        f"Location: {scenario['location']}",
                        f"Housing: {scenario['housing']}",
                        f"Education: {scenario['school_type']}"
                    ]
                }
        
        # Add recommendations
        if net_worths:
            best_net_worth = max(net_worths)
            best_scenario = next(s for s in scenarios 
                               if s['projection_results'] and 
                               s['projection_results']['final_net_worth'] == best_net_worth)
            
            comparison['metrics']['recommendations'] = [
                f"Best performing scenario: {best_scenario['name']}",
                f"Optimal location appears to be: {best_scenario['location']}",
                "Consider the trade-offs between financial outcomes and quality of life"
            ]
        
        return comparison
    
    async def create_scenario(self, scenario_input: ScenarioInput) -> str:
        """Create a new financial scenario."""
        scenario_id = str(uuid.uuid4())
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO scenarios (id, name, scenario_type, user_data, projection_data)
                VALUES (?, ?, ?, ?, ?)
            """, (
                scenario_id,
                scenario_input.name,
                scenario_input.scenario_type.value,
                scenario_input.user_profile.json(),
                scenario_input.projection_settings.json()
            ))
            await db.commit()
        
        logger.info(f"Created scenario: {scenario_input.name} ({scenario_id})")
        return scenario_id
    
    async def run_projection(
        self, 
        scenario_id: str, 
        include_monte_carlo: bool = False,
        projection_mode: str = "years",
        projection_value: int = None,
        progress_callback: Optional[callable] = None
    ) -> ScenarioProjection:
        """Run financial projection for a scenario."""
        
        # Load scenario data
        scenario_data = await self.get_scenario(scenario_id)
        if not scenario_data:
            raise ValueError(f"Scenario {scenario_id} not found")
        
        user_profile = UserProfile.parse_raw(scenario_data['user_data'])
        projection_settings = ProjectionSettings.parse_raw(scenario_data['projection_data'])
        
        # Calculate projection years based on mode
        if projection_mode == "retirement":
            if projection_value is None:
                projection_value = user_profile.retirement_age
            projection_years = max(1, projection_value - user_profile.current_age)
        elif projection_mode == "years":
            if projection_value is None:
                projection_value = projection_settings.projection_years
            projection_years = projection_value
        else:
            # Default to original projection settings
            projection_years = projection_settings.projection_years
        
        # Update projection settings with calculated years
        projection_settings.projection_years = projection_years
        
        # Run deterministic projection
        yearly_projections = await self._calculate_yearly_projections(
            user_profile, projection_settings
        )
        
        # Run Monte Carlo simulation if requested
        monte_carlo_results = None
        if include_monte_carlo:
            if progress_callback:
                await progress_callback(0.5, "Running Monte Carlo simulation...")
            
            monte_carlo_results = await self.monte_carlo.run_simulation(
                user_profile, projection_settings, progress_callback
            )
        
        # Calculate summary metrics
        final_net_worth = yearly_projections[-1].ending_assets if yearly_projections else 0
        retirement_expenses = sum(exp.annual_amount for exp in user_profile.expenses)
        retirement_income_replacement = (final_net_worth * 0.04) / retirement_expenses if retirement_expenses > 0 else 0
        years_covered = final_net_worth / retirement_expenses if retirement_expenses > 0 else 0
        is_achievable = retirement_income_replacement >= 0.8  # 80% replacement ratio
        
        projection = ScenarioProjection(
            scenario_id=scenario_id,
            scenario_name=scenario_data['name'],
            yearly_projections=yearly_projections,
            monte_carlo_results=monte_carlo_results,
            final_net_worth=final_net_worth,
            retirement_income_replacement=retirement_income_replacement,
            years_of_expenses_covered=years_covered,
            is_goal_achievable=is_achievable,
            assumptions_used=projection_settings.assumptions
        )
        
        # Save projection results
        await self._save_projection(projection)
        
        if progress_callback:
            await progress_callback(1.0, "Projection completed")
        
        return projection
    
    async def _calculate_yearly_projections(
        self,
        user_profile: UserProfile,
        projection_settings: ProjectionSettings
    ) -> List[ProjectionYear]:
        """Calculate deterministic yearly projections."""
        
        projections = []
        current_assets = sum(asset.current_value for asset in user_profile.assets)
        current_age = user_profile.current_age
        
        assumptions = projection_settings.assumptions
        
        for year in range(projection_settings.projection_years):
            age = current_age + year
            
            # Calculate income
            if age < user_profile.retirement_age:
                # Working years
                annual_income = user_profile.annual_salary * (
                    (1 + assumptions.salary_growth_rate) ** year
                )
                # Add other income sources
                for income_source in user_profile.income_sources:
                    if income_source.start_age <= age <= (income_source.end_age or 120):
                        annual_income += income_source.annual_amount * (
                            (1 + income_source.growth_rate) ** (age - income_source.start_age)
                        )
            else:
                # Retirement years - Social Security and pensions
                annual_income = 0
                for income_source in user_profile.income_sources:
                    if income_source.start_age <= age <= (income_source.end_age or 120):
                        annual_income += income_source.annual_amount * (
                            (1 + income_source.growth_rate) ** (age - income_source.start_age)
                        )
            
            # Calculate expenses
            annual_expenses = 0
            for expense in user_profile.expenses:
                if expense.start_age <= age <= (expense.end_age or 120):
                    if expense.inflation_adjusted:
                        expense_amount = expense.annual_amount * (
                            (1 + assumptions.inflation_rate) ** year
                        )
                    else:
                        expense_amount = expense.annual_amount
                    annual_expenses += expense_amount
            
            # Calculate taxes (simplified)
            tax_liability = 0
            if annual_income > 0:
                tax_liability = annual_income * assumptions.tax_rate
                annual_income -= tax_liability
            
            # Net cash flow
            net_cash_flow = annual_income - annual_expenses
            
            # Update assets
            beginning_assets = current_assets
            
            if age >= user_profile.retirement_age and net_cash_flow < 0:
                # Retirement withdrawals
                current_assets += net_cash_flow  # net_cash_flow is negative
            else:
                # Accumulation phase
                current_assets += net_cash_flow
            
            # Apply investment returns
            current_assets *= (1 + assumptions.investment_return)
            
            # Ensure non-negative assets
            current_assets = max(0, current_assets)
            
            projection_year = ProjectionYear(
                year=projection_settings.start_year + year,
                age=age,
                beginning_assets=beginning_assets,
                income=annual_income,
                expenses=annual_expenses,
                net_cash_flow=net_cash_flow,
                ending_assets=current_assets,
                tax_liability=tax_liability
            )
            
            projections.append(projection_year)
        
        return projections
    
    async def compare_scenarios(self, scenario_ids: List[str]) -> Dict[str, ScenarioProjection]:
        """Compare multiple scenarios."""
        results = {}
        
        for scenario_id in scenario_ids:
            projection = await self.run_projection(scenario_id, include_monte_carlo=False)
            results[scenario_id] = projection
        
        return results
    
    async def analyze_city_relocation(
        self,
        current_city: str,
        target_city: str,
        user_profile: UserProfile
    ) -> CityComparison:
        """Analyze financial impact of city relocation."""
        
        # Fetch cost of living data
        current_city_data = await self.external_data.get_city_cost_data(current_city)
        target_city_data = await self.external_data.get_city_cost_data(target_city)
        
        # Calculate annual cost difference
        annual_cost_diff = (target_city_data.cost_index - current_city_data.cost_index) * user_profile.annual_salary * 0.3
        
        # Project long-term impact
        years_to_retirement = user_profile.retirement_age - user_profile.current_age
        net_worth_impact_10_year = annual_cost_diff * 10 * 1.07**5  # Assume 7% investment return
        net_worth_impact_retirement = annual_cost_diff * years_to_retirement * 1.07**(years_to_retirement/2)
        
        return CityComparison(
            current_city=current_city_data,
            target_city=target_city_data,
            annual_cost_difference=annual_cost_diff,
            net_worth_impact_10_year=net_worth_impact_10_year,
            net_worth_impact_retirement=net_worth_impact_retirement
        )
    
    async def project_education_expenses(
        self,
        institution_type: str,
        start_year: int,
        duration_years: int,
        current_child_age: int
    ) -> EducationExpenseProjection:
        """Project education expenses."""
        
        # Base costs by institution type
        base_costs = {
            "private_k12": 25000,
            "public_college": 28000,
            "private_college": 58000
        }
        
        annual_cost = base_costs.get(institution_type, 30000)
        inflation_rate = 0.05  # Education inflation typically higher
        
        years_until_start = start_year - datetime.now().year
        
        # Calculate future value with education inflation
        total_cost_future = 0
        for year in range(duration_years):
            year_cost = annual_cost * ((1 + inflation_rate) ** (years_until_start + year))
            total_cost_future += year_cost
        
        # Present value
        total_cost_present = total_cost_future / ((1 + 0.07) ** years_until_start)
        
        # Required monthly savings
        months_to_save = years_until_start * 12
        monthly_rate = 0.07 / 12
        
        if months_to_save > 0:
            # PMT calculation for annuity
            monthly_savings = total_cost_present * (monthly_rate * (1 + monthly_rate)**months_to_save) / ((1 + monthly_rate)**months_to_save - 1)
        else:
            monthly_savings = total_cost_present / 12  # If starting immediately
        
        return EducationExpenseProjection(
            institution_type=institution_type,
            annual_cost=annual_cost,
            duration_years=duration_years,
            inflation_rate=inflation_rate,
            total_cost_present_value=total_cost_present,
            total_cost_future_value=total_cost_future,
            monthly_savings_required=monthly_savings
        )
    
    async def analyze_vehicle_ownership(
        self,
        vehicle_type: str,
        ownership_years: int,
        annual_mileage: int = 12000
    ) -> VehicleOwnershipProjection:
        """Analyze total cost of vehicle ownership."""
        
        # Base data by vehicle type
        vehicle_data = {
            "economy": {"price": 25000, "mpg": 30, "insurance": 1200, "maintenance": 800},
            "midsize": {"price": 35000, "mpg": 25, "insurance": 1400, "maintenance": 1000},
            "luxury": {"price": 55000, "mpg": 22, "insurance": 2000, "maintenance": 1500},
            "electric": {"price": 45000, "mpg": 100, "insurance": 1300, "maintenance": 600}  # MPGe for electric
        }
        
        data = vehicle_data.get(vehicle_type, vehicle_data["midsize"])
        
        purchase_price = data["price"]
        
        # Financing cost (assuming 5% APR, 60 months, 20% down)
        loan_amount = purchase_price * 0.8
        monthly_payment = loan_amount * (0.05/12) / (1 - (1 + 0.05/12)**(-60))
        total_financing_cost = monthly_payment * 60 - loan_amount
        
        # Annual costs
        insurance_annual = data["insurance"]
        maintenance_annual = data["maintenance"]
        
        # Fuel costs
        if vehicle_type == "electric":
            # Electric: ~$0.12/kWh, ~3.5 miles/kWh
            fuel_annual = (annual_mileage / 3.5) * 0.12
        else:
            # Gas: assume $3.50/gallon
            fuel_annual = (annual_mileage / data["mpg"]) * 3.5
        
        # Depreciation (simplified)
        depreciation_rate = 0.15  # 15% per year average
        residual_value = purchase_price * ((1 - depreciation_rate) ** ownership_years)
        total_depreciation = purchase_price - residual_value
        
        # Total cost of ownership
        total_annual_costs = insurance_annual + maintenance_annual + fuel_annual
        total_cost = purchase_price + total_financing_cost + (total_annual_costs * ownership_years) - residual_value
        
        return VehicleOwnershipProjection(
            vehicle_type=vehicle_type,
            purchase_price=purchase_price,
            financing_cost=total_financing_cost,
            insurance_annual=insurance_annual,
            fuel_annual=fuel_annual,
            maintenance_annual=maintenance_annual,
            depreciation_total=total_depreciation,
            total_cost_ownership=total_cost
        )
    
    async def analyze_financial_goals(
        self,
        goals: List[GoalDefinition],
        user_profile: UserProfile
    ) -> List[GoalProjection]:
        """Analyze financial goal feasibility."""
        
        projections = []
        
        for goal in goals:
            # Calculate required monthly contribution
            months_to_goal = (goal.target_date - date.today()).days / 30.44
            monthly_rate = goal.expected_return / 12
            
            if months_to_goal > 0:
                # Future value of current amount
                fv_current = goal.current_amount * ((1 + monthly_rate) ** months_to_goal)
                
                # Required future value from contributions
                fv_needed = goal.target_amount - fv_current
                
                # Required monthly contribution
                if fv_needed > 0:
                    required_monthly = fv_needed * monthly_rate / ((1 + monthly_rate) ** months_to_goal - 1)
                else:
                    required_monthly = 0
                
                # Projected final amount with current contribution
                fv_contributions = goal.monthly_contribution * (((1 + monthly_rate) ** months_to_goal - 1) / monthly_rate)
                projected_final = fv_current + fv_contributions
                
                shortfall = max(0, goal.target_amount - projected_final)
                success_probability = min(1.0, projected_final / goal.target_amount)
                
            else:
                required_monthly = goal.target_amount - goal.current_amount
                projected_final = goal.current_amount
                shortfall = goal.target_amount - goal.current_amount
                success_probability = 0.0 if shortfall > 0 else 1.0
            
            # Generate recommendations
            recommendations = []
            if shortfall > 0:
                recommendations.append(f"Increase monthly contribution by ${(required_monthly - goal.monthly_contribution):.2f}")
                recommendations.append(f"Consider extending timeline by 2-3 years")
                recommendations.append(f"Look for higher-yield investment options")
            
            projection = GoalProjection(
                goal=goal,
                projected_final_amount=projected_final,
                shortfall_amount=shortfall,
                probability_of_success=success_probability,
                required_monthly_contribution=required_monthly,
                recommended_adjustments=recommendations
            )
            
            projections.append(projection)
        
        return projections
    
    async def get_scenario(self, scenario_id: str) -> Optional[Dict]:
        """Get scenario data by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT * FROM scenarios WHERE id = ?", (scenario_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'name': row[1],
                        'scenario_type': row[2],
                        'user_data': row[3],
                        'projection_data': row[4],
                        'created_at': row[5],
                        'updated_at': row[6]
                    }
        return None
    
    async def list_scenarios(self) -> List[Dict]:
        """List all scenarios."""
        scenarios = []
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM scenarios ORDER BY created_at DESC") as cursor:
                async for row in cursor:
                    scenarios.append({
                        'id': row[0],
                        'name': row[1],
                        'scenario_type': row[2],
                        'created_at': row[5]
                    })
        return scenarios
    
    async def get_all_scenarios(self) -> List[Dict]:
        """Get all scenarios with full data for export."""
        scenarios = []
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM scenarios ORDER BY created_at DESC") as cursor:
                async for row in cursor:
                    scenarios.append({
                        'id': row[0],
                        'name': row[1],
                        'scenario_type': row[2],
                        'user_data': json.loads(row[3]),
                        'projection_data': json.loads(row[4]),
                        'created_at': row[5],
                        'updated_at': row[6]
                    })
        return scenarios
    
    async def _save_projection(self, projection: ScenarioProjection):
        """Save projection results to database."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO projections 
                (id, scenario_id, projection_data, monte_carlo_results)
                VALUES (?, ?, ?, ?)
            """, (
                f"{projection.scenario_id}_projection",
                projection.scenario_id,
                projection.json(),
                projection.monte_carlo_results.json() if projection.monte_carlo_results else None
            ))
            await db.commit()