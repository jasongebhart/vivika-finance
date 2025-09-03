"""
Pytest configuration and fixtures for the Long-Term Financial Planning Application.
"""

import pytest
import asyncio
import tempfile
import os
from typing import AsyncGenerator

# Configure pytest to handle async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def temp_database() -> AsyncGenerator[str, None]:
    """Create a temporary database file for testing."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_file.close()
    
    yield temp_file.name
    
    # Cleanup
    try:
        os.unlink(temp_file.name)
    except FileNotFoundError:
        pass


@pytest.fixture
def mock_external_api_responses():
    """Mock responses for external API calls."""
    return {
        'city_data': {
            'San Francisco, CA': {
                'city_name': 'San Francisco, CA',
                'state': 'CA',
                'cost_index': 180.0,
                'housing_cost': 4500.0,
                'utilities_cost': 250.0,
                'grocery_cost': 450.0,
                'transportation_cost': 200.0,
                'healthcare_cost': 350.0,
                'overall_cost_difference': 0.8
            },
            'Austin, TX': {
                'city_name': 'Austin, TX',
                'state': 'TX',
                'cost_index': 110.0,
                'housing_cost': 1800.0,
                'utilities_cost': 150.0,
                'grocery_cost': 320.0,
                'transportation_cost': 120.0,
                'healthcare_cost': 220.0,
                'overall_cost_difference': 0.1
            }
        },
        'education_data': {
            ('CA', 'public_college'): {
                'annual_tuition': 36400,
                'annual_fees': 3640,
                'room_board': 19500,
                'books_supplies': 1560,
                'transportation': 1000,
                'personal_expenses': 2000
            },
            ('TX', 'public_college'): {
                'annual_tuition': 25200,
                'annual_fees': 2520,
                'room_board': 13500,
                'books_supplies': 1080,
                'transportation': 1000,
                'personal_expenses': 2000
            }
        },
        'vehicle_data': {
            ('economy', 'west'): {
                'purchase_price': 25000,
                'annual_insurance': 1440,
                'annual_maintenance': 800,
                'fuel_efficiency_mpg': 30,
                'regional_gas_price': 4.03,
                'depreciation_rate': 0.15
            },
            ('luxury', 'west'): {
                'purchase_price': 55000,
                'annual_insurance': 2600,
                'annual_maintenance': 1500,
                'fuel_efficiency_mpg': 22,
                'regional_gas_price': 4.03,
                'depreciation_rate': 0.15
            }
        },
        'inflation_data': {
            'current_cpi': 3.2,
            'core_cpi': 2.8,
            'pce': 2.9,
            'housing_inflation': 4.1,
            'education_inflation': 5.2,
            'healthcare_inflation': 3.8,
            'energy_inflation': 8.5
        },
        'market_data': {
            'sp500_return_ytd': 0.12,
            'bond_yield_10yr': 0.045,
            'volatility_index': 18.5,
            'dollar_strength_index': 102.3,
            'real_estate_index': 0.085
        }
    }


# Custom pytest markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "monte_carlo: marks tests that run Monte Carlo simulations"
    )


# Test data fixtures
@pytest.fixture
def sample_financial_assumptions():
    """Standard financial assumptions for testing."""
    from models.financial_models import FinancialAssumptions
    
    return FinancialAssumptions(
        inflation_rate=0.03,
        investment_return=0.07,
        salary_growth_rate=0.03,
        tax_rate=0.22
    )


@pytest.fixture
def sample_monte_carlo_parameters():
    """Standard Monte Carlo parameters for testing."""
    from models.financial_models import MonteCarloParameters
    
    return MonteCarloParameters(
        simulations=100,  # Reduced for testing speed
        return_std_dev=0.15,
        inflation_std_dev=0.01,
        salary_growth_std_dev=0.02,
        confidence_level=0.9
    )


@pytest.fixture
def sample_assets():
    """Standard assets for testing."""
    from models.financial_models import Asset
    
    return [
        Asset(
            name="Savings Account",
            asset_type="cash",
            current_value=25000,
            growth_rate=0.02
        ),
        Asset(
            name="401k",
            asset_type="retirement",
            current_value=150000,
            growth_rate=0.07
        ),
        Asset(
            name="Roth IRA",
            asset_type="retirement",
            current_value=75000,
            growth_rate=0.08
        )
    ]


@pytest.fixture
def sample_liabilities():
    """Standard liabilities for testing."""
    from models.financial_models import Liability
    
    return [
        Liability(
            name="Mortgage",
            liability_type="mortgage",
            current_balance=250000,
            interest_rate=0.035,
            minimum_payment=1500
        ),
        Liability(
            name="Car Loan",
            liability_type="auto",
            current_balance=25000,
            interest_rate=0.045,
            minimum_payment=450
        )
    ]


@pytest.fixture
def sample_income_sources():
    """Standard income sources for testing."""
    from models.financial_models import IncomeSource
    
    return [
        IncomeSource(
            name="Social Security",
            source_type="social_security",
            annual_amount=24000,
            start_age=67,
            growth_rate=0.02
        ),
        IncomeSource(
            name="Pension",
            source_type="pension",
            annual_amount=18000,
            start_age=65,
            growth_rate=0.01
        )
    ]


@pytest.fixture
def sample_expenses():
    """Standard expenses for testing."""
    from models.financial_models import Expense
    
    return [
        Expense(
            name="Housing",
            category="housing",
            annual_amount=36000,
            start_age=38,
            inflation_adjusted=True
        ),
        Expense(
            name="Food",
            category="food",
            annual_amount=12000,
            start_age=38,
            inflation_adjusted=True
        ),
        Expense(
            name="Transportation",
            category="transportation",
            annual_amount=8000,
            start_age=38,
            inflation_adjusted=True
        ),
        Expense(
            name="Healthcare",
            category="healthcare",
            annual_amount=6000,
            start_age=38,
            inflation_adjusted=True
        )
    ]


# Performance testing utilities
@pytest.fixture
def performance_timer():
    """Utility for timing test operations."""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        @property
        def elapsed(self):
            if self.start_time is None or self.end_time is None:
                return None
            return self.end_time - self.start_time
    
    return Timer()


# Database testing utilities
@pytest.fixture
async def test_scenario_manager(temp_database):
    """Create a ScenarioManager instance with a temporary database."""
    from services.scenario_manager import ScenarioManager
    
    manager = ScenarioManager(db_path=temp_database)
    await manager.initialize_database()
    return manager


# Mock service utilities
@pytest.fixture
def mock_monte_carlo_engine():
    """Create a mock Monte Carlo engine for testing."""
    from unittest.mock import AsyncMock
    from models.financial_models import MonteCarloResult, MonteCarloProjectionYear, SimulationResult
    
    mock_engine = AsyncMock()
    
    # Mock successful simulation result
    mock_result = MonteCarloResult(
        simulations_run=100,
        projection_years=30,
        success_probability=0.85,
        median_final_value=750000,
        mean_final_value=800000,
        std_dev_final_value=200000,
        worst_case_10th_percentile=400000,
        best_case_90th_percentile=1200000,
        annual_projections=[
            MonteCarloProjectionYear(
                year=2024,
                simulation_results=[
                    SimulationResult(
                        net_worth=100000,
                        portfolio_value=80000,
                        annual_income=75000,
                        withdrawal_rate=0.0
                    )
                ]
            )
        ],
        final_year_distribution={
            'net_worth': [400000, 500000, 600000, 700000, 800000, 900000, 1000000, 1100000, 1200000]
        }
    )
    
    mock_engine.run_simulation.return_value = mock_result
    return mock_engine


# Test data validation utilities
def validate_projection_data(projection):
    """Validate that projection data is reasonable."""
    assert projection is not None
    assert len(projection.yearly_projections) > 0
    
    for year_proj in projection.yearly_projections:
        assert year_proj.year > 2020
        assert year_proj.age > 0
        assert year_proj.beginning_assets >= 0
        assert year_proj.ending_assets >= 0


def validate_monte_carlo_results(results):
    """Validate that Monte Carlo results are reasonable."""
    assert results is not None
    assert results.simulations_run > 0
    assert 0 <= results.success_probability <= 1
    assert results.median_final_value >= 0
    assert results.mean_final_value >= 0
    assert results.std_dev_final_value >= 0
    assert len(results.annual_projections) > 0