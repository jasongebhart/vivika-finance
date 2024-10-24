import sys
from pathlib import Path
import json
import logging
import argparse
from collections import namedtuple
from typing import Tuple, Union, List, Dict, Optional

# Try to import with relative paths for Flask app
try:
    from . import report_html_generator
    from . import utils  
except ImportError:
    # Fallback to absolute import if running as a standalone script
    import report_html_generator
    import utils

CAPITAL_GAIN_EXCLUSION = 500000

def load_configuration() -> Tuple[Dict, Dict]:
    """
    Loads and parses the configuration files.

    Returns:
        Tuple[Dict, Dict]: scenarios_data and general_config.
    """
    try:
        logging.info("Starting configuration loading process.")

        # Load the configurations
        logging.debug("Calling 'parse_and_load_config' to load scenarios and general configuration.")
        scenarios_data, general_config = parse_and_load_config()

        # Log the successful loading with a summary for each
        logging.info("Configuration files loaded successfully.")
        utils.log_data(scenarios_data, title="Loaded Scenarios Data", max_entries=10, log_level=logging.DEBUG)
        utils.log_data(general_config, title="General Configuration Data", max_entries=5, log_level=logging.DEBUG)

        return scenarios_data, general_config

    except FileNotFoundError as fnf_error:
        logging.error(f"Configuration file not found: {fnf_error}")
        sys.exit(1)

    except ValueError as val_error:
        logging.error(f"Value error encountered while parsing configuration: {val_error}")
        sys.exit(1)

    except Exception as e:
        logging.exception(f"Unexpected error occurred during configuration loading: {e}")
        sys.exit(1)

