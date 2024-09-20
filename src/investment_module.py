import logging
import sys  # import the sys module
from pathlib import Path
import json
import argparse
from collections import namedtuple
import report_html_generator
from utils import format_currency

CAPITAL_GAIN_EXCLUSION = 500000

def create_log_directory():
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir

def setup_logging(log_dir: Path, log_name: str):
    """
    Sets up logging configuration for a specific log file.

    Args:
        log_dir (Path): The directory where the log file should be created.
        log_name (str): The name of the log file (without the extension).
    """

    log_file_path = log_dir / log_name
    
    # Check if the file exists and delete it if necessary
    if log_file_path.exists():
        log_file_path.unlink()  # Use unlink() to delete the file
    
    # Create a custom logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Set the logging level

    # Create a file handler
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.INFO)

    # Create a console handler (optional)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Define a formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')

    # Set formatter for the handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Optionally, disable the default logging to prevent double logs
    logger.propagate = False

def log_data(data, title="Data"):
  """Logs a dictionary or list in a readable format.

  Args:
      data (dict or list): A dictionary containing the data or a list of values.
      title (str, optional): The title for the log message. Defaults to "Data".
  """

  if isinstance(data, list):
    # Handle lists
    formatted_data = ', '.join(map(str, data))
    logging.info(f"\n\n{title}:\n{formatted_data}\n")
  elif isinstance(data, dict):
    # Handle dictionaries
    formatted_data = '\n'.join(f"  {key}: {value}" for key, value in data.items())
    logging.info(f"\n\n{title}:\n{formatted_data}\n")
  else:
    logging.warning(f"Unsupported data type: {type(data)}")

def log_data_currency(data, title="Data"):
  """Logs a dictionary in a readable format, applying format_currency to numeric values.

  Args:
      data (dict): A dictionary containing the data.
      title (str, optional): The title for the log message. Defaults to "Data".
  """

  formatted_data = '\n'.join(
      f"  {key}: {format_currency(value) if isinstance(value, (int, float)) else value}"
      for key, value in data.items()
  )

  logging.info(f"\n\n{title}:\n{formatted_data}\n")


def parse_arguments():
    """
    Parses command-line arguments for the financial configuration script.

    Returns:
        argparse.Namespace: Parsed arguments containing the configuration file path.
    """
    logging.debug("Entering <function ")

    parser = argparse.ArgumentParser(description='Process financial configuration.')
    parser.add_argument('config_file_path', nargs='?', default='config.finance.json', help='Path to the configuration file')

    args = parser.parse_args()

    logging.info(f"Parsed arguments: {args}")
    return args

def load_config(config_file_path):
    logging.debug("Entering <function ")
    logging.info(f"{'Path:':<48} {config_file_path}")
    try:
        with open(config_file_path, 'r') as f:
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
    logging.debug("Entering <function ")

    args = parse_arguments()
    config_data = load_config(args.config_file_path)
    return config_data

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
    logging.debug("Entering <function ")
    logging.info(
        f"\n\n<calculate_balance> Balance with compounding interest:\n"
        f" balance={format_currency(balance)}\n"
        f" interest_rate={interest_rate}\n"
        f" years={years}\n"
        f" yearly_gain={format_currency(yearly_gain)}\n"
        f" gains={gains}\n"
        f" expenses={expenses}\n"
        f" yearly_expense={yearly_expense}\n"
    )
    # Print header for the log output
    logging.info("Creating Table ")
    logging.info(f"{'Year':<6} {'Balance':>12} {'Interest':>12} {'Net Gain':>12} {'Net Expense':>12}")

    for year in range(years):
        interest = balance * interest_rate
        net_gain = yearly_gain if yearly_gain != 0 else gains[year] if year < len(gains) else 0
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
    
    

def calculate_house_values(current_house, config_data):
    # Calculate sale basis and capital gains for the current house
    logging.debug("Entering <function ")
    logging.info("In order to realize the value of a house we need to determine the costs for selling it.")
    commission_rate_myhouse = config_data['house']['commission_rate']
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
    logging.debug("Entering <function ")
    if not new_house:
        logging.info("No new house, returning default values")
        return 0, 0, 0, 0, 0, 0, 0, 0  # Return default values if there's no new house

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
    logging.info(f"{'invest_capital:':<25} {format_currency(capital_from_house)} -{format_currency(new_house_cost_basis)} -{format_currency(new_house_fees)}")
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

