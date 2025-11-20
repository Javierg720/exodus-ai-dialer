#!/usr/bin/env python3
import requests
import re
import sys

# VICIdial API credentials
base_url = "https://merchantfundexp.cloudautodialer.in/vicidial"
api_url = f"{base_url}/non_agent_api.php"

# Try using the agent API instead
print("Attempting to use VICIdial API to clone user...")

# First, let's try to get user information via API
params = {
    'source': 'test',
    'user': 'root',
    'pass': '3L5v3XzKXC724bM8au8R',
    'function': 'user_info',
    'search_user': 'shiva37284'
}

try:
    response = requests.get(api_url, params=params, verify=False)
    print(f"API Response Status: {response.status_code}")
    print(f"API Response: {response.text[:500]}")
    
    # Try alternative: direct database query via webadmin
    # Let's try the proper VICIdial login with their specific auth
    session = requests.Session()
    session.verify = False
    
    # VICIdial uses specific authentication - try their welcome page
    welcome_url = f"{base_url}/welcome.php"
    login_data = {
        'VD_login': root_user,
        'VD_pass': root_pass,
        'SUBMIT': 'SUBMIT'
    }
    
    print("\nTrying alternative login method...")
    login_resp = session.post(welcome_url, data=login_data)
    print(f"Welcome page status: {login_resp.status_code}")
    
    # Save for debugging
    with open('/home/user/vicidial_welcome_response.html', 'w') as f:
        f.write(login_resp.text[:2000])
    
    print("\nSaved response to /home/user/vicidial_welcome_response.html")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

