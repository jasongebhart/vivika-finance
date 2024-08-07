import investment_module

def print_data_section(section_title, data):
    """
    Print a section with a title and data.

    Args:
    - section_title (str): Title of the section.
    - data (dict): Dictionary containing data to be printed.

    Returns:
    None
    """
    print(section_title)
    print("-" * 45)  # Adjusted length to match original indentation
    for key, value in data.items():
        print(f"{key:<45} {value}")
    print("-" * 45)  # Adjusted length to match original indentation

def print_investment_evaluation(calculated_data):
    """
    Print the Future Investment Evaluation section along with financial data.

    Args:
    - calculated_data (object): Object containing calculated data for the financial scenario.

    Returns:
    None
    """
    financial_data = {
        "Yearly Surplus": calculated_data["yearly_gain"],
        "Monthly Surplus": calculated_data["monthly_surplus"],
        "Surplus Type": calculated_data["surplus_type"],
    }
    print_data_section("Future Investment Evaluation", financial_data)

def print_investment_section(config_data, calculated_data):
    """
    Print the investment section of the financial report.

    Args:
    - config_data (dict): Configuration data for the financial scenario.
    - calculated_data (dict): Calculated financial values.

    Returns:
    None
    """
    print("\nInvestment:")
    print("-" * 45)
    print("Investment Additions:")
    print("-" * 45)
    total_investment_balance = config_data.get('investment_balance', 0) + calculated_data.get('invest_capital', 0)
    print(f"{' Total Investment Balance':<45} {investment_module.format_currency(total_investment_balance)}")
    print("-" * 45)
    print(f"{' Investment Balance':<47} ${int(config_data.get('investment_balance', 0)):,}")
    print(f"{' House Amount to Reinvest':<47} ${calculated_data.get('invest_capital', 0):,.0f}")

    print("\nInvestment Projection:")
    print("-" * 45)
    print(f"{' Investment Principal':<45} ${int(calculated_data.get('balance_with_expenses', 0) + calculated_data.get('house_capital_investment', 0)):,}")


def print_retirement_section(config_data, calculated_data):
    """
    Print the retirement section of the financial report.

    Args:
    - config_data (dict): Configuration data for the financial scenario.
    - calculated_data (dict): Calculated financial values.

    Returns:
    None
    """
    retirement_data = {
        "Starting Retirement": f"${int(config_data.get('retirement_principal', 0)):,}",
        "Growth & Contributions": f"${int(calculated_data.get('future_retirement_value_contrib', 0)):,}"
    }
    print_data_section("Retirement:", retirement_data)

def print_expenses_section(calculated_data):
    """
    Print the expenses section of the financial report.

    Args:
    - calculated_data (dict): Dictionary containing calculated financial data.

    Returns:
    None
    """
    expenses_data = {
        "Total Expense": calculated_data.get("total_expense", 0),
        "High School Tuition x2": calculated_data.get("total_highschool_expense", 0),
        "College Tuition x2": calculated_data.get("total_college_expense", 0),
        "Yearly Income Deficit": calculated_data.get("yearly_income_deficit", 0),
    }
    print_data_section("Expenses:", expenses_data)


def print_future_value_section(report_data):
    """
    Print the future value section of the financial report.

    Args:
    - report_data (dict): Dictionary containing all necessary data for printing the future value section.

    Returns:
    None
    """
    years = report_data["config_data"]["years"]
    new_house = report_data["house_info"]["new_house"]
    new_house_value = report_data["house_info"]["new_house_value"]
    house_networth_future = report_data["house_info"]["house_networth_future"]
    total_employee_stockplan = report_data["calculated_data"]["total_employee_stockplan"]
    balance_with_expenses = report_data["calculated_data"]["balance_with_expenses"]
    house_capital_investment = report_data["house_info"]["house_capital_investment"]
    future_retirement_value_contrib = report_data["calculated_data"]["future_retirement_value_contrib"]
    combined_networth_future = report_data["calculated_data"]["combined_networth_future"]

    print(f"\nFuture Value in {years} years:")
    print("-" * 45)
    if new_house:
        print(f"{' House Net worth':<45} ${new_house_value:,.0f}")
    else:
        print(f"{' House Net worth':<45} ${house_networth_future:,.0f}")

    print(f"{' Stock Plan Investment Principal':<45} ${int(total_employee_stockplan):,}")
    print(f"{' Investment Principal':<45} ${int(balance_with_expenses + house_capital_investment):,}")
    print(f"{' Retirement Principal':<45} ${int(future_retirement_value_contrib):,}")
    print(f"{' Net worth':<45} ${combined_networth_future:,.0f}\n")

