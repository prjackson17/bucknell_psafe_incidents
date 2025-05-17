from flask import Flask, jsonify, render_template
import json
import os
from collections import defaultdict
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reports/crime_log_<date>.json')
def reports(date):
    # Assuming JSON files are named by date, e.g., 2023-05-01.json
    file_path = f'reports/crime_log_{date}.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    else:
        return jsonify({"error": "Report not found"}), 404
    

@app.route('/api/stats/monthly')
def monthly_stats():
    reports_dir = 'reports'
    monthly_counts = defaultdict(int)

    for filename in os.listdir(reports_dir):
        if filename.endswith('.json') and filename.startswith('crime_log_'):
            filepath = os.path.join(reports_dir, filename)

            with open(filepath, 'r') as f:
                try:
                    entries = json.load(f)
                except json.JSONDecodeError:
                    continue

                for entry in entries:
                    raw_date = entry.get('Date', '')  # Expecting MM/DD/YYYY
                    try:
                        dt = datetime.strptime(raw_date, '%m/%d/%Y')
                        key = dt.strftime('%Y-%m')  # e.g., "2025-04"
                        monthly_counts[key] += 1
                    except ValueError:
                        continue

    # Convert to a regular dict and sort by month
    sorted_data = dict(sorted(monthly_counts.items()))

    return jsonify(sorted_data)

if __name__ == '__main__':
    app.run(debug=True)
