"""
Migration: Move general.finance.json data to database tables.

This migration creates the necessary database tables and migrates
data from the JSON configuration file to a normalized database structure.
"""

import asyncio
import json
import aiosqlite
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Database schema for financial configuration
FINANCIAL_CONFIG_TABLES = {
    'financial_config': '''
        CREATE TABLE IF NOT EXISTS financial_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_name TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''',
    
    'user_profiles': '''
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_id INTEGER NOT NULL,
            parent_one TEXT NOT NULL,
            parent_two TEXT NOT NULL,
            FOREIGN KEY (config_id) REFERENCES financial_config (id)
        )
    ''',
    
    'housing_details': '''
        CREATE TABLE IF NOT EXISTS housing_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_id INTEGER NOT NULL,
            include_new_house BOOLEAN NOT NULL,
            home_tenure TEXT NOT NULL,
            residence_location TEXT NOT NULL,
            FOREIGN KEY (config_id) REFERENCES financial_config (id)
        )
    ''',
    
    'tax_rates': '''
        CREATE TABLE IF NOT EXISTS tax_rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_id INTEGER NOT NULL,
            assumed REAL NOT NULL,
            federal_single REAL NOT NULL,
            state_single REAL NOT NULL,
            federal_dual REAL NOT NULL,
            state_dual REAL NOT NULL,
            FOREIGN KEY (config_id) REFERENCES financial_config (id)
        )
    ''',
    
    'financial_assumptions': '''
        CREATE TABLE IF NOT EXISTS financial_assumptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_id INTEGER NOT NULL,
            assumption_description TEXT,
            interest_rate REAL NOT NULL,
            years INTEGER NOT NULL,
            FOREIGN KEY (config_id) REFERENCES financial_config (id)
        )
    ''',
    
    'expense_categories': '''
        CREATE TABLE IF NOT EXISTS expense_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_id INTEGER NOT NULL,
            category_name TEXT NOT NULL,
            category_data TEXT NOT NULL, -- JSON blob for complex nested data
            FOREIGN KEY (config_id) REFERENCES financial_config (id)
        )
    ''',
    
    'spouse_variants': '''
        CREATE TABLE IF NOT EXISTS spouse_variants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_id INTEGER NOT NULL,
            spouse_number INTEGER NOT NULL, -- 1 or 2
            variant_name TEXT NOT NULL,
            base_income REAL NOT NULL,
            bonus_income REAL NOT NULL,
            quarterly_income REAL NOT NULL,
            pretax_retirement REAL NOT NULL,
            pretax_hsa REAL NOT NULL,
            pretax_serplus REAL NOT NULL,
            posttax_retirement REAL NOT NULL,
            posttax_espp REAL NOT NULL,
            FOREIGN KEY (config_id) REFERENCES financial_config (id)
        )
    ''',
    
    'retirement_accounts': '''
        CREATE TABLE IF NOT EXISTS retirement_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_id INTEGER NOT NULL,
            person_name TEXT NOT NULL,
            account_type TEXT NOT NULL, -- 'Roth', 'IRA', '401K'
            account_name TEXT NOT NULL,
            amount REAL NOT NULL,
            FOREIGN KEY (config_id) REFERENCES financial_config (id)
        )
    ''',
    
    'investments': '''
        CREATE TABLE IF NOT EXISTS investments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_id INTEGER NOT NULL,
            investment_key TEXT NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            FOREIGN KEY (config_id) REFERENCES financial_config (id)
        )
    ''',
    
    'education_scenarios': '''
        CREATE TABLE IF NOT EXISTS education_scenarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_id INTEGER NOT NULL,
            scenario_name TEXT NOT NULL,
            scenario_type TEXT NOT NULL,
            scenario_data TEXT NOT NULL, -- JSON blob for complex nested data
            FOREIGN KEY (config_id) REFERENCES financial_config (id)
        )
    ''',
    
    'houses': '''
        CREATE TABLE IF NOT EXISTS houses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_id INTEGER NOT NULL,
            house_type TEXT NOT NULL, -- 'house' or 'new_house'
            description TEXT NOT NULL,
            cost_basis REAL NOT NULL,
            closing_costs REAL DEFAULT 0,
            home_improvement REAL DEFAULT 0,
            value REAL NOT NULL,
            mortgage_principal REAL NOT NULL,
            commission_rate REAL NOT NULL,
            annual_growth_rate REAL NOT NULL,
            interest_rate REAL NOT NULL,
            monthly_payment REAL NOT NULL,
            payments_made INTEGER NOT NULL,
            number_of_payments INTEGER NOT NULL,
            annual_property_tax REAL NOT NULL,
            sell_house BOOLEAN DEFAULT 0,
            FOREIGN KEY (config_id) REFERENCES financial_config (id)
        )
    '''
}

