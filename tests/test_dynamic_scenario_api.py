"""
Tests for the dynamic scenario API endpoints.
"""

import pytest
import asyncio
import json
from httpx import AsyncClient
from main import app


@pytest.fixture
def client():
    """Create test client."""
    return AsyncClient(app=app, base_url="http://test")


class TestScenarioGeneration:
    """Test scenario generation API endpoint."""
    
    @pytest.mark.asyncio
    async def test_generate_scenario_basic(self, client):
        """Test basic scenario generation."""
        scenario_params = {
            "location": "Mn",
            "spouse1Status": "Work",
            "spouse2Status": "Work", 
            "housing": "Own",
            "schoolType": "Public",
            "projectionYears": 8
        }
        
        response = await client.post("/api/scenarios/generate", json=scenario_params)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "scenario_id" in data
        assert "name" in data
        assert data["status"] == "created"
        
    @pytest.mark.asyncio
    async def test_generate_scenario_all_locations(self, client):
        """Test scenario generation for all supported locations."""
        base_params = {
            "spouse1Status": "Work",
            "spouse2Status": "Work",
            "housing": "Own", 
            "schoolType": "Public",
            "projectionYears": 8
        }
        
        locations = ["Sf", "Sd", "Mn"]
        
        for location in locations:
            params = {**base_params, "location": location}
            response = await client.post("/api/scenarios/generate", json=params)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "created"
            
    @pytest.mark.asyncio
    async def test_generate_scenario_all_school_types(self, client):
        """Test scenario generation for all school types."""
        base_params = {
            "location": "Mn",
            "spouse1Status": "Work",
            "spouse2Status": "Work",
            "housing": "Own",
            "projectionYears": 8
        }
        
        school_types = ["Public", "Private"]
        
        for school_type in school_types:
            params = {**base_params, "schoolType": school_type}
            response = await client.post("/api/scenarios/generate", json=params)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "created"
            
    @pytest.mark.asyncio
    async def test_generate_scenario_invalid_params(self, client):
        """Test scenario generation with invalid parameters."""
        invalid_params = {
            "location": "InvalidLocation",
            "spouse1Status": "Work",
            "spouse2Status": "Work",
            "housing": "Own",
            "schoolType": "Public",
            "projectionYears": 8
        }
        
        response = await client.post("/api/scenarios/generate", json=invalid_params)
        
        # Should still create scenario but might use default location
        assert response.status_code in [200, 400]
        
    @pytest.mark.asyncio 
    async def test_generate_scenario_missing_params(self, client):
        """Test scenario generation with missing parameters."""
        incomplete_params = {
            "location": "Mn",
            "spouse1Status": "Work"
            # Missing other required fields
        }
        
        response = await client.post("/api/scenarios/generate", json=incomplete_params)
        
        # Should either succeed with defaults or return 400
        assert response.status_code in [200, 400]


class TestScenarioExecution:
    """Test scenario execution (running projections)."""
    
    @pytest.mark.asyncio
    async def test_run_scenario(self, client):
        """Test running a scenario projection."""
        # First generate a scenario
        scenario_params = {
            "location": "Mn",
            "spouse1Status": "Work",
            "spouse2Status": "Work",
            "housing": "Own", 
            "schoolType": "Public",
            "projectionYears": 8
        }
        
        create_response = await client.post("/api/scenarios/generate", json=scenario_params)
        assert create_response.status_code == 200
        
        scenario_data = create_response.json()
        scenario_id = scenario_data["scenario_id"]
        
        # Now run the scenario
        run_params = {
            "id": scenario_id,
            "name": scenario_data.get("name", "Test Scenario")
        }
        
        response = await client.post("/api/scenarios/run", json=run_params)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["status"] in ["running", "completed", "queued"]
        
    @pytest.mark.asyncio
    async def test_run_nonexistent_scenario(self, client):
        """Test running a scenario that doesn't exist."""
        run_params = {
            "id": "nonexistent-scenario-id",
            "name": "Nonexistent Scenario"
        }
        
        response = await client.post("/api/scenarios/run", json=run_params)
        
        assert response.status_code == 404


class TestScenarioRetrieval:
    """Test scenario retrieval endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_scenarios_list(self, client):
        """Test getting list of scenarios."""
        response = await client.get("/api/dynamic-scenarios")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        # Each scenario should have proper structure
        for scenario in data:
            assert "id" in scenario
            assert "name" in scenario
            assert "status" in scenario
            assert "created_at" in scenario
            
    @pytest.mark.asyncio
    async def test_get_scenarios_with_limit(self, client):
        """Test getting scenarios with limit parameter."""
        response = await client.get("/api/dynamic-scenarios?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) <= 5
        
    @pytest.mark.asyncio
    async def test_get_scenario_by_id(self, client):
        """Test getting a specific scenario by ID."""
        # First get list of scenarios
        list_response = await client.get("/api/dynamic-scenarios?limit=1")
        assert list_response.status_code == 200
        scenarios = list_response.json()
        
        if len(scenarios) > 0:
            scenario_id = scenarios[0]["id"]
            
            # Get specific scenario
            response = await client.get(f"/api/dynamic-scenarios/{scenario_id}")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["id"] == scenario_id
            assert "name" in data
            assert "location" in data
            assert "status" in data
            
    @pytest.mark.asyncio
    async def test_get_nonexistent_scenario(self, client):
        """Test getting a scenario that doesn't exist."""
        response = await client.get("/api/dynamic-scenarios/nonexistent-id")
        
        assert response.status_code == 404


