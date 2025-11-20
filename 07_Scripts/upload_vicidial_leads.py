#!/usr/bin/env python3
import requests
import csv
import sys
import time
from urllib.parse import urljoin

# VICIdial credentials
VICIDIAL_URL = "https://merchantfundexp.cloudautodialer.in"
API_USER = "javier"
API_PASS = "oX05mP6450c4L10"
SOURCE = "exodus_upload"

# API endpoint
API_ENDPOINT = f"{VICIDIAL_URL}/vicidial/non_agent_api.php"

def upload_lead(phone, first_name, last_name, company, email, address, city, state, zipcode, list_id="999"):
    """Upload a single lead to VICIdial via API"""
    
    params = {
        'source': SOURCE,
        'user': API_USER,
        'pass': API_PASS,
        'function': 'add_lead',
        'phone_number': phone,
        'phone_code': '1',
        'list_id': list_id,
        'first_name': first_name or '',
        'last_name': last_name or '',
        'address1': address or '',
        'city': city or '',
        'state': state or '',
        'postal_code': zipcode or '',
        'email': email or '',
        'comments': company or '',
        'dnc_check': 'N',
        'campaign_id': 'FUNDEXPRESS',
        'tz_method': 'POSTAL_CODE',
    }
    
    try:
        response = requests.get(API_ENDPOINT, params=params, verify=False, timeout=10)
        result = response.text.strip()
        
        # Check for success
        if 'SUCCESS' in result or 'ADDED' in result:
            return True, result
        else:
            return False, result
    except Exception as e:
        return False, str(e)

def process_csv(csv_file, list_id="999"):
    """Process a CSV file and upload all leads"""
    print(f"\n{'='*60}")
    print(f"Processing: {csv_file}")
    print(f"{'='*60}")
    
    success_count = 0
    error_count = 0
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for i, row in enumerate(reader, 1):
            phone = row.get('phone1', '').strip()
            
            # Skip if no phone number
            if not phone or len(phone) < 10:
                error_count += 1
                continue
            
            # Clean phone number (remove non-digits)
            phone = ''.join(filter(str.isdigit, phone))
            
            # Upload lead
            success, result = upload_lead(
                phone=phone,
                first_name=row.get('firstname', ''),
                last_name=row.get('lastname', ''),
                company=row.get('company', ''),
                email=row.get('email', ''),
                address=row.get('address1', ''),
                city=row.get('city', ''),
                state=row.get('state', ''),
                zipcode=row.get('zip', ''),
                list_id=list_id
            )
            
            if success:
                success_count += 1
                if i % 100 == 0:
                    print(f"✓ Uploaded {success_count} leads... (Row {i})")
            else:
                error_count += 1
                if 'duplicate' not in result.lower():
                    print(f"✗ Error on row {i}: {result[:100]}")
            
            # Rate limiting (avoid overwhelming API)
            if i % 50 == 0:
                time.sleep(1)
    
    print(f"\n📊 Results: {success_count} uploaded, {error_count} errors/skipped")
    return success_count, error_count

# Disable SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if __name__ == "__main__":
    lead_files = [
        '/home/user/Desktop/LEADS\/1 LMG 3k 10.17.25 (2).csv',
        '/home/user/Desktop/LEADS\/2 LMG 2k 10.17.25.csv',
        '/home/user/Desktop/LEADS\/LMG 2.5k 9.18.25(1).csv',
        '/home/user/Desktop/LEADS\/LMG 3.5k 8.25.25.csv',
        '/home/user/Desktop/LEADS\/LMG 3k 8.15.25.csv',
        '/home/user/Desktop/LEADS\/LMG 3k 09.30.25(1).csv',
        '/home/user/Desktop/LEADS\/LMG 4k 9.18.25(1).csv',
    ]
    
    total_success = 0
    total_errors = 0
    
    print("\n🚀 Starting VICIdial Lead Upload")
    print(f"📁 Files to process: {len(lead_files)}")
    
    for csv_file in lead_files:
        success, errors = process_csv(csv_file, list_id="999")
        total_success += success
        total_errors += errors
    
    print(f"\n{'='*60}")
    print(f"✅ TOTAL UPLOADED: {total_success}")
    print(f"❌ TOTAL ERRORS: {total_errors}")
    print(f"{'='*60}\n")
