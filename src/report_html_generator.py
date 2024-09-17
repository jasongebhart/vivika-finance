from utils import format_currency
from html import escape
import re
import logging

def format_key(key):
    import re
    # Convert camel case or underscore-separated words to space-separated words
    formatted_key = re.sub(r'(?<!^)(?=[A-Z][a-z])|_', ' ', key)
    # Capitalize the first letter of each word
    formatted_key = ' '.join(word.capitalize() for word in formatted_key.split())
    return formatted_key

def extract_numeric_value(currency_string):
    match = re.search(r'\d+\.\d+', currency_string)
    if match:
        return float(match.group())
    else:
        return None  # Handle invalid currency strings
    
def generate_school_expense_coverage_html(data):
    html = """
    <h2 id='school-expense-coverage-title'>School Expense Coverage
        <button type='button' class='toggle-button' onclick='toggleSectionVisibility("school-expense-coverage")'>Toggle</button>
    </h2>
    <div id='school-expense-coverage-content' class='section-content hidden'>
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

def generate_current_house_html_old(current_house):
    html_content = """
    <h2 id='current-house'>Current House
        <button type='button' class='toggle-button' onclick='toggleSectionVisibility("current-house")'>Toggle</button>
    </h2>
    <div id='current-house-content' class='section-content hidden'>
        <div class='table-container'>
            <table>
                <tr><th>Attribute</th><th>Value</th></tr>
    """
    for attr, value in current_house.__dict__.items():
        formatted_attr = format_key(attr)
        if isinstance(value, (int, float)):
            formatted_value = "${:,.2f}".format(value)
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

def generate_current_house_html(current_house):
    """Generates HTML content for the current house section.

    Args:
        current_house (object): An object representing the current house.

    Returns:
        str: The generated HTML content.
    """

    html_content = """
    <h2 id='current-house'>Current House
        <button type='button' class='toggle-button' onclick='toggleSectionVisibility("current-house")'>Toggle</button>
    </h2>
    <div id='current-house-content' class='section-content hidden'>
        <div class='table-container'>
            <table>
                <tr><th>Attribute</th><th>Value</th></tr>
    """

    for attr, value in current_house.__dict__.items():
        formatted_attr = format_key(attr)

        if isinstance(value, (float, int)):
            # Check for decimal interest rate (0 to 1)
            if 0 <= value <= 1:
                formatted_value = f"{value:.2%}"  # Convert to percentage
            else:
                # Check for currency format
                if re.search(r"^\$[\d,.]+$", str(value)):
                    formatted_value = str(value)  # Keep currency format
                else:
                    formatted_value = "${:,.2f}".format(value)
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
    years = report_data["config_data"]["years"]
    new_house = report_data["house_info"]["new_house"]
    new_house_value = report_data["house_info"]["new_house_value"]
    house_networth_future = report_data["house_info"]["house_networth_future"]
    total_employee_stockplan = report_data["calculated_data"]["total_employee_stockplan"]
    balance_with_expenses = report_data["calculated_data"]["balance_with_expenses"]
    house_capital_investment = report_data["house_info"]["house_capital_investment"]
    future_retirement_value_contrib = report_data["calculated_data"]["future_retirement_value_contrib"]
    combined_networth_future = report_data["calculated_data"]["combined_networth_future"]

    html_content = f"""
    <div class='table-container'>
        <table>
            <tr><th>House Net worth</th><td>${new_house_value if new_house else house_networth_future:,.0f}</td></tr>
            <tr><th>House Re-Investment</th><td>${int(house_capital_investment):,}</td></tr>
            <tr><th>Stock Plan Investment Principal</th><td>${int(total_employee_stockplan):,}</td></tr>
            <tr><th>Investment Principal</th><td>${int(balance_with_expenses):,}</td></tr>
            <tr><th>Retirement Principal</th><td>${int(future_retirement_value_contrib):,}</td></tr>
            <tr><th>Net worth</th><td>${combined_networth_future:,.0f}</td></tr>
            <tr><th># of Years</th><td>{years}</td></tr>
        </table>
    </div>
    """
    return html_content

def generate_current_networth_html_table(report_data):
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
        <div class='table-container'>
            <table>
                <tr><th>House Net worth</th><td>{format_currency(house_info.get("house_net_worth", 0))}</td></tr>
                <tr><th>Investment Balance</th><td>{format_currency(config_data.get('investment_balance', 0))}</td></tr>
                <tr><th>Retirement Balance</th><td>{format_currency(config_data.get('retirement_principal', 0))}</td></tr>
                <tr><th>Combined Net worth</th><td>{format_currency(calculated_data.get("combined_networth", 0))}</td></tr>
            </table>
        </div>
    """
    return html_content

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
    <h2 id='current-net-worth-title'>Current Net Worth 
        <button type='button' class='toggle-button' onclick='toggleSectionVisibility("current-net-worth")'>Toggle</button>
    </h2>
    <div id='current-net-worth-content' class='section-content hidden'>
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

def generate_paragraph_html(data):
    """Generates HTML for a paragraph.

    Args:
        data (str): The content of the paragraph.

    Returns:
        str: The generated HTML content for the paragraph.
    """

    return f"<p>{data}</p>"