def initialize_variables():
    return 0, 0, 0

def calculate_yearly_income(config_data, tax_rate):
    logging.debug("Entering <function ")
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
    log_data(yearly_data, title="<calculate_yearly_income> Yearly Data")
    return yearly_data

def calculate_yearly_surplus(monthly_surplus):
  """Calculates the yearly surplus based on the provided monthly surplus.

  Args:
      monthly_surplus: The amount of surplus each month.

  Returns:
      The total surplus for the year.
  """
  logging.info(f"{'Monthly_surplus':<35} {format_currency(monthly_surplus)}")
  yearly_surplus = monthly_surplus * 12
  logging.info(f"{'Yearly surplus':<35} {format_currency(yearly_surplus)}")
  return yearly_surplus

def determine_surplus_type(yearly_surplus):
  """Determines if the surplus is positive (gain) or negative (expense).

  Args:
      yearly_surplus: The total surplus for the year.

  Returns:
      A string indicating "Gain" if positive, "Expense" if negative, or "No Surplus/Expense" if zero.
  """
  logging.debug("Entering <function ")

  if yearly_surplus > 0:
    surplus_type = "Gain"
  elif yearly_surplus < 0:
    surplus_type = "Expense"
  else:
    surplus_type = "No Surplus/Expense"

  logging.info(f"{'Surplus type':<37} {surplus_type:}")
  return surplus_type

def format_currency(value):
  """Formats a numerical value as currency with commas."""
#   logging.info(f"format_currency: {value}")
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
    logging.debug("Entering <function ")

    logging.info(f"Checking if yearly surplus can cover school expenses")
    log_data(yearly_surplus, "yearly_surplus")
    log_data(school_expenses, "school_expenses")

    # Ensure lists have the same length
    if len(yearly_surplus) != len(school_expenses):
        logging.error("<can_cover_school_expenses_per_year> Yearly surplus and high school expenses lists must have the same length.")
        raise ValueError("<can_cover_school_expenses_per_year> Yearly surplus and high school expenses lists must have the same length.")

    report = []
    for year, expense in enumerate(school_expenses):
        surplus_used = min(expense, yearly_surplus[year])
        remaining_surplus = yearly_surplus[year] - surplus_used
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


def get_work_status(spouse1_income, spouse2_income):
    """
    Determines the work status based on spouse incomes.

    Args:
        spouse1_income: Spouse 1's base yearly income (numerical value, 0, or None).
        spouse2_income: Spouse 2's base yearly income (numerical value, 0, or None).

    Returns:
        A string indicating the work status ("Both Parents Work", "One Parent Works", or "No Parents Work").
    """
    logging.debug("Entering <function ")

    if spouse1_income is not None and spouse2_income is not None and spouse1_income > 0 and spouse2_income > 0:
        work_status = "Both Parents Work"
    elif (spouse1_income is not None and spouse1_income > 0) or (spouse2_income is not None and spouse2_income > 0):
        work_status = "One Parent Works"
    else:
        work_status = "No Parents Work"

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
    logging.info(f"{'Total monthly expenses:':<27} {format_currency(total_monthly_expenses)}")
    log_data(monthly_expenses_breakdown, "Monthly Expenses Breakdown")
    
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
    if 'new_house' in config_data and config_data['new_house'] is not None:
        logging.info("A New House is defined.")
        new_house = create_house_instance(config_data['new_house'])
    else:
        # Handle the case where new_house_data is None or empty
        logging.info("new_house data not found in config")
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


def calculate_combined_net_worth(config_data, house_net_worth):
    """
    Calculate the combined net worth.

    Args:
        config_data (dict): Configuration data for the financial scenario.
        house_net_worth (float): Net worth of the house.

    Returns:
        float: Combined net worth.
    """
    logging.debug("Entering <function ")

    combined_net_worth = config_data['investment_balance'] + config_data['retirement_principal'] + house_net_worth
    logging.info(f"{'Net Worth:':<31} {format_currency(combined_net_worth)}")
    return combined_net_worth

def calculate_financial_data(config_data, tax_rate):
    logging.debug("Entering <function ")
    yearly_data = calculate_yearly_income(config_data, tax_rate)
    total_monthly_expenses, monthly_expenses_breakdown = calculate_total_monthly_expenses(config_data)

    return yearly_data, total_monthly_expenses, monthly_expenses_breakdown