class TestScenarioComparison:
    """Test scenario comparison functionality."""
    
    @pytest.mark.asyncio
    async def test_compare_scenarios(self, client):
        """Test comparing multiple scenarios."""
        # Get list of scenarios
        list_response = await client.get("/api/dynamic-scenarios?limit=3")
        assert list_response.status_code == 200
        scenarios = list_response.json()
        
        if len(scenarios) >= 2:
            scenario_ids = [s["id"] for s in scenarios[:2]]
            
            comparison_params = {
                "scenario_ids": scenario_ids
            }
            
            response = await client.post("/api/scenarios/compare", json=comparison_params)
            
            assert response.status_code == 200
            data = response.json()
            
            assert "comparison" in data
            assert "summary" in data
            
    @pytest.mark.asyncio
    async def test_compare_insufficient_scenarios(self, client):
        """Test comparing with insufficient scenarios."""
        comparison_params = {
            "scenario_ids": ["single-scenario-id"]
        }
        
        response = await client.post("/api/scenarios/compare", json=comparison_params)
        
        assert response.status_code == 400


class TestScenarioDataStructure:
    """Test that scenario data has proper structure."""
    
    @pytest.mark.asyncio
    async def test_completed_scenario_structure(self, client):
        """Test that completed scenarios have proper data structure."""
        # Get completed scenarios
        response = await client.get("/api/dynamic-scenarios")
        assert response.status_code == 200
        scenarios = response.json()
        
        completed_scenarios = [s for s in scenarios if s["status"] == "completed"]
        
        if len(completed_scenarios) > 0:
            scenario = completed_scenarios[0]
            
            # Get full scenario details
            detail_response = await client.get(f"/api/dynamic-scenarios/{scenario['id']}")
            assert detail_response.status_code == 200
            
            data = detail_response.json()
            
            # Check basic structure
            assert "projection_results" in data
            results = data["projection_results"]
            
            # Check financial summary
            assert "final_net_worth" in results
            assert "annual_growth_rate" in results
            assert "total_expenses" in results
            assert "retirement_readiness" in results
            
            # Check that values are reasonable
            assert results["final_net_worth"] > 0
            assert 0 <= results["annual_growth_rate"] <= 1
            assert results["total_expenses"] > 0
            assert isinstance(results["retirement_readiness"], bool)
            
    @pytest.mark.asyncio
    async def test_scenario_with_detailed_expenses(self, client):
        """Test that scenarios include detailed expense breakdown."""
        response = await client.get("/api/dynamic-scenarios")
        assert response.status_code == 200
        scenarios = response.json()
        
        completed_scenarios = [s for s in scenarios if s["status"] == "completed"]
        
        if len(completed_scenarios) > 0:
            scenario = completed_scenarios[0]
            
            detail_response = await client.get(f"/api/dynamic-scenarios/{scenario['id']}")
            assert detail_response.status_code == 200
            data = detail_response.json()
            
            if "projection_results" in data and "detailed_expenses" in data["projection_results"]:
                expenses = data["projection_results"]["detailed_expenses"]
                
                # Should have multiple expense categories
                assert len(expenses) > 0
                
                # Check expense structure
                for expense in expenses:
                    assert "name" in expense
                    assert "annual_amount" in expense
                    assert "start_age" in expense
                    assert "inflation_adjusted" in expense
                    
                    # Amounts should be positive
                    assert expense["annual_amount"] > 0
                    assert expense["start_age"] > 0
                    
                    # End age should be greater than start age if present
                    if "end_age" in expense and expense["end_age"] is not None:
                        assert expense["end_age"] > expense["start_age"]


class TestAPIErrorHandling:
    """Test API error handling."""
    
    @pytest.mark.asyncio
    async def test_invalid_json(self, client):
        """Test API with invalid JSON."""
        response = await client.post(
            "/api/scenarios/generate",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422  # Unprocessable Entity
        
    @pytest.mark.asyncio
    async def test_empty_request_body(self, client):
        """Test API with empty request body."""
        response = await client.post("/api/scenarios/generate", json={})
        
        # Should handle empty body gracefully
        assert response.status_code in [200, 400, 422]
        
    @pytest.mark.asyncio
    async def test_method_not_allowed(self, client):
        """Test using wrong HTTP method."""
        response = await client.get("/api/scenarios/generate")  # Should be POST
        
        assert response.status_code == 405  # Method Not Allowed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])