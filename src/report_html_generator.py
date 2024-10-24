import os
from collections import defaultdict
from bs4 import BeautifulSoup, Tag
from html import escape
from pathlib import Path
import re
import logging
import json
from io import StringIO
from typing import Any, Optional, Union

# Try to import with relative paths for Flask app
try:
    from .utils import format_currency
except ImportError:
    # Fallback to absolute import if running as a standalone script
    from utils import format_currency

def extract_numeric_value(currency_string: str) -> float | None:
    """
    Extracts a numeric value from a currency string.
    
    Args:
        currency_string (str): A string containing a currency value.
    
    Returns:
        float | None: The extracted numeric value, or None if no valid number is found.
    """
    match = re.search(r'\d+(\.\d+)?', currency_string)
    return float(match.group()) if match else None

def generate_school_expense_coverage_html(data: list[dict[str, Any]]) -> str:
    """
    Generates HTML for school expense coverage table with a collapsible structure.
    
    Args:
        data (List[Dict[str, Any]]): List of dictionaries containing school expense data.
    
    Returns:
        str: Generated HTML string with collapsible structure.
    """
    if not data:
        logging.info("School expense coverage data NOT found")
        return "<p>No school expense coverage data available.</p>"
    
    logging.info("School expense coverage data found")
    
    html = """
    <button id='school-expense-coverage-button' class='collapsible' onclick='toggleCollapsible("school-expense-coverage-button", "school-expense-coverage-content")'>
        School Expense Coverage
    </button>
    <div id='school-expense-coverage-content' class='content'>
        <div class='table-container'>
            <table>
                <tr><th>Year</th><th>Covered</th><th>Remaining Surplus</th><th>Deficit</th></tr>
    """
    
    for row in data:
        html += f"""
            <tr>
                <td>{row['year']}</td>
                <td>{'Yes' if row['covered'] else 'No'}</td>
                <td>{format_currency(row['remaining_surplus'])}</td>
                <td>{format_currency(row['deficit'])}</td>
            </tr>
        """
    
    html += """
            </table>
        </div>
    </div>
    """
    
    return html

def generate_house_html(house_data: Any, title: str) -> str:
    """
    Generates HTML for house data (current or new) with a collapsible structure.
    
    Args:
        house_data (Any): An object representing the house data.
        title (str): Title of the table.
    
    Returns:
        str: Generated HTML string with collapsible structure.
    """
    if not house_data:
        logging.info(f"{title} info NOT found")
        return f"<p>No {title.lower()} data available.</p>"
    
    logging.info(f"{title} info found")
    
    # Create a lower case, hyphenated version of the title for IDs
    id_prefix = title.lower().replace(' ', '-')
    
    html = f"""
    <button id='{id_prefix}-button' class='collapsible' onclick='toggleCollapsible("{id_prefix}-button", "{id_prefix}-content")'>
        {title}
    </button>
    <div id='{id_prefix}-content' class='content'>
        <div class='table-container'>
            <table>
                <tr><th>Attribute</th><th>Value</th></tr>
    """
    
    for attr, value in house_data.__dict__.items():
        formatted_attr = format_key(attr)
        formatted_value = format_value(value)
        html += f"<tr><td>{formatted_attr}</td><td>{formatted_value}</td></tr>"
    
    html += """
            </table>
        </div>
    </div>
    """
    
    return html

def generate_current_house_html(current_house: Any) -> str:
    """
    Generates HTML for current house data.
    
    Args:
        current_house (Any): An object representing the current house.
    
    Returns:
        str: Generated HTML string with collapsible structure.
    """
    return generate_house_html(current_house, "Current House")

def generate_new_house_html(new_house: Any) -> str:
    """
    Generates HTML for new house data.
    
    Args:
        new_house (Any): An object representing the new house.
    
    Returns:
        str: Generated HTML string with collapsible structure.
    """
    return generate_house_html(new_house, "New House")

def format_percentage(value: float) -> str:
    """Formats a float as a percentage."""
    return f"{value:.2%}"

def calculate_safe_withdrawal(total_assets: float, rate: float = 0.04) -> float:
    """Calculates the safe withdrawal amount based on total assets and a safe withdrawal rate."""
    
    logging.debug(f"Calculating safe withdrawal: total_assets={total_assets}, rate={rate}")
    
    withdrawal_amount = total_assets * rate
    
    logging.debug(f"Calculated withdrawal amount: {withdrawal_amount}")
    
    return withdrawal_amount

