import sys
import investment_module
import report_html_generator
from pathlib import Path
import logging
import json  # Import JSON module

def main():
    investment_module.setup_logging()
    logging.info("Starting script execution.")

    args = investment_module.handle_arguments()

    input_file = Path(args.config_file_path)
    if not input_file.exists():
        investment_module.exit_script_with_message(f"File {input_file} does not exist.", log_message="Missing input file.")

    scenarios_data, general_config = investment_module.load_configuration()
    reports_dir = investment_module.create_reports_directory()
    # report_name = investment_module.determine_report_name(scenarios_data, input_file)
    # Call the function with input_file as an argument
    investment_module.process_scenarios(input_file, scenarios_data, general_config, reports_dir)


    logging.info(f"Generating HTML report for scenarios: {', '.join(scenarios_data['selected_scenarios'])}")
    # investment_module.generate_report(scenarios_data, scenario_name)

    logging.info(f"Summary report successfully generated.")

if __name__ == "__main__":
    main()