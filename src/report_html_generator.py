import os
from collections import defaultdict
from bs4 import BeautifulSoup, Tag
from utils import format_currency
from html import escape
from pathlib import Path
import re
import logging
import json  # Import the JSON module

def extract_numeric_value(currency_string):
    match = re.search(r'\d+\.\d+', currency_string)
    if match:
        return float(match.group())
    else:
        return None  # Handle invalid currency strings
    
def generate_school_expense_coverage_html(data):
    html = """  
    <button id='school-expense-coverage-button' type='button' class='collapsible' onclick='toggleCollapsible("school-expense-coverage-button", "school-expense-coverage-content")'>School Expense Coverage</button>
    <div id='school-expense-coverage-content' class='content'>
        <div class='table-container'>
            <table>
                <tr><th>Year</th><th>Covered</th><th>Remaining Surplus</th><th>Deficit</th></tr>
    """

    for row in data:
        html += f"<tr><td>{row['year']}</td><td>{'Yes' if row['covered'] else 'No'}</td><td>${row['remaining_surplus']:,}</td><td>${row['deficit']:,}</td></tr>"

    html += """
            </table>
        </div>
    </div>
    """

    return html


def generate_current_house_html(current_house):
    """Generates HTML content for the current house section with collapsible functionality,
    formatting specific fields differently as needed.

    Args:
        current_house (object): An object representing the current house.

    Returns:
        str: The generated HTML content.
    """

    if not current_house:
        # Return a message or an empty table if no data is provided
        logging.info("current house info NOT found")
        return "<p>No current_house data available.</p>"
    logging.info("current house info found")

    # Define fields that should be treated as plain numbers
    plain_number_fields = ["number_of_payments", "payments_made"]

    html_content = f"""
    <button id='current-house-button' class='collapsible' onclick='toggleCollapsible("current-house-button", "current-house-content")'>
        Current House
    </button>
    <div id='current-house-content' class='content'>
        <div class='table-container'>
            <table>
                <tr><th>Attribute</th><th>Value</th></tr>
    """

    for attr, value in current_house.__dict__.items():
        formatted_attr = format_key(attr)

        if isinstance(value, (float, int)):
            # Check if the attribute should be treated as a plain number
            if attr.lower() in plain_number_fields:
                formatted_value = str(value)  # Leave the number as-is
            # Check for decimal interest rate (0 to 1)
            elif 0 <= value <= 1:
                formatted_value = f"{value:.2%}"  # Convert to percentage
            else:
                # Check for currency format
                if re.search(r"^\$[\d,.]+$", str(value)):
                    formatted_value = str(value)  # Keep currency format
                else:
                    formatted_value = "${:,.2f}".format(value)  # Format other numbers as currency
        elif isinstance(value, str) and "%" in value:
            formatted_value = value  # Keep percentage format with existing symbol
        else:
            formatted_value = str(value)
        if isinstance(value, bool):
            formatted_value = "Yes" if value else "No"

        html_content += f"<tr><td>{formatted_attr}</td><td>{formatted_value}</td></tr>"

    html_content += """
            </table>
        </div>
    </div>
    """

    return html_content

def generate_new_house_html(new_house):
    """Generates HTML content for the new house section with collapsible functionality,
    formatting specific fields differently as needed.

    Args:
        new_house (object): An object representing the new house.

    Returns:
        str: The generated HTML content.
    """

    if not new_house:
        # Return a message or an empty table if no data is provided
        logging.info("new house info NOT found")
        return "<div class='collapsible'><p>New house not part of scenario.</p></div>"
    logging.info("new house info found")

    # Define fields that should be treated as plain numbers
    plain_number_fields = ["number_of_payments", "payments_made"]

    html_content = f"""
    <button id='new-house-button' class='collapsible' onclick='toggleCollapsible("new-house-button", "new-house-content")'>
        New House
    </button>
    <div id='new-house-content' class='content' '>
        <div class='table-container'>
            <table>
                <tr><th>Attribute</th><th>Value</th></tr>
    """

    for attr, value in new_house.__dict__.items():
        formatted_attr = format_key(attr)

        if isinstance(value, (float, int)):
            # Check if the attribute should be treated as a plain number
            if attr.lower() in plain_number_fields:
                formatted_value = str(value)  # Leave the number as-is
            # Check for decimal interest rate (0 to 1)
            elif 0 <= value <= 1:
                formatted_value = f"{value:.2%}"  # Convert to percentage
            else:
                # Check for currency format
                if re.search(r"^\$[\d,.]+$", str(value)):
                    formatted_value = str(value)  # Keep currency format
                else:
                    formatted_value = "${:,.2f}".format(value)  # Format other numbers as currency
        elif isinstance(value, str) and "%" in value:
            formatted_value = value  # Keep percentage format with existing symbol
        else:
            formatted_value = str(value)
        if isinstance(value, bool):
            formatted_value = "Yes" if value else "No"

        html_content += f"<tr><td>{formatted_attr}</td><td>{formatted_value}</td></tr>"

    html_content += """
            </table>
        </div>
    </div>
    """

    return html_content

def generate_future_value_html_table(report_data):
    """Generates HTML content for the future value section of the financial report."""
    years = report_data["config_data"]["years"]
    new_house = report_data["house_info"]["new_house"]
    new_house_value = report_data["house_info"]["new_house_value"]
    house_networth_future = report_data["house_info"]["house_networth_future"]
    total_employee_stockplan = report_data["calculated_data"]["total_employee_stockplan"]
    balance_with_expenses = report_data["calculated_data"]["balance_with_expenses"]
    house_capital_investment = report_data["house_info"]["house_capital_investment"]
    future_retirement_value_contrib = report_data["calculated_data"]["future_retirement_value_contrib"]
    combined_networth_future = report_data["calculated_data"]["combined_networth_future"]
    config_data = report_data["config_data"]

    interest_rate = report_data["config_data"]["interest_rate"]
    interest_rate_percentage = f"{interest_rate:.2%}"
    annual_growth_rate = config_data.get("house", {}).get("annual_growth_rate")
    annual_growth_rate_percentage = f"{annual_growth_rate:.2%}"
  
    # Calculate total retirement assets
    total_retirement_assets = future_retirement_value_contrib + balance_with_expenses + total_employee_stockplan

    # Calculate safe withdrawal amount
    safe_withdrawal_amount = 0.04 * total_retirement_assets
    # Calculate future values
    oneyear_house_value = house_networth_future * (0.035) 
    oneyear_stock_value = total_retirement_assets * (interest_rate) 

    # Combined future value
    oneyear_growth = oneyear_house_value + oneyear_stock_value
    # seven_percent_networth = 0.07 * combined_networth_future

    # HTML table rows
    rows = [
        generate_net_worth_row(
            "House Net Worth",
            new_house_value if new_house else house_networth_future,
        ),
        generate_net_worth_row(
            "House Re-Investment",
            house_capital_investment,
            f"This represents the capital that will be reinvested following the sale of the house, reflecting its value after {years} years of anticipated growth."
        ),
        generate_net_worth_row(
            "Stock Plan Investment Balance",
            total_employee_stockplan,
        ),
        generate_net_worth_row(
            "Investment Balance",
            balance_with_expenses,
        ),
        generate_net_worth_row(
            "Retirement Balance",
            future_retirement_value_contrib,
        ),
        generate_net_worth_row(
            "Total Investment Assets",
            total_retirement_assets,
            "The total investment assets include the sum of your investment balance, retirement principal, and Stock Plan Investment."
        ),
        generate_net_worth_row(
            "Net Worth",
            combined_networth_future,
        ),
        generate_net_worth_row(
            "Projected One-Year Growth",
            oneyear_growth,
            f"A {interest_rate_percentage} return on net worth is often used as a hypothetical annual growth rate for investments in the stock market. <br>{annual_growth_rate_percentage} represents the growth of the house over time."
        ),
        generate_net_worth_row(
            "4% Safe Withdrawal Rate",
            safe_withdrawal_amount,
        ),
    ]

    # Combine all rows into the table
    html_content = f"""
    <div class='table-container'>
        <table>
            {''.join(rows)}
        </table>
    </div>
    """
    return html_content


