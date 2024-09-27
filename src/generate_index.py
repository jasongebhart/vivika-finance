import os
from collections import defaultdict
from bs4 import BeautifulSoup

# Directory containing the HTML files
reports_dir = '../reports'

# Output file (the index page)
index_file = os.path.join(reports_dir, 'index.html')

# Helper function to extract key attributes from filenames
def extract_attributes_from_filename(filename):
    filename = filename.replace('summary_', '').replace('scenario_', '').replace('.html', '')
    parts = filename.split('_')
    
    # Create a more descriptive name with proper formatting
    names = parts[1].replace('-', ' & ').capitalize()  # Example: "Hav & Jason"
    work_status = parts[2].replace('-', ' ').capitalize()  # Example: "Retired" or "Work"
    
    # Simplify names for the aside
    location = parts[0].replace('sf', 'San Francisco').replace('mn', 'Minnesota').capitalize()  # Map as needed
    ownership = parts[3].replace('public', 'Public').replace('own', 'Own').replace('private', 'Private').capitalize()
    
    simplified_name = f"{location}, {ownership}"
    
    return names, work_status, simplified_name

# Get a list of all HTML files in the directory
html_files = [f for f in os.listdir(reports_dir) if f.endswith('.html') and (f.startswith('summary_') or f.startswith('scenario_'))]

# Helper function to check the viability status
def check_viability_status(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    status_element = soup.find('h4', class_='scenario-status')
    if status_element:
        return 'viable' if 'viable' in status_element.get('class', []) else 'not-viable'
    return 'unknown'

# Group files by viability and work status
file_groups = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))  # Nested defaultdict

# Process each HTML file
for html_file in html_files:
    file_path = os.path.join(reports_dir, html_file)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    viability_status = check_viability_status(content)
    names, work_status, simplified_name = extract_attributes_from_filename(html_file)
    
    # Create a composite key for names and work status
    key = f"{names} {work_status}"
    
    # Add files to the corresponding group
    file_groups[viability_status][key][simplified_name].append(html_file)

# Generate the index.html
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Financial Scenarios and Reports Index</title>
    <link rel="stylesheet" href="./static/css/styles.css">
</head>
<body>
    <h1>Overview of Financial Scenarios and Reports</h1>
"""

# Viable section
html_content += "<h2>Viable Scenarios</h2>\n"
if file_groups['viable']:
    html_content += "<ul>\n"
    for work_key, simplified_group in file_groups['viable'].items():
        html_content += f"<li><strong>{work_key}</strong>\n<ul>\n"
        for simplified_name, files in simplified_group.items():
            html_content += f"<li><strong>{simplified_name}</strong>\n<ul>\n"
            for file in files:
                html_content += f'<li><a href="{file}">{file}</a></li>\n'
            html_content += "</ul></li>\n"
        html_content += "</ul></li>\n"
    html_content += "</ul>\n"
else:
    html_content += "<p>No viable scenarios found.</p>\n"

# Not-viable section
html_content += "<h2>Not Viable Scenarios</h2>\n"
if file_groups['not-viable']:
    html_content += "<ul>\n"
    for work_key, simplified_group in file_groups['not-viable'].items():
        html_content += f"<li><strong>{work_key}</strong>\n<ul>\n"
        for simplified_name, files in simplified_group.items():
            html_content += f"<li><strong>{simplified_name}</strong>\n<ul>\n"
            for file in files:
                html_content += f'<li><a href="{file}">{file}</a></li>\n'
            html_content += "</ul></li>\n"
        html_content += "</ul></li>\n"
    html_content += "</ul>\n"
else:
    html_content += "<p>No not-viable scenarios found.</p>\n"

html_content += """
</body>
</html>
"""

# Write the generated index content to the file
with open(index_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Index file generated: {index_file}")

# Add separate <aside> sections to individual HTML files
for html_file in html_files:
    report_file_path = os.path.join(reports_dir, html_file)
    
    with open(report_file_path, 'r', encoding='utf-8') as file:
        original_content = file.read()

    soup = BeautifulSoup(original_content, 'html.parser')
    
    # Create aside content for Viable scenarios
    viable_aside_content = "<aside class='index-navigation'>\n<h2>Viable Scenarios</h2>\n<nav>\n<ul>\n"
    for work_key, simplified_group in file_groups['viable'].items():
        viable_aside_content += f"<li><strong>{work_key}</strong>\n<ul>\n"
        for simplified_name, files in simplified_group.items():
            viable_aside_content += f"<li><strong>{simplified_name}</strong>\n<ul>\n"
            for viable_file in files:
                if viable_file == html_file:
                    viable_aside_content += f'<li><a href="{viable_file}" class="active">{viable_file}</a></li>\n'
                else:
                    viable_aside_content += f'<li><a href="{viable_file}">{viable_file}</a></li>\n'
            viable_aside_content += "</ul></li>\n"
        viable_aside_content += "</ul></li>\n"
    viable_aside_content += "</ul>\n</nav>\n</aside>\n"

    # Create aside content for Not Viable scenarios
    not_viable_aside_content = "<aside class='index-navigation'>\n<h2>Not Viable Scenarios</h2>\n<nav>\n<ul>\n"
    for work_key, simplified_group in file_groups['not-viable'].items():
        not_viable_aside_content += f"<li><strong>{work_key}</strong>\n<ul>\n"
        for simplified_name, files in simplified_group.items():
            not_viable_aside_content += f"<li><strong>{simplified_name}</strong>\n<ul>\n"
            for not_viable_file in files:
                if not_viable_file == html_file:
                    not_viable_aside_content += f'<li><a href="{not_viable_file}" class="active">{not_viable_file}</a></li>\n'
                else:
                    not_viable_aside_content += f'<li><a href="{not_viable_file}">{not_viable_file}</a></li>\n'
            not_viable_aside_content += "</ul></li>\n"
        not_viable_aside_content += "</ul></li>\n"
    not_viable_aside_content += "</ul>\n</nav>\n</aside>\n"

    # Insert aside content before </body>
    if soup.body:
        # Ensure each aside is separated properly
        aside_container = soup.new_tag('div')
        aside_container.append(BeautifulSoup(viable_aside_content, 'html.parser'))
        aside_container.append(BeautifulSoup(not_viable_aside_content, 'html.parser'))
        
        soup.body.append(aside_container)

    # Write the updated content back to the report file
    with open(report_file_path, 'w', encoding='utf-8') as file:
        file.write(str(soup))

    print(f"Updated report file: {report_file_path}")
