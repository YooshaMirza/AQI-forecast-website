#!/usr/bin/env python3
"""
Setup GitHub Integration for AQI Forecast App

This script helps set up the GitHub integration for storing data and models.
It guides the user through the process of:
1. Creating a GitHub Personal Access Token (PAT)
2. Setting up a GitHub repository for data storage
3. Configuring local environment variables
4. Testing the GitHub integration

Usage:
    python setup_github_integration.py

Note: This script does not store your token. It only helps you set it up.
"""

import os
import sys
import json
import getpass
import requests
from pathlib import Path

# Add parent directory to path for importing app modules
sys.path.append(str(Path(__file__).parent.parent))

# Import GitHub storage module
try:
    from app.github_storage import save_file_to_github, download_file_from_github
except ImportError:
    print("❌ Failed to import GitHub storage module.")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)

def display_banner():
    """Display a nice banner for the setup script"""
    print("\n" + "=" * 80)
    print("🚀 GitHub Integration Setup for AQI Forecast App")
    print("=" * 80)
    print("""
This script will help you set up GitHub integration for your AQI Forecast App.
This integration allows your app to store models and data on GitHub,
ensuring data persistence even when deployed on platforms like Render.

What this script will help you with:
  1. Creating a GitHub Personal Access Token (PAT)
  2. Configuring your repository for data storage
  3. Setting up local environment variables
  4. Testing the GitHub connection
    """)
    print("=" * 80 + "\n")

def get_token_instructions():
    """Provide instructions for creating a GitHub token"""
    print("\n📝 GitHub Personal Access Token (PAT) Creation Steps:")
    print("-" * 60)
    print("1. Go to https://github.com/settings/tokens")
    print("2. Click 'Generate new token' > 'Generate new token (classic)'")
    print("3. Add a note like 'AQI Forecast App Data Storage'")
    print("4. Set expiration as needed (recommend at least 90 days)")
    print("5. Select the following scopes:")
    print("   - repo (Full control of private repositories)")
    print("6. Click 'Generate token'")
    print("7. Copy the token (You will NOT be able to see it again!)\n")

def get_repository_instructions():
    """Provide instructions for creating or selecting a GitHub repository"""
    print("\n📦 GitHub Repository Setup:")
    print("-" * 60)
    print("You'll need a GitHub repository to store your app's data and models.")
    print("\nOptions:")
    print("1. Use your existing app repository (recommended for simplicity)")
    print("   - Format: username/repo-name")
    print("   - Example: johndoe/aqi-forecast-app")
    print("\n2. Create a separate repository for data:")
    print("   a. Go to https://github.com/new")
    print("   b. Name it something like 'aqi-forecast-data'")
    print("   c. Make it private if you prefer")
    print("   d. Initialize with a README")
    print("   e. Create repository\n")

def setup_github_integration():
    """Main setup function"""
    display_banner()
    
    # Step 1: GitHub Token
    print("\n🔑 Step 1: GitHub Personal Access Token")
    print("-" * 60)
    
    get_token_instructions()
    input("Press Enter when you're ready to proceed...")
    
    token = getpass.getpass("Enter your GitHub Personal Access Token (will not be displayed): ")
    if not token:
        print("❌ No token provided. Exiting setup.")
        return False
    
    # Step 2: GitHub Repository
    print("\n🏢 Step 2: GitHub Repository Configuration")
    print("-" * 60)
    
    get_repository_instructions()
    repo = input("Enter your GitHub repository (format: username/repo-name): ")
    
    if not repo or "/" not in repo:
        print("❌ Invalid repository format. It should be 'username/repo-name'.")
        return False
    
    # Step 3: Test the connection
    print("\n🔄 Step 3: Testing GitHub Connection")
    print("-" * 60)
    
    # Set environment variables temporarily for testing
    os.environ['GITHUB_TOKEN'] = token
    os.environ['GITHUB_REPO'] = repo
    
    # Create a test file
    test_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                  "temp_github_test.txt")
    with open(test_file_path, 'w') as f:
        f.write(f"GitHub Integration Test\nTimestamp: {os.popen('date').read().strip()}")
    
    print("Testing connection by uploading a test file...")
    success = save_file_to_github(
        test_file_path,
        "github_integration_test.txt",
        "Test GitHub Integration Setup"
    )
    
    # Clean up temp file
    if os.path.exists(test_file_path):
        os.remove(test_file_path)
    
    if not success:
        print("❌ GitHub connection test failed. Please check your token and repository.")
        return False
    
    # Step 4: Save configuration instructions
    print("\n💾 Step 4: Saving Configuration")
    print("-" * 60)
    print("\nTo use these settings permanently, you need to set environment variables.")
    
    # For Render deployment
    print("\n📋 For Render deployment:")
    print("1. Go to your app's dashboard on Render")
    print("2. Click on 'Environment' tab")
    print("3. Add these environment variables:")
    print(f"   GITHUB_TOKEN = {token[:4]}...{token[-4:]} (your token)")
    print(f"   GITHUB_REPO = {repo}")
    
    # For local development
    env_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                ".env")
    
    print("\n📋 For local development:")
    print(f"Add these variables to your {env_file_path} file:")
    print(f"GITHUB_TOKEN={token}")
    print(f"GITHUB_REPO={repo}")
    
    create_env = input("\nWould you like to create/update the .env file now? (y/n): ")
    if create_env.lower() == 'y':
        try:
            with open(env_file_path, 'w') as f:
                f.write(f"GITHUB_TOKEN={token}\n")
                f.write(f"GITHUB_REPO={repo}\n")
            print(f"✅ Created .env file at {env_file_path}")
            
            # Add .env to .gitignore if it's not already there
            gitignore_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                         ".gitignore")
            
            add_to_gitignore = True
            if os.path.exists(gitignore_path):
                with open(gitignore_path, 'r') as f:
                    if '.env' in f.read():
                        add_to_gitignore = False
            
            if add_to_gitignore:
                with open(gitignore_path, 'a+') as f:
                    f.write("\n# Environment variables\n.env\n")
                print("✅ Added .env to .gitignore")
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
    
    print("\n✅ GitHub Integration Setup Complete!")
    print("\nYour AQI Forecast App is now configured to store data and models on GitHub.")
    print("This ensures that your data persists even when deployed on platforms with ephemeral storage.")
    
    return True

if __name__ == "__main__":
    setup_github_integration()