def calculate_expenses_not_factored_in_report(config_data):
    logging.debug("Entering <function ")
    expenses_not_factored_in_report = {
        "Total Widji": config_data.get('total_widji'),
        "Total Ski Camp": config_data.get('Total_ski_camp'),
        "Car Purchase": config_data.get('car_purchase'),
    }
    monthly_expenses = {f"Monthly {key}": int(value / 12) for key, value in expenses_not_factored_in_report.items()}
    expenses_not_factored_in_report.update(monthly_expenses)
    # logging.info("-" * 70)  # Use a line of dashes or other separator
    log_data(expenses_not_factored_in_report, title="Expenses Not Factored In Report")
    logging.debug("Exiting <function ")
    return expenses_not_factored_in_report


def calculate_surplus(yearly_data, total_monthly_expenses):
    logging.debug("Entering <function ")
    yearly_income = yearly_data["Yearly Net Income"]
    logging.info(f"{'Yearly Net Income':<42} {format_currency(yearly_income)}")
    logging.info(f"{'Monthly Net Income':<42} {format_currency(yearly_income / 12)}")
    logging.info(f"{'Monthly Expenses':<42} {format_currency(total_monthly_expenses)}")
    monthly_surplus = int(yearly_income / 12) - int(total_monthly_expenses)
    yearly_gain = calculate_yearly_surplus(monthly_surplus)
    surplus_type = determine_surplus_type(yearly_gain)

    return yearly_gain, surplus_type, monthly_surplus

def calculate_income_expenses(config_data, tax_rate):
    logging.debug("Entering <function ")
    yearly_data, total_monthly_expenses, monthly_expenses_breakdown = calculate_financial_data(config_data, tax_rate)
    expenses_not_factored_in_report = calculate_expenses_not_factored_in_report(config_data)
    yearly_gain, surplus_type, monthly_surplus = calculate_surplus(yearly_data, total_monthly_expenses)

    # Calculate expenses
    total_school_expense, total_highschool_expense, total_college_expense = calculate_total_school_expense(config_data)
    yearly_income_deficit = int(config_data['yearly_expense'])


    # Add expenses to the calculated_data dictionary
    calculated_data = {
        "yearly_data": yearly_data,
        "total_monthly_expenses": total_monthly_expenses,
        "monthly_expenses_breakdown": monthly_expenses_breakdown,
        "yearly_gain": yearly_gain,
        "surplus_type": surplus_type,
        "monthly_surplus": monthly_surplus,
        "total_school_expense": total_school_expense,
        "total_highschool_expense": total_highschool_expense,
        "total_college_expense": total_college_expense,
        "yearly_income_deficit": yearly_income_deficit,
        "expenses_not_factored_in_report": expenses_not_factored_in_report
    }

    return calculated_data

