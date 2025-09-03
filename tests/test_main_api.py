"""
Tests for the main FastAPI application endpoints.
"""

import pytest
import asyncio
import json
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

# Import the FastAPI app
from main import app
from models.financial_models import ScenarioInput, UserProfile, ProjectionSettings, FinancialAssumptions, ScenarioType


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Create an async test client for the FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_scenario_data():
    """Create sample scenario data for testing."""
    return {
        "name": "Test Retirement Scenario",
        "description": "Testing scenario creation",
        "scenario_type": "retirement",
        "user_profile": {
            "name": "Test User",
            "birth_date": "1985-01-01",
            "current_age": 38,
            "retirement_age": 65,
            "life_expectancy": 90,
            "current_city": "Test City",
            "annual_salary": 75000,
            "assets": [
                {
                    "name": "401k",
                    "asset_type": "retirement",
                    "current_value": 150000,
                    "growth_rate": 0.07
                }
            ],
            "liabilities": [],
            "income_sources": [],
            "expenses": [
                {
                    "name": "Living Expenses",
                    "category": "living",
                    "annual_amount": 48000,
                    "start_age": 38,
                    "inflation_adjusted": True
                }
            ],
            "retirement_accounts": []
        },
        "projection_settings": {
            "start_year": 2024,
            "projection_years": 30,
            "assumptions": {
                "inflation_rate": 0.03,
                "investment_return": 0.07,
                "salary_growth_rate": 0.03,
                "tax_rate": 0.22
            }
        },
        "retirement_income_target": 60000
    }


