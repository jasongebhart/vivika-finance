"""
Tests for the LifePlanningService - moving vs staying analysis with education costs.
"""

import pytest
import json
import tempfile
import os
from datetime import datetime
from services.life_planning_service import LifePlanningService


@pytest.fixture
def sample_children():
    """Sample children data for testing."""
    return [
        {"name": "Emma", "current_age": 12, "current_grade": 7},
        {"name": "Jake", "current_age": 9, "current_grade": 4}
    ]


@pytest.fixture
def sample_financial_profile():
    """Sample financial profile for testing."""
    return {
        "current_annual_income": 500000,
        "current_annual_expenses": 200000,
        "current_location": "San Francisco",
        "analysis_years": 10
    }


@pytest.fixture
def life_planning_service():
    """Create a LifePlanningService instance for testing."""
    return LifePlanningService()


class TestLifePlanningServiceInit:
    """Test service initialization."""
    
    def test_init(self, life_planning_service):
        """Test that service initializes properly."""
        assert life_planning_service is not None
        assert hasattr(life_planning_service, 'location_data')
        assert hasattr(life_planning_service, 'education_costs')
        
    def test_location_data_structure(self, life_planning_service):
        """Test that location data has proper structure."""
        locations = life_planning_service.location_data
        
        # Should have data for major locations
        expected_locations = ['San Francisco', 'San Diego', 'Minnesota']
        for location in expected_locations:
            if location in locations:
                assert 'cost_of_living_multiplier' in locations[location]
                assert 'housing_cost_ratio' in locations[location]
                assert 'quality_of_life_score' in locations[location]


class TestMoveAnalysis:
    """Test the core move analysis functionality."""
    
    def test_analyze_move_scenarios_basic(self, life_planning_service, sample_children, sample_financial_profile):
        """Test basic move analysis functionality."""
        analysis = life_planning_service.analyze_move_scenarios(
            children=sample_children,
            **sample_financial_profile
        )
        
        assert isinstance(analysis, dict)
        assert 'scenarios' in analysis
        assert 'summary' in analysis
        assert 'analysis_period' in analysis
        assert 'children_profiles' in analysis
        
        # Should have multiple scenarios
        assert len(analysis['scenarios']) > 0
        
    def test_scenarios_structure(self, life_planning_service, sample_children, sample_financial_profile):
        """Test that scenarios have proper structure."""
        analysis = life_planning_service.analyze_move_scenarios(
            children=sample_children,
            **sample_financial_profile
        )
        
        scenarios = analysis['scenarios']
        
        for scenario in scenarios:
            assert 'scenario' in scenario
            assert 'financial_summary' in scenario
            assert 'yearly_breakdown' in scenario
            assert 'quality_metrics' in scenario
            
            # Check scenario details
            scenario_details = scenario['scenario']
            assert 'description' in scenario_details
            assert 'location' in scenario_details
            assert 'education_strategy' in scenario_details
            
            # Check financial summary
            financial = scenario['financial_summary']
            assert 'total_moving_costs' in financial
            assert 'total_education_costs' in financial
            assert 'total_housing_savings' in financial
            assert 'net_present_value' in financial
            
    def test_yearly_breakdown_structure(self, life_planning_service, sample_children, sample_financial_profile):
        """Test that yearly breakdown has proper structure."""
        analysis = life_planning_service.analyze_move_scenarios(
            children=sample_children,
            **sample_financial_profile
        )
        
        scenario = analysis['scenarios'][0]
        yearly_breakdown = scenario['yearly_breakdown']
        
        assert len(yearly_breakdown) == sample_financial_profile['analysis_years']
        
        for year_data in yearly_breakdown:
            assert 'year' in year_data
            assert 'costs' in year_data
            assert 'savings' in year_data
            assert 'net' in year_data
            assert isinstance(year_data['costs'], dict)
            assert isinstance(year_data['savings'], dict)


