from flask import Flask, request, render_template, redirect, url_for, send_file, jsonify, Response
import os
import sys
import io
import zipfile
import json
from werkzeug.security import check_password_hash, generate_password_hash
from app.fetch_and_train import run_training_and_forecast
from app.model_loader import classify_aqi
from app.scheduled_training import start_scheduler
from app.init_directories import ensure_directories
from app.backup_manager import create_backup, restore_backup
from datetime import datetime, timedelta

# Ensure required directories exist
ensure_directories()

app = Flask(__name__)

# Start the scheduler in a background thread when the app starts
scheduler_thread = None

@app.route('/', methods=['GET', 'POST'])
def index():
    prediction = None
    city = ""
    heatmap_path = None
    current_aqi = None
    category = None
    forecast_data = []
    
    if request.method == 'POST':
        city = request.form.get('city', '')
        if city:
            # Run the forecast for the specified city
            # Run forecast and get results
            result = run_training_and_forecast(city)
            print(f"Result from forecast: {result}")
            
            # Set default values in case of missing data
            prediction = None
            current_aqi = None
            category = None
            
            if result.get('success', False):
                prediction = result.get('predicted_aqi')
                current_aqi = result.get('current_aqi')
                category = result.get('category')
                
                # Create forecast data for the next 3 days
                dates = []
                today = datetime.today()
                for i in range(1, 4):
                    dates.append((today + timedelta(days=i)).strftime('%Y-%m-%d'))
                
                # Combine dates with forecast values
                forecast_data = []
                forecast_values = result.get('forecast_values', [])
                
                for i, (date, value) in enumerate(zip(dates, forecast_values)):
                    if value is not None:  # Only include if there's a value
                        # Ensure AQI value is valid (positive)
                        aqi_value = abs(value)
                        if aqi_value > 500:  # Cap at reasonable maximum
                            aqi_value = 500
                        forecast_cat = classify_aqi(aqi_value)
                        forecast_data.append({
                            'day': f"Day {i+1}",
                            'date': date,
                            'value': round(float(aqi_value), 2),
                            'category': forecast_cat
                        })
            
            # Check if heatmap file was generated
            if os.path.exists('static/regional_heatmap.html'):
                heatmap_path = 'static/regional_heatmap.html'
                
            return render_template('index_enhanced.html', 
                               city=city.title(), 
                               prediction=prediction,
                               current_aqi=current_aqi,
                               category=category,
                               forecast_data=forecast_data,
                               heatmap_path=heatmap_path)
    
    return render_template('index_enhanced.html', 
                           city=city, 
                           heatmap_path=heatmap_path)

@app.route('/heatmap')
def heatmap():
    if os.path.exists('static/regional_heatmap.html'):
        with open('static/regional_heatmap.html', 'r') as f:
            return f.read()
    return "Heatmap not available yet. Please generate a forecast first."

@app.route('/admin')
def admin():
    # Simple admin panel for data management
    return render_template('admin.html')

@app.route('/backup', methods=['POST'])
def backup():
    try:
        # Create a backup and get the path
        backup_path = create_backup()
        
        # If the request wants JSON response
        if request.headers.get('Accept') == 'application/json':
            return jsonify({
                "success": True,
                "message": f"Backup created successfully at {backup_path}",
                "path": backup_path
            })
        
        # Otherwise, return the file for download
        return send_file(
            backup_path, 
            as_attachment=True,
            download_name=os.path.basename(backup_path),
            mimetype='application/zip'
        )
    except Exception as e:
        if request.headers.get('Accept') == 'application/json':
            return jsonify({
                "success": False,
                "message": f"Error creating backup: {str(e)}"
            }), 500
        return f"Error creating backup: {str(e)}", 500

@app.route('/restore', methods=['POST'])
def restore():
    if 'backup_file' not in request.files:
        return jsonify({"success": False, "message": "No file provided"}), 400
    
    file = request.files['backup_file']
    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected"}), 400
    
    # Save the uploaded file
    upload_path = os.path.join('temp', file.filename)
    os.makedirs('temp', exist_ok=True)
    file.save(upload_path)
    
    # Restore from the backup file
    success = restore_backup(upload_path)
    
    # Clean up
    if os.path.exists(upload_path):
        os.remove(upload_path)
    
    if success:
        return jsonify({"success": True, "message": "Backup restored successfully"})
    else:
        return jsonify({"success": False, "message": "Failed to restore backup"}), 500

if __name__ == '__main__':
    # Start the scheduler
    scheduler_thread = start_scheduler()
    app.run(debug=True)
