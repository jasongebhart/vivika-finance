"""
Tests for the DynamicFinancialService - the core service that generates
realistic financial scenarios based on dynamic parameters.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from services.dynamic_financial_service import DynamicFinancialService


@pytest.fixture
def sample_config():
    """Create a sample configuration for testing."""
    return {
        "UTILITIES": {
            "electricity": 180,
            "gas": 120,
            "water": 65,
            "internet": 85,
            "trash": 45,
            "sewer": 55
        },
        "INSURANCE": {
            "health": 850,
            "auto": 180,
            "home": 140,
            "life": 65,
            "umbrella": 45
        },
        "TRANSPORTATION": {
            "car_payment": 450,
            "gas": 280,
            "maintenance": 150,
            "registration": 25,
            "parking": 120
        },
        "LIVING_EXPENSES": {
            "groceries": 800,
            "clothing": 300,
            "personal_care": 150,
            "household_supplies": 100,
            "medical": 200
        },
        "HOUSING_EXPENSES": {
            "house_maintenance": 250,
            "monthly_rent": 0,
            "property_tax": 450,
            "hoa_fees": 85
        },
        "KIDS_ACTIVITIES": {
            "SPORTS": {
                "SKI_TEAM": {
                    "team_fee": 400,
                    "equipment": 300,
                    "clothing": 150,
                    "lift_passes": 500,
                    "gas": 100,
                    "travel_housing": 476.75
                },
                "BASEBALL": {
                    "team_fee_summer": 150,
                    "team_fee_fall": 100,
                    "equipment": 80,
                    "uniforms": 40,
                    "tournament_fees": 60,
                    "travel": 50,
                    "gas": 3.33
                }
            }
        },
        "house": {
            "value": 3600000,
            "annual_property_tax": 36599.26
        }
    }


@pytest.fixture
def temp_config_file(sample_config):
    """Create a temporary config file for testing."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(sample_config, temp_file)
    temp_file.close()
    yield temp_file.name
    os.unlink(temp_file.name)


@pytest.fixture
def service(temp_config_file):
    """Create a DynamicFinancialService instance for testing."""
    return DynamicFinancialService(temp_config_file)


class TestDynamicFinancialServiceInit:
    """Test service initialization."""
    
    def test_init_with_valid_config(self, service):
        """Test that service initializes properly with valid config."""
        assert service is not None
        assert service.base_financial_data is not None
        assert len(service.location_multipliers) == 3  # Sf, Sd, Mn
        
    def test_init_with_missing_config(self):
        """Test initialization with missing config file."""
        service = DynamicFinancialService("nonexistent.json")
        assert service.base_financial_data == {}


class TestLocationMultipliers:
    """Test location-based cost adjustments."""
    
    def test_san_francisco_multipliers(self, service):
        """Test San Francisco has higher cost multipliers."""
        sf_multipliers = service.location_multipliers['Sf']
        assert sf_multipliers['housing_cost'] > 1.0  # Higher than baseline
        assert sf_multipliers['general_expenses'] > 1.0
        assert sf_multipliers['salary_adjustment'] > 1.0
        
    def test_minnesota_multipliers(self, service):
        """Test Minnesota has lower cost multipliers."""
        mn_multipliers = service.location_multipliers['Mn']
        assert mn_multipliers['housing_cost'] < 1.0  # Lower than baseline
        assert mn_multipliers['general_expenses'] < 1.0
        assert mn_multipliers['salary_adjustment'] < 1.0
        
    def test_san_diego_middle_multipliers(self, service):
        """Test San Diego has middle-range multipliers."""
        sd_multipliers = service.location_multipliers['Sd']
        sf_multipliers = service.location_multipliers['Sf']
        mn_multipliers = service.location_multipliers['Mn']
        
        # San Diego should be between SF and MN
        assert mn_multipliers['housing_cost'] < sd_multipliers['housing_cost'] < sf_multipliers['housing_cost']


