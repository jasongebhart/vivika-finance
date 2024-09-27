import os
import subprocess
import json  # Import the JSON module
from pathlib import Path
import report_html_generator
import logging

# Setup logging configuration
config_path = './config.json'
with open(config_path, 'r') as f:
    config = json.load(f)

json_dir = config.get('json_dir', '../scenarios')
reports_dir = Path(config.get('reports_dir', '../reports')).resolve()
logs_dir = Path(config.get('logs_dir', '../logs')).resolve()
excluded_files = set(config.get('excluded_files', []))

# Configure logging to write to the specified logs directory
logs_dir.mkdir(parents=True, exist_ok=True)
log_file = logs_dir / 'generate_reports.log'
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

logging.info(f"Resolved reports directory: {reports_dir}")
logging.info(f"Resolved logs directory: {logs_dir}")

# Get a list of all JSON files in the directory
all_json_files = os.listdir(json_dir)

# Filter the files, excluding those that start with 'seq' and the excluded files
json_files = [
    f for f in all_json_files
    if f.endswith('.json') and f not in excluded_files and not f.startswith('seq')
]

# JSON Validation Function
def validate_json(json_file_path):
    """Validate the JSON file before running the report."""
    try:
        with open(json_file_path, 'r') as file:
            json.load(file)
        return True  # JSON is valid
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in {json_file_path}: {e}")
        return False  # JSON is invalid

# Run the report for each valid JSON file
for json_file in json_files:
    json_file_path = os.path.join(json_dir, json_file)
    
    # Validate JSON before proceeding
    if not validate_json(json_file_path):
        logging.error(f"Skipping invalid JSON file: {json_file_path}")
        continue  # Skip this file if the JSON is invalid

    logging.info(f"Running report for {json_file_path}")
    
    # Run the getFinances.py command for each JSON file
    result = subprocess.run(['python', 'getFinances.py', json_file_path], capture_output=True, text=True)
    
    if result.returncode != 0:
        logging.error(f"Error generating report for {json_file_path}: {result.stderr}")

# Get the HTML files generated in the reports directory
html_files = report_html_generator.get_html_files(reports_dir)

# Organize content and generate navigation
toc_content = report_html_generator.organize_content(html_files, reports_dir)

# Generate and write the index.html file
index_content = report_html_generator.generate_html_structure(toc_content)
report_html_generator.write_html_to_file(os.path.join(reports_dir, "index.html"), index_content)
logging.info(f"Index generated: {reports_dir / 'index.html'}")

# Inject navigation into each scenario report
for html_file in html_files:
    file_path = os.path.join(reports_dir, html_file)
    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()

    # Assuming you want to insert the navigation at a specific point in the HTML
    updated_content = file_content.replace("<!-- INSERT NAVIGATION HERE -->", report_html_generator.generate_navigation(toc_content))

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)
    logging.info(f"Updated navigation in: {file_path}")

logging.info("Reports generation completed. Check the reports directory for generated reports.")
