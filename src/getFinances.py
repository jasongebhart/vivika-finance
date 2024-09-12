import investment_module
import report_html_generator

def main():
    log_dir = investment_module.create_log_directory()
    investment_module.setup_logging(log_dir)
    scenarios_data = investment_module.parse_and_load_config()
    # print(f"Loaded scenarios_data: {scenarios_data}")
    
    base_config = investment_module.prepare_scenarios_data(scenarios_data)
    # print(f"Prepared data: {base_config}")
    
    reports_dir = investment_module.create_reports_directory()

    summary_report_data = {}

    for scenario_name in base_config["selected_scenarios"]:
        try:
            # summary_data = investment_module.process_scenario(scenario_name, base_config, reports_dir,scenarios_dir="scenarios/sequences")
            summary_data = investment_module.process_scenario(scenario_name, base_config, reports_dir,scenarios_dir="scenarios")
            summary_report_data[scenario_name] = summary_data
        except Exception as e:
            print(f"Failed to process scenario {scenario_name}: {e}")

    summary_report_html = report_html_generator.generate_summary_report_html(summary_report_data)
    summary_report_filename = reports_dir / "summary_report.html"
    with summary_report_filename.open('w') as summary_file:
        summary_file.write(summary_report_html)
    
    print(f"Summary report generated successfully. See: {summary_report_filename}")

if __name__ == "__main__":
    main()