def calculate_investment_values(config_data, yearly_gain):
    logging.debug("Entering <function ")
    logging.info(f"{'yearly_gain':<32} {format_currency(yearly_gain)}")
    logging.info(f"{'yearly_gain':<32} {config_data.get('yearly_gain',0)}")

    yearly_gain=yearly_gain + config_data.get('yearly_gain',0)

    logging.info("Employee Stock Plan")
    total_employee_stockplan = calculate_future_value(
        config_data.get('employee_stock_purchase', 0),
        config_data.get('employee_stock_purchase', 0),
        increase_contribution=0,
        interest_rate=config_data.get('interest_rate', 0),
        years=config_data.get('years', 0))
    logging.info(f"{'Total Employee Stock Plan':<31} {format_currency(total_employee_stockplan)}")
    school_expenses = [a + b for a, b in zip(config_data.get('college_expenses', []), config_data.get('highschool_expenses', []))]

    logging.info(f"Investments & Expenses ")
    balance_with_expenses = calculate_balance(
        config_data.get('investment_balance', 0),
        config_data.get('interest_rate', 0),
        config_data.get('years', 0),
        yearly_gain=yearly_gain,
        gains=config_data.get('gains', 0),
        expenses=school_expenses,
        yearly_expense=config_data.get('yearly_expense', 0))
    
    logging.info(f"Retirement Valuation")
    future_retirement_value_contrib = calculate_future_value(
        config_data.get('retirement_principal', 0),
        config_data.get('initial_contribution', 0),
        config_data.get('increase_contribution', 0),
        config_data.get('interest_rate', 0),
        config_data.get('years', 0))

    investment_values = {
        "total_employee_stockplan": total_employee_stockplan,
        "school_expenses": school_expenses,
        "balance_with_expenses": balance_with_expenses,
        "future_retirement_value_contrib": future_retirement_value_contrib
    }

    log_data_currency(investment_values, title="Future Value")
    return investment_values

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
    logging.debug("Entering calculate_future_net_worth_houseinfo")

    # Retrieve calculated data
    future_retirement_value_contrib = calculated_data.get("future_retirement_value_contrib", 0)
    balance_with_expenses = calculated_data.get("balance_with_expenses", 0)
    total_employee_stockplan = calculated_data.get("total_employee_stockplan", 0)

    # Check for house_info keys, set to 0 if missing
    new_house_value = house_info.get("new_house_value", 0)
    house_capital_investment = house_info.get("house_capital_investment", 0)
    house_networth_future = house_info.get("house_networth_future", 0)

    # Calculation based on new_house existence
    if new_house:
        combined_networth_future = (
            future_retirement_value_contrib + new_house_value + 
            balance_with_expenses + house_capital_investment + total_employee_stockplan
        )
        logging.info(f"{'New House?':<23} Yes")
    else:
        combined_networth_future = (
            future_retirement_value_contrib + balance_with_expenses + 
            house_networth_future + total_employee_stockplan
        )
        logging.info(f"{'New House?':<23} No")

    # Log the final projected net worth
    logging.info(f"{'Projected Net Worth:':<23} {format_currency(combined_networth_future)}")
    return combined_networth_future



def calculate_financial_values(config_data, tax_rate):
    logging.debug("Entering <function")
    calculated_data = calculate_income_expenses(config_data, tax_rate)
    investment_values = calculate_investment_values(config_data, calculated_data["yearly_gain"])

    # Combine calculated_data and investment_values into one dictionary
    calculated_data = calculated_data.copy()  # Create a copy of calculated_data
    calculated_data.update(investment_values)  # Update with investment_values
    logging.info("Exiting <function")

    return calculated_data


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
    logging.debug(f"Entering <function ")
    if config_data["home_tenure"] == "Own":
        sale_basis, total_commission, capital_gain, house_net_worth, capital_from_house = calculate_house_values(current_house, config_data)
        if not new_house:
            new_house_cost_basis = new_house_future_value = new_house_fees = invest_capital = house_capital_investment = 0
        else:
            new_house_sale_basis, new_house_total_commission, new_house_taxable_capital_gain, new_house_cost_basis, new_house_future_value, new_house_fees, invest_capital, house_capital_investment = calculate_new_house_values(new_house, capital_from_house, config_data)
        
    elif config_data["home_tenure"] == "Rent":
        # Calculate house-related values for renting
        sale_basis, total_commission, capital_gain, house_net_worth, capital_from_house = calculate_house_values(current_house, config_data)
        new_house_cost_basis = new_house_future_value = new_house_fees = invest_capital = 0
        house_value_future = house_networth_future = remaining_principal = 0
        new_house_sale_basis, new_house_total_commission, new_house_taxable_capital_gain, new_house_cost_basis, new_house_future_value, new_house_fees, invest_capital, house_capital_investment = calculate_new_house_values(new_house, capital_from_house, config_data)

        # Here, you can sell the current house and invest the money if desired
    else:
        raise ValueError("Invalid value for home_tenure. Use 'own' or 'rent'.")
    house_networth_future, house_value_future, remaining_principal = calculate_future_house_values(new_house, config_data, current_house, new_house_future_value)    
    logging.debug(f"Exiting <function ")
    return {
        "sale_basis": sale_basis,
        "total_commission": total_commission,
        "capital_gain": capital_gain,
        "house_value_future": house_value_future,
        "house_net_worth": house_net_worth,
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


def calculate_house_info(config_data):
    logging.debug("Entering <function ")

    current_house, new_house = initialize_house_variables(config_data)
    house_info = calculate_house_data(current_house=current_house, config_data=config_data, new_house=new_house)

    log_data(house_info, title="House Info")
    logging.debug("Exiting <function ")

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

    yearly_gain = calculated_data.get("yearly_gain", 0)
    yearly_surplus = max(yearly_gain, 0)
    school_expenses = calculated_data.get("school_expenses", [])

    school_expense_coverage = can_cover_school_expenses_per_year([yearly_surplus] * len(school_expenses), school_expenses)
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
    
    calculated_data["LIVING_EXPENSES"] = calculate_living_expenses(config_data, calculated_data)
    calculated_data["scenario_info"] = calculate_scenario_info(config_data, calculated_data)
    calculated_data["avg_yearly_fee"] = calculate_avg_yearly_school_fee(config_data, calculated_data)
    calculated_data["yearly_net_minus_school"] = calculate_yearly_net_minus_school(config_data, calculated_data)


    # Calculate combined net worth
    calculated_data["combined_networth"] = calculate_combined_net_worth(config_data, house_info["house_net_worth"])
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
        "Work Status": get_work_status(config_data["spouse1_yearly_income_base"],
                                        config_data["spouse2_yearly_income_base"]),
        "High School": config_data["highschool"],
        "Home Tenure": config_data["home_tenure"],
    }
    log_data(scenario_info, title="Scenario Summary")
    return scenario_info

