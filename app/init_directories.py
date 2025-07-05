import os

def ensure_directories():
    """Ensure all required directories exist."""
    dirs = [
        "static",
        "app/models",
        "app/historical_data"
    ]
    
    for d in dirs:
        dir_path = os.path.join(os.path.dirname(__file__), d)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"Created directory: {dir_path}")
    
    return True

if __name__ == "__main__":
    # This script can be run directly to create directories
    ensure_directories()
    print("All required directories have been created.")
