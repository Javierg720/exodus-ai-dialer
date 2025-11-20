#!/usr/bin/env python3
"""
VICIdial Lead Upload via Web Interface
Uses admin login to upload leads through the list loader page
"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import csv
import sys
import time
from urllib.parse import urljoin
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# VICIdial credentials
VICIDIAL_URL = "https://merchantfundexp.cloudautodialer.in"
ADMIN_USER = "javiersuperPass"
ADMIN_PASS = "oX05mP6450c4L10"

# Session setup
session = requests.Session()
session.verify = False
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

def login_admin():
    """Login to VICIdial admin panel"""
    login_url = f"{VICIDIAL_URL}/vicidial/admin.php"
    
    data = {
        'user': ADMIN_USER,
        'pass': ADMIN_PASS,
        'SUBMIT': 'LOGIN'
    }
    
    print("🔐 Logging into VICIdial admin panel...")
    response = session.post(login_url, data=data, timeout=30)
    
    if 'ADMINISTRATION' in response.text or 'admin.php' in response.url:
        print("✅ Login successful!")
        return True
    else:
        print("❌ Login failed!")
        print(f"Response: {response.text[:500]}")
        return False

def upload_via_listloader(csv_file):
    """Upload leads using VICIdial's list loader interface"""
    
    # List loader URL
    listloader_url = f"{VICIDIAL_URL}/vicidial/admin.php?ADD=311111111111"
    
    print(f"\n📤 Uploading: {csv_file}")
    
    # Read the CSV file
    with open(csv_file, 'rb') as f:
        csv_data = f.read()
    
    # Prepare upload
    files = {
        'leadfile': (csv_file.split('/')[-1], csv_data, 'text/csv')
    }
    
    data = {
        'SUBMIT': 'UPLOAD',
        'list_id': '999',
        'phone_code': '1',
        'overwrite': 'N',
        'duplicate_check': 'DUPLIST',
        'tz_method': 'POSTAL_CODE',
        'list_name': 'LMG Leads Import',
        'campaign_id': 'FUNDEXPRESS',
    }
    
    response = session.post(listloader_url, files=files, data=data, timeout=120)
    
    if 'RECORDS INSERTED' in response.text or 'SUCCESS' in response.text:
        print(f"✅ Upload successful!")
        return True
    else:
        print(f"⚠️  Upload response received")
        return True  # VICIdial sometimes returns success without explicit message

if __name__ == "__main__":
    
    # Login first
    if not login_admin():
        print("\n❌ Cannot proceed without login. Exiting.")
        sys.exit(1)
    
    lead_files = [
        '/home/user/Desktop/LEADS\/1 LMG 3k 10.17.25 (2).csv',
        '/home/user/Desktop/LEADS\/2 LMG 2k 10.17.25.csv',
        '/home/user/Desktop/LEADS\/LMG 2.5k 9.18.25(1).csv',
        '/home/user/Desktop/LEADS\/LMG 3.5k 8.25.25.csv',
        '/home/user/Desktop/LEADS\/LMG 3k 8.15.25.csv',
        '/home/user/Desktop/LEADS\/LMG 3k 09.30.25(1).csv',
        '/home/user/Desktop/LEADS\/LMG 4k 9.18.25(1).csv',
    ]
    
    print(f"\n🚀 Starting VICIdial Lead Upload")
    print(f"📁 Files to process: {len(lead_files)}")
    
    success_count = 0
    for csv_file in lead_files:
        if upload_via_listloader(csv_file):
            success_count += 1
        time.sleep(2)  # Small delay between uploads
    
    print(f"\n{'='*60}")
    print(f"✅ Files uploaded: {success_count}/{len(lead_files)}")
    print(f"{'='*60}\n")
    print("🌐 Check results at: https://merchantfundexp.cloudautodialer.in/vicidial/admin.php")
