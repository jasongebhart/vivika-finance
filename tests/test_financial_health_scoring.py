"""
Tests for the financial health scoring system.
"""

import pytest
import sys
import os

# Add the frontend source to the path for testing
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'frontend-modern', 'src'))

# Mock the financial health scoring functions since they're TypeScript
# In a real implementation, these would be tested in the frontend with Jest

def calculateFinancialHealthScore(metrics):
    """Mock implementation for testing the expected interface."""
    # This is a simplified mock - real tests would use the actual TypeScript functions
    return {
        'overall': 75,
        'category': 'good',
        'color': 'blue',
        'breakdown': {
            'cashFlow': {'score': 80, 'weight': 0.25},
            'netWorth': {'score': 70, 'weight': 0.20},
            'emergencyFund': {'score': 75, 'weight': 0.20},
            'growthRate': {'score': 75, 'weight': 0.15},
            'retirementReadiness': {'score': 80, 'weight': 0.15},
            'debtToIncome': {'score': 70, 'weight': 0.10}
        },
        'recommendations': ['Test recommendation']
    }


class TestFinancialHealthMetrics:
    """Test the FinancialHealthMetrics type and validation."""
    
    def test_valid_metrics_structure(self):
        """Test that valid metrics are accepted."""
        metrics = {
            'monthlyIncome': 10000,
            'monthlyExpenses': 7000,
            'monthlySurplus': 3000,
            'netWorth': 500000,
            'liquidSavings': 50000,
            'currentAge': 35,
            'annualGrowthRate': 0.07,
            'projectedNetWorth': 1000000,
            'retirementReadiness': True
        }
        
        # Should not raise any validation errors
        assert metrics['monthlyIncome'] > 0
        assert metrics['monthlySurplus'] == metrics['monthlyIncome'] - metrics['monthlyExpenses']


class TestCashFlowScoring:
    """Test cash flow scoring component."""
    
    def test_positive_cash_flow_high_score(self):
        """Test that positive cash flow results in high score."""
        metrics = {
            'monthlyIncome': 10000,
            'monthlyExpenses': 6000,
            'monthlySurplus': 4000,  # 40% surplus
            'netWorth': 500000,
            'liquidSavings': 50000,
            'currentAge': 35,
            'annualGrowthRate': 0.07,
            'projectedNetWorth': 1000000,
            'retirementReadiness': True
        }
        
        result = calculateFinancialHealthScore(metrics)
        
        # High surplus should result in high cash flow score
        assert result['breakdown']['cashFlow']['score'] >= 80
        assert result['overall'] >= 70  # Should contribute to good overall score
        
    def test_negative_cash_flow_low_score(self):
        """Test that negative cash flow results in low score."""
        metrics = {
            'monthlyIncome': 5000,
            'monthlyExpenses': 6000,
            'monthlySurplus': -1000,  # Negative surplus
            'netWorth': 100000,
            'liquidSavings': 10000,
            'currentAge': 35,
            'annualGrowthRate': 0.05,
            'projectedNetWorth': 200000,
            'retirementReadiness': False
        }
        
        result = calculateFinancialHealthScore(metrics)
        
        # Negative cash flow should result in low score
        assert result['breakdown']['cashFlow']['score'] <= 40
        
    def test_break_even_moderate_score(self):
        """Test that break-even cash flow results in moderate score."""
        metrics = {
            'monthlyIncome': 8000,
            'monthlyExpenses': 8000,
            'monthlySurplus': 0,  # Break even
            'netWorth': 300000,
            'liquidSavings': 30000,
            'currentAge': 40,
            'annualGrowthRate': 0.06,
            'projectedNetWorth': 600000,
            'retirementReadiness': True
        }
        
        result = calculateFinancialHealthScore(metrics)
        
        # Break-even should result in moderate score
        assert 40 <= result['breakdown']['cashFlow']['score'] <= 70


