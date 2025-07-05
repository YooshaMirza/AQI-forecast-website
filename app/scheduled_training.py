import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import threading
import schedule
from sklearn.metrics import mean_squared_error, mean_absolute_error

from .backend_utils import get_lat_lon, get_realtime_aqi, fetch_nasa_weather
from .model_loader import load_or_init_sgd, save_sgd_model
from .data_manager import get_historical_data, log_training_event, HISTORICAL_DATA_DIR
from .github_storage import save_file_to_github
from .backup_manager import create_backup

def train_on_historical_data(cities=None):
    """Train the model on all historical data for specified cities or all cities."""
    print(f"🔄 Starting scheduled model training at {datetime.now()}")
    
    # Load historical data
    history_df = get_historical_data(days=60)  # Get data for the last 60 days
    
    if history_df.empty:
        print("❌ No historical data available for training")
        return False
    
    # Filter by cities if specified
    if cities:
        history_df = history_df[history_df['city'].isin([c.lower() for c in cities])]
        if history_df.empty:
            print(f"❌ No historical data available for specified cities: {', '.join(cities)}")
            return False
    
    # Get unique cities in the data
    unique_cities = history_df['city'].unique()
    print(f"📊 Training on data from {len(unique_cities)} cities: {', '.join(unique_cities)}")
    
    # Load the current model
    model, scaler = load_or_init_sgd()
    
    # Process each city's data to extract features and targets
    all_features = []
    all_targets = []
    metrics = {}
    
    for city in unique_cities:
        city_data = history_df[history_df['city'] == city].sort_values('date')
        
        # Extract weather data and AQI values
        city_features = []
        city_targets = []
        
        for _, row in city_data.iterrows():
            try:
                # Parse weather data from JSON
                import json
                weather_data = json.loads(row['weather_data'])
                
                # Extract numeric features only
                feature_values = []
                for k, v in weather_data.items():
                    if isinstance(v, (int, float)) and not pd.isna(v):
                        feature_values.append(v)
                
                # If we have features and a valid AQI target
                if feature_values and not pd.isna(row['aqi']):
                    city_features.append(feature_values)
                    city_targets.append(row['aqi'])
            except Exception as e:
                print(f"Error processing row for {city}: {e}")
        
        # If we have data for this city
        if city_features and city_targets:
            # Ensure all feature vectors have the same length
            min_length = min(len(f) for f in city_features)
            city_features = [f[:min_length] for f in city_features]
            
            all_features.extend(city_features)
            all_targets.extend(city_targets)
            
            print(f"✅ Added {len(city_features)} training samples for {city}")
    
    # If we have training data
    if all_features and all_targets:
        try:
            # Convert to numpy arrays
            X = np.array(all_features)
            y = np.array(all_targets)
            
            # Scale features
            X_scaled = scaler.fit_transform(X)
            
            # Train the model
            model.partial_fit(X_scaled, y)
            
            # Calculate training metrics
            y_pred = model.predict(X_scaled)
            mse = mean_squared_error(y, y_pred)
            mae = mean_absolute_error(y, y_pred)
            
            metrics = {
                "mse": round(float(mse), 4),
                "mae": round(float(mae), 4),
                "training_samples": len(y)
            }
            
            print(f"📈 Training metrics - MSE: {metrics['mse']}, MAE: {metrics['mae']}")
            
            # Save the updated model
            save_sgd_model(model, scaler)
            print("💾 Model saved successfully")
            
            # Log the training event
            log_training_event(cities=list(unique_cities), metrics=metrics)
            
            # Save model and data files to GitHub for persistence
            try:
                # Paths to the model files
                model_dir = os.path.join(os.path.dirname(__file__), "models")
                sgd_model_path = os.path.join(model_dir, "sgd_model.pkl")
                scaler_path = os.path.join(model_dir, "scaler.pkl")
                
                # Try to save models to GitHub
                if os.environ.get('GITHUB_TOKEN'):
                    print("🔄 Saving models and data to GitHub...")
                    save_file_to_github(
                        sgd_model_path,
                        "models/sgd_model.pkl",
                        f"Update SGD model - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    save_file_to_github(
                        scaler_path,
                        "models/scaler.pkl",
                        f"Update scaler - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    
                    # Save historical data files
                    history_file = os.path.join(HISTORICAL_DATA_DIR, "aqi_history.csv")
                    log_file = os.path.join(HISTORICAL_DATA_DIR, "training_log.json")
                    
                    if os.path.exists(history_file):
                        save_file_to_github(
                            history_file,
                            "historical_data/aqi_history.csv",
                            f"Update history data - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        )
                    
                    if os.path.exists(log_file):
                        save_file_to_github(
                            log_file,
                            "historical_data/training_log.json",
                            f"Update training log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        )
                else:
                    print("⚠️ GitHub token not set - skipping GitHub backup")
                
                # Create a local backup every week (on Sunday)
                if datetime.now().weekday() == 6:  # Sunday
                    try:
                        create_backup()
                        print("✅ Weekly backup created")
                    except Exception as e:
                        print(f"⚠️ Error creating backup: {e}")
            except Exception as e:
                print(f"⚠️ Error during backup process: {e}")
            
            return True
        except Exception as e:
            print(f"❌ Error during model training: {e}")
            return False
    else:
        print("❌ Not enough valid data for training")
        return False

def scheduled_training():
    """Run model training on a schedule."""
    # This function is meant to be run in a background thread
    print("🔄 Scheduled training thread started")
    
    # Set up the schedule - train once per day at 2:00 AM
    schedule.every().day.at("02:00").do(train_on_historical_data)
    
    # For testing - also run once on startup after a short delay
    time.sleep(10)  # Wait 10 seconds after startup
    train_on_historical_data()  # Run once now
    
    # Keep the schedule running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def start_scheduler():
    """Start the scheduled training in a background thread."""
    training_thread = threading.Thread(target=scheduled_training)
    training_thread.daemon = True  # Thread will exit when the main program exits
    training_thread.start()
    print("✅ Scheduled training started in background thread")
    return training_thread
