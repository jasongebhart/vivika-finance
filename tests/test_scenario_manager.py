"""
Tests for the ScenarioManager service.
"""

import pytest
import asyncio
import tempfile
import os
from datetime import date, datetime
from models.financial_models import (
    ScenarioInput, UserProfile, ProjectionSettings, FinancialAssumptions,
    ScenarioType, Asset, Liability, IncomeSource, Expense
)
from services.scenario_manager import ScenarioManager


@pytest.fixture
async def temp_db():
    """Create a temporary database for testing."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_file.close()
    
    manager = ScenarioManager(db_path=temp_file.name)
    await manager.initialize_database()
    
    yield manager
    
    # Cleanup
    os.unlink(temp_file.name)


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
        )
    )


@pytest.fixture
def sample_scenario_input(sample_user_profile, sample_projection_settings):
    """Create a sample scenario input for testing."""
    return ScenarioInput(
        name="Test Retirement Scenario",
        description="Testing retirement planning scenario",
        scenario_type=ScenarioType.retirement,
        user_profile=sample_user_profile,
        projection_settings=sample_projection_settings,
        retirement_income_target=60000
    )


class TestScenarioManager:
    """Test cases for ScenarioManager."""

    @pytest.mark.asyncio
    async def test_database_initialization(self, temp_db):
        """Test that database initializes correctly."""
        # Database should be initialized without errors
        assert temp_db.db_path is not None
        
        # Should be able to create a scenario
        scenarios = await temp_db.list_scenarios()
        assert scenarios == []

    @pytest.mark.asyncio
    async def test_create_scenario(self, temp_db, sample_scenario_input):
        """Test creating a new scenario."""
        scenario_id = await temp_db.create_scenario(sample_scenario_input)
        
        # Should return a valid scenario ID
        assert scenario_id is not None
        assert isinstance(scenario_id, str)
        assert len(scenario_id) > 0
        
        # Should be able to retrieve the scenario
        scenario = await temp_db.get_scenario(scenario_id)
        assert scenario is not None
        assert scenario['name'] == sample_scenario_input.name
        assert scenario['scenario_type'] == sample_scenario_input.scenario_type.value

    @pytest.mark.asyncio
    async def test_list_scenarios(self, temp_db, sample_scenario_input):
        """Test listing scenarios."""
        # Initially should be empty
        scenarios = await temp_db.list_scenarios()
        assert len(scenarios) == 0
        
        # Create a scenario
        scenario_id = await temp_db.create_scenario(sample_scenario_input)
        
        # Should now have one scenario
        scenarios = await temp_db.list_scenarios()
        assert len(scenarios) == 1
        assert scenarios[0]['id'] == scenario_id
        assert scenarios[0]['name'] == sample_scenario_input.name

    @pytest.mark.asyncio
    async def test_get_scenario(self, temp_db, sample_scenario_input):
        """Test retrieving a specific scenario."""
        scenario_id = await temp_db.create_scenario(sample_scenario_input)
        
        scenario = await temp_db.get_scenario(scenario_id)
        assert scenario is not None
        assert scenario['id'] == scenario_id
        assert scenario['name'] == sample_scenario_input.name
        
        # Test non-existent scenario
        non_existent = await temp_db.get_scenario("non-existent-id")
        assert non_existent is None

    @pytest.mark.asyncio
    async def test_run_projection(self, temp_db, sample_scenario_input):
        """Test running a financial projection."""
        scenario_id = await temp_db.create_scenario(sample_scenario_input)
        
        projection = await temp_db.run_projection(scenario_id, include_monte_carlo=False)
        
        # Should return a valid projection
        assert projection is not None
        assert projection.scenario_id == scenario_id
        assert projection.scenario_name == sample_scenario_input.name
        assert len(projection.yearly_projections) > 0
        
        # Check projection data integrity
        first_year = projection.yearly_projections[0]
        assert first_year.year == sample_scenario_input.projection_settings.start_year
        assert first_year.age == sample_scenario_input.user_profile.current_age
        assert first_year.beginning_assets > 0  # Should have initial assets
        
        # Final year should be reasonable
        final_year = projection.yearly_projections[-1]
        assert final_year.year > first_year.year
        assert final_year.age > first_year.age

    @pytest.mark.asyncio
    async def test_yearly_projections_calculation(self, temp_db, sample_scenario_input):
        """Test the accuracy of yearly projection calculations."""
        scenario_id = await temp_db.create_scenario(sample_scenario_input)
        
        projection = await temp_db.run_projection(scenario_id)
        yearly_projections = projection.yearly_projections
        
        # Test first year calculations
        first_year = yearly_projections[0]
        user_profile = sample_scenario_input.user_profile
        
        # Should have initial assets from user profile
        initial_assets = sum(asset.current_value for asset in user_profile.assets)
        assert abs(first_year.beginning_assets - initial_assets) < 1  # Allow for rounding
        
        # Should have income equal to salary (first year)
        expected_income = user_profile.annual_salary * (1 - sample_scenario_input.projection_settings.assumptions.tax_rate)
        assert abs(first_year.income - expected_income) < 100  # Allow for rounding
        
        # Should have expenses from user profile
        expected_expenses = sum(expense.annual_amount for expense in user_profile.expenses)
        assert abs(first_year.expenses - expected_expenses) < 100

    @pytest.mark.asyncio
    async def test_compare_scenarios(self, temp_db, sample_scenario_input, sample_user_profile, sample_projection_settings):
        """Test comparing multiple scenarios."""
        # Create first scenario
        scenario1_id = await temp_db.create_scenario(sample_scenario_input)
        
        # Create second scenario with different parameters
        scenario2_input = ScenarioInput(
            name="Test Early Retirement Scenario",
            description="Testing early retirement scenario",
            scenario_type=ScenarioType.retirement,
            user_profile=sample_user_profile,
            projection_settings=sample_projection_settings,
            retirement_income_target=50000
        )
        scenario2_id = await temp_db.create_scenario(scenario2_input)
        
        # Compare scenarios
        comparison = await temp_db.compare_scenarios([scenario1_id, scenario2_id])
        
        assert len(comparison) == 2
        assert scenario1_id in comparison
        assert scenario2_id in comparison
        
        # Both projections should be valid
        proj1 = comparison[scenario1_id]
        proj2 = comparison[scenario2_id]
        
        assert proj1.scenario_name == sample_scenario_input.name
        assert proj2.scenario_name == scenario2_input.name

    @pytest.mark.asyncio
    async def test_analyze_city_relocation(self, temp_db, sample_user_profile):
        """Test city relocation analysis."""
        comparison = await temp_db.analyze_city_relocation(
            "New York, NY", 
            "Austin, TX", 
            sample_user_profile
        )
        
        assert comparison is not None
        assert comparison.current_city.city_name == "New York, NY"
        assert comparison.target_city.city_name == "Austin, TX"
        assert isinstance(comparison.annual_cost_difference, (int, float))
        assert isinstance(comparison.net_worth_impact_10_year, (int, float))
        assert isinstance(comparison.net_worth_impact_retirement, (int, float))

    @pytest.mark.asyncio
    async def test_project_education_expenses(self, temp_db):
        """Test education expense projection."""
        projection = await temp_db.project_education_expenses(
            institution_type="public_college",
            start_year=2030,
            duration_years=4,
            current_child_age=10
        )
        
        assert projection is not None
        assert projection.institution_type == "public_college"
        assert projection.duration_years == 4
        assert projection.total_cost_present_value > 0
        assert projection.total_cost_future_value > projection.total_cost_present_value
        assert projection.monthly_savings_required > 0

    @pytest.mark.asyncio
    async def test_analyze_vehicle_ownership(self, temp_db):
        """Test vehicle ownership analysis."""
        analysis = await temp_db.analyze_vehicle_ownership(
            vehicle_type="midsize",
            ownership_years=5,
            annual_mileage=12000
        )
        
        assert analysis is not None
        assert analysis.vehicle_type == "midsize"
        assert analysis.purchase_price > 0
        assert analysis.total_cost_ownership > analysis.purchase_price
        assert analysis.insurance_annual > 0
        assert analysis.fuel_annual > 0
        assert analysis.maintenance_annual > 0

    @pytest.mark.asyncio
    async def test_analyze_financial_goals(self, temp_db, sample_user_profile):
        """Test financial goals analysis."""
        from models.financial_models import GoalDefinition, GoalType
        
        goals = [
            GoalDefinition(
                name="Emergency Fund",
                goal_type=GoalType.emergency_fund,
                target_amount=50000,
                target_date=date(2030, 1, 1),
                current_amount=10000,
                monthly_contribution=500,
                expected_return=0.05
            )
        ]
        
        projections = await temp_db.analyze_financial_goals(goals, sample_user_profile)
        
        assert len(projections) == 1
        projection = projections[0]
        
        assert projection.goal.name == "Emergency Fund"
        assert projection.projected_final_amount > 0
        assert projection.probability_of_success >= 0
        assert projection.probability_of_success <= 1
        assert projection.required_monthly_contribution > 0

    @pytest.mark.asyncio
    async def test_invalid_scenario_projection(self, temp_db):
        """Test handling of invalid scenario ID for projections."""
        with pytest.raises(ValueError, match="Scenario .* not found"):
            await temp_db.run_projection("invalid-scenario-id")

    @pytest.mark.asyncio
    async def test_projection_with_monte_carlo(self, temp_db, sample_scenario_input):
        """Test projection with Monte Carlo simulation enabled."""
        scenario_id = await temp_db.create_scenario(sample_scenario_input)
        
        # Note: This test might be slow due to Monte Carlo simulation
        projection = await temp_db.run_projection(scenario_id, include_monte_carlo=True)
        
        assert projection is not None
        assert projection.monte_carlo_results is not None
        assert projection.monte_carlo_results.simulations_run > 0
        assert projection.monte_carlo_results.success_probability >= 0
        assert projection.monte_carlo_results.success_probability <= 1


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])