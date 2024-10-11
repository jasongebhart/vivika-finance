import os
import subprocess
import json
from pathlib import Path
import investment_module
import report_html_generator
import logging
import concurrent.futures  # For parallel execution
from utils import LOGS_DIR

def validate_json(json_file_path):
    """Validate the JSON file before running the report."""
    try:
        with open(json_file_path, 'r') as file:
            json.load(file)
        return True  # JSON is valid
    except FileNotFoundError:
        logging.error(f"File not found: {json_file_path}")
        return False  # JSON is invalid
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in {json_file_path}: {e}")
        return False  # JSON is invalid
    except Exception as e:
        logging.error(f"Unexpected error while validating JSON in {json_file_path}: {e}")
        return False

def run_report_for_json(json_file_path):
    """Runs getFinances.py for the given JSON file."""
    logging.info(f"Running report for {json_file_path}")
    try:
        result = subprocess.run(['python', 'getFinances.py', str(json_file_path)], capture_output=True, text=True)

        if result.returncode != 0:
            logging.error(f"Error generating report for {json_file_path}: {result.stderr}")
        else:
            logging.info(f"Successfully generated report for {json_file_path}")
    except Exception as e:
        logging.error(f"Failed to run report for {json_file_path}: {e}")

def main():
    # Load config from JSON
    config_path = Path('./config.json')
    try:
        with config_path.open('r') as f:
            config = json.load(f)
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {config_path}")
        return
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in configuration file: {e}")
        return
    except Exception as e:
        logging.error(f"Unexpected error while loading configuration: {e}")
        return

    # Setup directories
    json_dir = Path(config.get('json_dir', '../scenarios')).resolve()
    reports_dir = Path(config.get('reports_dir', '../reports')).resolve()
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Configure logging
    investment_module.setup_logging()

    logging.info(f"Resolved reports directory: {reports_dir}")
    logging.info(f"Resolved logs directory: {LOGS_DIR}")

    # Get a list of JSON files, excluding those starting with 'seq' and the excluded ones
    excluded_files = set(config.get('excluded_files', []))
    json_files = [
        f for f in json_dir.iterdir()
        if f.suffix == '.json' and f.name not in excluded_files and not f.name.startswith('seq')
    ]

    # Validate JSON and run reports in parallel
    valid_json_files = [f for f in json_files if validate_json(f)]
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(run_report_for_json, valid_json_files)

    # Generate the HTML files in the reports directory
    html_files = report_html_generator.get_html_files(reports_dir)

    # Organize content and generate navigation
    toc_content = report_html_generator.organize_content(html_files, reports_dir)

    # Generate and write the index.html file
    index_content = report_html_generator.generate_html_structure(toc_content)
    report_html_generator.write_html_to_file(reports_dir / "index.html", index_content)
    logging.info(f"Index generated: {reports_dir / 'index.html'}")

    # Inject navigation into each scenario report
    for html_file in html_files:
        file_path = reports_dir / html_file
        with file_path.open('r', encoding='utf-8') as file:
            file_content = file.read()

        updated_content = file_content.replace("<!-- INSERT NAVIGATION HERE -->", 
                                                report_html_generator.generate_navigation(toc_content))

        with file_path.open('w', encoding='utf-8') as file:
            file.write(updated_content)
        logging.info(f"Updated navigation in: {file_path}")

    logging.info("Reports generation completed. Check the reports directory for generated reports.")

if __name__ == "__main__":
    main()
