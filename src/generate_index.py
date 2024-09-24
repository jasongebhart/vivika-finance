import os
from collections import defaultdict

# Directory containing the HTML files (change this to your reports directory)
reports_dir = '../reports'

# Output file (the index page)
index_file = os.path.join(reports_dir, 'index.html')

# Location abbreviation mapping
location_map = {
    'sf': 'San Francisco',
    'ny': 'New York',
    'mn': 'Minnesota',
}

# Get a list of all HTML files in the directory that start with "summary_" or "scenario_"
html_files = [f for f in os.listdir(reports_dir) if f.endswith('.html') and (f.startswith('summary_') or f.startswith('scenario_'))]

# Helper function to create readable titles from filenames, excluding names and work statuses
def make_title_from_filename(filename):
    if filename.startswith('summary_'):
        filename = filename.replace('summary_', '').replace('.html', '')
    elif filename.startswith('scenario_'):
        filename = filename.replace('scenario_', '').replace('.html', '')

    parts = filename.split('_')

    location = location_map.get(parts[0], parts[0].capitalize())
    
    # Rent and school status if they exist
    rent_status = parts[4].capitalize() if len(parts) > 4 else ""
    school_status = parts[5].capitalize() if len(parts) > 5 else ""

    # Any unrecognized parts are treated as additional suffixes and included in the title
    suffixes = " ".join(parts[6:]).capitalize() if len(parts) > 6 else ""

    # Construct title excluding names and work statuses, but including other suffixes
    title = f"{location}"
    if rent_status:
        title += f", {rent_status}"
    if school_status:
        title += f", {school_status}"
    if suffixes:
        title += f", {suffixes}"

    return title

def get_human_readable_status(name1, name2, status1, status2):
    if status1 == status2:
        return f"{name1} & {name2} {status1}"
    else:
        return f"{name1} ({status1}) & {name2} ({status2})"

def get_status_key_from_filename(filename):
    # Remove any prefixes like 'scenario_' or 'summary_' before processing
    if filename.startswith('scenario_'):
        filename = filename.replace('scenario_', '')
    elif filename.startswith('summary_'):
        filename = filename.replace('summary_', '')

    # Split the filename into parts
    parts = filename.split('_')
    
    # Check if there are enough parts to extract the status
    if len(parts) >= 4:
        name1 = parts[1].capitalize()
        name2 = parts[2].capitalize()

        # Work status is the 4th part, which might look like 'retired-retired'
        work_status_part = parts[3]

        # Split the work status into two statuses
        statuses = work_status_part.split('-')

        # Check if both status1 and status2 exist
        if len(statuses) == 2:
            status1 = statuses[0].capitalize()
            status2 = statuses[1].capitalize()
            return get_human_readable_status(name1, name2, status1, status2)
        elif len(statuses) == 1:
            status1 = statuses[0].capitalize()
            return f"{name1} ({status1}) and {name2} (Unknown)"
    return "Unknown"

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
    <ul>
"""

# Add each HTML file with a descriptive title
for html_file in html_files:
    title = make_title_from_filename(html_file)
    html_content += f'<li><a href="{html_file}">{title}</a></li>\n'

html_content += """
    </ul>
</body>
</html>
"""

with open(index_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Index file generated: {index_file}")

# Create a dictionary to group HTML files by their work status
grouped_files = defaultdict(list)
for html_file in html_files:
    status_key = get_status_key_from_filename(html_file)
    grouped_files[status_key].append(html_file)

# Now modify each report file to add the <aside> navigation while preserving the main content
for html_file in html_files:
    report_file_path = os.path.join(reports_dir, html_file)

    with open(report_file_path, 'r', encoding='utf-8') as file:
        original_content = file.read()

    if '</body>' in original_content:
        aside_content = """
        <aside class='index-navigation'>
            <h2>Other Reports</h2>
            <nav>
        """

        # Add links grouped by work status
        for status_group, files_in_group in grouped_files.items():
            aside_content += f"<h3>{status_group}</h3>\n<ul>\n"
            for other_file in files_in_group:
                title = make_title_from_filename(other_file)
                
                # Check if it's the active report and apply 'active' class
                if other_file == html_file:
                    aside_content += f'<li><a href="{other_file}" class="active">{title}</a></li>\n'
                else:
                    aside_content += f'<li><a href="{other_file}">{title}</a></li>\n'
            aside_content += "</ul>\n"

        aside_content += """
            </nav>
        </aside>
        """

        updated_content = original_content.replace('</body>', f'{aside_content}\n</body>')

        with open(report_file_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)

        print(f"Updated report file: {report_file_path}")
