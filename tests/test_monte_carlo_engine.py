"""
Tests for the Monte Carlo Engine service.
"""

import pytest
import asyncio
from datetime import date
from models.financial_models import (
    UserProfile, ProjectionSettings, FinancialAssumptions, MonteCarloParameters,
    Asset, Liability, IncomeSource, Expense
)
from services.monte_carlo_engine import MonteCarloEngine


@pytest.fixture
def sample_user_profile():
    """Create a sample user profile for testing."""
    return UserProfile(
        name="Test User",
        birth_date="1985-01-01",
        current_age=38,
        retirement_age=65,
        life_expectancy=90,
        current_city="Test City",
        annual_salary=75000,
        assets=[
            Asset(
                name="401k",
                asset_type="retirement",
                current_value=150000,
                growth_rate=0.07
            ),
            Asset(
                name="Savings",
                asset_type="cash",
                current_value=25000,
                growth_rate=0.02
            )
        ],
        liabilities=[
            Liability(
                name="Mortgage",
                liability_type="mortgage",
                current_balance=250000,
                interest_rate=0.035,
                minimum_payment=1500
            )
        ],
        income_sources=[
            IncomeSource(
                name="Social Security",
                source_type="social_security",
                annual_amount=24000,
                start_age=67,
                growth_rate=0.02
            )
        ],
        expenses=[
            Expense(
                name="Living Expenses",
                category="living",
                annual_amount=48000,
                start_age=38,
                inflation_adjusted=True
            )
        ],
        retirement_accounts=[
            Asset(
                name="401k",
                asset_type="retirement",
                current_value=150000,
                growth_rate=0.07
            )
        ]
    )


@pytest.fixture
def sample_projection_settings():
    """Create sample projection settings for testing."""
    return ProjectionSettings(
        start_year=2024,
        projection_years=30,
        assumptions=FinancialAssumptions(
            inflation_rate=0.03,
            investment_return=0.07,
            salary_growth_rate=0.03,
            tax_rate=0.22
        ),
        monte_carlo=MonteCarloParameters(
            simulations=100,  # Reduced for testing speed
            return_std_dev=0.15,
            inflation_std_dev=0.01,
            salary_growth_std_dev=0.02,
            confidence_level=0.9
        )
    )


@pytest.fixture
def monte_carlo_engine():
    """Create a Monte Carlo engine instance."""
    return MonteCarloEngine()