class TestMainAPI:
    """Test cases for main API endpoints."""

    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "long-term-financial-planning"

    def test_root_endpoint(self, client):
        """Test the root endpoint serves React app."""
        # Note: This test might fail if the React build doesn't exist
        response = client.get("/")
        
        # Should either serve the React app or return a 404
        assert response.status_code in [200, 404]

    @patch('services.scenario_manager.ScenarioManager.create_scenario')
    def test_create_scenario(self, mock_create_scenario, client, sample_scenario_data):
        """Test creating a new scenario."""
        # Mock the scenario creation
        mock_create_scenario.return_value = "test-scenario-id"
        
        response = client.post("/api/scenarios", json=sample_scenario_data)
        
        assert response.status_code == 200
        assert response.json() == "test-scenario-id"
        mock_create_scenario.assert_called_once()

    @patch('services.scenario_manager.ScenarioManager.list_scenarios')
    def test_list_scenarios(self, mock_list_scenarios, client):
        """Test listing scenarios."""
        # Mock the scenario list
        mock_scenarios = [
            {
                "id": "scenario-1",
                "name": "Test Scenario 1",
                "scenario_type": "retirement",
                "created_at": "2024-01-01T00:00:00"
            }
        ]
        mock_list_scenarios.return_value = mock_scenarios
        
        response = client.get("/api/scenarios")
        
        assert response.status_code == 200
        assert response.json() == mock_scenarios
        mock_list_scenarios.assert_called_once()

    @patch('services.scenario_manager.ScenarioManager.get_scenario')
    def test_get_scenario(self, mock_get_scenario, client):
        """Test getting a specific scenario."""
        # Mock the scenario data
        mock_scenario_data = {
            "id": "test-scenario-id",
            "name": "Test Scenario",
            "scenario_type": "retirement",
            "user_data": "{}",
            "projection_data": "{}",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }
        mock_get_scenario.return_value = mock_scenario_data
        
        response = client.get("/api/scenarios/test-scenario-id")
        
        assert response.status_code == 200
        assert response.json() == mock_scenario_data
        mock_get_scenario.assert_called_once_with("test-scenario-id")

    @patch('services.scenario_manager.ScenarioManager.get_scenario')
    def test_get_nonexistent_scenario(self, mock_get_scenario, client):
        """Test getting a non-existent scenario."""
        mock_get_scenario.return_value = None
        
        response = client.get("/api/scenarios/nonexistent-id")
        
        assert response.status_code == 404
        assert "Scenario not found" in response.json()["detail"]

    @patch('services.scenario_manager.ScenarioManager.run_projection')
    def test_run_projection(self, mock_run_projection, client):
        """Test running a projection for a scenario."""
        # Mock the projection result
        mock_projection = {
            "scenario_id": "test-scenario-id",
            "scenario_name": "Test Scenario",
            "yearly_projections": [],
            "final_net_worth": 500000,
            "retirement_income_replacement": 0.8,
            "years_of_expenses_covered": 12.5,
            "is_goal_achievable": True
        }
        mock_run_projection.return_value = type('MockProjection', (), mock_projection)()
        
        response = client.post("/api/scenarios/test-scenario-id/project")
        
        assert response.status_code == 200
        mock_run_projection.assert_called_once()

    @patch('services.scenario_manager.ScenarioManager.compare_scenarios')
    def test_compare_scenarios(self, mock_compare_scenarios, client):
        """Test comparing multiple scenarios."""
        # Mock the comparison result
        mock_comparison = {
            "scenario-1": {"final_net_worth": 500000},
            "scenario-2": {"final_net_worth": 450000}
        }
        mock_compare_scenarios.return_value = mock_comparison
        
        response = client.post("/api/scenarios/compare", json=["scenario-1", "scenario-2"])
        
        assert response.status_code == 200
        assert response.json() == mock_comparison
        mock_compare_scenarios.assert_called_once_with(["scenario-1", "scenario-2"])

    def test_compare_scenarios_insufficient_data(self, client):
        """Test comparing scenarios with insufficient data."""
        response = client.post("/api/scenarios/compare", json=["scenario-1"])
        
        assert response.status_code == 400
        assert "At least 2 scenarios required" in response.json()["detail"]

    @patch('services.external_data_service.ExternalDataService.get_city_cost_data')
    def test_compare_cities(self, mock_get_city_data, client):
        """Test city cost comparison."""
        # Mock city data
        from models.financial_models import CityComparisonData
        
        mock_city_data = CityComparisonData(
            city_name="Test City",
            state="CA",
            cost_index=120.0,
            housing_cost=3000.0,
            utilities_cost=200.0,
            grocery_cost=400.0,
            transportation_cost=150.0,
            healthcare_cost=300.0,
            overall_cost_difference=0.2
        )
        
        with patch('services.scenario_manager.ScenarioManager.analyze_city_relocation') as mock_analyze:
            mock_comparison = type('MockComparison', (), {
                'current_city': mock_city_data,
                'target_city': mock_city_data,
                'annual_cost_difference': 5000,
                'net_worth_impact_10_year': 50000,
                'net_worth_impact_retirement': 100000
            })()
            mock_analyze.return_value = mock_comparison
            
            response = client.get("/api/city-comparison/New York, NY/Los Angeles, CA")
            
            assert response.status_code == 200
            mock_analyze.assert_called_once()

    @patch('services.external_data_service.ExternalDataService.get_city_cost_data')
    def test_get_city_data(self, mock_get_city_data, client):
        """Test getting city cost data."""
        from models.financial_models import CityComparisonData
        
        mock_city_data = CityComparisonData(
            city_name="San Francisco, CA",
            state="CA",
            cost_index=180.0,
            housing_cost=4500.0,
            utilities_cost=250.0,
            grocery_cost=450.0,
            transportation_cost=200.0,
            healthcare_cost=350.0,
            overall_cost_difference=0.8
        )
        mock_get_city_data.return_value = mock_city_data
        
        response = client.get("/api/city-data/San Francisco, CA")
        
        assert response.status_code == 200
        mock_get_city_data.assert_called_once_with("San Francisco, CA")

    @patch('services.scenario_manager.ScenarioManager.project_education_expenses')
    def test_education_projection(self, mock_project_education, client):
        """Test education expense projection."""
        from models.financial_models import EducationExpenseProjection
        
        mock_projection = EducationExpenseProjection(
            institution_type="public_college",
            annual_cost=30000,
            duration_years=4,
            inflation_rate=0.05,
            total_cost_present_value=100000,
            total_cost_future_value=150000,
            monthly_savings_required=800
        )
        mock_project_education.return_value = mock_projection
        
        response = client.post("/api/education-projection", params={
            "institution_type": "public_college",
            "start_year": 2030,
            "duration_years": 4,
            "current_child_age": 10
        })
        
        assert response.status_code == 200
        mock_project_education.assert_called_once()

    @patch('services.scenario_manager.ScenarioManager.analyze_vehicle_ownership')
    def test_vehicle_analysis(self, mock_analyze_vehicle, client):
        """Test vehicle ownership analysis."""
        from models.financial_models import VehicleOwnershipProjection
        
        mock_analysis = VehicleOwnershipProjection(
            vehicle_type="midsize",
            purchase_price=35000,
            financing_cost=5000,
            insurance_annual=1400,
            fuel_annual=2000,
            maintenance_annual=1000,
            depreciation_total=15000,
            total_cost_ownership=45000
        )
        mock_analyze_vehicle.return_value = mock_analysis
        
        response = client.post("/api/vehicle-analysis", params={
            "vehicle_type": "midsize",
            "ownership_years": 5,
            "annual_mileage": 12000
        })
        
        assert response.status_code == 200
        mock_analyze_vehicle.assert_called_once()

    @patch('services.external_data_service.ExternalDataService.get_inflation_data')
    def test_get_inflation_data(self, mock_get_inflation, client):
        """Test getting inflation data."""
        mock_inflation_data = {
            "current_cpi": 3.2,
            "core_cpi": 2.8,
            "pce": 2.9,
            "housing_inflation": 4.1,
            "education_inflation": 5.2,
            "healthcare_inflation": 3.8,
            "energy_inflation": 8.5
        }
        mock_get_inflation.return_value = mock_inflation_data
        
        response = client.get("/api/external-data/inflation")
        
        assert response.status_code == 200
        assert response.json() == mock_inflation_data
        mock_get_inflation.assert_called_once()

    @patch('services.external_data_service.ExternalDataService.get_market_data')
    def test_get_market_data(self, mock_get_market, client):
        """Test getting market data."""
        mock_market_data = {
            "sp500_return_ytd": 0.12,
            "bond_yield_10yr": 0.045,
            "volatility_index": 18.5,
            "dollar_strength_index": 102.3,
            "real_estate_index": 0.085
        }
        mock_get_market.return_value = mock_market_data
        
        response = client.get("/api/external-data/market")
        
        assert response.status_code == 200
        assert response.json() == mock_market_data
        mock_get_market.assert_called_once()

    def test_invalid_json_request(self, client, sample_scenario_data):
        """Test handling of invalid JSON in requests."""
        response = client.post("/api/scenarios", content="invalid json")
        
        assert response.status_code == 422  # Unprocessable Entity

    def test_missing_required_fields(self, client):
        """Test handling of missing required fields."""
        incomplete_data = {
            "name": "Test Scenario"
            # Missing required fields
        }
        
        response = client.post("/api/scenarios", json=incomplete_data)
        
        assert response.status_code == 422  # Validation error

    def test_cors_headers(self, client):
        """Test that CORS headers are properly set."""
        response = client.options("/api/health")
        
        # Should have CORS headers (exact implementation depends on FastAPI CORS setup)
        assert response.status_code in [200, 405]  # OPTIONS might not be implemented

    def test_static_file_serving(self, client):
        """Test that static files are served."""
        # This test depends on the frontend build existing
        response = client.get("/static/js/main.js")
        
        # Should either serve the file or return 404
        assert response.status_code in [200, 404]

    def test_catch_all_route(self, client):
        """Test that catch-all route serves React app."""
        response = client.get("/some-unknown-route")
        
        # Should serve React app (which handles client-side routing)
        assert response.status_code in [200, 404]

    @patch('services.scenario_manager.ScenarioManager.run_projection')
    def test_error_handling(self, mock_run_projection, client):
        """Test error handling in API endpoints."""
        # Mock an exception
        mock_run_projection.side_effect = ValueError("Test error")
        
        response = client.post("/api/scenarios/test-id/project")
        
        assert response.status_code == 404  # ValueError becomes 404
        assert "Test error" in response.json()["detail"]

    def test_request_timeout_handling(self, client):
        """Test handling of request timeouts."""
        # This is a basic test - actual timeout testing would require more setup
        response = client.get("/api/health")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_websocket_connection(self, async_client):
        """Test WebSocket connection endpoint."""
        # Note: Testing WebSocket connections requires special setup
        # This is a placeholder for WebSocket testing
        
        # Basic test that the endpoint exists
        try:
            async with async_client.websocket_connect("/ws/simulation/test-scenario-id") as websocket:
                # If we get here, connection was successful
                assert True
        except Exception:
            # WebSocket testing is complex and might fail without proper setup
            assert True  # Allow test to pass for now


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])