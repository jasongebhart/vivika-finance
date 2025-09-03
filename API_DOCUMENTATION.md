# Long-Term Financial Planning API Documentation

## Overview

The Long-Term Financial Planning API provides comprehensive endpoints for financial scenario modeling, Monte Carlo simulations, cost-of-living analysis, and specialized financial planning tools. All endpoints return JSON responses and support CORS for web applications.

**Base URL**: `http://localhost:8000/api`  
**WebSocket URL**: `ws://localhost:8000/ws`

## Authentication

Currently, the API does not require authentication. For production deployments, implement JWT tokens or session-based authentication.

## Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "data": {...},
  "status": "success"
}
```

### Error Response
```json
{
  "detail": "Error message",
  "status": "error"
}
```

## Core Endpoints

### Health Check

#### `GET /api/health`

Check the API health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "long-term-financial-planning"
}
```

---

## Scenario Management

### Create Scenario

#### `POST /api/scenarios`

Create a new financial scenario for analysis.

**Request Body:**
```json
{
  "name": "Early Retirement Plan",
  "description": "Analyzing early retirement at age 55",
  "scenario_type": "retirement",
  "user_profile": {
    "name": "John Doe",
    "birth_date": "1985-01-01",
    "current_age": 38,
    "retirement_age": 55,
    "life_expectancy": 90,
    "current_city": "Austin, TX",
    "annual_salary": 85000,
    "assets": [
      {
        "name": "401k",
        "asset_type": "retirement",
        "current_value": 250000,
        "growth_rate": 0.07
      }
    ],
    "liabilities": [
      {
        "name": "Mortgage", 
        "liability_type": "mortgage",
        "current_balance": 180000,
        "interest_rate": 0.035,
        "minimum_payment": 1200
      }
    ],
    "income_sources": [
      {
        "name": "Social Security",
        "source_type": "social_security", 
        "annual_amount": 24000,
        "start_age": 67,
        "growth_rate": 0.02
      }
    ],
    "expenses": [
      {
        "name": "Living Expenses",
        "category": "living",
        "annual_amount": 60000,
        "start_age": 38,
        "inflation_adjusted": true
      }
    ],
    "retirement_accounts": []
  },
  "projection_settings": {
    "start_year": 2024,
    "projection_years": 35,
    "assumptions": {
      "inflation_rate": 0.03,
      "investment_return": 0.07,
      "salary_growth_rate": 0.03,
      "tax_rate": 0.22
    }
  },
  "retirement_income_target": 50000
}
```

**Response:**
```json
"scenario-uuid-string"
```

### List Scenarios

#### `GET /api/scenarios`

Retrieve all created scenarios.

**Response:**
```json
[
  {
    "id": "scenario-uuid",
    "name": "Early Retirement Plan",
    "scenario_type": "retirement",
    "created_at": "2024-01-01T12:00:00Z"
  }
]
```

### Get Scenario

#### `GET /api/scenarios/{scenario_id}`

Retrieve a specific scenario by ID.

**Parameters:**
- `scenario_id` (path): UUID of the scenario