import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_future_value_html_table(
    report_data: dict, 
    capital_from_house_sale: float, 
    projected_investment: float, 
    projected_growth: float
) -> str:
    """Generates HTML content for the future value section of the financial report."""

    logging.debug("Starting generation of future value HTML table.")
    
    # Unpack report data for better readability
    house_info = report_data["house_info"]
    calc_data = report_data["calculated_data"]
    config_data = report_data["config_data"]
    
    logging.debug(f"Report data unpacked: house_info={house_info}, calc_data={calc_data}, config_data={config_data}")
    
    # Assign key variables
    years = config_data["years"]
    interest_rate = config_data["interest_rate"]
    annual_growth_rate = config_data.get("house", {}).get("annual_growth_rate", 0)  # Default to 0 if not available

    logging.debug(f"Years={years}, Interest rate={interest_rate}, Annual growth rate={annual_growth_rate}")
    
    # House and investment details
    new_house = house_info["new_house"]
    house_networth_future = house_info["house_networth_future"]
    house_capital_investment = house_info["house_capital_investment"]
    new_house_value = house_info["new_house_value"]
    
    logging.debug(f"House details: new_house={new_house}, house_networth_future={house_networth_future}, house_capital_investment={house_capital_investment}, new_house_value={new_house_value}")

    # Calculated data
    total_employee_stockplan = calc_data["total_employee_stockplan"]
    investment_balance_after_expenses = calc_data["investment_balance_after_expenses"]
    future_retirement_value_contrib = calc_data["future_retirement_value_contrib"]
    combined_networth_future = calc_data["combined_networth_future"]

    logging.debug(f"Calculated data: total_employee_stockplan={total_employee_stockplan}, investment_balance_after_expenses={investment_balance_after_expenses}, future_retirement_value_contrib={future_retirement_value_contrib}, combined_networth_future={combined_networth_future}")

    # Total retirement assets
    total_retirement_assets = (
        future_retirement_value_contrib 
        + investment_balance_after_expenses 
        + total_employee_stockplan
        + projected_investment
    )

    logging.debug(f"Total retirement assets: {total_retirement_assets}")

    # Calculations
    safe_withdrawal_amount = calculate_safe_withdrawal(total_retirement_assets)
    oneyear_house_value = house_networth_future * 0.035  # Example house growth calculation
    oneyear_stock_value = total_retirement_assets * interest_rate
    oneyear_growth = oneyear_house_value + oneyear_stock_value

    logging.debug(f"One-year growth: House value={oneyear_house_value}, Stock value={oneyear_stock_value}, Total growth={oneyear_growth}")
    logging.debug(f"Safe withdrawal amount: {safe_withdrawal_amount}")
        
    logging.debug(f"capital_from_house_sale: {capital_from_house_sale}")
    logging.debug(f"projected_investment: {projected_investment}")
    # HTML table rows
    rows = [
        generate_net_worth_row(
            "House Net Worth",
            new_house_value if new_house else house_networth_future,
        ),
        generate_net_worth_row(
            "House Re-Investment",
            projected_investment,
            f"This represents the capital that will be reinvested following the sale of the house, reflecting its value after {years} years of anticipated growth."
        ),
        generate_net_worth_row(
            "Stock Plan Investment Balance",
            total_employee_stockplan,
        ),
        generate_net_worth_row(
            "Investment Balance",
            investment_balance_after_expenses,
        ),
        generate_net_worth_row(
            "Retirement Balance",
            future_retirement_value_contrib,
        ),
        generate_net_worth_row(
            "Total Investment Assets",
            total_retirement_assets,
            "The total investment assets include the sum of your investment balance, retirement principal, Stock Plan Investment, and house re-investment."
        ),
        generate_net_worth_row(
            "Net Worth",
            combined_networth_future,
        ),
        generate_net_worth_row(
            "Projected One-Year Growth",
            oneyear_growth,
            f"A {format_percentage(interest_rate)} return on net worth is often used as a hypothetical annual growth rate for investments in the stock market. <br>{format_percentage(annual_growth_rate)} represents the growth of the house over time."
        ),
        generate_net_worth_row(
            "4% Safe Withdrawal Rate",
            safe_withdrawal_amount,
        ),
    ]

    logging.debug("HTML table rows generated.")
    
    # Combine all rows into the table
    html_content = f"""
    <div class='table-container'>
        <table>
            {''.join(rows)}
        </table>
    </div>
    """

    logging.debug("HTML content generated successfully.")
    
    return html_content


def generate_tooltip(icon="ℹ️", tooltip_text="", position="top"):
    """Generates HTML for a customizable tooltip.
    
    Args:
        icon (str): Icon to display for the tooltip trigger (default is ℹ️).
        tooltip_text (str): The tooltip message.
        position (str): Position of the tooltip, e.g., 'top', 'bottom', 'left', 'right'.
    
    Returns:
        str: HTML string for the tooltip.
    """
    return f"""
        <span class="tooltip" aria-describedby="tooltip" data-tooltip-position="{position}">
            <span class="tooltip-icon" aria-label="Tooltip available" role="tooltip">{icon}</span>
            <span class="tooltip-text" id="tooltip">{tooltip_text}</span>
        </span>
    """

def generate_net_worth_row(label, net_worth_value, tooltip_text=None):
    """Generates a row for the net worth table, with optional tooltip.
    
    Args:
        label (str): The label for the row (e.g., 'House Net Worth').
        net_worth_value (float): The net worth value to display.
        tooltip_text (str, optional): Tooltip text to display next to the value. Defaults to None.
    
    Returns:
        str: HTML string for the row.
    """
    logging.debug(f"Generating net worth row: label={label}, net_worth_value={net_worth_value}, tooltip_text={tooltip_text}")
    
    tooltip_html = generate_tooltip(tooltip_text=tooltip_text) if tooltip_text else ""
    
    html_row = f"""
        <tr>
            <th>{label}</th>
            <td>
                <div class="net-worth-field">
                    <span class="net-worth">{format_currency(net_worth_value)}</span>
                    {tooltip_html}
                </div>
            </td>
        </tr>
    """
    
    logging.debug(f"Generated HTML row: {html_row.strip()}")
    
    return html_row


