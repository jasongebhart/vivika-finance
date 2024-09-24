import os
import subprocess

# Directory containing the JSON scenario files
json_dir = '../scenarios'

# Files to exclude
excluded_files = {'general.finance.json', 'all.json', 'override.json'}

# Get a list of all JSON files in the directory
all_json_files = os.listdir(json_dir)
# print("All JSON files:", all_json_files)  # Debugging print

# Filter the files, excluding those that start with 'scenario_seq' and the excluded files
json_files = [
    f for f in all_json_files
    if f.endswith('.json') and f not in excluded_files and not f.startswith('seq')
]

# print("Filtered JSON files:", json_files)  # Debugging print

# Run the report for each JSON file
for json_file in json_files:
    json_file_path = os.path.join(json_dir, json_file)
    print(f"Running report for {json_file_path}")
    
    # Run the getFinances.py command for each JSON file
    subprocess.run(['python', 'getFinances.py', json_file_path])

