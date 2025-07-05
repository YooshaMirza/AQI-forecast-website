import os
import pandas as pd
from datetime import datetime, timedelta
import json
import time

# Path to store historical data
HISTORICAL_DATA_DIR = os.path.join(os.path.dirname(__file__), "historical_data")
HISTORY_FILE = os.path.join(HISTORICAL_DATA_DIR, "aqi_history.csv")
TRAINING_LOG_FILE = os.path.join(HISTORICAL_DATA_DIR, "training_log.json")

def ensure_data_dir_exists():
    """Ensure the historical data directory exists."""
    if not os.path.exists(HISTORICAL_DATA_DIR):
        os.makedirs(HISTORICAL_DATA_DIR)
        print(f"Created historical data directory: {HISTORICAL_DATA_DIR}")

def save_aqi_data(city, aqi_value, weather_data, date=None):
    """Save AQI and weather data to historical records."""
    ensure_data_dir_exists()
    
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # Convert weather data to a simple format for storage
    weather_summary = {}
    if weather_data is not None and isinstance(weather_data, pd.DataFrame) and not weather_data.empty:
        weather_row = weather_data.iloc[-1].to_dict()
        weather_summary = {k: round(float(v), 2) if isinstance(v, (int, float)) else v 
                          for k, v in weather_row.items()}
    
    # Create or load existing data
    if os.path.exists(HISTORY_FILE):
        try:
            df = pd.read_csv(HISTORY_FILE)
        except Exception as e:
            print(f"Error reading history file: {e}")
            df = pd.DataFrame(columns=['date', 'city', 'aqi', 'weather_data'])
    else:
        df = pd.DataFrame(columns=['date', 'city', 'aqi', 'weather_data'])
    
    # Add new data
    new_row = {
        'date': date,
        'city': city.lower(),
        'aqi': float(aqi_value),
        'weather_data': json.dumps(weather_summary)
    }
    
    # Check if we already have this date/city
    existing = df[(df['date'] == date) & (df['city'] == city.lower())]
    
    if len(existing) > 0:
        # Update existing record
        idx = existing.index[0]
        df.at[idx, 'aqi'] = float(aqi_value)
        df.at[idx, 'weather_data'] = json.dumps(weather_summary)
    else:
        # Append new record
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    # Save back to file
    df.to_csv(HISTORY_FILE, index=False)
    print(f"✅ Saved AQI data for {city} on {date}")
    return True

def get_historical_data(city=None, days=30):
    """Get historical AQI data for a city or all cities."""
    ensure_data_dir_exists()
    
    if not os.path.exists(HISTORY_FILE):
        return pd.DataFrame(columns=['date', 'city', 'aqi', 'weather_data'])
    
    try:
        df = pd.read_csv(HISTORY_FILE)
        
        # Filter by date (last X days)
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        df = df[df['date'] >= cutoff_date]
        
        # Filter by city if specified
        if city:
            df = df[df['city'] == city.lower()]
            
        return df
    except Exception as e:
        print(f"Error reading historical data: {e}")
        return pd.DataFrame(columns=['date', 'city', 'aqi', 'weather_data'])

def log_training_event(cities=None, metrics=None):
    """Log a training event with timestamps and performance metrics."""
    ensure_data_dir_exists()
    
    # Initialize or load training log
    if os.path.exists(TRAINING_LOG_FILE):
        try:
            with open(TRAINING_LOG_FILE, 'r') as f:
                training_log = json.load(f)
        except:
            training_log = {"training_events": []}
    else:
        training_log = {"training_events": []}
    
    # Create new training event entry
    training_event = {
        "timestamp": datetime.now().isoformat(),
        "unix_time": int(time.time()),
        "cities_trained": cities if cities else "all",
        "metrics": metrics if metrics else {}
    }
    
    # Add to log
    training_log["training_events"].append(training_event)
    
    # Save back to file
    with open(TRAINING_LOG_FILE, 'w') as f:
        json.dump(training_log, f, indent=2)
    
    print(f"✅ Logged training event at {training_event['timestamp']}")
    return True

def get_last_training_time():
    """Get the timestamp of the last training event."""
    ensure_data_dir_exists()
    
    if not os.path.exists(TRAINING_LOG_FILE):
        return None
    
    try:
        with open(TRAINING_LOG_FILE, 'r') as f:
            training_log = json.load(f)
        
        if training_log["training_events"]:
            return training_log["training_events"][-1]["timestamp"]
        return None
    except:
        return None
