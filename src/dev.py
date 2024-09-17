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

    html_content += """
        </div> <!-- End of header-container -->
    </body>
    </html>
    """
    return html_content


def generate_retirement_table(retirement_data, table_class="retirement-table"):
    """Generates HTML table content for retirement contributions and accounts.

    Args:
        retirement_data (list): A list containing retirement data for each person.
        table_class (str, optional): The CSS class to apply to the table.

    Returns:
        str: The generated HTML table content.
    """

    html_content = f"<table class='{table_class}'>\n"
    html_content += "<thead>\n"
    html_content += "<tr><th>Parent Name</th></tr>\n"
    html_content += "</thead>\n"
    html_content += "<tbody>\n"

    # Iterate through each parent in the retirement data
    for parent in retirement_data:
        html_content += f"<tr><td>{escape(parent['name'])}</td></tr>\n"

        # Generate table for contributions
        html_content += "<tr><td><h3>Contributions</h3></td></tr>\n"
        html_content += "<tr><td colspan='2'><table><thead><tr><th>Type</th><th>Contribution</th><th>Amount</th></tr></thead><tbody>"

        contributions_data = parent.get("contributions", {})
        for contribution_type, entries in contributions_data.items():
            for entry in entries:
                for contribution, amount in entry.items():
                    html_content += f"<tr><td>{escape(contribution_type)}</td><td>{escape(contribution)}</td><td>{amount}</td></tr>\n"

        html_content += "</tbody></table></td></tr>\n"

        # Generate table for accounts
        html_content += "<tr><td><h3>Accounts</h3></td></tr>\n"
        html_content += "<tr><td colspan='2'><table><thead><tr><th>Account Type</th><th>Account Name</th><th>Balance</th></tr></thead><tbody>"

        accounts_data = parent.get("accounts", {})
        for account_type, entries in accounts_data.items():
            for entry in entries:
                for account_name, balance in entry.items():
                    html_content += f"<tr><td>{escape(account_type)}</td><td>{escape(account_name)}</td><td>{balance}</td></tr>\n"

        html_content += "</tbody></table></td></tr>\n"

    html_content += "</tbody>\n"
    html_content += "</table>\n"
    return html_content


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
    report_html = generate_html(config_data)
    report_html_filename = reports_dir / "dev_report.html"
    with report_html_filename.open('w') as report_file:
        report_file.write(report_html)

        

if __name__ == "__main__":
    main()