def generate_section_html(section_title, data, custom_formatter=None):
    """Generates HTML content for a section, handling different data types.

    Args:
        section_title (str): The title of the section.
        data: The data to be displayed in the section.
        custom_formatter (function, optional): A custom function to format the values.

    Returns:
        str: The generated HTML content.
    """

    html_content = f"<h3>{section_title}</h3>"

    if isinstance(data, dict) or hasattr(data, '__dict__'):
        html_content += generate_table_html(data, custom_formatter)
    else:
        html_content += generate_paragraph_html(data)

    return html_content

def generate_html(report_data):
    excluded_sections = ["current_house", "school_expense_coverage", "LIVING_EXPENSES", "house_info"]

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

    html_content = """
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
    """

    future_value_html = generate_future_value_html_table(report_data)
    formatted_future_title = format_key("Future Value")
    html_content += f"<h2>{escape(formatted_future_title)} <button type='button' class='toggle-button' onclick='toggleSectionVisibility(\"future-value\")'>Toggle</button></h2>"
    html_content += f"<div id='future-value-content' class='section-content hidden'>{future_value_html}</div>"

    living_expenses_html = generate_section_html("Scenario", report_data["calculated_data"]["LIVING_EXPENSES"])
    formatted_living_expenses_title = format_key("Scenario")
    html_content += f"<h2>{escape(formatted_living_expenses_title)} <button type='button' class='toggle-button' onclick='toggleSectionVisibility(\"living-expenses\")'>Toggle</button></h2>"
    html_content += f"<div id='living-expenses-content' class='section-content hidden'>{living_expenses_html}</div>"

    for section_title, data in report_data.items():
        if section_title not in excluded_sections:
            section_class = section_title.replace('_', '-')
            formatted_section_title = format_key(section_title)
            html_content += f"<h2>{escape(formatted_section_title)} <button type='button' class='toggle-button' onclick='toggleSectionVisibility(\"{section_class}\")'>Toggle</button></h2>"
            formatted_data = format_data(data)
            html_content += f"<div id='{section_class}-content' class='section-content hidden'>{formatted_data}</div>"

    html_content += generate_current_networth_html(report_data)

    school_expense_coverage_html = generate_school_expense_coverage_html(report_data["calculated_data"]["school_expense_coverage"])
    html_content += school_expense_coverage_html

    house_info_html = generate_section_html("House Info", report_data["house_info"])
    formatted_house_info_title = format_key("House Info")
    html_content += f"<h2>{escape(formatted_house_info_title)} <button type='button' class='toggle-button' onclick='toggleSectionVisibility(\"house-info\")'>Toggle</button></h2>"
    html_content += f"<div id='house-info-content' class='section-content hidden'>{house_info_html}</div>"

    current_house_html = generate_current_house_html(report_data["current_house"])
    html_content += current_house_html

    html_content += """
    </body>
    </html>
    """
    return html_content

def generate_summary_report_html(summary_report_data):
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
        <div class='header-container'>
    """

    # Loop through summary data and populate report content
    for scenario_name, scenario_data in summary_report_data.items():
        scenario_id = scenario_name.replace(" ", "-").lower()
        assumption_description = scenario_data.get("assumption_description", "")
        description_detail = scenario_data.get("description_detail", "")
        html_content += f"""
            <div class='header'>
                <h2 id='{scenario_id}-title'>{escape(assumption_description)}</h2>
                <div id='{scenario_id}-content' class='section-content'>
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
                            {scenario_data["living_expenses_location"]}
                            {scenario_data["school_expenses"]}
                        </div>
                        <div>
                            <h3>School</h3>
                            {scenario_data["school_expenses_table_html"]}
                        </div>
                    </div>
                </div>
            </div>
        """

    html_content += """
        </div> <!-- End of header-container -->
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
    """Generates HTML table content for a child's educational expenses in a nested structure.

    Args:
        child_data (dict): A dictionary containing child information.
        table_class (str, optional): The CSS class to apply to the table.
        headers (list, optional): A list of column headers for the table.

    Returns:
        str: The generated HTML table content.
    """

    html_content = f"<table class='{table_class}'>\n"
    html_content += "<thead>\n"
    # html_content += "<tr><th>Child</th></tr>\n"
    html_content += "</thead>\n"
    html_content += "<tbody>\n"

    for child in child_data.get("children", []):
        html_content += f"<tr><td>{escape(child['name'])}</td></tr>\n"
        html_content += "<tr><td colspan='2'><table><thead><tr><th>School Type</th><th>Year</th><th>Cost</th></tr></thead><tbody>"

        school_data = child.get("school", {})
        
        # Combine all entries across school types into one list
        combined_entries = []
        for school_type, entries in school_data.items():
            for entry in entries:
                # Attach school type to each entry for display
                combined_entries.append({
                    'school_type': school_type,
                    'year': int(entry['year']),
                    'cost': entry['cost']
                })
        
        # Sort all combined entries by year
        sorted_entries = sorted(combined_entries, key=lambda entry: entry['year'])

        for entry in sorted_entries:
            year = escape(str(entry['year']))  # Convert back to string for HTML
            cost = format_currency(entry['cost'])  # Format cost for readability
            school_type = escape(entry['school_type'])
            html_content += f"<tr><td>{school_type}</td><td>{year}</td><td>{cost}</td></tr>\n"

        html_content += "</tbody></table></td></tr>\n"

    html_content += "</tbody>\n"
    html_content += "</table>\n"
    return html_content