def calculate_living_expenses(config_data, calculated_data):
    """
    Calculate living expenses and location data.

    Args:
        config_data (object): Object containing configuration data for the financial scenario.
        calculated_data (object): Object containing calculated data for the financial scenario.

    Returns:
        living_expenses_data (dict): Dictionary containing living expenses and location data.
    """
    logging.debug("Entering <function ")

    years = config_data["years"]
    # Calculate living expenses data
    living_expenses_data = {
        "Yearly Income Surplus": calculated_data["yearly_gain"],
    }
    log_data(living_expenses_data, title="Living Expenses")
    return living_expenses_data


def retrieve_assumptions(config_data):
    """
    Retrieve assumption data used in calculations

    Args:
        config_data (object): Object containing configuration data for the financial scenario.
        calculated_data (object): Object containing calculated data for the financial scenario.

    Returns:
        living_expenses_data (dict): Dictionary containing living expenses and location data.
    """
    logging.debug("Entering <function ")

    data = {
        "Assumed tax rate": config_data["assumed_tax_rate"],
        "federal tax rate dual": config_data["federal_tax_rate_dual"],
        "State tax rate dual": config_data["state_tax_rate_dual"],
        "Interest rate": config_data["interest_rate"],
        "house_annual_growth_rate": config_data.get("house", {}).get("annual_growth_rate")
    }
    logging.info(f"{data}")
    return data

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
    yearly_net_minus_school = calculated_data["yearly_gain"] - (calculated_data["total_school_expense"] / years)

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
    yearly_net_minus_school = calculated_data["yearly_gain"] - avg_yearly_fee

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


