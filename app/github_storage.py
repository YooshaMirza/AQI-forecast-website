import os
import base64
import json
import requests
from datetime import datetime

# Replace these with your GitHub details
# These would normally be stored as environment variables
GITHUB_TOKEN = None  # Set this as an environment variable in Render dashboard
GITHUB_REPO = "username/aqi-forecast-storage"  # Change to your repo

def get_github_token():
    """Get GitHub token from environment variable"""
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("⚠️ Warning: GITHUB_TOKEN environment variable not set.")
        print("Data will not be saved to GitHub.")
    return token

def get_github_repo():
    """Get GitHub repo from environment variable or use default"""
    return os.environ.get('GITHUB_REPO', GITHUB_REPO)

def save_file_to_github(file_path, github_path, commit_message=None):
    """Save a file to GitHub repository"""
    token = get_github_token()
    if not token:
        return False
    
    repo = get_github_repo()
    if not repo:
        return False
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"⚠️ File does not exist: {file_path}")
        return False
    
    # Read file content
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # Encode content as base64
    encoded_content = base64.b64encode(content).decode('utf-8')
    
    # Default commit message
    if not commit_message:
        commit_message = f"Update {github_path} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Get the SHA of the file if it exists
    sha = None
    try:
        url = f"https://api.github.com/repos/{repo}/contents/{github_path}"
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            sha = response.json()['sha']
    except Exception as e:
        print(f"Error checking if file exists: {e}")
    
    # Prepare the request data
    data = {
        'message': commit_message,
        'content': encoded_content
    }
    
    # Include SHA if updating an existing file
    if sha:
        data['sha'] = sha
    
    # Make the request to GitHub API
    try:
        url = f"https://api.github.com/repos/{repo}/contents/{github_path}"
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        response = requests.put(url, json=data, headers=headers)
        if response.status_code in [200, 201]:
            print(f"✅ Successfully saved to GitHub: {github_path}")
            return True
        else:
            print(f"⚠️ Failed to save to GitHub: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        print(f"⚠️ Error saving to GitHub: {e}")
        return False

def download_file_from_github(github_path, local_path):
    """Download a file from GitHub repository"""
    token = get_github_token()
    if not token:
        return False
    
    repo = get_github_repo()
    if not repo:
        return False
    
    try:
        url = f"https://api.github.com/repos/{repo}/contents/{github_path}"
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            # Ensure directory exists
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # Decode content and save to file
            content = base64.b64decode(response.json()['content'])
            with open(local_path, 'wb') as f:
                f.write(content)
            print(f"✅ Successfully downloaded from GitHub: {github_path} -> {local_path}")
            return True
        else:
            print(f"⚠️ Failed to download from GitHub: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        print(f"⚠️ Error downloading from GitHub: {e}")
        return False