def generate_current_networth_html_table(
    report_data: dict, 
    capital_from_house_sale: float, 
    projected_investment: float, 
    projected_growth: float
) -> str:
    """
    Generates HTML content for the current net worth section of the financial report.

    Args:
        report_data (dict): Contains financial and house information.
        capital_from_house_sale (float): Capital to be reinvested from house sale.
        projected_investment (float): Projected value of the house sale investment.
        projected_growth (float): Projected growth of investments.

    Returns:
        str: HTML content for the current net worth table.
    """
    # Constants
    SAFE_WITHDRAWAL_RATE = 0.04

    # Extracting necessary information
    house_info = report_data.get("house_info", {})
    config_data = report_data.get("config_data", {})
    calculated_data = report_data.get("calculated_data", {})

    years = config_data.get("years", 0)
    interest_rate = config_data.get("interest_rate", 0.0)
    annual_growth_rate = config_data.get("house", {}).get("annual_growth_rate", 0.0)

    # Calculating necessary values
    house_net_worth = house_info.get("house_net_worth", 0.0)
    retirement_principal = calculated_data.get('total_retirement_principal', 0.0)
    combined_networth = calculated_data.get("combined_networth", 0.0)

    total_investment_balance = calculated_data['total_investment_balance']
    total_retirement_assets = capital_from_house_sale + total_investment_balance + retirement_principal
    safe_withdrawal_amount = SAFE_WITHDRAWAL_RATE * total_retirement_assets

    oneyear_house_value = house_net_worth * annual_growth_rate 
    oneyear_stock_value = total_retirement_assets * interest_rate 
    oneyear_growth = oneyear_house_value + oneyear_stock_value

    logging.debug(f"capital_from_house_sale: {capital_from_house_sale}")

    # HTML table rows
    rows = [
        generate_net_worth_row(
            "House Net Worth",
            house_net_worth,
            "Calculated by (House Value - Remaining Mortgage Principal)"
        ),
        generate_net_worth_row(
            "House Re-Investment",
            capital_from_house_sale,
            f"This is the capital that will be reinvested after the house is sold.<br>Projected Future Value: {format_currency(projected_investment)}"
        ),
        generate_net_worth_row(
            "Investment Balance",
            total_investment_balance,
            f"Projected value if not used to cover expenses.<br>Projected Future Value: {format_currency(projected_growth)}"
        ),
        generate_net_worth_row("Retirement Balance", retirement_principal),
        generate_net_worth_row("Net Worth", combined_networth),
        generate_net_worth_row(
            "Total Investment Assets",
            total_retirement_assets,
            "Total investment assets include investment balance, retirement principal, and any capital reinvested from the house sale. House net worth is not included."
        ),
        generate_net_worth_row(
            "Projected One-Year Growth",
            oneyear_growth,
            f"A {interest_rate:.2%} return on net worth is often used as a hypothetical annual growth rate for investments. <br>{annual_growth_rate:.2%} represents the growth of the house over time."
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


def generate_income_expenses_html(section_title: str, calculated_data: dict) -> str:
    """
    Converts the calculated income and expenses data into an HTML table with collapsible functionality.

    Args:
        section_title (str): The title of the income/expenses section.
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

        if isinstance(value, dict):
            nested_table = generate_nested_table(value)
            html_content += f"<tr><td>{formatted_key}</td><td>{nested_table}</td></tr>"
        
        elif isinstance(value, list):
            list_html = generate_list(value)
            html_content += f"<tr><td>{formatted_key}</td><td>{list_html}</td></tr>"

        else:
            html_content += f"<tr><td>{formatted_key}</td><td>{format_value(value)}</td></tr>"

    html_content += """
                </tbody>
            </table>
        </div>
    </div>
    """

    return html_content

def format_key(key: str) -> str:
    """
    Formats a key for better readability in the HTML table.
    
    Args:
        key (str): The key to format.

    Returns:
        str: Formatted key for display.
    """
    return key.replace('_', ' ').capitalize()

def format_keydetailed(key: str) -> str:
    """
    Formats a key for detailed display, converting camel case or underscore-separated words
    to space-separated words.

    Args:
        key (str): The key to format.

    Returns:
        str: Formatted detailed key for display.
    """
    # Convert camel case or underscore-separated words to space-separated words
    formatted_key = re.sub(r'(?<!^)(?=[A-Z][a-z])|_', ' ', key)
    # Capitalize the first letter of each word
    return ' '.join(word.capitalize() for word in formatted_key.split())

def format_value(value) -> str:
    """
    Formats a value for display in the HTML table.

    Args:
        value: The value to format.

    Returns:
        str: Formatted value for display.
    """
    if isinstance(value, (int, float)):
        # Format numbers with commas
        return f"{value:,.3f}" if isinstance(value, float) else f"{value:,}"
    else:
        # Return the string representation for other types
        return str(value)

def generate_nested_table(data: dict) -> str:
    """Generate HTML for nested tables from a dictionary."""
    nested_table = "<table><thead><tr><th>Subcategory</th><th>Value</th></tr></thead><tbody>"
    for sub_key, sub_value in data.items():
        nested_table += f"<tr><td>{format_key(sub_key)}</td><td>{format_value(sub_value)}</td></tr>"
    nested_table += "</tbody></table>"
    return nested_table

def generate_list(items: list) -> str:
    """Generate HTML for a list of items."""
    return "<ul>" + "".join(f"<li>{format_value(item)}</li>" for item in items) + "</ul"

def generate_configuration_data_html(section_title: str, configuration_data: dict) -> str:
    """
    Converts the JSON configuration data into an HTML table with collapsible functionality.

    Args:
        section_title (str): The title of the configuration section.
        configuration_data (dict): The dictionary containing the JSON configuration.

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

    # Iterate over the configuration data dictionary
    for key, value in configuration_data.items():
        formatted_key = format_key(key)  # Format the key for readability

        if isinstance(value, dict):
            nested_table = generate_nested_table(value)
            html_content += f"<tr><td>{formatted_key}</td><td>{nested_table}</td></tr>"
        
        elif isinstance(value, list):
            list_html = generate_list(value)
            html_content += f"<tr><td>{formatted_key}</td><td>{list_html}</td></tr>"

        else:
            html_content += f"<tr><td>{formatted_key}</td><td>{format_value(value)}</td></tr>"

    html_content += """
                </tbody>
            </table>
        </div>
    </div>
    """

    return html_content


def safe_int_conversion(value) -> int:
    """
    Safely converts a value to an integer.

    Args:
        value: The value to convert.

    Returns:
        int: The converted integer or the original value if conversion fails.
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return value  # or return 0, or any other default value

def generate_current_networth_html(report_data: dict) -> str:
    """
    Generate HTML content for the current net worth section of the financial report.

    Args:
        report_data (dict): Dictionary containing all necessary data for calculating the current net worth section.

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
                <tr><th>House Net Worth</th><td>{format_currency(house_info.get("house_net_worth", 0))}</td></tr>
                <tr><th>Investment Balance</th><td>{format_currency(calculated_data.get('total_investment_balance', 0))}</td></tr>
                <tr><th>Retirement Balance</th><td>{format_currency(config_data.get('retirement_principal', 0))}</td></tr>
                <tr><th>Combined Net Worth</th><td>{format_currency(calculated_data.get("combined_networth", 0))}</td></tr>
            </table>
        </div>
    </div>
    """
    return html_content

def generate_table_html(data, custom_formatter=None, headers=None) -> str:
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
            formatted_value = apply_custom_formatter(value, custom_formatter)
            table_html += f"             <tr><th>{key}</th><td>{formatted_value}</td></tr>\n"
    elif hasattr(data, '__dict__'):
        for attr, value in data.__dict__.items():
            formatted_value = apply_custom_formatter(value, custom_formatter)
            table_html += f"             <tr><th>{attr}</th><td>{formatted_value}</td></tr>\n"
    table_html += "            </tbody>\n"

    table_html += "          </table>\n         </div>"
    return table_html


def generate_paragraph_html(data: str, custom_formatter=None) -> str:
    """
    Generates HTML for a paragraph, with optional custom formatting.

    Args:
        data (str): The content of the paragraph.
        custom_formatter (function, optional): A function to format the data.

    Returns:
        str: The generated HTML content for the paragraph.
    """
    # Apply custom formatting if provided
    data = apply_custom_formatter(data, custom_formatter)
    
    return f"<p>{data}</p>"


def apply_custom_formatter(value, custom_formatter):
    """
    Applies a custom formatter to a value if provided.

    Args:
        value: The value to format.
        custom_formatter (function, optional): A custom function to format the value.

    Returns:
        The formatted value or the original value if no formatter is provided.
    """
    return custom_formatter(value) if custom_formatter and value is not None else value


def generate_section_html(section_title, data, custom_formatter=None, headers=None, collapsible=False) -> str:
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
        logging.info("No data available passed to function")
        return "<p>No data available.</p>"
    
    html_content = ""
    section_id = generate_section_id(section_title)
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
        if section_title:
            html_content += f"<h3>{section_title}</h3>"

    # Generate table or paragraph based on data type
    html_content += generate_content_html(data, custom_formatter, headers)

    if collapsible:
        html_content += "</div>"  # Close the collapsible content div

    return html_content


def generate_section_id(section_title: str) -> str:
    """
    Generates a unique section ID based on the section title.

    Args:
        section_title (str): The title of the section.

    Returns:
        str: A unique ID for the section.
    """
    return section_title.replace(" ", "-").lower() if section_title else "section"


def generate_content_html(data, custom_formatter, headers) -> str:
    """
    Generates the HTML content for the provided data.

    Args:
        data: The data to be displayed.
        custom_formatter (function, optional): A custom function to format the values.
        headers (list, optional): A list of column headers for the table.

    Returns:
        str: The generated HTML content for the data.
    """
    if isinstance(data, dict) or hasattr(data, '__dict__'):
        try:
            return generate_table_html(data, custom_formatter, headers)
        except Exception as e:
            logging.error(f"Error generating table: {e}")
            return "<p>Error generating table content.</p>"
    else:
        return generate_paragraph_html(data, custom_formatter)


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

    investment_principal = report_data["calculated_data"].get("investment_balance_after_expenses", 0)
    house_capital_investment = report_data["house_info"].get("house_capital_investment", 0)

    # Ensure both are floats or ints and handle None cases if necessary
    investment_principal = investment_principal if investment_principal is not None else 0
    house_capital_investment = house_capital_investment if house_capital_investment is not None else 0

    # Conditional check for viability
    viable_status = "Viable" if (investment_principal + house_capital_investment) > 50000 else "Not Viable"
    logging.info(f"Investment Principal: {investment_principal}, House Capital Investment: {house_capital_investment}, Viable Status: {viable_status}")

    # Generate the scenario filename
    scenario_full_name = report_data["calculated_data"].get("scenario_name", "index")
    scenario_filename = f"scenario_{scenario_full_name}.html"
    scenario_link = f"scenario_{scenario_full_name}"

    # Start generating HTML content
    logging.debug("Generating HTML content for the report.")
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
                    <p><a href="{scenario_link}">View Full Scenario</a></p>
    """

    # future_value_html = build_future_value_html_table(report_data)
    # formatted_future_title = format_key("Future Value")
    # html_content += f"<button type='button' class='collapsible' onclick='toggleCollapsible(\"future-value\", \"future-value-content\")'>{escape(formatted_future_title)}</button>"
    # html_content += f"<div id='future-value-content' class='content'>{future_value_html}</div>"

    annual_income_surplus_html = generate_section_html("Annual Income Surplus", report_data["calculated_data"]["annual_surplus"], format_currency)
    annual_income_surplus_title = format_key("Annual Income Surplus")
    html_content += f"<button type='button' class='collapsible' onclick='toggleCollapsible(\"annual_income_surplus\", \"annual_income_surplus-content\")'>{escape(annual_income_surplus_title)}</button>"
    html_content += f"<div id='annual_income_surplus-content' class='content'>{annual_income_surplus_html}</div>"

    logging.debug("Adding configuration data to HTML content.")
    html_content += generate_configuration_data_html("Configuration Data", report_data['config_data'])
    html_content += generate_income_expenses_html("Income and Expenses", report_data['calculated_data'])
    html_content += generate_current_networth_html(report_data)

    school_expense_coverage_html = generate_school_expense_coverage_html(report_data["calculated_data"]["school_expense_coverage"])
    html_content += school_expense_coverage_html

    headers = ["Attribute", "Value"]
    logging.info("Generating house info HTML.")
    
    if "house_info" in report_data:
        house_info_html = generate_section_html(
            None,
            report_data["house_info"],
            custom_formatter=None,
            headers=headers,
            collapsible=True
        )
    else:
        logging.warning('"house_info" is NOT in report_data')
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
        logging.warning('new_house is NOT in report_data')
        html_content += "<p>new_house is NOT available.</p>"
    
    html_content += """
                    </div>
            </div>
            </div> <!-- End of header-container -->
    </body>
    </html>
    """
    
    logging.info("HTML content generated successfully.")
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
        <section class='scenario' id='{scenario_id}'>
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
        </section>
        """

    # Function to create detailed information section
    def create_detailed_info_section(scenario_name, scenario_data):
        """Generates HTML for detailed information section."""
        scenario_id = scenario_name.replace(" ", "-").lower()
        detail_filename = f"detail_{scenario_name}.html"
        detail_name = f"detail_{scenario_name}"
        return f"""
        <aside class='detailed-info' id='{scenario_id}-detail' aria-labelledby='{scenario_id}'>
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
                <a href="/view_report/{detail_name}" aria-label="View detailed information for {escape(scenario_name)}">View Detailed Information</a>
            </div>
        </aside>
        """

    # Loop through each scenario to generate the HTML content
    for scenario_name, scenario_data in summary_report_data.items():
        if not isinstance(scenario_data, dict):
            logging.warning(f"Invalid data for scenario '{scenario_name}'. Expected a dictionary.")
            continue  # Skip invalid scenario data

        logging.info(f"Generating HTML for scenario: {scenario_name}")
        
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
    
    logging.info("Summary report HTML generation complete.")
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
    if not child_data or "children" not in child_data:
        # Return a message if no data is provided
        return "<p>No children school expenses data available.</p>"
    
    html_content = ""  # Initialize the HTML content

    for index, child in enumerate(child_data.get("children", [])):
        child_name = escape(child.get('name', 'Unnamed Child'))  # Get and escape the child's name
        child_id = f"childDetails-{index}"  # Create a unique ID for each child's details section

        # Add the child name as a collapsible button with toggle functionality
        html_content += create_collapsible_button(child_id, child_name)

        # Generate the table for the child
        html_content += generate_child_table(child, table_class, headers, child_id)

    return html_content

def create_collapsible_button(child_id, child_name):
    """Creates a collapsible button for the child's educational expenses.

    Args:
        child_id (str): Unique ID for the child's details section.
        child_name (str): The name of the child.

    Returns:
        str: HTML for the collapsible button.
    """
    return f"""
        <button id="{child_id}-button" class="collapsible" onclick="toggleCollapsible('{child_id}-button', '{child_id}-content')">
            {child_name} School
        </button>
        <div id="{child_id}-content" class="content">
    """

def generate_child_table(child, table_class, headers, child_id):
    """Generates an HTML table for the child's school expenses.

    Args:
        child (dict): A dictionary containing the child's data.
        table_class (str): The CSS class to apply to the table.
        headers (list): A list of column headers for the table.
        child_id (str): Unique ID for the child's details section.

    Returns:
        str: HTML for the child's expenses table.
    """
    school_data = child.get("school", {})

    # Combine all entries across school types into one list
    combined_entries = []
    for school_type, entries in school_data.items():
        for entry in entries:
            combined_entries.append({
                'school_type': school_type,
                'year': int(entry.get('year', 0)),
                'cost': entry.get('cost', 0)
            })

    # Sort entries by year
    sorted_entries = sorted(combined_entries, key=lambda entry: entry['year'])

    if not sorted_entries:
        return "<p>No school expense entries available for this child.</p>"

    # Generate the table header
    table_html = f"""
        <table class='{table_class}'>
            <thead>
                <tr><th>{escape(headers[0])}</th><th>{escape(headers[1])}</th><th>{escape(headers[2])}</th></tr>
            </thead>
            <tbody>
    """

    # Generate the table rows
    for entry in sorted_entries:
        year = escape(str(entry['year']))  # Convert back to string for HTML
        cost = format_currency(entry['cost'])  # Format cost for readability
        school_type = escape(entry['school_type'])
        table_html += f"<tr><td>{school_type}</td><td>{year}</td><td>{cost}</td></tr>\n"

    table_html += """
            </tbody>
        </table>
        </div>  <!-- End of hidden details section -->
    """  # End of child section

    return table_html

def _generate_investment_table(data, custom_formatter=None):
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


def generate_investment_table(data, custom_formatter=None):
    """Generates HTML for a table based on the provided data.

    Args:
        data (dict): The data to be displayed in the table.
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
                <tr><th>Investment Name</th><th>Type</th><th>Amount</th></tr>
    """

    total = 0
    if isinstance(data, dict):
        for key, investment in data.items():
            # Extract the name, type, and amount from each investment
            name = investment.get('name', 'Unknown')
            inv_type = investment.get('type', 'Unknown')
            amount = investment.get('amount', 0)

            # Format the amount if necessary and add to total
            formatted_amount = custom_formatter(amount) if custom_formatter else amount
            total += amount  # Accumulate the total only for numeric 'amount'

            # Add each investment's details to the table
            html_content += f"<tr><th>{name}</th><td>{inv_type}</td><td>{formatted_amount}</td></tr>"

    # Add the total row
    formatted_total = custom_formatter(total) if custom_formatter else total
    html_content += f"<tr><th>Total</th><td colspan='2'>{formatted_total}</td></tr>"

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
    if not config_data or "RETIREMENT" not in config_data:
        return "<p>No retirement data available.</p>"

    html_content = ""  # Initialize the HTML content
    grand_total_balance = calculate_grand_total_balance(config_data["RETIREMENT"])

    # Add collapsible section for grand total balance at the top
    html_content += create_grand_total_section(grand_total_balance, table_class)

    # Iterate through each parent in the retirement data
    retirement_data = config_data["RETIREMENT"]
    for index, parent in enumerate(retirement_data):
        html_content += create_parent_section(parent, index, table_class)

    return html_content

def calculate_grand_total_balance(retirement_data):
    """Calculates the grand total balance from retirement accounts.

    Args:
        retirement_data (list): A list of retirement data for parents.

    Returns:
        float: The grand total balance for all parents.
    """
    grand_total = 0
    for parent in retirement_data:
        accounts_data = parent.get("accounts", {})
        for entries in accounts_data.values():
            for entry in entries:
                for balance in entry.values():
                    grand_total += balance
    return grand_total

def create_grand_total_section(grand_total_balance, table_class):
    """Creates the HTML for the grand total balance section.

    Args:
        grand_total_balance (float): The grand total balance to display.
        table_class (str): The CSS class to apply to the table.

    Returns:
        str: HTML for the grand total section.
    """
    formatted_grand_total_balance = "{:,.2f}".format(grand_total_balance)
    return f"""
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

def create_parent_section(parent, index, table_class):
    """Creates the HTML for a parent's section including contributions and accounts.

    Args:
        parent (dict): A dictionary containing retirement data for a parent.
        index (int): The index of the parent.
        table_class (str): The CSS class to apply to the table.

    Returns:
        str: HTML for the parent's section.
    """
    parent_name = escape(parent.get("name", "Unknown Parent"))
    parent_id = f"parentDetails-{index}"

    # Start the parent's section
    html_content = f"""
        <button id="{parent_id}-button" class="collapsible" onclick="toggleCollapsible('{parent_id}-button', '{parent_id}-content')">{parent_name} Retirement</button>
        <div id="{parent_id}-content" class="content">
            <h3>Contributions</h3>
            {create_contributions_table(parent.get("contributions", {}), table_class)}
            <h3>Accounts</h3>
            {create_accounts_table(parent.get("accounts", {}), table_class)}
        </div>  <!-- End of hidden details section -->
    """
    return html_content

def create_contributions_table(contributions_data, table_class):
    """Creates the HTML table for contributions.

    Args:
        contributions_data (dict): A dictionary of contributions data.
        table_class (str): The CSS class to apply to the table.

    Returns:
        str: HTML for the contributions table.
    """
    html_content = f"""
        <table class='{table_class}'>
            <thead>
                <tr><th>Type</th><th>Contribution</th><th>Amount</th></tr>
            </thead>
            <tbody>
    """
    total_contributions = 0

    for contribution_type, entries in contributions_data.items():
        for entry in entries:
            for contribution, amount in entry.items():
                stripped_contribution = format_contribution_name(contribution)
                formatted_amount = "{:,.2f}".format(amount)
                html_content += f"<tr><td>{escape(contribution_type)}</td><td>{escape(stripped_contribution)}</td><td>{formatted_amount}</td></tr>\n"
                total_contributions += amount

    formatted_total_contributions = "{:,.2f}".format(total_contributions)
    html_content += f"<tr><td colspan='2'><strong>Total Contributions</strong></td><td><strong>{formatted_total_contributions}</strong></td></tr>\n"
    html_content += "</tbody>\n</table>\n"  # End of contributions table
    return html_content

def create_accounts_table(accounts_data, table_class):
    """Creates the HTML table for accounts.

    Args:
        accounts_data (dict): A dictionary of accounts data.
        table_class (str): The CSS class to apply to the table.

    Returns:
        str: HTML for the accounts table.
    """
    html_content = f"""
        <table class='{table_class}'>
            <thead>
                <tr><th>Type</th><th>Account Name</th><th>Balance</th></tr>
            </thead>
            <tbody>
    """
    total_accounts_balance = 0

    for account_type, entries in accounts_data.items():
        for entry in entries:
            for account_name, balance in entry.items():
                formatted_balance = "{:,.2f}".format(balance)
                html_content += f"<tr><td>{escape(account_type)}</td><td>{escape(account_name)}</td><td>{formatted_balance}</td></tr>\n"
                total_accounts_balance += balance

    formatted_total_accounts = "{:,.2f}".format(total_accounts_balance)
    html_content += f"<tr><td colspan='2'><strong>Total Account Balances</strong></td><td><strong>{formatted_total_accounts}</strong></td></tr>\n"
    html_content += "</tbody>\n</table>\n"  # End of accounts table
    return html_content

def format_contribution_name(contribution):
    """Formats the contribution name to be more user-friendly.

    Args:
        contribution (str): The original contribution name.

    Returns:
        str: The formatted contribution name.
    """
    return contribution.replace("spouse1_", "").replace("spouse2_", "").replace("retirement_", "").replace("contribution_", "").replace("_", " ").title()


def generate_friendly_name(scenario_file):
    """Generate a user-friendly name for the scenario file."""
    if not scenario_file.endswith('.html'):
        raise ValueError("The scenario file must end with '.html'.")

    parts = scenario_file[:-5].split('_')  # Remove '.html' and split by '_'

    # Check if we have enough parts for our expected format
    if len(parts) < 4:
        raise ValueError("Scenario file does not have enough parts to generate a friendly name.")

    location = format_location(parts[0])
    names = format_names(parts[1:3])  # Expecting at least two names
    work_status = format_work_status(parts[2])
    ownership = format_ownership(parts[3])

    # Create a user-friendly description
    friendly_name = f"{names} in {location}, {work_status} ({ownership})"
    return friendly_name

def format_location(code):
    """Formats the location code to a friendly name."""
    return code.replace('sf', 'San Francisco').replace('mn', 'Minnesota').capitalize()

def format_names(name_parts):
    """Formats the names to a user-friendly string."""
    return ' & '.join(part.capitalize() for part in name_parts)

def format_work_status(status):
    """Formats the work status to a user-friendly string."""
    return status.replace('-', ' ').capitalize()

def format_ownership(ownership_code):
    """Formats the ownership code to a user-friendly string."""
    return ownership_code.replace('public', 'Public').replace('own', 'Own').replace('private', 'Private').capitalize()

# Helper function to check the viability status
def check_viability_status(html_content):
    """Check the viability status from the given HTML content.

    Args:
        html_content (str): The HTML content to parse.

    Returns:
        str: 'viable', 'not-viable', or 'unknown' based on the status found.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        status_element = soup.find('h4', class_='scenario-status')

        # Check if status_element is found
        if status_element is None:
            logging.warning("Status element not found. Returning 'unknown'.")
            return 'unknown'

        # Ensure status_element is a Tag
        if isinstance(status_element, Tag):
            class_list = status_element.get('class', [])
            if isinstance(class_list, list):
                if 'viable' in class_list:
                    return 'viable'
                elif 'not-viable' in class_list:
                    return 'not-viable'
                else:
                    logging.warning("No recognized status class found in the class list. Returning 'unknown'.")
                    return 'unknown'
            else:
                logging.warning(f"Unexpected class attribute type: {type(class_list)}. Returning 'unknown'.")
                return 'unknown'
        else:
            logging.warning(f"Unexpected element type: {type(status_element)}. Returning 'unknown'.")
            return 'unknown'

    except Exception as e:
        logging.error(f"Error while checking viability status: {e}")
        return 'unknown'

def extract_attributes_from_filename(filename, name_lookup, work_status_lookup, location_lookup, ownership_type_lookup, school_type_lookup):
    """Extracts attributes from a scenario filename.

    Args:
        filename (str): The filename to parse.
        name_lookup (dict): A mapping from short names to full names.
        work_status_lookup (dict): A mapping for work status.
        location_lookup (dict): A mapping for location codes.
        ownership_type_lookup (dict): A mapping for ownership types.
        school_type_lookup (dict): A mapping for school types.

    Returns:
        tuple: A tuple containing:
            - location (str): The location code (e.g., 'mn', 'sf').
            - full_names (list): List of full names corresponding to the extracted names.
            - work_status (str): The work status extracted from the filename.
            - simplified_name (str): A simplified name combining ownership and school type.
            - report_name_suffix (str): Additional content for the report name, if any.
    
    Raises:
        ValueError: If the filename does not contain enough parts.
    """
    # Remove the extension
    name_parts = filename[:-5].split('_')

    # Ensure sufficient parts are present
    if len(name_parts) < 5:
        raise ValueError(f"Filename '{filename}' does not have enough parts to unpack.")

    # Extract relevant parts
    location = name_parts[1]  # 'mn' or 'sf'
    names = name_parts[2:4]  # ['hav', 'jason']
    work_status = name_parts[4]  # 'work-retired'
    
    # Extract ownership type and school type, handling optional parts
    ownership_type = name_parts[5] if len(name_parts) > 5 else ""
    school_type = name_parts[6] if len(name_parts) > 6 else ""  # 'public' or similar

    # Capture any additional content beyond school type
    extra_content = "_".join(name_parts[7:]) if len(name_parts) > 7 else ""  # Join any extra parts into a single string

    # Generate full names using the lookup
    full_names = [name_lookup.get(name, name).title() for name in names]
    
    # Map ownership and school types to friendly names
    friendly_ownership = ownership_type_lookup.get(ownership_type, ownership_type.title())
    friendly_school = school_type_lookup.get(school_type, school_type.title())
    
    # Construct the simplified name
    simplified_name = f"{friendly_ownership} & {friendly_school}".strip()

    # Include extra content in the report name if available
    report_name_suffix = f" ({extra_content})" if extra_content else ""

    # Add the report name suffix to the simplified name if it exists
    if report_name_suffix:
        simplified_name += report_name_suffix

    return location, full_names, work_status, simplified_name, report_name_suffix


def process_html_file(file_path, config):
    """Process an HTML file to extract relevant attributes.

    Args:
        file_path (str): The path to the HTML file.
        config (dict): A configuration dictionary containing lookup mappings.

    Returns:
        tuple: A tuple containing:
            - html_content (str): The content of the HTML file.
            - location (str): The location code extracted from the filename.
            - full_names (list): List of full names corresponding to the extracted names.
            - work_status (str): The work status extracted from the filename.
            - simplified_name (str): A simplified name combining ownership and school type.
            - report_name_suffix (str): Additional content for the report name, if any.
    """
    # Check if the file exists
    if not os.path.isfile(file_path):
        logging.error(f"File not found: {file_path}")
        return ""

    # Read the HTML content from the file
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Extract attributes from the filename
    try:
        # Pass specific lookup dictionaries
        location, full_names, work_status, simplified_name, report_name_suffix = extract_attributes_from_filename(
            os.path.basename(file_path),
            config['name_lookup'],
            config['work_status_lookup'],
            config['location_lookup'],
            config['ownership_type_lookup'],
            config['school_type_lookup']
        )
        return html_content, location, full_names, work_status, simplified_name, report_name_suffix
    except ValueError as e:
        logging.warning(f"Skipping file {file_path}: {e}")
        return "", "", [], "", "", ""


def generate_navigation(toc_content, config):
    """Generate structured navigation HTML with collapsible sections and dynamic parent names in work statuses."""
    html_content = StringIO()  # Use StringIO for efficient string concatenation
    html_content.write("<nav class='site-navigation'>\n")
    
    # Add a div container for flexbox layout for buttons
    html_content.write("<div class='nav-buttons'>\n")

    for viability in toc_content:
        formatted_viability = viability.replace('-', ' ').title()
        section_id = f"{viability}-content"
        button_id = f"{viability}-button"

        # Check if the current viability is "viable" to add the active class
        active_class = "active" if viability == "viable" else ""

        # Add collapsible button inside the nav-buttons div for flexbox layout
        html_content.write(f"<button id='{button_id}' type='button' class='collapsible nav-collapsible {active_class}' onclick='toggleCollapsible(\"{button_id}\", \"{section_id}\", true)'>{formatted_viability}</button>\n")
    
    # Close the div for buttons
    html_content.write("</div>\n")

    # Add collapsible content sections
    for viability in toc_content:
        section_id = f"{viability}-content"
        max_height_style = "max-height:initial; overflow:hidden;" if viability == "viable" else "max-height:0; overflow:hidden;"

        html_content.write(f"<ul id='{section_id}' class='viability-list collapsible-content nav-collapsible-content' style='{max_height_style}'>\n")

        for location, reports in toc_content[viability].items():
            # Adding class for location items
            location_name = config['location_lookup'].get(location, location).title()  # Use config to get location names
            html_content.write(f"  <li class='location-item'>{location_name}\n")
            html_content.write("    <ul class='work-status-list'>\n")  # Work status list with its class

            # Organize reports by work status
            work_status_dict = {}
            for file, simplified_name, full_names, work_status, report_name_suffix in reports:
                # if len(full_names) == 2:
                parent1_name, parent2_name = full_names
                # else:
                #     logging.warning(f"Error: Parent names are not provided correctly in the configuration. {full_names}")
                #     parent1_name = parent2_name = "Unknown Parent"  # Fallback if names are missing

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

                work_status_dict.setdefault(friendly_status, []).append((file, simplified_name))

            for friendly_status, items in work_status_dict.items():
                # Add work-status-item and report-list classes
                html_content.write(f"      <li class='work-status-item'>{friendly_status}<ul class='report-list'>\n")

                for file, simplified_name in items:
                    # Remove .html suffix from file for the link
                    file_without_extension = file.replace('.html', '')  # Strip .html
                    # Add report-item class to list item and maintain anchor for the report
                    html_content.write(f"        <li class='report-item'><a href='/view_report/{file_without_extension}'>{simplified_name}</a></li>\n")
                
                html_content.write("      </ul></li>\n")  # Close work status item

            html_content.write("    </ul>\n")  # Close work status list
            html_content.write("  </li>\n")  # Close location item

        html_content.write("</ul>\n")  # Close collapsible section

    html_content.write("</nav>\n")
    return html_content.getvalue()  # Return the concatenated string


def _generate_index(html_dir, config):
    """Process function to generate the index report."""
    html_files = get_html_files(html_dir)

    if not html_files:
        print(f"No scenario HTML files found in {html_dir}.")
        return

    toc_content = organize_content(html_files, html_dir, config)

    # Generate final HTML content
    final_html_content = generate_html_structure(toc_content, config)

    # Write the HTML content to a file
    output_file = os.path.join(html_dir, "index.html")
    write_html_to_file(output_file, final_html_content)
    print(f"Report generated: {output_file}")


def get_html_files(html_dir):
    """Get a list of HTML files in the specified directory that start with 'scenario'."""
    try:
        # Use os.scandir for better performance and information
        with os.scandir(html_dir) as entries:
            html_files = [entry.name for entry in entries if entry.is_file() and entry.name.endswith('.html') and entry.name.startswith('scenario')]
        return html_files
    except FileNotFoundError:
        print(f"Error: The directory '{html_dir}' does not exist.")
        return []
    except PermissionError:
        print(f"Error: Permission denied for accessing the directory '{html_dir}'.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []
    

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

            # Ensure viability key always refers to a dictionary
            if viability not in toc_content:
                toc_content[viability] = {}  # If viability was missing, this would ensure it's always a dictionary

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


def process_reports(html_dir: Path, config: dict[str, Any]) -> Optional[str]:
    """
    Process function to gather report data without generating HTML.

    Args:
        html_dir (Path): Directory containing HTML files.
        config (dict[str, Any]): Configuration options.

    Returns:
        Optional[str]: Navigation data generated from the report files, or None if no files are found.
    """
    # Fetch HTML files from the directory
    html_files = get_html_files(html_dir)

    # Check if any HTML files were found
    if not html_files:
        logging.warning(f"No scenario HTML files found in {html_dir}.")
        return None

    # Organize the content from the HTML files based on viability and location
    toc_content = organize_content(html_files, html_dir, config)

    # Generate navigation data based on the organized content
    navigation_data = generate_navigation(toc_content, config)

    # Return the navigation data instead of writing it to a file
    logging.info("Navigation data successfully generated.")
    return navigation_data


def generate_html_structure(toc_content: dict[str, Any], config: dict[str, Any]) -> str:
    """Generate the HTML structure from the organized content.

    Args:
        toc_content (dict[str, Any]): Table of contents content organized by viability and location.
        config (dict[str, Any]): Configuration options for the report.

    Returns:
        str: The complete HTML structure as a string.
    """
    
    # Generate the dynamic title from the config or use a default
    title = config.get("report_title", "Financial Scenario Summary Report")

    # Start building the HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <link rel="stylesheet" href="../static/css/styles.css">
        <script src="../static/js/toggleVisibility.js" defer></script>
    </head>
    <body>
    """
    
    # Generate navigation and append to the HTML content
    html_content += generate_navigation(toc_content, config)

    # Close the HTML structure
    html_content += """
    </body>
    </html>
    """
    
    return html_content


def write_html_to_file(output_file: Union[str, Path], content: str) -> None:
    """Write the generated HTML content to a specified file.

    Args:
        output_file (Union[str, Path]): The path to the output file where HTML content will be written.
        content (str): The HTML content to write to the file.

    Raises:
        ValueError: If the content is empty.
    """
    if not content:
        raise ValueError("Content to write cannot be empty.")

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        logging.info(f"Successfully wrote to {output_file}")
    except IOError as e:
        logging.error(f"Error writing to file {output_file}: {e}")
