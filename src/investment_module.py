import sys  # import the sys module
from pathlib import Path
import json
import argparse
from collections import namedtuple
import report_html_generator
from utils import format_currency

CAPITAL_GAIN_EXCLUSION = 500000

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process financial configuration.')
    parser.add_argument('config_file_path', nargs='?', default='config.finance.json', help='Path to the configuration file')
    return parser.parse_args()

def calculate_future_value(principal, contribution, increase_contribution, interest_rate, years):
    """
    Calculates the future value of an investment with either an increasing annual contribution
    or a constant annual contribution and compounding interest.

    Args:
        principal (float): Initial investment amount.
        contribution (float): Initial annual contribution amount (base amount).
        increase_contribution (float): Annual increase amount for contribution (if applicable).
        interest_rate (float): Annual interest rate.
        years (int): Number of years.

    Returns:
        The future value of the investment after the specified years.
    """
    future_value = principal
    for year in range(years):
        # Calculate contribution for the year
        yearly_contribution = contribution + year * increase_contribution if increase_contribution > 0 else contribution
        future_value *= (1 + interest_rate)  # Apply interest
        future_value += yearly_contribution  # Add contribution
    return future_value

def calculate_future_value_byrate(present_value, annual_growth_rate, years):
    """
    Calculate the future value of an investment using compound interest formula.

    Args:
        present_value (float): The present value of the investment.
        annual_growth_rate (float): The annual growth rate as a decimal (e.g., 0.05 for 5%).
        years (int): The number of years the investment will grow.

    Returns:
        float: The future value of the investment.
    """
    future_value = present_value * (1 + annual_growth_rate) ** years
    return future_value

def calculate_total_expense(config_data):
    """
    Calculates the total expenses for the next n years based on the provided annual expenses (handles potential missing keys using defaults).

    Args:
        config_data (dict): Dictionary containing keys 'college_expenses' (optional), 'highschool_expenses' (optional), and 'years' (optional).

    Returns:
        tuple: A tuple containing total expense, high school total expense, and college total expense.
               (total_expense, highschool_total_expense, college_total_expense)
    """
    total_expense = 0
    total_highschool_expense = 0
    total_college_expense = 0
    years = config_data.get('years', 0)  # Get 'years' with default 0 if missing

    # Check if 'years' is present and greater than 0 to avoid empty list access errors
    if years > 0:
        college_expenses = config_data.get('college_expenses', [])
        highschool_expenses = config_data.get('highschool_expenses', [])
        
        # Calculate total expenses for the given number of years
        for i in range(years):
            college_expense = college_expenses[i] if i < len(college_expenses) else 0
            highschool_expense = highschool_expenses[i] if i < len(highschool_expenses) else 0
            total_college_expense += college_expense
            total_highschool_expense += highschool_expense
            total_expense += college_expense + highschool_expense

    return total_expense, total_highschool_expense, total_college_expense


def calculate_balance(balance, interest_rate, years, yearly_gain=0, gains=[], expenses=[], yearly_expense=0):
    """
    Calculates the ending balance with compounding interest, considering yearly
    net gains or expenses.

    Args:
        balance (float): Initial investment amount.
        interest_rate (float): Annual interest rate.
        years (int): Number of years.
        yearly_gain (float, optional): Constant yearly gain (default: 0).
        gains (list of float, optional): A list of annual gains (default: []).
        expenses (list of float, optional): A list of annual expenses (default: []).
        yearly_expense (float, optional): An additional annual expense (default: 0).

    Returns:
        float: The ending balance after considering compounding interest and net gains/expenses.
    """
    for year in range(years):
        interest = balance * interest_rate
        net_gain = yearly_gain if yearly_gain != 0 else gains[year] if year < len(gains) else 0
        net_expense = expenses[year] if year < len(expenses) else 0
        balance += interest + net_gain - net_expense - yearly_expense
    return balance


def calculate_expenses(college_expenses, highschool_expenses):
    """
    Calculates the total expenses by summing up the college and high school expenses.

    Args:
        college_expenses (list of float): A list of college expenses for each year.
        highschool_expenses (list of float): A list of high school expenses for each year.

    Returns:
        list of float: The total expenses for each year.
    """
    return [college + highschool for college, highschool in zip(college_expenses, highschool_expenses)]

def calculate_remaining_principal(original_principal, interest_rate, months_to_pay, number_of_payments):
    """
    This function calculates the remaining principal on a loan.

    Args:
        original_principal (float): The original amount borrowed.
        interest_rate (float): The monthly interest rate (as a decimal).
        months_to_pay (int): The number of months already paid.
        number_of_payments (int): The total number of loan payments.

    Returns:
        float: The remaining principal balance after a certain number of payments.
    """
    import math

    # Check if original_principal, interest_rate, months_to_pay, and number_of_payments are of the correct types
    if not all(isinstance(x, (int, float)) for x in [original_principal, interest_rate, months_to_pay, number_of_payments]):
        raise TypeError("All input parameters must be of type int or float")

    # Check if any input parameters are negative
    if original_principal < 0 or interest_rate < 0 or months_to_pay < 0 or number_of_payments < 0:
        raise ValueError("All input parameters must be non-negative")

    # Check if months_to_pay or number_of_payments is zero
    if months_to_pay == 0 or number_of_payments == 0:
        return 0  # Return 0 if either months_to_pay or number_of_payments is zero

    # Calculate the remaining principal using the loan amortization formula
    remaining_principal = int(original_principal * ((1 + interest_rate/12)**number_of_payments - (1 + interest_rate/12)**months_to_pay) / ((1 + interest_rate/12)**number_of_payments - 1))

    # Check if the result is NaN
    if math.isnan(remaining_principal):
        raise ValueError("Calculation resulted in NaN")

    return remaining_principal


