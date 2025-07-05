#!/usr/bin/env python3
"""
This script builds a static version of the AQI Forecast application
suitable for deployment on GitHub Pages.
"""

import os
import shutil
import json
from datetime import datetime, timedelta
import pandas as pd

# Import application modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.fetch_and_train import run_training_and_forecast
from app.model_loader import classify_aqi
from app.data_manager import get_historical_data
from app.github_storage import get_github_repo

# Get GitHub repo from environment or use default
GITHUB_REPO = get_github_repo() or "yourusername/aqi-forecast-app"

# List of cities to pre-generate data for
DEFAULT_CITIES = [
    # India
    "Delhi", "Mumbai", "Bangalore", "Kolkata", "Chennai", "Hyderabad", "Pune", "Ahmedabad",
    # North America
    "New York", "Los Angeles", "Chicago", "Toronto", "Mexico City", "San Francisco",
    # Europe
    "London", "Paris", "Berlin", "Rome", "Madrid", "Amsterdam", "Vienna",
    # Asia Pacific
    "Tokyo", "Beijing", "Shanghai", "Hong Kong", "Singapore", "Sydney", "Seoul",
    # Middle East & Africa
    "Dubai", "Cairo", "Johannesburg", "Cape Town"
]

# Detect if running in GitHub Actions
RUNNING_IN_GITHUB_ACTIONS = os.environ.get('GITHUB_ACTIONS') == 'true'

# If running in GitHub Actions and we have limited resources, use a smaller set
if RUNNING_IN_GITHUB_ACTIONS and os.environ.get('USE_REDUCED_CITIES') == 'true':
    DEFAULT_CITIES = DEFAULT_CITIES[:15]  # Use only first 15 cities to save time/resources

# Output directory for static site
STATIC_SITE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static_site")

