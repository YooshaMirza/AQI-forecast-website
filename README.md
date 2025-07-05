# AQI Forecast Application

This application provides Air Quality Index (AQI) forecasts using machine learning models. It uses a Random Forest model for accurate predictions based on NASA weather data.

## Features

- **City-Based Forecasting**: Get AQI predictions for any city worldwide
- **NASA Weather Data**: Leverages NASA's POWER API for reliable weather metrics
- **Random Forest Model**: High-accuracy predictions using pre-trained models
- **Simple Interface**: Easy-to-use interface for quick forecasts
- **AQI Classification**: Clear categorization of air quality levels

## Project Structure

```
aqi_forecast_app/
│
├── app.py                       # Flask backend
├── backend_utils.py             # Helper functions (NASA API, geocoding, etc.)
├── templates/
│   └── index.html               # Frontend UI
│
├── model/                       # ML models
│   ├── rf_large_model.pkl       # Pretrained Random Forest model
│   ├── rf_large_scaler.pkl      # RF model scaler
│   ├── sgd_model.pkl            # SGD model
│   └── scaler.pkl               # SGD scaler
│
├── fetch_and_train.py           # Script for model updates
├── requirements.txt             # Python dependencies
├── render.yaml                  # Render deployment config
└── README.md                    # This file
```

## Installation and Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd aqi_forecast_app
   ```

2. Create and activate a virtual environment:
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Open your browser and navigate to http://127.0.0.1:5000/

## How It Works

1. **City Selection**: User enters a city name
2. **Geocoding**: App converts city name to latitude/longitude
3. **Weather Data**: NASA POWER API provides weather metrics for the location
4. **Prediction**: Random Forest model predicts AQI based on weather parameters
5. **Classification**: AQI value is categorized into health impact levels

## Data Sources

- **Weather Data**: NASA POWER API (https://power.larc.nasa.gov/)
- **Geocoding**: Nominatim/OpenStreetMap

## AQI Categories

- **Good** (0-50): Air quality is satisfactory
- **Satisfactory** (51-100): Minor discomfort to sensitive people
- **Moderate** (101-200): May cause breathing discomfort to people with lung disease
- **Poor** (201-300): May cause discomfort to most people
- **Very Poor** (301-400): May cause respiratory issues
- **Severe** (401+): Affects healthy people and seriously impacts those with existing diseases

## Deployment

The application is configured for deployment on Render with the included `render.yaml` file.

## Development

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[MIT License](LICENSE)

## Acknowledgements

- NASA POWER API for providing reliable weather data
- OpenStreetMap/Nominatim for geocoding services
- Created with Flask, scikit-learn, and joblib