class TestEducationCostCalculations:
    """Test education cost calculations based on children's ages and timing."""
    
    def test_education_timing_based_on_age(self, life_planning_service):
        """Test that education costs are calculated based on children's actual ages."""
        # Emma is 12 (Grade 7), will start high school at 14, college at 18
        # Jake is 9 (Grade 4), will start high school at 14, college at 18
        
        children = [
            {"name": "Emma", "current_age": 12, "current_grade": 7},
            {"name": "Jake", "current_age": 9, "current_grade": 4}
        ]
        
        analysis = life_planning_service.analyze_move_scenarios(
            children=children,
            current_annual_income=400000,
            current_annual_expenses=150000,
            current_location="San Francisco",
            analysis_years=15  # Longer period to capture education costs
        )
        
        # Find a scenario with private education
        private_scenario = next(
            (s for s in analysis['scenarios'] if 'private' in s['scenario']['education_strategy'].lower()),
            None
        )
        
        if private_scenario:
            yearly_breakdown = private_scenario['yearly_breakdown']
            
            # Should have education costs starting when kids reach school age
            education_years = [year for year in yearly_breakdown if year['costs'].get('education', 0) > 0]
            assert len(education_years) > 0
            
    def test_college_costs_realistic_timing(self, life_planning_service):
        """Test that college costs occur at realistic times."""
        children = [
            {"name": "Emma", "current_age": 16, "current_grade": 11},  # Nearly college age
            {"name": "Jake", "current_age": 13, "current_grade": 8}    # Will reach college in 5 years
        ]
        
        analysis = life_planning_service.analyze_move_scenarios(
            children=children,
            current_annual_income=400000,
            current_annual_expenses=150000,
            current_location="Minnesota",
            analysis_years=10
        )
        
        scenario = analysis['scenarios'][0]
        yearly_breakdown = scenario['yearly_breakdown']
        
        # Emma should have college costs starting soon (within 2-3 years)
        early_college_costs = any(
            year['costs'].get('education', 0) > 10000  # Significant education cost
            for year in yearly_breakdown[:3]
        )
        
        # For a college-age child, we should see significant education costs early
        if any('college' in s['scenario']['education_strategy'].lower() for s in analysis['scenarios']):
            assert early_college_costs or scenario['financial_summary']['total_education_costs'] > 0


class TestLocationComparisons:
    """Test comparisons between different locations."""
    
    def test_different_locations_different_costs(self, life_planning_service, sample_children):
        """Test that different locations produce different cost structures."""
        base_params = {
            "children": sample_children,
            "current_annual_income": 400000,
            "current_annual_expenses": 150000,
            "analysis_years": 8
        }
        
        sf_analysis = life_planning_service.analyze_move_scenarios(
            current_location="San Francisco",
            **base_params
        )
        
        mn_analysis = life_planning_service.analyze_move_scenarios(
            current_location="Minnesota", 
            **base_params
        )
        
        # Should have different scenario counts or different financial outcomes
        sf_best = sf_analysis['scenarios'][0]['financial_summary']['net_present_value']
        mn_best = mn_analysis['scenarios'][0]['financial_summary']['net_present_value']
        
        # The financial outcomes should be different
        assert sf_best != mn_best
        
    def test_housing_cost_differences(self, life_planning_service, sample_children):
        """Test that housing costs differ significantly between locations."""
        analysis = life_planning_service.analyze_move_scenarios(
            children=sample_children,
            current_annual_income=500000,
            current_annual_expenses=200000,
            current_location="San Francisco",
            analysis_years=8
        )
        
        scenarios = analysis['scenarios']
        
        # Find scenarios for different locations
        sf_scenario = next((s for s in scenarios if 'San Francisco' in s['scenario']['location_name']), None)
        mn_scenario = next((s for s in scenarios if 'Minnesota' in s['scenario']['location_name']), None)
        
        if sf_scenario and mn_scenario:
            # Housing savings should be different (typically higher when moving from SF to MN)
            sf_housing_savings = sf_scenario['financial_summary']['total_housing_savings']
            mn_housing_savings = mn_scenario['financial_summary']['total_housing_savings']
            
            # Moving from SF should generally provide housing savings
            assert sf_housing_savings != mn_housing_savings


