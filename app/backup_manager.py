import os
import json
import shutil
import zipfile
from datetime import datetime
import time

from .data_manager import ensure_data_dir_exists, HISTORICAL_DATA_DIR
from .model_loader import ensure_model_dir_exists

def create_backup(backup_dir=None):
    """Create a backup of models and historical data"""
    if backup_dir is None:
        # Default to a folder in the user's home directory
        backup_dir = os.path.join(os.path.expanduser("~"), "aqi_forecast_backups")
    
    # Ensure backup directory exists
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Create timestamped backup folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"aqi_forecast_backup_{timestamp}")
    os.makedirs(backup_path)
    
    # Ensure our app directories exist
    ensure_data_dir_exists()
    ensure_model_dir_exists()
    
    # Path to models directory
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    
    # Create backup of models
    models_backup_dir = os.path.join(backup_path, "models")
    os.makedirs(models_backup_dir)
    
    # Copy model files
    model_files = 0
    if os.path.exists(models_dir):
        for file in os.listdir(models_dir):
            if file.endswith('.pkl'):
                src = os.path.join(models_dir, file)
                dst = os.path.join(models_backup_dir, file)
                shutil.copy2(src, dst)
                model_files += 1
    
    # Create backup of historical data
    data_backup_dir = os.path.join(backup_path, "historical_data")
    os.makedirs(data_backup_dir)
    
    # Copy data files
    data_files = 0
    if os.path.exists(HISTORICAL_DATA_DIR):
        for file in os.listdir(HISTORICAL_DATA_DIR):
            if file.endswith('.csv') or file.endswith('.json'):
                src = os.path.join(HISTORICAL_DATA_DIR, file)
                dst = os.path.join(data_backup_dir, file)
                shutil.copy2(src, dst)
                data_files += 1
    
    # Create a manifest file with backup details
    manifest = {
        "timestamp": timestamp,
        "datetime": datetime.now().isoformat(),
        "unix_time": int(time.time()),
        "model_files": model_files,
        "data_files": data_files
    }
    
    with open(os.path.join(backup_path, "manifest.json"), 'w') as f:
        json.dump(manifest, f, indent=2)
    
    # Create a zip archive
    zip_path = os.path.join(backup_dir, f"aqi_forecast_backup_{timestamp}.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(backup_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, backup_path)
                zipf.write(file_path, arcname)
    
    # Remove the temporary directory
    shutil.rmtree(backup_path)
    
    print(f"✅ Backup created: {zip_path}")
    print(f"Models: {model_files}, Data files: {data_files}")
    
    return zip_path

def restore_backup(backup_path):
    """Restore models and historical data from a backup"""
    if not os.path.exists(backup_path):
        print(f"⚠️ Backup file not found: {backup_path}")
        return False
    
    # Create a temporary directory for extraction
    temp_dir = os.path.join(os.path.dirname(backup_path), "temp_restore")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    try:
        # Extract the zip file
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            zipf.extractall(temp_dir)
        
        # Verify the manifest
        manifest_path = os.path.join(temp_dir, "manifest.json")
        if not os.path.exists(manifest_path):
            print("⚠️ Invalid backup: manifest.json not found")
            return False
        
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        print(f"📦 Restoring backup from {manifest.get('datetime', 'unknown date')}")
        
        # Restore models
        models_src_dir = os.path.join(temp_dir, "models")
        models_dst_dir = os.path.join(os.path.dirname(__file__), "models")
        
        if not os.path.exists(models_dst_dir):
            os.makedirs(models_dst_dir)
        
        model_files = 0
        if os.path.exists(models_src_dir):
            for file in os.listdir(models_src_dir):
                if file.endswith('.pkl'):
                    src = os.path.join(models_src_dir, file)
                    dst = os.path.join(models_dst_dir, file)
                    shutil.copy2(src, dst)
                    model_files += 1
        
        # Restore historical data
        data_src_dir = os.path.join(temp_dir, "historical_data")
        data_dst_dir = HISTORICAL_DATA_DIR
        
        if not os.path.exists(data_dst_dir):
            os.makedirs(data_dst_dir)
        
        data_files = 0
        if os.path.exists(data_src_dir):
            for file in os.listdir(data_src_dir):
                if file.endswith('.csv') or file.endswith('.json'):
                    src = os.path.join(data_src_dir, file)
                    dst = os.path.join(data_dst_dir, file)
                    shutil.copy2(src, dst)
                    data_files += 1
        
        print(f"✅ Backup restored. Models: {model_files}, Data files: {data_files}")
        return True
    
    except Exception as e:
        print(f"⚠️ Error restoring backup: {e}")
        return False
    
    finally:
        # Clean up the temporary directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
