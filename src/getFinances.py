import sys
import investment_module
import report_html_generator
from pathlib import Path
import logging
import utils

def main():
    """Main entry point of the script."""
    try:
        args = utils.handle_arguments()
        input_file = Path(args.config_file_path)
        logs_dir = utils.LOGS_DIR.resolve()
        scenario_log_file_name = logs_dir / f"{input_file.stem}.log"

        # Load the logging level from the configuration
        logging_level = utils.load_logging_level()  # Assume you have a function to get this

        utils.setup_logging(main_log_file=None, scenario_log_file=scenario_log_file_name, log_dir=logs_dir, log_level=logging_level)

        validate_input_file(input_file)
        
        scenarios_data, general_config = investment_module.load_configuration()
        reports_dir = investment_module.create_reports_directory()

        validate_reports_directory(reports_dir)

        process_scenarios(input_file, scenarios_data, general_config, reports_dir)

    except Exception as e:
        handle_error(e)

def validate_input_file(input_file: Path):
    """Validate the existence of the input file."""
    if not input_file.exists():
        logging.error("Missing input file.")
        print(f"File {input_file} does not exist.")
        sys.exit(1)

def validate_reports_directory(reports_dir: Path):
    """Validate the reports directory."""
    if not reports_dir:
        logging.error(f"Failed to create or locate reports directory: {reports_dir}")
        sys.exit(1)

def process_scenarios(input_file: Path, scenarios_data: dict, general_config: dict, reports_dir: Path):
    """Process the scenarios and generate the report."""
    investment_module.process_scenarios(input_file, scenarios_data, general_config, reports_dir)
    logging.info(f"Generating HTML report for scenarios: {', '.join(scenarios_data['selected_scenarios'])}")
    logging.info("Summary report successfully generated.")

def handle_error(error: Exception):
    """Log and exit on error."""
    logging.error(f"An error occurred: {error}", exc_info=True)
    sys.exit(1)  # Exit with error code 1 to indicate failure

if __name__ == "__main__":
    main()
