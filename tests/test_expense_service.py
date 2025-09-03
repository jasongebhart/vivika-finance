"""
Tests for the ExpenseService - enhanced expense management with detailed line items.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from services.expense_service import ExpenseService


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
        "KIDS_ACTIVITIES": {
            "SPORTS": {
                "SKI_TEAM": {
                    "team_fee": 400,
                    "equipment": 300,
                    "clothing": 150
                },
                "BASEBALL": {
                    "team_fee_summer": 150,
                    "equipment": 80
                }
            }
        },
        "EXCLUDED_EXPENSES": []
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
def expense_service(temp_config_file):
    """Create an ExpenseService instance for testing."""
    return ExpenseService(temp_config_file)


class TestExpenseServiceInit:
    """Test service initialization."""
    
    def test_init_with_valid_config(self, expense_service):
        """Test that service initializes properly with valid config."""
        assert expense_service is not None
        assert expense_service._expense_config is not None
        assert len(expense_service.location_multipliers) == 3  # Sf, Sd, Mn
        
    def test_location_multipliers_defined(self, expense_service):
        """Test that location multipliers are properly defined."""
        multipliers = expense_service.location_multipliers
        assert 'Sf' in multipliers
        assert 'Sd' in multipliers
        assert 'Mn' in multipliers
        
        # Each location should have all required multiplier keys
        for location in multipliers:
            assert 'living' in multipliers[location]
            assert 'housing' in multipliers[location]
            assert 'utilities' in multipliers[location]
            assert 'transport' in multipliers[location]
            assert 'insurance' in multipliers[location]
            assert 'leisure' in multipliers[location]


class TestGetExpenseConfig:
    """Test expense configuration retrieval."""
    
    def test_get_expense_config_basic(self, expense_service):
        """Test basic expense config retrieval."""
        config = expense_service.get_expense_config()
        
        assert isinstance(config, dict)
        assert 'UTILITIES' in config
        assert 'INSURANCE' in config
        assert 'TRANSPORTATION' in config
        assert 'LIVING_EXPENSES' in config
        
    def test_utilities_structure(self, expense_service):
        """Test utilities expense structure."""
        config = expense_service.get_expense_config()
        utilities = config['UTILITIES']
        
        expected_utilities = ['electricity', 'gas', 'water', 'internet', 'trash', 'sewer']
        for utility in expected_utilities:
            assert utility in utilities
            assert isinstance(utilities[utility], (int, float))
            assert utilities[utility] > 0


class TestLocationAdjustments:
    """Test location-based expense adjustments."""
    
    def test_sf_higher_costs(self, expense_service):
        """Test that San Francisco has higher costs."""
        base_config = expense_service.get_expense_config()
        sf_config = expense_service.get_location_adjusted_expenses('Sf')
        
        # Compare utilities (should be higher in SF)
        base_electricity = base_config['UTILITIES']['electricity']
        sf_electricity = sf_config['UTILITIES']['electricity']
        
        assert sf_electricity > base_electricity
        
    def test_mn_lower_costs(self, expense_service):
        """Test that Minnesota has lower costs."""
        base_config = expense_service.get_expense_config()
        mn_config = expense_service.get_location_adjusted_expenses('Mn')
        
        # Compare utilities (should be lower in MN)
        base_electricity = base_config['UTILITIES']['electricity']
        mn_electricity = mn_config['UTILITIES']['electricity']
        
        assert mn_electricity < base_electricity
        
    def test_location_adjustment_preserves_structure(self, expense_service):
        """Test that location adjustment preserves config structure."""
        base_config = expense_service.get_expense_config()
        sf_config = expense_service.get_location_adjusted_expenses('Sf')
        
        # Should have same top-level keys
        assert set(base_config.keys()) == set(sf_config.keys())
        
        # Should have same utility types
        assert set(base_config['UTILITIES'].keys()) == set(sf_config['UTILITIES'].keys())


class TestDetailedExpenseBreakdown:
    """Test detailed expense breakdown functionality."""
    
    def test_get_detailed_breakdown(self, expense_service):
        """Test getting detailed expense breakdown."""
        breakdown = expense_service.get_detailed_breakdown('Mn')
        
        assert isinstance(breakdown, list)
        assert len(breakdown) > 0
        
        # Check structure of expense items
        for expense in breakdown:
            assert 'name' in expense
            assert 'annual_amount' in expense
            assert 'category' in expense
            assert 'line_items' in expense
            assert expense['annual_amount'] > 0
            
    def test_breakdown_includes_major_categories(self, expense_service):
        """Test that breakdown includes all major expense categories."""
        breakdown = expense_service.get_detailed_breakdown('Mn')
        
        expense_names = [expense['name'] for expense in breakdown]
        
        # Should include major categories
        assert any('Utilities' in name for name in expense_names)
        assert any('Insurance' in name for name in expense_names)
        assert any('Transportation' in name for name in expense_names)
        assert any('Living' in name for name in expense_names)
        
    def test_line_items_sum_to_total(self, expense_service):
        """Test that line items sum approximately to the total amount."""
        breakdown = expense_service.get_detailed_breakdown('Mn')
        
        utilities = next((e for e in breakdown if 'Utilities' in e['name']), None)
        assert utilities is not None
        
        line_items_total = sum(utilities['line_items'].values()) * 12  # Monthly to annual
        annual_amount = utilities['annual_amount']
        
        # Should be approximately equal (within 10% due to rounding)
        assert abs(line_items_total - annual_amount) / annual_amount < 0.1


class TestExpenseFiltering:
    """Test expense filtering and exclusions."""
    
    def test_excluded_expenses_not_included(self, temp_config_file):
        """Test that excluded expenses are not included in breakdown."""
        # Modify config to exclude utilities
        with open(temp_config_file, 'r') as f:
            config = json.load(f)
        
        config['EXCLUDED_EXPENSES'] = ['UTILITIES']
        
        with open(temp_config_file, 'w') as f:
            json.dump(config, f)
        
        service = ExpenseService(temp_config_file)
        breakdown = service.get_detailed_breakdown('Mn')
        
        expense_names = [expense['name'] for expense in breakdown]
        assert not any('Utilities' in name for name in expense_names)


class TestExpenseCategorization:
    """Test expense categorization functionality."""
    
    def test_get_expenses_by_category(self, expense_service):
        """Test getting expenses grouped by category."""
        categorized = expense_service.get_expenses_by_category('Mn')
        
        assert isinstance(categorized, dict)
        assert len(categorized) > 0
        
        # Should have common categories
        expected_categories = ['Housing', 'Transportation', 'Insurance', 'Recreation']
        for category in expected_categories:
            if category in categorized:  # Some might not exist based on config
                assert isinstance(categorized[category], list)
                assert len(categorized[category]) > 0
                
    def test_category_totals(self, expense_service):
        """Test calculating category totals."""
        totals = expense_service.get_category_totals('Mn')
        
        assert isinstance(totals, dict)
        assert len(totals) > 0
        
        for category, total in totals.items():
            assert isinstance(total, (int, float))
            assert total > 0


class TestExpenseProjections:
    """Test expense projections over time."""
    
    def test_project_expenses_over_time(self, expense_service):
        """Test projecting expenses over multiple years."""
        projections = expense_service.project_expenses_over_time(
            location='Mn',
            years=5,
            inflation_rate=0.03
        )
        
        assert isinstance(projections, list)
        assert len(projections) == 5
        
        # Each year should have proper structure
        for year_data in projections:
            assert 'year' in year_data
            assert 'total_expenses' in year_data
            assert 'categories' in year_data
            assert year_data['total_expenses'] > 0
            
        # Total expenses should increase with inflation
        year1_total = projections[0]['total_expenses']
        year5_total = projections[4]['total_expenses']
        assert year5_total > year1_total
        
    def test_inflation_adjustment(self, expense_service):
        """Test that inflation is properly applied."""
        # Project with different inflation rates
        low_inflation = expense_service.project_expenses_over_time('Mn', 5, 0.02)
        high_inflation = expense_service.project_expenses_over_time('Mn', 5, 0.05)
        
        # Year 5 totals should reflect inflation differences
        low_year5 = low_inflation[4]['total_expenses']
        high_year5 = high_inflation[4]['total_expenses']
        
        assert high_year5 > low_year5


class TestExpenseAnalytics:
    """Test expense analytics and insights."""
    
    def test_get_expense_insights(self, expense_service):
        """Test getting expense insights."""
        insights = expense_service.get_expense_insights('Mn')
        
        assert isinstance(insights, dict)
        assert 'total_annual_expenses' in insights
        assert 'largest_category' in insights
        assert 'monthly_average' in insights
        
        assert insights['total_annual_expenses'] > 0
        assert insights['monthly_average'] > 0
        
    def test_compare_locations(self, expense_service):
        """Test comparing expenses across locations."""
        comparison = expense_service.compare_locations(['Sf', 'Mn'])
        
        assert isinstance(comparison, dict)
        assert 'Sf' in comparison
        assert 'Mn' in comparison
        
        # SF should generally be more expensive than MN
        sf_total = comparison['Sf']['total_annual_expenses']
        mn_total = comparison['Mn']['total_annual_expenses']
        assert sf_total > mn_total


if __name__ == "__main__":
    pytest.main([__file__, "-v"])