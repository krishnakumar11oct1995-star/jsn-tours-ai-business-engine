"""
Direct Netlify API Deployment Script for Jai Srimannarayana Tours & Travels.

This script directly publishes updates to https://jaisrimannarayana.netlify.app
via Netlify's official REST API without any manual dragging or browser interaction.

Requirements in .env:
- NETLIFY_AUTH_TOKEN: Personal Access Token from Netlify Dashboard (User Settings > Applications)
- NETLIFY_SITE_ID: Site ID from Netlify Site Configuration (General > Site details)
"""

import os
import sys
import json
import time
import requests
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
load_dotenv(os.path.join(BASE_DIR, ".env"))

ZIP_FILE = os.path.join(BASE_DIR, "website_hostinger.zip")
NETLIFY_AUTH_TOKEN = os.getenv("NETLIFY_AUTH_TOKEN")
NETLIFY_SITE_ID = os.getenv("NETLIFY_SITE_ID")


def deploy(rebuild=True):
    print("=" * 70)
    print("🚀 DIRECT NETLIFY API DEPLOYMENT — JAI SRIMANNARAYANA")
    print("=" * 70)

    # 1. Check Credentials
    if not NETLIFY_AUTH_TOKEN:
        print("\n❌ Error: NETLIFY_AUTH_TOKEN is missing in your .env file.")
        print("👉 How to get it:")
        print("   1. Open https://app.netlify.com/user/applications#personal-access-tokens")
        print("   2. Click 'New access token', give it a name, and copy the token.")
        print("   3. Add to your .env: NETLIFY_AUTH_TOKEN=your_token_here\n")
        return False

    if not NETLIFY_SITE_ID:
        print("\n❌ Error: NETLIFY_SITE_ID is missing in your .env file.")
        print("👉 How to get it:")
        print("   1. Open your site on Netlify: https://app.netlify.com/sites/jaisrimannarayana/configuration/general")
        print("   2. Under 'Site details', copy the 'Site ID' (UUID format).")
        print("   3. Add to your .env: NETLIFY_SITE_ID=your_site_id_here\n")
        return False

    # 2. Re-build site if requested
    if rebuild:
        print("\n[1/3] Building fresh static package...")
        from build_hostinger_site import build_site
        build_site()

    if not os.path.exists(ZIP_FILE):
        print(f"\n❌ Error: Archive not found at {ZIP_FILE}")
        return False

    zip_size_mb = round(os.path.getsize(ZIP_FILE) / (1024 * 1024), 2)
    print(f"\n[2/3] Preparing deployment archive: {ZIP_FILE} ({zip_size_mb} MB)...")

    # 3. Upload directly via Netlify API
    api_url = f"https://api.netlify.com/api/v1/sites/{NETLIFY_SITE_ID}/deploys"
    headers = {
        "Authorization": f"Bearer {NETLIFY_AUTH_TOKEN}",
        "Content-Type": "application/zip",
    }

    print(f"[3/3] Uploading archive to Netlify API endpoint...")
    start_time = time.time()

    try:
        with open(ZIP_FILE, "rb") as fp:
            response = requests.post(api_url, data=fp, headers=headers, timeout=60)

        elapsed = round(time.time() - start_time, 2)

        if response.status_code in [200, 201]:
            data = response.json()
            deploy_id = data.get("id")
            state = data.get("state")
            ssl_url = data.get("ssl_url", "https://jaisrimannarayana.netlify.app")
            
            print(f"\n{'='*70}")
            print(f"🎉 SUCCESS! DEPLOYED TO NETLIFY IN {elapsed}s")
            print(f"{'='*70}")
            print(f"• Deploy ID:   {deploy_id}")
            print(f"• State:       {state.upper()}")
            print(f"• Live URL:    {ssl_url}")
            print(f"• Target Site: https://jaisrimannarayana.netlify.app")
            print(f"{'='*70}\n")
            return True
        else:
            print(f"\n❌ Netlify API Error (HTTP {response.status_code}):")
            print(response.text)
            return False

    except Exception as e:
        print(f"\n❌ Deployment request failed: {e}")
        return False


if __name__ == "__main__":
    rebuild_flag = "--no-build" not in sys.argv
    success = deploy(rebuild=rebuild_flag)
    sys.exit(0 if success else 1)