def generate_tooltip(icon, tooltip_text):
    """Generates HTML for a tooltip."""
    return f"""
        <span class="tooltip">
            <span class="tooltip-icon" aria-label="Tooltip available" role="tooltip">ℹ️</span>
            <span class="tooltip-text">{tooltip_text}</span>
        </span>
    """

def generate_net_worth_row(label, value, tooltip_text=None):
    """Generates a row for the net worth table."""
    tooltip_html = generate_tooltip("ℹ️", tooltip_text) if tooltip_text else ""
    return f"""
        <tr>
            <th>{label}</th>
            <td>
                <div class="net-worth-field">
                    <span class="net-worth">{format_currency(value)}</span>
                    {tooltip_html}
                </div>
            </td>
        </tr>
    """

def generate_current_networth_html_table(report_data, invest_capital_from_house_sale, sale_of_house_investment, investment_projected_growth):
    """
    Generate HTML content for the current net worth section of the financial report.
    """
    house_info = report_data["house_info"]
    config_data = report_data["config_data"]
    years = config_data["years"]
    calculated_data = report_data["calculated_data"]
    interest_rate = config_data["interest_rate"]
    
    interest_rate_percentage = f"{interest_rate:.2%}"
    annual_growth_rate = config_data.get("house", {}).get("annual_growth_rate")
    annual_growth_rate_percentage = f"{annual_growth_rate:.2%}"

    investment_balance = config_data.get('investment_balance', 0)
    retirement_principal = config_data.get('retirement_principal', 0)
    combined_networth = calculated_data.get("combined_networth", 0)
    house_net_worth = house_info.get("house_net_worth", 0)
    total_retirement_assets = invest_capital_from_house_sale + investment_balance + retirement_principal

    safe_withdrawal_amount = 0.04 * total_retirement_assets
    # seven_percent_networth = 0.07 * combined_networth

    # Calculate future values
    oneyear_house_value = house_net_worth * annual_growth_rate 
    oneyear_stock_value = total_retirement_assets * (interest_rate) 

    # Combined future value
    oneyear_growth = oneyear_house_value + oneyear_stock_value

    # HTML table rows
    rows = [
        generate_net_worth_row(
            "House Net Worth",
            house_net_worth,
            "Calculated by (House Value - Remaining Mortgage Principal)"
        ),
        generate_net_worth_row(
            "House Re-Investment",
            invest_capital_from_house_sale,
            f"This is the capital that will be reinvested after the house is sold.<br>Projected Future Value: {format_currency(sale_of_house_investment)}"
        ),
        generate_net_worth_row(
            "Investment Balance",
            investment_balance,
            f"Projected value if not used to cover expenses.<br>Projected Future Value: {format_currency(investment_projected_growth)}"
        ),
        generate_net_worth_row("Retirement Balance", retirement_principal),
        generate_net_worth_row("Net Worth", combined_networth),
        generate_net_worth_row(
            "Total Investment Assets",
            total_retirement_assets,
            "The total investment assets include the sum of your investment balance, retirement principal, and any capital reinvested from the house sale. House net worth is not included."
        ),
        generate_net_worth_row(
            "Projected One-Year Growth",
            oneyear_growth,
            f"A {interest_rate_percentage} return on net worth is often used as a hypothetical annual growth rate for investments in the stock market. <br>{annual_growth_rate_percentage} represents the growth of the house over time."
        ),
        generate_net_worth_row(
            "4% Safe Withdrawal Rate",
            safe_withdrawal_amount,
            "The 4% rule suggests that you can safely withdraw 4% of your total retirement savings annually without running out of money over a 30-year retirement period.<br>This amount adjusts for inflation each year."
        )
    ]

    # Combine all rows into the table
    html_content = f"""
    <div class='table-container'>
        <table>
            {''.join(rows)}
        </table>
    </div>
    """
    return html_content


def generate_income_expenses_html(section_title, calculated_data):
    """
    Converts the calculated income and expenses data into an HTML table with collapsible functionality.

    Args:
        calculated_data (dict): The dictionary containing the income and expense data.

    Returns:
        str: The generated HTML content as a collapsible table.
    """

    html_content = f"""
    <button id='income-expenses-button' type='button' class='collapsible' onclick='toggleCollapsible("income-expenses-button", "income-expenses-content")'>
        {section_title}
    </button>
    <div id='income-expenses-content' class='content'>
        <div class='table-container'>
            <table class='income-expenses-table'>
                <thead>
                    <tr><th>Category</th><th>Value</th></tr>
                </thead>
                <tbody>
    """

    # Iterate over the calculated data dictionary
    for key, value in calculated_data.items():
        formatted_key = format_key(key)  # Format the key for readability

        # If the value is a dictionary (like monthly_expenses_breakdown), convert it into nested tables
        if isinstance(value, dict):
            nested_table = "<table><thead><tr><th>Subcategory</th><th>Value</th></tr></thead><tbody>"
            for sub_key, sub_value in value.items():
                nested_table += f"<tr><td>{format_key(sub_key)}</td><td>{format_value(sub_value)}</td></tr>"
            nested_table += "</tbody></table>"

            html_content += f"<tr><td>{formatted_key}</td><td>{nested_table}</td></tr>"
        
        # If the value is a list (like yearly_data), generate rows for each item
        elif isinstance(value, list):
            html_content += f"<tr><td>{formatted_key}</td><td>"
            html_content += "<ul>"
            for item in value:
                html_content += f"<li>{format_value(item)}</li>"
            html_content += "</ul></td></tr>"

        # For scalar values (int, float, str), directly add the row
        else:
            html_content += f"<tr><td>{formatted_key}</td><td>{format_value(value)}</td></tr>"

    html_content += """
                </tbody>
            </table>
        </div>
    </div>
    """

    return html_content