def ensure_dir_exists(path):
    """Ensure directory exists"""
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def copy_static_assets():
    """Copy static assets to the output directory"""
    # Create static directories
    static_dir = ensure_dir_exists(os.path.join(STATIC_SITE_DIR, "static"))
    css_dir = ensure_dir_exists(os.path.join(STATIC_SITE_DIR, "css"))
    js_dir = ensure_dir_exists(os.path.join(STATIC_SITE_DIR, "js"))
    data_dir = ensure_dir_exists(os.path.join(STATIC_SITE_DIR, "data"))
    
    # Copy CSS from the template
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                          "templates", "index_enhanced.html"), "r", encoding="utf-8") as f:
        template_content = f.read()
        
        # Extract CSS
        css_start = template_content.find("<style>") + 7
        css_end = template_content.find("</style>")
        css_content = template_content[css_start:css_end]
        
        # Write CSS to file
        with open(os.path.join(css_dir, "styles.css"), "w", encoding="utf-8") as css_file:
            css_file.write("/* AQI Forecast Application Styles */\n\n")
            css_file.write(css_content)
    
    # Create JavaScript file for the application
    with open(os.path.join(js_dir, "app.js"), "w", encoding="utf-8") as js_file:
        js_file.write("""// AQI Forecast Application
document.addEventListener('DOMContentLoaded', function() {
    // Handle form submission
    document.getElementById('searchForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const city = document.getElementById('cityInput').value.trim();
        if (city) {
            window.location.href = `city.html?city=${encodeURIComponent(city)}`;
        }
    });
    
    // Load pre-generated cities
    loadPreGeneratedCities();
    
    // Load and display last updated time
    loadBuildMetadata();
});

function loadBuildMetadata() {
    fetch('data/metadata.json')
        .then(response => response.json())
        .then(data => {
            // Add last updated info to the footer if element exists
            const lastUpdatedEl = document.getElementById('last-updated');
            if (lastUpdatedEl) {
                const date = new Date(data.data_updated);
                lastUpdatedEl.textContent = `Last updated: ${date.toLocaleString()}`;
            }
            
            // Add version info if element exists
            const versionEl = document.getElementById('app-version');
            if (versionEl && data.version) {
                versionEl.textContent = `v${data.version}`;
            }
        })
        .catch(error => console.error('Error loading metadata:', error));
}

function loadPreGeneratedCities() {
    fetch('data/cities.json')
        .then(response => response.json())
        .then(data => {
            const citiesList = document.getElementById('pre-generated-cities');
            if (citiesList) {
                citiesList.innerHTML = '';
                
                // Group cities by region for better organization
                const regions = {
                    "Asia": [],
                    "North America": [],
                    "Europe": [],
                    "Other Regions": []
                };
                
                // Simple region classification - can be improved
                data.cities.forEach(city => {
                    if (["Delhi", "Mumbai", "Bangalore", "Kolkata", "Chennai", "Hyderabad", 
                         "Tokyo", "Beijing", "Shanghai", "Hong Kong", "Singapore", "Seoul"].includes(city)) {
                        regions["Asia"].push(city);
                    } else if (["New York", "Los Angeles", "Chicago", "Toronto", "Mexico City", "San Francisco"].includes(city)) {
                        regions["North America"].push(city);
                    } else if (["London", "Paris", "Berlin", "Rome", "Madrid", "Amsterdam", "Vienna"].includes(city)) {
                        regions["Europe"].push(city);
                    } else {
                        regions["Other Regions"].push(city);
                    }
                });
                
                // Create region sections
                Object.keys(regions).forEach(region => {
                    if (regions[region].length > 0) {
                        const regionHeader = document.createElement('h4');
                        regionHeader.className = 'region-header';
                        regionHeader.textContent = region;
                        citiesList.appendChild(regionHeader);
                        
                        regions[region].sort().forEach(city => {
                            const link = document.createElement('a');
                            link.href = `city.html?city=${encodeURIComponent(city)}`;
                            link.className = 'city-link';
                            link.innerHTML = `<i class="fas fa-map-marker-alt"></i> ${city}`;
                            citiesList.appendChild(link);
                        });
                    }
                });
            }
        })
        .catch(error => console.error('Error loading cities:', error));
}

function loadCityData(city) {
    // Show loading state
    document.getElementById('loading-indicator').style.display = 'block';
    document.getElementById('city-results').style.display = 'none';
    
    // Attempt to load pre-generated data
    fetch(`data/${city.toLowerCase()}.json`)
        .then(response => {
            if (!response.ok) {
                throw new Error('City data not available');
            }
            return response.json();
        })
        .then(data => {
            displayCityData(city, data);
            
            // Load heatmap if available
            if (document.getElementById('heatmap-container')) {
                document.getElementById('heatmap-container').innerHTML = 
                    `<iframe src="data/${city.toLowerCase()}_heatmap.html" class="heatmap-iframe"></iframe>`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('error-message').style.display = 'block';
            document.getElementById('error-message').textContent = 
                'Data for this city is not available. Please try one of the pre-generated cities.';
        })
        .finally(() => {
            document.getElementById('loading-indicator').style.display = 'none';
        });
}

function displayCityData(city, data) {
    // Display city name
    document.querySelectorAll('.city-name').forEach(el => {
        el.textContent = city;
    });
    
    // Display current AQI
    if (data.current_aqi) {
        document.getElementById('current-aqi').textContent = data.current_aqi;
        document.getElementById('current-aqi-category').textContent = data.category.split(' – ')[0];
        document.getElementById('current-aqi-category').className = getCategoryClass(data.current_aqi);
    }
    
    // Display predicted AQI
    if (data.predicted_aqi) {
        document.getElementById('predicted-aqi').textContent = data.predicted_aqi;
        document.getElementById('predicted-aqi-category').textContent = data.category.split(' – ')[0];
        document.getElementById('predicted-aqi-category').className = getCategoryClass(data.predicted_aqi);
    }
    
    // Display forecast
    if (data.forecast_data && data.forecast_data.length > 0) {
        const forecastTable = document.getElementById('forecast-table-body');
        forecastTable.innerHTML = '';
        
        data.forecast_data.forEach(day => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${day.day}</td>
                <td>${day.date}</td>
                <td>${day.value}</td>
                <td><span class="${getCategoryClass(day.value)}">${day.category.split(' – ')[0]}</span></td>
            `;
            forecastTable.appendChild(row);
        });
        
        document.getElementById('forecast-section').style.display = 'block';
    } else {
        document.getElementById('forecast-section').style.display = 'none';
    }
    
    // Show the results section
    document.getElementById('city-results').style.display = 'block';
}

function getCategoryClass(aqi) {
    aqi = parseFloat(aqi);
    if (aqi <= 50) return 'category-good';
    if (aqi <= 100) return 'category-satisfactory';
    if (aqi <= 200) return 'category-moderate';
    if (aqi <= 300) return 'category-poor';
    if (aqi <= 400) return 'category-very-poor';
    return 'category-severe';
}
""")
    
    # Export historical data to JSON
    historical_data = get_historical_data(days=60)
    if not historical_data.empty:
        historical_data_json = historical_data.to_dict(orient='records')
        with open(os.path.join(data_dir, "historical_data.json"), "w", encoding="utf-8") as data_file:
            json.dump(historical_data_json, data_file, indent=2)
    
    # Create a cities list file
    with open(os.path.join(data_dir, "cities.json"), "w", encoding="utf-8") as cities_file:
        json.dump({"cities": DEFAULT_CITIES}, cities_file, indent=2)

