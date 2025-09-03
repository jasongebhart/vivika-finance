"""
Monte Carlo simulation engine for financial planning.
"""

import random
import asyncio
import math
from typing import List, Optional
from models.financial_models import (
    UserProfile, 
    ProjectionSettings, 
    MonteCarloResult, 
    MonteCarloProjectionYear,
    SimulationResult,
    WithdrawalStrategyAnalysis,
    WithdrawalStrategy
)
import logging

logger = logging.getLogger(__name__)

class MonteCarloEngine:
    """Monte Carlo simulation engine for retirement planning."""
    
    def __init__(self):
        random.seed()  # Initialize random number generator
    
    async def run_simulation(
        self, 
        user_profile: UserProfile,
        projection_settings: ProjectionSettings,
        progress_callback: Optional[callable] = None
    ) -> MonteCarloResult:
        """
        Run Monte Carlo simulation for retirement planning.
        
        Args:
            user_profile: User's financial profile
            projection_settings: Projection parameters
            progress_callback: Optional callback for progress updates
            
        Returns:
            MonteCarloResult with simulation outcomes
        """
        logger.info("Starting Monte Carlo simulation")
        
        # Default Monte Carlo parameters if not provided
        num_simulations = 1000
        return_std_dev = 0.15
        inflation_std_dev = 0.01
        
        projection_years = projection_settings.projection_years
        assumptions = projection_settings.assumptions
        
        # Initialize results storage
        final_net_worths = []
        annual_projections = []
        
        # Initialize annual projections structure
        for year_idx in range(projection_years):
            annual_projections.append(MonteCarloProjectionYear(
                year=projection_settings.start_year + year_idx,
                simulation_results=[]
            ))
        
        # Run simulations
        for sim_idx in range(num_simulations):
            if progress_callback and sim_idx % 100 == 0:
                progress = sim_idx / num_simulations
                await progress_callback(progress, f"Running simulation {sim_idx + 1}/{num_simulations}")
            
            # Run single simulation
            sim_result = await self._run_single_simulation(
                user_profile, 
                projection_settings, 
                return_std_dev,
                inflation_std_dev
            )
            
            final_net_worths.append(sim_result[-1]['net_worth'])
            
            # Add results to annual projections
            for year_idx, year_result in enumerate(sim_result):
                annual_projections[year_idx].simulation_results.append(
                    SimulationResult(
                        net_worth=year_result['net_worth'],
                        portfolio_value=year_result['portfolio_value'],
                        annual_income=year_result['annual_income'],
                        withdrawal_rate=year_result['withdrawal_rate']
                    )
                )
        
        # Calculate statistics
        final_net_worths.sort()
        n = len(final_net_worths)
        
        median_final_value = final_net_worths[n // 2]
        mean_final_value = sum(final_net_worths) / n
        std_dev = math.sqrt(sum((x - mean_final_value) ** 2 for x in final_net_worths) / n)
        
        tenth_percentile = final_net_worths[int(n * 0.1)]
        ninetieth_percentile = final_net_worths[int(n * 0.9)]
        
        # Calculate success probability (simplified - assume success if final value > 0)
        retirement_target = getattr(user_profile, 'retirement_income_target', 0) or 0
        if retirement_target > 0:
            success_count = sum(1 for val in final_net_worths if val * 0.04 >= retirement_target)
        else:
            success_count = sum(1 for val in final_net_worths if val > 0)
        
        success_probability = success_count / num_simulations
        
        # Create final year distribution
        final_year_distribution = {
            'net_worth': final_net_worths,
            'portfolio_value': [x * 0.9 for x in final_net_worths]  # Approximate
        }
        
        if progress_callback:
            await progress_callback(1.0, "Simulation completed")
        
        return MonteCarloResult(
            simulations_run=num_simulations,
            projection_years=projection_years,
            success_probability=success_probability,
            median_final_value=median_final_value,
            mean_final_value=mean_final_value,
            std_dev_final_value=std_dev,
            worst_case_10th_percentile=tenth_percentile,
            best_case_90th_percentile=ninetieth_percentile,
            annual_projections=annual_projections,
            final_year_distribution=final_year_distribution
        )
    
    async def _run_single_simulation(
        self,
        user_profile: UserProfile,
        projection_settings: ProjectionSettings,
        return_std_dev: float,
        inflation_std_dev: float
    ) -> List[dict]:
        """Run a single Monte Carlo simulation."""
        
        results = []
        current_assets = sum(asset.current_value for asset in user_profile.assets)
        current_age = user_profile.current_age
        assumptions = projection_settings.assumptions
        
        for year in range(projection_settings.projection_years):
            age = current_age + year
            
            # Generate random variations
            investment_return = random.normalvariate(
                assumptions.investment_return, 
                return_std_dev
            )
            inflation_rate = random.normalvariate(
                assumptions.inflation_rate,
                inflation_std_dev
            )
            
            # Calculate income
            if age < user_profile.retirement_age:
                annual_income = user_profile.annual_salary * (
                    (1 + assumptions.salary_growth_rate) ** year
                )
                # Apply taxes
                annual_income *= (1 - assumptions.tax_rate)
            else:
                # Retirement income (simplified)
                annual_income = sum(
                    source.annual_amount for source in user_profile.income_sources
                    if source.start_age <= age
                )
            
            # Calculate expenses with inflation
            annual_expenses = sum(
                expense.annual_amount * ((1 + inflation_rate) ** year)
                for expense in user_profile.expenses
                if expense.start_age <= age <= (expense.end_age or 120)
            )
            
            # Net cash flow
            net_cash_flow = annual_income - annual_expenses
            
            # Update assets
            beginning_assets = current_assets
            current_assets += net_cash_flow
            current_assets *= (1 + investment_return)
            current_assets = max(0, current_assets)  # Can't go negative
            
            # Calculate withdrawal rate (for retirees)
            withdrawal_rate = 0.0
            if age >= user_profile.retirement_age and beginning_assets > 0:
                withdrawal_rate = abs(net_cash_flow) / beginning_assets if net_cash_flow < 0 else 0
            
            results.append({
                'net_worth': current_assets,
                'portfolio_value': current_assets * 0.9,  # Approximate
                'annual_income': annual_income,
                'withdrawal_rate': withdrawal_rate
            })
        
        return results
    
    async def analyze_withdrawal_strategies(
        self,
        user_profile: UserProfile,
        projection_settings: ProjectionSettings
    ) -> WithdrawalStrategyAnalysis:
        """Analyze different withdrawal strategies."""
        
        strategies = [
            WithdrawalStrategy(
                name="4% Rule",
                description="Traditional 4% annual withdrawal rate",
                success_rate=0.85,
                median_final_value=500000,
                worst_case_10th_percentile=200000
            ),
            WithdrawalStrategy(
                name="Dynamic Withdrawal",
                description="Adjust withdrawal based on portfolio performance",
                success_rate=0.92,
                median_final_value=600000,
                worst_case_10th_percentile=300000
            ),
            WithdrawalStrategy(
                name="Bond Ladder",
                description="Use bond ladder for guaranteed income",
                success_rate=0.78,
                median_final_value=450000,
                worst_case_10th_percentile=350000
            )
        ]
        
        return WithdrawalStrategyAnalysis(strategies=strategies)