class TestNetWorthScoring:
    """Test net worth scoring component."""
    
    def test_high_net_worth_for_age(self):
        """Test high net worth relative to age and income."""
        metrics = {
            'monthlyIncome': 8000,
            'monthlyExpenses': 6000,
            'monthlySurplus': 2000,
            'netWorth': 1000000,  # High net worth
            'liquidSavings': 100000,
            'currentAge': 35,  # Relatively young
            'annualGrowthRate': 0.08,
            'projectedNetWorth': 2000000,
            'retirementReadiness': True
        }
        
        result = calculateFinancialHealthScore(metrics)
        
        # High net worth for age should score well
        assert result['breakdown']['netWorth']['score'] >= 80
        
    def test_low_net_worth_for_age(self):
        """Test low net worth relative to age and income."""
        metrics = {
            'monthlyIncome': 10000,
            'monthlyExpenses': 9000,
            'monthlySurplus': 1000,
            'netWorth': 50000,  # Low net worth for high income
            'liquidSavings': 5000,
            'currentAge': 45,  # Older age
            'annualGrowthRate': 0.05,
            'projectedNetWorth': 200000,
            'retirementReadiness': False
        }
        
        result = calculateFinancialHealthScore(metrics)
        
        # Low net worth for age/income should score poorly
        assert result['breakdown']['netWorth']['score'] <= 60


class TestEmergencyFundScoring:
    """Test emergency fund scoring component."""
    
    def test_adequate_emergency_fund(self):
        """Test adequate emergency fund (6+ months expenses)."""
        metrics = {
            'monthlyIncome': 8000,
            'monthlyExpenses': 5000,
            'monthlySurplus': 3000,
            'netWorth': 500000,
            'liquidSavings': 40000,  # 8 months of expenses
            'currentAge': 35,
            'annualGrowthRate': 0.07,
            'projectedNetWorth': 1000000,
            'retirementReadiness': True
        }
        
        result = calculateFinancialHealthScore(metrics)
        
        # 8 months emergency fund should score highly
        assert result['breakdown']['emergencyFund']['score'] >= 90
        
    def test_minimal_emergency_fund(self):
        """Test minimal emergency fund (< 3 months expenses)."""
        metrics = {
            'monthlyIncome': 6000,
            'monthlyExpenses': 5000,
            'monthlySurplus': 1000,
            'netWorth': 200000,
            'liquidSavings': 10000,  # 2 months of expenses
            'currentAge': 30,
            'annualGrowthRate': 0.06,
            'projectedNetWorth': 500000,
            'retirementReadiness': False
        }
        
        result = calculateFinancialHealthScore(metrics)
        
        # 2 months emergency fund should score poorly
        assert result['breakdown']['emergencyFund']['score'] <= 50


class TestRetirementReadinessScoring:
    """Test retirement readiness scoring component."""
    
    def test_retirement_ready_high_score(self):
        """Test that retirement readiness flag results in high score."""
        metrics = {
            'monthlyIncome': 10000,
            'monthlyExpenses': 7000,
            'monthlySurplus': 3000,
            'netWorth': 2000000,
            'liquidSavings': 100000,
            'currentAge': 55,
            'annualGrowthRate': 0.07,
            'projectedNetWorth': 3000000,
            'retirementReadiness': True  # Explicitly ready
        }
        
        result = calculateFinancialHealthScore(metrics)
        
        # Retirement readiness should result in high score
        assert result['breakdown']['retirementReadiness']['score'] >= 90
        
    def test_not_retirement_ready_lower_score(self):
        """Test that lack of retirement readiness results in lower score."""
        metrics = {
            'monthlyIncome': 5000,
            'monthlyExpenses': 4500,
            'monthlySurplus': 500,
            'netWorth': 100000,
            'liquidSavings': 15000,
            'currentAge': 55,  # Close to retirement
            'annualGrowthRate': 0.05,
            'projectedNetWorth': 200000,  # Not enough for retirement
            'retirementReadiness': False
        }
        
        result = calculateFinancialHealthScore(metrics)
        
        # Not retirement ready should result in lower score
        assert result['breakdown']['retirementReadiness']['score'] <= 60