def generate_html_files():
    """Generate HTML files for the static site"""
    
    # Generate index.html
    index_html = f"""<!DOCTYPE html>
<html>
<head>
  <title>AQI Forecast Application</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">
  <link rel="stylesheet" href="css/styles.css">
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>AQI Forecast Application</h1>
      <p>Get accurate air quality forecasts and predictions for any city worldwide</p>
    </div>

    <form id="searchForm" class="search-form">
      <input type="text" id="cityInput" placeholder="Enter a city name" required class="search-input">
      <button type="submit" class="search-button"><i class="fas fa-search"></i> Get Forecast</button>
    </form>

    <div class="section">
      <h3 class="result-header"><i class="fas fa-map-marker-alt"></i> Pre-generated City Reports</h3>
      <p>Click on a city below to see its pre-generated AQI forecast:</p>
      <div id="pre-generated-cities" class="cities-grid"></div>
    </div>

    <div class="section">
      <h3 class="result-header"><i class="fas fa-info-circle"></i> About This Application</h3>
      <p>This AQI Forecast application uses machine learning to predict Air Quality Index for cities worldwide. The application analyzes weather patterns and historical data to provide accurate forecasts.</p>
      <p>Data is updated periodically and the machine learning model is retrained daily.</p>
    </div>

    <div class="footer">
      <p>© 2025 AQI Forecast App | Powered by NASA POWER and WAQI API</p>
      <p id="last-updated">Last updated: Loading...</p>
      <p><i class="fas fa-code"></i> with <i class="fas fa-heart" style="color: #F44336;"></i> for cleaner air</p>
      <p style="margin-top: 10px;">
        <a href="https://github.com/{GITHUB_REPO}" target="_blank" style="color: #2196F3; text-decoration: none;">
          <i class="fab fa-github"></i> GitHub Repository <span id="app-version"></span>
        </a>
        <span style="margin-left: 15px;">
          <a href="build_report.html" style="color: #607D8B; font-size: 0.8em; text-decoration: none;">
            <i class="fas fa-info-circle"></i> Build Info
          </a>
        </span>
      </p>
    </div>
  </div>

  <script src="js/app.js"></script>
</body>
</html>"""
    
    with open(os.path.join(STATIC_SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)
    
    # Generate city.html (template for displaying city data)
    city_html = """<!DOCTYPE html>
<html>
<head>
  <title>AQI Forecast for City</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">
  <link rel="stylesheet" href="css/styles.css">
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>AQI Forecast Application</h1>
      <p>Get accurate air quality forecasts and predictions for any city worldwide</p>
    </div>

    <form id="searchForm" class="search-form">
      <input type="text" id="cityInput" placeholder="Enter a city name" required class="search-input">
      <button type="submit" class="search-button"><i class="fas fa-search"></i> Get Forecast</button>
    </form>
    
    <div id="loading-indicator" style="text-align: center; padding: 2rem; display: none;">
      <i class="fas fa-spinner fa-spin" style="font-size: 2rem; color: var(--primary-color);"></i>
      <p>Loading data...</p>
    </div>
    
    <div id="error-message" class="error-message" style="display: none;">
      Data for this city is not available.
    </div>

    <div id="city-results" style="display: none;">
      <div class="result-section">
        <h3 class="result-header"><i class="fas fa-map-marker-alt"></i> Results for <span class="city-name">City</span></h3>
        
        <div class="aqi-cards">
          <div class="aqi-card">
            <h4><i class="fas fa-broadcast-tower"></i> Current AQI</h4>
            <div id="current-aqi" class="aqi-value">--</div>
            <span id="current-aqi-category" class="aqi-category">Not Available</span>
            <p>Real-time air quality data from WAQI API</p>
          </div>
          
          <div class="aqi-card">
            <h4><i class="fas fa-chart-line"></i> Predicted AQI</h4>
            <div id="predicted-aqi" class="aqi-value">--</div>
            <span id="predicted-aqi-category" class="aqi-category">Not Available</span>
            <p id="predicted-aqi-description"></p>
          </div>
        </div>

        <div id="forecast-section" class="forecast-section" style="display: none;">
          <h3>3-Day AQI Forecast</h3>
          <table class="forecast-table">
            <thead>
              <tr>
                <th>Day</th>
                <th>Date</th>
                <th>Predicted AQI</th>
                <th>Category</th>
              </tr>
            </thead>
            <tbody id="forecast-table-body">
              <!-- Forecast data rows will be inserted here -->
            </tbody>
          </table>
        </div>
      </div>

      <div class="heatmap-section">
        <div class="heatmap-title">
          <i class="fas fa-map-marked-alt"></i>
          <h3 class="result-header">AQI Heatmap for <span class="city-name">City</span></h3>
        </div>
        <p class="map-instruction"><i class="fas fa-info-circle"></i> Interactive map showing air quality in <span class="city-name">City</span>. Click on the marker for detailed information.</p>
        <div id="heatmap-container" class="heatmap-container">
          <!-- Heatmap iframe will be inserted here -->
        </div>
      </div>
    </div>

    <div class="footer">
      <p>© 2025 AQI Forecast App | Powered by NASA POWER and WAQI API</p>
      <p><i class="fas fa-code"></i> with <i class="fas fa-heart" style="color: #F44336;"></i> for cleaner air</p>
      <p style="margin-top: 10px;">
        <a href="index.html" style="color: #2196F3; text-decoration: none;">
          <i class="fas fa-home"></i> Back to Home
        </a>
      </p>
    </div>
  </div>

  <script src="js/app.js"></script>
  <script>
    document.addEventListener('DOMContentLoaded', function() {
      const urlParams = new URLSearchParams(window.location.search);
      const city = urlParams.get('city');
      
      if (city) {
        document.getElementById('cityInput').value = city;
        loadCityData(city);
      } else {
        window.location.href = 'index.html';
      }
    });
  </script>
</body>
</html>"""
    
    with open(os.path.join(STATIC_SITE_DIR, "city.html"), "w", encoding="utf-8") as f:
        f.write(city_html)

def generate_city_data(city):
    """Generate data for a specific city"""
    print(f"Generating data for {city}...")
    data_dir = ensure_dir_exists(os.path.join(STATIC_SITE_DIR, "data"))
    
    try:
        # Get forecast data for the city
        result = run_training_and_forecast(city)
        
        if not result.get('success', False):
            print(f"Failed to generate data for {city}")
            return False
        
        # Create forecast data
        forecast_data = []
        forecast_values = result.get('forecast_values', [])
        
        today = datetime.today()
        dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]
        
        for i, (date, value) in enumerate(zip(dates, forecast_values)):
            if value is not None:
                # Ensure AQI value is valid (positive)
                aqi_value = abs(value)
                if aqi_value > 500:
                    aqi_value = 500
                forecast_cat = classify_aqi(aqi_value)
                forecast_data.append({
                    'day': f"Day {i+1}",
                    'date': date,
                    'value': round(float(aqi_value), 2),
                    'category': forecast_cat
                })
        
        # Store city data as JSON
        city_data = {
            'city': city,
            'current_aqi': result.get('current_aqi'),
            'predicted_aqi': result.get('predicted_aqi'),
            'category': result.get('category'),
            'forecast_data': forecast_data,
            'coordinates': result.get('coordinates'),
            'generation_time': datetime.now().isoformat()
        }
        
        with open(os.path.join(data_dir, f"{city.lower()}.json"), "w", encoding="utf-8") as f:
            json.dump(city_data, f, indent=2)
        
        # Copy the heatmap if it exists
        heatmap_path = 'static/regional_heatmap.html'
        if os.path.exists(heatmap_path):
            with open(heatmap_path, 'r', encoding='utf-8') as src_file:
                heatmap_content = src_file.read()
                
                # Write to city-specific heatmap file
                with open(os.path.join(data_dir, f"{city.lower()}_heatmap.html"), "w", encoding="utf-8") as dest_file:
                    dest_file.write(heatmap_content)
        
        print(f"✅ Generated data for {city}")
        return True
    except Exception as e:
        print(f"❌ Error generating data for {city}: {e}")
        return False

