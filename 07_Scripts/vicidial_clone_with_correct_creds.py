#!/usr/bin/env python3
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base_url = "https://merchantfundexp.cloudautodialer.in"

# Correct admin credentials from email
admin_user = "javiersuper"
admin_pass = "oX05mP6450c4L10"

print("VICIdial User Cloning - Using Correct Admin Credentials")
print("=" * 70)
print(f"Admin: {admin_user}")
print("Target: Clone shiva37284 → javi (password: 457332)")
print("=" * 70)

# Try the non-agent API with correct credentials
print("\nAttempting user creation via API...")

params = {
    'source': 'admin',
    'user': admin_user,
    'pass': admin_pass,
    'function': 'add_user',
    'agent_user': 'javi',
    'agent_pass': '457332',
    'agent_user_level': '9',
    'agent_full_name': 'Javi Admin',
    'agent_user_group': 'ADMIN',
    'active': 'Y'
}

try:
    response = requests.get(f"{base_url}/vicidial/non_agent_api.php", 
                           params=params, verify=False, timeout=15)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if "SUCCESS" in response.text or "added" in response.text.upper():
        print("\n✓ User 'javi' created successfully!")
    elif "already exists" in response.text.lower():
        print("\n⚠ User 'javi' already exists!")
    else:
        print("\nAPI response received. Trying admin panel method...")
        
        # Method 2: Try admin panel login
        session = requests.Session()
        session.verify = False
        
        login_data = {
            'user': admin_user,
            'pass': admin_pass,
            'DB': 'asterisk',
            'SUBMIT': 'LOGIN'
        }
        
        login_resp = session.post(f"{base_url}/vicidial/admin.php", data=login_data)
        
        if login_resp.status_code == 200 and "logout" in login_resp.text.lower():
            print("✓ Logged into admin panel successfully")
            
            # Now try to access user management
            print("\nAccessing user management...")
            user_page = session.get(f"{base_url}/vicidial/admin.php?ADD=3")
            
            if "shiva37284" in user_page.text:
                print("✓ Found shiva37284 user")
                print("\nYou'll need to clone manually via the web interface:")
                print("1. Go to: https://merchantfundexp.cloudautodialer.in/vicidial/admin.php")
                print(f"2. Login as: {admin_user} / {admin_pass}")
                print("3. Click ADMIN → Users")
                print("4. Find shiva37284 and click COPY/CLONE")
                print("5. Set username: javi")
                print("6. Set password: 457332")
                print("7. Click SUBMIT")
            
        else:
            print(f"Admin panel login status: {login_resp.status_code}")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

