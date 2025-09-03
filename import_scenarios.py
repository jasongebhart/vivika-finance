#!/usr/bin/env python3
"""
Command-line utility to import private scenario data from JSON files.
This script provides a secure way to import your personal financial scenarios
without storing them in the git repository.

Usage:
    python import_scenarios.py <json_file_path>
    python import_scenarios.py --help

Example JSON format:
{
  "scenarios": [
    {
      "name": "My Retirement Plan",
      "description": "Conservative retirement planning scenario",
      "scenario_type": "retirement",
      "user_profile": {
        "name": "John Doe",
        "birth_date": "1980-01-01",
        "current_age": 44,
        "retirement_age": 65,
        "life_expectancy": 90,
        "current_city": "Seattle",
        "annual_salary": 75000,
        "assets": [],
        "liabilities": [],
        "income_sources": [],
        "expenses": [],
        "retirement_accounts": []
      },
      "projection_settings": {
        "projection_years": 40,
        "assumptions": {
          "inflation_rate": 0.03,
          "investment_return": 0.07,
          "salary_growth_rate": 0.03,
          "tax_rate": 0.22
        }
      }
    }
  ]
}
"""

import asyncio
import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path to import our modules
sys.path.append(str(Path(__file__).parent))

from services.scenario_manager import ScenarioManager
from models.financial_models import ScenarioInput

class ScenarioImporter:
    """Handles importing scenarios from JSON files."""
    
    def __init__(self):
        self.scenario_manager = ScenarioManager()
    
    async def import_from_file(self, file_path: str) -> Dict[str, Any]:
        """Import scenarios from a JSON file."""
        try:
            # Read JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Initialize database
            await self.scenario_manager.initialize_database()
            
            # Import scenarios
            result = await self.import_scenarios(data)
            return result
            
        except FileNotFoundError:
            return {"error": f"File not found: {file_path}", "success": False}
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON format: {str(e)}", "success": False}
        except Exception as e:
            return {"error": f"Import failed: {str(e)}", "success": False}
    
    async def import_scenarios(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Import scenarios from parsed JSON data."""
        imported_count = 0
        errors = []
        scenario_ids = []
        
        scenarios = data.get('scenarios', [])
        
        if not scenarios:
            return {
                "error": "No scenarios found in JSON data",
                "success": False
            }
        
        print(f"Found {len(scenarios)} scenario(s) to import...")
        
        for i, scenario_data in enumerate(scenarios):
            try:
                print(f"Importing scenario {i+1}: {scenario_data.get('name', 'Unnamed')}")
                
                # Validate and create ScenarioInput from JSON
                scenario_input = ScenarioInput(**scenario_data)
                scenario_id = await self.scenario_manager.create_scenario(scenario_input)
                scenario_ids.append(scenario_id)
                imported_count += 1
                
                print(f"Successfully imported: {scenario_input.name} (ID: {scenario_id})")
                
            except Exception as e:
                error_msg = f"Scenario {i+1} ({scenario_data.get('name', 'Unnamed')}): {str(e)}"
                errors.append(error_msg)
                print(f"Failed to import scenario {i+1}: {str(e)}")
        
        return {
            "imported_count": imported_count,
            "total_scenarios": len(scenarios),
            "scenario_ids": scenario_ids,
            "errors": errors,
            "success": imported_count > 0
        }
    
    async def validate_json_structure(self, file_path: str) -> Dict[str, Any]:
        """Validate JSON structure without importing."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            scenarios = data.get('scenarios', [])
            validation_errors = []
            
            if not scenarios:
                return {"valid": False, "error": "No 'scenarios' array found in JSON"}
            
            for i, scenario_data in enumerate(scenarios):
                try:
                    # Try to create ScenarioInput to validate structure
                    ScenarioInput(**scenario_data)
                except Exception as e:
                    validation_errors.append(f"Scenario {i+1}: {str(e)}")
            
            return {
                "valid": len(validation_errors) == 0,
                "scenario_count": len(scenarios),
                "errors": validation_errors
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}

def print_help():
    """Print usage information."""
    print(__doc__)

async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Import private scenario data from JSON files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('file_path', nargs='?', help='Path to JSON file containing scenarios')
    parser.add_argument('--validate', '-v', action='store_true', 
                       help='Validate JSON structure without importing')
    parser.add_argument('--example', '-e', action='store_true',
                       help='Show example JSON structure')
    
    args = parser.parse_args()
    
    if args.example:
        example_data = {
            "scenarios": [
                {
                    "name": "Example Retirement Scenario",
                    "description": "Basic retirement planning example",
                    "scenario_type": "retirement",
                    "user_profile": {
                        "name": "John Doe",
                        "birth_date": "1980-01-01",
                        "current_age": 44,
                        "retirement_age": 65,
                        "life_expectancy": 90,
                        "current_city": "Seattle",
                        "annual_salary": 75000,
                        "assets": [
                            {
                                "name": "Investment Portfolio",
                                "asset_type": "stocks",
                                "current_value": 50000,
                                "expected_return": 0.07,
                                "allocation_percentage": 0.7
                            }
                        ],
                        "liabilities": [],
                        "income_sources": [],
                        "expenses": [
                            {
                                "name": "Living Expenses",
                                "annual_amount": 50000,
                                "start_age": 44,
                                "end_age": 120,
                                "inflation_adjusted": True
                            }
                        ],
                        "retirement_accounts": []
                    },
                    "projection_settings": {
                        "projection_years": 40,
                        "assumptions": {
                            "inflation_rate": 0.03,
                            "investment_return": 0.07,
                            "salary_growth_rate": 0.03,
                            "tax_rate": 0.22
                        }
                    }
                }
            ]
        }
        print("Example JSON structure:")
        print(json.dumps(example_data, indent=2))
        return
    
    if not args.file_path:
        parser.print_help()
        return
    
    importer = ScenarioImporter()
    
    if args.validate:
        print(f"Validating JSON structure in: {args.file_path}")
        result = await importer.validate_json_structure(args.file_path)
        
        if result["valid"]:
            print(f"JSON structure is valid ({result['scenario_count']} scenarios)")
        else:
            print(f"JSON validation failed: {result.get('error', 'Unknown error')}")
            if result.get('errors'):
                for error in result['errors']:
                    print(f"  - {error}")
    else:
        print(f"Importing scenarios from: {args.file_path}")
        result = await importer.import_from_file(args.file_path)
        
        if result["success"]:
            print(f"\nImport completed successfully!")
            print(f"  - Imported: {result['imported_count']} scenarios")
            print(f"  - Scenario IDs: {', '.join(result['scenario_ids'])}")
            
            if result.get('errors'):
                print(f"  - Errors: {len(result['errors'])}")
                for error in result['errors']:
                    print(f"    - {error}")
        else:
            print(f"\nImport failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(main())