def generate_configuration_data_html(section_title, configuration_data):
    """
    Converts the calculated income and expenses data into an HTML table with collapsible functionality.

    Args:
        configuration_data (dict): The dictionary containing the json configuration.

    Returns:
        str: The generated HTML content as a collapsible table.
    """

    html_content = f"""
    <button id='calculated-data-button' type='button' class='collapsible' onclick='toggleCollapsible("calculated-data-button", "calculated-data-content")'>
        {section_title}
    </button>
    <div id='calculated-data-content' class='content'>
        <div class='table-container'>
            <table class='calculated-data-table'>
                <thead>
                    <tr><th>Category</th><th>Value</th></tr>
                </thead>
                <tbody>
    """

    # Iterate over the calculated data dictionary
    for key, value in configuration_data.items():
        formatted_key = format_key(key)  # Format the key for readability

        # If the value is a dictionary (like monthly_expenses_breakdown), convert it into nested tables
        if isinstance(value, dict):
            nested_table = "<table><thead><tr><th>Subcategory</th><th>Value</th></tr></thead><tbody>"
            for sub_key, sub_value in value.items():
                nested_table += f"<tr><td>{format_key(sub_key)}</td><td>{format_value(sub_value)}</td></tr>"
            nested_table += "</tbody></table>"

            html_content += f"<tr><td>{formatted_key}</td><td>{nested_table}</td></tr>"
        
        # If the value is a list (like yearly_data), generate rows for each item
        elif isinstance(value, list):
            html_content += f"<tr><td>{formatted_key}</td><td>"
            html_content += "<ul>"
            for item in value:
                html_content += f"<li>{format_value(item)}</li>"
            html_content += "</ul></td></tr>"

        # For scalar values (int, float, str), directly add the row
        else:
            html_content += f"<tr><td>{formatted_key}</td><td>{format_value(value)}</td></tr>"

    html_content += """
                </tbody>
            </table>
        </div>
    </div>
    """

    return html_content

def format_key(key):
    """
    Formats a key for better readability in the HTML table.
    Example: Converts 'yearly_income_deficit' to 'Yearly Income Deficit'.
    """
    return key.replace('_', ' ').capitalize()

def format_keydetailed(key):
    import re
    # Convert camel case or underscore-separated words to space-separated words
    formatted_key = re.sub(r'(?<!^)(?=[A-Z][a-z])|_', ' ', key)
    # Capitalize the first letter of each word
    formatted_key = ' '.join(word.capitalize() for word in formatted_key.split())
    return formatted_key

def format_value(value):
    """
    Formats a value for display in the HTML table.
    """
    if isinstance(value, (int, float)):
        # Format numbers with commas
        return f"{value:,.3f}" if isinstance(value, float) else f"{value:,}"
    else:
        # Return the string representation for other types
        return str(value)


def generate_current_networth_html(report_data):
    """
    Generate HTML content for the current net worth section of the financial report.

    Args:
    - report_data (dict): Dictionary containing all necessary data for calculating the current net worth section.

    Returns:
    str: HTML content for the current net worth section.
    """
    house_info = report_data["house_info"]
    config_data = report_data["config_data"]
    calculated_data = report_data["calculated_data"]

    html_content = f"""  
    <button id='current-net-worth-button' type='button' class='collapsible' onclick='toggleCollapsible("current-net-worth-button", "current-net-worth-content" )'>Current Net Worth</button>
    <div id='current-net-worth-content' class='content'>
        <div class='table-container'>
            <table>
                <tr><th>House Net worth</th><td>{format_currency(house_info.get("house_net_worth", 0))}</td></tr>
                <tr><th>Investment Balance</th><td>{format_currency(config_data.get('investment_balance', 0))}</td></tr>
                <tr><th>Retirement Balance</th><td>{format_currency(config_data.get('retirement_principal', 0))}</td></tr>
                <tr><th>Combined Net worth</th><td>{format_currency(calculated_data.get("combined_networth", 0))}</td></tr>
            </table>
        </div>
    </div>
    """
    return html_content

