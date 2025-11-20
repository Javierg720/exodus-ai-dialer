#!/usr/bin/env python3
import requests
from requests.auth import HTTPBasicAuth
import sys

# VICIdial credentials
base_url = "https://merchantfundexp.cloudautodialer.in"
root_user = "root"
root_pass = "3L5v3XzKXC724bM8au8R"

# Create session
session = requests.Session()
session.verify = False  # Disable SSL verification if needed

# Login to VICIdial
login_url = f"{base_url}/vicidial/admin.php"

try:
    # First, let's try to access the admin page with basic auth
    print("Attempting to login to VICIdial...")
    response = session.get(login_url, auth=HTTPBasicAuth(root_user, root_pass))
    print(f"Login response status: {response.status_code}")
    
    # VICIdial typically uses form-based authentication
    # Let's try posting login credentials
    login_data = {
        'user': root_user,
        'pass': root_pass,
        'SUBMIT': 'LOGIN'
    }
    
    login_response = session.post(f"{base_url}/vicidial/admin.php", data=login_data)
    print(f"Form login status: {login_response.status_code}")
    
    if "logout" in login_response.text.lower() or "admin" in login_response.text.lower():
        print("✓ Successfully logged in")
        
        # Now we need to fetch the shiva37284 user details first
        user_list_url = f"{base_url}/vicidial/admin.php?ADD=3"
        user_response = session.get(user_list_url)
        
        print("\nSearching for user 'shiva37284'...")
        
        # Check if we can see users
        if "shiva37284" in user_response.text:
            print("✓ Found shiva37284 user")
            
            # Now create the new user by accessing the user modification page
            # We'll need to replicate shiva37284's settings
            print("\nCreating new user 'javi' with admin privileges...")
            
            # VICIdial user creation typically uses ADD=31 for new user
            create_user_data = {
                'ADD': '31',
                'user': 'javi',
                'pass': '457332',
                'full_name': 'Javi',
                'user_level': '9',  # Super admin level
                'user_group': 'ADMIN',
                'active': 'Y',
                'SUBMIT': 'SUBMIT'
            }
            
            create_response = session.post(f"{base_url}/vicidial/admin.php", data=create_user_data)
            
            if "added" in create_response.text.lower() or "success" in create_response.text.lower():
                print("✓ User 'javi' created successfully with super admin privileges")
            else:
                print("Response received, checking status...")
                # Save response for inspection
                with open('/home/user/vicidial_create_response.html', 'w') as f:
                    f.write(create_response.text)
                print("Response saved to /home/user/vicidial_create_response.html")
        else:
            print("Could not find shiva37284 in user list")
            with open('/home/user/vicidial_users.html', 'w') as f:
                f.write(user_response.text)
            print("User list saved to /home/user/vicidial_users.html")
    else:
        print("Login may have failed. Saving response...")
        with open('/home/user/vicidial_login_response.html', 'w') as f:
            f.write(login_response.text)
        print("Login response saved to /home/user/vicidial_login_response.html")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