**Response:**
```json
{
  "id": "scenario-uuid",
  "name": "Early Retirement Plan", 
  "scenario_type": "retirement",
  "user_data": "{...}",
  "projection_data": "{...}",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Run Projection

#### `POST /api/scenarios/{scenario_id}/project`

Run a financial projection for a scenario.

**Parameters:**
- `scenario_id` (path): UUID of the scenario
- `include_monte_carlo` (query, optional): Boolean to include Monte Carlo analysis

**Response:**
```json
{
  "scenario_id": "scenario-uuid",
  "scenario_name": "Early Retirement Plan",
  "yearly_projections": [
    {
      "year": 2024,
      "age": 38,
      "beginning_assets": 250000,
      "income": 66300,
      "expenses": 60000,
      "net_cash_flow": 6300,
      "ending_assets": 274610,
      "tax_liability": 18700
    }
  ],
  "final_net_worth": 850000,
  "retirement_income_replacement": 0.72,
  "years_of_expenses_covered": 14.2,
  "is_goal_achievable": true,
  "assumptions_used": {
    "inflation_rate": 0.03,
    "investment_return": 0.07,
    "salary_growth_rate": 0.03,
    "tax_rate": 0.22
  },
  "monte_carlo_results": null
}
```

### Compare Scenarios

#### `POST /api/scenarios/compare`

Compare multiple scenarios side by side.

**Request Body:**
```json
["scenario-uuid-1", "scenario-uuid-2", "scenario-uuid-3"]
```

**Response:**
```json
{
  "scenario-uuid-1": {
    "scenario_name": "Conservative Plan",
    "final_net_worth": 750000,
    "retirement_income_replacement": 0.65
  },
  "scenario-uuid-2": {
    "scenario_name": "Aggressive Plan", 
    "final_net_worth": 950000,
    "retirement_income_replacement": 0.85
  }
}
```

---

## Monte Carlo Simulations

### Run Monte Carlo Simulation

#### `POST /api/monte-carlo/{scenario_id}`

Run a Monte Carlo simulation for probabilistic analysis.

**Parameters:**
- `scenario_id` (path): UUID of the scenario

**Request Body (optional):**
```json
{
  "simulations": 1000,
  "return_std_dev": 0.15,
  "inflation_std_dev": 0.01,
  "salary_growth_std_dev": 0.02,
  "confidence_level": 0.9
}
```

**Response:**
```json
{
  "simulations_run": 1000,
  "projection_years": 35,
  "success_probability": 0.78,
  "median_final_value": 825000,
  "mean_final_value": 850000,
  "std_dev_final_value": 320000,
  "worst_case_10th_percentile": 420000,
  "best_case_90th_percentile": 1350000,
  "annual_projections": [
    {
      "year": 2024,
      "simulation_results": [
        {
          "net_worth": 275000,
          "portfolio_value": 260000,
          "annual_income": 66500,
          "withdrawal_rate": 0.0
        }
      ]
    }
  ],
  "final_year_distribution": {
    "net_worth": [420000, 520000, 625000, 725000, 825000, 925000, 1025000, 1125000, 1350000]
  }
}
```

### Analyze Withdrawal Strategies

#### `POST /api/withdrawal-strategies/{scenario_id}`

Analyze different retirement withdrawal strategies.

**Parameters:**
- `scenario_id` (path): UUID of the scenario

**Response:**
```json
{
  "strategies": [
    {
      "name": "4% Rule",
      "description": "Traditional 4% annual withdrawal rate",
      "success_rate": 0.82,
      "median_final_value": 650000,
      "worst_case_10th_percentile": 280000
    },
    {
      "name": "Dynamic Withdrawal",
      "description": "Adjust withdrawal based on portfolio performance",
      "success_rate": 0.91,
      "median_final_value": 750000,
      "worst_case_10th_percentile": 350000
    }
  ]
}
```

---

## Cost-of-Living Analysis

### Compare Cities

#### `GET /api/city-comparison/{current_city}/{target_city}`

Compare cost of living between two cities.

**Parameters:**
- `current_city` (path): Current city name (URL encoded)
- `target_city` (path): Target city name (URL encoded)

**Example:** `/api/city-comparison/New%20York,%20NY/Austin,%20TX`

**Response:**
```json
{
  "current_city": {
    "city_name": "New York, NY",
    "state": "NY",
    "cost_index": 180.0,
    "housing_cost": 4500.0,
    "utilities_cost": 250.0,
    "grocery_cost": 450.0,
    "transportation_cost": 200.0,
    "healthcare_cost": 350.0,
    "overall_cost_difference": 0.8
  },
  "target_city": {
    "city_name": "Austin, TX",
    "state": "TX", 
    "cost_index": 110.0,
    "housing_cost": 1800.0,
    "utilities_cost": 150.0,
    "grocery_cost": 320.0,
    "transportation_cost": 120.0,
    "healthcare_cost": 220.0,
    "overall_cost_difference": 0.1
  },
  "annual_cost_difference": -28000,
  "net_worth_impact_10_year": -350000,
  "net_worth_impact_retirement": -750000
}
```

### Get City Data

#### `GET /api/city-data/{city_name}`

Get detailed cost of living data for a specific city.

**Parameters:**
- `city_name` (path): City name (URL encoded)

**Response:**
```json
{
  "city_name": "San Francisco, CA",
  "state": "CA",
  "cost_index": 180.0,
  "housing_cost": 4500.0,
  "utilities_cost": 250.0,
  "grocery_cost": 450.0,
  "transportation_cost": 200.0,
  "healthcare_cost": 350.0,
  "overall_cost_difference": 0.8
}
```

---

## Education Planning

### Project Education Expenses

#### `POST /api/education-projection`

Calculate education expense projections with inflation.

**Query Parameters:**
- `institution_type` (string): Type of institution
  - `private_k12`
  - `public_college_in_state`
  - `public_college_out_state`
  - `private_college`
- `start_year` (integer): Year when education begins
- `duration_years` (integer): Length of education program
- `current_child_age` (integer): Child's current age

**Example:** `/api/education-projection?institution_type=private_college&start_year=2030&duration_years=4&current_child_age=12`

**Response:**
```json
{
  "institution_type": "private_college",
  "annual_cost": 58000,
  "duration_years": 4,
  "inflation_rate": 0.05,
  "total_cost_present_value": 185000,
  "total_cost_future_value": 275000,
  "monthly_savings_required": 950
}
```

---

## Vehicle Analysis

### Analyze Vehicle Ownership

#### `POST /api/vehicle-analysis`

Analyze total cost of vehicle ownership.

**Query Parameters:**
- `vehicle_type` (string): Type of vehicle
  - `economy`
  - `midsize`
  - `luxury`
  - `suv`
  - `electric`
- `ownership_years` (integer): Length of ownership period
- `annual_mileage` (integer, optional): Miles driven per year (default: 12000)

**Example:** `/api/vehicle-analysis?vehicle_type=midsize&ownership_years=5&annual_mileage=15000`

**Response:**
```json
{
  "vehicle_type": "midsize",
  "purchase_price": 35000,
  "financing_cost": 4200,
  "insurance_annual": 1400,
  "fuel_annual": 2400,
  "maintenance_annual": 1000,
  "depreciation_total": 18500,
  "total_cost_ownership": 47500
}
```

---

## Goal Analysis

### Analyze Financial Goals

#### `POST /api/goals/analyze`

Analyze the feasibility of financial goals.

**Request Body:**
```json
[
  {
    "name": "Emergency Fund",
    "goal_type": "emergency_fund",
    "target_amount": 50000,
    "target_date": "2028-01-01",
    "current_amount": 12000,
    "monthly_contribution": 800,
    "expected_return": 0.04
  },
  {
    "name": "House Down Payment",
    "goal_type": "major_purchase",
    "target_amount": 80000,
    "target_date": "2027-06-01", 
    "current_amount": 25000,
    "monthly_contribution": 1200,
    "expected_return": 0.06
  }
]
```

**Response:**
```json
[
  {
    "goal": {
      "name": "Emergency Fund",
      "target_amount": 50000,
      "target_date": "2028-01-01"
    },
    "projected_final_amount": 52500,
    "shortfall_amount": 0,
    "probability_of_success": 1.0,
    "required_monthly_contribution": 750,
    "recommended_adjustments": []
  }
]
```

---

## External Data

### Get Inflation Data

#### `GET /api/external-data/inflation`

Retrieve current inflation data for modeling.

**Response:**
```json
{
  "current_cpi": 3.2,
  "core_cpi": 2.8,
  "pce": 2.9,
  "housing_inflation": 4.1,
  "education_inflation": 5.2,
  "healthcare_inflation": 3.8,
  "energy_inflation": 8.5
}
```

### Get Market Data

#### `GET /api/external-data/market`

Retrieve current market data for investment modeling.

**Response:**
```json
{
  "sp500_return_ytd": 0.12,
  "bond_yield_10yr": 0.045,
  "volatility_index": 18.5,
  "dollar_strength_index": 102.3,
  "real_estate_index": 0.085
}
```

---

## WebSocket Endpoints

### Real-time Simulation Updates

#### `WS /ws/simulation/{scenario_id}`

WebSocket connection for real-time Monte Carlo simulation progress.

**Connection URL:** `ws://localhost:8000/ws/simulation/{scenario_id}`

