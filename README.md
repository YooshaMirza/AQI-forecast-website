# AQI Forecast Application

This application provides Air Quality Index (AQI) forecasts using machine learning models. It uses a machine learning model trained on weather data from NASA's POWER API combined with real-time AQI data from the WAQI API.

## Features

- **City-Based Forecasting**: Get AQI predictions for any city worldwide
- **Daily Model Retraining**: Model automatically retrains daily with new data
- **Interactive Heatmaps**: Visual representation of air quality by region
- **Persistent Data Storage**: Models and historical data stored on GitHub
- **Modern UI**: Responsive design with color-coded AQI categories
- **Static Site Generation**: Can be deployed as a static site on GitHub Pages

## Deployment Options

This application can be deployed in two ways:

### 1. Full Dynamic Application (Render, Heroku, etc.)

The complete Flask application with real-time forecasting, automatic model retraining, and admin features.

### 2. Static GitHub Pages Site

A pre-generated static version that can be hosted on GitHub Pages. This version:
- Contains pre-generated forecasts for popular cities
- Automatically updates via GitHub Actions
- Stores all data and models directly in your GitHub repository
- Eliminates the need for a separate data persistence pipeline

## Project Structure

```
aqi_forecast_app/
│
├── .github/workflows/           # GitHub Actions workflows for GitHub Pages
├── app/                         # Core application modules
│   ├── models/                  # Trained ML models
│   ├── historical_data/         # Historical AQI and training data
│   ├── backup_manager.py        # Data backup/restore utilities
│   ├── backend_utils.py         # API and utility functions
│   ├── data_manager.py          # Historical data management
│   ├── fetch_and_train.py       # Model training pipeline
│   ├── github_storage.py        # GitHub data persistence
│   ├── init_directories.py      # Directory initialization
│   ├── model_loader.py          # Model loading and AQI classification
│   ├── plot_heatmap.py          # Heatmap generation
│   └── scheduled_training.py    # Automatic daily retraining
│
├── main.py                      # Main Flask application
├── scripts/                     # Utility scripts
│   ├── build_static_site.py     # Static site generator for GitHub Pages
│   ├── deploy_to_github_pages.py # GitHub Pages deployment helper
│   └── setup_github_integration.py # GitHub token and repo setup
│
├── static/                      # Static assets and generated maps
├── templates/                   # HTML templates
│   ├── admin.html               # Admin panel
│   └── index_enhanced.html      # Main application UI
│
├── Procfile                     # Deployment configuration for Render/Heroku
├── README.md                    # This file
├── render.yaml                  # Render configuration
├── requirements.txt             # Python dependencies
└── wsgi.py                      # WSGI entry point
```

## Setup for GitHub Pages Deployment

To leverage GitHub Pages for hosting your app and storing data:

1. **Configure GitHub Integration**:
   ```bash
   python scripts/setup_github_integration.py
   ```

2. **Build and Test Static Site**:
   ```bash
   python scripts/build_static_site.py
   ```

3. **Deploy to GitHub Pages**:
   ```bash
   python scripts/deploy_to_github_pages.py
   ```

4. **Setup GitHub Actions** (Optional):
   - Ensure your repository has the following secrets:
     - `WAQI_API_KEY`: Your World Air Quality Index API key

   The GitHub Actions workflow will:
   - Run daily to retrain the model with fresh data
   - Update the static site with new forecasts
   - Commit all data and models back to your repository
   - Deploy the updated static site to GitHub Pages

## Setup for Full Dynamic Application

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**:
   - `WAQI_API_KEY`: Your World Air Quality Index API key
   - `GITHUB_TOKEN`: Personal Access Token for GitHub storage (optional)
   - `GITHUB_REPO`: Repository for data storage (optional, format: username/repo-name)

3. **Initialize Application**:
   ```bash
   python -c "from app.init_directories import init_all; init_all()"
   ```

4. **Run the Application**:
   ```bash
   python main.py
   ```

## Data Persistence Strategy

This application uses a multi-layered approach to ensure data persistence:

1. **Local Storage**: All models and historical data are saved locally
2. **GitHub Repository**: Data is automatically backed up to GitHub after each training session
3. **Manual Backups**: Admin panel allows downloading/uploading backup files
4. **Static Site**: Pre-generated forecasts are included in the static GitHub Pages site

This ensures that even if deployed on platforms with ephemeral storage (like Render's free tier), your data will persist.

## How It Works

### Dynamic Application
1. **City Selection**: User enters a city name
2. **Geocoding**: App converts city name to latitude/longitude
3. **Weather Data**: NASA POWER API provides weather metrics for the location
4. **Real-time AQI**: Current AQI is fetched from WAQI API
5. **Prediction**: ML model predicts AQI based on weather parameters
6. **Training**: Model retrains daily using historical data

### Static GitHub Pages Site
1. **Pre-generated Data**: Static site includes pre-generated data for popular cities
2. **GitHub Actions**: Automatically updates data daily via GitHub Actions
3. **GitHub Storage**: All data and models are stored in your GitHub repository
4. **No Server Required**: Pure static HTML/JS/CSS that runs entirely in the browser

## AQI Categories

- **Good** (0-50): Air quality is satisfactory
- **Satisfactory** (51-100): Minor discomfort to sensitive people
- **Moderate** (101-200): May cause breathing discomfort to people with lung disease
- **Poor** (201-300): May cause discomfort to most people
- **Very Poor** (301-400): May cause respiratory issues
- **Severe** (401+): Affects healthy people and seriously impacts those with existing diseases

## API Credits

- [World Air Quality Index (WAQI) API](https://aqicn.org/api/)
- [NASA POWER API](https://power.larc.nasa.gov/docs/services/api/)

## License

MIT
