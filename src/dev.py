import math
import datetime
import investment_module
import report_html_generator
from pathlib import Path
import logging
from utils import format_currency
from html import escape

def generate_html(config_data):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Development Report</title>
        <link rel="stylesheet" href="../static/css/styles.css">
        <script src="../static/js/toggleVisibility.js"></script>
    </head>
    <body class="print-columns">
        <h1>Development Report</h1>
        <div class='header-container'>
    """
    html_content += generate_retirement_table(config_data, table_class="retirement-table")
    html_content += generate_table_html(config_data['Investment'])

    html_content += """
        </div> <!-- End of header-container -->
    </body>
    </html>
    """
    return html_content


def generate_retirement_table(config_data, table_class="retirement-table"):
    """Generates HTML table content for retirement contributions and accounts with totals.

    Args:
        config_data (dict): A dictionary containing retirement data for each person.
        table_class (str, optional): The CSS class to apply to the table.

    Returns:
        str: The generated HTML table content.
    """
    
    html_content = ""  # Initialize the HTML content

    retirement_data = config_data.get("RETIREMENT", [])  # Extract the "RETIREMENT" list
    grand_total_balance = 0  # Initialize grand total for all parents
    # Iterate through each parent in the retirement data
    for parent in retirement_data:
        parent_name = parent.get("name", "Unknown Parent")  # Get parent's name or default
        html_content += f"<div class='parent-section'>\n"
        html_content += f"<h2>{escape(parent_name)}</h2>\n"  # Display parent name as a section heading

        # Initialize totals
        total_contributions = 0
        total_accounts_balance = 0

        # Generate table for contributions
        html_content += "<h3>Contributions</h3>\n"
        html_content += f"<table class='{table_class}'>\n"
        html_content += "<thead>\n<tr><th>Type</th><th>Contribution</th><th>Amount</th></tr>\n</thead>\n<tbody>\n"

        contributions_data = parent.get("contributions", {})
        for contribution_type, entries in contributions_data.items():
            for entry in entries:
                for contribution, amount in entry.items():
                    formatted_amount = "{:,.2f}".format(amount)  # Format amount with commas
                    html_content += f"<tr><td>{escape(contribution_type)}</td><td>{escape(contribution)}</td><td>{formatted_amount}</td></tr>\n"
                    total_contributions += amount  # Add to total contributions

        # Display total contributions
        formatted_total_contributions = "{:,.2f}".format(total_contributions)
        html_content += f"<tr><td colspan='2'><strong>Total Contributions</strong></td><td><strong>{formatted_total_contributions}</strong></td></tr>\n"
        html_content += "</tbody>\n</table>\n"  # End of contributions table

        # Generate table for accounts
        html_content += "<h3>Accounts</h3>\n"
        html_content += f"<table class='{table_class}'>\n"
        html_content += "<thead>\n<tr><th>Account Type</th><th>Account Name</th><th>Balance</th></tr>\n</thead>\n<tbody>\n"

        accounts_data = parent.get("accounts", {})
        for account_type, entries in accounts_data.items():
            for entry in entries:
                for account_name, balance in entry.items():
                    formatted_balance = "{:,.2f}".format(balance)  # Format balance with commas
                    html_content += f"<tr><td>{escape(account_type)}</td><td>{escape(account_name)}</td><td>{formatted_balance}</td></tr>\n"
                    total_accounts_balance += balance  # Add to total accounts balance
                    grand_total_balance += balance

        # Display total account balances
        formatted_total_accounts = "{:,.2f}".format(total_accounts_balance)
        html_content += f"<tr><td colspan='2'><strong>Total Account Balances</strong></td><td><strong>{formatted_total_accounts}</strong></td></tr>\n"
        html_content += "</tbody>\n</table>\n"  # End of accounts table
        html_content += "</div>\n"  # End of parent section

    # Add grand total to the HTML content
    # html_content += "<h2>Grand Total</h2>\n"
    html_content += f"<table class='{table_class}'>\n"
    html_content += "<thead>\n<tr><th>Total Balance</th></tr>\n</thead>\n<tbody>\n"
    formatted_grand_total_balance = "{:,.2f}".format(grand_total_balance)
    html_content += f"<tr><td><strong>{formatted_grand_total_balance}</strong></td></tr>\n"
    html_content += "</tbody>\n</table>\n"

    return html_content

def generate_table_html(data, custom_formatter=None):
    """Generates HTML for a table based on the provided data.

    Args:
        data (dict or object): The data to be displayed in the table.
        custom_formatter (function, optional): A custom function to format the values.

    Returns:
        str: The generated HTML content for the table.
    """

    table_html = "<div class='table-container'><table>"

    if isinstance(data, dict):
        for key, value in data.items():
            formatted_value = custom_formatter(value) if custom_formatter else value
            table_html += f"<tr><th>{key}</th><td>{formatted_value}</td></tr>"
    elif hasattr(data, '__dict__'):
        for attr, value in data.__dict__.items():
            formatted_value = custom_formatter(value) if custom_formatter else value
            table_html += f"<tr><th>{attr}</th><td>{formatted_value}</td></tr>"

    table_html += "</table></div>"
    return table_html


def retrieve_assumptions(config_data, calculated_data):
    """
    Retrieve assumption data used in calculations

    Args:
        config_data (object): Object containing configuration data for the financial scenario.
        calculated_data (object): Object containing calculated data for the financial scenario.

    Returns:
        living_expenses_data (dict): Dictionary containing living expenses and location data.
    """
    logging.debug("Entering <function ")
    # logging.info(config_data)
    years = config_data["years"]
    # Calculate living expenses data
    data = {
        "Assumed tax rate": config_data["assumed_tax_rate"],
        "federal tax rate dual": config_data["federal_tax_rate_dual"],
        "State tax rate dual": config_data["state_tax_rate_dual"],
        "Interest rate": config_data["interest_rate"],
        "house_annual_growth_rate": config_data.get("house", {}).get("annual_growth_rate")
    }
    logging.info(f"{data}")
    return data

def main():
    log_dir = investment_module.create_log_directory()
    investment_module.setup_logging(log_dir, "dev.log")   
    reports_dir = investment_module.create_reports_directory()

    scenario_name = 'seq003.sf.havjason.work'
    scenarios_dir="scenarios"
    logging.info(f"{'Scenario:':<43} {scenario_name}")

    scenario_file = Path(__file__).parent.parent / scenarios_dir / f"{scenario_name}.json"
    config_data = investment_module.load_config(scenario_file)
    logging.info(f"{'retirement:':<43} {config_data['RETIREMENT']}")
    retrieve_assumptions(config_data, None)
    report_html = generate_html(config_data)
    report_html_filename = reports_dir / "dev_report.html"
    with report_html_filename.open('w') as report_file:
        report_file.write(report_html)

        

if __name__ == "__main__":
    main()