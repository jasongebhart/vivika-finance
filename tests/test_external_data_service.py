"""
Tests for the External Data Service.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from services.external_data_service import ExternalDataService


@pytest.fixture
async def external_data_service():
    """Create an external data service instance."""
    service = ExternalDataService()
    yield service
    await service.close()


class TestExternalDataService:
    """Test cases for External Data Service."""

    @pytest.mark.asyncio
    async def test_get_city_cost_data(self, external_data_service):
        """Test fetching city cost data."""
        # Test expensive city
        sf_data = await external_data_service.get_city_cost_data("San Francisco, CA")
        
        assert sf_data is not None
        assert sf_data.city_name == "San Francisco, CA"
        assert sf_data.cost_index > 100  # Should be above national average
        assert sf_data.housing_cost > 0
        assert sf_data.utilities_cost > 0
        assert sf_data.grocery_cost > 0
        assert sf_data.transportation_cost > 0
        assert sf_data.healthcare_cost > 0
        assert sf_data.overall_cost_difference != 0

    @pytest.mark.asyncio
    async def test_city_cost_data_caching(self, external_data_service):
        """Test that city cost data is properly cached."""
        city_name = "New York, NY"
        
        # First call
        start_time = datetime.now()
        data1 = await external_data_service.get_city_cost_data(city_name)
        first_call_time = datetime.now() - start_time
        
        # Second call (should be cached)
        start_time = datetime.now()
        data2 = await external_data_service.get_city_cost_data(city_name)
        second_call_time = datetime.now() - start_time
        
        # Data should be identical
        assert data1.city_name == data2.city_name
        assert data1.cost_index == data2.cost_index
        assert data1.housing_cost == data2.housing_cost
        
        # Second call should be significantly faster (cached)
        assert second_call_time < first_call_time

    @pytest.mark.asyncio
    async def test_different_city_cost_levels(self, external_data_service):
        """Test that different cities return different cost levels."""
        # Test expensive city
        expensive_data = await external_data_service.get_city_cost_data("San Francisco, CA")
        
        # Test affordable city
        affordable_data = await external_data_service.get_city_cost_data("Austin, TX")
        
        # Test average city
        average_data = await external_data_service.get_city_cost_data("Unknown City")
        
        # Expensive city should have higher costs
        assert expensive_data.cost_index > affordable_data.cost_index
        assert expensive_data.housing_cost > affordable_data.housing_cost
        
        # Average city should be around 100 index
        assert average_data.cost_index == 100.0

    @pytest.mark.asyncio
    async def test_get_education_cost_data(self, external_data_service):
        """Test fetching education cost data."""
        costs = await external_data_service.get_education_cost_data("CA", "private_college")
        
        assert costs is not None
        assert "annual_tuition" in costs
        assert "annual_fees" in costs
        assert "room_board" in costs
        assert "books_supplies" in costs
        assert "transportation" in costs
        assert "personal_expenses" in costs
        
        # All costs should be positive
        for cost in costs.values():
            assert cost > 0

    @pytest.mark.asyncio
    async def test_education_cost_state_variations(self, external_data_service):
        """Test that education costs vary by state."""
        ca_costs = await external_data_service.get_education_cost_data("CA", "public_college_in_state")
        tx_costs = await external_data_service.get_education_cost_data("TX", "public_college_in_state")
        
        # California should be more expensive than Texas
        assert ca_costs["annual_tuition"] > tx_costs["annual_tuition"]

    @pytest.mark.asyncio
    async def test_education_cost_institution_types(self, external_data_service):
        """Test that different institution types have different costs."""
        public_costs = await external_data_service.get_education_cost_data("CA", "public_college_in_state")
        private_costs = await external_data_service.get_education_cost_data("CA", "private_college")
        
        # Private should be more expensive than public
        assert private_costs["annual_tuition"] > public_costs["annual_tuition"]

    @pytest.mark.asyncio
    async def test_get_vehicle_cost_data(self, external_data_service):
        """Test fetching vehicle cost data."""
        costs = await external_data_service.get_vehicle_cost_data("midsize", "west")
        
        assert costs is not None
        assert "purchase_price" in costs
        assert "annual_insurance" in costs
        assert "annual_maintenance" in costs
        assert "fuel_efficiency_mpg" in costs
        assert "regional_gas_price" in costs
        assert "depreciation_rate" in costs
        
        # All costs should be reasonable
        assert costs["purchase_price"] > 20000
        assert costs["annual_insurance"] > 500
        assert costs["fuel_efficiency_mpg"] > 15
        assert 0 < costs["depreciation_rate"] < 1

    @pytest.mark.asyncio
    async def test_vehicle_cost_regional_variations(self, external_data_service):
        """Test that vehicle costs vary by region."""
        west_costs = await external_data_service.get_vehicle_cost_data("midsize", "west")
        south_costs = await external_data_service.get_vehicle_cost_data("midsize", "south")
        
        # West should have higher insurance and gas costs
        assert west_costs["annual_insurance"] > south_costs["annual_insurance"]
        assert west_costs["regional_gas_price"] > south_costs["regional_gas_price"]

    @pytest.mark.asyncio
    async def test_vehicle_cost_type_variations(self, external_data_service):
        """Test that different vehicle types have different costs."""
        economy_costs = await external_data_service.get_vehicle_cost_data("economy", "midwest")
        luxury_costs = await external_data_service.get_vehicle_cost_data("luxury", "midwest")
        electric_costs = await external_data_service.get_vehicle_cost_data("electric", "midwest")
        
        # Luxury should be more expensive than economy
        assert luxury_costs["purchase_price"] > economy_costs["purchase_price"]
        assert luxury_costs["annual_insurance"] > economy_costs["annual_insurance"]
        
        # Electric should have better efficiency and lower maintenance
        assert electric_costs["fuel_efficiency_mpg"] > economy_costs["fuel_efficiency_mpg"]
        assert electric_costs["annual_maintenance"] < economy_costs["annual_maintenance"]

    @pytest.mark.asyncio
    async def test_get_inflation_data(self, external_data_service):
        """Test fetching inflation data."""
        inflation_data = await external_data_service.get_inflation_data()
        
        assert inflation_data is not None
        assert "current_cpi" in inflation_data
        assert "core_cpi" in inflation_data
        assert "pce" in inflation_data
        assert "housing_inflation" in inflation_data
        assert "education_inflation" in inflation_data
        assert "healthcare_inflation" in inflation_data
        assert "energy_inflation" in inflation_data
        
        # All inflation rates should be reasonable (between -10% and 20%)
        for rate in inflation_data.values():
            assert -10 < rate < 20

    @pytest.mark.asyncio
    async def test_get_market_data(self, external_data_service):
        """Test fetching market data."""
        market_data = await external_data_service.get_market_data()
        
        assert market_data is not None
        assert "sp500_return_ytd" in market_data
        assert "bond_yield_10yr" in market_data
        assert "volatility_index" in market_data
        assert "dollar_strength_index" in market_data
        assert "real_estate_index" in market_data
        
        # Market data should be reasonable
        assert -1 < market_data["sp500_return_ytd"] < 1  # -100% to +100%
        assert 0 < market_data["bond_yield_10yr"] < 0.20  # 0% to 20%
        assert 0 < market_data["volatility_index"] < 100
        assert 50 < market_data["dollar_strength_index"] < 150

    @pytest.mark.asyncio
    async def test_inflation_data_caching(self, external_data_service):
        """Test that inflation data is cached with shorter duration."""
        # First call
        data1 = await external_data_service.get_inflation_data()
        
        # Second call (should be cached)
        data2 = await external_data_service.get_inflation_data()
        
        # Data should be identical (cached)
        assert data1 == data2

    @pytest.mark.asyncio
    async def test_market_data_caching(self, external_data_service):
        """Test that market data is cached with hourly refresh."""
        # First call
        data1 = await external_data_service.get_market_data()
        
        # Second call (should be cached)
        data2 = await external_data_service.get_market_data()
        
        # Data should be identical (cached)
        assert data1 == data2

    @pytest.mark.asyncio
    async def test_cache_expiration(self, external_data_service):
        """Test cache expiration logic."""
        city_name = "Test City"
        
        # Get data
        original_data = await external_data_service.get_city_cost_data(city_name)
        
        # Manually expire the cache by modifying the timestamp
        cache_key = f"city_cost_{city_name.lower()}"
        if cache_key in external_data_service.cache:
            data, timestamp = external_data_service.cache[cache_key]
            # Set timestamp to 25 hours ago (past expiration)
            external_data_service.cache[cache_key] = (data, timestamp - timedelta(hours=25))
        
        # Get data again (should fetch fresh data)
        fresh_data = await external_data_service.get_city_cost_data(city_name)
        
        # Data should still be valid
        assert fresh_data.city_name == original_data.city_name

    @pytest.mark.asyncio
    async def test_default_fallback_data(self, external_data_service):
        """Test fallback to default data when API fails."""
        # Test with unknown city (should return default)
        unknown_data = await external_data_service.get_city_cost_data("Unknown City, ZZ")
        
        assert unknown_data.city_name == "Unknown City, ZZ"
        assert unknown_data.state == "Unknown"
        assert unknown_data.cost_index == 100.0  # National average

    @pytest.mark.asyncio
    async def test_service_cleanup(self, external_data_service):
        """Test that service can be properly closed."""
        # Service should close without errors
        await external_data_service.close()
        
        # Should be able to close multiple times
        await external_data_service.close()

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, external_data_service):
        """Test handling of concurrent requests."""
        # Make multiple concurrent requests
        tasks = [
            external_data_service.get_city_cost_data("New York, NY"),
            external_data_service.get_city_cost_data("Los Angeles, CA"),
            external_data_service.get_city_cost_data("Chicago, IL"),
            external_data_service.get_education_cost_data("CA", "public_college"),
            external_data_service.get_vehicle_cost_data("midsize", "west"),
            external_data_service.get_inflation_data(),
            external_data_service.get_market_data()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All requests should complete successfully
        for result in results:
            assert not isinstance(result, Exception)
            assert result is not None


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])