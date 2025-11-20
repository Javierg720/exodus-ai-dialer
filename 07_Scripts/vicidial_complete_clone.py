#!/usr/bin/env python3
"""
VICIdial User Cloning Script
Attempts multiple methods to clone shiva37284 to javi user
"""
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base_url = "https://merchantfundexp.cloudautodialer.in"

def try_api_methods():
    """Try various VICIdial API endpoints"""
    
    # Method 1: Non-agent API
    print("=" * 60)
    print("METHOD 1: Non-Agent API")
    print("=" * 60)
    
    api_endpoints = [
        "/vicidial/non_agent_api.php",
        "/agc/api.php",
        "/vicidial/admin_web_api.php"
    ]
    
    credentials = [
        {'user': 'root', 'pass': '3L5v3XzKXC724bM8au8R'},
        {'user': '6666', 'pass': '3L5v3XzKXC724bM8au8R'},  # Sometimes root is 6666
    ]
    
    for endpoint in api_endpoints:
        for cred in credentials:
            print(f"\nTrying {endpoint} with user: {cred['user']}")
            
            params = {
                'source': 'admin',
                'user': cred['user'],
                'pass': cred['pass'],
                'function': 'add_user',
                'agent_user': 'javi',
                'agent_pass': '457332',
                'agent_user_level': '9',
                'agent_full_name': 'Javi Admin',
                'agent_user_group': 'ADMIN',
                'active': 'Y'
            }
            
            try:
                response = requests.get(f"{base_url}{endpoint}", params=params, verify=False, timeout=10)
                print(f"  Status: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                
                if "SUCCESS" in response.text or "added" in response.text.lower():
                    print("  ✓ SUCCESS!")
                    return True
            except Exception as e:
                print(f"  Error: {e}")
    
    return False

def try_admin_login():
    """Try admin panel login"""
    print("\n" + "=" * 60)
    print("METHOD 2: Admin Panel Login")
    print("=" * 60)
    
    session = requests.Session()
    session.verify = False
    
    # Try admin.php with POST
    login_urls = [
        "/vicidial/admin.php",
        "/vicidial/vicidial_admin.php",
        "/agc/vicidial.php"
    ]
    
    for url in login_urls:
        print(f"\nTrying {url}")
        
        # Try form-based login
        login_data = {
            'user': 'root',
            'pass': '3L5v3XzKXC724bM8au8R',
            'DB': 'asterisk',  # Default VICIdial DB
            'SUBMIT': 'LOGIN'
        }
        
        try:
            response = session.post(f"{base_url}{url}", data=login_data, timeout=10)
            print(f"  Status: {response.status_code}")
            
            # Check if logged in
            if "logout" in response.text.lower() or "logged in" in response.text.lower():
                print("  ✓ Login successful!")
                
                # Save session cookies
                with open('/home/user/vicidial_cookies.txt', 'w') as f:
                    f.write(str(session.cookies))
                
                return session
            else:
                snippet = response.text[:300].replace('\n', ' ')
                print(f"  Response snippet: {snippet}")
                
        except Exception as e:
            print(f"  Error: {e}")
    
    return None

def main():
    print("VICIdial User Cloning Tool")
    print("Target: Clone shiva37284 → javi with same admin privileges")
    print()
    
    # Try API methods
    if try_api_methods():
        print("\n✓ User created successfully via API!")
        return
    
    # Try admin login
    session = try_admin_login()
    if session:
        print("\n✓ Logged into admin panel!")
        print("Next steps would require parsing the admin interface")
    
    print("\n" + "=" * 60)
    print("ALTERNATIVE APPROACH NEEDED")
    print("=" * 60)
    print("\nThe credentials may not have API access enabled.")
    print("You may need to:")
    print("1. Log in via web browser manually")
    print("2. Access the database directly (MySQL)")
    print("3. Contact the VICIdial administrator")
    print("4. Use SSH access if available")

if __name__ == "__main__":
    main()