async def create_financial_config_tables(db_path: str):
    """Create all financial configuration tables."""
    async with aiosqlite.connect(db_path) as db:
        for table_name, schema in FINANCIAL_CONFIG_TABLES.items():
            logger.info(f"Creating table: {table_name}")
            await db.execute(schema)
        await db.commit()
        logger.info("All financial configuration tables created successfully")

async def migrate_json_to_database(json_file_path: str, db_path: str, config_name: str = "default"):
    """Migrate data from general.finance.json to database tables."""
    
    # Load JSON data
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    async with aiosqlite.connect(db_path) as db:
        # Insert main config record
        cursor = await db.execute(
            "INSERT INTO financial_config (config_name) VALUES (?)",
            (config_name,)
        )
        config_id = cursor.lastrowid
        logger.info(f"Created financial config with ID: {config_id}")
        
        # Migrate user profile
        await db.execute(
            "INSERT INTO user_profiles (config_id, parent_one, parent_two) VALUES (?, ?, ?)",
            (config_id, data["parent_one"], data["parent_two"])
        )
        
        # Migrate housing details
        housing = data["HOUSING_DETAILS"]
        await db.execute(
            """INSERT INTO housing_details 
               (config_id, include_new_house, home_tenure, residence_location) 
               VALUES (?, ?, ?, ?)""",
            (config_id, housing["include_new_house"], housing["home_tenure"], housing["residence_location"])
        )
        
        # Migrate tax rates
        tax_rates = data["TAX_RATES"]
        await db.execute(
            """INSERT INTO tax_rates 
               (config_id, assumed, federal_single, state_single, federal_dual, state_dual) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (config_id, tax_rates["assumed"], tax_rates["federal_single"], 
             tax_rates["state_single"], tax_rates["federal_dual"], tax_rates["state_dual"])
        )
        
        # Migrate financial assumptions
        assumptions = data["FINANCIAL_ASSUMPTIONS"]
        await db.execute(
            """INSERT INTO financial_assumptions 
               (config_id, assumption_description, interest_rate, years) 
               VALUES (?, ?, ?, ?)""",
            (config_id, assumptions["assumption_description"], 
             assumptions["interest_rate"], assumptions["years"])
        )
        
        # Migrate expense categories (as JSON blobs for complex nested data)
        expense_categories = [
            "VACATION_EXPENSES", "MISCELLANEOUS_EXPENSES", "MISCELLANEOUS_INCOME",
            "HOUSING_EXPENSES", "LIVING_EXPENSES", "LEISURE_ACTIVITIES", 
            "TRANSPORTATION", "KIDS_ACTIVITIES", "UTILITIES", "INSURANCE", "SUBSCRIPTIONS"
        ]
        
        for category in expense_categories:
            if category in data:
                await db.execute(
                    "INSERT INTO expense_categories (config_id, category_name, category_data) VALUES (?, ?, ?)",
                    (config_id, category, json.dumps(data[category]))
                )
        
        # Handle excluded expenses as special category
        await db.execute(
            "INSERT INTO expense_categories (config_id, category_name, category_data) VALUES (?, ?, ?)",
            (config_id, "EXCLUDED_EXPENSES", json.dumps(data["EXCLUDED_EXPENSES"]))
        )
        
        # Migrate spouse variants
        for spouse_num, spouse_key in enumerate(["spouse1_variants", "spouse2_variants"], 1):
            if spouse_key in data:
                for variant_name, variant_data in data[spouse_key].items():
                    income = variant_data["yearly_income"]
                    pretax = variant_data["pretax_investments"]
                    posttax = variant_data["posttax_investments"]
                    
                    await db.execute(
                        """INSERT INTO spouse_variants 
                           (config_id, spouse_number, variant_name, base_income, bonus_income, 
                            quarterly_income, pretax_retirement, pretax_hsa, pretax_serplus,
                            posttax_retirement, posttax_espp) 
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (config_id, spouse_num, variant_name, income["base"], income["bonus"],
                         income["quarterly"], pretax["retirement_contribution"], pretax["hsa"],
                         pretax["serplus"], posttax["retirement_contribution"], 
                         posttax["employee_stock_purchase_plan"])
                    )
        
        # Migrate retirement accounts
        if "RETIREMENT" in data:
            for person in data["RETIREMENT"]:
                person_name = person["name"]
                accounts = person["accounts"]
                
                for account_type, account_list in accounts.items():
                    for account_dict in account_list:
                        for account_name, amount in account_dict.items():
                            await db.execute(
                                """INSERT INTO retirement_accounts 
                                   (config_id, person_name, account_type, account_name, amount) 
                                   VALUES (?, ?, ?, ?, ?)""",
                                (config_id, person_name, account_type, account_name, amount)
                            )
        
        # Migrate investments
        if "INVESTMENTS" in data:
            for inv_key, inv_data in data["INVESTMENTS"].items():
                await db.execute(
                    """INSERT INTO investments 
                       (config_id, investment_key, name, type, amount) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (config_id, inv_key, inv_data["name"], inv_data["type"], inv_data["amount"])
                )
        
        # Migrate education scenarios
        if "children_variants" in data:
            for scenario_name, scenario_data in data["children_variants"].items():
                await db.execute(
                    """INSERT INTO education_scenarios 
                       (config_id, scenario_name, scenario_type, scenario_data) 
                       VALUES (?, ?, ?, ?)""",
                    (config_id, scenario_name, scenario_data["type"], json.dumps(scenario_data))
                )
        
        # Migrate house data
        for house_type in ["house", "new_house"]:
            if house_type in data:
                house = data[house_type]
                await db.execute(
                    """INSERT INTO houses 
                       (config_id, house_type, description, cost_basis, closing_costs, 
                        home_improvement, value, mortgage_principal, commission_rate,
                        annual_growth_rate, interest_rate, monthly_payment, payments_made,
                        number_of_payments, annual_property_tax, sell_house) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (config_id, house_type, house["description"], house["cost_basis"],
                     house.get("closing_costs", 0), house.get("home_improvement", 0),
                     house["value"], house["mortgage_principal"], house["commission_rate"],
                     house["annual_growth_rate"], house["interest_rate"], house["monthly_payment"],
                     house["payments_made"], house["number_of_payments"], 
                     house["annual_property_tax"], house.get("sell_house", False))
                )
        
        await db.commit()
        logger.info(f"Successfully migrated all data to database with config_id: {config_id}")
        return config_id

async def run_migration(
    json_file_path: str = "G:/jason/git/WebDevelopment/Frameworks/vivikaFinance/scenarios/general.finance.json",
    db_path: str = "scenarios.db",
    config_name: str = "default"
):
    """Run the complete migration process."""
    logger.info("Starting financial configuration migration...")
    
    # Create tables
    await create_financial_config_tables(db_path)
    
    # Check if JSON file exists
    if not Path(json_file_path).exists():
        raise FileNotFoundError(f"JSON file not found: {json_file_path}")
    
    # Migrate data
    config_id = await migrate_json_to_database(json_file_path, db_path, config_name)
    
    logger.info(f"Migration completed successfully! Config ID: {config_id}")
    return config_id

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run migration
    asyncio.run(run_migration())