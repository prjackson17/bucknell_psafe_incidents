from flask import Flask, jsonify, render_template
import json
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reports/<date>')
def reports(date):
    # Assuming JSON files are named by date, e.g., 2023-05-01.json
    file_path = f'reports/{date}.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    else:
        return jsonify({"error": "Report not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
