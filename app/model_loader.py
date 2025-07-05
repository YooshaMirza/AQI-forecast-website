import os
import joblib
from sklearn.linear_model import SGDRegressor
from sklearn.preprocessing import StandardScaler

def ensure_model_dir_exists():
    """Ensure the models directory exists."""
    model_dir = os.path.join(os.path.dirname(__file__), "models")
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
        print(f"Created models directory: {model_dir}")

def load_or_init_sgd(model_path=os.path.join(os.path.dirname(__file__), "models/sgd_model.pkl"), 
                  scaler_path=os.path.join(os.path.dirname(__file__), "models/scaler.pkl")):
    ensure_model_dir_exists()
    
    try:
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            model = joblib.load(model_path)
            scaler = joblib.load(scaler_path)
            print("✅ Successfully loaded existing SGD model and scaler")
            return model, scaler
    except Exception as e:
        print(f"⚠️ Error loading SGD model or scaler: {e}")
        print("Creating new SGD model and scaler instead")
    
    # Create a new model and scaler if loading failed or files don't exist
    model = SGDRegressor(max_iter=1000, tol=1e-3)
    scaler = StandardScaler()
    return model, scaler

def save_sgd_model(model, scaler, model_path=os.path.join(os.path.dirname(__file__), "models/sgd_model.pkl"), 
                   scaler_path=os.path.join(os.path.dirname(__file__), "models/scaler.pkl")):
    ensure_model_dir_exists()
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)

def classify_aqi(aqi):
    if aqi <= 50:
        return "🟢 Good – Air quality is considered satisfactory."
    elif aqi <= 100:
        return "🟡 Satisfactory – Minor discomfort to sensitive people"
    elif aqi <= 200:
        return "🟠 Moderate – May cause breathing discomfort to people with lung disease"
    elif aqi <= 300:
        return "🔴 Poor – May cause discomfort to most people"
    elif aqi <= 400:
        return "🟣 Very Poor – May cause respiratory issues"
    else:
        return "⚫ Severe – Affects healthy people and seriously impacts those with existing diseases"