**Messages to Send:**
```json
"start_monte_carlo"
```

**Messages Received:**

**Progress Update:**
```
progress:45.5:Running simulation iteration 455/1000
```

**Completion:**
```
complete:{"simulations_run": 1000, "success_probability": 0.78, ...}
```

**Error:**
```
error:Scenario not found
```

**Connection Status:**
- **Connected**: Ready to receive simulation commands
- **Progress**: Simulation running with percentage complete
- **Complete**: Simulation finished with full results
- **Error**: Simulation failed with error message

---

## Data Models

### Scenario Types
- `current`: Current financial plan analysis
- `retirement`: Retirement planning scenario
- `relocation`: City relocation impact analysis
- `education`: Education expense planning
- `major_purchase`: Major purchase impact analysis

### Asset Types
- `cash`: Savings, checking accounts
- `investment`: Stocks, bonds, mutual funds
- `retirement`: 401k, IRA, pension accounts
- `real_estate`: Primary residence, rental properties
- `other`: Other tangible assets

### Goal Types
- `emergency_fund`: Emergency savings goal
- `retirement`: Retirement savings goal
- `major_purchase`: House, car, etc.
- `education`: Education savings goal
- `debt_payoff`: Debt elimination goal

---

## Error Codes

### HTTP Status Codes
- `200`: Success
- `400`: Bad Request - Invalid input data
- `404`: Not Found - Resource not found
- `422`: Unprocessable Entity - Validation error
- `500`: Internal Server Error - Server-side error

