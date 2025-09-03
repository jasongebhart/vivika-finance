import os
import subprocess
import json
from pathlib import Path
import logging
import concurrent.futures

# Try to import with relative paths for Flask app
try:
    # from .investment_module import some_function  # Replace `some_function` with actual functions you need
    from .report_html_generator import generate_html_structure
    from .utils import format_currency
except ImportError:
    # Fallback to absolute import if running as a standalone script
    import investment_module
    import report_html_generator
    import utils


# Define constants for magic strings
GET_FINANCES_SCRIPT = Path('src/getFinances.py')
INDEX_FILE = 'index.html'
NAVIGATION_PLACEHOLDER = "<!-- INSERT NAVIGATION HERE -->"
JSON_SUFFIX = '.json'
EXCLUDED_PREFIX = 'seq'

class ConfigurationError(Exception):
    """Custom exception for configuration errors."""
    pass

def validate_json(json_file_path: Path) -> bool:
    """Validate the JSON file before running the report."""
    if not json_file_path.is_file():
        logging.error(f"File not found: {json_file_path}")
        return False

    try:
        with json_file_path.open('r') as file:
            json.load(file)
        return True  # JSON is valid
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in {json_file_path}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error while validating JSON in {json_file_path}: {e}")
    return False  # JSON is invalid

def run_report_for_json(json_file_path: Path):
    """Runs getFinances.py for the given JSON file."""
    logging.info(f"Running report for {json_file_path}")
    try:
        result = subprocess.run(['python', str(GET_FINANCES_SCRIPT), str(json_file_path)], capture_output=True, text=True)

        if result.returncode != 0:
            logging.error(f"Error generating report for {json_file_path}: {result.stderr}")
        else:
            logging.info(f"Successfully generated report for {json_file_path}")
    except Exception as e:
        logging.error(f"Failed to run report for {json_file_path}: {e}")

def load_configuration(config_path: Path) -> dict:
    """Load configuration from the JSON file."""
    if not config_path.is_file():
        logging.error(f"Configuration file not found: {config_path}")
        raise ConfigurationError(f"Configuration file not found: {config_path}")

    try:
        with config_path.open('r') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in configuration file: {e}")
        raise ConfigurationError(f"Invalid JSON in configuration file: {e}")
    except Exception as e:
        logging.error(f"Unexpected error while loading configuration: {e}")
        raise ConfigurationError(f"Unexpected error while loading configuration: {e}")

def setup_directories(json_dir: Path, reports_dir: Path):
    """Setup required directories."""
    json_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    utils.LOGS_DIR.mkdir(parents=True, exist_ok=True)

def get_valid_json_files(json_dir: Path, excluded_files: set) -> list:
    """Get a list of valid JSON files."""
    return [
        f for f in json_dir.iterdir()
        if f.suffix == JSON_SUFFIX and f.name not in excluded_files and not f.name.startswith(EXCLUDED_PREFIX)
    ]

def update_navigation_in_reports(html_files: list, reports_dir: Path, toc_content: dict, config):
    """Inject navigation into each scenario report."""
    for html_file in html_files:
        file_path = reports_dir / html_file
        with file_path.open('r', encoding='utf-8') as file:
            file_content = file.read()

        updated_content = file_content.replace(NAVIGATION_PLACEHOLDER, 
                                                report_html_generator.generate_navigation(toc_content, config))

        with file_path.open('w', encoding='utf-8') as file:
            file.write(updated_content)
        logging.info(f"Updated navigation in: {file_path}")

def main():
    """Main entry point of the script."""
    config_path = Path('./src/config.json')

    try:
        config = load_configuration(config_path)
    except ConfigurationError:
        return  # Exit if config loading failed

    # Setup directories
    json_dir = Path(config.get('json_dir', './scenarios')).resolve()
    reports_dir = Path(config.get('reports_dir', './reports')).resolve()
    setup_directories(json_dir, reports_dir)

    # Configure logging using utils
    logging_level = config.get('logging_level', 'INFO')  # Default to INFO if not specified
    utils.setup_logging(main_log_file="generate_reports.log", scenario_log_file=None, log_dir=utils.LOGS_DIR, log_level=logging_level)

    logging.info(f"Resolved reports directory: {reports_dir}")
    logging.info(f"Resolved logs directory: {utils.LOGS_DIR.resolve()}")

    # Get a list of JSON files, excluding those starting with 'seq' and the excluded ones
    excluded_files = set(config.get('excluded_files', []))
    json_files = get_valid_json_files(json_dir, excluded_files)

    # Validate JSON and run reports in parallel
    valid_json_files = [f for f in json_files if validate_json(f)]
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(run_report_for_json, valid_json_files)

    # Generate the HTML files in the reports directory
    html_files = report_html_generator.get_html_files(reports_dir)

    # Organize content and generate navigation
    toc_content = report_html_generator.organize_content(html_files, reports_dir, config)

    # Generate the navigation HTML
    navigation_html = report_html_generator.generate_navigation(toc_content, config)

    # Generate and write the index.html file
    index_content = report_html_generator.generate_html_structure(toc_content, config)
    index_content_with_navigation = index_content.replace(NAVIGATION_PLACEHOLDER, navigation_html)

    # report_html_generator.write_html_to_file(reports_dir / INDEX_FILE, index_content)
    report_html_generator.write_html_to_file(reports_dir / INDEX_FILE, index_content_with_navigation)
    logging.info(f"Index generated: {reports_dir / INDEX_FILE}")

    # Inject navigation into each scenario report
    update_navigation_in_reports(html_files, reports_dir, toc_content, config)

    logging.info("Reports generation completed. Check the reports directory for generated reports.")

if __name__ == "__main__":
    main()