class TestScenarioGeneration:
    """Test complete scenario data generation."""
    
    def test_basic_scenario_structure(self, service):
        """Test that generated scenario has proper structure."""
        parameters = {
            'location': 'Mn',
            'spouse1Status': 'Work',
            'spouse2Status': 'Work',
            'housing': 'Own',
            'schoolType': 'Public',
            'projectionYears': 8
        }
        
        scenario = service.generate_scenario_data(parameters)
        
        # Check top-level structure
        assert 'user_data' in scenario
        assert 'projection_data' in scenario
        
        user_data = scenario['user_data']
        assert 'name' in user_data
        assert 'current_age' in user_data
        assert 'retirement_age' in user_data
        assert 'annual_salary' in user_data
        assert 'current_city' in user_data
        assert 'expenses' in user_data
        assert 'assets' in user_data
        
    def test_location_affects_expenses(self, service):
        """Test that different locations produce different expense amounts."""
        base_params = {
            'spouse1Status': 'Work',
            'spouse2Status': 'Work', 
            'housing': 'Own',
            'schoolType': 'Public',
            'projectionYears': 8
        }
        
        sf_scenario = service.generate_scenario_data({**base_params, 'location': 'Sf'})
        mn_scenario = service.generate_scenario_data({**base_params, 'location': 'Mn'})
        
        # Find utilities expense in both scenarios
        sf_utilities = next((e for e in sf_scenario['user_data']['expenses'] if e['name'] == 'Utilities'), None)
        mn_utilities = next((e for e in mn_scenario['user_data']['expenses'] if e['name'] == 'Utilities'), None)
        
        assert sf_utilities is not None
        assert mn_utilities is not None
        # SF should have higher utilities cost than MN
        assert sf_utilities['annual_amount'] > mn_utilities['annual_amount']
        
    def test_school_type_affects_education_costs(self, service):
        """Test that school type affects education expenses."""
        base_params = {
            'location': 'Mn',
            'spouse1Status': 'Work',
            'spouse2Status': 'Work',
            'housing': 'Own',
            'projectionYears': 8
        }
        
        public_scenario = service.generate_scenario_data({**base_params, 'schoolType': 'Public'})
        private_scenario = service.generate_scenario_data({**base_params, 'schoolType': 'Private'})
        
        # Public school should have fewer/cheaper education expenses
        public_edu_expenses = [e for e in public_scenario['user_data']['expenses'] if 'College' in e['name']]
        private_edu_expenses = [e for e in private_scenario['user_data']['expenses'] if 'College' in e['name'] or 'High School' in e['name']]
        
        # Private should have more education-related expenses
        assert len(private_edu_expenses) >= len(public_edu_expenses)


class TestEducationExpenseTiming:
    """Test that education expenses use realistic kid ages."""
    
    def test_college_timing_realistic(self, service):
        """Test that college expenses occur at realistic parent ages."""
        parameters = {
            'location': 'Mn',
            'spouse1Status': 'Work',
            'spouse2Status': 'Work',
            'housing': 'Own',
            'schoolType': 'Private',
            'projectionYears': 8
        }
        
        scenario = service.generate_scenario_data(parameters)
        
        # Find college expenses
        tate_college = next((e for e in scenario['user_data']['expenses'] if e['name'] == 'Tate College'), None)
        wynn_college = next((e for e in scenario['user_data']['expenses'] if e['name'] == 'Wynn College'), None)
        
        assert tate_college is not None
        assert wynn_college is not None
        
        # Check realistic timing (Tate older than Wynn)
        assert tate_college['start_age'] < wynn_college['start_age']  # Tate starts college first
        
        # College should start in parent's 55+ age range (when kids are ~18)
        assert tate_college['start_age'] >= 55
        assert wynn_college['start_age'] >= 55
        
        # College should last 4 years
        assert tate_college['end_age'] - tate_college['start_age'] == 4
        assert wynn_college['end_age'] - wynn_college['start_age'] == 4
        
    def test_high_school_timing_realistic(self, service):
        """Test that high school expenses occur at realistic ages."""
        parameters = {
            'location': 'Mn',
            'spouse1Status': 'Work',
            'spouse2Status': 'Work',
            'housing': 'Own',
            'schoolType': 'Private',
            'projectionYears': 8
        }
        
        scenario = service.generate_scenario_data(parameters)
        
        # Find high school expenses
        tate_hs = next((e for e in scenario['user_data']['expenses'] if e['name'] == 'Tate High School'), None)
        wynn_hs = next((e for e in scenario['user_data']['expenses'] if e['name'] == 'Wynn High School'), None)
        
        if tate_hs and wynn_hs:  # Only test if high school expenses exist
            # Tate should start high school before or at the same time as Wynn
            assert tate_hs['start_age'] <= wynn_hs['start_age']
            # And high school should be reasonable duration (2-4 years)
            assert 2 <= (tate_hs['end_age'] - tate_hs['start_age']) <= 4
            assert 2 <= (wynn_hs['end_age'] - wynn_hs['start_age']) <= 4


