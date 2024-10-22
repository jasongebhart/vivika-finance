from flask import Flask, render_template, jsonify, request, send_from_directory
import os
from src.report_html_generator import generate_html_structure  # Import your existing report generator

app = Flask(__name__)

# Serve the homepage
@app.route('/')
def index():
    # This will render the index.html that you've generated within the reports directory
    return send_from_directory('reports', 'index.html')

# Route to render the create.html template
@app.route('/create')
def create():
    return render_template('create.html')  # Ensure you have a create.html file in the 'templates' directory


# Endpoint to generate reports dynamically (using existing logic)
# @app.route('/generate_report', methods=['POST'])
# def generate_report():
#     scenario_data = request.json  # Assuming you want to handle JSON input
#     report_html = generate_html_report(scenario_data)  # Call your existing function
#     return jsonify({"report": report_html})

# Endpoint to view specific reports
@app.route('/view_report/<string:filename>')
def view_report(filename):
    # Return a specific report by serving the HTML file
    return send_from_directory('reports', f'{filename}.html')

app.route('/scenarios/<path:filename>')
def serve_json(filename):
    return send_from_directory('scenarios', filename)

if __name__ == "__main__":
    app.run(debug=True)
