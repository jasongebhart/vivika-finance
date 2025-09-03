"""
Service for managing financial configuration data from database.
"""

import json
import aiosqlite
import logging
from typing import Dict, List, Optional, Any
from models.config_models import (
    FinancialConfiguration, 
    UserProfile, 
    HousingDetails,
    TaxRates,
    FinancialAssumptions,
    HouseData,
    Investment,
    PersonRetirement,
    RetirementAccount,
    EducationVariant
)

logger = logging.getLogger(__name__)

class FinancialConfigService:
    """Service for managing financial configuration data."""
    
    def __init__(self, db_path: str = "scenarios.db"):
        self.db_path = db_path
    
    async def get_financial_config(self, config_name: str = "default") -> Optional[Dict[str, Any]]:
        """Get complete financial configuration by name."""
        async with aiosqlite.connect(self.db_path) as db:
            # Get config ID
            cursor = await db.execute(
                "SELECT id FROM financial_config WHERE config_name = ?",
                (config_name,)
            )
            row = await cursor.fetchone()
            if not row:
                logger.warning(f"Financial config '{config_name}' not found")
                return None
            
            config_id = row[0]
            
            # Build complete configuration
            config = {
                "config_id": config_id,
                "config_name": config_name
            }
            
            # Get user profile
            user_profile = await self._get_user_profile(db, config_id)
            if user_profile:
                config.update(user_profile)
            
            # Get housing details
            housing_details = await self._get_housing_details(db, config_id)
            if housing_details:
                config["HOUSING_DETAILS"] = housing_details
            
            # Get tax rates
            tax_rates = await self._get_tax_rates(db, config_id)
            if tax_rates:
                config["TAX_RATES"] = tax_rates
            
            # Get financial assumptions
            assumptions = await self._get_financial_assumptions(db, config_id)
            if assumptions:
                config["FINANCIAL_ASSUMPTIONS"] = assumptions
            
            # Get expense categories
            expense_categories = await self._get_expense_categories(db, config_id)
            config.update(expense_categories)
            
            # Get spouse variants
            spouse_variants = await self._get_spouse_variants(db, config_id)
            config.update(spouse_variants)
            
            # Get retirement accounts
            retirement_data = await self._get_retirement_accounts(db, config_id)
            if retirement_data:
                config["RETIREMENT"] = retirement_data
            
            # Get investments
            investments = await self._get_investments(db, config_id)
            if investments:
                config["INVESTMENTS"] = investments
            
            # Get education scenarios
            education_scenarios = await self._get_education_scenarios(db, config_id)
            if education_scenarios:
                config["children_variants"] = education_scenarios
            
            # Get house data
            houses = await self._get_houses(db, config_id)
            config.update(houses)
            
            return config
    
    async def _get_user_profile(self, db: aiosqlite.Connection, config_id: int) -> Optional[Dict[str, str]]:
        """Get user profile data."""
        cursor = await db.execute(
            "SELECT parent_one, parent_two FROM user_profiles WHERE config_id = ?",
            (config_id,)
        )
        row = await cursor.fetchone()
        if row:
            return {
                "parent_one": row[0],
                "parent_two": row[1]
            }
        return None
    
    async def _get_housing_details(self, db: aiosqlite.Connection, config_id: int) -> Optional[Dict[str, Any]]:
        """Get housing details."""
        cursor = await db.execute(
            "SELECT include_new_house, home_tenure, residence_location FROM housing_details WHERE config_id = ?",
            (config_id,)
        )
        row = await cursor.fetchone()
        if row:
            return {
                "include_new_house": bool(row[0]),
                "home_tenure": row[1],
                "residence_location": row[2]
            }
        return None
    
    async def _get_tax_rates(self, db: aiosqlite.Connection, config_id: int) -> Optional[Dict[str, float]]:
        """Get tax rates."""
        cursor = await db.execute(
            "SELECT assumed, federal_single, state_single, federal_dual, state_dual FROM tax_rates WHERE config_id = ?",
            (config_id,)
        )
        row = await cursor.fetchone()
        if row:
            return {
                "assumed": row[0],
                "federal_single": row[1],
                "state_single": row[2],
                "federal_dual": row[3],
                "state_dual": row[4]
            }
        return None
    
    async def _get_financial_assumptions(self, db: aiosqlite.Connection, config_id: int) -> Optional[Dict[str, Any]]:
        """Get financial assumptions."""
        cursor = await db.execute(
            "SELECT assumption_description, interest_rate, years FROM financial_assumptions WHERE config_id = ?",
            (config_id,)
        )
        row = await cursor.fetchone()
        if row:
            return {
                "assumption_description": row[0],
                "interest_rate": row[1],
                "years": row[2]
            }
        return None
    
    async def _get_expense_categories(self, db: aiosqlite.Connection, config_id: int) -> Dict[str, Any]:
        """Get all expense categories."""
        cursor = await db.execute(
            "SELECT category_name, category_data FROM expense_categories WHERE config_id = ?",
            (config_id,)
        )
        categories = {}
        async for row in cursor:
            category_name = row[0]
            category_data = json.loads(row[1])
            categories[category_name] = category_data
        return categories
    
    async def _get_spouse_variants(self, db: aiosqlite.Connection, config_id: int) -> Dict[str, Dict[str, Any]]:
        """Get spouse income variants."""
        cursor = await db.execute(
            """SELECT spouse_number, variant_name, base_income, bonus_income, quarterly_income,
                      pretax_retirement, pretax_hsa, pretax_serplus, posttax_retirement, posttax_espp 
               FROM spouse_variants WHERE config_id = ?""",
            (config_id,)
        )
        
        spouse1_variants = {}
        spouse2_variants = {}
        
        async for row in cursor:
            spouse_num = row[0]
            variant_name = row[1]
            variant_data = {
                "yearly_income": {
                    "base": row[2],
                    "bonus": row[3],
                    "quarterly": row[4]
                },
                "pretax_investments": {
                    "retirement_contribution": row[5],
                    "hsa": row[6],
                    "serplus": row[7]
                },
                "posttax_investments": {
                    "retirement_contribution": row[8],
                    "employee_stock_purchase_plan": row[9]
                }
            }
            
            if spouse_num == 1:
                spouse1_variants[variant_name] = variant_data
            else:
                spouse2_variants[variant_name] = variant_data
        
        return {
            "spouse1_variants": spouse1_variants,
            "spouse2_variants": spouse2_variants
        }
    
    async def _get_retirement_accounts(self, db: aiosqlite.Connection, config_id: int) -> List[Dict[str, Any]]:
        """Get retirement account data."""
        cursor = await db.execute(
            "SELECT person_name, account_type, account_name, amount FROM retirement_accounts WHERE config_id = ?",
            (config_id,)
        )
        
        # Group accounts by person
        people = {}
        async for row in cursor:
            person_name = row[0]
            account_type = row[1]
            account_name = row[2]
            amount = row[3]
            
            if person_name not in people:
                people[person_name] = {
                    "name": person_name,
                    "accounts": {
                        "Roth": [],
                        "IRA": [],
                        "401K": []
                    }
                }
            
            people[person_name]["accounts"][account_type].append({account_name: amount})
        
        return list(people.values())
    
    async def _get_investments(self, db: aiosqlite.Connection, config_id: int) -> Dict[str, Dict[str, Any]]:
        """Get investment data."""
        cursor = await db.execute(
            "SELECT investment_key, name, type, amount FROM investments WHERE config_id = ?",
            (config_id,)
        )
        
        investments = {}
        async for row in cursor:
            investments[row[0]] = {
                "name": row[1],
                "type": row[2],
                "amount": row[3]
            }
        
        return investments
    
    async def _get_education_scenarios(self, db: aiosqlite.Connection, config_id: int) -> Dict[str, Any]:
        """Get education scenarios."""
        cursor = await db.execute(
            "SELECT scenario_name, scenario_type, scenario_data FROM education_scenarios WHERE config_id = ?",
            (config_id,)
        )
        
        scenarios = {}
        async for row in cursor:
            scenarios[row[0]] = json.loads(row[2])
        
        return scenarios
    
    async def _get_houses(self, db: aiosqlite.Connection, config_id: int) -> Dict[str, Dict[str, Any]]:
        """Get house data."""
        cursor = await db.execute(
            """SELECT house_type, description, cost_basis, closing_costs, home_improvement,
                      value, mortgage_principal, commission_rate, annual_growth_rate,
                      interest_rate, monthly_payment, payments_made, number_of_payments,
                      annual_property_tax, sell_house 
               FROM houses WHERE config_id = ?""",
            (config_id,)
        )
        
        houses = {}
        async for row in cursor:
            house_type = row[0]
            houses[house_type] = {
                "description": row[1],
                "cost_basis": row[2],
                "closing_costs": row[3],
                "home_improvement": row[4],
                "value": row[5],
                "mortgage_principal": row[6],
                "commission_rate": row[7],
                "annual_growth_rate": row[8],
                "interest_rate": row[9],
                "monthly_payment": row[10],
                "payments_made": row[11],
                "number_of_payments": row[12],
                "annual_property_tax": row[13],
                "sell_house": bool(row[14])
            }
        
        return houses
    
    async def get_house_data(self, config_name: str = "default") -> Optional[Dict[str, Any]]:
        """Get just the house data for quick access."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """SELECT h.house_type, h.description, h.cost_basis, h.closing_costs, h.home_improvement,
                          h.value, h.mortgage_principal, h.commission_rate, h.annual_growth_rate,
                          h.interest_rate, h.monthly_payment, h.payments_made, h.number_of_payments,
                          h.annual_property_tax, h.sell_house 
                   FROM houses h
                   JOIN financial_config fc ON h.config_id = fc.id
                   WHERE fc.config_name = ?""",
                (config_name,)
            )
            
            houses = {}
            async for row in cursor:
                house_type = row[0]
                houses[house_type] = {
                    "description": row[1],
                    "cost_basis": row[2],
                    "closing_costs": row[3],
                    "home_improvement": row[4],
                    "value": row[5],
                    "mortgage_principal": row[6],
                    "commission_rate": row[7],
                    "annual_growth_rate": row[8],
                    "interest_rate": row[9],
                    "monthly_payment": row[10],
                    "payments_made": row[11],
                    "number_of_payments": row[12],
                    "annual_property_tax": row[13],
                    "sell_house": bool(row[14])
                }
            
            return houses if houses else None

    async def update_house_data(self, config_name: str, house_updates: Dict[str, Any]) -> int:
        """Update house data in the database."""
        async with aiosqlite.connect(self.db_path) as db:
            updated_count = 0
            
            # Get config ID
            cursor = await db.execute(
                "SELECT id FROM financial_config WHERE config_name = ?",
                (config_name,)
            )
            row = await cursor.fetchone()
            if not row:
                return 0
            
            config_id = row[0]
            
            # Update each house type provided
            for house_type, house_data in house_updates.items():
                if house_type in ['house', 'new_house']:
                    # Build dynamic UPDATE query based on provided fields
                    update_fields = []
                    update_values = []
                    
                    for field, value in house_data.items():
                        if field in ['description', 'cost_basis', 'closing_costs', 'home_improvement',
                                   'value', 'mortgage_principal', 'commission_rate', 'annual_growth_rate',
                                   'interest_rate', 'monthly_payment', 'payments_made', 'number_of_payments',
                                   'annual_property_tax', 'sell_house']:
                            update_fields.append(f"{field} = ?")
                            update_values.append(value)
                    
                    if update_fields:
                        update_values.extend([config_id, house_type])
                        query = f"""
                            UPDATE houses 
                            SET {', '.join(update_fields)}, updated_at = datetime('now')
                            WHERE config_id = ? AND house_type = ?
                        """
                        
                        cursor = await db.execute(query, update_values)
                        updated_count += cursor.rowcount
            
            await db.commit()
            return updated_count

    async def update_expense_category(self, config_name: str, category_name: str, category_data: Dict[str, Any]) -> int:
        """Update an expense category in the database."""
        async with aiosqlite.connect(self.db_path) as db:
            # Get config ID
            cursor = await db.execute(
                "SELECT id FROM financial_config WHERE config_name = ?",
                (config_name,)
            )
            row = await cursor.fetchone()
            if not row:
                return 0
            
            config_id = row[0]
            
            # Update the expense category
            cursor = await db.execute(
                """UPDATE expense_categories 
                   SET category_data = ?
                   WHERE config_id = ? AND category_name = ?""",
                (json.dumps(category_data), config_id, category_name)
            )
            
            await db.commit()
            return cursor.rowcount

    async def update_tax_rates(self, config_name: str, tax_rates: Dict[str, float]) -> int:
        """Update tax rates in the database."""
        async with aiosqlite.connect(self.db_path) as db:
            # Get config ID
            cursor = await db.execute(
                "SELECT id FROM financial_config WHERE config_name = ?",
                (config_name,)
            )
            row = await cursor.fetchone()
            if not row:
                return 0
            
            config_id = row[0]
            
            # Build dynamic UPDATE query
            update_fields = []
            update_values = []
            
            for field, value in tax_rates.items():
                if field in ['assumed', 'federal_single', 'state_single', 'federal_dual', 'state_dual']:
                    update_fields.append(f"{field} = ?")
                    update_values.append(value)
            
            if not update_fields:
                return 0
            
            update_values.append(config_id)
            query = f"UPDATE tax_rates SET {', '.join(update_fields)} WHERE config_id = ?"
            
            cursor = await db.execute(query, update_values)
            await db.commit()
            return cursor.rowcount

    async def restore_config(self, config_name: str, config_data: Dict[str, Any]) -> int:
        """Restore a complete configuration from backup data."""
        # This is a complex operation that would recreate all the configuration data
        # For now, we'll implement a simplified version that updates the existing config
        async with aiosqlite.connect(self.db_path) as db:
            # Check if config exists
            cursor = await db.execute(
                "SELECT id FROM financial_config WHERE config_name = ?",
                (config_name,)
            )
            row = await cursor.fetchone()
            
            if row:
                config_id = row[0]
                # Update existing config timestamp
                await db.execute(
                    "UPDATE financial_config SET updated_at = datetime('now') WHERE id = ?",
                    (config_id,)
                )
            else:
                # Create new config
                cursor = await db.execute(
                    "INSERT INTO financial_config (config_name) VALUES (?)",
                    (config_name,)
                )
                config_id = cursor.lastrowid
            
            await db.commit()
            logger.info(f"Restored/created config '{config_name}' with ID {config_id}")
            return config_id