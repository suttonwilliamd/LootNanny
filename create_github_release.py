#!/usr/bin/env python3

import os
import requests
import json
import mimetypes
from pathlib import Path

# Configuration
GITHUB_TOKEN = ""  # Replace with your actual GitHub token
REPO_OWNER = "suttonwilliamd"
REPO_NAME = "LootNanny"
RELEASE_VERSION = "0.0.11w"
EXECUTABLE_PATH = "dist/LootNanny-0.0.11w-p3_13_9.exe"

# GitHub API headers
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def create_github_release():
    """Create a GitHub release"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases"
    
    release_data = {
        "tag_name": RELEASE_VERSION,
        "name": RELEASE_VERSION,
        "body": f"Release {RELEASE_VERSION} of LootNanny",
        "draft": False,
        "prerelease": False
    }
    
    print(f"Creating GitHub release {RELEASE_VERSION}...")
    response = requests.post(url, headers=headers, data=json.dumps(release_data))
    
    if response.status_code == 201:
        print("Release created successfully!")
        return response.json()
    else:
        print(f"Failed to create release. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def upload_asset(release_id, asset_path):
    """Upload an asset to the release"""
    url = f"https://uploads.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/{release_id}/assets?name={os.path.basename(asset_path)}"
    
    # Guess the content type
    content_type, _ = mimetypes.guess_type(asset_path)
    if content_type is None:
        content_type = "application/octet-stream"
    
    headers_with_content_type = headers.copy()
    headers_with_content_type["Content-Type"] = content_type
    
    print(f"Uploading {asset_path}...")
    with open(asset_path, "rb") as file:
        response = requests.post(url, headers=headers_with_content_type, data=file)
    
    if response.status_code == 201:
        print("Asset uploaded successfully!")
        return True
    else:
        print(f"Failed to upload asset. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def main():
    # Check if executable exists
    if not os.path.exists(EXECUTABLE_PATH):
        print(f"Error: Executable not found at {EXECUTABLE_PATH}")
        return
    
    # Create release
    release_info = create_github_release()
    if not release_info:
        print("Failed to create release")
        return
    
    release_id = release_info["id"]
    print(f"Release ID: {release_id}")
    
    # Upload asset
    if upload_asset(release_id, EXECUTABLE_PATH):
        print("Release and asset creation completed successfully!")
    else:
        print("Failed to upload asset")

if __name__ == "__main__":
    main()