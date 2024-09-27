import os
from pathlib import Path
import subprocess
import json  # Import the JSON module
from report_html_generator import generate_index  # Adjust the import based on where your function is defined

# Directory containing the JSON scenario files
json_dir = '../scenarios'

# Files to exclude
excluded_files = {'general.finance.json', 'all.json', 'override.json'}

# Get a list of all JSON files in the directory
all_json_files = os.listdir(json_dir)

# Filter the files, excluding those that start with 'scenario_seq' and the excluded files
json_files = [
    f for f in all_json_files
    if f.endswith('.json') and f not in excluded_files and not f.startswith('seq')
]

# # Run the report for each JSON file
# for json_file in json_files:
#     json_file_path = os.path.join(json_dir, json_file)
#     print(f"Running report for {json_file_path}")
    
#     # Run the getFinances.py command for each JSON file
#     subprocess.run(['python', 'getFinances.py', json_file_path])


# Resolve the absolute path for 'reports'
reports_dir = Path('../reports').resolve()
print(f"Resolved reports directory: {reports_dir}")

# Generate the index with the resolved absolute path
generate_index(reports_dir)