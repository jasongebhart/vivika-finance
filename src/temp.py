import report_html_generator
# Sample mock data
html_files = ["scenario_sf_hav_jason_retired-retired_own_private_8yrs.html"]
html_dir = "./reports"
config = {
    "name_lookup": {
        "hav": "Havilah",
        "jason": "Jason"
    },
    "work_status_lookup": {
        "retired": "Retired"
    },
    "location_lookup": {
        "sf": "San Francisco"
    },
    "ownership_type_lookup": {
        "own": "Own"
    },
    "school_type_lookup": {
        "private": "Private",
        "public": "Public"
    }
}

# Call the function
toc_content = report_html_generator.organize_content(html_files, html_dir, config)

# Print the organized content for verification
print(toc_content)
