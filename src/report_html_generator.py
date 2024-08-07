from utils import format_currency
from html import escape

def format_key(key):
    import re
    # Convert camel case or underscore-separated words to space-separated words
    formatted_key = re.sub(r'(?<!^)(?=[A-Z][a-z])|_', ' ', key)
    # Capitalize the first letter of each word
    formatted_key = ' '.join(word.capitalize() for word in formatted_key.split())
    return formatted_key

def generate_school_expense_coverage_html(data):
    html = """
    <h2 id='school-expense-coverage-title'>School Expense Coverage 
        <button type='button' class='toggle-button' onclick='toggleSectionVisibility("school-expense-coverage")'>Toggle</button>
    </h2>
    <div id='school-expense-coverage-content' class='section-content hidden'>
        <div class='table-container'>
            <table>
                <tr><th>Grade</th><th>Coverage</th><th>Expenses Covered</th><th>Remaining Expenses</th></tr>
    """
    for row in data:
        grade, coverage, expenses_covered, remaining_expenses = row
        html += f"<tr><td>{grade}</td><td>{'Yes' if coverage else 'No'}</td><td>${expenses_covered:,}</td><td>${remaining_expenses:,}</td></tr>"
    html += """
            </table>
        </div>
    </div>
    """
    return html


def generate_current_house_html(current_house):
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

def generate_section_html(section_title, data):
    html_content = ""
    if isinstance(data, dict):
        html_content += "<div class='table-container'><table>"
        for key, value in data.items():
            html_content += f"<tr><th>{key}</th><td>{value}</td></tr>"
        html_content += "</table></div>"
    elif hasattr(data, '__dict__'):
        html_content += "<div class='table-container'><table>"
        for attr, value in data.__dict__.items():
            html_content += f"<tr><th>{attr}</th><td>{value}</td></tr>"
        html_content += "</table></div>"
    else:
        html_content += f"<p>{data}</p>"
    return html_content

def safe_int_conversion(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return value  # or return 0, or any other default value


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
        html_content += f"""
            <div class='header'>
                <h2 id='{scenario_id}-title'>{escape(assumption_description)}</h2>
                <div id='{scenario_id}-content' class='section-content'>
                    <div class='table-container'>
                        <div>
                            <h3>Scenario</h3>
                            {scenario_data["living_expenses_location"]}
                        </div>
                        <div>
                            <h3>Future Value</h3>
                            {scenario_data["future_value"]}
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

