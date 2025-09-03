import os
from collections import defaultdict
from bs4 import BeautifulSoup, Tag
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Directory containing the HTML files
reports_dir = '../reports'

# Output file (the index page)
index_file = os.path.join(reports_dir, 'index.html')


def extract_attributes_from_filename(filename):
    """Extract key attributes like names, work status, and location from the filename."""
    filename = filename.replace('summary_', '').replace('scenario_', '').replace('.html', '')
    parts = filename.split('_')

    try:
        names = parts[1].replace('-', ' & ').capitalize()
        work_status = parts[2].replace('-', ' ').capitalize()
        location = parts[0].replace('sf', 'San Francisco').replace('mn', 'Minnesota').capitalize()
        ownership = parts[3].replace('public', 'Public').replace('own', 'Own').replace('private', 'Private').capitalize()

        simplified_name = f"{location}, {ownership}"
    except IndexError:
        logging.error(f"Filename {filename} does not follow expected naming convention.")
        return None, None, None

    return names, work_status, simplified_name


def get_html_files(directory):
    """Return a list of summary and scenario HTML files in the specified directory."""
    return [
        f for f in os.listdir(directory)
        if f.endswith('.html') and (f.startswith('summary_') or f.startswith('scenario_'))
    ]


def check_viability_status(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    status_element = soup.find('h4', class_='scenario-status')

    # Check if status_element is found
    if status_element is None:
        logging.warning("Status element not found. Returning 'unknown'.")
        return 'unknown'

    # Ensure status_element is a Tag and not a NavigableString or other type
    if isinstance(status_element, Tag):
        class_list = status_element.get('class', [])
        
        # Ensure class_list is a list before performing 'in' checks
        if isinstance(class_list, list):
            return 'viable' if 'viable' in class_list else 'not-viable' if 'not-viable' in class_list else 'unknown'
        else:
            logging.warning(f"Unexpected class attribute type: {type(class_list)}. Returning 'unknown'.")
    else:
        logging.warning(f"Unexpected element type: {type(status_element)}. Returning 'unknown'.")

    logging.warning("No recognized status class found. Returning 'unknown'.")
    return 'unknown'


def generate_index_html(file_groups):
    """Generate the main index HTML content."""
    html_template = """
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
        {viable_section}
        {not_viable_section}
    </body>
    </html>
    """
    viable_section = generate_scenario_section(file_groups['viable'], 'Viable Scenarios')
    not_viable_section = generate_scenario_section(file_groups['not-viable'], 'Not Viable Scenarios')

    return html_template.format(viable_section=viable_section, not_viable_section=not_viable_section)


def generate_scenario_section(scenario_group, section_title):
    """Generate HTML for a specific scenario section (Viable or Not Viable)."""
    if not scenario_group:
        return f"<h2>{section_title}</h2><p>No {section_title.lower()} found.</p>"

    section_html = f"<h2>{section_title}</h2><ul>\n"
    for work_key, simplified_group in scenario_group.items():
        section_html += f"<li><strong>{work_key}</strong>\n<ul>\n"
        for simplified_name, files in simplified_group.items():
            section_html += f"<li><strong>{simplified_name}</strong>\n<ul>\n"
            for file in files:
                section_html += f'<li><a href="{file}">{file}</a></li>\n'
            section_html += "</ul></li>\n"
        section_html += "</ul></li>\n"
    section_html += "</ul>\n"
    return section_html


def update_html_file(file_groups, html_file, file_path):
    """Update individual HTML files by inserting aside navigation for viable and not-viable scenarios."""
    with open(file_path, 'r', encoding='utf-8') as file:
        original_content = file.read()

    soup = BeautifulSoup(original_content, 'html.parser')

    aside_container = soup.new_tag('div')
    aside_container.append(BeautifulSoup(generate_aside_navigation(file_groups['viable'], html_file, 'Viable Scenarios'), 'html.parser'))
    aside_container.append(BeautifulSoup(generate_aside_navigation(file_groups['not-viable'], html_file, 'Not Viable Scenarios'), 'html.parser'))

    if soup.body:
        soup.body.append(aside_container)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(str(soup))
    logging.info(f"Updated report file: {file_path}")


def generate_aside_navigation(scenario_group, current_file, section_title):
    """Generate HTML aside navigation for a specific scenario group (viable or not-viable)."""
    aside_content = f"<aside class='index-navigation'>\n<h2>{section_title}</h2>\n<nav>\n<ul>\n"
    for work_key, simplified_group in scenario_group.items():
        aside_content += f"<li><strong>{work_key}</strong>\n<ul>\n"
        for simplified_name, files in simplified_group.items():
            aside_content += f"<li><strong>{simplified_name}</strong>\n<ul>\n"
            for scenario_file in files:
                class_attr = ' class="active"' if scenario_file == current_file else ''
                aside_content += f'<li><a href="{scenario_file}"{class_attr}>{scenario_file}</a></li>\n'
            aside_content += "</ul></li>\n"
        aside_content += "</ul></li>\n"
    aside_content += "</ul>\n</nav>\n</aside>\n"
    return aside_content


def main():
    """Main function to process files and generate index and asides."""
    # Get list of HTML files
    html_files = get_html_files(reports_dir)

    file_groups = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    # Process each HTML file
    for html_file in html_files:
        file_path = os.path.join(reports_dir, html_file)

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        viability_status = check_viability_status(content)
        names, work_status, simplified_name = extract_attributes_from_filename(html_file)

        if names and work_status and simplified_name:
            key = f"{names} {work_status}"
            file_groups[viability_status][key][simplified_name].append(html_file)

    # Generate the index.html file
    index_content = generate_index_html(file_groups)
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_content)
    logging.info(f"Index file generated: {index_file}")

    # Add aside sections to each HTML file
    for html_file in html_files:
        report_file_path = os.path.join(reports_dir, html_file)
        update_html_file(file_groups, html_file, report_file_path)


if __name__ == "__main__":
    main()