class House:
    def __init__(self, cost_basis=0, closing_costs=0, home_improvement=0, value=0, mortgage_principal=0, 
                 commission_rate=0.0, annual_growth_rate=0.0461, interest_rate=0.0262, 
                 monthly_payment=8265.21, number_of_payments=248, sell_house=False):
        """
        Initializes a House object with its purchase costs, value, and mortgage details.

        Args:
            cost_basis (float, optional): The original purchase price of the house. (default: 0)
            closing_costs (float, optional): Closing costs associated with the purchase. (default: 0)
            home_improvement (float, optional): Cost of home improvements made. (default: 0)
            value (float, optional): The current market value of the house. (default: 0)
            mortgage_principal (float, optional): The remaining principal balance on the mortgage. (default: 0)
            commission_rate (float, optional): The commission rate for selling the house. (default: 0.0)
            annual_growth_rate (float, optional): The annual growth rate of the house value. (default: 0.0461)
            interest_rate (float, optional): The annual interest rate of the mortgage. (default: 0.0262)
            monthly_payment (float, optional): The monthly mortgage payment. (default: 8265.21)
            number_of_payments (int, optional): The total number of mortgage payments. (default: 248)
            sell_house (bool, optional): Indicates if the house is to be sold. (default: False)
        """
        self.cost_basis = cost_basis
        self.closing_costs = closing_costs
        self.home_improvement = home_improvement
        self.value = value
        self.mortgage_principal = mortgage_principal
        self.commission_rate = commission_rate
        self.annual_growth_rate = annual_growth_rate
        self.interest_rate = interest_rate
        self.monthly_payment = monthly_payment
        self.number_of_payments = number_of_payments
        self.sell_house = sell_house

    def __str__(self):
        """
        Returns a string representation of the House object.
        """
        return f"House Object:\nCost Basis: ${self.cost_basis}\nClosing Costs: ${self.closing_costs}\n" \
               f"Home Improvement Costs: ${self.home_improvement}\nCurrent Value: ${self.value}\n" \
               f"Mortgage Principal: ${self.mortgage_principal}\nCommission Rate: {self.commission_rate}\n" \
               f"Annual Growth Rate: {self.annual_growth_rate}\nInterest Rate: {self.interest_rate}\n" \
               f"Monthly Payment: ${self.monthly_payment}\nNumber of Payments: {self.number_of_payments}\n" \
               f"Sell House: {self.sell_house}"

    def calculate_basis(self):
        """
        Calculates the total basis of the house considering purchase costs and improvements.

        Returns:
            float: The total basis of the house.
        """
        return self.cost_basis + self.closing_costs + self.home_improvement

    def calculate_sale_basis(self, commission_rate=0.06):
        """
        Calculates the sale basis and commission, considering the house value, commission rate, and escrow.

        Args:
            commission_rate (float, optional): The commission rate for selling the house (default: 0.06).

        Returns:
            tuple: A tuple containing the sale basis and the commission amount.
        """
        escrow_rate = 0.002
        escrow = self.value * escrow_rate
        commission = self.value * commission_rate
        sale_basis = self.value - commission - escrow

        return sale_basis, commission

    def calculate_capital_gains(self):
        """
        Calculates the capital gains tax on selling the house, considering exclusion.

        Returns:
            float: The amount of capital gains tax to be paid.
        """
        sale_basis, commission = self.calculate_sale_basis()  # Unpack the tuple
        capital_gain = sale_basis - self.calculate_basis()
        return max(0, capital_gain - CAPITAL_GAIN_EXCLUSION)

    def calculate_net_worth(self):
        """
        Calculates the net worth of the house, considering its value and mortgage principal.

        Returns:
            float: The net worth of the house (value minus mortgage principal).
        """
        return self.value - self.mortgage_principal

    def calculate_future_investment(self, invest_capital, interest_rate, years):
        """
        Calculates the future value of capital invested after selling the house

        Args:
            invest_capital (float): The amount of capital available for investment after selling the house.
            interest_rate (float): The annual interest rate for the investment.
            years (int): The number of years for the investment.

        Returns:
            float: The future value of the investment after the specified years.
        """
        return calculate_future_value(invest_capital, 0, 0, interest_rate, years)