def generate_metadata():
    """Generate metadata file with build information"""
    data_dir = ensure_dir_exists(os.path.join(STATIC_SITE_DIR, "data"))
    
    build_metadata = {
        "build_timestamp": datetime.now().isoformat(),
        "build_environment": "GitHub Actions" if RUNNING_IN_GITHUB_ACTIONS else "Local",
        "cities_included": DEFAULT_CITIES,
        "data_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
        "version": "1.0.0"
    }
    
    # Add GitHub-specific metadata if available
    if RUNNING_IN_GITHUB_ACTIONS:
        build_metadata.update({
            "github_repository": os.environ.get('GITHUB_REPOSITORY', ''),
            "github_run_id": os.environ.get('GITHUB_RUN_ID', ''),
            "github_sha": os.environ.get('GITHUB_SHA', '')[:7]  # Short SHA
        })
    
    # Write metadata file
    with open(os.path.join(data_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(build_metadata, f, indent=2)
    
    return build_metadata

def main():
    """Main function to build the static site"""
    start_time = datetime.now()
    print(f"Building static site at {start_time.strftime('%Y-%m-%d %H:%M:%S')}...")
    
    # Ensure the static site directory exists
    if os.path.exists(STATIC_SITE_DIR):
        shutil.rmtree(STATIC_SITE_DIR)
    os.makedirs(STATIC_SITE_DIR)
    
    # Copy static assets
    print("Copying static assets...")
    copy_static_assets()
    
    # Generate HTML files
    print("Generating HTML files...")
    generate_html_files()
    
    # Generate data for each city
    print(f"Generating data for {len(DEFAULT_CITIES)} cities...")
    successful_cities = []
    failed_cities = []
    
    for city in DEFAULT_CITIES:
        if generate_city_data(city):
            successful_cities.append(city)
        else:
            failed_cities.append(city)
    
    # Generate metadata with build information
    metadata = generate_metadata()
    
    # Print summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"✅ Static site built successfully at {STATIC_SITE_DIR}")
    print(f"⏱️ Build completed in {duration:.2f} seconds")
    print(f"🏙️ Successfully generated data for {len(successful_cities)} cities")
    
    if failed_cities:
        print(f"⚠️ Failed to generate data for {len(failed_cities)} cities: {', '.join(failed_cities)}")
    
    # Create a simple build report in the static site
    with open(os.path.join(STATIC_SITE_DIR, "build_report.html"), "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head>
  <title>AQI Forecast App - Build Report</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link href="css/styles.css" rel="stylesheet">
</head>
<body>
  <div class="container">
    <h1>Static Site Build Report</h1>
    <p>Build completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>Build duration: {duration:.2f} seconds</p>
    <p>Environment: {metadata['build_environment']}</p>
    <h2>City Data Status:</h2>
    <p>✅ Successfully built: {len(successful_cities)} cities</p>
    <p>❌ Failed: {len(failed_cities)} cities</p>
    <div>
      <a href="index.html" class="search-button">Back to Home</a>
    </div>
  </div>
</body>
</html>""")

if __name__ == "__main__":
    main()
