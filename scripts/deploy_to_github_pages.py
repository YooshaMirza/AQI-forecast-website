pip install -r requirements.txt#!/usr/bin/env python3
"""
Deploy AQI Forecast App to GitHub Pages

This script helps you deploy your AQI Forecast application to GitHub Pages.
It handles:
1. Setting up the GitHub repository for GitHub Pages
2. Creating a static version of your application
3. Testing the static site locally
4. Pushing the static site to GitHub Pages branch (gh-pages)

Usage:
    python deploy_to_github_pages.py
"""

import os
import sys
import subprocess
import webbrowser
import http.server
import socketserver
import threading
import time
from pathlib import Path

# Add parent directory to path for importing app modules
sys.path.append(str(Path(__file__).parent.parent))

def display_banner():
    """Display a nice banner for the deploy script"""
    print("\n" + "=" * 80)
    print("🚀 Deploy AQI Forecast App to GitHub Pages")
    print("=" * 80)
    print("""
This script will help you deploy your AQI Forecast App to GitHub Pages.
The deployed app will be a static version of your Flask application,
capable of showing pre-generated forecasts for selected cities.

Steps this script will perform:
  1. Check if your GitHub repository is configured
  2. Create a static version of your application
  3. Allow you to test the static site locally
  4. Push the static site to your gh-pages branch
    """)
    print("=" * 80 + "\n")

def run_command(command, explanation=None):
    """Run a shell command and print output"""
    if explanation:
        print(f"\n{explanation}")
    
    print(f"\n$ {command}\n")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            text=True,
            capture_output=True
        )
        if result.stdout:
            print(result.stdout)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False, e.stderr

def check_git_repo():
    """Check if the current directory is a git repository"""
    return os.path.exists('.git')

def check_github_remote():
    """Check if a GitHub remote is configured"""
    success, output = run_command('git remote -v', "Checking Git remotes...")
    if not success:
        return None
    
    for line in output.split('\n'):
        if 'github.com' in line and '(fetch)' in line:
            parts = line.split()
            if len(parts) >= 2:
                remote_url = parts[1]
                if remote_url.endswith('.git'):
                    remote_url = remote_url[:-4]
                
                if 'github.com' in remote_url:
                    # Extract username/repo from URL
                    if 'github.com/' in remote_url:
                        repo = remote_url.split('github.com/')[-1]
                        return repo
    
    return None

def serve_static_site():
    """Serve the static site locally for testing"""
    static_site_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                  "static_site")
    
    if not os.path.exists(static_site_dir):
        print("❌ Static site not found. Please build it first.")
        return
    
    # Choose a port
    port = 8000
    handler = http.server.SimpleHTTPRequestHandler
    
    # Change directory to the static site
    os.chdir(static_site_dir)
    
    # Start the server in a separate thread
    server = socketserver.TCPServer(("", port), handler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    print(f"\n✅ Serving static site at http://localhost:{port}")
    print("Press Ctrl+C to stop the server when you're done testing.\n")
    
    # Open browser
    webbrowser.open(f"http://localhost:{port}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.shutdown()
        print("\n✅ Server stopped.")

def build_static_site():
    """Build the static site"""
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                              "build_static_site.py")
    
    success, _ = run_command(f'python "{script_path}"', 
                           "Building static site...")
    
    if not success:
        print("❌ Failed to build static site.")
        return False
    
    return True

def push_to_gh_pages():
    """Push the static site to gh-pages branch"""
    static_site_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                  "static_site")
    
    if not os.path.exists(static_site_dir):
        print("❌ Static site not found. Please build it first.")
        return False
    
    # Create and push to gh-pages branch
    commands = [
        f'cd "{static_site_dir}" && git init',
        f'cd "{static_site_dir}" && git add .',
        f'cd "{static_site_dir}" && git commit -m "Update GitHub Pages site"',
        f'cd "{static_site_dir}" && git branch -M gh-pages',
        f'cd "{static_site_dir}" && git remote add origin "$(git -C "{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}" remote get-url origin)"',
        f'cd "{static_site_dir}" && git push -f origin gh-pages'
    ]
    
    print("\n🚀 Pushing to gh-pages branch...")
    
    for command in commands:
        success, _ = run_command(command)
        if not success:
            print("❌ Failed to push to gh-pages branch.")
            return False
    
    print("✅ Successfully pushed to gh-pages branch.")
    return True

def deploy_to_github_pages():
    """Main deployment function"""
    display_banner()
    
    # Step 1: Check Git repository
    print("\n🔍 Step 1: Checking Git Repository")
    print("-" * 60)
    
    if not check_git_repo():
        print("❌ Not a Git repository. Please run this script from your project root.")
        return False
    
    github_repo = check_github_remote()
    if not github_repo:
        print("❌ No GitHub remote found. Please set up a GitHub remote first.")
        return False
    
    print(f"✅ Found GitHub repository: {github_repo}")
    
    # Step 2: Build static site
    print("\n🏗️ Step 2: Building Static Site")
    print("-" * 60)
    
    if not build_static_site():
        return False
    
    # Step 3: Test static site locally
    print("\n🧪 Step 3: Testing Static Site Locally")
    print("-" * 60)
    
    test_local = input("Would you like to test the static site locally? (y/n): ")
    if test_local.lower() == 'y':
        serve_static_site()
    
    # Step 4: Push to GitHub Pages
    print("\n🚀 Step 4: Deploying to GitHub Pages")
    print("-" * 60)
    
    deploy = input("Ready to deploy to GitHub Pages? (y/n): ")
    if deploy.lower() != 'y':
        print("Deployment cancelled.")
        return False
    
    if push_to_gh_pages():
        print("\n✅ Deployment Complete!")
        print(f"Your site should be available at: https://{github_repo.split('/')[0]}.github.io/{github_repo.split('/')[1]}")
        print("Note: It may take a few minutes for the site to be available.")
        
        # Ask user if they want to configure GitHub Pages in repository settings
        print("\n⚙️ Final Step: Configure GitHub Pages in Repository Settings")
        print("To complete setup, go to your repository settings:")
        print(f"https://github.com/{github_repo}/settings/pages")
        print("and ensure the source is set to 'gh-pages' branch.")
        
        open_settings = input("Would you like to open this page now? (y/n): ")
        if open_settings.lower() == 'y':
            webbrowser.open(f"https://github.com/{github_repo}/settings/pages")
        
        return True
    
    return False

if __name__ == "__main__":
    deploy_to_github_pages()