def prepare_scenarios_data(scenarios_data):
    logging.debug("Entering <function ")

    prepared_data = {
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
    if 'selected_scenarios' in prepared_data:
      logging.info(f"Selected Scenarios:\n\n{''.join([f'{scenario:<24}\n' for scenario in prepared_data['selected_scenarios']])}")
    else:
      logging.warn(f"Selected Scenarios key not found in prepared_data")
    
    if 'years_override' in prepared_data:
      logging.info(f"{'Years Override:':<37} {prepared_data['years_override']}")
    else:
      logging.info(f"Years Override: Not specified") 
    
    return prepared_data


def generate_report(config_data, scenario_name):
    logging.debug(f"Scenario: {scenario_name}")

    if not config_data:
        logging.error("config_data is missing")
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
        "new_house": new_house,
    }

    future_value_html = report_html_generator.generate_future_value_html_table(report_data)
    current_value_html = report_html_generator.generate_current_networth_html_table(report_data)
    scenario_summary_html = report_html_generator.generate_section_html(
        "Scenario",
        calculated_data.get("scenario_info", {})
    )
    yearly_net_html = report_html_generator.generate_section_html(
        "Cash Flow Before School Fees",
        calculated_data.get("LIVING_EXPENSES", {}),
        custom_formatter=format_currency
    )
    avg_yearly_fee_html = report_html_generator.generate_section_html(
        "Projected Average Yearly School Costs",
        calculated_data.get("avg_yearly_fee", {}),
        custom_formatter=format_currency
    )
    cashflow_after_school_fee_html = report_html_generator.generate_section_html(
        "Cash Flow After School Fees",
        calculated_data.get("yearly_net_minus_school", {}),
        custom_formatter=format_currency
    )
    assumptions_html = report_html_generator.generate_section_html(
        section_title="Assumptions",
        data=retrieve_assumptions(config_data),
        custom_formatter=None,
        collapsible=True
    )
    
    monthly_expenses_html = report_html_generator.generate_section_html(
        section_title="Monthly Expenses Breakdown",
        data=calculated_data.get("monthly_expenses_breakdown", {}),
        custom_formatter=format_currency,
        collapsible=True
    )
    expenses_not_factored_html = report_html_generator.generate_section_html(
        section_title="Expenses Not Factored In",
        data=calculated_data.get("expenses_not_factored_in_report", {}),
        custom_formatter=None,
        collapsible=True
    )
    school_expenses_table_html = report_html_generator.generate_table_for_child(config_data, headers=["School", "Year", "Cost"])
    retirement_table_html = report_html_generator.generate_retirement_table(config_data, table_class="retirement-table")
    investment_table_html = report_html_generator.generate_investment_table(config_data.get("Investment", {}),format_currency)
    # current_house_html = report_html_generator.generate_current_house_html(report_data["current_house"])
    current_house_html = report_html_generator.generate_current_house_html(current_house)
    new_house_html = report_html_generator.generate_new_house_html(new_house)


    summary_data = {
        "assumption_description": config_data.get("assumption_description", ""),
        "description_detail": config_data.get("description_detail", ""),
        "yearly_gain": calculated_data.get("yearly_gain", ""),
        "future_value": future_value_html,
        "current_value": current_value_html,
        "scenario_summary_info": scenario_summary_html,
        "yearly_net_html": yearly_net_html,
        "assumptions_html": assumptions_html,
        "monthly_expenses_html": monthly_expenses_html,
        "expenses_not_factored_html": expenses_not_factored_html,
        "avg_yearly_fee_html": avg_yearly_fee_html,
        "cashflow_after_school_fee_html": cashflow_after_school_fee_html,
        "school_expenses_table_html": school_expenses_table_html,
        "investment_table_html": investment_table_html,
        "retirement_table_html": retirement_table_html,
        "current_house_html": current_house_html,
        "new_house_html": new_house_html,
    }

    scenario_html = report_html_generator.generate_html(report_data)
    report_filename = f"{Path(__file__).parent.parent}/reports/financial_report_{scenario_name}.html"
    with open(report_filename, 'w') as file:
        file.write(scenario_html)
        logging.info(f"Report: {report_filename}")

    logging.info(f"Scenario: {scenario_name}")
    return summary_data

def create_reports_directory():
    logging.debug("Entering <function ")
    reports_dir = Path(__file__).parent.parent / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    logging.info(f"{'Created:':<35} {reports_dir}")
    return reports_dir

def process_scenario(scenario_name, base_config, reports_dir, scenarios_dir="scenarios"):
    logging.debug("Entering <function")
    logging.info(f"{'Scenario:':<43} {scenario_name}")

    scenario_file = Path(__file__).parent.parent / scenarios_dir / f"{scenario_name}.json"
    logging.debug(f"Scenario file: {scenario_file}")
    config_data = load_config(scenario_file)
    # Log essential config data
    logging.info(f"{'config_data:':<43} {'json'}")
    logging.info(f"{'years:':<43} {config_data['years']}")
    logging.info(f"{'residence_location:':<43} {config_data['residence_location']}")
    logging.info(f"{'home_tenure:':<43} {config_data['home_tenure']}")
    logging.info(f"{'sell_house:':<43} {config_data['sell_house']}")

    adjust_config(
        config_data,
        base_config["years_override"],
        base_config["include_ski_team"], base_config["ski_team_data"],
        base_config["include_baseball_team"], base_config["baseball_team_data"],
        base_config["include_highschool_expenses"], base_config["highschool_expenses_data"]
    )
    logging.debug("Local Scenario Objects")
    log_data(config_data['BASEBALL_TEAM'], "Baseball Team")
    log_data(config_data['SKI_TEAM'], "Ski Team")
    log_data(config_data['highschool_expenses'], "High School Expenses")
  
    summary_data = generate_report(config_data, scenario_name)
    logging.info("-" * 70)  # Use a line of dashes or other separator

    return summary_data