def load_config(config_file_path):
    try:
        with open(config_file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config file '{config_file_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Invalid JSON format in '{config_file_path}'.")
        sys.exit(1)


def calculate_house_values(current_house, config_data):
    # Calculate sale basis and capital gains for the current house
    commission_rate_myhouse = config_data['house']['commission_rate']
    sale_basis, total_commission = current_house.calculate_sale_basis(commission_rate=commission_rate_myhouse)
    capital_gain = current_house.calculate_capital_gains()
    house_net_worth = current_house.calculate_net_worth()
    capital_from_house = sale_basis - current_house.mortgage_principal - capital_gain
    return sale_basis, total_commission, capital_gain, house_net_worth, capital_from_house

def calculate_new_house_values(new_house, capital_from_house, config_data):
    if not new_house:
        return 0, 0, 0, 0, 0, 0, 0, 0  # Return default values if there's no new house

    # Calculate sale basis and capital gains for the new house
    commission_rate_newhouse = config_data['new_house']['commission_rate']
    new_house_sale_basis, new_house_total_commission = new_house.calculate_sale_basis(commission_rate=commission_rate_newhouse)
    new_house_capital_gain = new_house.calculate_capital_gains()
    
    # Set the new_house_value
    new_house_cost = config_data['new_house']['cost_basis']
    house_value_rate = config_data.get('house_value_rate', 1.0)
    new_house_value = new_house_cost * house_value_rate
    new_house_fees = new_house_cost * .01
    
    # Calculate the investment capital from the sale of the current house
    invest_capital = capital_from_house - new_house_cost - new_house_fees
    interest_rate = config_data['interest_rate']
    years = config_data['years']
    house_capital_investment = calculate_future_value(invest_capital, 0, 0, interest_rate, years)

    return (new_house_sale_basis, new_house_total_commission, new_house_capital_gain,
            new_house_cost, new_house_value, new_house_fees, 
            invest_capital, house_capital_investment)

def initialize_variables():
    return 0, 0, 0

def calculate_yearly_income(config_data, tax_rate):
    spouse1_yearly_income = config_data['spouse1_yearly_income_base'] + config_data['spouse1_yearly_income_bonus'] + config_data['spouse1_yearly_income_quarterly']
    spouse1_pre_tax_investments = config_data.get("SPOUSE1_PRETAX_INVESTMENTS", {})
    spouse1_total_pre_tax_investments = sum(spouse1_pre_tax_investments.values())
    spouse1_income_after_pretax_items = int(spouse1_yearly_income - spouse1_total_pre_tax_investments)
    spouse1_income_after_taxes = int(spouse1_income_after_pretax_items * (1 - tax_rate))
    spouse1_post_tax_investments = config_data.get("SPOUSE1_POSTTAX_INVESTMENTS", {})
    spouse1_total_post_tax_investments = sum(spouse1_post_tax_investments.values())
    spouse1_income_after_posttax_items = int(spouse1_income_after_taxes - spouse1_total_post_tax_investments)

    spouse2_yearly_income_base = config_data.get('spouse2_yearly_income_base')
    if spouse2_yearly_income_base != 0:
        spouse2_yearly_income = config_data['spouse2_yearly_income_base'] + config_data['spouse2_yearly_income_bonus'] + config_data['spouse2_yearly_income_quarterly']
        spouse2_pre_tax_investments = config_data.get("SPOUSE2_PRETAX_INVESTMENTS", {})
        spouse2_total_pre_tax_investments = sum(spouse2_pre_tax_investments.values())
        spouse2_income_after_pretax_items = int(spouse2_yearly_income - spouse2_total_pre_tax_investments)
        spouse2_income_after_taxes = int(spouse2_income_after_pretax_items * (1 - tax_rate))
        spouse2_post_tax_investments = config_data.get("SPOUSE2_POSTTAX_INVESTMENTS", {})
        spouse2_total_post_tax_investments = sum(spouse2_post_tax_investments.values())
        spouse2_income_after_posttax_items = int(spouse2_income_after_taxes - spouse2_total_post_tax_investments)

        yearly_income = spouse1_income_after_posttax_items + spouse2_income_after_posttax_items
    else:
        spouse2_yearly_income = 0
        spouse2_income_after_posttax_items = 0
        spouse2_total_post_tax_investments = 0
        spouse2_total_pre_tax_investments = 0
        spouse2_income_after_taxes = 0
        spouse2_income_after_pretax_items = 0
        yearly_income = spouse1_income_after_posttax_items

    yearly_data = {
        "Spouse 1 Yearly Income Combined": spouse1_yearly_income,
        "Spouse 1 Yearly Income Base": config_data.get('spouse1_yearly_income_base', 'Not found'),
        "Spouse 1 Yearly Income Bonus": config_data.get('spouse1_yearly_income_bonus', 'Not found'),
        "Spouse 1 Yearly Income Bonus Quarterly": config_data.get('spouse1_yearly_income_quarterly', 'Not found'),
        "Spouse 1 Total Pre-Tax Investments": spouse1_total_pre_tax_investments,
        "Spouse 1 Total Post-Tax Investments": spouse1_total_post_tax_investments,
        "Spouse 1 After Pre-Tax Investments": spouse1_income_after_pretax_items,
        f"Spouse 1 After tax ({tax_rate})": spouse1_income_after_taxes,
        "Spouse 1 After-Tax Investment Income": spouse1_income_after_posttax_items,
        "Spouse 2 Yearly Income Combined": spouse2_yearly_income,
        "Spouse 2 Yearly Income Base": config_data.get('spouse2_yearly_income_base', 'Not found'),
        "Spouse 2 Yearly Income Bonus": config_data.get('spouse2_yearly_income_bonus', 'Not found'),
        "Spouse 2 Yearly Income Quarterly": config_data.get('spouse2_yearly_income_quarterly', 'Not found'),
        "Spouse 2 Total Pre-Tax Investments": spouse2_total_pre_tax_investments,
        "Spouse 2 Total Post-Tax Investments": spouse2_total_post_tax_investments,
        "Spouse 2 After Pre-Tax Investments": spouse2_income_after_pretax_items,
        f"Spouse 2 After tax ({tax_rate})": spouse2_income_after_taxes,
        "Spouse 2 After-Tax Investment Income": spouse2_income_after_posttax_items,
        "Yearly Net Income": yearly_income
    }
    return yearly_data

def calculate_yearly_surplus(monthly_surplus):
  """Calculates the yearly surplus based on the provided monthly surplus.

  Args:
      monthly_surplus: The amount of surplus each month.

  Returns:
      The total surplus for the year.
  """
  yearly_surplus = monthly_surplus * 12
  return yearly_surplus

def determine_surplus_type(yearly_surplus):
  """Determines if the surplus is positive (gain) or negative (expense).

  Args:
      yearly_surplus: The total surplus for the year.

  Returns:
      A string indicating "Gain" if positive, "Expense" if negative, or "No Surplus/Expense" if zero.
  """
  if yearly_surplus > 0:
      return "Gain"
  elif yearly_surplus < 0:
      return "Expense"
  else:
      return "No Surplus/Expense"

def format_currency(value):
  """Formats a numerical value as currency with commas."""
  return "${:,.0f}".format(value)

def can_cover_school_expenses_per_year(yearly_surplus, school_expenses):
    """
    Checks if the yearly surplus can cover school expenses for each year.

    Args:
        yearly_surplus: The annual surplus amount.
        school_expenses: A list of high school expenses for each year.

    Returns:
        A list of tuples containing (year, covered, remaining_surplus/deficit).
    """

    # Ensure lists have the same length
    if len(yearly_surplus) != len(school_expenses):
        raise ValueError("Yearly surplus and high school expenses lists must have the same length.")

    report = []
    for year, expense in enumerate(school_expenses):
        if yearly_surplus[year] <= 0:  # If yearly surplus is zero or negative
            surplus_used = 0  # No surplus available
            remaining_surplus = 0  # Remaining surplus is also zero
            covered = False  # Expense not covered
            deficit = expense  # Full expense is a deficit
        else:
            surplus_used = min(expense, yearly_surplus[year])  # Use surplus for current year
            remaining_surplus = yearly_surplus[year] - surplus_used
            covered = surplus_used >= expense  # True if expense is covered, False otherwise
            deficit = expense - surplus_used if not covered else 0  # Calculate deficit if expense is not covered
        report.append((year + 1, covered, remaining_surplus, deficit))

    return report


def get_work_status(spouse1_income, spouse2_income):
    """
    Determines the work status based on spouse incomes.

    Args:
        spouse1_income: Spouse 1's base yearly income (numerical value, 0, or None).
        spouse2_income: Spouse 2's base yearly income (numerical value, 0, or None).

    Returns:
        A string indicating the work status ("Both Parents Work", "One Parent Works", or "No Parents Work").
    """
    if spouse1_income is not None and spouse2_income is not None and spouse1_income > 0 and spouse2_income > 0:
        return "Both Parents Work"
    elif (spouse1_income is not None and spouse1_income > 0) or (spouse2_income is not None and spouse2_income > 0):
        return "One Parent Works"
    else:
        return "No Parents Work"

def calculate_tax_rate(config_data):
    spouse2_yearly_income_base = config_data.get('spouse2_yearly_income_base', 0)
    if spouse2_yearly_income_base:
        return config_data['federal_tax_rate_dual'] + config_data['state_tax_rate_dual']
    return config_data['federal_tax_rate_single'] + config_data['state_tax_rate_single']

# Function to parse config
def parse_config(args):
    config_data = load_config(args.config_file_path)
    tax_rate = calculate_tax_rate(config_data)
    return config_data, tax_rate

def calculate_total_monthly_expenses(config_data):
    monthly_expenses_breakdown = {
        "Mortgage": config_data['mortgage'],
        "Yearly Property Tax": int(config_data['yearly_property_tax'] / 12),
        "Ski Team": int(sum(config_data.get("SKI_TEAM", {}).values()) / 12),
        "Baseball Team": int(sum(config_data.get("BASEBALL_TEAM", {}).values()) / 12),
        "Utilities": sum(config_data.get("UTILITIES", {}).values()),
        "Insurance": sum(config_data.get("INSURANCE", {}).values()),
        "Subscriptions": sum(config_data.get("SUBSCRIPTIONS", {}).values()),
        "Car Expenses": sum(config_data.get("CAR_MONTHLY", {}).values()),
        "Groceries": config_data.get('Groceries', 0),
        "Jiujitsu": config_data.get('jiujitsu', 0),
        "House Maintenance": config_data.get('monthly_house_maintenance', 0),
        "Bike Maintenance": config_data.get('bike_maintenance', 0),
        "Clothing": config_data.get('monthly_clothing', 0)
    }
    total_monthly_expenses = sum(monthly_expenses_breakdown.values())
    return total_monthly_expenses, monthly_expenses_breakdown

def initialize_house_variables(config_data):
    """
    Initialize relevant variables based on configuration data.

    Args:
    - config_data (dict): Configuration data for the financial scenario.

    Returns:
    - tuple: A tuple containing the initialized variables.
    """

    # Create House instances
    current_house = create_house_instance(config_data['house'])
    new_house = create_house_instance(config_data.get('new_house'))

    return current_house, new_house

def create_house_instance(house_data):
    """
    Create a House instance based on configuration data.

    Args:
    - house_data (dict): Configuration data for the house.

    Returns:
    - House: An instance of the House class.
    """
    if house_data:
        return House(**house_data)
    else:
        return None


def calculate_combined_net_worth(config_data, house_net_worth):
    """
    Calculate the combined net worth.

    Args:
    - config_data (dict): Configuration data for the financial scenario.
    - house_net_worth (float): Net worth of the house.

    Returns:
    - float: Combined net worth.
    """
    return config_data['investment_balance'] + config_data['retirement_principal'] + house_net_worth

def calculate_financial_data(config_data, tax_rate):
    yearly_data = calculate_yearly_income(config_data, tax_rate)
    total_monthly_expenses, monthly_expenses_breakdown = calculate_total_monthly_expenses(config_data)
    return yearly_data, total_monthly_expenses, monthly_expenses_breakdown

def calculate_expenses_not_factored_in_report(config_data):
    expenses_not_factored_in_report = {
        "Total Widji": config_data.get('total_widji'),
        "Total Ski Camp": config_data.get('Total_ski_camp'),
        "Car Purchase": config_data.get('car_purchase'),
    }
    monthly_expenses = {f"Monthly {key}": int(value / 12) for key, value in expenses_not_factored_in_report.items()}
    expenses_not_factored_in_report.update(monthly_expenses)
    return expenses_not_factored_in_report

def calculate_surplus(yearly_data, total_monthly_expenses):
    yearly_income = yearly_data["Yearly Net Income"]
    monthly_surplus = int(yearly_income / 12) - int(total_monthly_expenses)
    yearly_gain = calculate_yearly_surplus(monthly_surplus)
    surplus_type = determine_surplus_type(yearly_gain)
    return yearly_gain, surplus_type, monthly_surplus


def calculate_income_expenses(config_data, tax_rate):
    yearly_data, total_monthly_expenses, monthly_expenses_breakdown = calculate_financial_data(config_data, tax_rate)
    yearly_gain, surplus_type, monthly_surplus = calculate_surplus(yearly_data, total_monthly_expenses)
    
    # Calculate expenses
    total_expense, total_highschool_expense, total_college_expense = calculate_total_expense(config_data)
    yearly_income_deficit = int(config_data['yearly_expense'])
    expenses_not_factored_in_report = calculate_expenses_not_factored_in_report(config_data)
    
    # Add expenses to the income_calculated_data dictionary
    calculated_data = {
        "yearly_data": yearly_data,
        "total_monthly_expenses": total_monthly_expenses,
        "monthly_expenses_breakdown": monthly_expenses_breakdown,
        "yearly_gain": yearly_gain,
        "surplus_type": surplus_type,
        "monthly_surplus": monthly_surplus,
        "total_expense": total_expense,
        "total_highschool_expense": total_highschool_expense,
        "total_college_expense": total_college_expense,
        "yearly_income_deficit": yearly_income_deficit,
        "expenses_not_factored_in_report": expenses_not_factored_in_report
    }
    
    return calculated_data

def calculate_investment_values(config_data, yearly_gain):
    total_employee_stockplan = calculate_future_value(
        config_data.get('employee_stock_purchase', 0), config_data.get('employee_stock_purchase', 0),
        increase_contribution=0, interest_rate=config_data.get('interest_rate', 0), years=config_data.get('years', 0))
    school_expenses = [a + b for a, b in zip(config_data.get('college_expenses', []), config_data.get('highschool_expenses', []))]
    balance_with_expenses = calculate_balance(
        config_data.get('investment_balance', 0), config_data.get('interest_rate', 0), config_data.get('years', 0),
        yearly_gain=yearly_gain, gains=config_data.get('gains', 0), expenses=school_expenses,
        yearly_expense=config_data.get('yearly_expense', 0))
    future_retirement_value_contrib = calculate_future_value(
        config_data.get('retirement_principal', 0), config_data.get('initial_contribution', 0),
        config_data.get('increase_contribution', 0), config_data.get('interest_rate', 0), config_data.get('years', 0))
    
    # Return variables as a dictionary
    return {
        "total_employee_stockplan": total_employee_stockplan,
        "school_expenses": school_expenses,
        "balance_with_expenses": balance_with_expenses,
        "future_retirement_value_contrib": future_retirement_value_contrib
    }

def calculate_future_house_values(new_house, config_data, current_house, new_house_value):
  """Calculate future house net worth and combined net worth."""
  if new_house:
    house_networth_future = new_house_value
    remaining_principal = None
    house_value_future = None
  else:
    house_value_future = calculate_future_value_byrate(current_house.value, current_house.annual_growth_rate, config_data.get('years', 0))
    remaining_principal = calculate_remaining_principal(
        current_house.mortgage_principal, current_house.interest_rate,
        (config_data.get('years', 0) * 12), current_house.number_of_payments)
    house_networth_future = house_value_future - remaining_principal
  return house_networth_future, house_value_future, remaining_principal

def calculate_future_net_worth_houseinfo(new_house, calculated_data, house_info):
    """Calculate future house net worth and combined net worth."""
    future_retirement_value_contrib = calculated_data["future_retirement_value_contrib"]
    balance_with_expenses = calculated_data["balance_with_expenses"]
    total_employee_stockplan = calculated_data["total_employee_stockplan"]

    if new_house:
        combined_networth_future = future_retirement_value_contrib + house_info["new_house_value"] + balance_with_expenses + house_info["house_capital_investment"] + total_employee_stockplan
    else:
        combined_networth_future = future_retirement_value_contrib + balance_with_expenses + house_info["house_networth_future"] + total_employee_stockplan

    return combined_networth_future


def calculate_financial_values(config_data, tax_rate):
    """Calculate financial values."""
    calculated_data = calculate_income_expenses(config_data, tax_rate)
    investment_values = calculate_investment_values(config_data, calculated_data["yearly_gain"])
    
    # Combine calculated_data and investment_values into one dictionary
    calculated_data = calculated_data.copy()  # Create a copy of calculated_data
    calculated_data.update(investment_values)  # Update with investment_values
    
    return calculated_data



def calculate_house_dataold(current_house, config_data, new_house):
  """
  This function calculates all house related information.

  Args:
      current_house: Dictionary containing current house information.
      config_data: Dictionary containing configuration data.
      new_house: Boolean indicating if buying a new house.

  Returns:
      A dictionary containing various house related information.
  """
  sale_basis, total_commission, capital_gain, house_net_worth, capital_from_house = calculate_house_values(current_house, config_data)
  if not new_house:
    new_house_cost = new_house_value = new_house_fees = invest_capital = house_capital_investment = 0
  else:
    new_house_sale_basis, new_house_total_commission, new_house_capital_gain, new_house_cost, new_house_value, new_house_fees, invest_capital, house_capital_investment = calculate_new_house_values(new_house, capital_from_house, config_data)
  house_networth_future, house_value_future, remaining_principal = calculate_future_house_values(new_house, config_data, current_house, new_house_value)
  
  return {
      "sale_basis": sale_basis,
      "total_commission": total_commission,
      "capital_gain": capital_gain,
      "house_value_future": house_value_future,
      "house_net_worth": house_net_worth,
      "capital_from_house": capital_from_house,
      "new_house": new_house,
      "new_house_cost": new_house_cost,
      "new_house_value": new_house_value,
      "new_house_fees": new_house_fees,
      "invest_capital": invest_capital,
      "house_capital_investment": house_capital_investment,
      "house_networth_future": house_networth_future, 
      "remaining_principal": remaining_principal,
  }

def calculate_house_data(current_house, config_data, new_house):
    """
    This function calculates all house related information.

    Args:
        current_house: Dictionary containing current house information.
        config_data: Dictionary containing configuration data.
        home_tenure: String indicating whether the home is owned or rented. Default is "own".

    Returns:
        A dictionary containing various house related information.
    """
    if config_data["home_tenure"] == "Own":
        sale_basis, total_commission, capital_gain, house_net_worth, capital_from_house = calculate_house_values(current_house, config_data)
        if not new_house:
            new_house_cost = new_house_value = new_house_fees = invest_capital = house_capital_investment = 0
        else:
            new_house_sale_basis, new_house_total_commission, new_house_capital_gain, new_house_cost, new_house_value, new_house_fees, invest_capital, house_capital_investment = calculate_new_house_values(new_house, capital_from_house, config_data)
        
    elif config_data["home_tenure"] == "Rent":
        # Calculate house-related values for renting
        sale_basis, total_commission, capital_gain, house_net_worth, capital_from_house = calculate_house_values(current_house, config_data)
        new_house_cost = new_house_value = new_house_fees = invest_capital = 0
        house_value_future = house_networth_future = remaining_principal = 0
        new_house_sale_basis, new_house_total_commission, new_house_capital_gain, new_house_cost, new_house_value, new_house_fees, invest_capital, house_capital_investment = calculate_new_house_values(new_house, capital_from_house, config_data)

        
        # Here, you can sell the current house and invest the money if desired
    else:
        raise ValueError("Invalid value for home_tenure. Use 'own' or 'rent'.")
    house_networth_future, house_value_future, remaining_principal = calculate_future_house_values(new_house, config_data, current_house, new_house_value)    
    return {
        "sale_basis": sale_basis,
        "total_commission": total_commission,
        "capital_gain": capital_gain,
        "house_value_future": house_value_future,
        "house_net_worth": house_net_worth,
        "capital_from_house": capital_from_house,
        "new_house": new_house,
        "new_house_cost": new_house_cost,
        "new_house_value": new_house_value,
        "new_house_fees": new_house_fees,
        "invest_capital": invest_capital, 
        "house_capital_investment": house_capital_investment,
        "house_networth_future": house_networth_future,
        "remaining_principal": remaining_principal,
    }



def calculate_house_info(config_data):
    current_house, new_house = initialize_house_variables(config_data)
    house_info = calculate_house_data(current_house=current_house, config_data=config_data, new_house=new_house)
    return current_house, new_house, house_info


def calculate_school_expense_coverage(calculated_data):
    """
    Calculate the coverage of school expenses for each year.

    Args:
    - calculated_data (dict): Dictionary containing financial data.

    Returns:
    - school_expense_coverage (list): List containing coverage of school expenses for each year.
    """
    yearly_gain = calculated_data.get("yearly_gain", 0)
    yearly_surplus = max(yearly_gain, 0)
    school_expenses = calculated_data.get("school_expenses", [])
    return can_cover_school_expenses_per_year([yearly_surplus] * len(school_expenses), school_expenses)

def calculate_expenses_and_net_worth(config_data, calculated_data, house_info):
    """
    Calculate the coverage of school expenses for each year and net worth.

    Args:
    - config_data (dict): Configuration data for the financial scenario.
    - calculated_data (dict): Calculated financial values.
    - house_info (dict): Dictionary containing house information.

    Returns:
    None
    """
    # Calculate the coverage of school expenses for each year
    calculated_data["school_expense_coverage"] = calculate_school_expense_coverage(calculated_data)
    calculated_data["LIVING_EXPENSES"] = calculate_living_expenses(config_data, calculated_data)

    # Calculate combined net worth
    calculated_data["combined_networth"] = calculate_combined_net_worth(config_data, house_info["house_net_worth"])
    calculated_data["combined_networth_future"] = calculate_future_net_worth_houseinfo(
        house_info["new_house"],
        calculated_data,
        house_info
    )

def calculate_living_expenses(config_data, calculated_data):
    """
    Calculate living expenses and location data.

    Args:
    - config_data (object): Object containing configuration data for the financial scenario.
    - calculated_data (object): Object containing calculated data for the financial scenario.

    Returns:
    - living_expenses_data (dict): Dictionary containing living expenses and location data.
    """
    years = config_data["years"]
    # Calculate living expenses data
    living_expenses_data = {
        "Live in": config_data["residence_location"],
        "Work Status": get_work_status(config_data["spouse1_yearly_income_base"],
                                        config_data["spouse2_yearly_income_base"]),
        "High School": config_data["highschool"],
        "Home Tenure": config_data["home_tenure"],
        "Yearly Income Surplus": format_currency(calculated_data["yearly_gain"]),
        "Avg. Yearly School Fee": format_currency(calculated_data["total_expense"] / years),
        "Yearly Net Minus School ": format_currency((calculated_data["yearly_gain"]) - (calculated_data["total_expense"] / years))
    }
    return living_expenses_data

def adjust_config(config_data, years_override, include_ski_team, ski_team_data, include_baseball_team, baseball_team_data, include_highschool_expenses, highschool_expenses_data):
    """
    Adjusts the configuration dictionary based on the provided parameters.

    Parameters:
    config_data (dict): The configuration dictionary to adjust.
    years_override (int or None): The years override value.
    include_ski_team (str): Option to include, exclude, or use defined ski team data.
    ski_team_data (dict): The ski team data to include.
    include_baseball_team (str): Option to include, exclude, or use defined baseball team data.
    baseball_team_data (dict): The baseball team data to include.
    include_highschool_expenses (str): Option to include, exclude, or use defined high school expenses data.
    highschool_expenses_data (list): The high school expenses data to include.
    """
    if years_override is not None:
        config_data["years"] = years_override

    # Adjust SKI_TEAM data
    if include_ski_team == "exclude":
        config_data["SKI_TEAM"] = {}
    elif include_ski_team == "use_defined":
        ski_team_years = config_data["SKI_TEAM"].get("ski_team_years", 1)
        adjusted_ski_team_data = {
            key: (value if key == "ski_team_years" else (value if ski_team_years == 1 else 0))
            for key, value in config_data["SKI_TEAM"].items()
        }
        config_data["SKI_TEAM"] = adjusted_ski_team_data
    else:
        ski_team_years = ski_team_data.get("ski_team_years", 1)
        adjusted_ski_team_data = {
            key: (value if key == "ski_team_years" else (value if ski_team_years == 1 else 0))
            for key, value in ski_team_data.items()
        }
        config_data["SKI_TEAM"] = adjusted_ski_team_data

    # Adjust BASEBALL_TEAM data
    if include_baseball_team == "exclude":
        config_data["BASEBALL_TEAM"] = {}
    elif include_baseball_team == "use_defined":
        baseball_team_years = config_data["BASEBALL_TEAM"].get("baseball_team_years", 1)
        adjusted_baseball_team_data = {
            key: (value if key == "baseball_team_years" else (value if baseball_team_years == 1 else 0))
            for key, value in config_data["BASEBALL_TEAM"].items()
        }
        config_data["BASEBALL_TEAM"] = adjusted_baseball_team_data
    else:
        baseball_team_years = baseball_team_data.get("baseball_team_years", 1)
        adjusted_baseball_team_data = {
            key: (value if key == "baseball_team_years" else (value if baseball_team_years == 1 else 0))
            for key, value in baseball_team_data.items()
        }
        config_data["BASEBALL_TEAM"] = adjusted_baseball_team_data

    # Adjust highschool_expenses data
    if include_highschool_expenses == "exclude":
        config_data["highschool_expenses"] = [0] * len(config_data.get("highschool_expenses", [0]*9))
    elif include_highschool_expenses == "use_defined":
        config_data["highschool_expenses"] = config_data.get("highschool_expenses", [0]*9)
    else:
        config_data["highschool_expenses"] = highschool_expenses_data


def adjust_configOLD(config_data, years_override, include_ski_team, ski_team_data, include_baseball_team, baseball_team_data, include_highschool_expenses, highschool_expenses_data):
    """
    Adjusts the configuration dictionary based on the provided parameters.

    Parameters:
    config_data (dict): The configuration dictionary to adjust.
    years_override (int or None): The years override value.
    include_ski_team (str): Option to include, exclude, or use defined ski team data.
    ski_team_data (dict): The ski team data to include.
    include_baseball_team (str): Option to include, exclude, or use defined baseball team data.
    baseball_team_data (dict): The baseball team data to include.
    include_highschool_expenses (str): Option to include, exclude, or use defined high school expenses data.
    highschool_expenses_data (dict): The high school expenses data to include.
    """
    if years_override is not None:
        config_data["years"] = years_override

    config_data["SKI_TEAM"] = {} if include_ski_team == "exclude" else (config_data["SKI_TEAM"] if include_ski_team == "use_defined" else ski_team_data)
    config_data["BASEBALL_TEAM"] = {} if include_baseball_team == "exclude" else (config_data["BASEBALL_TEAM"] if include_baseball_team == "use_defined" else baseball_team_data)
    config_data["highschool_expenses"] = [0] * 9 if include_highschool_expenses == "exclude" else (config_data["highschool_expenses"] if include_highschool_expenses == "use_defined" else highschool_expenses_data)

def prepare_scenarios_data(scenarios_data):

    return {
        "config_data": scenarios_data.get("config_data", {}),
        "selected_scenarios": scenarios_data.get("selected_scenarios", []),
        "years_override": scenarios_data.get("years_override"),
        "include_ski_team": scenarios_data.get("include_ski_team", "include"),
        "ski_team_data": scenarios_data.get("SKI_TEAM", {}),
        "include_baseball_team": scenarios_data.get("include_baseball_team", "include"),
        "baseball_team_data": scenarios_data.get("BASEBALL_TEAM", {}),
        "include_highschool_expenses": scenarios_data.get("include_highschool_expenses", "include"),
        "highschool_expenses_data": scenarios_data.get("highschool_expenses", {})
    }



def generate_report(config_data, scenario_name):
    print(f"def generate_report: Report for scenario: {scenario_name}")
    if not config_data:
        raise ValueError("config_data is missing")

    tax_rate = calculate_tax_rate(config_data)
    calculated_data = calculate_financial_values(config_data, tax_rate)
    current_house, new_house, house_info = calculate_house_info(config_data)
    calculate_expenses_and_net_worth(config_data, calculated_data, house_info)

    report_data = {
        "config_data": config_data,
        "calculated_data": calculated_data,
        "house_info": house_info,
        "current_house": current_house,
    }

    future_value_html = report_html_generator.generate_future_value_html_table(report_data)
    living_expenses_html = report_html_generator.generate_section_html("Scenarios", calculated_data.get("LIVING_EXPENSES", {}))

    summary_data = {
        "assumption_description": config_data.get("assumption_description", ""),
        "yearly_gain": calculated_data.get("yearly_gain", ""),
        "future_value": future_value_html,
        "living_expenses_location": living_expenses_html,
    }

    scenario_html = report_html_generator.generate_html(report_data)
    report_filename = f"{Path(__file__).parent.parent}/reports/financial_report_{scenario_name}.html"
    with open(report_filename, 'w') as file:
        file.write(scenario_html)
    
    # print(f"Generated report for scenario: {scenario_name}. See: {report_filename}")
    return summary_data

def parse_and_load_config():
    args = parse_arguments()
    return load_config(args.config_file_path)

def create_reports_directory():
    """Creates a reports directory one level above the current script's directory."""
    reports_dir = Path(__file__).parent.parent / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    return reports_dir


def process_scenario(scenario_name, base_config, reports_dir):
    scenario_file = Path(__file__).parent.parent / "scenarios" / f"{scenario_name}.json"
    config_data = load_config(scenario_file)
    # print(f"Loaded config_data for scenario {scenario_name}")

    adjust_config(
        config_data, 
        base_config["years_override"], 
        base_config["include_ski_team"], base_config["ski_team_data"],
        base_config["include_baseball_team"], base_config["baseball_team_data"],
        base_config["include_highschool_expenses"], base_config["highschool_expenses_data"]
    )
    # print(f"Adjusted config_data for scenario {scenario_name}:")

    summary_data = generate_report(config_data, scenario_name)
    # print(f"Generated summary_data for scenario {scenario_name}")

    # report_filename = reports_dir / f"financial_report_summary{scenario_name}.html"
    # with report_filename.open('w') as file:
    #     file.write(summary_data['future_value'])  # Assuming future_value contains the entire report HTML
    # print(f"Generated report for scenario: {scenario_name}. See: {report_filename}")

    return summary_data