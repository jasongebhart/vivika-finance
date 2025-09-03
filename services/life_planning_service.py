"""
Life Planning Decision Engine
Analyzes optimal timing for major life decisions like moving, education choices, and family planning.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import copy

logger = logging.getLogger(__name__)

class EducationType(Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    PREP = "prep"
    PREPUB = "prepub"  # Mix of prep and public

class SchoolLevel(Enum):
    ELEMENTARY = "elementary"
    MIDDLE = "middle"
    HIGH = "high"
    COLLEGE = "college"

@dataclass
class Child:
    name: str
    current_age: int
    current_grade: int
    
    def age_in_year(self, target_year: int) -> int:
        current_year = datetime.now().year
        return self.current_age + (target_year - current_year)
    
    def grade_in_year(self, target_year: int) -> int:
        current_year = datetime.now().year
        return self.current_grade + (target_year - current_year)
    
    def school_level_in_year(self, target_year: int) -> SchoolLevel:
        grade = self.grade_in_year(target_year)
        if grade <= 5:
            return SchoolLevel.ELEMENTARY
        elif grade <= 8:
            return SchoolLevel.MIDDLE
        elif grade <= 12:
            return SchoolLevel.HIGH
        else:
            return SchoolLevel.COLLEGE

@dataclass
class LocationProfile:
    name: str
    display_name: str
    cost_multipliers: Dict[str, float]
    education_costs: Dict[str, Dict[str, float]]  # school_type -> level -> annual_cost
    housing_cost_difference: float  # vs current location
    moving_costs: float
    job_income_impact: float  # multiplier on current income
    quality_of_life_score: float  # 1-10 scale

@dataclass
class MovingScenario:
    move_year: int
    target_location: str
    education_strategy: EducationType
    reason: str

class LifePlanningService:
    """Service for comprehensive life planning decision analysis."""
    
    def __init__(self):
        self.current_year = datetime.now().year
        
        # Location profiles with comprehensive data
        self.locations = {
            'current': LocationProfile(
                name='current',
                display_name='Current Location (SF)',
                cost_multipliers={'living': 1.4, 'housing': 2.8, 'utilities': 1.4, 'transport': 1.4},
                education_costs={
                    'public': {'elementary': 0, 'middle': 0, 'high': 0, 'college': 28000},
                    'private': {'elementary': 35000, 'middle': 40000, 'high': 45000, 'college': 65000},
                    'prep': {'elementary': 40000, 'middle': 45000, 'high': 55000, 'college': 70000}
                },
                housing_cost_difference=0,
                moving_costs=0,
                job_income_impact=1.0,
                quality_of_life_score=7.5
            ),
            'sd': LocationProfile(
                name='sd',
                display_name='San Diego',
                cost_multipliers={'living': 1.2, 'housing': 1.8, 'utilities': 1.2, 'transport': 1.2},
                education_costs={
                    'public': {'elementary': 0, 'middle': 0, 'high': 0, 'college': 25000},
                    'private': {'elementary': 28000, 'middle': 32000, 'high': 38000, 'college': 60000},
                    'prep': {'elementary': 32000, 'middle': 36000, 'high': 45000, 'college': 65000}
                },
                housing_cost_difference=-120000,  # Annual savings
                moving_costs=75000,
                job_income_impact=0.95,  # 5% income reduction
                quality_of_life_score=8.5
            ),
            'mn': LocationProfile(
                name='mn',
                display_name='Minnesota',
                cost_multipliers={'living': 0.85, 'housing': 0.7, 'utilities': 0.85, 'transport': 0.85},
                education_costs={
                    'public': {'elementary': 0, 'middle': 0, 'high': 0, 'college': 22000},
                    'private': {'elementary': 20000, 'middle': 25000, 'high': 30000, 'college': 50000},
                    'prep': {'elementary': 25000, 'middle': 30000, 'high': 35000, 'college': 55000}
                },
                housing_cost_difference=-180000,  # Annual savings
                moving_costs=95000,
                job_income_impact=0.85,  # 15% income reduction
                quality_of_life_score=8.0
            )
        }
        
        # Education transition costs (one-time costs when changing schools)
        self.transition_costs = {
            'public_to_private': 5000,
            'private_to_public': 2000,
            'location_change': 3000,
            'grade_level_change': 1000
        }
    
    def analyze_move_timing_scenarios(self, 
                                    children: List[Child],
                                    current_annual_income: float,
                                    current_annual_expenses: float,
                                    analysis_years: int = 10) -> Dict[str, Any]:
        """Analyze different move timing scenarios for optimal financial and life outcomes."""
        
        scenarios = []
        
        # Generate scenarios for each potential move year
        for move_year in range(self.current_year, self.current_year + 6):  # Next 5 years
            for location in ['sd', 'mn']:
                for education_type in [EducationType.PUBLIC, EducationType.PRIVATE]:
                    scenario = MovingScenario(
                        move_year=move_year,
                        target_location=location,
                        education_strategy=education_type,
                        reason=f"Move to {self.locations[location].display_name} in {move_year}"
                    )
                    scenarios.append(scenario)
        
        # Add "stay put" scenario
        stay_scenario = MovingScenario(
            move_year=None,
            target_location='current',
            education_strategy=EducationType.PRIVATE,  # Assume private if staying
            reason="Stay in current location"
        )
        scenarios.append(stay_scenario)
        
        # Analyze each scenario
        results = []
        for scenario in scenarios:
            analysis = self._analyze_single_scenario(
                scenario, children, current_annual_income, current_annual_expenses, analysis_years
            )
            results.append(analysis)
        
        # Rank scenarios by net present value
        results.sort(key=lambda x: x['financial_summary']['net_present_value'], reverse=True)
        
        return {
            'scenarios': results,
            'summary': self._generate_decision_summary(results, children),
            'analysis_period': f"{self.current_year}-{self.current_year + analysis_years}",
            'children_profiles': [
                {
                    'name': child.name,
                    'current_age': child.current_age,
                    'current_grade': child.current_grade,
                    'graduation_year': self.current_year + (12 - child.current_grade)
                }
                for child in children
            ]
        }
    
    def _analyze_single_scenario(self,
                                scenario: MovingScenario,
                                children: List[Child],
                                current_income: float,
                                current_expenses: float,
                                years: int) -> Dict[str, Any]:
        """Analyze a single moving scenario over the specified time period."""
        
        total_costs = 0
        total_savings = 0
        education_costs = 0
        moving_costs = 0
        income_impact = 0
        yearly_breakdown = []
        
        location = self.locations[scenario.target_location]
        
        # One-time moving costs
        if scenario.move_year:
            moving_costs = location.moving_costs
            total_costs += moving_costs
        
        # Analyze each year
        for year_offset in range(years):
            year = self.current_year + year_offset
            year_data = {'year': year, 'costs': {}, 'savings': {}, 'net': 0}
            
            # Calculate if move has happened
            moved = scenario.move_year and year >= scenario.move_year
            current_location = location if moved else self.locations['current']
            
            # Income impact (only after move)
            if moved:
                income_change = current_income * (current_location.job_income_impact - 1)
                income_impact += income_change
                year_data['income_impact'] = income_change
            
            # Housing cost difference (only after move)
            if moved:
                housing_savings = -current_location.housing_cost_difference  # Negative means savings
                total_savings += housing_savings
                year_data['savings']['housing'] = housing_savings
            
            # Living expenses difference (only after move)
            if moved:
                expense_multiplier = current_location.cost_multipliers.get('living', 1.0)
                current_multiplier = self.locations['current'].cost_multipliers.get('living', 1.0)
                expense_difference = current_expenses * (expense_multiplier - current_multiplier)
                total_costs += expense_difference
                year_data['costs']['living_expenses'] = expense_difference
            
            # Education costs for each child
            year_education_cost = 0
            for child in children:
                child_grade = child.grade_in_year(year)
                if child_grade >= 1 and child_grade <= 12:  # K-12
                    school_level = child.school_level_in_year(year).value
                    edu_type = scenario.education_strategy.value
                    
                    if edu_type in current_location.education_costs:
                        if school_level in current_location.education_costs[edu_type]:
                            cost = current_location.education_costs[edu_type][school_level]
                            year_education_cost += cost
                            education_costs += cost
            
            year_data['costs']['education'] = year_education_cost
            year_data['net'] = (year_data['savings'].get('housing', 0) - 
                              year_data['costs'].get('living_expenses', 0) - 
                              year_data['costs'].get('education', 0) +
                              year_data.get('income_impact', 0))
            yearly_breakdown.append(year_data)
        
        # Calculate net present value (simple 3% discount rate)
        discount_rate = 0.03
        npv = -moving_costs  # Start with moving costs as negative
        for i, year_data in enumerate(yearly_breakdown):
            npv += year_data['net'] / ((1 + discount_rate) ** i)
        
        # Calculate break-even point
        break_even_year = None
        cumulative_net = -moving_costs
        for i, year_data in enumerate(yearly_breakdown):
            cumulative_net += year_data['net']
            if cumulative_net > 0 and break_even_year is None:
                break_even_year = year_data['year']
        
        return {
            'scenario': {
                'description': scenario.reason,
                'move_year': scenario.move_year,
                'location': scenario.target_location,
                'location_name': location.display_name,
                'education_strategy': scenario.education_strategy.value
            },
            'financial_summary': {
                'total_moving_costs': moving_costs,
                'total_education_costs': education_costs,
                'total_housing_savings': total_savings,
                'total_income_impact': income_impact,
                'net_present_value': npv,
                'break_even_year': break_even_year,
                'total_net_benefit': sum(year['net'] for year in yearly_breakdown) - moving_costs
            },
            'yearly_breakdown': yearly_breakdown,
            'quality_metrics': {
                'quality_of_life_score': location.quality_of_life_score,
                'education_quality': self._assess_education_quality(scenario.education_strategy, location),
                'financial_stress_level': self._calculate_financial_stress(npv, current_income)
            }
        }
    
    def _generate_decision_summary(self, results: List[Dict], children: List[Child]) -> Dict[str, Any]:
        """Generate executive summary of decision analysis."""
        
        best_scenario = results[0] if results else None
        worst_scenario = results[-1] if results else None
        
        # Find best scenario for different criteria
        best_npv = max(results, key=lambda x: x['financial_summary']['net_present_value'])
        best_quality = max(results, key=lambda x: x['quality_metrics']['quality_of_life_score'])
        fastest_breakeven = min([r for r in results if r['financial_summary']['break_even_year']], 
                               key=lambda x: x['financial_summary']['break_even_year'], default=None)
        
        # Identify critical decision points
        decision_points = []
        for child in children:
            high_school_start = self.current_year + (9 - child.current_grade)
            college_start = self.current_year + (13 - child.current_grade)
            
            if high_school_start > self.current_year:
                decision_points.append({
                    'year': high_school_start,
                    'event': f"{child.name} starts high school",
                    'recommendation': "Consider move before this date to avoid school transition stress"
                })
            
            if college_start > self.current_year and college_start <= self.current_year + 10:
                decision_points.append({
                    'year': college_start,
                    'event': f"{child.name} starts college",
                    'recommendation': "Major expense begins, location less important"
                })
        
        return {
            'best_overall': best_scenario['scenario'] if best_scenario else None,
            'best_financial': best_npv['scenario'],
            'best_quality_of_life': best_quality['scenario'],
            'fastest_payback': fastest_breakeven['scenario'] if fastest_breakeven else None,
            'decision_points': sorted(decision_points, key=lambda x: x['year']),
            'key_insights': self._generate_key_insights(results),
            'recommendations': self._generate_recommendations(results, children)
        }
    
    def _assess_education_quality(self, education_type: EducationType, location: LocationProfile) -> float:
        """Assess education quality score (1-10) based on type and location."""
        base_scores = {
            EducationType.PUBLIC: 6.0,
            EducationType.PRIVATE: 8.0,
            EducationType.PREP: 9.0,
            EducationType.PREPUB: 7.5
        }
        
        location_bonuses = {
            'current': 0.5,  # SF has good schools
            'sd': 0.3,
            'mn': 0.2
        }
        
        return base_scores.get(education_type, 6.0) + location_bonuses.get(location.name, 0)
    
    def _calculate_financial_stress(self, npv: float, annual_income: float) -> str:
        """Calculate financial stress level based on NPV and income."""
        stress_ratio = abs(npv) / annual_income
        
        if stress_ratio < 0.1:
            return "Low"
        elif stress_ratio < 0.3:
            return "Moderate"
        elif stress_ratio < 0.6:
            return "High"
        else:
            return "Very High"
    
    def _generate_key_insights(self, results: List[Dict]) -> List[str]:
        """Generate key insights from the analysis."""
        insights = []
        
        if len(results) > 1:
            best = results[0]
            worst = results[-1]
            npv_difference = best['financial_summary']['net_present_value'] - worst['financial_summary']['net_present_value']
            
            insights.append(f"Best vs worst scenario differs by ${npv_difference:,.0f} in net present value")
            
            # Analyze timing patterns
            early_moves = [r for r in results if r['scenario']['move_year'] and r['scenario']['move_year'] <= self.current_year + 2]
            late_moves = [r for r in results if r['scenario']['move_year'] and r['scenario']['move_year'] > self.current_year + 2]
            
            if early_moves and late_moves:
                early_avg = sum(r['financial_summary']['net_present_value'] for r in early_moves) / len(early_moves)
                late_avg = sum(r['financial_summary']['net_present_value'] for r in late_moves) / len(late_moves)
                
                if early_avg > late_avg:
                    insights.append("Earlier moves generally provide better financial outcomes")
                else:
                    insights.append("Later moves may be financially advantageous")
        
        return insights
    
    def _generate_recommendations(self, results: List[Dict], children: List[Child]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if results:
            best = results[0]
            recommendations.append(f"Primary recommendation: {best['scenario']['description']}")
            
            if best['financial_summary']['break_even_year']:
                recommendations.append(f"This choice breaks even by {best['financial_summary']['break_even_year']}")
            
            # Child-specific recommendations
            for child in children:
                if child.current_grade <= 8:  # Elementary/Middle school
                    recommendations.append(f"For {child.name}: Consider moving before high school (grade 9) to minimize transition stress")
                elif child.current_grade <= 11:  # High school
                    recommendations.append(f"For {child.name}: Moving now may disrupt high school - weigh carefully against financial benefits")
        
        return recommendations

# Global instance
life_planning_service = LifePlanningService()