### Common Error Messages
- `"Scenario not found"`: Invalid scenario ID
- `"At least 2 scenarios required for comparison"`: Insufficient scenarios for comparison
- `"Invalid scenario type"`: Unsupported scenario type
- `"Validation error"`: Pydantic model validation failed

---

## Rate Limits

Currently no rate limits are implemented. For production use, consider implementing:
- 100 requests per minute per IP
- 10 Monte Carlo simulations per hour per IP
- WebSocket connections limited to 5 per IP

---

## Caching

The API implements intelligent caching:
- **External Data**: 24-hour cache for city costs, market data
- **Inflation Data**: 6-hour cache for economic indicators  
- **Simulation Results**: No caching (results are scenario-specific)

---

## Examples

### Complete Scenario Creation and Analysis

```bash
# 1. Create a scenario
curl -X POST "http://localhost:8000/api/scenarios" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Retirement Analysis",
    "scenario_type": "retirement",
    "user_profile": {...},
    "projection_settings": {...}
  }'

# Response: "scenario-uuid"

# 2. Run projection
curl -X POST "http://localhost:8000/api/scenarios/scenario-uuid/project?include_monte_carlo=true"

# 3. Compare cities for relocation
curl "http://localhost:8000/api/city-comparison/Austin,%20TX/Denver,%20CO"

# 4. WebSocket connection for real-time updates
wscat -c ws://localhost:8000/ws/simulation/scenario-uuid
> start_monte_carlo
< progress:25.0:Running simulation...
< complete:{...}
```

### Frontend Integration

```javascript
// API client setup
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' }
});

// Create scenario
const scenario = await api.post('/scenarios', scenarioData);

// Run projection with progress tracking
const ws = new WebSocket(`ws://localhost:8000/ws/simulation/${scenario.data}`);
ws.onmessage = (event) => {
  if (event.data.startsWith('progress:')) {
    const [, progress, message] = event.data.split(':');
    updateProgressBar(parseFloat(progress));
  }
};
ws.send('start_monte_carlo');
```

---

This API provides comprehensive financial planning capabilities with sophisticated modeling, real-time updates, and extensive scenario analysis features.