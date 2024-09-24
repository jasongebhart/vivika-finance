import sys
import investment_module
import report_html_generator
from pathlib import Path
import logging

def main():
    log_dir = investment_module.create_log_directory()
    investment_module.setup_logging(log_dir, "getfinance.log")
    logging.info("Logging setup completed successfully.")

    logging.info("Starting script execution.")
    args = investment_module.parse_arguments()

    logging.info(f"Arguments received: {args}")
    input_file = Path(args.config_file_path)

    if not input_file.exists():
        print(f"File {input_file} does not exist.")
        return

    # Load the configuration data and general configuration data
    scenarios_data, general_config = investment_module.parse_and_load_config()
    # logging.info(f"Scenarios Data: {scenarios_data}")
    # logging.info(f"General Config: {general_config}")


    # Check if the input is a sequence or a direct scenario
    if not "sequence" in input_file.stem:
        # If it's a direct scenario, add default values and merge with general_config
        scenarios_data["selected_scenarios"] = [input_file.stem]

        # Merge missing values from general_config into scenarios_data
        for key, value in general_config.items():
            if key not in scenarios_data:
                scenarios_data[key] = value
                logging.debug(f"Adding '{key}' from general_config to scenarios_data with value: {value}")
            else:
                logging.debug(f"Key '{key}' already exists in scenarios_data with value: {scenarios_data[key]}")

    # No need to call `prepare_scenarios_data` anymore since we've handled the data merging above

    reports_dir = investment_module.create_reports_directory()
    report_name_prefix = "scenario_"

    summary_report_data = {}

    for scenario_name in scenarios_data["selected_scenarios"]:
        try:
            summary_data = investment_module.process_scenario(scenario_name, scenarios_data, reports_dir, scenarios_dir="scenarios")

            if not summary_data:
                logging.error(f"No summary data returned for scenario: {scenario_name}")
                continue

            summary_report_data[scenario_name] = summary_data

        except Exception as e:
            logging.error(f"Failed to process scenario {scenario_name}: {e}")

    if not summary_report_data:
        logging.error("No valid scenario data to generate the report.")
        return

    if "sequence" in input_file.stem and "report_name" in scenarios_data:
        report_name = scenarios_data["report_name"]
    else:
        report_name = f"{report_name_prefix}{scenarios_data['selected_scenarios'][0]}" if len(scenarios_data['selected_scenarios']) == 1 else "summary_report"

    summary_report_html = report_html_generator.generate_summary_report_html(summary_report_data)

    summary_report_filename = reports_dir / f"{report_name}.html"
    with summary_report_filename.open('w', encoding='utf-8') as summary_file:
        summary_file.write(summary_report_html)


    print(f"Summary report generated successfully. See: {summary_report_filename}")

if __name__ == "__main__":
    main()