def load_config(config_file_path):
    logging.debug("Entering <function ")
    logging.info(f"{'Path:':<48} {config_file_path}")
    try:
        with open(config_file_path, 'r', encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Config file '{config_file_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON format in '{config_file_path}'.")
        sys.exit(1)
    else:
        logging.info("Configuration loaded successfully")
        return data

def parse_and_load_config():
    logging.debug("Entering parse_and_load_config")

    # Load the main scenario configuration file
    args = utils.parse_arguments()
    config_data = load_config(args.config_file_path)
    
    # Log the loaded scenario file path
    logging.info(f"Scenario configuration file loaded: {args.config_file_path}")

    # Check if 'base_config_file' is provided in the scenario file
    base_config_file = config_data.get('base_config_file', 'general.finance.json')

    # Get the directory of the configuration file
    config_dir = Path(args.config_file_path).parent

    # Log whether the default or an alternative base configuration file is used
    if base_config_file == 'general.finance.json':
        logging.info(f"Using default general configuration file: {base_config_file}")
    else:
        logging.info(f"Using custom base configuration file: {base_config_file}")

    # Load the general configuration file from the specified or default path
    general_config_path = config_dir / base_config_file
    logging.info(f"Loading base configuration from: {general_config_path}")

    general_config_data = load_config(general_config_path)

    # Log successful loading of configurations
    logging.info("Scenario and general configuration loaded successfully.")
    
    # Log the contents of the loaded configurations
    utils.log_data(config_data, title="Loaded Scenarios Data")
    utils.log_data(general_config_data, title="Loaded General Configuration Data")

    return config_data, general_config_data


def get_setting(key, scenarios_data, general_config):
    """
    Retrieves a setting from the scenarios data if available,
    otherwise falls back to the general configuration.
    """
    if key in scenarios_data:
        return scenarios_data[key]
    elif key in general_config:
        logging.info(f"Using fallback for '{key}' from general config.")
        return general_config[key]
    else:
        logging.warning(f"Setting '{key}' not found in both scenarios and general config.")
        return None  # or raise an exception if a default behavior is needed


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
    logging.debug("Entering <function ")
    logging.info(f"""
                 
        principal = {format_currency(principal)}
        contribution = {format_currency(contribution)}
        increase_contribution = {format_currency(increase_contribution)}
        interest_rate = {interest_rate:.2%} 
        years = {years}
    """)
    future_value = principal
    logging.info(f"{'Year':<6} {'Yearly Contribution':>17} {'Future Value':>14}")

    for year in range(years):
        yearly_contribution = contribution + year * increase_contribution if increase_contribution > 0 else contribution
        future_value *= (1 + interest_rate)
        future_value += yearly_contribution
        logging.info(
            f"{year+1:<6} {format_currency(yearly_contribution):>17} {format_currency(future_value):>14} "
        )

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
    logging.debug("Entering <function ")
    logging.info("Calculating future_value = present_value * (1 + annual_growth_rate) ** years")
    logging.info(f"{'present_value:':<30} {format_currency(present_value)}")
    logging.info(f"{'annual_growth_rate:':<30} {annual_growth_rate}")
    logging.info(f"{'years:':<30} {years}")

    future_value = present_value * (1 + annual_growth_rate) ** years
    logging.info(f"{'future value:':<30} {format_currency(future_value)}")
    return future_value

def calculate_total_child_education_expense(config_data):
    """
    Calculates the total school expenses for each child based on the new JSON structure.

    Args:
        config_data (dict): Dictionary containing 'children' with each child's 'school' data (college and high school expenses).

    Returns:
        tuple: A tuple containing total school expense, high school total expense, and college total expense.
               (total_school_expense, highschool_total_school_expense, college_total_school_expense)
    """
    logging.debug("Entering calculate_total_child_education_expense")

    total_school_expense = 0
    total_highschool_expense = 0
    total_college_expense = 0

    # Loop through each child and their school expenses
    for child in config_data.get('children', []):
        logging.info(f"Calculating expenses for {child['name']}")
        
        school_data = child.get('school', {})
        college_expenses = school_data.get('college', [])
        highschool_expenses = school_data.get('high_school', [])
        
        logging.info(f"{'Year':<6} {'college_expense':>17} {'highschool_expense':>14}")
        
        # Calculate total expenses for both college and high school
        for year_data in college_expenses:
            year = year_data['year']
            cost = year_data['cost']
            total_college_expense += cost
            total_school_expense += cost
            logging.info(f"{year:<6} {format_currency(cost):>14} {'-':>14}")

        for year_data in highschool_expenses:
            year = year_data['year']
            cost = year_data['cost']
            total_highschool_expense += cost
            total_school_expense += cost
            logging.info(f"{year:<6} {'-':>14} {format_currency(cost):>14}")
    
    logging.info(f"{'Total School Expense:':<36} {format_currency(total_school_expense)}")
    logging.info(f"{'Total High School Expense:':<36} {format_currency(total_highschool_expense)}")
    logging.info(f"{'Total College Expense:':<36} {format_currency(total_college_expense)}")

    return total_school_expense, total_highschool_expense, total_college_expense


def calculate_total_school_expense(config_data):
    """
    Calculates the total expenses for the next n years based on the provided annual expenses (handles potential missing keys using defaults).

    Args:
        config_data (dict): Dictionary containing keys 'college_expenses' (optional), 'highschool_expenses' (optional), and 'years' (optional).

    Returns:
        tuple: A tuple containing total expense, high school total expense, and college total expense.
               (total_school_expense, highschool_total_school_expense, college_total_school_expense)
    """
    logging.debug("Entering <function ")
    log_messages = [
        "Total expenses for scenario:",
        f"{'years:':<36} {config_data.get('years', 0)}",
        f"{'college expenses count:':<36} {len(config_data.get('college_expenses', []))}",
        f"{'high school expenses count:':<36} {len(config_data.get('highschool_expenses', []))}"
    ]
    for message in log_messages:
        logging.info(f"{message}")

    total_school_expense = 0
    total_highschool_expense = 0
    total_college_expense = 0
    years = config_data.get('years', 0)  # Get 'years' with default 0 if missing

    # Check if 'years' is present and greater than 0 to avoid empty list access errors
    if years > 0:
        college_expenses = config_data.get('college_expenses', [])
        highschool_expenses = config_data.get('highschool_expenses', [])
        
        # Calculate total expenses for the given number of years
        logging.info(f"{'Year':<6} {'college_expense':>17} {'highschool_expense':>14}")
        for i in range(years):
            college_expense = college_expenses[i] if i < len(college_expenses) else 0
            highschool_expense = highschool_expenses[i] if i < len(highschool_expenses) else 0
            total_college_expense += college_expense
            total_highschool_expense += highschool_expense
            total_school_expense += college_expense + highschool_expense

            logging.info(
                f"{i+1:<6} {format_currency(college_expense):>14} {format_currency(highschool_expense):>14}"
            )
            # logging.info(f"Year {i+1}: college_expense={college_expense}, highschool_expense={highschool_expense}")
    
    logging.info(f"{'Total School Expense:':<36} {format_currency(total_school_expense)}")
    logging.info(f"{'Total High School Expense:':<36} {format_currency(total_highschool_expense)}")
    logging.info(f"{'Total College Expense:':<36} {format_currency(total_college_expense)}")

    return total_school_expense, total_highschool_expense, total_college_expense

def unused_function():
     print("This function is never called.")
     
def calculate_balance(balance, interest_rate, years, annual_surplus=0, gains=[], expenses=[], yearly_expense=0):
    """
    Calculates the ending balance with compounding interest, considering yearly
    net gains or expenses.

    Args:
        balance (float): Initial investment amount.
        interest_rate (float): Annual interest rate.
        years (int): Number of years.
        annual_surplus (float, optional): Constant yearly gain (default: 0).
        gains (list of float, optional): A list of annual gains (default: []).
        expenses (list of float, optional): A list of annual expenses (default: []).
        yearly_expense (float, optional): An additional annual expense (default: 0).

    Returns:
        float: The ending balance after considering compounding interest and net gains/expenses.
    """
    logging.debug("Entering <function ")
    logging.info(
        f"\n\n<calculate_balance> Balance with compounding interest:\n"
        f" balance={format_currency(balance)}\n"
        f" interest_rate={interest_rate}\n"
        f" years={years}\n"
        f" annual_surplus={format_currency(annual_surplus)}\n"
        f" gains={gains}\n"
        f" expenses={expenses}\n"
        f" yearly_expense={yearly_expense}\n"
    )
    # Print header for the log output
    logging.info("Creating Table ")
    logging.info(f"{'Year':<6} {'Balance':>12} {'Interest':>12} {'Net Gain':>12} {'Net Expense':>12}")

    for year in range(years):
        interest = balance * interest_rate
        net_gain = annual_surplus if annual_surplus != 0 else gains[year] if year < len(gains) else 0
        net_expense = expenses[year] if year < len(expenses) else 0
        balance += interest + net_gain - net_expense - yearly_expense

        # Log values in a table-like format
        logging.info(
            f"{year+1:<6} {format_currency(balance):>12} {format_currency(interest):>12} "
            f"{format_currency(net_gain):>12} {format_currency(net_expense):>12}"
        )

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
    logging.debug("Entering <function ")
    logging.info(f"Total expenses with college_expenses: {college_expenses}, highschool_expenses: {highschool_expenses}")
    total_school_expenses = [college + highschool for college, highschool in zip(college_expenses, highschool_expenses)]

    logging.info(f"Total school expenses: {total_school_expenses}")

    return total_school_expenses

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
    logging.debug("Entering <function ")
    logging.info(f"{'original_principal:':<30} {format_currency(original_principal)}")
    logging.info(f"{'interest_rate:':<30} {interest_rate}")
    logging.info(f"{'months_to_pay:':<30} {months_to_pay}")
    logging.info(f"{'number_of_payments:':<30} {number_of_payments}")
    
    # Check if original_principal, interest_rate, months_to_pay, and number_of_payments are of the correct types
    if not all(isinstance(x, (int, float)) for x in [original_principal, interest_rate, months_to_pay, number_of_payments]):
        logging.error("Invalid input: All input parameters must be of type int or float")
        raise TypeError("All input parameters must be of type int or float")

    # Check if any input parameters are negative
    if original_principal < 0 or interest_rate < 0 or months_to_pay < 0 or number_of_payments < 0:
        logging.error("Invalid input: All input parameters must be non-negative")
        raise ValueError("All input parameters must be non-negative")

    # Check if months_to_pay or number_of_payments is zero
    if months_to_pay == 0 or number_of_payments == 0:
        logging.warning("Either months_to_pay or number_of_payments is zero, returning 0")
        return 0

    # Calculate the remaining principal using the loan amortization formula
    remaining_principal = int(original_principal * ((1 + interest_rate/12)**number_of_payments - (1 + interest_rate/12)**months_to_pay) / ((1 + interest_rate/12)**number_of_payments - 1))

    # Check if the result is NaN
    if math.isnan(remaining_principal):
        logging.error("Calculation resulted in NaN")
        raise ValueError("Calculation resulted in NaN")

    logging.info(f"{'Updated principal:':<30} {format_currency(remaining_principal)}")
    return remaining_principal


class House:
    def __init__(self, description="",cost_basis=0, closing_costs=0, home_improvement=0, value=0, mortgage_principal=0, 
                 commission_rate=0.0, annual_growth_rate=0.0461, interest_rate=0.0262, 
                 monthly_payment=8265.21, number_of_payments=276, payments_made=36, sell_house=False):
        """
        Initializes a House object with its purchase costs, value, and mortgage details.

        Args:
            description (string, optional): Brief description of house. (default: blank)
            cost_basis (float, optional): The original purchase price of the house. (default: 0)
            closing_costs (float, optional): Closing costs associated with the purchase. (default: 0)
            home_improvement (float, optional): Cost of home improvements made. (default: 0)
            value (float, optional): The current market value of the house. (default: 0)
            mortgage_principal (float, optional): The starting principal balance of the mortgage. (default: 0)
            commission_rate (float, optional): The commission rate for selling the house. (default: 0.0)
            annual_growth_rate (float, optional): The annual growth rate of the house value. (default: 0.0461)
            interest_rate (float, optional): The annual interest rate of the mortgage. (default: 0.0262)
            monthly_payment (float, optional): The monthly mortgage payment. (default: 8265.21)
            number_of_payments (int, optional): The total number of mortgage payments. (default: 248)
            sell_house (bool, optional): Indicates if the house is to be sold. (default: False)
        """
        logging.info("Calling Class: ")
        self.description = description
        self.cost_basis = cost_basis
        self.closing_costs = closing_costs
        self.home_improvement = home_improvement
        self.value = value
        self.mortgage_principal = mortgage_principal
        self.remaining_principal = self.mortgage_principal  # Initialize with starting principal
        self.commission_rate = commission_rate
        self.annual_growth_rate = annual_growth_rate
        self.interest_rate = interest_rate
        self.monthly_payment = monthly_payment
        self.number_of_payments = number_of_payments
        self.payments_made = payments_made
        self.sell_house = sell_house

    def __str__(self):
        """
        Returns a string representation of the House object.
        """
        return f"House Object:\ndescription: {self.description}\nCost Basis: ${self.cost_basis}\nClosing Costs: ${self.closing_costs}\n" \
               f"Home Improvement Costs: ${self.home_improvement}\nCurrent Value: ${self.value}\n" \
               f"Remaining Principal: ${self.remaining_principal}\n" \
               f"Mortgage Principal: ${self.mortgage_principal}\nCommission Rate: {self.commission_rate}\n" \
               f"Annual Growth Rate: {self.annual_growth_rate}\nInterest Rate: {self.interest_rate}\n" \
               f"Monthly Payment: ${self.monthly_payment}\nNumber of Payments: {self.number_of_payments}\n" \
               f"Payments Made: {self.payments_made}\nSell House: {self.sell_house}"

    def calculate_basis(self):
        """
        Calculates the total basis of the house considering purchase costs and improvements.

        Returns:
            float: The total basis of the house.
        """
        logging.debug("Entering <function ")
        logging.info("The basis of the house = purchase costs, closing costs and improvements")
        basis = self.cost_basis + self.closing_costs + self.home_improvement
        logging.info(f"{'Basis:':<44} {format_currency(basis)}")
        return basis    

    def calculate_sale_basis(self, commission_rate=0.06):
        """
        Calculates the sale basis and commission, considering the house value, commission rate, and escrow.

        Args:
            commission_rate (float, optional): The commission rate for selling the house (default: 0.06).

        Returns:
            tuple: A tuple containing the sale basis and the commission amount.
        """
        logging.debug("Entering <function ")
        logging.info(f"The sale basis is equal to house value minus commission and escrow.")
        escrow_rate = 0.002
        escrow_rate = 0.002
        escrow = self.value * escrow_rate
        commission = self.value * commission_rate
        sale_basis = self.value - commission - escrow

        logging.info(f"{'House Value:':<39} {format_currency(self.value)}")          
        logging.info(f"{'sale basis:':<39} {format_currency(sale_basis)}")   
        logging.info(f"{'commission:':<39} {format_currency(commission)}")
        logging.info(f"{'commission_rate:':<39} {commission_rate}")
        logging.info(f"{'escrow:':<39} {format_currency(escrow)}")         
        
        return sale_basis, commission

    def calculate_capital_gains(self):
        """
        Calculates the capital gains tax on selling the house, considering exclusion.

        Returns:
            float: The amount of capital gains to be paid. Multiple this by the tax_rate to determine tax owed.
        """
        logging.debug("Entering <function ")
        sale_basis, commission = self.calculate_sale_basis()  
        basis = self.calculate_basis()
        capital_gain = sale_basis - basis
        taxable_capital_gains = max(0, capital_gain - CAPITAL_GAIN_EXCLUSION)

        logging.info(f"{'sale_basis:':<36} {format_currency(sale_basis)}")
        logging.info(f"{'basis:':<36} {format_currency(basis)}")
        logging.info(f"{'capital_gain:':<36} {format_currency(capital_gain)}")
        logging.info(f"{'Capital Gain Exclusion:':<36} {format_currency(CAPITAL_GAIN_EXCLUSION)}")
        logging.info(f"{'Taxable Capital Gains:':<36} {format_currency(taxable_capital_gains)}")

        return taxable_capital_gains

    def calculate_remaining_principal(self):
        """
        Calculates the remaining principal on the house mortgage based on payments made.

        Returns:
            float: The remaining principal balance on the mortgage.
        """
        months_to_pay = self.payments_made
        remaining_principal = calculate_remaining_principal(
            self.mortgage_principal, self.interest_rate , months_to_pay, self.number_of_payments
        )
        self.remaining_principal = remaining_principal
        return remaining_principal
    
    def calculate_net_worth(self):
        """
        Calculates the net worth of the house, considering its value and mortgage principal.

        Returns:
            float: The net worth of the house (value minus mortgage principal).
        """
        logging.debug("Entering <function ")
        net_worth = self.value - self.remaining_principal
        logging.info(f"{'House net worth:':<40} {'value('}{format_currency(self.value)})- principal({format_currency(self.remaining_principal)})")
        logging.info(f"{'House net worth:':<40} {format_currency(net_worth)}")
        return net_worth

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
        logging.debug("Entering <function ")
        logging.info(f"invest_capital={invest_capital}, interest_rate={interest_rate}, years={years}")
        future_value = calculate_future_value(invest_capital, 0, 0, interest_rate, years)
        logging.info(f"Future Investment: {future_value}")
        return future_value
    
    

def calculate_house_values(current_house):
    # Calculate sale basis and capital gains for the current house
    logging.debug("Entering <function ")
    logging.info("In order to realize the value of a house we need to determine the costs for selling it.")
    commission_rate_myhouse = current_house.commission_rate
    sale_basis, total_commission = current_house.calculate_sale_basis(commission_rate=commission_rate_myhouse)
    taxable_capital_gains = current_house.calculate_capital_gains()
    logging.info(f"{'Taxable Capital Gains:':<37} {format_currency(taxable_capital_gains)}")
    capital_gain = taxable_capital_gains * .15
    logging.info(f"{'Capital Gains Tax:':<37} {format_currency(capital_gain)}")
    house_net_worth = current_house.calculate_net_worth()
    capital_from_house = sale_basis - current_house.remaining_principal - capital_gain
    logging.info("capital_from_house is sale_basis - remaining principal - capital_gain tax")
    logging.info(f"{'Capital from house:':<37} {format_currency(capital_from_house)}")
    
    return sale_basis, total_commission, capital_gain, house_net_worth, capital_from_house


def calculate_new_house_values(new_house, capital_from_house, config_data):
    logging.debug("Entering <function calculate_new_house_values>")
    
    if not new_house:
        logging.warning("No new house provided; cannot calculate values.")
        return (None, None, None, 0, 0, 0, 0, 0)  # Return None for calculations that depend on new house

    # Assuming new_house is an object with expected properties and methods
    try:
        # Calculate sale basis and capital gains for the new house
        commission_rate_newhouse = config_data['new_house']['commission_rate']
        new_house_sale_basis, new_house_total_commission = new_house.calculate_sale_basis(commission_rate=commission_rate_newhouse)
        new_house_taxable_capital_gain = new_house.calculate_capital_gains()
        
        logging.info(f"{'New House Taxable Capital Gains:':<33} {format_currency(new_house_taxable_capital_gain)}")
        
        new_house_capital_gains_tax = new_house_taxable_capital_gain * .15
        logging.info(f"{'New House Capital Gains Tax:':<33} {format_currency(new_house_capital_gains_tax)}")

        # Set the new_house_value
        years = config_data['years']
        annual_growth_rate = config_data['new_house']['annual_growth_rate']
        
        new_house_cost_basis = config_data['new_house']['cost_basis']
        new_house_future_value = new_house_cost_basis * (1 + annual_growth_rate) ** years
        new_house_fees = config_data['new_house']['cost_basis'] * .01

        # Calculate the investment capital from the sale of the current house
        logging.info(f"{'invest_capital:':<25} {format_currency(capital_from_house)} - {format_currency(new_house_cost_basis)} - {format_currency(new_house_fees)}")
        invest_capital = capital_from_house - new_house_cost_basis - new_house_fees
        logging.info(f"{'invest_capital:':<33} {format_currency(invest_capital)}")
        
        interest_rate = config_data['interest_rate']
        house_capital_investment = calculate_future_value(invest_capital, 0, 0, interest_rate, years)
        
        logging.info(f"{config_data['new_house']['annual_growth_rate']}")
        
        house_values = {
            "sale_basis": new_house_sale_basis,
            "total_commission": new_house_total_commission,
            "capital_gain": new_house_taxable_capital_gain,
            "new_house_cost": new_house_cost_basis,
            "new_house_future_value": new_house_future_value,
            "new_house_fees": new_house_fees,
            "invest_capital": invest_capital,
            "house_capital_investment": house_capital_investment
        }

        formatted_values = "\n".join([f"{key}={format_currency(value)}" for key, value in house_values.items()])
        logging.info(f"New house values:\n{formatted_values}")

        return (new_house_sale_basis, new_house_total_commission, new_house_taxable_capital_gain,
                new_house_cost_basis, new_house_future_value, new_house_fees, 
                invest_capital, house_capital_investment)

    except Exception as e:
        logging.error(f"Error calculating new house values: {str(e)}")
        return (None, None, None, 0, 0, 0, 0, 0)  # Return defaults on error

def initialize_variables():
    return 0, 0, 0

def calculate_spouse_annual_income(spouse_data, overrides, spouse_key, tax_rate):
    logging.debug(f"Calculating income for {spouse_key}")
   
    # Calculate income for spouse
    spouse_income_data = calculate_spouse_income(spouse_data, tax_rate)
    
    return spouse_income_data

# Function to create the yearly data dictionary
def create_yearly_data(spouse1_income_data, spouse1_data, spouse2_income_data, spouse2_data, tax_rate):
    logging.debug("Creating yearly data dictionary")
    
    yearly_data = {
        "Spouse 1 Yearly Income Combined": spouse1_income_data["yearly_income_combined"],
        "Spouse 1 Yearly Income Base": spouse1_data.get('yearly_income', {}).get('base', 'Not found'),
        "Spouse 1 Yearly Income Bonus": spouse1_data.get('yearly_income', {}).get('bonus', 'Not found'),
        "Spouse 1 Yearly Income Quarterly": spouse1_data.get('yearly_income', {}).get('quarterly', 'Not found'),
        "Spouse 1 Total Pre-Tax Investments": spouse1_income_data["total_pre_tax_investments"],
        "Spouse 1 Total Post-Tax Investments": spouse1_income_data["total_post_tax_investments"],
        "Spouse 1 After Pre-Tax Investments": spouse1_income_data["income_after_pretax_items"],
        f"Spouse 1 After tax ({tax_rate})": spouse1_income_data["income_after_taxes"],
        "Spouse 1 After-Tax Investment Income": spouse1_income_data["income_after_posttax_items"],
        
        "Spouse 2 Yearly Income Combined": spouse2_income_data["yearly_income_combined"],
        "Spouse 2 Yearly Income Base": spouse2_data.get('yearly_income', {}).get('base', 'Not found'),
        "Spouse 2 Yearly Income Bonus": spouse2_data.get('yearly_income', {}).get('bonus', 'Not found'),
        "Spouse 2 Yearly Income Quarterly": spouse2_data.get('yearly_income', {}).get('quarterly', 'Not found'),
        "Spouse 2 Total Pre-Tax Investments": spouse2_income_data["total_pre_tax_investments"],
        "Spouse 2 Total Post-Tax Investments": spouse2_income_data["total_post_tax_investments"],
        "Spouse 2 After Pre-Tax Investments": spouse2_income_data["income_after_pretax_items"],
        f"Spouse 2 After tax ({tax_rate})": spouse2_income_data["income_after_taxes"],
        "Spouse 2 After-Tax Investment Income": spouse2_income_data["income_after_posttax_items"],
        
        "Yearly Net Income": spouse1_income_data["income_after_posttax_items"] + spouse2_income_data["income_after_posttax_items"]
    }

    return yearly_data

# Main function
def calculate_annual_income(config_data, tax_rate):
    logging.debug("Entering calculate_annual_income")
    spouse1_data = config_data.get("spouse1_data",0)
    spouse2_data = config_data.get("spouse2_data",0)
    
    # Retrieve overrides
    overrides = config_data.get('overrides', {})
    
    # Calculate spouse 1 income
    spouse1_income_data = calculate_spouse_annual_income(spouse1_data, overrides, 'spouse1', tax_rate)
    
    # Calculate spouse 2 income
    spouse2_income_data = calculate_spouse_annual_income(spouse2_data, overrides, 'spouse2', tax_rate)
    
    # Create the yearly data dictionary
    yearly_data = create_yearly_data(spouse1_income_data, config_data.get("spouse1_data",0), spouse2_income_data, config_data.get("spouse2_data",0), tax_rate)

    # Log the yearly data
    utils.log_data(yearly_data, title="<calculate_yearly_income> Yearly Data")
    
    return yearly_data

def apply_spouse_variant(spouse_data, spouse_key, config_data):
    """
    Apply the variant for the specified spouse if a variant exists in the config_data.
    """
    spouse_variant = config_data.get(f'{spouse_key}_variant')
    if spouse_variant:
        # Retrieve the variant data for the given spouse key and apply it
        variant_data = config_data.get(f"{spouse_key}_variants", {}).get(spouse_variant)

        if variant_data:
            # Apply the variant by updating the spouse_data dictionary
            spouse_data.update(variant_data)
            logging.info(f"Applied variant '{spouse_variant}' for {spouse_key}: {variant_data}")
        else:
            logging.warning(f"Variant '{spouse_variant}' for {spouse_key} not found in config_data.")
    
    return spouse_data

def apply_children_variant(children_data, config_data):
    """Apply the selected children variant to the children data."""
    variant = config_data.get('children_variant')
    
    if variant and variant in config_data.get('children_variants', {}):
        return config_data['children_variants'][variant]['children']
    else:
        logging.warning(f"Children variant '{variant}' not found in children variants.")
        return children_data  # Return original data if variant not found
    
def apply_overrides(config_data, overrides, spouse_key):
    """
    Apply overrides for the specified spouse key.
    """
    logging.info(f"Applying overrides for {spouse_key}")

    # Retrieve the base spouse data from config
    spouse_data = config_data.get(spouse_key, {}).copy()
    logging.info(f"Initial {spouse_key} data from config: {spouse_data}")

    # Check if overrides should be applied
    if overrides.get(spouse_key) == "on":
        logging.info(f"Overrides are enabled for {spouse_key}")
        
        # Get override values and update spouse_data
        alt_values = overrides.get("alt_values", {}).get(spouse_key, {})
        logging.info(f"Override values for {spouse_key}: {alt_values}")
        
        spouse_data.update(alt_values)
        logging.info(f"Updated {spouse_key} data after applying overrides: {spouse_data}")
    else:
        logging.info(f"No overrides enabled for {spouse_key}")

    return spouse_data

def calculate_spouse_income(spouse_data, tax_rate):
    """
    Calculate income data for a given spouse based on their data and tax rate.
    This function contains the logic for calculating various income components.
    """
    # Retrieve income data
    base_income = spouse_data.get('yearly_income', {}).get('base', 0)
    bonus_income = spouse_data.get('yearly_income', {}).get('bonus', 0)
    quarterly_income = spouse_data.get('yearly_income', {}).get('quarterly', 0)

    # Sample calculations for total yearly income
    yearly_income_combined = base_income + bonus_income + (quarterly_income * 4)

    logging.debug(f"Base Income: {base_income}")
    logging.debug(f"Bonus Income: {bonus_income}")
    logging.debug(f"Quarterly Income: {quarterly_income} (Annual Total: {quarterly_income * 4})")
    logging.debug(f"Yearly Income Combined: {yearly_income_combined}")

    # Retrieve pre-tax and post-tax investment data
    pretax_investments = spouse_data.get('pretax_investments', {})
    posttax_investments = spouse_data.get('posttax_investments', {})

    # Calculate total pre-tax investments
    total_pre_tax_investments = sum(pretax_investments.values())
    logging.debug(f"Total Pre-Tax Investments: {total_pre_tax_investments}")

    # Calculate total post-tax investments
    total_post_tax_investments = sum(posttax_investments.values())
    logging.debug(f"Total Post-Tax Investments: {total_post_tax_investments}")

    # Calculate income after pre-tax items
    income_after_pretax_items = yearly_income_combined - total_pre_tax_investments
    logging.debug(f"Income After Pre-Tax Items: {income_after_pretax_items}")

    # Calculate income after taxes
    income_after_taxes = income_after_pretax_items * (1 - tax_rate)
    logging.debug(f"Income After Taxes (Tax Rate: {tax_rate}): {income_after_taxes}")

    # Calculate income after post-tax items
    income_after_posttax_items = income_after_taxes - total_post_tax_investments
    logging.debug(f"Income After Post-Tax Items: {income_after_posttax_items}")

    return {
        "yearly_income_combined": yearly_income_combined,
        "total_pre_tax_investments": total_pre_tax_investments,
        "total_post_tax_investments": total_post_tax_investments,
        "income_after_pretax_items": income_after_pretax_items,
        "income_after_taxes": income_after_taxes,
        "income_after_posttax_items": income_after_posttax_items
    }

def calculate_annual_surplus(monthly_surplus):
  """Calculates the yearly surplus based on the provided monthly surplus.

  Args:
      monthly_surplus: The amount of surplus each month.

  Returns:
      The total surplus for the year.
  """
  logging.info(f"{'Monthly_surplus':<35} {format_currency(monthly_surplus)}")
  annual_surplus = monthly_surplus * 12
  logging.info(f"{'Yearly surplus':<35} {format_currency(annual_surplus)}")
  return annual_surplus

def determine_surplus_type(annual_surplus):
  """Determines if the surplus is positive (gain) or negative (expense).

  Args:
      annual_surplus: The total surplus for the year.

  Returns:
      A string indicating "Gain" if positive, "Expense" if negative, or "No Surplus/Expense" if zero.
  """
  logging.debug("Entering <function ")

  if annual_surplus > 0:
    surplus_type = "Gain"
  elif annual_surplus < 0:
    surplus_type = "Expense"
  else:
    surplus_type = "No Surplus/Expense"

  logging.info(f"{'Surplus type':<37} {surplus_type:}")
  return surplus_type

def format_currency(value):
  """Formats a numerical value as currency with commas."""
#   logging.info(f"format_currency: {value}")
  return "${:,.0f}".format(value)


def can_cover_school_expenses_per_year(annual_surplus, school_expenses):
    """
    Checks if the yearly surplus can cover school expenses for each year.

    Args:
        annual_surplus: The annual surplus amount.
        school_expenses: A list of high school expenses for each year.

    Returns:
        A list of tuples containing (year, covered, remaining_surplus/deficit).
    """
    logging.debug("Entering <function ")

    logging.info(f"Checking if yearly surplus can cover school expenses")
    utils.log_data(annual_surplus, "annual_surplus")
    utils.log_data(school_expenses, "school_expenses")

    # Ensure lists have the same length
    if len(annual_surplus) != len(school_expenses):
        logging.error("<can_cover_school_expenses_per_year> Yearly surplus and high school expenses lists must have the same length.")
        raise ValueError("<can_cover_school_expenses_per_year> Yearly surplus and high school expenses lists must have the same length.")

    report = []
    for year, expense in enumerate(school_expenses):
        surplus_used = min(expense, annual_surplus[year])
        remaining_surplus = annual_surplus[year] - surplus_used
        covered = surplus_used >= expense
        deficit = expense - surplus_used if not covered else 0
        logging.debug(f"Year {year+1} calculations: surplus_used={surplus_used}, remaining_surplus={remaining_surplus}, covered={covered}, deficit={deficit}")
        # Report as dictionary for easier access
        report_data = {
            "year": year + 1,
            "covered": covered,
            "remaining_surplus": remaining_surplus,
            "deficit": deficit,
        }
        report.append(report_data)
        logging.info(f"Year {year+1}: {covered if covered else 'Deficit: '}{deficit}")

    return report


def get_work_status(config_data):
    """
    Determines the work status based on spouse incomes and custom parent names.

    Args:
        config_data: Dictionary containing parent and income information.

    Returns:
        A string indicating the work status ("Both [Parent1] and [Parent2] Work", 
        "[Parent1] Works", "[Parent2] Works", or "Neither [Parent1] nor [Parent2] Work").
    """
    logging.debug("Entering get_work_status function")
    
    # Retrieve incomes and parent names from the config data
    spouse1_income = config_data.get("spouse1_data", {}).get("yearly_income", {}).get("base", 0)
    spouse2_income = config_data.get("spouse2_data", {}).get("yearly_income", {}).get("base", 0)
    parent_one = config_data.get("parent_one", "Parent 1")
    parent_two = config_data.get("parent_two", "Parent 2")
    
    # Determine work status based on incomes
    if spouse1_income > 0 and spouse2_income > 0:
        work_status = f"Both Work"
    elif spouse1_income > 0:
        work_status = f"{parent_one} Works"
    elif spouse2_income > 0:
        work_status = f"{parent_two} Works"
    else:
        work_status = f"Both Retired"

    logging.debug(f"{'Work Status:':<37} {work_status}")
    return work_status


def calculate_tax_rate(config_data):
    logging.debug("Entering <function ")
    spouse2_yearly_income_base = config_data.get('spouse2_yearly_income_base', 0)
    if spouse2_yearly_income_base:
        tax_rate = config_data['federal_tax_rate_dual'] + config_data['state_tax_rate_dual']
        logging.info(f"{'Tax rate for dual income:':<41} {tax_rate}")
    else:
        tax_rate = config_data['federal_tax_rate_single'] + config_data['state_tax_rate_single']
        logging.info(f"{'Tax rate for single income:':<41} {tax_rate}")

    return tax_rate


# Function to parse config
def parse_config(args):
    logging.info("<parse_config> Entering <function ")

    config_data = load_config(args.config_file_path)
    tax_rate = calculate_tax_rate(config_data)

    logging.info(f"Parsed config data: {config_data}, tax_rate: {tax_rate}")
    return config_data, tax_rate

def calculate_total_monthly_expenses(config_data):
    logging.debug("Entering <function ")
    sell_house = config_data.get('house', {}).get('sell_house', 0)
    if sell_house:
        logging.info("sell_house property exists")
        monthly_payment = config_data.get('new_house', {}).get('monthly_payment', 0)  # Use nested get with default 0
    else:
        logging.info("sell_house property does NOT exist or is false")
        monthly_payment = config_data['house']['monthly_payment']
    # monthly_payment = config_data['house']['monthly_payment']

    monthly_expenses_breakdown = {
        "Mortgage": monthly_payment,
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
    logging.info(f"{'Total monthly expenses:':<27} {format_currency(total_monthly_expenses)}")
    utils.log_data(monthly_expenses_breakdown, "Monthly Expenses Breakdown")
    
    return total_monthly_expenses, monthly_expenses_breakdown

def initialize_house_variables(config_data):
    """
    Initialize relevant variables based on configuration data.

    Args:
        config_data (dict): Configuration data for the financial scenario.

    Returns:
        tuple: A tuple containing the initialized variables.
    """
    logging.debug("Entering <function ")
    logging.info("-------------------------- Initialize House")
    # Create House instances
    if 'house' in config_data and config_data['house'] is not None:
        logging.info(f"{'Current House =':<33} Defined")
        current_house = create_house_instance(config_data['house'])
    else:
        # Handle the case where new_house_data is None or empty
        logging.info("Current house not found in config")
        current_house = None
    
    # current_house = create_house_instance(config_data['house'])
    # Check if 'new_house' key exists and has a non-None value
    # if 'new_house' in config_data and config_data['new_house'] is not None:
    #     logging.info("A New House is defined.")
    #     new_house = create_house_instance(config_data['new_house'])
    # else:
    #     # Handle the case where new_house_data is None or empty
    #     logging.info("new_house data not found in config")
    #     new_house = None
    if 'new_house' in config_data:
        if config_data['new_house'] is not None:
            logging.info("A New House is defined.")
            new_house = create_house_instance(config_data['new_house'])
        else:
            logging.info("new_house data is explicitly set to None.")
            new_house = None
    else:
        # This block will execute if 'new_house' key is missing
        logging.info("new_house key not found in config")
        new_house = None


    return current_house, new_house

def create_house_instance(house_data):
    """
    Create a House instance based on configuration data.

    Args:
        house_data (dict): Configuration data for the house.

    Returns:
        House: An instance of the House class with updated remaining principal.
    """
    logging.debug(f"Entering <function ")
    if house_data:
        house_instance = House(**house_data)

        # Check if the mortgage principal is 0, meaning the house is not financed
        if house_instance.mortgage_principal == 0:
            logging.info(f"The house is not financed (Mortgage Principal: {house_instance.mortgage_principal}).")
        else:
            # Calculate the remaining principal only if the house is financed
            house_instance.calculate_remaining_principal()
            logging.info(f"Remaining mortgage principal: {house_instance.remaining_principal}")


        logging.info(f"\n {house_instance}\n")
        logging.debug(f"Exiting <function ")
        return house_instance
    else:
        logging.info("No house data provided, returning None")
        logging.debug(f"Exiting <function ")
        return None

def calculate_combined_net_worth(config_data, house_info, calculated_data):
    """
    Calculate the combined net worth, accounting for house sale and purchase of new house.

    Args:
        config_data (dict): Configuration data for the financial scenario.
        house_info (dict): Dictionary containing house-related information.

    Returns:
        float: Combined net worth.
    """
    logging.debug("Entering <function calculate_combined_net_worth>")

    # Determine which house value to use based on whether the house is being sold
    if house_info.get("sell_house", False):
        house_value = house_info.get("cost_basis", 0)
        logging.info(f"Using cost basis for new house: {house_value}")
    else:
        house_value = house_info.get("house_net_worth", 0)
        logging.info(f"Using current house net worth: {house_value}")

    # Include house capital investment if it exists
    invest_capital = house_info.get("invest_capital", 0)
    logging.info(f"House capital investment: {invest_capital}")

    # Calculate combined net worth
    combined_net_worth = (
        calculated_data['total_investment_balance']
        + calculated_data['total_retirement_principal']
        + house_value
        + invest_capital
    )

    logging.info(f"Combined Net Worth: {format_currency(combined_net_worth)}")
    return combined_net_worth

def calculate_retirement_principal(RETIREMENT):
    """
    Calculate the total retirement principal by summing the values of retirement accounts
    (Roth, IRA, 401K) for both spouses in the 'RETIREMENT' section of the config data.
    """
    logging.info("Starting retirement principal calculation.")
    logging.debug(f"RETIREMENT data received: {RETIREMENT}")

    total_retirement_principal = 0

    for spouse in RETIREMENT:
        spouse_name = spouse.get("name", "Unknown")
        accounts = spouse.get("accounts", {})
        logging.debug(f"Processing retirement accounts for {spouse_name}: {accounts}")

        # Sum up all Roth accounts
        roth_accounts = accounts.get("Roth", [])
        for account in roth_accounts:
            total_retirement_principal += sum(account.values())

        # Sum up all IRA accounts
        ira_accounts = accounts.get("IRA", [])
        for account in ira_accounts:
            total_retirement_principal += sum(account.values())

        # Sum up all 401K accounts
        k401_accounts = accounts.get("401K", [])
        for account in k401_accounts:
            total_retirement_principal += sum(account.values())

    logging.info(f"Total retirement principal calculated: {total_retirement_principal}")
    
    return total_retirement_principal


def calculate_financial_data(config_data, tax_rate):
    logging.debug("Entering <function ")
    yearly_data = calculate_annual_income(config_data, tax_rate)
    total_monthly_expenses, monthly_expenses_breakdown = calculate_total_monthly_expenses(config_data)

    return yearly_data, total_monthly_expenses, monthly_expenses_breakdown

def calculate_expenses_not_factored_in_report(config_data):
    logging.debug("Entering <function ")
    expenses_not_factored_in_report = {
        "Total Widji": config_data.get('total_widji'),
        "Total Ski Camp": config_data.get('Total_ski_camp'),
    }
    monthly_expenses = {f"Monthly {key}": int(value / 12) for key, value in expenses_not_factored_in_report.items()}
    expenses_not_factored_in_report.update(monthly_expenses)
    # logging.info("-" * 70)  # Use a line of dashes or other separator
    utils.log_data(expenses_not_factored_in_report, title="Expenses Not Factored In Report")
    logging.debug("Exiting <function ")
    return expenses_not_factored_in_report

def calculate_surplus(yearly_data, total_monthly_expenses, yearly_expenses=None):
    logging.debug("Entering <function ")

    annual_income = yearly_data["Yearly Net Income"]
    logging.info(f"{'Yearly Net Income':<42} {format_currency(annual_income)}")
    logging.info(f"{'Monthly Net Income':<42} {format_currency(annual_income / 12)}")
    logging.info(f"{'Monthly Expenses':<42} {format_currency(total_monthly_expenses)}")
    
    # Calculate monthly surplus (without considering annual expenses yet)
    monthly_surplus = int(annual_income / 12) - int(total_monthly_expenses)
    logging.info(f"{'Monthly Surplus':<42} {format_currency(monthly_surplus)}")

    # Convert monthly surplus into yearly surplus
    annual_surplus = monthly_surplus * 12
    logging.info(f"{'Annual Surplus':<42} {format_currency(annual_surplus)}")

    # Subtract yearly expenses if provided
    if yearly_expenses:
        annual_surplus -= yearly_expenses
        logging.info(f"{'Yearly Expenses':<42} {format_currency(yearly_expenses)}")
    logging.info(f"{'Annual Surplus after yearly expenses':<42} {format_currency(annual_surplus)}")

    surplus_type = determine_surplus_type(annual_surplus)

    return annual_surplus, surplus_type, monthly_surplus


def calculate_income_expenses(config_data, tax_rate):
    logging.debug("Entering <function ")

    # Calculate financial data
    yearly_data, total_monthly_expenses, monthly_expenses_breakdown = calculate_financial_data(config_data, tax_rate)
    logging.info(f"Financial data calculated. Yearly income: {yearly_data}")
    logging.info(f"Total monthly expenses: {format_currency(total_monthly_expenses)}")
    
    # Additional expenses that may not be included in monthly expenses
    expenses_not_factored_in_report = calculate_expenses_not_factored_in_report(config_data)
    logging.info(f"Expenses not factored in report: {expenses_not_factored_in_report}")

    # Yearly expenses (e.g., vacations, insurance, etc.) from config_data
    annual_vacation = config_data.get('annual_vacation', 0)
    additional_insurance = config_data.get('additional_insurance', 0)
    annual_rent = config_data.get('annual_rent', 0)
    logging.info(f"Annual vacation: {format_currency(annual_vacation)}, "
                f"Annual insurance: {format_currency(additional_insurance)}, "
                f"Annual rent: {format_currency(annual_rent)}")
    
    # Total yearly expenses (sum of all yearly costs)
    total_yearly_expenses = annual_vacation + additional_insurance + annual_rent
    logging.info(f"{'total_yearly_expenses':<42} {format_currency(total_yearly_expenses)}")
    
    # Calculate surplus, now factoring in yearly expenses
    annual_surplus, surplus_type, monthly_surplus = calculate_surplus(yearly_data, total_monthly_expenses, total_yearly_expenses)
    logging.info(f"Annual surplus: {format_currency(annual_surplus)} ({surplus_type}), "
                 f"Monthly surplus (annual expenses not included): {format_currency(monthly_surplus)}")
    
    # Calculate school expenses
    total_school_expense, total_highschool_expense, total_college_expense = calculate_total_child_education_expense(config_data)
    logging.info(f"Total school expenses: {format_currency(total_school_expense)}, "
                 f"High school expenses: {format_currency(total_highschool_expense)}, "
                 f"College expenses: {format_currency(total_college_expense)}")
    
    # Yearly income deficit if provided
    yearly_income_deficit = int(config_data['yearly_expense'])
    logging.info(f"Yearly income deficit: {format_currency(yearly_income_deficit)}")

    # Add everything to the calculated_data dictionary
    calculated_data = {
        "yearly_data": yearly_data,
        "total_monthly_expenses": total_monthly_expenses,
        "monthly_expenses_breakdown": monthly_expenses_breakdown,
        "annual_surplus": annual_surplus,
        "surplus_type": surplus_type,
        "monthly_surplus": monthly_surplus,
        "total_school_expense": total_school_expense,
        "total_highschool_expense": total_highschool_expense,
        "total_college_expense": total_college_expense,
        "yearly_income_deficit": yearly_income_deficit,
        "expenses_not_factored_in_report": expenses_not_factored_in_report
    }

    return calculated_data


def calculate_investment_values(config_data, annual_surplus):
    logging.debug("Entering <function ")
    logging.info(f"{'annual_surplus':<32} {format_currency(annual_surplus)}")
    logging.info(f"{'yearly_gain':<32} {config_data.get('yearly_gain', 0)}")

    # Adjust annual surplus with yearly gains
    annual_surplus += config_data.get('yearly_gain', 0)

    # Sum all investment amounts using the new helper function
    total_investment_balance = calculate_total_investments(config_data.get('INVESTMENTS', {}))
    logging.info(f"{'Total Investment Balance':<31} {format_currency(total_investment_balance)}")
    
    total_retirement_principal = calculate_retirement_principal(config_data.get('RETIREMENT', []))


    # Employee Stock Plan Calculation
    logging.info("Employee Stock Plan")
    total_employee_stockplan = calculate_future_value(
        0,
        config_data.get('employee_stock_purchase', 0),
        increase_contribution=0,
        interest_rate=config_data.get('interest_rate', 0),
        years=config_data.get('years', 0)
    )
    logging.info(f"{'Total Employee Stock Plan':<31} {format_currency(total_employee_stockplan)}")

    # School Expenses Calculation
    school_expenses = calculate_school_expenses(config_data, flatten=True)

    # Investment Balance with Expenses Calculation, using total investment balance
    logging.info(f"Investments & Expenses ")
    investment_balance_after_expenses = calculate_balance(
        total_investment_balance,  # Now using summed investment balance
        config_data.get('interest_rate', 0),
        config_data.get('years', 0),
        annual_surplus=annual_surplus,
        gains=config_data.get('gains', 0),
        expenses=school_expenses,
        yearly_expense=config_data.get('yearly_expense', 0)
    )

    # Retirement Valuation
    logging.info(f"Retirement Valuation")
    future_retirement_value_contrib = calculate_future_value(
        total_retirement_principal,
        config_data.get('initial_contribution', 0),
        config_data.get('increase_contribution', 0),
        config_data.get('interest_rate', 0),
        config_data.get('years', 0)
    )

    # Collect results in dictionary
    investment_values = {
        "total_employee_stockplan": total_employee_stockplan,
        "school_expenses": school_expenses,
        "investment_balance_after_expenses": investment_balance_after_expenses,
        "future_retirement_value_contrib": future_retirement_value_contrib
    }

    # Log the resulting values
    utils.log_data(investment_values, title="Future Value", format_as_currency=True)
    
    return investment_values



def calculate_total_investments(INVESTMENTS):
    """
    Calculate the total investment balance by summing the 'amount' field
    from each investment in the 'Investments' section of the config data.
    """
    logging.info("Starting total investment calculation.")
    logging.debug(f"Investments data received: {INVESTMENTS}")

    # Calculate total investment by summing the 'amount' of each investment
    total_investment = sum(investment.get('amount', 0) for investment in INVESTMENTS.values())
    
    logging.info(f"Total investment calculated: {total_investment}")
    
    return total_investment




def calculate_house_data(current_house, config_data, new_house):
    """
    This function calculates all house-related information.
    """
    logging.debug("Entering <function calculate_house_data>")

    # Check if current_house, config_data, or new_house are None and log appropriately
    if current_house is None:
        logging.error("current_house is None")
        return None

    if config_data is None:
        logging.error("config_data is None")
        return None

    # Proceed only if config_data has the expected keys
    if "home_tenure" not in config_data:
        logging.error("'home_tenure' not found in config_data")
        return None

    # Determine if a new house is expected
    new_house_expected = config_data.get("new_house_expected", False)
    
    if new_house is None and new_house_expected:
        logging.error("new_house is None for a scenario that expects a new house purchase")
        return None

    # Initialize variables to ensure they have default values
    new_house_cost_basis = new_house_future_value = new_house_fees = invest_capital = house_capital_investment = sale_basis = total_commission = capital_gain = house_net_worth = capital_from_house = 0

    # When owning the house
    if config_data["home_tenure"] == "Own":
        sale_basis, total_commission, capital_gain, house_net_worth, capital_from_house = calculate_house_values(current_house)

        if new_house:
            (new_house_sale_basis, new_house_total_commission, new_house_taxable_capital_gain,
             new_house_cost_basis, new_house_future_value, new_house_fees,
             invest_capital, house_capital_investment) = calculate_new_house_values(new_house, capital_from_house, config_data)
            
            # Call with the correct arguments
            house_networth_future, house_value_future, remaining_principal = calculate_future_house_values(new_house, config_data, current_house, new_house_future_value)
        else:
            # Handle case where no new house is being purchased
            house_networth_future, house_value_future, remaining_principal = calculate_future_house_values(None, config_data, current_house, 0)

    elif config_data["home_tenure"] == "Rent":
        if current_house:
            logging.info("Home_tenure set to Rent and Current House object found")
            _, _, _, _, capital_from_house = calculate_house_values(current_house)
            logging.info(f"Sell current house and retrieve capital_from_house: {capital_from_house}")
        else:
            logging.error("Current House Not Found")
            return None
        
        interest_rate = 0
        years = config_data['years'] 
        new_house_cost_basis, new_house_future_value, new_house_fees = 0,0,0
        house_networth_future, house_value_future, remaining_principal = 0, 0, 0
        house_capital_investment = calculate_future_value(capital_from_house, 0, 0, interest_rate, years)
        invest_capital = capital_from_house

    else:
        logging.error("Invalid 'home_tenure' value")
        return None

    logging.debug("Exiting <function calculate_house_data>")
    
    return {
        "sale_basis": sale_basis,
        "total_commission": total_commission,
        "capital_gain": capital_gain,
        "house_value_future": house_value_future,
        "house_net_worth": new_house_cost_basis if new_house else house_net_worth,
        "capital_from_house": capital_from_house,
        "new_house": new_house,
        "new_house_cost": new_house_cost_basis,
        "new_house_value": new_house_future_value,
        "new_house_fees": new_house_fees,
        "invest_capital": invest_capital,
        "house_capital_investment": house_capital_investment,
        "house_networth_future": house_networth_future,
        "remaining_principal": remaining_principal,
    }

def calculate_future_house_values(new_house, config_data, current_house, new_house_value):
    logging.debug("Entering <function ")

    if new_house:
        house_networth_future = new_house_value
        remaining_principal = None
        house_value_future = None
        logging.info("Using new house values")

    else:
        logging.info("future house values based on current house")
        years = config_data.get('years', 0) 
        remaining_principal = calculate_remaining_principal(
            current_house.mortgage_principal, current_house.interest_rate,
            ((config_data.get('years', 0)  * 12) + current_house.payments_made), current_house.number_of_payments)
        house_value_future = calculate_future_value_byrate(current_house.value, current_house.annual_growth_rate, config_data.get('years', 0))
        house_networth_future = house_value_future - remaining_principal
        logging.info(f"{'Updated Principal:':<29}  {format_currency(remaining_principal)}")
        # logging.info(f"'House Net Worth' {years} 'years:' {:<29}  {format_currency(house_networth_future)}")
        logging.info(f"House Net Worth {years} years:\t{format_currency(house_networth_future)}")

    return house_networth_future, house_value_future, remaining_principal

def calculate_future_net_worth_houseinfo(new_house, calculated_data, house_info):
    logging.debug("Entered calculate_future_net_worth_houseinfo")

    # Retrieve calculated data with default values
    future_retirement_value_contrib = calculated_data.get("future_retirement_value_contrib", 0)
    investment_balance_after_expenses = calculated_data.get("investment_balance_after_expenses", 0)
    total_employee_stockplan = calculated_data.get("total_employee_stockplan", 0)
    investment_projected_growth = calculated_data.get("investment_projected_growth", 0)

    logging.debug(f"Retrieved calculated_data - "
                  f"Future Retirement Contribution: {future_retirement_value_contrib}, "
                  f"Balance with Expenses: {investment_balance_after_expenses}, "
                  f"Total Employee Stock Plan: {total_employee_stockplan}, "
                  f"Investment Projected Growth: {investment_projected_growth}")

    # Retrieve house info, setting defaults if keys are missing
    new_house_value = house_info.get("new_house_value", 0)
    house_capital_investment = house_info.get("house_capital_investment", 0)
    house_networth_future = house_info.get("house_networth_future", 0)
    sell_house = house_info.get("sell_house", False)  # Get sell_house flag, default to False if not present

    logging.debug(f"Retrieved house_info - "
                  f"New House Value: {new_house_value}, "
                  f"House Capital Investment: {house_capital_investment}, "
                  f"House Net Worth Future: {house_networth_future}, "
                  f"Sell House: {sell_house}")

    # Calculation based on whether a new house is involved
    if new_house:
        combined_networth_future = (
            future_retirement_value_contrib + new_house_value +
            investment_balance_after_expenses + house_capital_investment + total_employee_stockplan
        )
        logging.info(f"{'New House?':<23} Yes - Included New House Value: {new_house_value} and "
                     f"House Capital Investment: {house_capital_investment}")
    else:
        # Only include investment_projected_growth if sell_house is True
        if sell_house:
            combined_networth_future = (
                future_retirement_value_contrib + investment_balance_after_expenses + 
                house_networth_future + investment_projected_growth + total_employee_stockplan
            )
            logging.info(f"{'New House?':<23} No - House will be sold, including House Net Worth Future: {house_networth_future} "
                         f"and Investment Projected Growth: {investment_projected_growth}")
        else:
            combined_networth_future = (
                future_retirement_value_contrib + investment_balance_after_expenses + 
                house_networth_future + total_employee_stockplan
            )
            logging.info(f"{'New House?':<23} No - House will not be sold, included House Net Worth Future: {house_networth_future}")

    # Log the final projected net worth
    logging.info(f"{'Projected Net Worth:':<23} {format_currency(combined_networth_future)}")

    return combined_networth_future


def _calculate_future_net_worth_houseinfo(new_house, calculated_data, house_info):
    logging.debug("Entered calculate_future_net_worth_houseinfo")

    # Retrieve calculated data with default values
    future_retirement_value_contrib = calculated_data.get("future_retirement_value_contrib", 0)
    investment_balance_after_expenses = calculated_data.get("investment_balance_after_expenses", 0)
    total_employee_stockplan = calculated_data.get("total_employee_stockplan", 0)
    investment_projected_growth = calculated_data.get("investment_projected_growth", 0)

    logging.debug(f"Retrieved calculated_data - "
                  f"Future Retirement Contribution: {future_retirement_value_contrib}, "
                  f"Balance with Expenses: {investment_balance_after_expenses}, "
                  f"Total Employee Stock Plan: {total_employee_stockplan}, "
                  f"Investment Projected Growth: {investment_projected_growth}")

    # Retrieve house info, setting defaults if keys are missing
    new_house_value = house_info.get("new_house_value", 0)
    house_capital_investment = house_info.get("house_capital_investment", 0)
    house_networth_future = house_info.get("house_networth_future", 0)

    logging.debug(f"Retrieved house_info - "
                  f"New House Value: {new_house_value}, "
                  f"House Capital Investment: {house_capital_investment}, "
                  f"House Net Worth Future: {house_networth_future}")

    # Calculation based on whether a new house is involved
    if new_house:
        combined_networth_future = (
            future_retirement_value_contrib + new_house_value +
            investment_balance_after_expenses + house_capital_investment + total_employee_stockplan
        )
        logging.info(f"{'New House?':<23} Yes - Included New House Value: {new_house_value} and "
                     f"House Capital Investment: {house_capital_investment}")
    else:
        combined_networth_future = (
            future_retirement_value_contrib + investment_balance_after_expenses + 
            house_networth_future + investment_projected_growth + total_employee_stockplan
        )
        logging.info(f"{'New House?':<23} No - Included Existing House Net Worth Future: {house_networth_future} and "
                     f"Investment Projected Growth: {investment_projected_growth}")

    # Log the final projected net worth
    logging.info(f"{'Projected Net Worth:':<23} {format_currency(combined_networth_future)}")

    return combined_networth_future


def calculate_financial_values(config_data, tax_rate):
    logging.debug("Entering <function")
    calculated_data = calculate_income_expenses(config_data, tax_rate)
    investment_values = calculate_investment_values(config_data, calculated_data["annual_surplus"])

    # Combine calculated_data and investment_values into one dictionary
    calculated_data = calculated_data.copy()  # Create a copy of calculated_data
    calculated_data.update(investment_values)  # Update with investment_values
    logging.info("Exiting <function")

    return calculated_data

def calculate_house_info(config_data):
    logging.debug("Entering <function calculate_house_info>")

    current_house, new_house = initialize_house_variables(config_data)
    house_info = calculate_house_data(current_house=current_house, config_data=config_data, new_house=new_house)

    # Check if house_info is None
    if house_info is None:
        logging.warning("house_info is None. Using an empty dictionary for logging.")
        house_info = {}

    utils.log_data(house_info, title="House Info")
    logging.debug("Exiting <function calculate_house_info>")

    return current_house, new_house, house_info



def calculate_school_expense_coverage(calculated_data):
    """
    Calculate the coverage of school expenses for each year.

    Args:
        calculated_data (dict): Dictionary containing financial data.

    Returns:
        school_expense_coverage (list): List containing coverage of school expenses for each year.
    """
    logging.debug("Entering <function ")

    annual_surplus = calculated_data.get("annual_surplus", 0)
    annual_surplus = max(annual_surplus, 0)
    school_expenses = calculated_data.get("school_expenses", [])

    school_expense_coverage = can_cover_school_expenses_per_year([annual_surplus] * len(school_expenses), school_expenses)
    logging.debug(f"School Expense Coverage: {school_expense_coverage}")

    return school_expense_coverage

def calculate_expenses_and_net_worth(config_data, calculated_data, house_info):
    """
    Calculate the coverage of school expenses for each year and net worth.

    Args:
        config_data (dict): Configuration data for the financial scenario.
        calculated_data (dict): Calculated financial values.
        house_info (dict): Dictionary containing house information.

    Returns:
        None
    """
    logging.debug("Entering <function ")

    # Calculate the coverage of school expenses for each year
    calculated_data["school_expense_coverage"] = calculate_school_expense_coverage(calculated_data)
    
    calculated_data["yearly_income_report"] = calculate_yearly_income_report(config_data, calculated_data)
    calculated_data["scenario_info"] = calculate_scenario_info(config_data, calculated_data)
    calculated_data["avg_yearly_fee"] = calculate_avg_yearly_school_fee(config_data, calculated_data)
    calculated_data["yearly_net_minus_school"] = calculate_yearly_net_minus_school(config_data, calculated_data)


    # Calculate combined net worth
    calculated_data["combined_networth"] = calculate_combined_net_worth(config_data, house_info, calculated_data)
    new_house = house_info.get("new_house", {})
    calculated_data = calculated_data or {}
    house_info = house_info or {}

    calculated_data["combined_networth_future"] = calculate_future_net_worth_houseinfo(
        new_house, calculated_data, house_info
    )



def calculate_scenario_info(config_data, calculated_data):
    """
    Calculate living expenses and location data.

    Args:
        config_data (object): Object containing configuration data for the financial scenario.
        calculated_data (object): Object containing calculated data for the financial scenario.

    Returns:
        scenario_info (dict): Dictionary containing the scenario.
    """
    logging.debug("Entering <function ")

    years = config_data["years"]
    scenario_info = {
        "Live in": config_data["residence_location"],
        "Work Status": get_work_status(config_data),
        "High School": config_data["highschool"],
        "Home Tenure": config_data["home_tenure"],
        "# of Years": config_data["years"],
    }
    utils.log_data(scenario_info, title="Scenario Summary")
    return scenario_info

def calculate_yearly_income_report(config_data, calculated_data):
    """
    Calculate living expenses and location data.

    Args:
        config_data (object): Object containing configuration data for the financial scenario.
        calculated_data (object): Object containing calculated data for the financial scenario.

    Returns:
        yearly_income_report_data (dict): Dictionary containing living expenses and location data.
    """
    logging.debug("Entering <function ")

    years = config_data["years"]
    spouse1_yearly_income_combined = calculated_data["yearly_data"].get("Spouse 1 Yearly Income Combined", "Not found")
    spouse2_yearly_income_combined = calculated_data["yearly_data"].get("Spouse 2 Yearly Income Combined", "Not found")
    parent_one = config_data["parent_one"]
    parent_two = config_data["parent_two"]
    # Calculate living expenses data
    yearly_income_report_data = {
        "Annual Income Surplus": calculated_data.get("annual_surplus", 0),  # Default to 0 if missing
        f"Annual Income {parent_one}": spouse1_yearly_income_combined,
        f"Annual Income {parent_two}": spouse2_yearly_income_combined,
        "Annual Gains (other)": config_data.get("yearly_gain", 0),
        "Annual Expenses (other)": config_data.get("yearly_expense", 0),
        "Annual Vacation": config_data.get("annual_vacation", 0),
        "Annual Rent": config_data.get("annual_rent", 0),
        "Annual Additional Insurance": config_data.get("additional_insurance", 0),
    }
    utils.log_data(yearly_income_report_data, title="Annual Income")
    return yearly_income_report_data


def retrieve_assumptions(config_data, tax_rate):
    """
    Retrieve assumption data used in calculations

    Args:
        config_data (object): Object containing configuration data for the financial scenario.
        calculated_data (object): Object containing calculated data for the financial scenario.

    Returns:
        data (dict): Dictionary containing living expenses and location data.
    """
    logging.debug("Entering <function ")

    data = {
        "Assumed tax rate": tax_rate,
        "federal tax rate dual": config_data["federal_tax_rate_dual"],
        "State tax rate dual": config_data["state_tax_rate_dual"],
        "federal tax rate single": config_data["federal_tax_rate_single"],
        "State tax rate dual": config_data["state_tax_rate_single"],
        "Interest rate": config_data["interest_rate"],
        "house_annual_growth_rate": config_data.get("house", {}).get("annual_growth_rate")
    }
    logging.info(f"{data}")
    return data

def calculate_school_expenses(config_data, flatten=False):
    """
    Calculate combined college and high school expenses for each child and return a list of expenses.

    Args:
        config_data (dict): A dictionary containing the 'children' key, which is a list of children with their
                            respective college and high school expenses.
        flatten (bool): A flag to determine if the result should be flattened across all children.

    Returns:
        list: A list of combined school expenses (college + high school) for each year.
    """
    # Initialize a list to hold combined expenses for each year
    years_to_consider = config_data.get('years', 0)
    combined_expenses_by_year = [0] * years_to_consider

    # Find the minimum year for proper indexing
    min_year = float('inf')

    # First pass to find the minimum year
    for child in config_data.get('children', []):
        for entry in child['school'].get('college', []):
            min_year = min(min_year, entry['year'])
        for entry in child['school'].get('high_school', []):
            min_year = min(min_year, entry['year'])

    # Adjust the index based on the minimum year
    year_offset = min_year  # No need for -1 if years are given as 2025, 2026, etc.

    # Iterate over each child
    for child in config_data.get('children', []):
        college_expenses = child['school'].get('college', [])
        highschool_expenses = child['school'].get('high_school', [])

        # Combine the college and high school expenses for each year
        for entry in college_expenses:
            year_index = entry['year'] - year_offset  # Adjust to zero-based index
            if 0 <= year_index < years_to_consider:
                combined_expenses_by_year[year_index] += entry['cost']

        for entry in highschool_expenses:
            year_index = entry['year'] - year_offset  # Adjust to zero-based index
            if 0 <= year_index < years_to_consider:
                combined_expenses_by_year[year_index] += entry['cost']

    # Capture the result
    school_expenses = combined_expenses_by_year

    # Debug: Print the structure before flattening
    print("School Expenses Before Flattening:", school_expenses)

    # Flatten the result if requested
    if flatten:
        # Ensure school_expenses is in a list of lists format before flattening
        if isinstance(school_expenses, list) and all(isinstance(i, list) for i in school_expenses):
            school_expenses = [sum(x) for x in zip(*school_expenses)]
        else:
            # Handle the case where flattening is requested but not possible
            print("Cannot flatten; 'school_expenses' is not in a list of lists format.")
            school_expenses = school_expenses  # No flattening occurs

    return school_expenses


def calculate_school_expenses_old(config_data, calculated_data):
    """

    Args:
        config_data (object): Object containing configuration data for the financial scenario.
        calculated_data (object): Object containing calculated data for the financial scenario.

    Returns:
        school_expenses_data (dict): Dictionary containing school expenses.
    """
    logging.debug("Entering <function ")

    years = config_data["years"]
    avg_yearly_fee = calculated_data["total_school_expense"] / years
    yearly_net_minus_school = calculated_data["annual_surplus"] - (calculated_data["total_school_expense"] / years)

    logging.info(f"{'Average Yearly School Fee:':<34} {format_currency(avg_yearly_fee)}")
    logging.info(f"{'Yearly Net (Minus School):':<34} {format_currency(yearly_net_minus_school)}")

    school_expenses_data = {
        "Avg. Yearly School Fee": avg_yearly_fee,
        "Yearly Net Minus School ": yearly_net_minus_school
    }
    return school_expenses_data

def calculate_avg_yearly_school_fee(config_data, calculated_data):
    """
    Calculate and log the average yearly school fee.

    Args:
        config_data (object): Object containing configuration data for the financial scenario.
        calculated_data (object): Object containing calculated data for the financial scenario.

    Returns:
        float: The average yearly school fee.
    """
    logging.debug("Entering calculate_avg_yearly_school_fee function")

    years = config_data["years"]
    avg_yearly_fee = calculated_data["total_school_expense"] / years

    # Log the average yearly school fee
    logging.info(f"{'Average Yearly School Fee:':<34} {format_currency(avg_yearly_fee)}")

    return avg_yearly_fee


def calculate_yearly_net_minus_school(config_data, calculated_data):
    """
    Calculate and log the yearly net minus school expenses.

    Args:
        config_data (object): Object containing configuration data for the financial scenario.
        calculated_data (object): Object containing calculated data for the financial scenario.

    Returns:
        float: The yearly net income minus school expenses.
    """
    logging.debug("Entering calculate_yearly_net_minus_school function")

    avg_yearly_fee = calculate_avg_yearly_school_fee(config_data, calculated_data)  # Reuse the first function
    yearly_net_minus_school = calculated_data["annual_surplus"] - avg_yearly_fee

    # Log the yearly net minus school expenses
    logging.info(f"{'Yearly Net (Minus School):':<34} {format_currency(yearly_net_minus_school)}")

    return yearly_net_minus_school


def analyze_tuition_data(config_data):
    """Analyzes tuition data and calculates total and average expenses per year.

    Args:
        data (dict): The JSON data containing tuition information.

    Returns:
        list: A list of dictionaries containing child information, total expenses, and average expenses per year.
    """

    results = []
    for child in config_data["children"]:
        child_data = {"name": child["name"]}
        child_data["total_school_expenses"] = {}
        child_data["average_expenses"] = {}

        for expense_type in ["college", "high_school"]:
            child_data["total_school_expenses"][expense_type] = sum(expense["cost"] for expense in child["expenses"][expense_type])
            child_data["average_expenses"][expense_type] = child_data["total_school_expenses"][expense_type] / len(child["expenses"][expense_type])

        child_data["total_school_expenses"]["combined"] = sum(child_data["total_school_expenses"].values())
        child_data["average_expenses"]["combined"] = child_data["total_school_expenses"]["combined"] / 4  # Assuming 4 years of data

        results.append(child_data)

    return results

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
    logging.debug("Entering <function ")
    if years_override is not None:
        logging.info(f"Overriding years with {years_override}.")
        config_data["years"] = years_override

    # Adjust SKI_TEAM data
    if include_ski_team == "exclude":
        config_data["SKI_TEAM"] = {}
        logging.info(f"{'SKI_TEAM data:':<46} {'Excluded'}")
    elif include_ski_team == "use_local_defined":
        ski_team_years = config_data["SKI_TEAM"].get("ski_team_years", 1)
        adjusted_ski_team_data = {
            key: (value if key == "ski_team_years" else (value if ski_team_years == 1 else 0))
            for key, value in config_data["SKI_TEAM"].items()
        }
        config_data["SKI_TEAM"] = adjusted_ski_team_data
        logging.info(f"{'SKI_TEAM data:':<42} {'Local scenario'}")
        logging.info(f"{'Adjusted SKI_TEAM data:':<42} {adjusted_ski_team_data}")
    else:
        ski_team_years = ski_team_data.get("ski_team_years", 1)
        adjusted_ski_team_data = {
            key: (value if key == "ski_team_years" else (value if ski_team_years == 1 else 0))
            for key, value in ski_team_data.items()
        }
        config_data["SKI_TEAM"] = adjusted_ski_team_data
        logging.info("Using provided SKI_TEAM data with adjustments.")
        logging.info(f"Adjusted SKI_TEAM data: {adjusted_ski_team_data}")

    # Adjust BASEBALL_TEAM data
    if include_baseball_team == "exclude":
        config_data["BASEBALL_TEAM"] = {}
        logging.info(f"{'BASEBALL_TEAM data:':<42} Excluded")
    elif include_baseball_team == "use_local_defined":
        baseball_team_years = config_data["BASEBALL_TEAM"].get("baseball_team_years", 1)
        adjusted_baseball_team_data = {
            key: (value if key == "baseball_team_years" else (value if baseball_team_years == 1 else 0))
            for key, value in config_data["BASEBALL_TEAM"].items()
        }
        config_data["BASEBALL_TEAM"] = adjusted_baseball_team_data
        logging.info(f"{'BASEBALL_TEAM data:':<46} Local scenario")
        # logging.info(f"Adjusted BASEBALL_TEAM data: {adjusted_baseball_team_data}")
    else:
        baseball_team_years = baseball_team_data.get("baseball_team_years", 1)
        adjusted_baseball_team_data = {
            key: (value if key == "baseball_team_years" else (value if baseball_team_years == 1 else 0))
            for key, value in baseball_team_data.items()
        }
        config_data["BASEBALL_TEAM"] = adjusted_baseball_team_data
        logging.info(f"{'BASEBALL_TEAM data:':<46} {'Using global scenario'}")

    # Adjust highschool_expenses data
    if include_highschool_expenses == "exclude":
        default_expenses = [0] * len(config_data.get("highschool_expenses", [0]*9))
        config_data["highschool_expenses"] = default_expenses
        logging.info(f"{'High school expenses:':<45}  {'Excluded'}")
    elif include_highschool_expenses == "use_local_defined":
        config_data["highschool_expenses"] = config_data.get("highschool_expenses", [0]*9)
        logging.info(f"{'High school expenses:':<45}  Local scenario")
    else:
        config_data["highschool_expenses"] = highschool_expenses_data
        logging.info(f"{'High school expenses:':<45}  {'Using global scenario'}")


def determine_report_name(scenarios_data, report_name_prefix="scenario_"):
    """
    Determines the name of the report based on the selected scenarios and configuration.
    
    :param scenarios_data: Dictionary containing scenarios and configuration details
    :param report_name_prefix: Prefix for the report name, default is 'scenario_'
    :return: The determined report name
    """
    # Ensure 'selected_scenarios' exists in scenarios_data
    if "selected_scenarios" not in scenarios_data:
        raise KeyError("The key 'selected_scenarios' is missing from scenarios_data.")
    
    # Logic to determine report name
    if len(scenarios_data['selected_scenarios']) == 1:
        return f"{report_name_prefix}{scenarios_data['selected_scenarios'][0]}"
    
    return "summary_report"


def generate_report(config_data, scenario_name):
    logging.debug(f"Starting report generation for scenario: {scenario_name}")

    if not config_data:
        logging.error("config_data is missing")
        raise ValueError("config_data is missing")

    logging.debug(f"Initial config_data keys: {list(config_data.keys())}")
    
    # Apply children variant
    logging.debug("Applying children variant")
    children_data = apply_children_variant(config_data.get('children', []), config_data)
    config_data['children'] = children_data
    logging.debug(f"Processed children data: {children_data}")

    # Apply variants for both spouses
    logging.debug("Applying spouse1 variant")
    spouse1_data = apply_spouse_variant(config_data.get('spouse1', {}), 'spouse1', config_data)
    logging.debug(f"Processed spouse1 data: {spouse1_data}")

    logging.debug("Applying spouse2 variant")
    spouse2_data = apply_spouse_variant(config_data.get('spouse2', {}), 'spouse2', config_data)
    logging.debug(f"Processed spouse2 data: {spouse2_data}")

    config_data['spouse1_data'] = spouse1_data
    config_data['spouse2_data'] = spouse2_data

    tax_rate = calculate_tax_rate(config_data)
    logging.info(f"Calculated tax rate: {tax_rate}")

    logging.debug("Calculating financial values")
    calculated_data = calculate_financial_values(config_data, tax_rate)
    calculated_data["scenario_name"] = scenario_name
    logging.debug(f"Calculated data: {calculated_data}")

    total_investment_balance = calculate_total_investments(config_data.get('INVESTMENTS', {}))
    logging.info(f"Total investment balance: {total_investment_balance}")
    calculated_data["total_investment_balance"] = total_investment_balance

    total_retirement_principal = calculate_retirement_principal(config_data.get('RETIREMENT', []))
    logging.info(f"Total retirement principal: {total_retirement_principal}")
    calculated_data["total_retirement_principal"] = total_retirement_principal

    logging.debug("Calculating house info")
    current_house, new_house, house_info = calculate_house_info(config_data)
    
    if house_info is None:
        logging.error("house_info is None. Ensure calculate_house_info returns valid data.")
        raise ValueError("house_info is None. Ensure calculate_house_info returns valid data.")
    logging.debug(f"House info: {house_info}")

    invest_capital_from_house_sale = house_info.get("invest_capital", 0)
    logging.info(f"Investment capital from house sale: {invest_capital_from_house_sale}")

    if invest_capital_from_house_sale is None:
        logging.warning("invest_capital_from_house_sale is None; defaulting to 0.")
        invest_capital_from_house_sale = 0

    logging.debug("Calculating future values")
    sale_of_house_investment = calculate_future_value(invest_capital_from_house_sale, 0, 0, config_data["interest_rate"], config_data["years"])
    investment_projected_growth = calculate_future_value(total_investment_balance, 0, 0, config_data["interest_rate"], config_data["years"])
    calculated_data["investment_projected_growth"] = investment_projected_growth

    calculate_expenses_and_net_worth(config_data, calculated_data, house_info)

    logging.debug(f"Projected growth for investments: {investment_projected_growth}")
    investment_principal = calculated_data.get("investment_balance_after_expenses", 0)
    house_capital_investment = house_info.get("house_capital_investment", 0)

   # Prepare report data
    logging.debug("Preparing report data.")
    report_data = {
        "config_data": config_data,
        "calculated_data": calculated_data,
        "house_info": house_info,
        "current_house": current_house,
        "new_house": new_house,
    }

    # Generate HTML sections for the report
    try:
        logging.debug("Generating HTML sections")
        future_value_html = report_html_generator.generate_future_value_html_table(
            report_data, invest_capital_from_house_sale, sale_of_house_investment, investment_projected_growth
        )
        logging.debug("Generated future value HTML table.")

        current_value_html = report_html_generator.generate_current_networth_html_table(
            report_data, invest_capital_from_house_sale, sale_of_house_investment, investment_projected_growth
        )
        logging.debug("Generated current net worth HTML table.")

        scenario_summary_html = report_html_generator.generate_section_html(
            "Scenario", calculated_data.get("scenario_info", {})
        )
        logging.debug("Generated scenario summary HTML.")

        yearly_net_html = report_html_generator.generate_section_html(
            "Cash Flow Before School Fees", calculated_data.get("yearly_income_report", {}), custom_formatter=format_currency
        )
        logging.debug("Generated yearly net HTML.")

        yearly_net_minus_school = float(calculated_data.get("yearly_net_minus_school", 0))
        avg_yearly_fee = float(calculated_data.get("avg_yearly_fee", 0))
        cashflow_After_school_data = {
            "Average Annual School Fees": avg_yearly_fee,
            "Cash Flow After School Fees": yearly_net_minus_school,
        }

        total_after_fees_html = report_html_generator.generate_section_html(
            "Cash Flow After School Fees", cashflow_After_school_data, custom_formatter=format_currency
        )
        logging.debug("Generated cash flow after school fees HTML.")

        assumptions_html = report_html_generator.generate_section_html(
            section_title="Assumptions", data=retrieve_assumptions(config_data, tax_rate), custom_formatter=None, collapsible=True
        )
        logging.debug("Generated assumptions HTML.")

        monthly_expenses_html = report_html_generator.generate_section_html(
            section_title="Monthly Expenses Breakdown", data=calculated_data.get("monthly_expenses_breakdown", {}), custom_formatter=format_currency, collapsible=True
        )
        logging.debug("Generated monthly expenses breakdown HTML.")

        expenses_not_factored_html = report_html_generator.generate_section_html(
            section_title="Expenses Not Factored In", data=calculated_data.get("expenses_not_factored_in_report", {}), custom_formatter=None, collapsible=True
        )
        logging.debug("Generated expenses not factored in HTML.")

        school_expenses_table_html = report_html_generator.generate_table_for_child(
            config_data, headers=["School", "Year", "Cost"]
        )
        logging.debug("Generated school expenses table HTML.")

        retirement_table_html = report_html_generator.generate_retirement_table(
            config_data, table_class="retirement-table"
        )
        logging.debug("Generated retirement table HTML.")

        investment_table_html = report_html_generator.generate_investment_table(
            config_data.get("INVESTMENTS", {}), format_currency
        )
        logging.debug("Generated investment table HTML.")

        current_house_html = report_html_generator.generate_current_house_html(current_house)
        logging.debug("Generated current house HTML.")

        new_house_html = report_html_generator.generate_new_house_html(new_house)
        logging.debug("Generated new house HTML.")

    except Exception as e:
        logging.error(f"Error generating HTML sections for scenario '{scenario_name}': {str(e)}")
        raise

    summary_data = {
        "house_capital_investment": house_capital_investment,
        "investment_principal": investment_principal,
        "assumption_description": config_data.get("assumption_description", ""),
        "description_detail": config_data.get("description_detail", ""),
        "annual_surplus": calculated_data.get("annual_surplus", ""),
        "future_value": future_value_html,
        "current_value": current_value_html,
        "scenario_summary_info": scenario_summary_html,
        "yearly_net_html": yearly_net_html,
        "assumptions_html": assumptions_html,
        "monthly_expenses_html": monthly_expenses_html,
        "expenses_not_factored_html": expenses_not_factored_html,
        "total_after_fees_html": total_after_fees_html,
        "school_expenses_table_html": school_expenses_table_html,
        "investment_table_html": investment_table_html,
        "retirement_table_html": retirement_table_html,
        "current_house_html": current_house_html,
        "new_house_html": new_house_html,
    }

    # Generate the complete report HTML
    try:
        logging.debug(f"Generating complete HTML report for scenario: {scenario_name}")
        scenario_html = report_html_generator.generate_html(report_data)
        report_filename = Path(__file__).parent.parent / f"reports/detail_{scenario_name}.html"
        logging.debug(f"report_filename: {report_filename}")
        # Ensure the reports directory exists
        Path(report_filename.parent).mkdir(parents=True, exist_ok=True)

        with open(report_filename, 'w', encoding="utf-8") as file:
            file.write(scenario_html)
            logging.info(f"Report saved successfully: {report_filename}")

    except Exception as e:
        logging.error(f"Failed to write report {report_filename}: {e}")
        raise

    logging.debug(f"Report generation completed for scenario: {scenario_name}") 
    return summary_data


def create_reports_directory():
    logging.debug("Entering <function ")
    reports_dir = Path(__file__).parent.parent / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    logging.info(f"{'Created:':<35} {reports_dir}")
    return reports_dir

def process_scenarios(input_file, scenarios_data, general_config, reports_dir, scenarios_dir="scenarios"):
    logging.debug("Entering process_scenarios")
    
    # Scenario selection logic
    if "sequence" not in input_file.stem:
        scenario_name = input_file.stem
        selected_scenarios = [scenario_name]  # Get the scenario name from the input file
        scenarios_data["selected_scenarios"] = selected_scenarios  # Ensure it's in scenarios_data

        # Merge general_config into scenarios_data
        for key, value in general_config.items():
            if key not in scenarios_data:
                variant_key = f"{key}_variant"
                if variant_key in scenarios_data:
                    # Use variant-specific data if available
                    variant_name = scenarios_data[variant_key]
                    if variant_name in general_config.get(key, {}):
                        scenarios_data[key] = general_config[key][variant_name]
                        logging.debug(f"Using variant '{variant_name}' for key '{key}'")
                else:
                    # Use the default value from general_config
                    scenarios_data[key] = value
                    logging.debug(f"Adding '{key}' from general_config to scenarios_data with value: {value}")
                  
        
    else:
        selected_scenarios = scenarios_data.get("selected_scenarios", [])
        if not selected_scenarios:
            logging.error("No selected scenarios found in scenarios_data for sequence processing.")
            return  # Exit the function if no scenarios are found

    # Store summary report data for all processed scenarios
    summary_report_data = {}

    # Process each selected scenario
    for scenario_name in selected_scenarios:
        logging.info(f"Processing scenario: {scenario_name}")

        scenario_file = Path(__file__).parent.parent / scenarios_dir / f"{scenario_name}.json"
        logging.debug(f"Scenario file: {scenario_file}")

        # Load scenario-specific data
        try:
            scenario_specific_data = load_config(scenario_file)
            if scenario_specific_data is None:
                logging.error(f"Loaded scenario data is None for {scenario_file}. Skipping this scenario.")
                continue  # Skip this scenario if the data is None
        except Exception as e:
            logging.error(f"Failed to load scenario file {scenario_file}: {str(e)}")
            continue  # Skip to the next scenario

        # Ensure scenarios_data and scenario_specific_data are dictionaries
        if not isinstance(scenarios_data, dict):
            logging.error("scenarios_data is not a valid dictionary.")
            continue
        if not isinstance(scenario_specific_data, dict):
            logging.error("scenario_specific_data is not a valid dictionary.")
            continue

        # Merge the scenario-specific data with scenarios_data
        config_data = {**scenarios_data, **scenario_specific_data}

        # Log essential config data
        logging.info(f"{'config_data:':<43} {'json'}")
        logging.info(f"{'years:':<43} {config_data.get('years', 'Not specified')}")
        logging.info(f"{'residence_location:':<43} {config_data.get('residence_location', 'Not specified')}")
        logging.info(f"{'home_tenure:':<43} {config_data.get('home_tenure', 'Not specified')}")

        # Generate the report
        try:
            summary_data = generate_report(config_data, scenario_name)
            summary_report_data[scenario_name] = summary_data  # Store as a dictionary
            logging.info(f"Report generated successfully for scenario: {scenario_name}")
        except Exception as e:
            logging.error(f"Error processing scenario {scenario_name}: {str(e)}")

        logging.info("-" * 70)  # Use a line of dashes or other separator

    # Determine the report name
    report_name = determine_report_name(scenarios_data)

    logging.info(f"Generating HTML report for scenarios: {', '.join(selected_scenarios)}")

    # Generate the HTML report
    summary_report_html = report_html_generator.generate_summary_report_html(summary_report_data)

    summary_report_filename = reports_dir / f"{report_name}.html"
    with summary_report_filename.open('w', encoding='utf-8') as summary_file:
        summary_file.write(summary_report_html)

    return summary_report_data  # Optionally return the summary report data if needed


def process_scenario(scenario_name, scenarios_data, reports_dir, scenarios_dir="scenarios"):
    logging.debug("Entering process_scenario")
    logging.info(f"{'Scenario:':<43} {scenario_name}")

    scenario_file = Path(__file__).parent.parent / scenarios_dir / f"{scenario_name}.json"
    logging.debug(f"Scenario file: {scenario_file}")

    # Load scenario-specific data
    scenario_specific_data = load_config(scenario_file)

    # Merge scenario-specific data with scenarios_data (and general_config by extension)
    config_data = {**scenarios_data, **scenario_specific_data}  # Merge dictionaries, with scenario-specific overwriting scenarios_data

    # Log essential config data
    logging.info(f"{'config_data:':<43} {'json'}")
    logging.info(f"{'years:':<43} {config_data.get('years', 'Not specified')}")
    logging.info(f"{'residence_location:':<43} {config_data.get('residence_location', 'Not specified')}")
    logging.info(f"{'home_tenure:':<43} {config_data.get('home_tenure', 'Not specified')}")

    # Safely get team data and log
    logging.debug("Local Scenario Objects")
    utils.log_data(config_data.get('BASEBALL_TEAM', {}), "Baseball Team")
    utils.log_data(config_data.get('SKI_TEAM', {}), "Ski Team")
    utils.log_data(config_data.get('highschool_expenses', {}), "High School Expenses")

    summary_data = generate_report(config_data, scenario_name)
    logging.info("-" * 70)  # Use a line of dashes or other separator

    return summary_data

# Merge children data from base_config if scenario indicates a specific variant
def merge_children_variants(base, scenario):
    """
    Merge children data from base_config if scenario indicates a specific variant.
    """
    # Check if 'children_variant' exists in the scenario
    if 'children_variant' in scenario:
        variant = scenario['children_variant']
        # Ensure the variant exists in the base configuration
        if variant in base.get('children_variants', {}):
            # Merge the children data from the variant
            scenario['children'] = base['children_variants'][variant]['children']
            logging.info(f"Children variant '{variant}' merged from base configuration.")
        else:
            logging.warning(f"Children variant '{variant}' not found in base configuration.")
    else:
        logging.info("No children variant specified in the scenario.")