def safe_int_conversion(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return value  # or return 0, or any other default value

def generate_table_html(data, custom_formatter=None, headers=None):
    """Generates HTML for a table based on the provided data.

    Args:
        data (dict or object): The data to be displayed in the table.
        custom_formatter (function, optional): A custom function to format the values.
        headers (list, optional): A list of column headers to display at the top of the table.

    Returns:
        str: The generated HTML content for the table.
    """

    table_html = "          <div class='table-container'>\n            <table>\n"

    # Add table headers if provided
    if headers:
        table_html += "         <thead><tr>"
        for header in headers:
            table_html += f"<th>{header}</th>"
        table_html += "</tr></thead>\n"

    # Add table body with data
    table_html += "             <tbody>\n"
    if isinstance(data, dict):
        for key, value in data.items():
            formatted_value = custom_formatter(value) if custom_formatter and value is not None else value
            table_html += f"             <tr><th>{key}</th><td>{formatted_value}</td></tr>\n"
    elif hasattr(data, '__dict__'):
        for attr, value in data.__dict__.items():
            formatted_value = custom_formatter(value) if custom_formatter and value is not None else value
            table_html += f"             <tr><th>{attr}</th><td>{formatted_value}</td></tr>\n"
    table_html += "            </tbody>\n"

    table_html += "          </table>\n         </div>"
    return table_html


def generate_paragraph_html(data, custom_formatter=None):
    """
    Generates HTML for a paragraph, with optional custom formatting.

    Args:
        data (str): The content of the paragraph.
        custom_formatter (function, optional): A function to format the data.

    Returns:
        str: The generated HTML content for the paragraph.
    """
    # Apply custom formatting if provided
    if custom_formatter:
        data = custom_formatter(data)
    
    return f"<p>{data}</p>"


def generate_section_html(section_title, data, custom_formatter=None, headers=None, collapsible=False):
    """Generates HTML content for a section, handling different data types with optional collapsibility.

    Args:
        section_title (str or None): The title of the section, or None if no title is needed.
        data: The data to be displayed in the section.
        custom_formatter (function, optional): A custom function to format the values.
        headers (list, optional): A list of column headers to display at the top of the table.
        collapsible (bool, optional): Whether the section should be collapsible.

    Returns:
        str: The generated HTML content.
    """
    if not data:
        # Return a message or an empty table if no data is provided
        logging.info("No data available passed to function")
        return "<p>No data available.</p>"
    
    html_content = ""

    # Generate a unique ID for the collapsible section
    section_id = section_title.replace(" ", "-").lower() if section_title else "section"
    button_id = f"{section_id}-button"
    content_id = f"{section_id}-content"

    logging.info(f"{section_id}, {button_id}, {content_id}") 
    # Add collapsibility button if required
    if collapsible:
        html_content += f"""
            <button id="{button_id}" class="collapsible" onclick="toggleCollapsible('{button_id}', '{content_id}')">{section_title}</button>
            <div id="{content_id}" class="content">
        """
    else:
        # Standard section title without collapsibility
        if section_title:
            html_content += f"<h3>{section_title}</h3>\n"

    # Check if data is dict or object and pass headers if provided
    if isinstance(data, dict) or hasattr(data, '__dict__'):
        try:
            html_content += generate_table_html(data, custom_formatter, headers)
        except Exception as e:
            logging.error(f"Error generating table: {e}")
            html_content += "<p>Error generating table content.</p>"
    else:
        html_content += generate_paragraph_html(data, custom_formatter)

    # Close the collapsible content div if collapsibility is enabled
    if collapsible:
        html_content += "</div>"

    return html_content

def generate_house_section_html(section_title, data, custom_formatter=None, headers=None, collapsible=False):
    """Generates HTML content for a section, handling different data types with optional collapsibility.

    Args:
        section_title (str or None): The title of the section, or None if no title is needed.
        data: The data to be displayed in the section.
        custom_formatter (function, optional): A custom function to format the values.
        headers (list, optional): A list of column headers to display at the top of the table.
        collapsible (bool, optional): Whether the section should be collapsible.

    Returns:
        str: The generated HTML content.
    """
    if not data:
        # Return a message or an empty table if no data is provided
        logging.info("No data available passed to function")
        return "<p>No data available.</p>"
    
    html_content = ""

    # Generate a unique ID for the collapsible section
    section_id = section_title.replace(" ", "-").lower() if section_title else "section"
    button_id = f"{section_id}-button"
    content_id = f"{section_id}-content"

    logging.info(f"{section_id}, {button_id}, {content_id}") 
    # Add collapsibility button if required
    if collapsible:
        html_content += f"""
            <button id="{button_id}" class="collapsible" onclick="toggleCollapsible('{button_id}', '{content_id}')">{section_title}</button>
            <div id="{content_id}" class="content">
        """
    else:
        # Standard section title without collapsibility
        if section_title:
            html_content += f"<h3>{section_title}</h3>"

    # Check if data is dict or object and pass headers if provided
    if isinstance(data, dict) or hasattr(data, '__dict__'):
        try:
            html_content += generate_table_html(data, custom_formatter=None, headers=headers)
        except Exception as e:
            logging.error(f"Error generating table: {e}")
            html_content += "<p>Error generating table content.</p>"
    else:
        html_content += generate_paragraph_html(data, custom_formatter)

    # Close the collapsible content div if collapsibility is enabled
    if collapsible:
        html_content += "</div>"

    return html_content

def generate_html(report_data):
    excluded_sections = ["current_house", "school_expense_coverage", "Yearly Income", "house_info"]

    def format_data(data):
        formatted_data = ""
        if isinstance(data, dict):
            formatted_data += "<ul>"
            for key, value in data.items():
                if key not in excluded_sections:
                    formatted_key = format_key(key)
                    formatted_data += f"<li><strong>{escape(formatted_key)}:</strong> <span class='{key}-data'>{safe_int_conversion(format_data(value))}</span></li>"
            formatted_data += "</ul>"
        elif isinstance(data, list):
            formatted_data += "<ul>"
            for item in data:
                formatted_data += f"<li>{escape(str(item))}</li>"
            formatted_data += "</ul>"
        else:
            formatted_data += f"{safe_int_conversion(data)}"
        return formatted_data

    investment_principal = report_data["calculated_data"].get("balance_with_expenses", 0)
    house_capital_investment = report_data["house_info"].get("house_capital_investment", 0)

    # Ensure both are floats or ints and handle None cases if necessary
    if investment_principal is None:
        investment_principal = 0
    if house_capital_investment is None:
        house_capital_investment = 0

    # Conditional check for viability
    viable_status = "Viable" if (investment_principal + house_capital_investment) > 50000 else "Not Viable"

    # Generate the scenario filename (make sure to format the name correctly)
    scenario_full_name = report_data["calculated_data"].get("scenario_name", "index")
    scenario_filename = f"scenario_{scenario_full_name}.html"

    # Debugging the final result
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Financial Report</title>
        <link rel="stylesheet" href="../static/css/styles.css">
        <script src="../static/js/toggleVisibility.js"></script>
    </head>
    <body>
        <h1>Financial Report</h1>
        <div class='header-container'>
            <div class='header'>
                <h2 id='detail-title'>Detail</h2>
                <div id='content' class='section-content'>
                    <p><strong>Status:</strong> {viable_status}</p>
                    <p><a href="{scenario_filename}">View Full Scenario</a></p>
    """
    
    future_value_html = generate_future_value_html_table(report_data)
    formatted_future_title = format_key("Future Value")
    html_content += f"<button type='button' class='collapsible' onclick='toggleCollapsible(\"future-value\", \"future-value-content\")'>{escape(formatted_future_title)}</button>"
    html_content += f"<div id='future-value-content' class='content'>{future_value_html}</div>"

    annual_income_surplus_html = generate_section_html("Annual Income Surplus", report_data["calculated_data"]["annual_surplus"], format_currency)
    annual_income_surplus_title = format_key("Annual Income Surplus")
    html_content += f"<button type='button' class='collapsible' onclick='toggleCollapsible(\"annual_income_surplus\", \"annual_income_surplus-content\")'>{escape(annual_income_surplus_title)}</button>"
    html_content += f"<div id='annual_income_surplus-content' class='content'>{annual_income_surplus_html}</div>"

    html_content += generate_configuration_data_html("Configuration Data", report_data['config_data'])
    html_content += generate_income_expenses_html("Income and Expenses", report_data['calculated_data'])
    html_content += generate_current_networth_html(report_data)

    school_expense_coverage_html = generate_school_expense_coverage_html(report_data["calculated_data"]["school_expense_coverage"])
    html_content += school_expense_coverage_html

    headers = ["Attribute", "Value"]
    logging.info("Generate house info HTML")
    
    if "house_info" in report_data:
        house_info_html = generate_house_section_html(
            None,
            report_data["house_info"],
            custom_formatter=None,
            headers=headers
        )
    else:
        logging.info('"house_info" is NOT in report_data')
        house_info_html = "<p>No house information available.</p>"

    formatted_house_info_title = format_key("House Info")
    html_content += f"<button type='button' class='collapsible' onclick='toggleCollapsible(\"house-info\", \"house-info-content\")'>{formatted_house_info_title}</button>"
    html_content += f"<div id='house-info-content' class='content'>{house_info_html}</div>"

    current_house_html = generate_current_house_html(report_data["current_house"])
    html_content += current_house_html

    if "new_house" in report_data:
       logging.info('new_house FOUND in report_data')
       new_house_html = generate_new_house_html(report_data["new_house"])
       html_content += new_house_html
    else:
        logging.info('new_house is NOT in report_data')
        html_content += "<p>new_house is NOT available.</p>"
    
    html_content += """
                    </div>
            </div>
            </div> <!-- End of header-container -->
    </body>
    </html>
    """
    return html_content


def _generate_html(report_data):
    excluded_sections = ["current_house", "school_expense_coverage", "Yearly Income", "house_info"]

    def format_data(data):
        formatted_data = ""
        if isinstance(data, dict):
            formatted_data += "<ul>"
            for key, value in data.items():
                if key not in excluded_sections:
                    formatted_key = format_key(key)
                    formatted_data += f"<li><strong>{escape(formatted_key)}:</strong> <span class='{key}-data'>{safe_int_conversion(format_data(value))}</span></li>"
            formatted_data += "</ul>"
        elif isinstance(data, list):
            formatted_data += "<ul>"
            for item in data:
                formatted_data += f"<li>{escape(str(item))}</li>"
            formatted_data += "</ul>"
        else:
            formatted_data += f"{safe_int_conversion(data)}"
        return formatted_data
 
    investment_principal = report_data["calculated_data"].get("balance_with_expenses", 0)
    house_capital_investment = report_data["house_info"].get("house_capital_investment", 0)


    # Ensure both are floats or ints and handle None cases if necessary
    if investment_principal is None:
        investment_principal = 0
    if house_capital_investment is None:
        house_capital_investment = 0


    # Conditional check for viability
    viable_status = "Viable" if (investment_principal + house_capital_investment) > 50000 else "Not Viable"

    # Debugging the final result

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Financial Report</title>
        <link rel="stylesheet" href="../static/css/styles.css">
        <script src="../static/js/toggleVisibility.js"></script>
    </head>
    <body>
        <h1>Financial Report</h1>
        <div class='header-container'>
    """
    html_content += """
        <div class='header'>
        <h2 id='detail-title'>Detail</h2>
        <div id='content' class='section-content'>
    """
    future_value_html = generate_future_value_html_table(report_data)
    formatted_future_title = format_key("Future Value")
    html_content += f"<button type='button' class='collapsible' onclick='toggleCollapsible(\"future-value\", \"future-value-content\")'>{escape(formatted_future_title)}</button>"
    html_content += f"<div id='future-value-content' class='content'>{future_value_html}</div>"

    annual_income_surplus_html = generate_section_html("Annual Income Surplus", report_data["calculated_data"]["annual_surplus"], format_currency)
    annual_income_surplus_title = format_key("Annual Income Surplus")
    html_content += f"<button type='button' class='collapsible' onclick='toggleCollapsible(\"annual_income_surplus\", \"annual_income_surplus-content\")'>{escape(annual_income_surplus_title)}</button>"
    html_content += f"<div id='annual_income_surplus-content' class='content'>{annual_income_surplus_html}</div>"

    html_content += generate_configuration_data_html("Configuration Data", report_data['config_data'])
    html_content += generate_income_expenses_html("Income and Expenses", report_data['calculated_data'])
    html_content += generate_current_networth_html(report_data)

    school_expense_coverage_html = generate_school_expense_coverage_html(report_data["calculated_data"]["school_expense_coverage"])
    html_content += school_expense_coverage_html

    headers = ["Attribute", "Value"]
    logging.info("Generate house info HTML")
    
    if "house_info" in report_data:
        house_info_html = generate_house_section_html(
            None,
            report_data["house_info"],
            custom_formatter=None,
            headers=headers
        )
    else:
        logging.info('"house_info" is NOT in report_data')
        house_info_html = "<p>No house information available.</p>"

    formatted_house_info_title = format_key("House Info")
    html_content += f"<button type='button' class='collapsible' onclick='toggleCollapsible(\"house-info\", \"house-info-content\")'>{formatted_house_info_title}</button>"
    html_content += f"<div id='house-info-content' class='content'>{house_info_html}</div>"

    current_house_html = generate_current_house_html(report_data["current_house"])
    html_content += current_house_html

    if "new_house" in report_data:
       logging.info('new_house FOUND in report_data')
       new_house_html = generate_new_house_html(report_data["new_house"])
       html_content += new_house_html
    else:
        logging.info('new_house is NOT in report_data')
        html_content += "<p>new_house is NOT available.</p>"
    
    html_content += """
                    </div>
            </div>
            </div> <!-- End of header-container -->
    </body>
    </html>
    """
    return html_content

def generate_summary_report_html(summary_report_data):
    """
    Generates an HTML report for financial scenario summaries.

    Args:
        summary_report_data (dict): Dictionary containing the scenario data.

    Returns:
        str: HTML content as a string.
    """
    
    # HTML structure start
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Financial Scenario Summary Report</title>
        <link rel="stylesheet" href="../static/css/styles.css">
        <script src="../static/js/toggleVisibility.js"></script>
    </head>
    <body class="print-columns">
      <h1>Financial Scenario Summary Report</h1>
      <div class='container'> <!-- Main container for layout with flexbox -->
        <!-- INSERT NAVIGATION HERE -->
    """
    
    # Function to create a scenario section
    def create_scenario_section(scenario_name, scenario_data):
        """Generates HTML for a single scenario section."""
        scenario_id = scenario_name.replace(" ", "-").lower()
        assumption_description = scenario_data.get("assumption_description", "")
        description_detail = scenario_data.get("description_detail", "")
        investment_principal = scenario_data.get("investment_principal", 0) or 0
        house_capital_investment = scenario_data.get("house_capital_investment", 0) or 0

        # Determine viability based on investment and house capital
        viable_status = (investment_principal + house_capital_investment) > 50000
        viability_class = "viable" if viable_status else "not-viable"
        viability_label = "Viable" if viable_status else "Not Viable"
        
        # Scenario section template with links to scenario and detail files
        return f"""
        <main class='main-content' id='{scenario_id}-main'>
          <div class='header'>
            <h2>{escape(assumption_description)}</h2>
            <h4 class="scenario-status {viability_class}">
              {viability_label}
            </h4>
          </div>
          <div class='section-content'>
            <div class='table-container'>
              <div>
                {scenario_data["scenario_summary_info"]}
                <p>{escape(description_detail)}</p>
              </div>
              <div>
                <h3>Current Value</h3>
                {scenario_data["current_value"]}
              </div>
              <div>
                <h3>Future Value</h3>
                {scenario_data["future_value"]}
              </div>
              <div>
                {scenario_data["yearly_net_html"]}
                {scenario_data["total_after_fees_html"]}
              </div>
            </div>
          </div>
        </main>
        """

    # Function to create detailed information section
    def create_detailed_info_section(scenario_name, scenario_data):
        """Generates HTML for detailed information section."""
        scenario_id = scenario_name.replace(" ", "-").lower()
        detail_filename = f"detail_{scenario_name}.html"
        return f"""
        <aside class='detailed-info' id='{scenario_id}-detail'>
            <h3>Detailed Information</h3>
            <div>{scenario_data["assumptions_html"]}</div>
            <div>{scenario_data["monthly_expenses_html"]}</div>
            <div>{scenario_data["expenses_not_factored_html"]}</div>
            <div>{scenario_data["school_expenses_table_html"]}</div>
            <div>{scenario_data["investment_table_html"]}</div>
            <div>{scenario_data["retirement_table_html"]}</div>
            <div>{scenario_data["current_house_html"]}</div>
            <div>{scenario_data["new_house_html"]}</div>
            <div>
                <a href="{detail_filename}">View Detailed Information</a>
            </div>
        </aside>
        """

    # Loop through each scenario to generate the HTML content
    for scenario_name, scenario_data in summary_report_data.items():
        html_content += "<div class='scenario-wrapper'>"  # Wrap scenario and detail together
        html_content += create_scenario_section(scenario_name, scenario_data)
        html_content += create_detailed_info_section(scenario_name, scenario_data)
        html_content += "</div>"  # End of wrapper

    # End the HTML structure
    html_content += """
        </div> <!-- End of container -->
    </body>
    </html>
    """
    
    return html_content


def generate_html_for_dict(data):
    html_content = "<table>"
    for key, value in data.items():
        if isinstance(value, dict):
            html_content += f"<tr><th colspan='2'>{escape(str(key))}</th></tr>"
            html_content += generate_html_for_dict(value)
        else:
            html_content += f"<tr><th>{escape(str(key))}</th><td>{escape(str(value))}</td></tr>"
    html_content += "</table>"
    return html_content

def generate_table_for_child(child_data, table_class="expense-table", headers=["School Type", "Year", "Cost"]):
    """Generates HTML table content for a child's educational expenses in a nested structure with collapsible sections.

    Args:
        child_data (dict): A dictionary containing child information.
        table_class (str, optional): The CSS class to apply to the table.
        headers (list, optional): A list of column headers for the table.

    Returns:
        str: The generated HTML table content.
    """
    if not child_data:
        # Return a message or an empty table if no data is provided
        return "<p>No chidlren school expenses data available.</p>"
    
    html_content = ""  # Initialize the HTML content

    for index, child in enumerate(child_data.get("children", [])):
        child_name = escape(child['name'])  # Get and escape the child's name
        child_id = f"childDetails-{index}"  # Create a unique ID for each child's details section

        # Add the child name as a collapsible button with toggle functionality
        html_content += f"""
            <button id="{child_id}-button" class="collapsible" onclick="toggleCollapsible('{child_id}-button', '{child_id}-content')">
                {child_name} School
            </button>
            <div id="{child_id}-content" class="content">
                <table class='{table_class}'>
                    <thead>
                        <tr><th>{escape(headers[0])}</th><th>{escape(headers[1])}</th><th>{escape(headers[2])}</th></tr>
                    </thead>
                    <tbody>
        """

        school_data = child.get("school", {})
        
        # Combine all entries across school types into one list
        combined_entries = []
        for school_type, entries in school_data.items():
            for entry in entries:
                combined_entries.append({
                    'school_type': school_type,
                    'year': int(entry['year']),
                    'cost': entry['cost']
                })

        # Sort entries by year
        sorted_entries = sorted(combined_entries, key=lambda entry: entry['year'])

        for entry in sorted_entries:
            year = escape(str(entry['year']))  # Convert back to string for HTML
            cost = format_currency(entry['cost'])  # Format cost for readability
            school_type = escape(entry['school_type'])
            html_content += f"<tr><td>{school_type}</td><td>{year}</td><td>{cost}</td></tr>\n"

        html_content += """
                    </tbody>
                </table>
            </div>  <!-- End of hidden details section -->
        """  # End of child section

    return html_content

def generate_investment_table(data, custom_formatter=None):
    """Generates HTML for a table based on the provided data.

    Args:
        data (dict or object): The data to be displayed in the table.
        custom_formatter (function, optional): A custom function to format the values.

    Returns:
        str: The generated HTML content for the table.
    """
    
    if not data:
        # Return a message or an empty table if no data is provided
        return "<p>No investment data available.</p>"

    html_content = ""
    html_content += f"""
        <button id="investment-button" class="collapsible" onclick="toggleCollapsible('investment-button', 'investment-content')">Investment Breakdown</button>
        <div id="investment-content" class="content">
            <table>
    """

    total = 0
    if isinstance(data, dict):
        for key, value in data.items():
            formatted_value = custom_formatter(value) if custom_formatter else value
            total += value  # Accumulate the total
            html_content += f"<tr><th>{key}</th><td>{formatted_value}</td></tr>"
    elif hasattr(data, '__dict__'):
        for attr, value in data.__dict__.items():
            formatted_value = custom_formatter(value) if custom_formatter else value
            total += value  # Accumulate the total
            html_content += f"<tr><th>{attr}</th><td>{formatted_value}</td></tr>"

    # Add the total row
    html_content += f"<tr><th>Total</th><td>{custom_formatter(total) if custom_formatter else total}</td></tr>"

    html_content += "</table></div>"
    return html_content


def generate_retirement_table(config_data, table_class="retirement-table"):
    """Generates HTML table content for retirement contributions and accounts with toggle functionality for each spouse.

    Args:
        config_data (dict): A dictionary containing retirement data for each person.
        table_class (str, optional): The CSS class to apply to the table.

    Returns:
        str: The generated HTML table content.
    """
    if not config_data:
        # Return a message or an empty table if no data is provided
        return "<p>No No Retirement data available.</p>"

    html_content = ""  # Initialize the HTML content
    grand_total_balance = 0  # Initialize grand total for all parents
    
    retirement_data = config_data.get("RETIREMENT", [])  # Extract the "RETIREMENT" list

    # Calculate grand total balance for all parents first
    for parent in retirement_data:
        accounts_data = parent.get("accounts", {})
        for account_type, entries in accounts_data.items():
            for entry in entries:
                for account_name, balance in entry.items():
                    grand_total_balance += balance  # Add to grand total balance

    # Add collapsible section for grand total balance at the top
    formatted_grand_total_balance = "{:,.2f}".format(grand_total_balance)
    html_content += f"""
        <button id="grandTotal-button" class="collapsible" onclick="toggleCollapsible('grandTotal-button', 'grandTotal-content')">Total Retirement Balance</button>
        <div id="grandTotal-content" class="content">
            <table class='{table_class}'>
                <tbody>
                    <tr>
                        <th>Total Retirement Balance</th>
                        <td>{formatted_grand_total_balance}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    """

    # Iterate through each parent in the retirement data
    for index, parent in enumerate(retirement_data):
        parent_name = parent.get("name", "Unknown Parent")  # Get parent's name or default
        parent_id = f"parentDetails-{index}"  # Unique ID for each parent's details section

        # Add collapsible section for each parent's details
        html_content += f"""
            <button id="{parent_id}-button" class="collapsible" onclick="toggleCollapsible('{parent_id}-button', '{parent_id}-content')">{escape(parent_name)} Retirement</button>
            <div id="{parent_id}-content" class="content">
                <h3>Contributions</h3>
                <table class='{table_class}'>
                    <thead>
                        <tr><th>Type</th><th>Contribution</th><th>Amount</th></tr>
                    </thead>
                    <tbody>
        """

        # Initialize totals
        total_contributions = 0
        total_accounts_balance = 0

        # Generate table for contributions
        contributions_data = parent.get("contributions", {})
        for contribution_type, entries in contributions_data.items():
            for entry in entries:
                for contribution, amount in entry.items():
                    stripped_contribution = contribution.replace("spouse1_", "").replace("spouse2_", "").replace("retirement_", "").replace("contribution_", "").replace("_", " ").title()
                    formatted_amount = "{:,.2f}".format(amount)  # Format amount with commas
                    html_content += f"<tr><td>{escape(contribution_type)}</td><td>{escape(stripped_contribution)}</td><td>{formatted_amount}</td></tr>\n"
                    total_contributions += amount  # Add to total contributions

        # Display total contributions
        formatted_total_contributions = "{:,.2f}".format(total_contributions)
        html_content += f"<tr><td colspan='2'><strong>Total Contributions</strong></td><td><strong>{formatted_total_contributions}</strong></td></tr>\n"
        html_content += "</tbody>\n</table>\n"  # End of contributions table

        # Generate table for accounts
        html_content += f"""
                <h3>Accounts</h3>
                <table class='{table_class}'>
                    <thead>
                        <tr><th>Type</th><th>Account Name</th><th>Balance</th></tr>
                    </thead>
                    <tbody>
        """

        accounts_data = parent.get("accounts", {})
        for account_type, entries in accounts_data.items():
            for entry in entries:
                for account_name, balance in entry.items():
                    formatted_balance = "{:,.2f}".format(balance)  # Format balance with commas
                    html_content += f"<tr><td>{escape(account_type)}</td><td>{escape(account_name)}</td><td>{formatted_balance}</td></tr>\n"
                    total_accounts_balance += balance  # Add to total accounts balance

        # Display total account balances
        formatted_total_accounts = "{:,.2f}".format(total_accounts_balance)
        html_content += f"<tr><td colspan='2'><strong>Total Account Balances</strong></td><td><strong>{formatted_total_accounts}</strong></td></tr>\n"
        html_content += "</tbody>\n</table>\n"  # End of accounts table

        html_content += "</div>  <!-- End of hidden details section -->\n"  # End of parent section

    return html_content

def generate_friendly_name(scenario_file):
    """Generate a user-friendly name for the scenario file."""
    parts = scenario_file.replace('.html', '').split('_')
    
    # Example of creating a friendly name
    location = parts[0].replace('sf', 'San Francisco').replace('mn', 'Minnesota').capitalize()
    names = ' & '.join(part.capitalize() for part in parts[1:3])  # Example: "Hav & Jason"
    work_status = parts[2].replace('-', ' ').capitalize()  # "Retired Work", etc.
    ownership = parts[3].replace('public', 'Public').replace('own', 'Own').replace('private', 'Private').capitalize()

    # Create a user-friendly description
    friendly_name = f"{names} in {location}, {work_status} ({ownership})"
    return friendly_name


# Helper function to check the viability status
def check_viability_status(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    status_element = soup.find('h4', class_='scenario-status')

    # Check if status_element is found
    if status_element is None:
        logging.warning("Status element not found. Returning 'unknown'.")
        return 'unknown'

    # Ensure status_element is a Tag and not a NavigableString or other type
    if isinstance(status_element, Tag):
        class_list = status_element.get('class', [])
        
        # Ensure class_list is a list before performing 'in' checks
        if isinstance(class_list, list):
            return 'viable' if 'viable' in class_list else 'not-viable' if 'not-viable' in class_list else 'unknown'
        else:
            logging.warning(f"Unexpected class attribute type: {type(class_list)}. Returning 'unknown'.")
    else:
        logging.warning(f"Unexpected element type: {type(status_element)}. Returning 'unknown'.")

    logging.warning("No recognized status class found. Returning 'unknown'.")
    return 'unknown'

# Define dictionaries for name and work status lookups
name_lookup = {
    'hav': 'Havilah',
    'jason': 'Jason',
}

work_status_lookup = {
    'retired': 'Retired',
    'work': 'Working',
    'work-retired': 'Working & Retired',
    'retired-retired': 'Retired',
    'work-work': 'Working',
    'retired-work': 'Retired & Working',
}

# Mapping for location names
location_lookup = {
    'mn': 'Minnesota',
    'sf': 'San Francisco',
}

ownership_type_lookup = {
    'own': 'Own House',
    'rent': 'Rent',
}

school_type_lookup = {
    'public': 'Public HS',
    'private': 'Private HS',
    'pripub': 'Public-Private HS',
}

def extract_attributes_from_filename(filename, lookup):
    # Remove the extension
    name_parts = filename[:-5].split('_')

    # Check that we have enough parts
    if len(name_parts) < 5:
        raise ValueError("Filename does not have enough parts to unpack.")

    # Extract relevant parts
    location = name_parts[1]  # 'mn' or 'sf'
    names = name_parts[2:4]  # ['hav', 'jason']
    work_status = name_parts[4]  # 'work-retired'
    
    # Adjust ownership_type and school_type, while capturing extra content if available
    ownership_type = name_parts[5] if len(name_parts) > 5 else ""
    school_type = name_parts[6] if len(name_parts) > 6 else ""  # 'public' or similar

    # Capture any additional content beyond school type
    extra_content = "_".join(name_parts[7:]) if len(name_parts) > 7 else ""  # Join any extra parts into a single string

    # Generate full names using the lookup
    full_names = [lookup['name_lookup'].get(name, name).title() for name in names]
    
    friendly_ownership = lookup['ownership_type_lookup'].get(ownership_type, ownership_type.title())
    friendly_school = lookup['school_type_lookup'].get(school_type, school_type.title())
    
    # Include extra content in the report name if available
    report_name_suffix = f" ({extra_content})" if extra_content else ""
    
    # Combine for the simplified name
    simplified_name = f"{friendly_ownership} & {friendly_school}".strip()

    # Add the report name suffix to the simplified name if it exists
    if report_name_suffix:
        simplified_name += report_name_suffix

    return location, full_names, work_status, simplified_name, report_name_suffix


def process_html_file(file_path, config):
    """Process an HTML file to extract relevant attributes."""
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Extract attributes from the filename
    try:
        location, full_names, work_status, simplified_name, report_name_suffix = extract_attributes_from_filename(os.path.basename(file_path),config['lookup'])
        return html_content, location, full_names, work_status, simplified_name, report_name_suffix
    except ValueError as e:
        print(f"Skipping file {file_path}: {e}")
        return None

def generate_navigation(toc_content):
    """Generate structured navigation HTML with collapsible sections and dynamic parent names in work statuses."""
    html_content = "<nav class='site-navigation'>\n"
    
    # Add a div container for flexbox layout for buttons
    html_content += "<div class='nav-buttons'>\n"

    for viability in toc_content:
        formatted_viability = viability.replace('-', ' ').title()
        section_id = f"{viability}-content"
        button_id = f"{viability}-button"

        # Check if the current viability is "viable" to add the active class
        active_class = "active" if viability == "viable" else ""

        # Add collapsible button inside the nav-buttons div for flexbox layout
        html_content += f"<button id='{button_id}' type='button' class='collapsible nav-collapsible {active_class}' onclick='toggleCollapsible(\"{button_id}\", \"{section_id}\", true)'>{formatted_viability}</button>\n"
    
    # Close the div for buttons
    html_content += "</div>\n"

    # Now add the content sections that will be collapsible
    for viability in toc_content:
        section_id = f"{viability}-content"

        # Set the 'Viable' section to be visible by default
        if viability == "viable":
            html_content += f"<ul id='{section_id}' class='viability-list collapsible-content nav-collapsible-content' style='max-height:initial; overflow:hidden;'>\n"  # Make it visible
        else:
            html_content += f"<ul id='{section_id}' class='viability-list collapsible-content nav-collapsible-content' style='max-height:0; overflow:hidden;'>\n"  # Hidden by default

        for location, reports in toc_content[viability].items():
            # Adding class for location items
            html_content += f"  <li class='location-item'>{location_lookup.get(location, location).title()}\n"
            html_content += "    <ul class='work-status-list'>\n"  # Work status list with its class

            # Organize reports by work status
            work_status_dict = {}
            for file, simplified_name, full_names, work_status, report_name_suffix in reports:
                parent1_name, parent2_name = full_names  # Extract the parent names

                # Dynamically create the friendly status based on the work status
                if work_status == "retired-retired":
                    friendly_status = "Both Retired"
                elif work_status == "work-work":
                    friendly_status = "Both Working"
                elif work_status == "retired-work":
                    friendly_status = f"{parent1_name} Retired & {parent2_name} Working"
                elif work_status == "work-retired":
                    friendly_status = f"{parent1_name} Working & {parent2_name} Retired"
                else:
                    friendly_status = work_status  # Fallback if work status isn't found

                if friendly_status not in work_status_dict:
                    work_status_dict[friendly_status] = []
                work_status_dict[friendly_status].append((file, simplified_name))

            for friendly_status, items in work_status_dict.items():
                # Add work-status-item and report-list classes
                html_content += f"      <li class='work-status-item'>{friendly_status}<ul class='report-list'>\n"

                for file, simplified_name in items:
                    # Add report-item class to list item and maintain anchor for the report
                    html_content += f"        <li class='report-item'><a href='{file}'>{simplified_name}</a></li>\n"

                html_content += "      </ul></li>\n"  # Close work status item

            html_content += "    </ul>\n"  # Close work status list
            html_content += "  </li>\n"  # Close location item

        html_content += "</ul>\n"  # Close collapsible section

    html_content += "</nav>\n"
    return html_content



def _generate_navigation(toc_content):
    """Generate structured navigation HTML with collapsible sections."""
    html_content = "<nav class='site-navigation'>\n"
    
    # Add a div container for flexbox layout for buttons
    html_content += "<div class='nav-buttons'>\n"

    for viability in toc_content:
        formatted_viability = viability.replace('-', ' ').title()
        section_id = f"{viability}-content"
        button_id = f"{viability}-button"

        # Check if the current viability is "viable" to add the active class
        active_class = "active" if viability == "viable" else ""

        # Add collapsible button inside the nav-buttons div for flexbox layout
        html_content += f"<button id='{button_id}' type='button' class='collapsible nav-collapsible {active_class}' onclick='toggleCollapsible(\"{button_id}\", \"{section_id}\", true)'>{formatted_viability}</button>\n"
    
    # Close the div for buttons
    html_content += "</div>\n"

    # Now add the content sections that will be collapsible
    for viability in toc_content:
        section_id = f"{viability}-content"

        # Set the 'Viable' section to be visible by default
        if viability == "viable":
            html_content += f"<ul id='{section_id}' class='viability-list collapsible-content nav-collapsible-content' style='max-height:initial; overflow:hidden;'>\n"  # Make it visible
        else:
            html_content += f"<ul id='{section_id}' class='viability-list collapsible-content nav-collapsible-content' style='max-height:0; overflow:hidden;'>\n"  # Hidden by default

        for location, reports in toc_content[viability].items():
            # Adding class for location items
            html_content += f"  <li class='location-item'>{location_lookup.get(location, location).title()}\n"
            html_content += "    <ul class='work-status-list'>\n"  # Work status list with its class

            # Organize reports by work status
            work_status_dict = {}
            for file, simplified_name, _, work_status, report_name_suffix in reports:
                if work_status not in work_status_dict:
                    work_status_dict[work_status] = []
                work_status_dict[work_status].append((file, simplified_name))

            for work_status, items in work_status_dict.items():
                # Add work-status-item and report-list classes
                friendly_status = work_status_lookup.get(work_status, work_status).title()
                html_content += f"      <li class='work-status-item'>{friendly_status}<ul class='report-list'>\n"

                for file, simplified_name in items:
                    # Add report-item class to list item and maintain anchor for the report
                    html_content += f"        <li class='report-item'><a href='{file}'>{simplified_name}</a></li>\n"

                html_content += "      </ul></li>\n"  # Close work status item

            html_content += "    </ul>\n"  # Close work status list
            html_content += "  </li>\n"  # Close location item

        html_content += "</ul>\n"  # Close collapsible section

    html_content += "</nav>\n"
    return html_content


def parse_filename(filename): 
    """Parse the filename to generate a simplified and user-friendly title."""
    
    # Determine housing type
    housing_type = "Own House" if "_own_" in filename else "Rent House"
    
    # Determine school type(s)
    if "pripub" in filename:
        school_type = "Private & Public HS Blend"  # Updated to use the new term
    elif "private" in filename:
        school_type = "Private HS"
    elif "public" in filename:
        school_type = "Public HS"
    else:
        school_type = "Unknown School Type"
    
    # Extract years
    years = None
    if "3yrs" in filename:
        years = "3 Years"
    elif "4yrs" in filename:
        years = "4 Years"
    elif "6yrs" in filename:
        years = "6 Years"
    
    # Construct the final simplified name
    simplified_name = f"{housing_type} ({school_type})"
    
    if years:
        simplified_name += f" - {years}"
    
    return simplified_name


def generate_index(html_dir, config):
    """Process function to generate the index report."""
    html_files = get_html_files(html_dir)

    if not html_files:
        print(f"No scenario HTML files found in {html_dir}.")
        return

    toc_content = organize_content(html_files, html_dir, config)

    # Generate final HTML content
    final_html_content = generate_html_structure(toc_content)

    # Write the HTML content to a file
    output_file = os.path.join(html_dir, "index.html")
    write_html_to_file(output_file, final_html_content)
    print(f"Report generated: {output_file}")


def get_html_files(html_dir):
    """Get a list of HTML files in the specified directory."""
    all_files = os.listdir(html_dir)
    return [f for f in all_files if f.endswith('.html') and f.startswith('scenario')]

def organize_content(html_files, html_dir, config):
    """Organize content from HTML files into a structured format."""
    # Initialize with 'viable', 'not-viable', and 'all'
    toc_content = {"viable": {}, "not-viable": {}, "all": {}}

    for file in html_files:
        file_path = os.path.join(html_dir, file)
        logging.info(f"Processing file: {file_path}")

        try:
            # Pass config to process_html_file
            result = process_html_file(file_path, config)
            if result is None:
                logging.warning(f"No result returned for file: {file_path}. Skipping.")
                continue

            html_content, location, full_names, work_status, simplified_name, report_name_suffix = result

            # Check viability status
            viability = check_viability_status(html_content)

            # Handle unexpected viability statuses
            if viability not in toc_content:
                logging.warning(f"Unexpected viability status '{viability}' for file {file_path}. Defaulting to 'all'.")
                viability = 'all'  # Default to 'all' if the status is unrecognized

            # Initialize location in toc_content if it doesn't exist
            if location not in toc_content[viability]:
                toc_content[viability][location] = []

            # Append the file details to the recognized viability category
            toc_content[viability][location].append((file, simplified_name, full_names, work_status, report_name_suffix))

            # Also append the file details to 'all' as fallback
            if location not in toc_content['all']:
                toc_content['all'][location] = []
            toc_content['all'][location].append((file, simplified_name, full_names, work_status, report_name_suffix))

        except Exception as e:
            logging.error(f"Error processing file {file_path}: {str(e)}")

    return toc_content


def process_reports(html_dir, config):
    """Process function to gather report data without generating HTML."""
    html_files = get_html_files(html_dir)

    if not html_files:
        print(f"No scenario HTML files found in {html_dir}.")
        return

    toc_content = organize_content(html_files, html_dir, config)
    
    # Generate navigation data
    navigation_data = generate_navigation(toc_content)
    
    # Instead of writing to a file, return or print the navigation data
    return navigation_data

def generate_html_structure(toc_content):
    """Generate the HTML structure from the organized content."""
    html_content = """
    <html>
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Financial Scenario Summary Report</title>
        <link rel="stylesheet" href="../static/css/styles.css">
        <script src="../static/js/toggleVisibility.js"></script>
    </head>
    <body>
    """
    
    html_content += generate_navigation(toc_content)
    
    html_content += """
    </body>
    </html>
    """
    return html_content


def write_html_to_file(output_file, content):
    """Write the generated HTML content to a specified file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

def generate_scenario_html(scenario_title, scenario_content, navigation, output_file):
    # Read the template file
    with open('../templates/scenario_template.html', 'r', encoding='utf-8') as template_file:
        template = template_file.read()

    # Replace placeholders with actual values
    html_content = template.replace('{{ title }}', scenario_title) \
                           .replace('{{ navigation }}', navigation) \
                           .replace('{{ scenario_title }}', scenario_title) \
                           .replace('{{ scenario_content }}', scenario_content)

    # Write the generated HTML to a file
    with open(output_file, 'w', encoding='utf-8') as output:
        output.write(html_content)
    print(f"Generated HTML for {scenario_title} at {output_file}")