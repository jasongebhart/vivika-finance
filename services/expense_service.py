"""
Enhanced service for managing detailed expense breakdowns and line items.
Provides comprehensive expense analysis, categorization, and forecasting.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import copy

logger = logging.getLogger(__name__)

class ExpenseService:
    """Service for enhanced expense management with detailed line items."""
    
    def __init__(self, general_finance_path: str = "general.finance.json"):
        self.general_finance_path = Path(general_finance_path)
        self._expense_config = None
        
        # Location-based cost multipliers
        self.location_multipliers = {
            'Sf': {
                'living': 1.4, 'housing': 2.8, 'utilities': 1.4, 
                'transport': 1.4, 'insurance': 1.4, 'leisure': 1.5
            },
            'Sd': {
                'living': 1.2, 'housing': 1.8, 'utilities': 1.2, 
                'transport': 1.2, 'insurance': 1.2, 'leisure': 1.3
            },
            'Mn': {
                'living': 0.85, 'housing': 0.7, 'utilities': 0.85, 
                'transport': 0.85, 'insurance': 0.85, 'leisure': 0.9
            }
        }
        
        # Category mappings for enhanced functionality
        self.category_mappings = {
            "Ski Team Activities": {
                "path": ["KIDS_ACTIVITIES", "SPORTS", "SKI_TEAM"],
                "multiplier_key": "leisure",
                "category": "Recreation",
                "essential": False
            },
            "Baseball Activities": {
                "path": ["KIDS_ACTIVITIES", "SPORTS", "BASEBALL"],
                "multiplier_key": "leisure", 
                "category": "Recreation",
                "essential": False
            },
            "Utilities": {
                "path": ["UTILITIES"],
                "multiplier_key": "utilities",
                "category": "Housing",
                "essential": True
            },
            "Insurance": {
                "path": ["INSURANCE"],
                "multiplier_key": "insurance",
                "category": "Protection",
                "essential": True
            },
            "Subscriptions": {
                "path": ["SUBSCRIPTIONS"],
                "multiplier_key": "living",
                "category": "Lifestyle",
                "essential": False
            },
            "Transportation": {
                "path": ["TRANSPORTATION"],
                "multiplier_key": "transport",
                "category": "Transportation",
                "essential": True
            },
            "Leisure Activities": {
                "path": ["LEISURE_ACTIVITIES"],
                "multiplier_key": "leisure",
                "category": "Recreation",
                "essential": False
            },
            "Living Expenses": {
                "path": ["LIVING_EXPENSES"],
                "multiplier_key": "living",
                "category": "Basic Needs",
                "essential": True
            },
            "Housing Expenses": {
                "path": ["HOUSING_EXPENSES"],
                "multiplier_key": "housing",
                "category": "Housing",
                "essential": True
            }
        }
    
    def load_expense_config(self) -> Dict[str, Any]:
        """Load the general finance configuration file."""
        if self._expense_config is not None:
            return self._expense_config
            
        try:
            if self.general_finance_path.exists():
                with open(self.general_finance_path, 'r', encoding='utf-8') as f:
                    self._expense_config = json.load(f)
                logger.info(f"Loaded expense configuration from {self.general_finance_path}")
            else:
                logger.warning(f"General finance config not found at {self.general_finance_path}")
                self._expense_config = {}
        except Exception as e:
            logger.error(f"Error loading expense configuration: {e}")
            self._expense_config = {}
            
        return self._expense_config
    
    def get_line_items_for_expense(self, expense_name: str) -> Optional[Dict[str, float]]:
        """Get detailed line items for a specific expense category."""
        config = self.load_expense_config()
        
        if expense_name not in self.category_mappings:
            return None
            
        # Navigate through the nested config structure
        current_level = config
        for key in self.category_mappings[expense_name]["path"]:
            if isinstance(current_level, dict) and key in current_level:
                current_level = current_level[key]
            else:
                return None
        
        # Return the line items if it's a dictionary of key-value pairs
        if isinstance(current_level, dict):
            return current_level
            
        return None
    
    def get_location_adjusted_expense(self, expense: Dict[str, Any], location: str) -> Dict[str, Any]:
        """Adjust expense amounts based on location cost-of-living multipliers."""
        adjusted_expense = copy.deepcopy(expense)
        expense_name = expense.get('name', '')
        
        if expense_name not in self.category_mappings:
            return adjusted_expense
        
        multiplier_key = self.category_mappings[expense_name]["multiplier_key"]
        location_mult = self.location_multipliers.get(location, self.location_multipliers['Sf'])
        multiplier = location_mult.get(multiplier_key, 1.0)
        
        # Adjust the annual amount
        original_amount = expense.get('annual_amount', 0)
        adjusted_expense['annual_amount'] = round(original_amount * multiplier, 2)
        adjusted_expense['location_multiplier'] = multiplier
        adjusted_expense['original_amount'] = original_amount
        
        # Adjust line items if they exist
        if 'line_items' in adjusted_expense:
            adjusted_line_items = {}
            for item_name, monthly_amount in adjusted_expense['line_items'].items():
                adjusted_line_items[item_name] = round(monthly_amount * multiplier, 2)
            adjusted_expense['line_items'] = adjusted_line_items
        
        return adjusted_expense
    
    def analyze_expense_breakdown(self, expenses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Provide comprehensive analysis of expense breakdown."""
        total_annual = sum(exp.get('annual_amount', 0) for exp in expenses)
        
        # Categorize expenses
        categories = {}
        essential_total = 0
        non_essential_total = 0
        
        for expense in expenses:
            expense_name = expense.get('name', '')
            annual_amount = expense.get('annual_amount', 0)
            
            if expense_name in self.category_mappings:
                mapping = self.category_mappings[expense_name]
                category = mapping['category']
                is_essential = mapping['essential']
                
                if category not in categories:
                    categories[category] = {'total': 0, 'expenses': [], 'essential': is_essential}
                
                categories[category]['total'] += annual_amount
                categories[category]['expenses'].append({
                    'name': expense_name,
                    'amount': annual_amount,
                    'percentage': (annual_amount / total_annual * 100) if total_annual > 0 else 0
                })
                
                if is_essential:
                    essential_total += annual_amount
                else:
                    non_essential_total += annual_amount
            else:
                # Handle unmapped expenses
                if 'Other' not in categories:
                    categories['Other'] = {'total': 0, 'expenses': [], 'essential': False}
                categories['Other']['total'] += annual_amount
                categories['Other']['expenses'].append({
                    'name': expense_name,
                    'amount': annual_amount,
                    'percentage': (annual_amount / total_annual * 100) if total_annual > 0 else 0
                })
                non_essential_total += annual_amount
        
        # Calculate percentages for categories
        for category_data in categories.values():
            category_data['percentage'] = (category_data['total'] / total_annual * 100) if total_annual > 0 else 0
        
        return {
            'total_annual': total_annual,
            'total_monthly': total_annual / 12,
            'essential_total': essential_total,
            'non_essential_total': non_essential_total,
            'essential_percentage': (essential_total / total_annual * 100) if total_annual > 0 else 0,
            'categories': categories,
            'summary': {
                'highest_category': max(categories.keys(), key=lambda k: categories[k]['total']) if categories else None,
                'lowest_category': min(categories.keys(), key=lambda k: categories[k]['total']) if categories else None,
                'category_count': len(categories)
            }
        }
    
    def generate_expense_optimization_suggestions(self, expenses: List[Dict[str, Any]], 
                                                target_reduction_percent: float = 10.0) -> Dict[str, Any]:
        """Generate suggestions for optimizing expenses."""
        analysis = self.analyze_expense_breakdown(expenses)
        target_reduction = analysis['total_annual'] * (target_reduction_percent / 100)
        
        suggestions = []
        potential_savings = 0
        
        # Focus on non-essential categories first
        non_essential_expenses = []
        for expense in expenses:
            expense_name = expense.get('name', '')
            if expense_name in self.category_mappings:
                if not self.category_mappings[expense_name]['essential']:
                    non_essential_expenses.append(expense)
        
        # Sort by highest amount first
        non_essential_expenses.sort(key=lambda x: x.get('annual_amount', 0), reverse=True)
        
        for expense in non_essential_expenses:
            expense_name = expense.get('name', '')
            annual_amount = expense.get('annual_amount', 0)
            
            if expense_name == "Subscriptions":
                reduction = annual_amount * 0.3  # Suggest 30% reduction
                suggestions.append({
                    'category': expense_name,
                    'suggestion': 'Review and cancel unused subscriptions',
                    'potential_savings': reduction,
                    'difficulty': 'Easy'
                })
                potential_savings += reduction
            
            elif expense_name == "Leisure Activities":
                reduction = annual_amount * 0.2  # Suggest 20% reduction
                suggestions.append({
                    'category': expense_name,
                    'suggestion': 'Find free/low-cost entertainment alternatives',
                    'potential_savings': reduction,
                    'difficulty': 'Medium'
                })
                potential_savings += reduction
            
            elif "Activities" in expense_name:
                reduction = annual_amount * 0.15  # Suggest 15% reduction
                suggestions.append({
                    'category': expense_name,
                    'suggestion': 'Consider sharing equipment or carpooling',
                    'potential_savings': reduction,
                    'difficulty': 'Medium'
                })
                potential_savings += reduction
        
        # Add essential category suggestions if needed
        if potential_savings < target_reduction:
            remaining_needed = target_reduction - potential_savings
            
            suggestions.append({
                'category': 'Transportation',
                'suggestion': 'Optimize driving routes and maintenance schedules',
                'potential_savings': analysis['categories'].get('Transportation', {}).get('total', 0) * 0.1,
                'difficulty': 'Medium'
            })
            
            suggestions.append({
                'category': 'Utilities',
                'suggestion': 'Implement energy-saving measures',
                'potential_savings': analysis['categories'].get('Housing', {}).get('total', 0) * 0.05,
                'difficulty': 'Easy'
            })
        
        return {
            'target_reduction': target_reduction,
            'potential_total_savings': potential_savings,
            'suggestions': suggestions,
            'feasibility': 'High' if potential_savings >= target_reduction else 'Medium'
        }
    
    def enhance_expense_with_line_items(self, expense: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance an expense dictionary with line item details and metadata."""
        enhanced_expense = expense.copy()
        
        expense_name = expense.get('name', '')
        logger.info(f"Processing expense: {expense_name}")
        
        line_items = self.get_line_items_for_expense(expense_name)
        logger.info(f"Found line items for {expense_name}: {line_items}")
        
        if line_items:
            enhanced_expense['line_items'] = line_items
            
            # Add metadata if available
            if expense_name in self.category_mappings:
                mapping = self.category_mappings[expense_name]
                enhanced_expense['category'] = mapping['category']
                enhanced_expense['essential'] = mapping['essential']
                enhanced_expense['multiplier_key'] = mapping['multiplier_key']
            
            # Verify the line items sum matches the annual amount (approximately)
            line_items_total = sum(line_items.values()) * 12  # Convert monthly to annual
            annual_amount = expense.get('annual_amount', 0)
            
            enhanced_expense['line_items_monthly_total'] = sum(line_items.values())
            enhanced_expense['line_items_annual_total'] = line_items_total
            enhanced_expense['variance'] = abs(line_items_total - annual_amount)
            enhanced_expense['variance_percentage'] = (abs(line_items_total - annual_amount) / annual_amount * 100) if annual_amount > 0 else 0
            
            logger.info(f"Line items total: {line_items_total}, Annual amount: {annual_amount}")
            
            if abs(line_items_total - annual_amount) > annual_amount * 0.1:  # 10% tolerance
                logger.warning(
                    f"Line items total ({line_items_total}) doesn't match annual amount "
                    f"({annual_amount}) for {expense_name}"
                )
        else:
            logger.info(f"No line items found for expense: {expense_name}")
            # Add basic metadata even without line items
            if expense_name in self.category_mappings:
                mapping = self.category_mappings[expense_name]
                enhanced_expense['category'] = mapping['category']
                enhanced_expense['essential'] = mapping['essential']
                enhanced_expense['multiplier_key'] = mapping['multiplier_key']
        
        return enhanced_expense
    
    def enhance_expense_list(self, expenses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance a list of expenses with line item details."""
        return [self.enhance_expense_with_line_items(expense) for expense in expenses]
    
    def get_all_available_line_items(self) -> Dict[str, Dict[str, Any]]:
        """Get all available line item categories and their comprehensive breakdowns."""
        config = self.load_expense_config()
        result = {}
        
        for category_name, mapping in self.category_mappings.items():
            path = mapping["path"]
            current_level = config
            
            for key in path:
                if isinstance(current_level, dict) and key in current_level:
                    current_level = current_level[key]
                else:
                    current_level = None
                    break
            
            if isinstance(current_level, dict):
                monthly_total = sum(current_level.values())
                result[category_name] = {
                    'line_items': current_level,
                    'monthly_total': monthly_total,
                    'annual_total': monthly_total * 12,
                    'category': mapping['category'],
                    'essential': mapping['essential'],
                    'multiplier_key': mapping['multiplier_key']
                }
        
        return result
    
    def compare_expenses_across_locations(self, expenses: List[Dict[str, Any]], 
                                        locations: List[str] = None) -> Dict[str, Any]:
        """Compare expenses across different locations."""
        if locations is None:
            locations = ['Sf', 'Sd', 'Mn']
        
        comparison = {}
        
        for location in locations:
            location_expenses = []
            for expense in expenses:
                adjusted_expense = self.get_location_adjusted_expense(expense, location)
                location_expenses.append(adjusted_expense)
            
            location_analysis = self.analyze_expense_breakdown(location_expenses)
            comparison[location] = {
                'total_annual': location_analysis['total_annual'],
                'total_monthly': location_analysis['total_monthly'],
                'essential_total': location_analysis['essential_total'],
                'non_essential_total': location_analysis['non_essential_total'],
                'categories': location_analysis['categories'],
                'expenses': location_expenses
            }
        
        # Calculate location differences
        base_location = locations[0]
        base_total = comparison[base_location]['total_annual']
        
        for location in locations[1:]:
            current_total = comparison[location]['total_annual']
            comparison[location]['difference_from_base'] = current_total - base_total
            comparison[location]['percentage_difference'] = ((current_total - base_total) / base_total * 100) if base_total > 0 else 0
        
        return {
            'comparison': comparison,
            'locations': locations,
            'base_location': base_location,
            'summary': {
                'cheapest_location': min(locations, key=lambda loc: comparison[loc]['total_annual']),
                'most_expensive_location': max(locations, key=lambda loc: comparison[loc]['total_annual']),
                'max_savings': max([comparison[loc].get('difference_from_base', 0) for loc in locations[1:]]) * -1 if len(locations) > 1 else 0
            }
        }

# Global instance
expense_service = ExpenseService()