class TestOverallScoring:
    """Test overall scoring and categories."""
    
    def test_excellent_financial_health(self):
        """Test case that should result in excellent financial health."""
        metrics = {
            'monthlyIncome': 15000,
            'monthlyExpenses': 8000,
            'monthlySurplus': 7000,  # High surplus
            'netWorth': 2000000,     # High net worth
            'liquidSavings': 80000,  # 10 months emergency fund
            'currentAge': 45,
            'annualGrowthRate': 0.08,  # Good growth
            'projectedNetWorth': 4000000,
            'retirementReadiness': True
        }
        
        result = calculateFinancialHealthScore(metrics)
        
        assert result['overall'] >= 85
        assert result['category'] == 'excellent'
        assert result['color'] == 'green'
        
    def test_poor_financial_health(self):
        """Test case that should result in poor financial health."""
        metrics = {
            'monthlyIncome': 4000,
            'monthlyExpenses': 4500,
            'monthlySurplus': -500,  # Negative cash flow
            'netWorth': 10000,       # Very low net worth
            'liquidSavings': 1000,   # Minimal emergency fund
            'currentAge': 50,        # Older with poor finances
            'annualGrowthRate': 0.02,  # Poor growth
            'projectedNetWorth': 20000,
            'retirementReadiness': False
        }
        
        result = calculateFinancialHealthScore(metrics)
        
        assert result['overall'] <= 40
        assert result['category'] == 'poor'
        assert result['color'] == 'red'


class TestRecommendations:
    """Test recommendation generation."""
    
    def test_recommendations_for_negative_cash_flow(self):
        """Test that negative cash flow generates appropriate recommendations."""
        metrics = {
            'monthlyIncome': 5000,
            'monthlyExpenses': 6000,
            'monthlySurplus': -1000,  # Negative
            'netWorth': 100000,
            'liquidSavings': 10000,
            'currentAge': 35,
            'annualGrowthRate': 0.05,
            'projectedNetWorth': 200000,
            'retirementReadiness': False
        }
        
        result = calculateFinancialHealthScore(metrics)
        
        recommendations = result['recommendations']
        assert len(recommendations) > 0
        
        # Should recommend action for negative cash flow
        negative_flow_rec = any(
            'cash flow' in rec.lower() or 'expenses' in rec.lower() or 'income' in rec.lower()
            for rec in recommendations
        )
        assert negative_flow_rec
        
    def test_recommendations_for_low_emergency_fund(self):
        """Test that low emergency fund generates appropriate recommendations."""
        metrics = {
            'monthlyIncome': 8000,
            'monthlyExpenses': 6000,
            'monthlySurplus': 2000,
            'netWorth': 300000,
            'liquidSavings': 10000,  # Only ~1.7 months expenses
            'currentAge': 35,
            'annualGrowthRate': 0.07,
            'projectedNetWorth': 800000,
            'retirementReadiness': True
        }
        
        result = calculateFinancialHealthScore(metrics)
        
        recommendations = result['recommendations']
        
        # Should recommend building emergency fund
        emergency_fund_rec = any(
            'emergency' in rec.lower() for rec in recommendations
        )
        assert emergency_fund_rec


class TestScoreConsistency:
    """Test scoring consistency and edge cases."""
    
    def test_score_bounds(self):
        """Test that all scores are within valid bounds (0-100)."""
        metrics = {
            'monthlyIncome': 7000,
            'monthlyExpenses': 5000,
            'monthlySurplus': 2000,
            'netWorth': 400000,
            'liquidSavings': 30000,
            'currentAge': 40,
            'annualGrowthRate': 0.06,
            'projectedNetWorth': 800000,
            'retirementReadiness': True
        }
        
        result = calculateFinancialHealthScore(metrics)
        
        # Overall score bounds
        assert 0 <= result['overall'] <= 100
        
        # Individual component score bounds
        for component in result['breakdown'].values():
            assert 0 <= component['score'] <= 100
            
    def test_weighted_scoring(self):
        """Test that component weights sum to 1.0."""
        metrics = {
            'monthlyIncome': 8000,
            'monthlyExpenses': 6000,
            'monthlySurplus': 2000,
            'netWorth': 500000,
            'liquidSavings': 40000,
            'currentAge': 35,
            'annualGrowthRate': 0.07,
            'projectedNetWorth': 1000000,
            'retirementReadiness': True
        }
        
        result = calculateFinancialHealthScore(metrics)
        
        # Calculate weighted sum manually
        breakdown = result['breakdown']
        weighted_sum = sum(
            component['score'] * component['weight']
            for component in breakdown.values()
        )
        
        # Should approximately equal overall score (within rounding)
        assert abs(weighted_sum - result['overall']) <= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])