class TestMonteCarloEngine:
    """Test cases for Monte Carlo Engine."""

    @pytest.mark.asyncio
    async def test_basic_simulation(self, monte_carlo_engine, sample_user_profile, sample_projection_settings):
        """Test basic Monte Carlo simulation functionality."""
        results = await monte_carlo_engine.run_simulation(
            sample_user_profile,
            sample_projection_settings
        )
        
        # Check basic result structure
        assert results is not None
        assert results.simulations_run == 100
        assert results.projection_years == 30
        assert 0 <= results.success_probability <= 1
        
        # Check statistical measures
        assert results.median_final_value > 0
        assert results.mean_final_value > 0
        assert results.std_dev_final_value >= 0
        
        # Check percentiles are ordered correctly
        assert results.worst_case_10th_percentile <= results.median_final_value
        assert results.median_final_value <= results.best_case_90th_percentile
        
        # Check annual projections
        assert len(results.annual_projections) == 30
        for projection in results.annual_projections:
            assert len(projection.simulation_results) == 100
            assert projection.year >= 2024

    @pytest.mark.asyncio
    async def test_simulation_with_progress_callback(self, monte_carlo_engine, sample_user_profile, sample_projection_settings):
        """Test simulation with progress callback."""
        progress_updates = []
        
        async def progress_callback(progress, message=""):
            progress_updates.append((progress, message))
        
        results = await monte_carlo_engine.run_simulation(
            sample_user_profile,
            sample_projection_settings,
            progress_callback
        )
        
        # Should have received progress updates
        assert len(progress_updates) > 0
        
        # Progress should be between 0 and 1
        for progress, _ in progress_updates:
            assert 0 <= progress <= 1
        
        # Should have final progress of 1.0
        final_progress, _ = progress_updates[-1]
        assert final_progress == 1.0

    @pytest.mark.asyncio
    async def test_retirement_success_calculation(self, monte_carlo_engine, sample_user_profile, sample_projection_settings):
        """Test retirement success probability calculation."""
        # Set a realistic retirement income target
        sample_projection_settings.retirement_income_target = 40000
        
        results = await monte_carlo_engine.run_simulation(
            sample_user_profile,
            sample_projection_settings
        )
        
        # Success probability should be reasonable given the parameters
        assert 0 <= results.success_probability <= 1
        
        # With reasonable assumptions, should have some success probability
        assert results.success_probability > 0

    @pytest.mark.asyncio
    async def test_different_simulation_counts(self, monte_carlo_engine, sample_user_profile, sample_projection_settings):
        """Test with different numbers of simulations."""
        # Test with small number of simulations
        sample_projection_settings.monte_carlo.simulations = 50
        
        results_50 = await monte_carlo_engine.run_simulation(
            sample_user_profile,
            sample_projection_settings
        )
        
        assert results_50.simulations_run == 50
        
        # Test with larger number
        sample_projection_settings.monte_carlo.simulations = 200
        
        results_200 = await monte_carlo_engine.run_simulation(
            sample_user_profile,
            sample_projection_settings
        )
        
        assert results_200.simulations_run == 200
        
        # Both should produce reasonable results
        assert results_50.median_final_value > 0
        assert results_200.median_final_value > 0

    @pytest.mark.asyncio
    async def test_varying_market_conditions(self, monte_carlo_engine, sample_user_profile, sample_projection_settings):
        """Test simulation under different market volatility conditions."""
        # Test with low volatility
        sample_projection_settings.monte_carlo.return_std_dev = 0.05
        
        results_low_vol = await monte_carlo_engine.run_simulation(
            sample_user_profile,
            sample_projection_settings
        )
        
        # Test with high volatility
        sample_projection_settings.monte_carlo.return_std_dev = 0.25
        
        results_high_vol = await monte_carlo_engine.run_simulation(
            sample_user_profile,
            sample_projection_settings
        )
        
        # High volatility should have higher standard deviation
        assert results_high_vol.std_dev_final_value > results_low_vol.std_dev_final_value

    @pytest.mark.asyncio
    async def test_withdrawal_strategies_analysis(self, monte_carlo_engine, sample_user_profile, sample_projection_settings):
        """Test withdrawal strategies analysis."""
        strategies = await monte_carlo_engine.analyze_withdrawal_strategies(
            sample_user_profile,
            sample_projection_settings
        )
        
        assert strategies is not None
        assert len(strategies.strategies) > 0
        
        # Each strategy should have required fields
        for strategy in strategies.strategies:
            assert strategy.name is not None
            assert strategy.description is not None
            assert 0 <= strategy.success_rate <= 1
            assert strategy.median_final_value >= 0
            assert strategy.worst_case_10th_percentile >= 0

    @pytest.mark.asyncio
    async def test_early_retirement_scenario(self, monte_carlo_engine, sample_user_profile, sample_projection_settings):
        """Test Monte Carlo simulation for early retirement scenario."""
        # Set early retirement age
        sample_user_profile.retirement_age = 55
        sample_projection_settings.projection_years = 35  # Longer projection period
        
        results = await monte_carlo_engine.run_simulation(
            sample_user_profile,
            sample_projection_settings
        )
        
        # Should handle early retirement scenario
        assert results.projection_years == 35
        assert len(results.annual_projections) == 35
        
        # Results should be reasonable for early retirement
        assert results.median_final_value > 0

    @pytest.mark.asyncio
    async def test_statistical_accuracy(self, monte_carlo_engine, sample_user_profile, sample_projection_settings):
        """Test statistical accuracy of Monte Carlo results."""
        # Use more simulations for better statistical accuracy
        sample_projection_settings.monte_carlo.simulations = 500
        
        results = await monte_carlo_engine.run_simulation(
            sample_user_profile,
            sample_projection_settings
        )
        
        # Check that final year distribution exists and is reasonable
        final_year = results.annual_projections[-1]
        final_values = [sim.net_worth for sim in final_year.simulation_results]
        
        # Should have correct number of simulation results
        assert len(final_values) == 500
        
        # Statistical measures should be consistent
        import statistics
        calculated_median = statistics.median(final_values)
        calculated_mean = statistics.mean(final_values)
        
        # Allow for some rounding differences
        assert abs(calculated_median - results.median_final_value) < results.median_final_value * 0.01
        assert abs(calculated_mean - results.mean_final_value) < results.mean_final_value * 0.01

    @pytest.mark.asyncio
    async def test_edge_case_scenarios(self, monte_carlo_engine, sample_user_profile, sample_projection_settings):
        """Test edge case scenarios."""
        # Test with very high expenses (should impact success rate)
        high_expense_profile = sample_user_profile.copy(deep=True)
        high_expense_profile.expenses = [
            Expense(
                name="High Living Expenses",
                category="living",
                annual_amount=100000,  # Very high expenses
                start_age=38,
                inflation_adjusted=True
            )
        ]
        
        results = await monte_carlo_engine.run_simulation(
            high_expense_profile,
            sample_projection_settings
        )
        
        # Should still complete simulation
        assert results is not None
        assert results.simulations_run == sample_projection_settings.monte_carlo.simulations

    @pytest.mark.asyncio
    async def test_confidence_levels(self, monte_carlo_engine, sample_user_profile, sample_projection_settings):
        """Test different confidence levels."""
        # Test 80% confidence
        sample_projection_settings.monte_carlo.confidence_level = 0.8
        
        results_80 = await monte_carlo_engine.run_simulation(
            sample_user_profile,
            sample_projection_settings
        )
        
        # Test 95% confidence
        sample_projection_settings.monte_carlo.confidence_level = 0.95
        
        results_95 = await monte_carlo_engine.run_simulation(
            sample_user_profile,
            sample_projection_settings
        )
        
        # Both should complete successfully
        assert results_80 is not None
        assert results_95 is not None
        
        # Wider confidence interval should have lower worst case
        assert results_95.worst_case_10th_percentile <= results_80.worst_case_10th_percentile

    @pytest.mark.asyncio
    async def test_simulation_determinism(self, monte_carlo_engine, sample_user_profile, sample_projection_settings):
        """Test that simulations can be made deterministic for testing."""
        # Note: This test assumes we can set a random seed in the future
        # For now, just test that two runs produce similar statistical results
        
        results1 = await monte_carlo_engine.run_simulation(
            sample_user_profile,
            sample_projection_settings
        )
        
        results2 = await monte_carlo_engine.run_simulation(
            sample_user_profile,
            sample_projection_settings
        )
        
        # Results should be similar (within reasonable variance)
        variance_threshold = 0.1  # 10% variance acceptable
        median_diff = abs(results1.median_final_value - results2.median_final_value)
        assert median_diff < results1.median_final_value * variance_threshold


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])