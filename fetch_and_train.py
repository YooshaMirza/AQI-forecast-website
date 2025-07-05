"""
Script to update SGD model with real-time data.
Will be replaced with the actual implementation later.
"""

import os
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import SGDRegressor
import requests
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("model_update.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Constants
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model')
SGD_MODEL_PATH = os.path.join(MODEL_DIR, 'sgd_model.pkl')
SCALER_PATH = os.path.join(MODEL_DIR, 'scaler.pkl')

# Ensure model directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

def fetch_aqi_data(days=7):
    """
    Fetch AQI data from an external API or source.
    
    Replace this with your actual data fetching logic.
    """
    logger.info(f"Fetching {days} days of AQI data")
    
    try:
        # Replace this with your actual API call
        # Example: response = requests.get("https://api.airquality.com/data", params={"days": days})
        
        # For demonstration, we're generating synthetic data
        np.random.seed(int(datetime.now().timestamp()) % 100)  # Semi-random seed
        n_samples = days * 24  # Hourly data
        
        data = {
            'timestamp': pd.date_range(end=datetime.now(), periods=n_samples, freq='H'),
            'temperature': np.random.normal(25, 5, n_samples),
            'humidity': np.random.normal(50, 15, n_samples),
            'wind_speed': np.abs(np.random.normal(5, 3, n_samples)),
            'pressure': np.random.normal(1013, 5, n_samples),
        }
        
        df = pd.DataFrame(data)
        
        # Generate target (AQI) - replace with your actual formula if available
        df['aqi'] = (
            30 +
            0.8 * (df['temperature'] - 20) +
            0.3 * (df['humidity'] - 40) +
            -2 * df['wind_speed'] / 5 +
            np.random.normal(0, 10, n_samples)
        ).clip(lower=0)
        
        logger.info(f"Data fetched successfully: {len(df)} records")
        return df
        
    except Exception as e:
        logger.error(f"Error fetching AQI data: {e}")
        return None

def update_sgd_model():
    """Update the SGD model with new data"""
    logger.info("Starting SGD model update")
    
    try:
        # Skip if SGD model file doesn't exist (will be uploaded manually)
        if not os.path.exists(SGD_MODEL_PATH):
            logger.info("SGD model file not found. Skipping update.")
            return False
            
        # Get recent data
        df = fetch_aqi_data(days=7)
        if df is None or len(df) == 0:
            logger.error("No data available for model update")
            return False
            
        # Extract features and target
        X = df[['temperature', 'humidity', 'wind_speed', 'pressure']].values
        y = df['aqi'].values
        
        # Load existing model and scaler
        try:
            with open(SGD_MODEL_PATH, 'rb') as f:
                model = pickle.load(f)
                
            with open(SCALER_PATH, 'rb') as f:
                scaler = pickle.load(f)
                
        except Exception as e:
            logger.error(f"Error loading model or scaler: {e}")
            return False
            
        # Scale features
        X_scaled = scaler.transform(X)
        
        # Update model using partial_fit
        model.partial_fit(X_scaled, y)
        
        # Evaluate
        y_pred = model.predict(X_scaled)
        mse = mean_squared_error(y, y_pred)
        r2 = r2_score(y, y_pred)
        
        logger.info(f"Model updated - MSE: {mse:.2f}, R²: {r2:.2f}")
        
        # Save updated model
        with open(SGD_MODEL_PATH, 'wb') as f:
            pickle.dump(model, f)
            
        logger.info(f"Updated SGD model saved to {SGD_MODEL_PATH}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating SGD model: {e}")
        return False

if __name__ == "__main__":
    # This script assumes models will be uploaded manually
    # It only updates the SGD model if it already exists
    update_sgd_model()
