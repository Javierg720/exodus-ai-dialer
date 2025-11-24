#!/usr/bin/env python3
"""
Subdomain Scanner for warmconnect.com
Scans for active *.cc.warmconnect.com subdomains
"""

import requests
import concurrent.futures
from typing import List, Tuple
import sys
import string

# Disable SSL warnings for self-signed certificates
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Common subdomain patterns to check
COMMON_NAMES = [
    'onelove', 'twolove', 'threelove', 'fourlove', 'fivelove',
    'ava', 'bot', 'dialer', 'vicidial', 'vici', 'asterisk',
    'pbx', 'voip', 'sip', 'trunk', 'carrier',
    'admin', 'web', 'portal', 'dashboard', 'app',
    'prod', 'production', 'staging', 'dev', 'test',
    'server', 'node', 'host', 'client', 'customer'
]

def check_subdomain(subdomain: str, path: str = "/wiz.php") -> Tuple[str, bool, str]:
    """
    Check if a subdomain is active
    
    Args:
        subdomain: The subdomain name to check
        path: The path to check (default: /wiz.php)
        
    Returns:
        Tuple of (subdomain, is_active, status_info)
    """
    url = f"http://{subdomain}.cc.warmconnect.com{path}"
    
    try:
        response = requests.get(url, timeout=5, allow_redirects=True, verify=False)
        if response.status_code == 200:
            return (subdomain, True, f"Status 200 - Active ({len(response.content)} bytes)")
        elif response.status_code in [301, 302, 303, 307, 308]:
            return (subdomain, True, f"Status {response.status_code} - Redirect to {response.headers.get('Location', 'unknown')}")
        elif response.status_code == 404:
            return (subdomain, False, f"Status 404 - Not Found")
        elif response.status_code == 403:
            return (subdomain, True, f"Status 403 - Forbidden (Server exists)")
        elif response.status_code == 401:
            return (subdomain, True, f"Status 401 - Authentication Required (Server exists)")
        else:
            return (subdomain, True, f"Status {response.status_code} - Server responds")
    except requests.exceptions.Timeout:
        return (subdomain, False, "Timeout")
    except requests.exceptions.ConnectionError:
        return (subdomain, False, "Connection Error")
    except Exception as e:
        return (subdomain, False, f"Error: {str(e)}")

def scan_subdomains(subdomain_list: List[str], max_workers: int = 20) -> List[Tuple[str, bool, str]]:
    """
    Scan a list of subdomains concurrently
    
    Args:
        subdomain_list: List of subdomain names to check
        max_workers: Maximum concurrent workers
        
    Returns:
        List of results
    """
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_subdomain, name): name for name in subdomain_list}
        
        completed = 0
        total = len(subdomain_list)
        
        for future in concurrent.futures.as_completed(futures):
            completed += 1
            result = future.result()
            results.append(result)
            
            # Print progress
            if completed % 10 == 0 or result[1]:  # Every 10 or when active found
                print(f"Progress: {completed}/{total} - Last checked: {result[0]}", end='\r')
                if result[1]:
                    print(f"\n[ACTIVE] {result[0]}.cc.warmconnect.com - {result[2]}")
    
    print()  # New line after progress
    return results

def generate_subdomain_list(mode: str = "common") -> List[str]:
    """
    Generate list of subdomains to check
    
    Args:
        mode: "common" for common names, "alpha" for a-z, "numeric" for numbers
        
    Returns:
        List of subdomain names
    """
    if mode == "common":
        return COMMON_NAMES
    elif mode == "alpha":
        # Single letters and combinations
        subdomains = list(string.ascii_lowercase)
        # Add two-letter combinations
        for a in string.ascii_lowercase:
            for b in string.ascii_lowercase:
                subdomains.append(f"{a}{b}")
        return subdomains
    elif mode == "numeric":
        # Numbers 1-1000
        return [str(i) for i in range(1, 1001)]
    elif mode == "love":
        # Pattern: onelove, twolove, etc.
        words = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
        return [f"{word}love" for word in words]
    else:
        return COMMON_NAMES

def main():
    print("=" * 70)
    print("Warmconnect.com Subdomain Scanner")
    print("Scans for active *.cc.warmconnect.com subdomains")
    print("=" * 70)
    print()
    
    # Default mode
    mode = "common"
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    
    print(f"Scan mode: {mode}")
    
    subdomain_list = generate_subdomain_list(mode)
    
    print(f"Total subdomains to check: {len(subdomain_list)}")
    print()
    
    results = scan_subdomains(subdomain_list)
    
    # Filter active subdomains
    active_subdomains = [(name, status) for name, is_active, status in results if is_active]
    
    print()
    print("=" * 70)
    print("SCAN COMPLETE")
    print("=" * 70)
    print()
    print(f"Total scanned: {len(results)}")
    print(f"Active subdomains found: {len(active_subdomains)}")
    print()
    
    if active_subdomains:
        print("Active Subdomains:")
        print("-" * 70)
        for name, status in sorted(active_subdomains):
            print(f"  {name}.cc.warmconnect.com - {status}")
            print(f"    URL: http://{name}.cc.warmconnect.com/wiz.php")
        print()
    else:
        print("No active subdomains found in this scan.")
    
    # Save results to file
    output_file = f"warmconnect_scan_{mode}.txt"
    with open(output_file, 'w') as f:
        f.write(f"Warmconnect.com Subdomain Scan Results\n")
        f.write(f"Mode: {mode}\n")
        f.write(f"\nTotal Scanned: {len(results)}\n")
        f.write(f"Active Found: {len(active_subdomains)}\n\n")
        f.write("=" * 70 + "\n")
        f.write("ACTIVE SUBDOMAINS:\n")
        f.write("=" * 70 + "\n\n")
        
        for name, status in sorted(active_subdomains):
            f.write(f"{name}.cc.warmconnect.com\n")
            f.write(f"  Status: {status}\n")
            f.write(f"  URL: http://{name}.cc.warmconnect.com/wiz.php\n\n")
    
    print(f"Results saved to: {output_file}")
    print()
    print("Available modes:")
    print("  common  - Check common subdomain names (default)")
    print("  love    - Check *love pattern (onelove, twolove, etc.)")
    print("  alpha   - Check a-z and aa-zz patterns")
    print("  numeric - Check numbers 1-1000")

if __name__ == "__main__":
    main()
