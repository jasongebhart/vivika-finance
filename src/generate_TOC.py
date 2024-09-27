import os
import report_html_generator
from pathlib import Path
import report_html_generator

# Directory containing the HTML files
reports_dir = Path('../reports').resolve()

# Output file (the index page)
index_file = os.path.join(reports_dir, 'index.html')
print(f"Resolved reports directory: {reports_dir}")

html_files = report_html_generator.get_html_files(reports_dir)

if not html_files:
    print(f"No scenario HTML files found in {reports_dir}.")

toc_content = report_html_generator.organize_content(html_files, reports_dir)

navigation = report_html_generator.generate_navigation(toc_content)
# print(f"{navigation}")
title = "Financial Report Table of Contents"
index_file = os.path.join(reports_dir, 'index.html')
content = ""


# for title, content, output in scenarios:
report_html_generator.generate_scenario_html(title, content, navigation, index_file)