def print_house_details(current_house, house_info, config_data):
    """
    Print house details including sale and purchase information.

    Args:
    - current_house (House): Object representing the current house.
    - house_info (dict): Dictionary containing house information.
    - config_data (dict): Configuration data for the financial scenario.

    Returns:
    None
    """
    new_house = house_info["new_house"]
    # Extract relevant information from house_info
    sale_basis = house_info["sale_basis"]
    total_commission = house_info["total_commission"]
    capital_gain = house_info["capital_gain"]
    remaining_principal = house_info["remaining_principal"]
    invest_capital = house_info["invest_capital"]
    capital_from_house = house_info["capital_from_house"]
    new_house_cost = house_info["new_house_cost"]
    new_house_fees = house_info["new_house_fees"]
    house_capital_investment = house_info["house_capital_investment"]
    new_house_value = house_info["new_house_value"]
    house_value_future = house_info["house_value_future"]

    # Print house details
    if new_house:
        print(f"\nHouse - Sell House in {config_data['current_residence_location']}")
    else:
        print(f"\nHouse - {config_data['residence_location']}")
    print("-" * 45)

    if new_house:
        sale_details = [
            ("House Sale Value", f"${current_house.value:,}"),
            ("Basis", f"${current_house.calculate_basis():,}"),
            ("Purchase Price", f"${current_house.cost_basis:,}"),
            ("Closing Costs", f"${current_house.closing_costs:,}"),
            ("Home Improvement", f"${current_house.home_improvement:,}"),
            ("Sale basis", f"${sale_basis:,.0f}"),
            ("Sale Price", f"${current_house.value:,}"),
            ("Realtor Commission", f"-${total_commission:,.0f}"),
            ("Escrow", f"-${(current_house.value * 0.002):,.0f}"),
            ("Taxable Capital Gains", f"${int(capital_gain):,}"),
            ("Capital Gain", f"${int(sale_basis - current_house.calculate_basis()):,}"),
            ("Capital Gains Exclusion", f"-${int(investment_module.CAPITAL_GAIN_EXCLUSION):,}"),
            ("Capital Gains Owed (20%)", f"${int(capital_gain * .2):,}"),
            ("Other Placeholder", "$0"),  # Placeholder for other details
            ("Capital From House", f"${int(sale_basis - current_house.mortgage_principal - capital_gain):,}"),
            ("Sale basis", f"${sale_basis:,.0f}"),
            ("Mortgage Principal", f"-${current_house.mortgage_principal:,.0f}"),
            ("Capital Gains Owed (20%)", f"-${int(capital_gain * .2):,}")
        ]
    else:
        remaining_principal = None  # or provide an appropriate default value
        sale_details = [
            ("Mortgage Principal", f"${current_house.mortgage_principal:,.0f}"),
            ("Remaining Principal", f"${remaining_principal:,.0f}" if remaining_principal is not None else "N/A"),
            ("Estimated Value", f"${house_value_future:,.0f}")
        ]

    for label, value in sale_details:
        print(f"{label:<47} {value}")

    if new_house:
        print(f"\nPurchase House in {config_data['residence_location']}")
        print("-" * 45)
        print("invest_capital:", invest_capital)
        purchase_details = [
            ("House Amount to Reinvest", f"${invest_capital:,.0f}"),
            ("Capital From House", f"+${int(capital_from_house):,}"),
            ("New House Price Start", f"-${int(new_house_cost):,}"),
            ("New House Fees", f"-${int(new_house_fees):,}"),
            ("House Re-investment Value", f"${house_capital_investment:,.0f}"),
            ("House Increase Rate", f"{config_data['house_value_rate']}"),
            ("New House Growth", f"${new_house_value - new_house_cost:,.0f}"),
            ("House Net worth", f"${new_house_value:,.0f}")
        ]

        for label, value in purchase_details:
            print(f"{label:<45} {value}")

def print_expense_coverage_report(report):
    """
    Print the school expenses coverage report.

    Args:
    - report (list): List of tuples containing year, covered by salary flag, surplus, and deficit.

    Returns:
    None
    """
    header = "Year | Covered By Salary | Surplus | Deficit"
    print("School Expenses Coverage Report:")
    print("-" * len(header))
    print(header)
    print("-" * len(header))
    
    for year, covered, surplus, deficit in report:
        coverage_str = "Yes" if covered else "No"
        surplus_str = f"{surplus:.0f}" if surplus >= 0 else f"{surplus:.0f} (Deficit)"
        deficit_color = "\033[91m" if deficit > 0 else ""
        deficit_value = f"{deficit:.0f}"
        print(f"{year:<4} | {coverage_str:<17} | {surplus_str:>7} | {deficit_color}{deficit_value:<5}\033[0m")
    
    print("-" * len(header))


def print_current_values_section(house_info, config_data, calculated_data):
    """
    Print the current values section of the financial report.

    Args:
    - config_data (dict): Configuration data for the financial scenario.
    - calculated_data (dict): Calculated financial values.

    Returns:
    None
    """
    current_values_data = {
        "House Net worth": investment_module.format_currency(house_info.get("house_net_worth", 0)),
        "Investment Balance": investment_module.format_currency(config_data.get('investment_balance', 0)),
        "Retirement Balance": investment_module.format_currency(config_data.get('retirement_principal', 0)),
        "Combined Net worth": investment_module.format_currency(calculated_data.get("combined_networth", 0))
    }
    print_data_section("Current Values:", current_values_data)


def print_reports(report_data):
    """
    Print various reports based on the provided report data.

    Args:
    - report_data (dict): Dictionary containing all necessary data for printing reports.

    Returns:
    None
    """
    # Extract data from the dictionary
    config_data = report_data.get("config_data", {})
    calculated_data = report_data.get("calculated_data", {})
    house_info = report_data.get("house_info", {})
    current_house = report_data.get("current_house", {})
    
    # Print various reports
    print_data_section("Yearly Data:", calculated_data.get("yearly_data", {}))
    print_data_section("Monthly Expenses Breakdown:", calculated_data.get("monthly_expenses_breakdown", {}))
    print_data_section("Not Factored In", calculated_data["expenses_not_factored_in_report"])
    print_investment_evaluation(calculated_data)
    print_data_section("Scenario:", calculated_data["LIVING_EXPENSES"])
    print_expense_coverage_report(calculated_data["school_expense_coverage"])    
    print_current_values_section(house_info, config_data, calculated_data)
    print_house_details(current_house, house_info, config_data)
    print_investment_section(config_data, calculated_data)
    print_retirement_section(config_data, calculated_data)
    print_expenses_section(calculated_data)
    print_future_value_section(report_data)