# Private Scenario Data Import Guide

This guide explains how to securely import your private financial scenario data into the Long-Term Financial Planning Application.

## 🔒 Security First

Your financial data is **never committed to git**. The application includes:
- `.gitignore` rules to exclude private data files
- Database files are excluded from version control
- All personal financial information stays local

## 📥 Import Methods

### Method 1: Command Line Import (Recommended)

Use the dedicated import utility for secure, validated imports:

```bash
# Show example JSON structure
python import_scenarios.py --example

# Validate your JSON without importing
python import_scenarios.py --validate my_scenarios.json

# Import your scenarios
python import_scenarios.py my_scenarios.json
```

### Method 2: API Import

Use the REST API for programmatic imports:

```bash
# Import via API (requires running server)
curl -X POST http://localhost:8000/api/scenarios/import \
  -H "Content-Type: application/json" \
  -d @my_scenarios.json
```

### Method 3: Web Interface

*(Future enhancement - not yet implemented)*

## 📄 JSON Format

Your scenario data should follow this structure:

```json
{
  "scenarios": [
    {
      "name": "My Retirement Plan",
      "description": "Conservative retirement planning",
      "scenario_type": "retirement",
      "user_profile": {
        "name": "Your Name",
        "birth_date": "1980-01-01",
        "current_age": 44,
        "retirement_age": 65,
        "life_expectancy": 90,
        "current_city": "Your City",
        "annual_salary": 75000,
        "assets": [
          {
            "name": "401k Portfolio",
            "asset_type": "stocks",
            "current_value": 150000,
            "expected_return": 0.07,
            "allocation_percentage": 0.8
          }
        ],
        "expenses": [
          {
            "name": "Living Expenses",
            "annual_amount": 50000,
            "start_age": 44,
            "inflation_adjusted": true
          }
        ],
        "income_sources": [],
        "liabilities": [],
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
```

## 🏗️ Data Structure Reference

### Required Fields

**Scenario Level:**
- `name`: String - Scenario name
- `scenario_type`: String - One of: "retirement", "current", "relocation", "education", "major_purchase"
- `user_profile`: Object - Your financial profile
- `projection_settings`: Object - Projection parameters

**User Profile:**
- `name`: String - Your name
- `birth_date`: String (YYYY-MM-DD) - Birth date
- `current_age`: Integer - Current age
- `annual_salary`: Number - Annual salary

**Assets** (optional array):
- `name`: String - Asset name
- `asset_type`: String - "stocks", "bonds", "real_estate", "cash", "crypto"
- `current_value`: Number - Current value
- `expected_return`: Number - Expected annual return (0.07 = 7%)
- `allocation_percentage`: Number - Portfolio allocation (0.0-1.0)

**Expenses** (optional array):
- `name`: String - Expense category name
- `annual_amount`: Number - Annual expense amount
- `start_age`: Integer - Age when expense starts
- `end_age`: Integer (optional) - Age when expense ends
- `inflation_adjusted`: Boolean - Whether to adjust for inflation

### Optional Fields

- `description`: String - Scenario description
- `retirement_age`: Integer - Retirement age (default: 65)
- `life_expectancy`: Integer - Life expectancy (default: 90)
- `target_city`: String - Target city for relocation scenarios
- `liabilities`: Array - Debts and liabilities
- `income_sources`: Array - Additional income sources
- `retirement_accounts`: Array - 401k, IRA accounts

## 🔍 Validation

The import process validates:
- Required fields are present
- Data types are correct
- Numeric values are within valid ranges
- Dates are properly formatted
- Enum values are valid

## 📊 After Import

Once imported, your scenarios will be available in:
- The web interface at http://localhost:3000
- Via API endpoints for projections and analysis
- Stored securely in your local SQLite database

## 🗂️ File Organization

Recommended file naming for privacy:
- `my_scenarios_private.json` - Your main scenarios
- `retirement_planning_private.json` - Retirement-specific scenarios
- `financial_backup_private.json` - Backup data

All files with `*_private.json` patterns are automatically ignored by git.

## 🚀 Quick Start

1. **Create your JSON file** using the example structure above
2. **Validate the structure**: `python import_scenarios.py --validate your_file.json`
3. **Import your data**: `python import_scenarios.py your_file.json`
4. **View in the app**: Navigate to http://localhost:3000

## 🆘 Troubleshooting

**Import Errors:**
- Check JSON syntax with a validator
- Ensure all required fields are present
- Verify numeric values are not strings
- Check date formats (YYYY-MM-DD)

**API Errors:**
- Ensure the backend server is running (http://localhost:8000)
- Check the API documentation for correct endpoints
- Verify JSON Content-Type headers

**Data Not Appearing:**
- Check the import success message
- Verify scenarios appear in API: `curl http://localhost:8000/api/scenarios`
- Check server logs for errors

## 📋 Export Data

Export your scenarios for backup:

```bash
# Via API
curl http://localhost:8000/api/export/scenarios > backup.json

# Via command line (future enhancement)
python export_scenarios.py --output backup.json
```

---

Your financial privacy is protected - no personal data leaves your machine!