class TestKidsActivitiesTiming:
    """Test that kids activities have realistic timing."""
    
    def test_activities_timing_makes_sense(self, service):
        """Test that kids activities have logical start/end ages."""
        parameters = {
            'location': 'Mn',
            'spouse1Status': 'Work',
            'spouse2Status': 'Work',
            'housing': 'Own',
            'schoolType': 'Public',
            'projectionYears': 8
        }
        
        scenario = service.generate_scenario_data(parameters)
        
        # Find kids activities
        baseball = next((e for e in scenario['user_data']['expenses'] if e['name'] == 'Baseball Activities'), None)
        ski_team = next((e for e in scenario['user_data']['expenses'] if e['name'] == 'Ski Team Activities'), None)
        
        if baseball:
            assert baseball['start_age'] < baseball['end_age']  # End age should be after start age
            assert baseball['end_age'] <= 65  # Should end before retirement
            
        if ski_team:
            assert ski_team['start_age'] < ski_team['end_age']
            assert ski_team['end_age'] <= 65


class TestExpenseLineItems:
    """Test that expense line items are properly generated."""
    
    def test_utilities_has_line_items(self, service):
        """Test that utilities expense includes detailed line items."""
        parameters = {
            'location': 'Mn',
            'spouse1Status': 'Work',
            'spouse2Status': 'Work',
            'housing': 'Own',
            'schoolType': 'Public',
            'projectionYears': 8
        }
        
        scenario = service.generate_scenario_data(parameters)
        
        utilities = next((e for e in scenario['user_data']['expenses'] if e['name'] == 'Utilities'), None)
        assert utilities is not None
        assert 'line_items' in utilities
        
        line_items = utilities['line_items']
        expected_items = ['electricity', 'gas', 'water', 'internet', 'trash', 'sewer']
        
        for item in expected_items:
            assert item in line_items
            assert line_items[item] > 0  # Should have positive values
            
    def test_line_items_affected_by_location(self, service):
        """Test that line items are adjusted based on location."""
        base_params = {
            'spouse1Status': 'Work',
            'spouse2Status': 'Work',
            'housing': 'Own',
            'schoolType': 'Public',
            'projectionYears': 8
        }
        
        sf_scenario = service.generate_scenario_data({**base_params, 'location': 'Sf'})
        mn_scenario = service.generate_scenario_data({**base_params, 'location': 'Mn'})
        
        sf_utilities = next((e for e in sf_scenario['user_data']['expenses'] if e['name'] == 'Utilities'), None)
        mn_utilities = next((e for e in mn_scenario['user_data']['expenses'] if e['name'] == 'Utilities'), None)
        
        # Compare electricity costs
        sf_electricity = sf_utilities['line_items']['electricity']
        mn_electricity = mn_utilities['line_items']['electricity']
        
        # SF should have higher electricity cost than MN
        assert sf_electricity > mn_electricity


class TestAssetsGeneration:
    """Test asset generation and allocation."""
    
    def test_assets_structure(self, service):
        """Test that assets are properly structured."""
        parameters = {
            'location': 'Mn',
            'spouse1Status': 'Work',
            'spouse2Status': 'Work',
            'housing': 'Own',
            'schoolType': 'Public',
            'projectionYears': 8
        }
        
        scenario = service.generate_scenario_data(parameters)
        
        assert 'assets' in scenario['user_data']
        assert len(scenario['user_data']['assets']) > 0
        
        # Check asset structure
        for asset in scenario['user_data']['assets']:
            assert 'name' in asset
            assert 'asset_type' in asset
            assert 'current_value' in asset
            assert 'expected_return' in asset
            assert asset['current_value'] > 0
            assert 0 < asset['expected_return'] < 1  # Should be a percentage
            
    def test_total_asset_value_reasonable(self, service):
        """Test that total asset value is reasonable."""
        parameters = {
            'location': 'Mn',
            'spouse1Status': 'Work',
            'spouse2Status': 'Work',
            'housing': 'Own',
            'schoolType': 'Public',
            'projectionYears': 8
        }
        
        scenario = service.generate_scenario_data(parameters)
        
        total_assets = sum(asset['current_value'] for asset in scenario['user_data']['assets'])
        
        # Should have substantial assets (> $1M for this scenario)
        assert total_assets > 1000000
        # But not unreasonably high (< $10M)
        assert total_assets < 10000000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])