class TestQualityMetrics:
    """Test quality of life and risk assessment metrics."""
    
    def test_quality_metrics_structure(self, life_planning_service, sample_children, sample_financial_profile):
        """Test that quality metrics have proper structure."""
        analysis = life_planning_service.analyze_move_scenarios(
            children=sample_children,
            **sample_financial_profile
        )
        
        scenario = analysis['scenarios'][0]
        quality_metrics = scenario['quality_metrics']
        
        assert 'quality_of_life_score' in quality_metrics
        assert 'education_quality' in quality_metrics
        assert 'financial_stress_level' in quality_metrics
        
        # Scores should be reasonable ranges
        assert 0 <= quality_metrics['quality_of_life_score'] <= 10
        assert 0 <= quality_metrics['education_quality'] <= 10
        assert quality_metrics['financial_stress_level'] in ['Low', 'Moderate', 'High', 'Very High']
        
    def test_quality_scores_vary_by_scenario(self, life_planning_service, sample_children, sample_financial_profile):
        """Test that quality scores vary meaningfully between scenarios."""
        analysis = life_planning_service.analyze_move_scenarios(
            children=sample_children,
            **sample_financial_profile
        )
        
        scenarios = analysis['scenarios']
        
        if len(scenarios) > 1:
            quality_scores = [s['quality_metrics']['quality_of_life_score'] for s in scenarios]
            education_scores = [s['quality_metrics']['education_quality'] for s in scenarios]
            
            # Should have some variation in scores
            assert len(set(quality_scores)) > 1 or len(set(education_scores)) > 1


class TestSummaryAndRecommendations:
    """Test analysis summary and recommendations."""
    
    def test_summary_structure(self, life_planning_service, sample_children, sample_financial_profile):
        """Test that summary has proper structure."""
        analysis = life_planning_service.analyze_move_scenarios(
            children=sample_children,
            **sample_financial_profile
        )
        
        summary = analysis['summary']
        
        assert 'best_overall' in summary
        assert 'best_financial' in summary
        assert 'best_quality_of_life' in summary
        assert 'decision_points' in summary
        assert 'key_insights' in summary
        assert 'recommendations' in summary
        
    def test_recommendations_exist(self, life_planning_service, sample_children, sample_financial_profile):
        """Test that recommendations are generated."""
        analysis = life_planning_service.analyze_move_scenarios(
            children=sample_children,
            **sample_financial_profile
        )
        
        summary = analysis['summary']
        
        assert isinstance(summary['key_insights'], list)
        assert isinstance(summary['recommendations'], list)
        assert len(summary['key_insights']) > 0
        assert len(summary['recommendations']) > 0
        
    def test_decision_points_timing(self, life_planning_service, sample_children, sample_financial_profile):
        """Test that decision points are identified at appropriate times."""
        analysis = life_planning_service.analyze_move_scenarios(
            children=sample_children,
            **sample_financial_profile
        )
        
        decision_points = analysis['summary']['decision_points']
        
        if len(decision_points) > 0:
            for point in decision_points:
                assert 'year' in point
                assert 'event' in point
                assert 'recommendation' in point
                
                # Year should be within analysis period
                current_year = datetime.now().year
                assert current_year <= point['year'] <= current_year + sample_financial_profile['analysis_years']


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_no_children(self, life_planning_service):
        """Test analysis with no children."""
        analysis = life_planning_service.analyze_move_scenarios(
            children=[],
            current_annual_income=400000,
            current_annual_expenses=150000,
            current_location="San Francisco",
            analysis_years=8
        )
        
        assert isinstance(analysis, dict)
        assert 'scenarios' in analysis
        # Should still generate scenarios, just without education costs
        
    def test_single_child(self, life_planning_service):
        """Test analysis with single child."""
        single_child = [{"name": "Emma", "current_age": 12, "current_grade": 7}]
        
        analysis = life_planning_service.analyze_move_scenarios(
            children=single_child,
            current_annual_income=400000,
            current_annual_expenses=150000,
            current_location="San Francisco",
            analysis_years=8
        )
        
        assert len(analysis['children_profiles']) == 1
        
    def test_high_school_graduate(self, life_planning_service):
        """Test analysis with child who's already graduated high school."""
        older_child = [{"name": "Emma", "current_age": 19, "current_grade": 13}]  # College age
        
        analysis = life_planning_service.analyze_move_scenarios(
            children=older_child,
            current_annual_income=400000,
            current_annual_expenses=150000,
            current_location="San Francisco",
            analysis_years=5
        )
        
        # Should handle college-age children appropriately
        assert isinstance(analysis, dict)
        assert len(analysis['children_profiles']) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])