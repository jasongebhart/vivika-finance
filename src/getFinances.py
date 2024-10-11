import sys
import investment_module
import report_html_generator
from pathlib import Path
import logging
import json  # Import JSON module
from utils import LOGS_DIR

def main():
    try:
        # Extract scenario name from input file path or arguments
        args = investment_module.handle_arguments()
        input_file = Path(args.config_file_path)

        # Extract the scenario name from the input file
        scenario_name = input_file.stem  # Filename without extension

        # Create scenario log file name using LOGS_DIR
        scenario_log_file_name = LOGS_DIR / f"{scenario_name}.log"
    
        # Setup logging
        investment_module.setup_logging(scenario_log_file=scenario_log_file_name, log_dir=LOGS_DIR, log_level=logging.DEBUG)

        logging.info("Starting script execution.")

        if not input_file.exists():
            investment_module.exit_script_with_message(f"File {input_file} does not exist.", log_message="Missing input file.")

        # Load scenarios data and configuration
        scenarios_data, general_config = investment_module.load_configuration()
        reports_dir = investment_module.create_reports_directory()

        # Verify reports_dir is valid
        if not reports_dir:
            logging.error(f"Failed to create or locate reports directory: {reports_dir}")
            sys.exit(1)

        # Process scenarios
        investment_module.process_scenarios(input_file, scenarios_data, general_config, reports_dir)

        logging.info(f"Generating HTML report for scenarios: {', '.join(scenarios_data['selected_scenarios'])}")
        logging.info("Summary report successfully generated.")

    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
        sys.exit(1)  # Exit with error code 1 to indicate failure

if __name__ == "__main__":
    main()
